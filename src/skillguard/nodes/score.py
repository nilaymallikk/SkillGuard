"""Turn findings into a risk score, severity band and recommendation."""

from __future__ import annotations

from skillguard.models import (
    SEVERITY_POINTS,
    Recommendation,
    RiskAssessment,
    Severity,
)
from skillguard.state import ScanState

#: (upper score bound, severity, recommendation) from Part 3.3.
_BANDS: tuple[tuple[int, Severity, Recommendation], ...] = (
    (20, Severity.LOW, Recommendation.SAFE),
    (50, Severity.MEDIUM, Recommendation.CAUTION),
    (80, Severity.HIGH, Recommendation.DO_NOT_INSTALL),
    (100, Severity.CRITICAL, Recommendation.DO_NOT_INSTALL),
)


def _band(score: int) -> tuple[Severity, Recommendation]:
    for upper, severity, recommendation in _BANDS:
        if score <= upper:
            return severity, recommendation
    return Severity.CRITICAL, Recommendation.DO_NOT_INSTALL


def score_node(state: ScanState) -> dict[str, object]:
    findings = list(state.get("effective_findings", []))
    score = min(100, sum(SEVERITY_POINTS[finding.severity] for finding in findings))
    severity, recommendation = _band(score)
    return {"risk": RiskAssessment(score=score, severity=severity, recommendation=recommendation)}
