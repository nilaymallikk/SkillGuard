"""Build the ScanContext analyzers read from"""

from __future__ import annotations

from skillguard.config import get_settings
from skillguard.discovery import discover
from skillguard.models import ScanContext
from skillguard.state import ScanState


def build_context(state: ScanState) -> dict[str, object]:
    """Walk the resolved skill directory into a ScanContext"""
    skill_path = state.get("skill_path")
    if not skill_path:
        return {"context": ScanContext(skill_path="")}

    settings = get_settings()
    context = discover(
        skill_path,
        max_files=settings.max_files,
        max_file_bytes=settings.max_file_bytes,
    )
    return {"context": context}
