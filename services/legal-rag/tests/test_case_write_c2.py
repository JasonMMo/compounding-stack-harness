"""
tests/test_case_write_c2.py — G-2 C2 당사자 쓰기 단위 테스트

커버리지:
  - CasePartyCreateIn / CasePartyUpdateIn Pydantic 모델 검증
      * role enum 거부 (허용값 외 → ValidationError)
      * name/notes 길이 상한 255자 (DDL VARCHAR 진실)
      * contact_id 클라이언트 제출 무시 확인
  - POST /cases/{case_id}/parties mock 통합 테스트 (201, CasePartyOut 직렬화)
  - PATCH /cases/{case_id}/parties/{party_id} mock 통합 테스트 (200, 404 RLS 은폐)
  - GET /cases/{case_id} 응답에 parties 필드 포함 확인 (OQ-11 CTO判定)
  - CaseDetailResponse.parties 필드 존재 확인
  - CasePartyOut 모델 필드 확인

AC-05~AC-07 (RLS 라이브): @pytest.mark.postgres — live DB 없으면 skip.
DDL 보고: name/notes VARCHAR(255) 상한 적용 (spec §3.2 256/2000 을 DDL 진실로 대체).

실행:
  cd services/legal-rag && python -m pytest tests/test_case_write_c2.py -q
"""
from __future__ import annotations

import sys
import os
import uuid
import time
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# ── api import guard ──────────────────────────────────────────────────────────

try:
    from api import (
        app,
        CasePartyOut,
        CasePartyCreateIn,
        CasePartyUpdateIn,
        CaseDetailResponse,
        CaseDocumentItem,
        _PARTY_ROLE_VALUES,
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


# ── CasePartyCreateIn 모델 검증 ───────────────────────────────────────────────

@skip_if_no_api
class TestCasePartyCreateInModel:
    """CasePartyCreateIn Pydantic 검증 규칙."""

    def test_minimum_valid(self):
        m = CasePartyCreateIn(role="plaintiff", name="홍길동")
        assert m.role == "plaintiff"
        assert m.name == "홍길동"
        assert m.notes is None

    def test_all_valid_roles(self):
        for role in ("plaintiff", "defendant", "witness", "opposing-counsel", "expert-witness"):
            m = CasePartyCreateIn(role=role, name="테스트")
            assert m.role == role

    def test_invalid_role_rejected(self):
        with pytest.raises(Exception):
            CasePartyCreateIn(role="judge", name="테스트")

    def test_invalid_role_other_rejected(self):
        with pytest.raises(Exception):
            CasePartyCreateIn(role="other", name="테스트")

    def test_name_max_length_255_ok(self):
        m = CasePartyCreateIn(role="plaintiff", name="A" * 255)
        assert len(m.name) == 255

    def test_name_max_length_256_rejected(self):
        """DDL VARCHAR(255) 진실 — 256자 거부."""
        with pytest.raises(Exception):
            CasePartyCreateIn(role="plaintiff", name="A" * 256)

    def test_notes_max_length_255_ok(self):
        m = CasePartyCreateIn(role="plaintiff", name="T", notes="N" * 255)
        assert len(m.notes) == 255

    def test_notes_max_length_256_rejected(self):
        """DDL VARCHAR(255) 진실 — notes 256자 거부."""
        with pytest.raises(Exception):
            CasePartyCreateIn(role="plaintiff", name="T", notes="N" * 256)

    def test_notes_none_allowed(self):
        m = CasePartyCreateIn(role="defendant", name="피고법인", notes=None)
        assert m.notes is None

    def test_contact_id_not_a_field(self):
        """contact_id 는 v1 미노출 — 모델 필드에 없어야 함."""
        fields = set(CasePartyCreateIn.model_fields.keys())
        assert "contact_id" not in fields, "contact_id 는 v1 미노출 필드여야 함"

    def test_party_role_values_complete(self):
        expected = {"plaintiff", "defendant", "witness", "opposing-counsel", "expert-witness"}
        assert _PARTY_ROLE_VALUES == expected


# ── CasePartyUpdateIn 모델 검증 ───────────────────────────────────────────────

@skip_if_no_api
class TestCasePartyUpdateInModel:
    """CasePartyUpdateIn Pydantic 검증 규칙 (partial PATCH)."""

    def test_all_none_is_valid(self):
        """제출 필드 없음 → 유효 (no-op update)."""
        m = CasePartyUpdateIn()
        assert m.role is None
        assert m.name is None
        assert m.notes is None

    def test_partial_update_name_only(self):
        m = CasePartyUpdateIn(name="변경된 당사자명")
        assert m.name == "변경된 당사자명"
        assert m.role is None

    def test_partial_update_role_only(self):
        m = CasePartyUpdateIn(role="witness")
        assert m.role == "witness"

    def test_invalid_role_rejected(self):
        with pytest.raises(Exception):
            CasePartyUpdateIn(role="unknown_role")

    def test_name_max_255_ok(self):
        m = CasePartyUpdateIn(name="A" * 255)
        assert len(m.name) == 255

    def test_name_max_256_rejected(self):
        with pytest.raises(Exception):
            CasePartyUpdateIn(name="A" * 256)

    def test_notes_max_255_ok(self):
        m = CasePartyUpdateIn(notes="N" * 255)
        assert len(m.notes) == 255

    def test_notes_max_256_rejected(self):
        with pytest.raises(Exception):
            CasePartyUpdateIn(notes="N" * 256)

    def test_contact_id_not_a_field(self):
        """contact_id 는 CasePartyUpdateIn 에 없어야 함 (v1 미노출)."""
        fields = set(CasePartyUpdateIn.model_fields.keys())
        assert "contact_id" not in fields


# ── CasePartyOut 모델 필드 확인 ───────────────────────────────────────────────

@skip_if_no_api
class TestCasePartyOutModel:
    """CasePartyOut 구조 계약."""

    def test_required_fields(self):
        fields = set(CasePartyOut.model_fields.keys())
        assert fields == {"party_id", "case_id", "role", "name", "notes"}

    def test_contact_id_not_exposed(self):
        """contact_id 는 CasePartyOut 에 없어야 함 (존재 은폐)."""
        fields = set(CasePartyOut.model_fields.keys())
        assert "contact_id" not in fields

    def test_instantiation(self):
        pid = str(uuid.uuid4())
        cid = str(uuid.uuid4())
        m = CasePartyOut(party_id=pid, case_id=cid, role="plaintiff", name="홍길동")
        assert m.party_id == pid
        assert m.notes is None


# ── CaseDetailResponse.parties 필드 확인 (OQ-11) ─────────────────────────────

@skip_if_no_api
class TestCaseDetailResponseParties:
    """OQ-11 CTO判定: CaseDetailResponse.parties 가산 확인."""

    def test_parties_field_exists(self):
        fields = set(CaseDetailResponse.model_fields.keys())
        assert "parties" in fields, "CaseDetailResponse 에 parties 필드가 없음 (OQ-11)"

    def test_parties_default_empty_list(self):
        """parties 기본값은 빈 리스트여야 함."""
        cid = str(uuid.uuid4())
        m = CaseDetailResponse(
            case_id=cid,
            case_number="X",
            title="T",
            status="intake",
            documents=[],
        )
        assert m.parties == []

    def test_existing_fields_unchanged(self):
        """기존 필드 보존 계약 (§5.3)."""
        fields = set(CaseDetailResponse.model_fields.keys())
        expected_original = {
            "case_id", "case_number", "title", "status",
            "case_type", "description", "opened_at", "closed_at", "documents",
        }
        assert expected_original.issubset(fields), f"기존 필드 누락: {expected_original - fields}"


# ── POST /cases/{case_id}/parties 엔드포인트 mock 테스트 ─────────────────────

@skip_if_no_api
@skip_if_no_jwt
class TestCreatePartyEndpoint:
    SECRET = "test"

    def _make_pool(self, insert_return=None):
        """INSERT RETURNING fetchone 하나 반환하는 pool mock."""
        class _Cur:
            def __init__(self, row):
                self._row = row
            async def fetchone(self):
                return self._row

        conn = MagicMock()

        async def _execute(sql, params=None):
            return _Cur(insert_return)

        conn.execute = _execute

        @asynccontextmanager
        async def _conn_ctx():
            yield conn

        pool = MagicMock()
        pool.connection = _conn_ctx
        return pool

    def test_no_auth_returns_401(self):
        import api as api_mod
        import db as db_mod
        pool = self._make_pool(None)
        case_id = str(uuid.uuid4())

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.post(
                f"/cases/{case_id}/parties",
                json={"role": "plaintiff", "name": "테스트"},
            )

        assert res.status_code == 401, res.text

    def test_invalid_case_uuid_returns_400(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)
        import api as api_mod
        import db as db_mod
        pool = self._make_pool(None)

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.post(
                "/cases/not-a-uuid/parties",
                json={"role": "plaintiff", "name": "테스트"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 400, res.text

    def test_invalid_role_returns_422(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)
        import api as api_mod
        import db as db_mod
        pool = self._make_pool(None)
        case_id = str(uuid.uuid4())

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.post(
                f"/cases/{case_id}/parties",
                json={"role": "judge", "name": "테스트"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 422, res.text

    def test_success_returns_201_party_out(self):
        attorney_id = str(uuid.uuid4())
        case_id = str(uuid.uuid4())
        party_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        # INSERT RETURNING: id, case_id, role, name, notes
        db_row = (party_id, case_id, "plaintiff", "주식회사 한빛테크", "원고 법인.")
        pool = self._make_pool(db_row)

        import api as api_mod
        import db as db_mod

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.post(
                f"/cases/{case_id}/parties",
                json={"role": "plaintiff", "name": "주식회사 한빛테크", "notes": "원고 법인."},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 201, res.text
        data = res.json()
        assert data["party_id"] == party_id
        assert data["case_id"] == case_id
        assert data["role"] == "plaintiff"
        assert data["name"] == "주식회사 한빛테크"
        assert data["notes"] == "원고 법인."
        assert "contact_id" not in data

    def test_contact_id_in_body_is_ignored(self):
        """클라이언트가 contact_id 를 제출해도 422 가 아닌 정상 처리 (무시됨)."""
        attorney_id = str(uuid.uuid4())
        case_id = str(uuid.uuid4())
        party_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        db_row = (party_id, case_id, "defendant", "피고", None)
        pool = self._make_pool(db_row)

        import api as api_mod
        import db as db_mod

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.post(
                f"/cases/{case_id}/parties",
                json={
                    "role": "defendant",
                    "name": "피고",
                    "contact_id": str(uuid.uuid4()),  # 무시되어야 함
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        # contact_id 가 모델에 없으므로 Pydantic 이 무시, 정상 처리
        assert res.status_code == 201, res.text
        data = res.json()
        assert "contact_id" not in data


# ── PATCH /cases/{case_id}/parties/{party_id} 엔드포인트 mock 테스트 ─────────

@skip_if_no_api
@skip_if_no_jwt
class TestUpdatePartyEndpoint:
    SECRET = "test"

    def _make_pool_patch(self, select_return=None):
        """UPDATE(no-return) + SELECT fetchone 순서 pool mock."""
        call_count = [0]

        class _CurUpdate:
            async def fetchone(self):
                return None

        class _CurSelect:
            def __init__(self, row):
                self._row = row
            async def fetchone(self):
                return self._row

        conn = MagicMock()

        async def _execute(sql, params=None):
            call_count[0] += 1
            if call_count[0] == 1:
                return _CurUpdate()
            return _CurSelect(select_return)

        conn.execute = _execute

        @asynccontextmanager
        async def _conn_ctx():
            call_count[0] = 0
            yield conn

        pool = MagicMock()
        pool.connection = _conn_ctx
        return pool

    def test_no_auth_returns_401(self):
        import api as api_mod
        import db as db_mod
        pool = self._make_pool_patch(None)

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(
                f"/cases/{uuid.uuid4()}/parties/{uuid.uuid4()}",
                json={"name": "변경"},
            )

        assert res.status_code == 401, res.text

    def test_invalid_case_uuid_returns_400(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)
        import api as api_mod
        import db as db_mod
        pool = self._make_pool_patch(None)

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(
                f"/cases/not-a-uuid/parties/{uuid.uuid4()}",
                json={"name": "변경"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 400, res.text

    def test_invalid_party_uuid_returns_400(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)
        import api as api_mod
        import db as db_mod
        pool = self._make_pool_patch(None)

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(
                f"/cases/{uuid.uuid4()}/parties/bad-party-id",
                json={"name": "변경"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 400, res.text

    def test_rls_hidden_party_returns_404(self):
        """RLS SELECT 가 0행 반환 → 404 (존재 은폐, AC-07 패턴)."""
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)
        import api as api_mod
        import db as db_mod
        pool = self._make_pool_patch(None)  # SELECT returns None

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(
                f"/cases/{uuid.uuid4()}/parties/{uuid.uuid4()}",
                json={"name": "변경시도"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 404, res.text
        assert "찾을 수 없습니다" in res.json()["detail"]

    def test_success_returns_200_party_out(self):
        attorney_id = str(uuid.uuid4())
        case_id = str(uuid.uuid4())
        party_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        db_row = (party_id, case_id, "witness", "변경된 증인", "변경 메모")
        pool = self._make_pool_patch(db_row)

        import api as api_mod
        import db as db_mod

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(
                f"/cases/{case_id}/parties/{party_id}",
                json={"name": "변경된 증인"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 200, res.text
        data = res.json()
        assert data["party_id"] == party_id
        assert data["case_id"] == case_id
        assert data["name"] == "변경된 증인"
        assert "contact_id" not in data

    def test_invalid_role_in_patch_returns_422(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)
        import api as api_mod
        import db as db_mod
        pool = self._make_pool_patch(None)

        with (
            patch.object(api_mod, "_pool", pool),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.patch(
                f"/cases/{uuid.uuid4()}/parties/{uuid.uuid4()}",
                json={"role": "invalid_role"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 422, res.text


# ── @pytest.mark.postgres: AC-05~AC-07 RLS 라이브 테스트 ─────────────────────

@pytest.mark.postgres
class TestPartyWriteRLSIntegration:
    """
    실 PostgreSQL 필요 (LEGAL_RAG_DB_DSN_POSTGRES) — founder DSN 게이트로 실행 보류.

    AC-05: 담당 변호사 JWT 로 POST /cases/{id}/parties → 201, CasePartyOut 반환.
           GET /cases/{id} 응답에 party 행 노출 (parties 배열).
    AC-06: PATCH /cases/{id}/parties/{party_id} name 수정 → 200, 수정 값 반영.
           contact_id 제출해도 응답에서 contact_id 없음.
    AC-07: 변호사 B 토큰으로 변호사 A 사건 party 등록 → 404.
           변호사 B 토큰으로 변호사 A 사건 party 수정 → 404.
    """

    def test_placeholder_ac05(self):
        pytest.skip("AC-05: Postgres integration — founder DSN 게이트로 실행 보류")

    def test_placeholder_ac06(self):
        pytest.skip("AC-06: Postgres integration — founder DSN 게이트로 실행 보류")

    def test_placeholder_ac07(self):
        pytest.skip("AC-07: Postgres integration — founder DSN 게이트로 실행 보류")
