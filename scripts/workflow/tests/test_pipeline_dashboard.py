"""test_pipeline_dashboard.py -- Pure unit tests for pipeline_dashboard.py.

No live server, no network. Tests render_dashboard_html and _format_duration.

Run:
  PYTHONUTF8=1 python -m pytest scripts/workflow/tests/test_pipeline_dashboard.py -q
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup (mirrors test_ui_check.py pattern)
# ---------------------------------------------------------------------------

_WORKFLOW_DIR = Path(__file__).resolve().parent.parent
if str(_WORKFLOW_DIR) not in sys.path:
    sys.path.insert(0, str(_WORKFLOW_DIR))

from pipeline_dashboard import render_dashboard_html, _format_duration  # noqa: E402
from pipeline_monitor import aggregate_health, project_node_states, NODES  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _minimal_case(
    *,
    client_id: str = "case001",
    slug: str = "test-co",
    triage_status: str = "qualify",
    events: list[dict] | None = None,
) -> dict:
    """Build a minimal case dict that project_node_states can process."""
    return {
        "client_id": client_id,
        "slug": slug,
        "triage_status": triage_status,
        "pipeline_events": events or [],
    }


def _render(cases: list[dict], *, evidence_dir: Path | None = None, mirror_dir: Path | None = None) -> str:
    """Convenience wrapper: compute health then render HTML."""
    now = _now()
    health = aggregate_health(cases, now)
    return render_dashboard_html(
        cases,
        health,
        now,
        evidence_dir=evidence_dir or Path("/nonexistent/evidence"),
        mirror_dir=mirror_dir,
    )


# ---------------------------------------------------------------------------
# Test: empty cases -> valid idle HTML
# ---------------------------------------------------------------------------

class TestEmptyCases:
    def test_returns_html_string(self, tmp_path):
        html = _render([])
        assert isinstance(html, str)
        assert "<html" in html

    def test_contains_idle_message(self, tmp_path):
        html = _render([])
        assert "pipeline idle" in html.lower() or "no cases" in html.lower()

    def test_no_exception_on_empty(self, tmp_path):
        # Must not raise
        _render([])


# ---------------------------------------------------------------------------
# Test: qualify case with completed/in_progress nodes renders correctly
# ---------------------------------------------------------------------------

class TestQualifyCase:
    def _make_case(self) -> dict:
        now = _now()
        enter_submit = _iso(now - timedelta(seconds=600))
        exit_submit = _iso(now - timedelta(seconds=500))
        enter_triage = _iso(now - timedelta(seconds=400))
        exit_triage = _iso(now - timedelta(seconds=300))
        enter_deploy = _iso(now - timedelta(seconds=100))
        return _minimal_case(
            slug="acme-corp",
            events=[
                {"node_id": "SUBMITTED", "event": "NODE_ENTER", "ts": enter_submit, "error_class": None},
                {"node_id": "SUBMITTED", "event": "NODE_EXIT_OK", "ts": exit_submit, "error_class": None},
                {"node_id": "TRIAGED", "event": "NODE_ENTER", "ts": enter_triage, "error_class": None},
                {"node_id": "TRIAGED", "event": "NODE_EXIT_OK", "ts": exit_triage, "error_class": None},
                {"node_id": "DEPLOYED", "event": "NODE_ENTER", "ts": enter_deploy, "error_class": None},
            ],
        )

    def test_slug_appears_in_html(self):
        html = _render([self._make_case()])
        assert "acme-corp" in html

    def test_node_chips_rendered(self):
        html = _render([self._make_case()])
        # Qualify path chips should be present
        assert "SUBMITTED" in html
        assert "DEPLOYED" in html

    def test_contains_html_structure(self):
        html = _render([self._make_case()])
        assert "<html" in html
        assert "</html>" in html


# ---------------------------------------------------------------------------
# Test: failed node on DEPLOYED renders drill-in block
# ---------------------------------------------------------------------------

class TestFailedNode:
    def _make_failed_case(self) -> dict:
        now = _now()
        return _minimal_case(
            slug="fail-slug",
            events=[
                {"node_id": "DEPLOYED", "event": "NODE_ENTER",
                 "ts": _iso(now - timedelta(seconds=200)), "error_class": None},
                {"node_id": "DEPLOYED", "event": "NODE_FAIL",
                 "ts": _iso(now - timedelta(seconds=50)), "error_class": "deploy-fail"},
            ],
        )

    def test_error_class_appears_in_html(self):
        html = _render([self._make_failed_case()])
        assert "deploy-fail" in html

    def test_failed_status_appears(self):
        html = _render([self._make_failed_case()])
        # Either the word FAIL or the chip color for red should be present
        assert "FAIL" in html or "failed" in html.lower()

    def test_slug_in_drill_in(self):
        html = _render([self._make_failed_case()])
        assert "fail-slug" in html

    def test_dwell_rendered(self):
        html = _render([self._make_failed_case()])
        # Some duration string should be in the drill-in table
        # dwell ~150s -> "2m" or "3m"
        assert any(x in html for x in ["m</", "s</", "h </"])


# ---------------------------------------------------------------------------
# Test: PII-free -- stray email/free_text keys must not reach HTML
# ---------------------------------------------------------------------------

class TestPiiSafety:
    def _make_pii_case(self) -> dict:
        """Case that includes stray PII-like top-level keys."""
        case = _minimal_case(slug="pii-test", triage_status="qualify")
        # Inject stray PII keys that should be filtered out
        case["email"] = "secret@example.com"
        case["free_text"] = "This is confidential free text content"
        case["name"] = "John Doe"
        case["phone"] = "010-1234-5678"
        return case

    def test_email_not_in_html(self):
        html = _render([self._make_pii_case()])
        assert "secret@example.com" not in html

    def test_free_text_not_in_html(self):
        html = _render([self._make_pii_case()])
        assert "confidential free text content" not in html

    def test_name_not_in_html(self):
        html = _render([self._make_pii_case()])
        # "John Doe" should not appear; slug "pii-test" should
        assert "John Doe" not in html

    def test_phone_not_in_html(self):
        html = _render([self._make_pii_case()])
        assert "010-1234-5678" not in html

    def test_safe_slug_still_present(self):
        html = _render([self._make_pii_case()])
        assert "pii-test" in html


# ---------------------------------------------------------------------------
# Test: _format_duration boundaries
# ---------------------------------------------------------------------------

class TestFormatDuration:
    def test_45_seconds(self):
        assert _format_duration(45) == "45s"

    def test_59_seconds(self):
        assert _format_duration(59) == "59s"

    def test_60_seconds_is_one_minute(self):
        # 60/60 = 1.0 -> "1m"
        assert _format_duration(60) == "1m"

    def test_90_seconds(self):
        # 90/60 = 1.5 -> f"{1.5:.0f}m" = "2m" (rounds half to even / rounds up)
        result = _format_duration(90)
        assert result in ("1m", "2m")  # Python round-half-even: 1.5 rounds to 2

    def test_120_seconds(self):
        assert _format_duration(120) == "2m"

    def test_3600_seconds_is_one_hour(self):
        assert _format_duration(3600) == "1h 0m"

    def test_7384_seconds(self):
        # 7384 // 3600 = 2h, (7384 % 3600) // 60 = 3m
        assert _format_duration(7384) == "2h 3m"

    def test_zero(self):
        assert _format_duration(0) == "0s"
