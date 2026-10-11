"""the graph runs end to end and merges parallel analyzers"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from skillguard.graph import build_graph
from skillguard.models import Finding, Location, Severity
from skillguard.pipeline import initial_state, run_scan, stream_scan
from skillguard.state import ScanState


def _finding(rule_id: str) -> Finding:
    return Finding(
        rule_id=rule_id,
        category="test",
        severity=Severity.LOW,
        message="synthetic",
        location=Location(file="SKILL.md", start_line=1),
    )


def _analyzer(rule_id: str) -> Callable[[ScanState], dict[str, object]]:
    def run(state: ScanState) -> dict[str, object]:
        return {"findings": [_finding(rule_id)]}

    return run


def test_graph_runs_to_a_report(tmp_path: Path) -> None:
    skill = tmp_path / "demo-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# demo", encoding="utf-8")

    final = run_scan(initial_state(str(skill)))

    report = final["report"]
    assert report.skill_name == "demo-skill"
    assert len(report.findings) == 1
    assert report.findings[0].rule_id == "PLACEHOLDER"


def test_parallel_analyzers_both_survive_the_merge(tmp_path: Path) -> None:
    skill = tmp_path / "demo-skill"
    skill.mkdir()

    app = build_graph(analyzers={"analyzer_a": _analyzer("A"), "analyzer_b": _analyzer("B")})
    final = app.invoke(initial_state(str(skill)))

    assert sorted(f.rule_id for f in final["findings"]) == ["A", "B"]


def test_stream_emits_each_node_once(tmp_path: Path) -> None:
    skill = tmp_path / "demo-skill"
    skill.mkdir()

    nodes = [name for name, _update in stream_scan(initial_state(str(skill)))]

    assert nodes[0] == "resolve_input"
    assert nodes[-1] == "report"
    assert len(nodes) == len(set(nodes))


def test_missing_directory_is_recorded_as_an_error(tmp_path: Path) -> None:
    final = run_scan(initial_state(str(tmp_path / "does-not-exist")))

    assert any("not a directory" in message for message in final["errors"])
