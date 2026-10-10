"""Build the ScanContext analyzers read from"""

from __future__ import annotations

from skillguard.models import ScanContext
from skillguard.state import ScanState


def build_context(state: ScanState) -> dict[str, object]:
    return {"context": ScanContext(skill_path=state.get("skill_path", ""))}
