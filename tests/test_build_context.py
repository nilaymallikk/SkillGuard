"""the build_context node wires discovery into the graph state."""

from __future__ import annotations

from pathlib import Path

from skillguard.nodes.build_context import build_context
from skillguard.state import ScanState


def test_builds_context_from_the_state(tmp_path: Path) -> None:
    (tmp_path / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")

    update = build_context(ScanState(skill_path=str(tmp_path)))
    context = update["context"]

    assert context.manifest.get("name") == "demo"
    assert [c.path for c in context.components] == ["SKILL.md"]


def test_missing_skill_path_gives_an_empty_context() -> None:
    update = build_context(ScanState())

    context = update["context"]
    assert context.skill_path == ""
    assert context.components == []
