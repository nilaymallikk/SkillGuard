"""Resolve the user's input reference into a local skill directory"""

from __future__ import annotations

from pathlib import Path

from skillguard.state import ScanState


def resolve_input(state: ScanState) -> dict[str, object]:
    ref = state.get("input_ref", "")
    path = Path(ref).expanduser()
    if not path.is_dir():
        return {"errors": [f"resolve_input: not a directory: {ref}"]}
    return {"skill_path": str(path.resolve())}
