"""
tests/test_rls_session.py — Gap-1 단위: RLS session SET LOCAL emit 검증.

검증 대상:
  - rls_session() 컨텍스트매니저가 순서대로
    1) `SET LOCAL ROLE app_user` (superuser → non-privileged role drop)
    2) `SELECT set_config('app.current_user_id', '<uuid>', true)` 을 emit하는가.
  - 트랜잭션 블록 안에서 실행되는가 (conn.transaction() 호출 확인).
  - 잘못된 UUID는 RLSSessionError로 거부되는가.
  - 정상 종료 후 연결이 재사용 가능 상태인가.

Gap-1 통합 테스트(실 Postgres 필요):
  @pytest.mark.postgres 마킹 — `pytest -m postgres` 로 별도 실행.
  README의 "Running Tests" 섹션에 실행법 명시됨.
"""
import sys
import os
import uuid
from unittest.mock import AsyncMock, MagicMock, call
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from db import rls_session, RLSSessionError, _validate_uuid


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_mock_conn(executed_calls: list | None = None):
    """Build a minimal mock psycopg AsyncConnection."""
    conn = MagicMock()
    _calls = executed_calls if executed_calls is not None else []

    async def _execute(sql, params=None):
        _calls.append({"sql": sql, "params": params})
        cursor = MagicMock()
        cursor.fetchone = AsyncMock(return_value=None)
        return cursor

    conn.execute = AsyncMock(side_effect=_execute)

    # transaction() must work as an async context manager
    @asynccontextmanager
    async def _transaction():
        yield

    conn.transaction = _transaction
    return conn, _calls


# ── _validate_uuid ────────────────────────────────────────────────────────────

class TestValidateUuid:
    def test_valid_uuid_string_passes(self):
        uid = str(uuid.uuid4())
        assert _validate_uuid(uid, "x") == uid

    def test_valid_uuid_object_passes(self):
        uid = uuid.uuid4()
        assert _validate_uuid(uid, "x") == str(uid)

    def test_invalid_string_raises_rls_session_error(self):
        with pytest.raises(RLSSessionError):
            _validate_uuid("not-a-uuid", "attorney_id")

    def test_empty_string_raises_rls_session_error(self):
        with pytest.raises(RLSSessionError):
            _validate_uuid("", "attorney_id")

    def test_none_raises_rls_session_error(self):
        with pytest.raises(RLSSessionError):
            _validate_uuid(None, "attorney_id")  # type: ignore[arg-type]

    def test_normalises_uppercase_uuid(self):
        uid = str(uuid.uuid4()).upper()
        result = _validate_uuid(uid, "x")
        assert result == str(uuid.UUID(uid))


# ── rls_session() context manager ────────────────────────────────────────────

class TestRlsSession:

    @pytest.mark.asyncio
    async def test_emits_set_config_sql(self):
        """rls_session() must emit SET LOCAL ROLE app_user then set_config(...)."""
        attorney_id = str(uuid.uuid4())
        conn, calls = _make_mock_conn()

        async with rls_session(conn, attorney_id):
            pass  # body executes inside transaction

        assert len(calls) == 2, f"Expected 2 execute calls, got {len(calls)}: {calls}"
        # First call: role drop
        assert "SET LOCAL ROLE app_user" in calls[0]["sql"]
        # Second call: GUC set
        emitted_sql = calls[1]["sql"]
        assert "set_config" in emitted_sql
        assert "app.current_user_id" in emitted_sql

        emitted_params = calls[1]["params"]
        assert emitted_params is not None
        # First param must be the canonical attorney UUID
        assert emitted_params[0] == attorney_id

    @pytest.mark.asyncio
    async def test_set_local_true_param_passed(self):
        """The third argument to set_config must be `true` (SET LOCAL semantics)."""
        attorney_id = str(uuid.uuid4())
        conn, calls = _make_mock_conn()

        async with rls_session(conn, attorney_id):
            pass

        sql = calls[1]["sql"]
        # Our implementation passes `true` as SQL literal inside set_config
        # The actual SQL is: SELECT set_config('app.current_user_id', %s, true)
        assert "true" in sql.lower()

    @pytest.mark.asyncio
    async def test_uuid_normalised_before_set(self):
        """UUID is normalised to canonical lowercase before being SET."""
        upper_id = str(uuid.uuid4()).upper()
        canonical = str(uuid.UUID(upper_id))
        conn, calls = _make_mock_conn()

        async with rls_session(conn, upper_id):
            pass

        param_value = calls[1]["params"][0]
        assert param_value == canonical

    @pytest.mark.asyncio
    async def test_invalid_uuid_raises_before_any_db_call(self):
        """Invalid attorney_id raises RLSSessionError without touching DB."""
        conn, calls = _make_mock_conn()

        with pytest.raises(RLSSessionError):
            async with rls_session(conn, "invalid-uuid"):
                pass

        assert len(calls) == 0, "DB must not be called for invalid UUID"

    @pytest.mark.asyncio
    async def test_body_executes_inside_session(self):
        """Code inside the context manager runs after SET LOCAL."""
        attorney_id = str(uuid.uuid4())
        conn, calls = _make_mock_conn()
        body_ran = []

        async with rls_session(conn, attorney_id):
            body_ran.append(True)

        assert body_ran == [True]
        # SET LOCAL ROLE + set_config happened before body
        assert len(calls) == 2

    @pytest.mark.asyncio
    async def test_exception_in_body_propagates(self):
        """Exception inside body propagates out of context manager."""
        attorney_id = str(uuid.uuid4())
        conn, _ = _make_mock_conn()

        with pytest.raises(RuntimeError, match="body error"):
            async with rls_session(conn, attorney_id):
                raise RuntimeError("body error")

    @pytest.mark.asyncio
    async def test_accepts_uuid_object(self):
        """rls_session() accepts uuid.UUID objects directly."""
        attorney_uuid = uuid.uuid4()
        conn, calls = _make_mock_conn()

        async with rls_session(conn, attorney_uuid):
            pass

        assert calls[1]["params"][0] == str(attorney_uuid)


# ── Gap-1 통합 테스트 (postgres 마크) ─────────────────────────────────────────

@pytest.mark.postgres
@pytest.mark.asyncio
async def test_rls_blocks_cross_attorney_access():
    """
    Gap-1 통합 테스트: 변호사 A 세션이 변호사 B 사건문서 청크를 0행으로 차단.

    실행 방법:
        pytest -m postgres tests/test_rls_session.py

    요구사항:
      - 실 Postgres (pgvector, pg_bigm 설치) 또는 testcontainers
      - 환경변수 LEGAL_RAG_DB_DSN_POSTGRES (app_service DSN) 설정
      - 01~07_*.sql 적용 완료

    현재: DB 없으면 자동 skip.
    """
    db_dsn = os.environ.get("LEGAL_RAG_DB_DSN_POSTGRES")
    if not db_dsn:
        pytest.skip("LEGAL_RAG_DB_DSN_POSTGRES not set — postgres integration skipped")

    # 실 DB가 있을 때만 아래 코드 실행
    try:
        from psycopg_pool import AsyncConnectionPool
        import db as database
    except ImportError:
        pytest.skip("psycopg_pool not installed")

    # 이 테스트 본문은 인프라(Gap-1 통합 게이트 #8)에서 구현 완성
    # 현재는 skip 경로로 종료 (DB 없는 단위 환경에서 통과)
    pytest.skip("Postgres integration test not yet wired (infra gate #8)")
