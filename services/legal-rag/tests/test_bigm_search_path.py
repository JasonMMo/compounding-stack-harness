"""
tests/test_bigm_search_path.py — bigm 경로 단위 회귀 가드.

목적:
  - use_bigm=True 시 OR/AND 양 모드 모두 LIKE 경로를 타는지 확인.
  - =% / =%% 가 FTS SQL에 절대 나타나지 않음을 assert (회귀 방어).
  - 누가 OR을 =% 경로로 되돌리면 이 테스트가 즉시 깨진다.

No live DB required. conn.execute는 mock — 실행된 SQL 문자열을 캡처.
"""
from __future__ import annotations

import asyncio
import sys
import os
import uuid
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import retrieve


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def force_bigm_true(monkeypatch):
    """_BIGM_AVAILABLE=True로 고정 — probe DB 호출 없이 bigm 경로 강제 진입."""
    monkeypatch.setattr(retrieve, "_BIGM_AVAILABLE", True)
    yield
    # monkeypatch이 teardown에서 원복하므로 추가 복원 불필요


def _build_capturing_conn_bigm(fts_id: str) -> tuple:
    """bigm 경로용 conn mock. 실행된 (sql, params) 쌍을 리스트로 캡처.

    - pg_extension 쿼리: _BIGM_AVAILABLE 이미 True이므로 probe가 호출되지 않음.
    - LIKE 포함 SELECT: fts_id 한 행 반환 (tuple-of-tuple 형식).
    - EMBEDDING <=>: ANN row 반환.
    - ANY(: FETCH_CHUNKS row 반환.
    """
    captured_calls: list[tuple] = []

    ann_id = str(uuid.uuid4())
    chunk_row = (
        fts_id,
        "precedent",
        str(uuid.uuid4()),
        None,
        0,
        "손해배상 관련 판례 텍스트입니다.",
        40,
    )

    class _Cur:
        def __init__(self, rows):
            self._rows = rows

        async def fetchall(self):
            return self._rows

    async def _execute(sql, params=None):
        captured_calls.append((sql, params))
        sql_upper = sql.strip().upper()
        if "EMBEDDING <=>" in sql_upper:
            return _Cur([(ann_id, 0.2)])
        elif "ANY(" in sql_upper:
            return _Cur([chunk_row])
        else:
            # FTS bigm LIKE SQL
            return _Cur([(fts_id,)])

    conn = MagicMock()
    conn.execute = _execute
    return conn, captured_calls


# ── 핵심 회귀 가드 ─────────────────────────────────────────────────────────────

class TestBigmPathOrMode:
    """OR 모드에서 bigm 경로가 LIKE를 쓰는지, =% 류를 쓰지 않는지 검증."""

    def test_or_mode_fts_sql_contains_like(self):
        """bigm OR 모드: FTS SQL에 'LIKE'가 포함돼야 한다."""
        fts_id = str(uuid.uuid4())
        conn, calls = _build_capturing_conn_bigm(fts_id)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상 계약해지",
                query_embedding=[0.0] * 768,
                top_k=5,
                match_mode="or",
            )
        )

        fts_sql = _find_fts_bigm_sql(calls)
        assert fts_sql is not None, "bigm FTS execute call not found"
        assert "LIKE" in fts_sql.upper(), (
            f"OR 모드 bigm FTS SQL에 LIKE가 없음: {fts_sql!r}"
        )

    def test_or_mode_fts_sql_no_percent_equal(self):
        """bigm OR 모드: FTS SQL에 '=%' 또는 '=%%' 가 없어야 한다 (퇴행 방지)."""
        fts_id = str(uuid.uuid4())
        conn, calls = _build_capturing_conn_bigm(fts_id)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상",
                query_embedding=[0.0] * 768,
                top_k=5,
                match_mode="or",
            )
        )

        fts_sql = _find_fts_bigm_sql(calls)
        assert fts_sql is not None, "bigm FTS execute call not found"
        # =% 및 =%% 모두 금지 — 전체유사도 연산자 퇴행 가드
        assert "=%" not in fts_sql, (
            f"OR 모드 bigm FTS SQL에 금지된 '=%' 연산자 발견: {fts_sql!r}"
        )

    def test_or_mode_fts_sql_contains_or_operator(self):
        """bigm OR 모드, 2토큰: FTS SQL 내 LIKE 체인에 ' OR ' 가 들어가야 한다."""
        fts_id = str(uuid.uuid4())
        conn, calls = _build_capturing_conn_bigm(fts_id)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상 계약해지",
                query_embedding=[0.0] * 768,
                top_k=5,
                match_mode="or",
            )
        )

        fts_sql = _find_fts_bigm_sql(calls)
        assert fts_sql is not None
        assert " OR " in fts_sql.upper(), (
            f"OR 모드 2토큰 bigm SQL에 OR 연산자 없음: {fts_sql!r}"
        )

    def test_or_mode_returns_results(self):
        """bigm OR 모드: FTS에서 잡힌 chunk가 최종 결과에 포함돼야 한다."""
        fts_id = str(uuid.uuid4())
        conn, _ = _build_capturing_conn_bigm(fts_id)

        results = asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상",
                query_embedding=[0.0] * 768,
                top_k=5,
                match_mode="or",
            )
        )

        found_ids = [r.chunk_id for r in results]
        assert fts_id in found_ids, (
            f"bigm OR 모드: FTS로 잡힌 {fts_id!r}가 결과에 없음. 결과: {found_ids}"
        )


class TestBigmPathAndMode:
    """AND 모드에서도 동일하게 LIKE AND-chain을 쓰는지 검증."""

    def test_and_mode_fts_sql_contains_like(self):
        """bigm AND 모드: FTS SQL에 'LIKE'가 포함돼야 한다."""
        fts_id = str(uuid.uuid4())
        conn, calls = _build_capturing_conn_bigm(fts_id)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상 계약해지",
                query_embedding=[0.0] * 768,
                top_k=5,
                match_mode="and",
            )
        )

        fts_sql = _find_fts_bigm_sql(calls)
        assert fts_sql is not None, "bigm FTS execute call not found"
        assert "LIKE" in fts_sql.upper(), (
            f"AND 모드 bigm FTS SQL에 LIKE가 없음: {fts_sql!r}"
        )

    def test_and_mode_fts_sql_no_percent_equal(self):
        """bigm AND 모드: FTS SQL에 '=%' 가 없어야 한다."""
        fts_id = str(uuid.uuid4())
        conn, calls = _build_capturing_conn_bigm(fts_id)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상",
                query_embedding=[0.0] * 768,
                top_k=5,
                match_mode="and",
            )
        )

        fts_sql = _find_fts_bigm_sql(calls)
        assert fts_sql is not None
        assert "=%" not in fts_sql, (
            f"AND 모드 bigm FTS SQL에 금지된 '=%' 연산자 발견: {fts_sql!r}"
        )

    def test_and_mode_fts_sql_contains_and_operator(self):
        """bigm AND 모드, 2토큰: FTS SQL 내 LIKE 체인에 ' AND ' 가 들어가야 한다."""
        fts_id = str(uuid.uuid4())
        conn, calls = _build_capturing_conn_bigm(fts_id)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상 계약해지",
                query_embedding=[0.0] * 768,
                top_k=5,
                match_mode="and",
            )
        )

        fts_sql = _find_fts_bigm_sql(calls)
        assert fts_sql is not None
        assert " AND " in fts_sql.upper(), (
            f"AND 모드 2토큰 bigm SQL에 AND 연산자 없음: {fts_sql!r}"
        )


class TestBigmNoSetLocalCall:
    """=% 제거 후 SET LOCAL pg_bigm.similarity_limit 호출이 사라졌는지 검증."""

    def test_no_set_local_similarity_limit(self):
        """bigm 경로에서 'SET LOCAL' 호출이 없어야 한다 (=% 전용이었음)."""
        fts_id = str(uuid.uuid4())
        conn, calls = _build_capturing_conn_bigm(fts_id)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상",
                query_embedding=[0.0] * 768,
                top_k=5,
                match_mode="or",
            )
        )

        set_local_calls = [
            sql for sql, _ in calls
            if sql.strip().upper().startswith("SET")
        ]
        assert set_local_calls == [], (
            f"bigm 경로에서 예상치 못한 SET LOCAL 호출 발견: {set_local_calls}"
        )


# ── helpers ───────────────────────────────────────────────────────────────────

def _find_fts_bigm_sql(calls: list[tuple]) -> str | None:
    """captured execute_calls에서 bigm FTS SQL을 찾아 반환.

    bigm FTS SQL 특징: LIKE가 들어있고, EMBEDDING <=> 나 ANY( 는 없음.
    """
    for sql, _ in calls:
        if sql is None:
            continue
        u = sql.upper()
        if "LIKE" in u and "EMBEDDING <=>" not in u and "ANY(" not in u:
            return sql
    return None
