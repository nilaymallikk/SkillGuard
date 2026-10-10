"""the domain models validate and serialize."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from skillguard.constants import SCANNER_VERSION
from skillguard.models import (
    SEVERITY_POINTS,
    Component,
    Finding,
    Location,
    Recommendation,
    Report,
    RiskAssessment,
    Severity,
)


def make_finding(**overrides: object) -> Finding:
    data: dict[str, object] = {
        "rule_id": "E2",
        "category": "data_exfiltration",
        "severity": Severity.HIGH,
        "message": "Environment variable harvesting",
        "location": Location(file="scripts/exfil.py", start_line=23),
        "snippet": "for key, val in os.environ.items():",
        "confidence": 0.94,
        "remediation": "Do not read secrets from the environment.",
    }
    data.update(overrides)
    return Finding.model_validate(data)


def make_report() -> Report:
    return Report(
        skill_name="malicious-skill",
        source="./tests/fixtures/malicious_skill/",
        scanned_at="2026-01-29T10:30:00Z",
        components=[
            Component(path="SKILL.md", type="markdown", lines=142),
            Component(
                path="scripts/exfil.py",
                type="python",
                lines=87,
                executable=True,
                size_bytes=2411,
            ),
        ],
        findings=[make_finding()],
        risk=RiskAssessment(
            score=78,
            severity=Severity.HIGH,
            recommendation=Recommendation.DO_NOT_INSTALL,
        ),
        has_executable_scripts=True,
    )


def test_valid_finding_is_constructible() -> None:
    assert make_finding().severity is Severity.HIGH


def test_confidence_out_of_range_is_rejected() -> None:
    with pytest.raises(ValidationError):
        make_finding(confidence=2.0)


def test_line_numbers_are_one_based() -> None:
    with pytest.raises(ValidationError):
        Location(file="SKILL.md", start_line=0)


def test_finding_is_immutable() -> None:
    finding = make_finding()
    with pytest.raises(ValidationError):
        finding.message = "tampered"


def test_finding_is_hashable_so_dedupe_can_use_a_set() -> None:
    assert len({make_finding(), make_finding()}) == 1


def test_report_serializes_enums_as_strings() -> None:
    data = json.loads(make_report().model_dump_json(indent=2))
    assert data["risk"]["recommendation"] == "DO_NOT_INSTALL"
    assert data["risk"]["severity"] == "HIGH"
    assert data["findings"][0]["severity"] == "HIGH"
    assert data["scanner_version"] == SCANNER_VERSION


def test_every_severity_has_score_points() -> None:
    assert set(SEVERITY_POINTS) == set(Severity)
