"""
tests/test_case_scoped_search.py — unit tests for hybrid_search case_id scoping.

Covers:
  1. case_id=None → SQL에 case_id 조건 없음 (기존 동작 무회귀)
  2. case_id 제공 → FTS SQL에 "case_id = " 포함 + execute params에 case_id 전달
  3. case_id 제공 → ANN SQL에 "case_id = " 포함 + execute params에 case_id 전달
  4. case_id 제공 시 반환 청크가 RRF+RLS 정상 통과

No live DB or embedding sidecar required. conn.execute 호출 인자를 캡처해 검증.
"""
from __future__ import annotations

import sys
import os
import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, call

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import retrieve


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_chunk_row(chunk_id: str, case_id: str | None = None) -> tuple:
    """7-column chunk row matching _FETCH_CHUNKS_SQL column order."""
    return (
        chunk_id,
        "case_document",
        str(uuid.uuid4()),
        case_id,
        0,
        "사건 관련 텍스트",
        40,
    )


def _build_capturing_conn(
    fts_ids: list[str],
    ann_rows: list[tuple],
    chunk_rows: list[tuple],
) -> tuple:
    """Build async conn mock that captures (sql, params) for each execute call.

    Returns (conn, execute_calls_list).
    execute_calls_list is mutated in-place as calls arrive.
    """
    execute_calls: list[tuple] = []
    fts_result = [(row,) for row in fts_ids]

    class _Cur:
        def __init__(self, rows):
            self._rows = rows

        async def fetchall(self):
            return self._rows

    async def _execute(sql, params=None):
        execute_calls.append((sql, params))
        sql_upper = sql.strip().upper()
        if "PG_EXTENSION" in sql_upper:
            return _Cur([(False,)])   # pg_bigm absent → tsquery path
        elif sql_upper.startswith("SET"):
            return _Cur([])
        elif "EMBEDDING <=>" in sql_upper:
            return _Cur(ann_rows)
        elif "ANY(" in sql_upper:
            return _Cur(chunk_rows)
        else:
            return _Cur(fts_result)

    conn = MagicMock()
    conn.execute = _execute
    return conn, execute_calls


# ── force pg_bigm=False so tests always use tsquery path ─────────────────────
# _probe_bigm is cached module-wide; reset before each test.

@pytest.fixture(autouse=True)
def reset_bigm_cache():
    original = retrieve._BIGM_AVAILABLE
    retrieve._BIGM_AVAILABLE = False   # skip probe; force tsquery path
    yield
    retrieve._BIGM_AVAILABLE = original


# ── Test: case_id=None — 기존 SQL 그대로 (무회귀) ────────────────────────────

class TestCaseIdNone:
    def test_fts_sql_has_no_case_filter(self):
        """case_id=None 시 FTS SQL에 'case_id' 키워드가 없어야 한다."""
        cid = str(uuid.uuid4())
        ann_rows = [(cid, 0.1)]
        chunk_rows = [_make_chunk_row(cid)]
        conn, calls = _build_capturing_conn([cid], ann_rows, chunk_rows)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상",
                query_embedding=[0.0] * 768,
                top_k=5,
                case_id=None,
            )
        )

        fts_call = next(
            (sql for sql, _ in calls if "TO_TSVECTOR" in sql.upper()), None
        )
        assert fts_call is not None, "FTS execute call not found"
        assert "case_id" not in fts_call.lower()

    def test_ann_sql_has_no_case_filter(self):
        """case_id=None 시 ANN SQL에 'case_id' 키워드가 없어야 한다."""
        cid = str(uuid.uuid4())
        ann_rows = [(cid, 0.1)]
        chunk_rows = [_make_chunk_row(cid)]
        conn, calls = _build_capturing_conn([cid], ann_rows, chunk_rows)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상",
                query_embedding=[0.0] * 768,
                top_k=5,
                case_id=None,
            )
        )

        ann_call = next(
            (sql for sql, _ in calls if "EMBEDDING <=>" in sql.upper()), None
        )
        assert ann_call is not None, "ANN execute call not found"
        assert "case_id" not in ann_call.lower()


# ── Test: case_id 제공 — SQL + params 검증 ───────────────────────────────────

class TestCaseIdProvided:
    def test_fts_sql_contains_case_filter(self):
        """case_id 제공 시 FTS SQL에 'case_id = ' 조건이 포함돼야 한다."""
        target_case = str(uuid.uuid4())
        cid = str(uuid.uuid4())
        ann_rows = [(cid, 0.1)]
        chunk_rows = [_make_chunk_row(cid, target_case)]
        conn, calls = _build_capturing_conn([cid], ann_rows, chunk_rows)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상",
                query_embedding=[0.0] * 768,
                top_k=5,
                case_id=target_case,
            )
        )

        fts_sql, fts_params = next(
            ((sql, p) for sql, p in calls if "TO_TSVECTOR" in sql.upper()), (None, None)
        )
        assert fts_sql is not None, "FTS execute call not found"
        assert "case_id" in fts_sql.lower(), f"case_id not in FTS SQL: {fts_sql!r}"
        assert target_case in fts_params, (
            f"case_id {target_case!r} not in FTS params: {fts_params!r}"
        )

    def test_ann_sql_contains_case_filter(self):
        """case_id 제공 시 ANN SQL에 'case_id = ' 조건이 포함돼야 한다."""
        target_case = str(uuid.uuid4())
        cid = str(uuid.uuid4())
        ann_rows = [(cid, 0.1)]
        chunk_rows = [_make_chunk_row(cid, target_case)]
        conn, calls = _build_capturing_conn([cid], ann_rows, chunk_rows)

        asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="손해배상",
                query_embedding=[0.0] * 768,
                top_k=5,
                case_id=target_case,
            )
        )

        ann_sql, ann_params = next(
            ((sql, p) for sql, p in calls if "EMBEDDING <=>" in sql.upper()), (None, None)
        )
        assert ann_sql is not None, "ANN execute call not found"
        assert "case_id" in ann_sql.lower(), f"case_id not in ANN SQL: {ann_sql!r}"
        assert target_case in ann_params, (
            f"case_id {target_case!r} not in ANN params: {ann_params!r}"
        )

    def test_results_returned_with_case_id(self):
        """case_id 제공 시 청크가 정상 반환돼야 한다 (RRF·RLS 통과 시뮬레이션)."""
        target_case = str(uuid.uuid4())
        cid = str(uuid.uuid4())
        ann_rows = [(cid, 0.15)]
        chunk_rows = [_make_chunk_row(cid, target_case)]
        conn, _ = _build_capturing_conn([cid], ann_rows, chunk_rows)

        results = asyncio.run(
            retrieve.hybrid_search(
                conn=conn,
                query_text="계약해지",
                query_embedding=[0.0] * 768,
                top_k=5,
                case_id=target_case,
            )
        )

        assert len(results) == 1
        assert results[0].chunk_id == cid
        assert results[0].case_id == target_case
