"""Read files from an untrusted skill without trusting them.

Three rules:
- never load more than ``max_bytes`` into memory,
- never crash on a bad encoding,
- never treat binary content as text.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# A file containing a NUL byte is treated as binary.
_NUL = b"\x00"


@dataclass(frozen=True, slots=True)
class ReadResult:
    """Outcome of one read attempt."""

    content: str | None  # None when the file was skipped
    size_bytes: int
    lines: int
    binary: bool
    skip_reason: str | None  # None when content was read successfully


def read_file(path: Path, *, max_bytes: int) -> ReadResult:
    """Read ``path`` as text, bounded by ``max_bytes``. Never raises on bad input."""
    try:
        size = path.stat().st_size
    except OSError as exc:
        return ReadResult(None, 0, 0, False, f"unreadable: {exc.strerror}")

    # Read one byte PAST the cap. If we get back more than max_bytes the file is
    # oversized and we never loaded the whole thing into memory
    try:
        with path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
    except OSError as exc:
        return ReadResult(None, size, 0, False, f"unreadable: {exc.strerror}")

    if len(data) > max_bytes:
        return ReadResult(None, size, 0, False, f"oversized: {size} bytes > {max_bytes}")

    if _NUL in data:
        return ReadResult(None, size, 0, True, "binary")

    # errors="replace" means one bad byte can never abort a whole scan
    text = data.decode("utf-8", errors="replace")
    return ReadResult(text, size, len(text.splitlines()), False, None)
