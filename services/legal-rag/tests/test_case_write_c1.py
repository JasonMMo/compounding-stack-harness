"""
tests/test_case_write_c1.py — G-2 C1 사건 메타 쓰기 단위 테스트

커버리지:
  - CaseCreateIn / CaseUpdateIn Pydantic 모델 검증 (enum, 길이, 공백, 날짜 형식)
  - POST /cases mock 통합 테스트 (201 반환, CaseOut 직렬화)
  - PATCH /cases/{id} mock 통합 테스트 (200, 404 RLS 은폐, 400 UUID)
  - 기존 모델(CaseOut, CaseDetailResponse) 불변 검증

AC-02~AC-04 (RLS 라이브): @pytest.mark.postgres — live DB 없으면 skip.
DDL 보고: case_type 허용값에 'other' 없음 (DDL CHECK 기준).

실행:
  cd services/legal-rag && python -m pytest tests/test_case_write_c1.py -q
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
    from api import (
        app,
        CaseCreateIn,
        CaseUpdateIn,
        CaseOut,
        CaseDetailResponse,
        CaseDocumentItem,
    )
    from fastapi.testclient import TestClient
    _API_IMPORTABLE = True
    _API_IMPORT_ERR = ""
except Exception as exc:
    _API_IMPORTABLE = False
    _API_IMPORT_ERR = str(exc)

skip_if_no_api = pytest.mark.skipif(
    not _API_IMPORTABLE,
    reason=f"api.py import 불가: {_API_IMPORT_ERR}",
)

try:
    import jwt as _pyjwt  # noqa: F401
    _PYJWT_AVAILABLE = True
except ImportError:
    _PYJWT_AVAILABLE = False

skip_if_no_jwt = pytest.mark.skipif(
    not _PYJWT_AVAILABLE,
    reason="pyjwt not installed",
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
    yield


def _make_pool_mock_single_execute(fetchone_return=None, fetchall_return=None):
    """pool mock: execute 호출 순서에 따라 fetchone/fetchall 반환."""
    call_count = 0

    class _CurOne:
        async def fetchone(self):
            return fetchone_return

    class _CurAll:
        async def fetchall(self):
            return fetchall_return or []

    conn = MagicMock()

    async def _execute(sql, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _CurOne()
        return _CurAll()

    conn.execute = _execute

    @asynccontextmanager
    async def _conn_ctx():
        nonlocal call_count
        call_count = 0
        yield conn

    pool = MagicMock()
    pool.connection = _conn_ctx
    return pool


# ── CaseCreateIn 모델 검증 ────────────────────────────────────────────────────

@skip_if_no_api
class TestCaseCreateInModel:
    """CaseCreateIn Pydantic 검증 규칙."""

    def test_minimum_valid(self):
        m = CaseCreateIn(case_number="2026가합99001", title="손해배상")
        assert m.status == "intake"
        assert m.case_type is None

    def test_case_number_no_space(self):
        with pytest.raises(Exception):
            CaseCreateIn(case_number="2026 가합99001", title="손해배상")

    def test_case_number_max_length(self):
        with pytest.raises(Exception):
            CaseCreateIn(case_number="A" * 65, title="손해배상")

    def test_title_max_length(self):
        with pytest.raises(Exception):
            CaseCreateIn(case_number="2026가합99001", title="A" * 513)

    def test_description_max_length(self):
        with pytest.raises(Exception):
            CaseCreateIn(case_number="2026가합99001", title="손해배상", description="A" * 4001)

    def test_valid_case_types(self):
        for ct in ("civil", "criminal", "administrative", "family", "commercial"):
            m = CaseCreateIn(case_number="X", title="T", case_type=ct)
            assert m.case_type == ct

    def test_invalid_case_type_other(self):
        """DDL CHECK 에 'other' 없음 — 422 검증 실패여야 함."""
        with pytest.raises(Exception):
            CaseCreateIn(case_number="X", title="T", case_type="other")

    def test_invalid_case_type_unknown(self):
        with pytest.raises(Exception):
            CaseCreateIn(case_number="X", title="T", case_type="unknown")

    def test_valid_statuses(self):
        for s in ("intake", "active", "trial", "appeal", "closed", "withdrawn"):
            m = CaseCreateIn(case_number="X", title="T", status=s)
            assert m.status == s

    def test_invalid_status(self):
        with pytest.raises(Exception):
            CaseCreateIn(case_number="X", title="T", status="pending")

    def test_opened_at_valid_format(self):
        m = CaseCreateIn(case_number="X", title="T", opened_at="2026-06-22")
        assert m.opened_at == "2026-06-22"

    def test_opened_at_invalid_format(self):
        with pytest.raises(Exception):
            CaseCreateIn(case_number="X", title="T", opened_at="22/06/2026")

    def test_case_type_null_allowed(self):
        m = CaseCreateIn(case_number="X", title="T", case_type=None)
        assert m.case_type is None


# ── CaseUpdateIn 모델 검증 ────────────────────────────────────────────────────

@skip_if_no_api
class TestCaseUpdateInModel:
    """CaseUpdateIn Pydantic 검증 규칙 (partial PATCH)."""

    def test_all_none_is_valid(self):
        """제출 필드 없음 → 유효 (no-op update)."""
        m = CaseUpdateIn()
        assert m.title is None
        assert m.status is None

    def test_partial_update(self):
        m = CaseUpdateIn(title="새 사건명", status="active")
        assert m.title == "새 사건명"
        assert m.status == "active"

    def test_invalid_case_type_other(self):
        with pytest.raises(Exception):
            CaseUpdateIn(case_type="other")

    def test_invalid_status(self):
        with pytest.raises(Exception):
            CaseUpdateIn(status="pending")

    def test_closed_at_valid_format(self):
        m = CaseUpdateIn(closed_at="2026-12-31")
        assert m.closed_at == "2026-12-31"

    def test_closed_at_invalid_format(self):
        with pytest.raises(Exception):
            CaseUpdateIn(closed_at="31-12-2026")

    def test_title_max_length(self):
        with pytest.raises(Exception):
            CaseUpdateIn(title="A" * 513)

    def test_description_max_length(self):
        with pytest.raises(Exception):
            CaseUpdateIn(description="A" * 4001)

    def test_case_number_not_a_field(self):
        """case_number 는 CaseUpdateIn 에 없어야 한다 (immutable)."""
        fields = set(CaseUpdateIn.model_fields.keys())
        assert "case_number" not in fields, "case_number 는 PATCH 에서 immutable"
        assert "assigned_attorney_id" not in fields
        assert "partner_id" not in fields


# ── POST /cases 엔드포인트 mock 테스트 ───────────────────────────────────────

@skip_if_no_api
@skip_if_no_jwt
class TestCreateCaseEndpoint:
    SECRET = "test"

    def test_no_auth_returns_401(self):
        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_single_execute(None)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.post("/cases", json={"case_number": "X", "title": "T"})

        assert res.status_code == 401, res.text

    def test_invalid_body_returns_422(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_single_execute(None)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            # case_type='other' 는 DDL CHECK 위반 → 422
            res = client.post(
                "/cases",
                json={"case_number": "X", "title": "T", "case_type": "other"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 422, res.text

    def test_success_returns_201_case_out(self):
        attorney_id = str(uuid.uuid4())
        new_case_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        # INSERT RETURNING 결과: id, case_number, title, status
        db_row = (new_case_id, "2026가합99001", "손해배상", "intake")

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_single_execute(db_row)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.post(
                "/cases",
                json={"case_number": "2026가합99001", "title": "손해배상"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 201, res.text
        data = res.json()
        assert data["case_id"] == new_case_id
        assert data["case_number"] == "2026가합99001"
        assert data["status"] == "intake"
        assert data["doc_total"] == 0

    def test_missing_case_number_returns_422(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_single_execute(None)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.post(
                "/cases",
                json={"title": "T"},  # case_number 없음
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 422, res.text


# ── PATCH /cases/{id} 엔드포인트 mock 테스트 ─────────────────────────────────

@skip_if_no_api
@skip_if_no_jwt
class TestUpdateCaseEndpoint:
    SECRET = "test"

    def test_no_auth_returns_401(self):
        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_single_execute(None)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(f"/cases/{uuid.uuid4()}", json={"title": "수정"})

        assert res.status_code == 401, res.text

    def test_invalid_uuid_returns_400(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import api as api_mod
        import db as db_mod
        pool_mock = _make_pool_mock_single_execute(None)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(
                "/cases/not-a-uuid",
                json={"title": "수정"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 400, res.text

    def test_rls_hidden_case_returns_404(self):
        """RLS SELECT 가 0행 반환 → 404 (존재 은폐).

        PATCH 핸들러 execute 순서:
          #1: UPDATE(no return needed)
          #2: SELECT fetchone → None (RLS 격리)
          #3: doc fetchall → (선행 execute 가 없음, 선행에서 404 raise)
        """
        attorney_id = str(uuid.uuid4())
        case_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import api as api_mod
        import db as db_mod

        call_count = [0]

        class _CurUpdate:
            async def fetchone(self):
                return None

        class _CurSelectNone:
            async def fetchone(self):
                return None  # RLS: 타 변호사 사건 숨김

        conn = MagicMock()

        async def _execute(sql, params=None):
            call_count[0] += 1
            if call_count[0] == 1:
                return _CurUpdate()
            return _CurSelectNone()

        conn.execute = _execute

        @asynccontextmanager
        async def _conn_ctx():
            call_count[0] = 0
            yield conn

        pool = MagicMock()
        pool.connection = _conn_ctx

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(
                f"/cases/{case_id}",
                json={"title": "수정시도"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 404, res.text
        assert "사건을 찾을 수 없습니다" in res.json()["detail"]

    def test_success_returns_200_case_detail(self):
        """수정 성공 → 200 + CaseDetailResponse."""
        attorney_id = str(uuid.uuid4())
        case_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        # PATCH: 1st execute=UPDATE(None), 2nd=SELECT fetchone, 3rd=doc fetchall
        call_count = 0

        class _CurUpdate:
            async def fetchone(self):
                return None  # UPDATE rowcount 무시

        class _CurSelect:
            async def fetchone(self):
                return (
                    case_id,
                    "2026가합99001",
                    "수정된 사건명",
                    "active",
                    "civil",
                    "개요",
                    "2026-01-01",
                    None,
                )

        class _CurDocs:
            async def fetchall(self):
                return []

        conn = MagicMock()

        async def _execute(sql, params=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _CurUpdate()
            if call_count == 2:
                return _CurSelect()
            return _CurDocs()

        conn.execute = _execute

        @asynccontextmanager
        async def _conn_ctx():
            nonlocal call_count
            call_count = 0
            yield conn

        pool = MagicMock()
        pool.connection = _conn_ctx

        import api as api_mod
        import db as db_mod

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(
                f"/cases/{case_id}",
                json={"title": "수정된 사건명", "status": "active"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 200, res.text
        data = res.json()
        assert data["case_id"] == case_id
        assert data["title"] == "수정된 사건명"
        assert data["status"] == "active"
        assert data["documents"] == []


# ── 기존 모델 불변 검증 ───────────────────────────────────────────────────────

@skip_if_no_api
class TestExistingModelsUnchanged:
    """기존 모델이 G-2 C1 구현 후 변경되지 않았음을 확인 (보존 계약 §5.3)."""

    def test_case_out_fields_unchanged(self):
        fields = set(CaseOut.model_fields.keys())
        assert fields == {
            "case_id", "case_number", "title", "status",
            "doc_total", "doc_indexed", "doc_pending", "doc_failed",
        }, f"CaseOut 필드 변경 감지: {fields}"

    def test_case_detail_response_fields_unchanged(self):
        fields = set(CaseDetailResponse.model_fields.keys())
        # G-2 C2 additive: 'parties' 가산 (OQ-11 CTO判定 — open-closed, documents 동일 패턴)
        assert fields == {
            "case_id", "case_number", "title", "status",
            "case_type", "description", "opened_at", "closed_at", "documents",
            "parties",
        }, f"CaseDetailResponse 필드 변경 감지: {fields}"

    def test_case_document_item_fields_unchanged(self):
        fields = set(CaseDocumentItem.model_fields.keys())
        assert fields == {
            "doc_id", "title", "document_type", "ingest_status",
        }, f"CaseDocumentItem 필드 변경 감지: {fields}"


# ── @pytest.mark.postgres: AC-02~AC-04 RLS 라이브 테스트 ─────────────────────

@pytest.mark.postgres
class TestCaseWriteRLSIntegration:
    """
    실 PostgreSQL 필요 (LEGAL_RAG_DB_DSN_POSTGRES) — founder DSN 게이트로 실행 보류.

    AC-02: 담당 변호사 JWT 로 POST /cases → 201, case_id UUID 확인.
           생성 직후 GET /cases 에 해당 사건 노출.
    AC-03: PATCH /cases/{id} title 수정 → 200, case_number 기존 값 유지.
    AC-04: 변호사 B 토큰으로 변호사 A 사건 PATCH → 404 (존재 은폐).
    """

    def test_placeholder_ac02(self):
        pytest.skip("AC-02: Postgres integration — founder DSN 게이트로 실행 보류")

    def test_placeholder_ac03(self):
        pytest.skip("AC-03: Postgres integration — founder DSN 게이트로 실행 보류")

    def test_placeholder_ac04(self):
        pytest.skip("AC-04: Postgres integration — founder DSN 게이트로 실행 보류")
