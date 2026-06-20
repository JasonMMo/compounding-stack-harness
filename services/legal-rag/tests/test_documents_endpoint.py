"""
tests/test_documents_endpoint.py — GET /documents/{source_type}/{source_id} 단위 테스트

커버리지:
  (a) precedent 원문 200 — full_text 존재
  (b) precedent full_text NULL → holding fallback (body_is_holding_fallback: true)
  (c) case_document 본인 사건 200
  (d) 타 변호사 case_document → 404 격리 (RLS 격리 시나리오)
  (e) 잘못된 source_type → 400
  (f) 인증 없음 → 401

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
    from api import app, DocumentResponse
    from fastapi.testclient import TestClient
    _API_IMPORTABLE = True
except Exception as exc:
    _API_IMPORTABLE = False
    _API_IMPORT_ERR = str(exc)

skip_if_no_api = pytest.mark.skipif(
    not _API_IMPORTABLE,
    reason=f"api.py 가 import 불가 — 스킵 (이유: {_API_IMPORTABLE or ''})",
)

# pyjwt 필요
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


def _make_pool_mock(fetchone_return):
    """Build a minimal async context-manager pool mock.

    fetchone_return: the value returned by cur.fetchone().
    """
    cur = MagicMock()
    cur.fetchone = AsyncMock(return_value=fetchone_return)

    conn = MagicMock()
    conn.execute = AsyncMock(return_value=cur)

    @asynccontextmanager
    async def _conn_ctx():
        yield conn

    pool = MagicMock()
    pool.connection = _conn_ctx
    return pool


# ── DocumentResponse 모델 테스트 ──────────────────────────────────────────────

@skip_if_no_api
class TestDocumentResponseModel:
    def test_precedent_fields(self):
        doc = DocumentResponse(
            source_type="precedent",
            source_id=str(uuid.uuid4()),
            title="대법원 2020다12345",
            citation="대법원 2020다12345",
            court="대법원",
            decided_date="2020-06-01",
            case_type="민사",
            keywords="손해배상, 계약",
            body="본문 전문...",
            body_is_holding_fallback=False,
        )
        d = doc.model_dump()
        assert d["source_type"] == "precedent"
        assert d["body_is_holding_fallback"] is False
        assert d["court"] == "대법원"

    def test_holding_fallback_flag(self):
        doc = DocumentResponse(
            source_type="precedent",
            source_id=str(uuid.uuid4()),
            body="판시요지 텍스트",
            body_is_holding_fallback=True,
        )
        assert doc.body_is_holding_fallback is True

    def test_case_document_fields(self):
        doc = DocumentResponse(
            source_type="case_document",
            source_id=str(uuid.uuid4()),
            title="2024가합10001 소장",
            document_type="소장",
            filed_at="2024-03-01",
            body="소장 본문...",
        )
        d = doc.model_dump()
        assert d["source_type"] == "case_document"
        assert d["document_type"] == "소장"
        assert d["citation"] is None  # 사건문서에는 없음

    def test_defaults(self):
        doc = DocumentResponse(source_type="precedent", source_id=str(uuid.uuid4()))
        assert doc.body is None
        assert doc.body_is_holding_fallback is False
        assert doc.court is None


# ── 엔드포인트 통합(mock) 테스트 ─────────────────────────────────────────────

@skip_if_no_api
@skip_if_no_jwt
class TestDocumentsEndpoint:
    """
    DB pool과 rls_session을 mock으로 대체해 API 레이어만 검증.
    실제 SQL 실행 없이 응답 계약 준수 여부를 확인한다.
    """

    SECRET = "test"  # conftest.py 에서 LEGAL_RAG_JWT_SECRET=test 로 설정됨

    def _client_with_mocks(self, fetchone_return):
        """TestClient + pool/rls mock 설정."""
        from api import _get_pool  # noqa: F401 — verify import path
        import api as api_mod
        import db as db_mod

        pool_mock = _make_pool_mock(fetchone_return)

        # _pool 직접 패치 (모듈 전역)
        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=False)
            yield client

    # (a) precedent 원문 200 — full_text 존재
    def test_precedent_with_full_text_returns_200(self):
        source_id = str(uuid.uuid4())
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        # row: citation, court, decided_date, case_type, holding, full_text, keywords
        row = ("대법원 2020다12345", "대법원", "2020-06-01", "민사", "판시요지", "전문 본문", "키워드1")

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock(row)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                f"/documents/precedent/{source_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 200, res.text
        data = res.json()
        assert data["source_type"] == "precedent"
        assert data["body"] == "전문 본문"
        assert data["body_is_holding_fallback"] is False
        assert data["court"] == "대법원"

    # (b) precedent full_text NULL → holding fallback
    def test_precedent_null_full_text_returns_holding_fallback(self):
        source_id = str(uuid.uuid4())
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        # full_text=None → holding 을 body 로 반환, body_is_holding_fallback=True
        row = ("대법원 2021다99999", "대법원", "2021-01-01", "민사", "판시요지 텍스트", None, None)

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock(row)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                f"/documents/precedent/{source_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 200, res.text
        data = res.json()
        assert data["body"] == "판시요지 텍스트"
        assert data["body_is_holding_fallback"] is True

    # (c) case_document 본인 사건 200
    def test_case_document_own_case_returns_200(self):
        source_id = str(uuid.uuid4())
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        # row: document_type, title, filed_at, content_text
        row = ("소장", "2024가합10001 소장", "2024-03-01", "소장 본문 내용")

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock(row)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                f"/documents/case_document/{source_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 200, res.text
        data = res.json()
        assert data["source_type"] == "case_document"
        assert data["title"] == "2024가합10001 소장"
        assert data["body"] == "소장 본문 내용"
        assert data["body_is_holding_fallback"] is False

    # (d) 타 변호사 case_document → 404 (RLS 격리 시나리오: fetchone=None)
    def test_cross_attorney_case_document_returns_404(self):
        """
        RLS 격리 시나리오: 박서연이 이준호 사건문서 UUID 로 조회 시
        rls_session 컨텍스트 안에서 SELECT 가 0행을 반환 → 404.
        존재 여부를 노출하지 않는다.
        """
        source_id = str(uuid.uuid4())
        attorney_id = str(uuid.uuid4())  # 이 변호사는 해당 문서에 접근 권한 없음
        token = _make_token(attorney_id, self.SECRET)

        # fetchone=None → RLS 에 의해 행이 보이지 않음
        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock(None)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                f"/documents/case_document/{source_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 404, res.text
        # 존재 여부를 누설하지 않아야 한다 (동일 메시지)
        assert res.json()["detail"] == "원문을 찾을 수 없습니다."

    # (e) 잘못된 source_type → 400
    def test_invalid_source_type_returns_400(self):
        source_id = str(uuid.uuid4())
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock(None)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                f"/documents/invalid_type/{source_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 400, res.text

    # (f) 인증 없음 → 401
    def test_no_auth_returns_401(self):
        source_id = str(uuid.uuid4())

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock(None)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(f"/documents/precedent/{source_id}")

        assert res.status_code == 401, res.text

    # (g) source_id 가 UUID 가 아닌 경우 → 400
    def test_invalid_source_id_uuid_returns_400(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock(None)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                "/documents/precedent/not-a-valid-uuid",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 400, res.text

    # (h) precedent 존재하지 않으면 404
    def test_precedent_not_found_returns_404(self):
        source_id = str(uuid.uuid4())
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock(None)  # DB 에 없음

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                f"/documents/precedent/{source_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 404, res.text
        assert res.json()["detail"] == "원문을 찾을 수 없습니다."


# ── /search 계약 불변 검증 ────────────────────────────────────────────────────

@skip_if_no_api
class TestSearchContractUnchanged:
    """
    /documents 추가로 /search 응답 모델이 변경되지 않았음을 확인.
    SearchResponse / CitationOut 키 목록 고정.
    """

    def test_search_response_keys_unchanged(self):
        from api import SearchResponse, CitationOut
        import inspect

        sr_fields = set(SearchResponse.model_fields.keys())
        expected_sr = {"query_log_id", "total_results", "results", "note"}
        assert expected_sr == sr_fields, f"SearchResponse 필드 변경 감지: {sr_fields}"

        co_fields = set(CitationOut.model_fields.keys())
        expected_co = {
            "chunk_id", "source_type", "source_id", "case_id",
            "chunk_index", "chunk_text_excerpt", "rrf_score",
            "fts_rank", "ann_rank", "relevance",
            "case_number", "court",
            "decision_date", "holding_summary", "document_title", "document_type",
        }
        assert expected_co == co_fields, f"CitationOut 필드 변경 감지: {co_fields}"


# ── @pytest.mark.postgres: 실 DB 격리 통합 테스트 자리 ─────────────────────

@pytest.mark.postgres
class TestDocumentsRLSIntegration:
    """
    실 PostgreSQL 필요 — 인프라 게이트에서 구현.

    SPEC:
      - GET /documents/case_document/<이준호사건문서UUID> Bearer 이준호 → 200
      - GET /documents/case_document/<이준호사건문서UUID> Bearer 박서연 → 404
      - GET /documents/precedent/<precedent_UUID> Bearer 이준호 → 200 (firm-wide 접근)
      - GET /documents/precedent/<precedent_UUID> Bearer 박서연 → 200 (firm-wide 접근)
    """

    def test_placeholder(self):
        pytest.skip("Postgres integration: implement after DB fixture is available")
