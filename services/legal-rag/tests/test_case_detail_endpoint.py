"""
tests/test_case_detail_endpoint.py — GET /cases/{case_id} 단위 테스트

커버리지:
  (a) 인증 없음 → 401
  (b) 잘못된 UUID 형식 → 400
  (c) 이준호(본인 사건) → 200 + 사건 메타 + 문서 목록
  (d) 박서연 cross-attorney 사건 → 404 (RLS 격리 실증)
  (e) 존재하지 않는 UUID → 404

DB 없이 DB 계층을 mock 해 단위 테스트.
@pytest.mark.postgres 마킹 테스트는 실 DB 없이 skip.
"""
from __future__ import annotations

import sys
import os
import uuid
import time
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# ── api import guard ──────────────────────────────────────────────────────────

try:
    from api import app, CaseDetailResponse, CaseDocumentItem
    from fastapi.testclient import TestClient
    _API_IMPORTABLE = True
except Exception as exc:
    _API_IMPORTABLE = False
    _API_IMPORT_ERR = str(exc)

skip_if_no_api = pytest.mark.skipif(
    not _API_IMPORTABLE,
    reason=f"api.py 가 import 불가 — 스킵 (이유: {_API_IMPORTABLE or ''})",
)

try:
    import jwt as _pyjwt  # noqa: F401
    _PYJWT_AVAILABLE = True
except ImportError:
    _PYJWT_AVAILABLE = False

skip_if_no_jwt = pytest.mark.skipif(
    not _PYJWT_AVAILABLE,
    reason="pyjwt not installed — run: pip install pyjwt",
)


# ── 헬퍼 ─────────────────────────────────────────────────────────────────────

def _make_token(attorney_id: str, secret: str = "test") -> str:
    import jwt
    return jwt.encode(
        {"sub": attorney_id, "exp": int(time.time()) + 3600},
        secret,
        algorithm="HS256",
    )


@asynccontextmanager
async def _rls_noop(conn, attorney_id):
    """Mock rls_session: does nothing, just yields."""
    yield


def _make_pool_mock_two_queries(fetchone_return, fetchall_return, party_rows=None):
    """Build an async pool mock for GET /cases/{case_id}.

    conn.execute is called THREE times within the same rls_session (G-2 C2):
      1st call → case meta (fetchone)
      2nd call → document list (fetchall)  — returns fetchall_return
      3rd call → party list (fetchall)     — returns party_rows (default [])

    party_rows: list of 5-tuples (id, case_id, role, name, notes).
    Pass a list with one tuple to assert party data in the response.
    """
    if party_rows is None:
        party_rows = []

    call_count = 0

    class _Cur1:
        async def fetchone(self):
            return fetchone_return

    class _CurDocs:
        async def fetchall(self):
            return fetchall_return

    class _CurParties:
        async def fetchall(self):
            return party_rows

    conn = MagicMock()

    async def _execute(sql, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _Cur1()
        if call_count == 2:
            return _CurDocs()
        return _CurParties()

    conn.execute = _execute

    @asynccontextmanager
    async def _conn_ctx():
        nonlocal call_count
        call_count = 0  # reset per connection use
        yield conn

    pool = MagicMock()
    pool.connection = _conn_ctx
    return pool


# ── Pydantic 모델 단위 테스트 ─────────────────────────────────────────────────

@skip_if_no_api
class TestCaseDetailResponseModel:
    def test_basic_fields(self):
        item = CaseDocumentItem(
            doc_id=str(uuid.uuid4()),
            title="소장",
            document_type="소장",
            ingest_status="done",
        )
        detail = CaseDetailResponse(
            case_id=str(uuid.uuid4()),
            case_number="2024가합12345",
            title="손해배상(불법행위)",
            status="active",
            documents=[item],
        )
        d = detail.model_dump()
        assert d["case_number"] == "2024가합12345"
        assert len(d["documents"]) == 1
        assert d["documents"][0]["doc_id"] == item.doc_id

    def test_optional_fields_default_none(self):
        detail = CaseDetailResponse(
            case_id=str(uuid.uuid4()),
            case_number="2024나99999",
            title="계약위반",
            status="closed",
            documents=[],
        )
        assert detail.case_type is None
        assert detail.description is None
        assert detail.opened_at is None
        assert detail.closed_at is None

    def test_empty_documents_list(self):
        detail = CaseDetailResponse(
            case_id=str(uuid.uuid4()),
            case_number="2024다00001",
            title="임차권",
            status="active",
            documents=[],
        )
        assert detail.documents == []


# ── 엔드포인트 통합(mock) 테스트 ─────────────────────────────────────────────

@skip_if_no_api
@skip_if_no_jwt
class TestCaseDetailEndpoint:
    """
    DB pool과 rls_session을 mock으로 대체해 API 레이어만 검증.
    """

    SECRET = "test"  # conftest.py 에서 LEGAL_RAG_JWT_SECRET=test 로 설정됨

    # (a) 인증 없음 → 401
    def test_no_auth_returns_401(self):
        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_two_queries(None, [])

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(f"/cases/{uuid.uuid4()}")

        assert res.status_code == 401, res.text

    # (b) 잘못된 UUID 형식 → 400
    def test_invalid_uuid_returns_400(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_two_queries(None, [])

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                "/cases/not-a-valid-uuid",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 400, res.text
        assert "not a valid UUID" in res.json()["detail"]

    # (c) 이준호 본인 사건 → 200 + 사건 메타 + 문서 목록 + 당사자 목록
    def test_own_case_returns_200_with_documents(self):
        """
        이준호가 자신이 담당하는 사건(2024가합12345)을 조회.
        DB 에서 사건 메타 + 문서 2건 + 당사자 1명 반환 → 200.

        G-2 C2: get_case 핸들러가 이제 3번째 execute 로 party 목록을 조회한다.
        mock 은 3번째 execute 에 party_rows 를 반환하도록 갱신됨.
        """
        attorney_id = str(uuid.uuid4())
        case_id = str(uuid.uuid4())
        doc_id_1 = str(uuid.uuid4())
        doc_id_2 = str(uuid.uuid4())
        party_id_1 = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        # 1st execute: case meta row
        # columns: id, case_number, title, status, case_type, summary, filed_date
        # (description=summary, opened_at=filed_date, closed_at=None 로 api.py 가 매핑)
        case_row = (
            case_id,
            "2024가합12345",
            "손해배상(불법행위)",
            "active",
            "민사",
            "차량 충돌 손해배상 사건",
            "2024-03-01",
        )
        # 2nd execute: document list rows (4-tuple: id, title, document_type, ingest_status)
        doc_rows = [
            (doc_id_1, "소장", "소장", "done"),
            (doc_id_2, "준비서면 1차", "준비서면", "pending"),
        ]
        # 3rd execute: party list rows (5-tuple: id, case_id, role, name, notes)
        party_rows = [
            (party_id_1, case_id, "plaintiff", "주식회사 한빛테크", "원고 법인."),
        ]

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_two_queries(case_row, doc_rows, party_rows=party_rows)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                f"/cases/{case_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 200, res.text
        data = res.json()
        assert data["case_id"] == case_id
        assert data["case_number"] == "2024가합12345"
        assert data["title"] == "손해배상(불법행위)"
        assert data["status"] == "active"
        assert data["case_type"] == "민사"
        assert len(data["documents"]) == 2
        assert data["documents"][0]["doc_id"] == doc_id_1
        assert data["documents"][0]["document_type"] == "소장"
        assert data["documents"][1]["ingest_status"] == "pending"
        # G-2 C2: parties 필드 확인 (OQ-11 additive)
        assert len(data["parties"]) == 1
        assert data["parties"][0]["party_id"] == party_id_1
        assert data["parties"][0]["role"] == "plaintiff"
        assert data["parties"][0]["name"] == "주식회사 한빛테크"

    # (d) 박서연 cross-attorney 사건 → 404 (RLS 격리 실증)
    def test_cross_attorney_case_returns_404(self):
        """
        RLS 격리 시나리오:
        박서연이 이준호 사건 UUID 로 GET /cases/{id} 조회.
        rls_session 컨텍스트 안에서 SELECT legal_case 가 0행 반환 → 404.
        사건의 존재 자체를 노출하지 않는다.
        """
        박서연_attorney_id = str(uuid.uuid4())
        이준호_case_id = str(uuid.uuid4())
        token = _make_token(박서연_attorney_id, self.SECRET)

        # fetchone=None → RLS에 의해 박서연은 이준호 사건을 볼 수 없음
        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_two_queries(None, [])

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                f"/cases/{이준호_case_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 404, res.text
        # 존재 여부를 누설하지 않아야 한다 (동일 메시지)
        assert res.json()["detail"] == "사건을 찾을 수 없습니다."

    # (e) 존재하지 않는 UUID → 404
    def test_nonexistent_case_returns_404(self):
        attorney_id = str(uuid.uuid4())
        nonexistent_case_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        # fetchone=None → case not found in DB
        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_two_queries(None, [])

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                f"/cases/{nonexistent_case_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 404, res.text
        assert res.json()["detail"] == "사건을 찾을 수 없습니다."


# ── CasesResponse 계약 불변 검증 ─────────────────────────────────────────────

@skip_if_no_api
class TestCasesContractUnchanged:
    """GET /cases 기존 응답 모델이 변경되지 않았음을 확인."""

    def test_cases_response_keys_unchanged(self):
        from api import CasesResponse, CaseOut
        sr_fields = set(CasesResponse.model_fields.keys())
        # G-4 pagination: `limit` and `offset` added to CasesResponse (intentional extension)
        assert {"cases", "total", "limit", "offset"} == sr_fields, \
            f"CasesResponse 필드 변경 감지: {sr_fields}"

        co_fields = set(CaseOut.model_fields.keys())
        assert {
            "case_id", "case_number", "title", "status",
            "doc_total", "doc_indexed", "doc_pending", "doc_failed",
        } == co_fields, f"CaseOut 필드 변경 감지: {co_fields}"

    def test_case_detail_response_fields(self):
        from api import CaseDetailResponse, CaseDocumentItem
        dr_fields = set(CaseDetailResponse.model_fields.keys())
        # G-2 C2 additive: 'parties' 가산 (OQ-11 CTO判定 — open-closed, documents 동일 패턴)
        assert {
            "case_id", "case_number", "title", "status",
            "case_type", "description", "opened_at", "closed_at", "documents",
            "parties",
        } == dr_fields, f"CaseDetailResponse 필드 변경 감지: {dr_fields}"

        di_fields = set(CaseDocumentItem.model_fields.keys())
        assert {"doc_id", "title", "document_type", "ingest_status"} == di_fields, \
            f"CaseDocumentItem 필드 변경 감지: {di_fields}"


# ── @pytest.mark.postgres: 실 DB 격리 통합 테스트 자리 ─────────────────────

@pytest.mark.postgres
class TestCaseDetailRLSIntegration:
    """
    실 PostgreSQL 필요 — 인프라 게이트에서 구현.

    SPEC:
      - GET /cases/<이준호_사건_UUID> Bearer 이준호 → 200, documents 포함
      - GET /cases/<이준호_사건_UUID> Bearer 박서연 → 404 (RLS 격리)
      - GET /cases/<박서연_사건_UUID> Bearer 이준호 → 404 (RLS 격리)
      - GET /cases/<이준호_사건_UUID> Bearer 이준호 → documents[].ingest_status 검증
    """

    def test_placeholder(self):
        pytest.skip("Postgres integration: implement after DB fixture is available")
