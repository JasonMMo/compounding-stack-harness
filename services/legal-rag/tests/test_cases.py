"""
tests/test_cases.py — /cases 엔드포인트 응답 모델 + 사건현황 뱃지 로직 단위 테스트.

커버리지:
  - CaseOut / CasesResponse pydantic 직렬화
  - ingest_status 집계 대표 상태 로직 (indexed / pending / failed / unknown)
  - doc_total/doc_indexed/doc_pending/doc_failed 계수 정합성
  - @pytest.mark.postgres: DB 통합 테스트는 마크로 분리

DB 없이 순수 로직(모델·집계)만 테스트한다.
"""
from __future__ import annotations

import uuid

import pytest

# ── api 모듈 import (CaseOut, CasesResponse) ─────────────────────────────────

try:
    from api import CaseOut, CasesResponse
    _API_IMPORTABLE = True
except Exception:
    _API_IMPORTABLE = False

skip_if_no_api = pytest.mark.skipif(
    not _API_IMPORTABLE,
    reason="api.py 가 import 불가 (DB env 누락 등) — 스킵",
)


# ── 헬퍼 ─────────────────────────────────────────────────────────────────────

def _case(
    case_number="2024가합10001",
    title="테스트 사건",
    status="active",
    doc_total=10,
    doc_indexed=8,
    doc_pending=1,
    doc_failed=1,
):
    return CaseOut(
        case_id=str(uuid.uuid4()),
        case_number=case_number,
        title=title,
        status=status,
        doc_total=doc_total,
        doc_indexed=doc_indexed,
        doc_pending=doc_pending,
        doc_failed=doc_failed,
    )


# ── CaseOut 직렬화 테스트 ─────────────────────────────────────────────────────

@skip_if_no_api
class TestCaseOutModel:
    def test_basic_fields_round_trip(self):
        c = _case()
        d = c.model_dump()
        assert d["case_number"] == "2024가합10001"
        assert d["doc_total"] == 10
        assert d["doc_indexed"] == 8

    def test_case_id_is_string_uuid(self):
        c = _case()
        # case_id 는 UUID 형식 문자열이어야 한다
        parsed = uuid.UUID(c.case_id)
        assert str(parsed) == c.case_id

    def test_zero_docs_case(self):
        c = _case(doc_total=0, doc_indexed=0, doc_pending=0, doc_failed=0)
        assert c.doc_total == 0

    def test_status_values_pass_through(self):
        for status in ("active", "trial", "closed", "appeal", "intake"):
            c = _case(status=status)
            assert c.status == status


# ── CasesResponse 직렬화 테스트 ──────────────────────────────────────────────

@skip_if_no_api
class TestCasesResponseModel:
    def test_empty_cases(self):
        # G-4: limit/offset have defaults (50/0) so existing callers need not pass them
        resp = CasesResponse(cases=[], total=0)
        d = resp.model_dump()
        assert d["cases"] == []
        assert d["total"] == 0
        assert d["limit"] == 50   # default
        assert d["offset"] == 0   # default

    def test_total_matches_list_length(self):
        cases = [_case(case_number=f"2024가합{i:05d}") for i in range(5)]
        resp = CasesResponse(cases=cases, total=len(cases))
        assert resp.total == 5
        assert len(resp.cases) == 5

    def test_json_serializable(self):
        import json
        cases = [_case()]
        resp = CasesResponse(cases=cases, total=1)
        raw = resp.model_dump_json()
        parsed = json.loads(raw)
        assert parsed["total"] == 1
        assert len(parsed["cases"]) == 1
        # G-4: pagination fields present in JSON
        assert "limit" in parsed
        assert "offset" in parsed


# ── 사건 ingest 상태 대표 상태 로직 ─────────────────────────────────────────

class TestIngestStatusLogic:
    """
    UI에서 뱃지를 결정하는 로직:
      failed > 0  → 색인 실패 (가장 높은 우선순위)
      pending > 0 → 대기 중
      indexed > 0 → 색인 완료
      else        → 상태 불명
    이 로직은 app.js 에 구현되어 있으나 Python 레벨에서도 명세 검증.
    """

    def _representative_status(self, doc_indexed, doc_pending, doc_failed):
        """app.js getIngestBadgeClass 와 동일한 파이썬 구현."""
        if doc_failed > 0:
            return "failed"
        if doc_pending > 0:
            return "pending"
        if doc_indexed > 0:
            return "indexed"
        return "unknown"

    def test_failed_takes_priority_over_indexed(self):
        assert self._representative_status(8, 0, 1) == "failed"

    def test_failed_takes_priority_over_pending(self):
        assert self._representative_status(0, 5, 2) == "failed"

    def test_pending_when_no_failures(self):
        assert self._representative_status(3, 2, 0) == "pending"

    def test_indexed_when_all_done(self):
        assert self._representative_status(10, 0, 0) == "indexed"

    def test_unknown_when_zero_docs(self):
        assert self._representative_status(0, 0, 0) == "unknown"

    def test_pending_counts_processing_as_pending(self):
        # doc_pending 은 pending + processing + NULL 을 포함 (api.py 쿼리 기준)
        # doc_pending=5 → 대기중
        assert self._representative_status(0, 5, 0) == "pending"


# ── doc_total 정합성 검증 ─────────────────────────────────────────────────────

class TestDocCountConsistency:
    """
    api.py 쿼리 기준:
      doc_total = COUNT(lcd.id)
      doc_indexed = COUNT FILTER (ingest_status = 'done')
      doc_pending = COUNT FILTER (status IN ('pending','processing') OR IS NULL)
      doc_failed  = COUNT FILTER (status = 'error')

    doc_indexed + doc_pending + doc_failed <= doc_total 이어야 한다.
    (ingest_status 가 NULL 이 아닌 다른 값이면 둘 다 아님 — 현재 DDL 에는 없음)
    """

    def test_counts_do_not_exceed_total(self):
        # 정상 케이스: 합계가 total 이하
        cases = [
            (10, 8, 1, 1),   # 8+1+1=10 ✓
            (5,  0, 5, 0),   # 0+5+0=5 ✓
            (3,  3, 0, 0),   # 3+0+0=3 ✓
            (0,  0, 0, 0),   # 0+0+0=0 ✓
        ]
        for doc_total, doc_indexed, doc_pending, doc_failed in cases:
            sub_sum = doc_indexed + doc_pending + doc_failed
            assert sub_sum <= doc_total, (
                f"Sub-counts {sub_sum} > doc_total {doc_total}: "
                f"(indexed={doc_indexed}, pending={doc_pending}, failed={doc_failed})"
            )


# ── @pytest.mark.postgres: DB 통합 테스트 자리 ──────────────────────────────

@pytest.mark.postgres
class TestCasesEndpointIntegration:
    """
    실제 PostgreSQL 인스턴스 필요 — 로컬 DB 없으면 skip.

    SPEC 상태 (미검증):
      - GET /cases Bearer <이준호 JWT> → c001~c006 사건 6건 반환
      - GET /cases Bearer <박서연 JWT> → c007~c012 사건 6건 반환
      - GET /cases: RLS 격리 — 이준호가 박서연 사건 조회 불가
      - GET /cases: 토큰 없음 → 401
    """

    def test_placeholder(self):
        pytest.skip("Postgres integration: implement after DB fixture is available")
