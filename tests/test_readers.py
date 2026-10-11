"""safe reading of untrusted files"""

from __future__ import annotations

from pathlib import Path

from skillguard.readers import read_file


def test_reads_text_and_counts_lines(tmp_path: Path) -> None:
    path = tmp_path / "a.txt"
    path.write_text("one\ntwo\n", encoding="utf-8")

    result = read_file(path, max_bytes=1000)

    assert result.content == "one\ntwo\n"
    assert result.lines == 2
    assert result.binary is False
    assert result.skip_reason is None


def test_binary_is_skipped(tmp_path: Path) -> None:
    path = tmp_path / "blob.bin"
    path.write_bytes(b"\x00\x01\x02")

    result = read_file(path, max_bytes=1000)

    assert result.binary is True
    assert result.content is None
    assert result.skip_reason == "binary"


def test_oversized_is_skipped_without_loading_it(tmp_path: Path) -> None:
    path = tmp_path / "big.txt"
    path.write_text("x" * 50, encoding="utf-8")

    result = read_file(path, max_bytes=10)

    assert result.content is None
    assert result.size_bytes == 50
    assert result.skip_reason is not None
    assert "oversized" in result.skip_reason


def test_invalid_utf8_is_replaced_not_fatal(tmp_path: Path) -> None:
    path = tmp_path / "bad.txt"
    path.write_bytes(b"ok \xff\xfe end")

    result = read_file(path, max_bytes=1000)

    assert result.content is not None
    assert result.content.startswith("ok ")
    assert result.skip_reason is None


def test_empty_file_is_readable(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")

    result = read_file(path, max_bytes=1000)

    assert result.content == ""
    assert result.lines == 0


def test_missing_file_is_reported_not_raised(tmp_path: Path) -> None:
    result = read_file(tmp_path / "nope.txt", max_bytes=10)

    assert result.content is None
    assert result.skip_reason is not None
