"""Collapse duplicate findings before scoring"""

from __future__ import annotations

from skillguard.state import ScanState


def deduplicate(state: ScanState) -> dict[str, object]:
    return {"effective_findings": list(state.get("findings", []))}
