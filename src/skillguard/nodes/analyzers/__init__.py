"""Analyzer registry.

An analyzer is a node function: ``state -> partial update``. Adding it to
ANALYZER_NODES is all that is needed for the graph to run it in parallel
with the other analyzers.
"""

from __future__ import annotations

from collections.abc import Callable

from skillguard.models import Finding, Location, Severity
from skillguard.state import ScanState

#: Signature every analyzer node must satisfy.
AnalyzerFn = Callable[[ScanState], dict[str, object]]


def static_placeholder(state: ScanState) -> dict[str, object]:
    """Temporary analyzer that always reports one finding"""
    return {
        "findings": [
            Finding(
                rule_id="PLACEHOLDER",
                category="placeholder",
                severity=Severity.LOW,
                message="Placeholder analyzer ran",
                location=Location(file="SKILL.md", start_line=1),
                snippet=str(state.get("skill_path", "")),
            )
        ]
    }


ANALYZER_NODES: dict[str, AnalyzerFn] = {
    "static_placeholder": static_placeholder,
}
