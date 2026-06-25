"""
tests/test_billing.py — L1 guard for K3 타임시트·빌링 청구 롤업 (Growth K3).

What this pins:
  1. billing_summary dict: billable_total / unbilled_total / total_minutes 계산 정확성
  2. unbilled_ids: billable=True AND status!="billed" 인 id 집합
  3. entity_type!="time-entry" 이면 billing_summary=None, unbilled_ids=set() (개방-폐쇄)
  4. 렌더: billing_summary 배너가 time-entry 목록에만 렌더됨
     (entity_type!="time-entry" 이면 billing-summary 클래스 미출력)

Pattern mirrors test_entity_list_params.py — mock _proxy_request, exercise Flask route.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

_ADAPTER_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_ADAPTER_ROOT))

import server  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(monkeypatch):
    """Flask test client with auth session pre-set."""
    server.app.config["TESTING"] = True
    server.app.config["SECRET_KEY"] = "test-secret"
    with server.app.test_client() as c:
        with server.app.test_request_context():
            pass
        with c.session_transaction() as sess:
            sess["token"] = "test-token"
            sess["user"] = "test@example.com"
        yield c


# ---------------------------------------------------------------------------
# Sample time-entry items covering all status / billable combinations
# ---------------------------------------------------------------------------

_ITEMS_TIME_ENTRY = [
    # billable=True, status=billed    → contributes to billable_total only
    {"id": "id-1", "case_id": "c1", "employee_id": "e1",
     "work_date": "2024-02-10", "minutes": 120, "description": "소장 검토",
     "billable": True, "hourly_rate": 400000, "amount": 800000, "status": "billed"},
    # billable=True, status=submitted → contributes to billable_total AND unbilled_total
    {"id": "id-2", "case_id": "c1", "employee_id": "e2",
     "work_date": "2024-04-10", "minutes": 60,  "description": "기일 출석",
     "billable": True, "hourly_rate": 400000, "amount": 400000, "status": "submitted"},
    # billable=True, status=draft     → contributes to billable_total AND unbilled_total
    {"id": "id-3", "case_id": "c2", "employee_id": "e1",
     "work_date": "2024-05-01", "minutes": 90,  "description": "준비서면",
     "billable": True, "hourly_rate": 200000, "amount": 300000, "status": "draft"},
    # billable=False                  → excluded from all totals
    {"id": "id-4", "case_id": "c2", "employee_id": "e1",
     "work_date": "2024-05-02", "minutes": 45,  "description": "내부 회의",
     "billable": False, "hourly_rate": 150000, "amount": 0,      "status": "draft"},
]

# Expected values from the items above:
#   billable_total  = 800000 + 400000 + 300000 = 1,500,000
#   unbilled_total  = 400000 + 300000           =   700,000
#   total_minutes   = 120 + 60 + 90             =   270
#   unbilled_ids    = {"id-2", "id-3"}
_EXPECTED_BILLABLE_TOTAL = 1_500_000
_EXPECTED_UNBILLED_TOTAL =   700_000
_EXPECTED_TOTAL_MINUTES  =   270
_EXPECTED_UNBILLED_IDS   = {"id-2", "id-3"}


def _make_proxy_response(items: list) -> tuple[dict, int]:
    return {"items": items, "total": len(items)}, 200


# ---------------------------------------------------------------------------
# Unit-level: compute billing_summary directly from server logic
# (mirrors the computation in entity_list without HTTP overhead)
# ---------------------------------------------------------------------------

def _compute_billing(items: list) -> tuple[dict, set]:
    """Replicate the K3 billing rollup logic from server.entity_list."""
    billable_total = 0
    unbilled_total = 0
    total_minutes = 0
    unbilled_ids: set = set()
    for it in items:
        is_billable = it.get("billable") in (True, "true", "True", 1, "1")
        amt = int(it.get("amount") or 0)
        mins = int(it.get("minutes") or 0)
        if is_billable:
            billable_total += amt
            total_minutes += mins
            if str(it.get("status", "")).lower() != "billed":
                unbilled_total += amt
                unbilled_ids.add(it.get("id"))
    summary = {
        "billable_total": billable_total,
        "unbilled_total": unbilled_total,
        "total_minutes": total_minutes,
    }
    return summary, unbilled_ids


class TestBillingRollupCalculation:
    """Pins the arithmetic of billable_total / unbilled_total / total_minutes."""

    def test_billable_total(self):
        summary, _ = _compute_billing(_ITEMS_TIME_ENTRY)
        assert summary["billable_total"] == _EXPECTED_BILLABLE_TOTAL

    def test_unbilled_total(self):
        summary, _ = _compute_billing(_ITEMS_TIME_ENTRY)
        assert summary["unbilled_total"] == _EXPECTED_UNBILLED_TOTAL

    def test_total_minutes(self):
        summary, _ = _compute_billing(_ITEMS_TIME_ENTRY)
        assert summary["total_minutes"] == _EXPECTED_TOTAL_MINUTES

    def test_unbilled_ids(self):
        _, unbilled_ids = _compute_billing(_ITEMS_TIME_ENTRY)
        assert unbilled_ids == _EXPECTED_UNBILLED_IDS

    def test_non_billable_excluded_from_all(self):
        """Non-billable entry (id-4) must not appear in any total or unbilled_ids."""
        summary, unbilled_ids = _compute_billing(_ITEMS_TIME_ENTRY)
        assert "id-4" not in unbilled_ids
        # amount for id-4 is 0 but we verify the sum doesn't accidentally include it
        # billable_total must equal exactly the three billable entries
        assert summary["billable_total"] == _EXPECTED_BILLABLE_TOTAL

    def test_billed_not_in_unbilled_ids(self):
        """billed entry (id-1) must NOT be in unbilled_ids."""
        _, unbilled_ids = _compute_billing(_ITEMS_TIME_ENTRY)
        assert "id-1" not in unbilled_ids

    def test_all_billed_gives_zero_unbilled(self):
        all_billed = [
            {"id": "x1", "billable": True,  "amount": 500000, "minutes": 60,  "status": "billed"},
            {"id": "x2", "billable": True,  "amount": 300000, "minutes": 30,  "status": "billed"},
        ]
        summary, unbilled_ids = _compute_billing(all_billed)
        assert summary["unbilled_total"] == 0
        assert unbilled_ids == set()

    def test_empty_items(self):
        summary, unbilled_ids = _compute_billing([])
        assert summary == {"billable_total": 0, "unbilled_total": 0, "total_minutes": 0}
        assert unbilled_ids == set()

    def test_hours_minutes_math(self):
        """270 minutes = 4h 30m — verify caller can derive correctly."""
        summary, _ = _compute_billing(_ITEMS_TIME_ENTRY)
        mins = summary["total_minutes"]
        assert mins // 60 == 4
        assert mins % 60 == 30


# ---------------------------------------------------------------------------
# Integration: Flask route renders billing-summary banner for time-entry
# ---------------------------------------------------------------------------

class TestBillingRenderIntegration:
    """Exercises the Flask entity_list route end-to-end via test client."""

    def test_billing_banner_present_for_time_entry(self, client, monkeypatch):
        """billing-summary banner must appear when entity_type==time-entry."""
        monkeypatch.setattr(
            server, "_proxy_request",
            lambda *a, **kw: _make_proxy_response(_ITEMS_TIME_ENTRY),
        )
        resp = client.get("/entities/time-entry")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert "billing-summary" in body

    def test_billing_banner_absent_for_other_entity(self, client, monkeypatch):
        """billing-summary banner must NOT appear for non-time-entry entities."""
        other_items = [
            {"id": "c1", "case_number": "CASE-001", "title": "테스트 사건",
             "status": "active", "case_type": "civil"},
        ]
        monkeypatch.setattr(
            server, "_proxy_request",
            lambda *a, **kw: _make_proxy_response(other_items),
        )
        resp = client.get("/entities/legal-case")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert "billing-summary" not in body

    def test_unbilled_badge_present(self, client, monkeypatch):
        """미청구 배지(badge--billing)는 time-entry 목록에서 미청구 행에 출력됨."""
        monkeypatch.setattr(
            server, "_proxy_request",
            lambda *a, **kw: _make_proxy_response(_ITEMS_TIME_ENTRY),
        )
        resp = client.get("/entities/time-entry")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert "badge--billing" in body

    def test_billing_amounts_in_banner(self, client, monkeypatch):
        """배너에 billable_total과 unbilled_total 금액이 포함됨."""
        monkeypatch.setattr(
            server, "_proxy_request",
            lambda *a, **kw: _make_proxy_response(_ITEMS_TIME_ENTRY),
        )
        resp = client.get("/entities/time-entry")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        # 1,500,000 formatted with comma
        assert "1,500,000" in body
        # 700,000 formatted with comma
        assert "700,000" in body
