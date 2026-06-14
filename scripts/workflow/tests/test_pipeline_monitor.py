"""test_pipeline_monitor.py — Phase 8 pipeline monitor unit tests.

Covers:
  - emit_node_event: creates / appends case yaml; set_triage_status works; no PII.
  - project_node_states: NODE_ENTER with no EXIT past SLA -> stalled.
  - NODE_FAIL event -> failed + error_class surfaced.
  - detect_stalls: human-gate node past SLA -> human-gate-stall alert.
  - detect_stalls: non-qualify (gap_only) case excluded from accounting.
  - render_node_graph / render_status_table: produce strings without exception.
  - g14: empty dir -> SPEC; stalled qualify case -> FAIL.

Run:
  PYTHONIOENCODING=utf-8 python -m pytest scripts/workflow/tests/test_pipeline_monitor.py -q
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WORKFLOW_DIR = REPO_ROOT / "scripts" / "workflow"

for _p in (str(WORKFLOW_DIR), str(REPO_ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pipeline_emit import (  # noqa: E402
    emit_node_event,
    set_triage_status,
    capture_evidence,
    VALID_NODES,
)
from pipeline_monitor import (  # noqa: E402
    NODES,
    NodeState,
    Alert,
    load_cases,
    project_node_states,
    detect_stalls,
    aggregate_health,
    render_summary,
)
from pipeline_status import (  # noqa: E402
    render_status_table,
    render_node_graph,
)

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_case_yaml(tmp_path: Path, client_id: str, *, slug: str = "test-co") -> Path:
    """Return a path to a (not-yet-created) case YAML in tmp_path."""
    return tmp_path / f"{client_id}.yaml"


def _load_yaml(path: Path) -> dict:
    if not _HAS_YAML:
        import json
        return json.loads(path.read_text(encoding="utf-8"))
    return _yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# ---------------------------------------------------------------------------
# emit_node_event tests
# ---------------------------------------------------------------------------

class TestEmitNodeEvent:
    def test_creates_case_file(self, tmp_path):
        p = _make_case_yaml(tmp_path, "abc123", slug="slug-a")
        ev = emit_node_event(p, "SUBMITTED", "NODE_ENTER", slug="slug-a", score=60)
        assert p.exists(), "case yaml must be created"
        data = _load_yaml(p)
        assert data["client_id"] == "abc123"
        assert data["slug"] == "slug-a"
        assert data["score"] == 60
        assert len(data["pipeline_events"]) == 1
        assert data["pipeline_events"][0]["event"] == "NODE_ENTER"
        assert ev["node_id"] == "SUBMITTED"

    def test_appends_events(self, tmp_path):
        p = _make_case_yaml(tmp_path, "abc123", slug="slug-a")
        emit_node_event(p, "SUBMITTED", "NODE_ENTER", slug="slug-a")
        emit_node_event(p, "SUBMITTED", "NODE_EXIT_OK", slug="slug-a")
        data = _load_yaml(p)
        assert len(data["pipeline_events"]) == 2
        assert data["pipeline_events"][1]["event"] == "NODE_EXIT_OK"

    def test_no_pii_written(self, tmp_path):
        p = _make_case_yaml(tmp_path, "abc123", slug="slug-a")
        emit_node_event(p, "DEPLOYED", "NODE_ENTER", slug="slug-a", score=75)
        raw = p.read_text(encoding="utf-8")
        # No PII indicators should appear
        for pii_word in ("email", "company", "name", "phone", "free_text"):
            assert pii_word not in raw.lower(), f"PII key {pii_word!r} found in case yaml"

    def test_invalid_node_raises(self, tmp_path):
        p = _make_case_yaml(tmp_path, "abc123", slug="slug-a")
        with pytest.raises(ValueError, match="Unknown node_id"):
            emit_node_event(p, "NOT_A_NODE", "NODE_ENTER", slug="slug-a")

    def test_invalid_event_raises(self, tmp_path):
        p = _make_case_yaml(tmp_path, "abc123", slug="slug-a")
        with pytest.raises(ValueError, match="Unknown event"):
            emit_node_event(p, "SUBMITTED", "BAD_EVENT", slug="slug-a")

    def test_set_triage_status(self, tmp_path):
        p = _make_case_yaml(tmp_path, "abc123", slug="slug-a")
        emit_node_event(p, "SUBMITTED", "NODE_ENTER", slug="slug-a")
        set_triage_status(p, "qualify")
        data = _load_yaml(p)
        assert data["triage_status"] == "qualify"

    def test_set_triage_status_invalid_raises(self, tmp_path):
        p = _make_case_yaml(tmp_path, "abc123", slug="slug-a")
        with pytest.raises(ValueError, match="Unknown triage_status"):
            set_triage_status(p, "INVALID_STATUS")

    def test_set_triage_status_creates_file(self, tmp_path):
        p = _make_case_yaml(tmp_path, "new-case", slug="slug-b")
        assert not p.exists()
        set_triage_status(p, "defer")
        assert p.exists()
        data = _load_yaml(p)
        assert data["triage_status"] == "defer"

    def test_capture_evidence_no_pii(self, tmp_path):
        ev_dir = tmp_path / "evidence"
        path = capture_evidence(
            "DEPLOYED", "slug-a",
            returncode=1,
            stderr_tail="Error: connection refused",
            report_path="/some/report.json",
            out_dir=ev_dir,
        )
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "DEPLOYED" in content
        assert "slug-a" in content
        assert "email" not in content.lower()
        assert "company" not in content.lower()


# ---------------------------------------------------------------------------
# project_node_states tests
# ---------------------------------------------------------------------------

class TestProjectNodeStates:
    def _make_case(
        self,
        *,
        triage_status: str = "qualify",
        events: list[dict] | None = None,
        slug: str = "test-slug",
        client_id: str = "case001",
    ) -> dict:
        return {
            "client_id": client_id,
            "slug": slug,
            "triage_status": triage_status,
            "pipeline_events": events or [],
        }

    def test_node_enter_no_exit_past_sla_is_stalled(self):
        sla = NODES["DEPLOYED"]["sla_seconds"]  # 36000
        enter_time = _now() - timedelta(seconds=sla + 100)
        case = self._make_case(events=[
            {"node_id": "DEPLOYED", "event": "NODE_ENTER", "ts": _iso(enter_time), "error_class": None},
        ])
        states = project_node_states(case, _now())
        deployed = next((s for s in states if s.node_id == "DEPLOYED"), None)
        assert deployed is not None
        assert deployed.status == "stalled"
        assert deployed.dwell_seconds > sla

    def test_node_enter_no_exit_within_sla_is_in_progress(self):
        enter_time = _now() - timedelta(seconds=60)
        case = self._make_case(events=[
            {"node_id": "SUBMITTED", "event": "NODE_ENTER", "ts": _iso(enter_time), "error_class": None},
        ])
        states = project_node_states(case, _now())
        submitted = next((s for s in states if s.node_id == "SUBMITTED"), None)
        assert submitted is not None
        assert submitted.status == "in_progress"

    def test_node_fail_event_yields_failed_status(self):
        enter_time = _now() - timedelta(seconds=100)
        case = self._make_case(events=[
            {"node_id": "DEPLOYED", "event": "NODE_ENTER", "ts": _iso(enter_time), "error_class": None},
            {"node_id": "DEPLOYED", "event": "NODE_FAIL", "ts": _iso(_now()), "error_class": "deploy-fail"},
        ])
        states = project_node_states(case, _now())
        deployed = next((s for s in states if s.node_id == "DEPLOYED"), None)
        assert deployed is not None
        assert deployed.status == "failed"
        assert deployed.error_class == "deploy-fail"

    def test_node_enter_plus_exit_is_complete(self):
        enter_time = _now() - timedelta(seconds=200)
        exit_time = _now() - timedelta(seconds=50)
        case = self._make_case(events=[
            {"node_id": "SUBMITTED", "event": "NODE_ENTER", "ts": _iso(enter_time), "error_class": None},
            {"node_id": "SUBMITTED", "event": "NODE_EXIT_OK", "ts": _iso(exit_time), "error_class": None},
        ])
        states = project_node_states(case, _now())
        submitted = next((s for s in states if s.node_id == "SUBMITTED"), None)
        assert submitted is not None
        assert submitted.status == "complete"

    def test_multiple_nodes(self):
        enter = _now() - timedelta(seconds=500)
        case = self._make_case(events=[
            {"node_id": "SUBMITTED", "event": "NODE_ENTER", "ts": _iso(enter), "error_class": None},
            {"node_id": "SUBMITTED", "event": "NODE_EXIT_OK", "ts": _iso(_now() - timedelta(seconds=400)), "error_class": None},
            {"node_id": "TRIAGED", "event": "NODE_ENTER", "ts": _iso(_now() - timedelta(seconds=300)), "error_class": None},
            {"node_id": "TRIAGED", "event": "NODE_EXIT_OK", "ts": _iso(_now() - timedelta(seconds=200)), "error_class": None},
        ])
        states = project_node_states(case, _now())
        node_map = {s.node_id: s for s in states}
        assert node_map["SUBMITTED"].status == "complete"
        assert node_map["TRIAGED"].status == "complete"


# ---------------------------------------------------------------------------
# detect_stalls tests
# ---------------------------------------------------------------------------

class TestDetectStalls:
    def _qualify_stalled_state(self, node_id: str = "DEPLOYED") -> NodeState:
        sla = NODES[node_id]["sla_seconds"]
        enter_time = _now() - timedelta(seconds=sla + 500)
        return NodeState(
            node_id=node_id,
            case_id="case001",
            slug="test-slug",
            entered_at=_iso(enter_time),
            exited_at=None,
            status="stalled",
            dwell_seconds=sla + 500,
            error_class=None,
            detail=None,
        )

    def _human_gate_stalled_state(self, node_id: str = "PROFILE_CONFIRMED") -> NodeState:
        sla = NODES[node_id]["sla_seconds"]
        enter_time = _now() - timedelta(seconds=sla + 100)
        return NodeState(
            node_id=node_id,
            case_id="case002",
            slug="test-slug-2",
            entered_at=_iso(enter_time),
            exited_at=None,
            status="stalled",
            dwell_seconds=sla + 100,
            error_class=None,
            detail=None,
        )

    def test_stalled_node_produces_alert(self):
        state = self._qualify_stalled_state("DEPLOYED")
        alerts = detect_stalls([state], _now())
        assert len(alerts) == 1
        a = alerts[0]
        assert a.alert_type == "stall"
        assert a.node_id == "DEPLOYED"
        assert a.severity in ("warn", "error")

    def test_human_gate_stall_classified_correctly(self):
        state = self._human_gate_stalled_state("PROFILE_CONFIRMED")
        alerts = detect_stalls([state], _now())
        assert len(alerts) == 1
        a = alerts[0]
        assert a.error_class == "human-gate-stall"

    def test_failed_node_produces_defect_alert(self):
        state = NodeState(
            node_id="DEPLOYED",
            case_id="case001",
            slug="test-slug",
            entered_at=_iso(_now() - timedelta(seconds=100)),
            exited_at=None,
            status="failed",
            dwell_seconds=100,
            error_class="deploy-fail",
            detail=None,
        )
        alerts = detect_stalls([state], _now())
        assert len(alerts) == 1
        a = alerts[0]
        assert a.alert_type == "defect"
        assert a.error_class == "deploy-fail"

    def test_non_qualify_nodes_excluded(self):
        """CALL_QUEUE, GAP_RECORDED, PM_TRIAGE should produce no alerts."""
        for nid in ("CALL_QUEUE", "GAP_RECORDED", "PM_TRIAGE"):
            sla = NODES[nid]["sla_seconds"]
            state = NodeState(
                node_id=nid,
                case_id="case003",
                slug="call-slug",
                entered_at=_iso(_now() - timedelta(seconds=sla + 9999)),
                exited_at=None,
                status="stalled",
                dwell_seconds=sla + 9999,
                error_class=None,
                detail=None,
            )
            alerts = detect_stalls([state], _now())
            assert alerts == [], f"{nid} should be excluded from stall accounting"

    def test_retry_exhausted_alert(self):
        state = NodeState(
            node_id="DEPLOYED",
            case_id="case001",
            slug="test-slug",
            entered_at=_iso(_now() - timedelta(seconds=100)),
            exited_at=None,
            status="failed",
            dwell_seconds=100,
            error_class="deploy-fail",
            detail=None,
        )
        processed = [
            {"slug": "test-slug", "status": "failed"},
            {"slug": "test-slug", "status": "failed"},
            {"slug": "test-slug", "status": "failed"},
        ]
        alerts = detect_stalls([state], _now(), processed=processed)
        assert len(alerts) == 1
        assert alerts[0].alert_type == "retry-exhausted"
        assert alerts[0].severity == "critical"


# ---------------------------------------------------------------------------
# aggregate_health / non-qualify exclusion tests
# ---------------------------------------------------------------------------

class TestAggregateHealth:
    def _case(
        self,
        client_id: str,
        triage_status: str,
        events: list[dict] | None = None,
    ) -> dict:
        return {
            "client_id": client_id,
            "slug": f"slug-{client_id}",
            "triage_status": triage_status,
            "pipeline_events": events or [],
        }

    def test_gap_only_case_excluded_from_stall_metrics(self):
        sla = NODES["DEPLOYED"]["sla_seconds"]
        enter_time = _now() - timedelta(seconds=sla + 9999)
        gap_case = self._case("gap001", "gap_only", events=[
            {"node_id": "DEPLOYED", "event": "NODE_ENTER", "ts": _iso(enter_time), "error_class": None},
        ])
        health = aggregate_health([gap_case], _now())
        # gap_only is not qualify -> should NOT count in failed/stalled
        assert health.stalled_cases == 0
        assert health.failed_cases == 0

    def test_qualify_stalled_case_counted(self):
        sla = NODES["DEPLOYED"]["sla_seconds"]
        enter_time = _now() - timedelta(seconds=sla + 100)
        qualify_case = self._case("q001", "qualify", events=[
            {"node_id": "SUBMITTED", "event": "NODE_ENTER", "ts": _iso(_now() - timedelta(seconds=500)), "error_class": None},
            {"node_id": "SUBMITTED", "event": "NODE_EXIT_OK", "ts": _iso(_now() - timedelta(seconds=400)), "error_class": None},
            {"node_id": "DEPLOYED", "event": "NODE_ENTER", "ts": _iso(enter_time), "error_class": None},
        ])
        health = aggregate_health([qualify_case], _now())
        assert health.stalled_cases == 1

    def test_qualify_failed_case_counted(self):
        qualify_case = self._case("q002", "qualify", events=[
            {"node_id": "DEPLOYED", "event": "NODE_ENTER", "ts": _iso(_now() - timedelta(seconds=100)), "error_class": None},
            {"node_id": "DEPLOYED", "event": "NODE_FAIL", "ts": _iso(_now()), "error_class": "deploy-fail"},
        ])
        health = aggregate_health([qualify_case], _now())
        assert health.failed_cases == 1

    def test_total_cases_counts_all(self):
        cases = [
            self._case("a", "qualify"),
            self._case("b", "gap_only"),
            self._case("c", "defer"),
        ]
        health = aggregate_health(cases, _now())
        assert health.total_cases == 3


# ---------------------------------------------------------------------------
# render_node_graph / render_status_table tests
# ---------------------------------------------------------------------------

class TestRenders:
    def _minimal_case(self, slug: str = "render-test", triage_status: str = "qualify") -> dict:
        return {
            "client_id": "case-render",
            "slug": slug,
            "triage_status": triage_status,
            "pipeline_events": [],
        }

    def test_render_status_table_no_exception(self):
        cases = [self._minimal_case()]
        result = render_status_table(cases, _now())
        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_status_table_empty_cases(self):
        result = render_status_table([], _now())
        assert isinstance(result, str)

    def test_render_node_graph_no_exception(self):
        case = self._minimal_case()
        result = render_node_graph(case, _now())
        assert isinstance(result, str)
        assert "render-test" in result

    def test_render_node_graph_with_events(self):
        enter_time = _now() - timedelta(seconds=100)
        exit_time = _now() - timedelta(seconds=50)
        case = {
            "client_id": "case-graph",
            "slug": "graph-slug",
            "triage_status": "qualify",
            "pipeline_events": [
                {"node_id": "SUBMITTED", "event": "NODE_ENTER", "ts": _iso(enter_time), "error_class": None},
                {"node_id": "SUBMITTED", "event": "NODE_EXIT_OK", "ts": _iso(exit_time), "error_class": None},
                {"node_id": "DEPLOYED", "event": "NODE_ENTER", "ts": _iso(_now() - timedelta(seconds=30)), "error_class": None},
                {"node_id": "DEPLOYED", "event": "NODE_FAIL", "ts": _iso(_now()), "error_class": "deploy-fail"},
            ],
        }
        result = render_node_graph(case, _now())
        assert isinstance(result, str)
        # SUBMITTED should show OK, DEPLOYED should show XX
        assert "OK" in result
        assert "XX" in result

    def test_render_summary_text(self):
        cases = [self._minimal_case()]
        health = aggregate_health(cases, _now())
        summary = render_summary(health, output="text")
        assert isinstance(summary, str)
        assert "Pipeline Health" in summary

    def test_render_summary_json(self):
        import json
        cases = [self._minimal_case()]
        health = aggregate_health(cases, _now())
        summary = render_summary(health, output="json")
        parsed = json.loads(summary)
        assert "total_cases" in parsed


# ---------------------------------------------------------------------------
# G-14 guard tests
# ---------------------------------------------------------------------------

class TestG14Guard:
    """Tests for diagnose.g14_intake_pipeline_health using injected cases_dir."""

    def _import_g14(self):
        """Import and return the g14 function from diagnose."""
        import importlib
        # Ensure scripts dir is in path
        scripts_dir = str(REPO_ROOT / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        # Force reload to ensure we get the current version
        import diagnose
        importlib.reload(diagnose)
        return diagnose.g14_intake_pipeline_health

    def test_empty_cases_dir_returns_spec(self, tmp_path):
        g14 = self._import_g14()
        cases_dir = tmp_path / "cases_empty"
        cases_dir.mkdir()
        result = g14(cases_dir=cases_dir)
        assert result.status == "SPEC", f"Expected SPEC, got {result.status}: {result.notes}"

    def test_absent_cases_dir_returns_spec(self, tmp_path):
        g14 = self._import_g14()
        absent = tmp_path / "does_not_exist"
        result = g14(cases_dir=absent)
        assert result.status == "SPEC"

    def test_qualify_case_with_node_fail_returns_fail(self, tmp_path):
        g14 = self._import_g14()
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        # Create a qualify case with a NODE_FAIL event
        p = cases_dir / "abc001.yaml"
        emit_node_event(p, "DEPLOYED", "NODE_ENTER", slug="test-co",
                        ts=_iso(_now() - timedelta(seconds=100)))
        emit_node_event(p, "DEPLOYED", "NODE_FAIL", slug="test-co",
                        error_class="deploy-fail",
                        ts=_iso(_now()))
        set_triage_status(p, "qualify")

        result = g14(cases_dir=cases_dir)
        assert result.status == "FAIL", f"Expected FAIL, got {result.status}"
        assert any("DEPLOYED" in v for v in result.violations)

    def test_qualify_case_with_sla_stall_returns_fail(self, tmp_path):
        g14 = self._import_g14()
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        sla = NODES["DEPLOYED"]["sla_seconds"]
        old_ts = _now() - timedelta(seconds=sla + 9999)

        p = cases_dir / "stall001.yaml"
        emit_node_event(p, "DEPLOYED", "NODE_ENTER", slug="stall-co",
                        ts=_iso(old_ts))
        set_triage_status(p, "qualify")

        result = g14(cases_dir=cases_dir)
        assert result.status == "FAIL", f"Expected FAIL, got {result.status}"
        assert any("stalled" in v or "DEPLOYED" in v for v in result.violations)

    def test_non_qualify_case_only_returns_spec_or_pass(self, tmp_path):
        g14 = self._import_g14()
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        sla = NODES["DEPLOYED"]["sla_seconds"]
        old_ts = _now() - timedelta(seconds=sla + 9999)

        p = cases_dir / "gap001.yaml"
        emit_node_event(p, "DEPLOYED", "NODE_ENTER", slug="gap-co", ts=_iso(old_ts))
        set_triage_status(p, "gap_only")

        result = g14(cases_dir=cases_dir)
        # gap_only case: no qualify cases -> SPEC (zero qualify cases)
        assert result.status in ("SPEC", "PASS"), \
            f"Expected SPEC or PASS for gap_only-only cases, got {result.status}"

    def test_qualify_case_all_complete_returns_pass(self, tmp_path):
        g14 = self._import_g14()
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        p = cases_dir / "ok001.yaml"
        # All events within SLA and exit OK
        enter_t = _now() - timedelta(seconds=60)
        exit_t = _now() - timedelta(seconds=30)
        emit_node_event(p, "SUBMITTED", "NODE_ENTER", slug="ok-co", ts=_iso(enter_t))
        emit_node_event(p, "SUBMITTED", "NODE_EXIT_OK", slug="ok-co", ts=_iso(exit_t))
        set_triage_status(p, "qualify")

        result = g14(cases_dir=cases_dir)
        assert result.status == "PASS", f"Expected PASS, got {result.status}: {result.violations}"


# ---------------------------------------------------------------------------
# load_cases tests
# ---------------------------------------------------------------------------

class TestLoadCases:
    def test_skips_readme_and_gitkeep(self, tmp_path):
        # Create a fake README.yaml and .gitkeep
        (tmp_path / "README.md").write_text("readme", encoding="utf-8")
        (tmp_path / ".gitkeep").write_text("", encoding="utf-8")

        if _HAS_YAML:
            import yaml
            (tmp_path / "case001.yaml").write_text(
                yaml.dump({"client_id": "case001", "slug": "s", "triage_status": "qualify", "pipeline_events": []}),
                encoding="utf-8",
            )

        cases = load_cases(tmp_path)
        for c in cases:
            assert c.get("client_id") not in ("README", ".gitkeep")

    def test_returns_empty_for_absent_dir(self, tmp_path):
        absent = tmp_path / "not_here"
        cases = load_cases(absent)
        assert cases == []
