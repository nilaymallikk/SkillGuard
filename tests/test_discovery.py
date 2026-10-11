"""turning a directory into a trustworthy ScanContext"""

from __future__ import annotations

from pathlib import Path

from skillguard.discovery import classify, discover, parse_front_matter
from skillguard.models import ScanContext


def _skill(tmp_path: Path) -> Path:
    root = tmp_path / "skill"
    (root / "scripts").mkdir(parents=True)
    (root / "SKILL.md").write_text("---\nname: demo\n---\n\n# Demo\n", encoding="utf-8")
    (root / "scripts" / "run.py").write_text("print('hi')\n", encoding="utf-8")
    (root / "requirements.txt").write_text("requests\n", encoding="utf-8")
    return root


def _discover(root: Path, *, max_files: int = 100, max_file_bytes: int = 1000) -> ScanContext:
    return discover(str(root), max_files=max_files, max_file_bytes=max_file_bytes)


def test_components_are_sorted_for_reproducible_reports(tmp_path: Path) -> None:
    context = _discover(_skill(tmp_path))

    assert [c.path for c in context.components] == [
        "SKILL.md",
        "requirements.txt",
        "scripts/run.py",
    ]


def test_types_are_classified(tmp_path: Path) -> None:
    context = _discover(_skill(tmp_path))
    types = {c.path: c.type for c in context.components}

    assert types["SKILL.md"] == "markdown"
    assert types["scripts/run.py"] == "python"
    assert types["requirements.txt"] == "requirements"


def test_executable_files_set_the_multiplier_flag(tmp_path: Path) -> None:
    context = _discover(_skill(tmp_path))

    assert context.has_executable_scripts is True


def test_ignored_directories_are_never_entered(tmp_path: Path) -> None:
    root = _skill(tmp_path)
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("secret\n", encoding="utf-8")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "x.pyc").write_bytes(b"\x00")

    context = _discover(root)
    paths = " ".join(c.path for c in context.components)

    assert ".git" not in paths
    assert "__pycache__" not in paths


def test_binary_and_oversized_land_in_skipped(tmp_path: Path) -> None:
    root = _skill(tmp_path)
    (root / "blob.bin").write_bytes(b"\x00\x01")
    (root / "big.txt").write_text("x" * 100, encoding="utf-8")

    context = _discover(root, max_file_bytes=10)
    reasons = dict(context.skipped)

    assert reasons["blob.bin"] == "binary"
    assert "oversized" in reasons["big.txt"]


def test_file_cache_holds_text_only(tmp_path: Path) -> None:
    root = _skill(tmp_path)
    (root / "blob.bin").write_bytes(b"\x00")

    context = _discover(root)

    assert "scripts/run.py" in context.file_cache
    assert "blob.bin" not in context.file_cache


def test_manifest_is_parsed_from_skill_md(tmp_path: Path) -> None:
    context = _discover(_skill(tmp_path))

    assert context.manifest.get("name") == "demo"


def test_max_files_is_enforced(tmp_path: Path) -> None:
    context = _discover(_skill(tmp_path), max_files=1)

    assert len(context.components) == 1
    assert any("max_files" in reason for _path, reason in context.skipped)


def test_symlinks_are_not_followed(tmp_path: Path) -> None:
    root = _skill(tmp_path)
    (root / "link.py").symlink_to("/etc/passwd")

    context = _discover(root)
    reasons = dict(context.skipped)

    assert reasons["link.py"] == "symlink"
    assert "link.py" not in context.file_cache


def test_classify_requirements_variants() -> None:
    assert classify(Path("requirements.txt")) == "requirements"
    assert classify(Path("requirements-dev.txt")) == "requirements"
    assert classify(Path("notes.txt")) == "text"
    assert classify(Path("Makefile")) == "other"


def test_front_matter_absent() -> None:
    assert parse_front_matter("# just markdown") == {}


def test_front_matter_yaml_cannot_execute_code() -> None:
    evil = '---\n!!python/object/apply:os.system ["echo pwned"]\n---\nbody\n'

    assert parse_front_matter(evil) == {}
