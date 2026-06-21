"""
tests/test_postgres_integration.py — C2 postgres integration test suite.

Markers: @pytest.mark.postgres  (requires LEGAL_RAG_DB_DSN_POSTGRES)
         @pytest.mark.asyncio

All tests auto-skip when the env var is unset (dev boxes with no Postgres).
Every test runs inside the pg_conn force_rollback transaction → zero DB pollution.

Tests:
  G-P7  — idempotent re-ingest (upsert, chunk count stable on second call)
  G-P8a — ingest of non-empty file → ingest_status = 'done'
  G-P8b — ingest of empty/whitespace file → returns 0, ingest_status = 'error'
  G-P17 — log_query inserts exactly one row into legal_rag_query_log
  G-P19 — app_user role denied SELECT on legal_attorney (privilege isolation)
"""
from __future__ import annotations

import pytest

pytestmark = [pytest.mark.postgres, pytest.mark.asyncio]

# Seed UUIDs (committed in preview DB — do NOT change)
_ATTORNEY_이준호 = "a1000000-0000-0000-0000-000000000001"
_ATTORNEY_박서연 = "a1000000-0000-0000-0000-000000000002"
_SOURCE_ID = "d0c00000-0001-0001-0001-000000000001"   # belongs to c001
_CASE_ID = "c0000000-0001-0001-0001-000000000001"     # c001 — 이준호-only case

_LEGAL_TEXT = (
    "소프트웨어 공급계약 해지에 관한 손해배상 청구 건입니다. "
    "계약 당사자인 원고는 피고가 납품 기한을 준수하지 아니하여 "
    "상당한 재산적 손해가 발생하였다고 주장합니다. "
    "법원은 계약서 제7조에 따른 위약금 조항 및 민법 제390조를 검토하여야 합니다. "
    "이 사건에서 쟁점은 귀책사유의 유무 및 손해액 산정 방법입니다."
)


# ── G-P7: idempotent re-ingest ────────────────────────────────────────────────

async def test_gp7_idempotent_reingest(pg_conn, stub_embed_client, tmp_path):
    """Ingesting the same source_id twice must not grow the chunk count (upsert)."""
    from ingest import ingest_file

    txt = tmp_path / "contract.txt"
    txt.write_text(_LEGAL_TEXT, encoding="utf-8")

    common = dict(
        conn=pg_conn,
        embed_client=stub_embed_client,
        model_version="test",
        file_path=txt,
        source_type="case_document",
        source_id=_SOURCE_ID,
        case_id=_CASE_ID,
    )

    n1 = await ingest_file(**common)
    assert n1 > 0, "First ingest produced 0 chunks — check seed data / text"

    cur = await pg_conn.execute(
        "SELECT COUNT(*) FROM legal_document_chunk "
        "WHERE source_id = %s::uuid AND source_type = 'case_document'",
        (_SOURCE_ID,),
    )
    count_after_first = (await cur.fetchone())[0]

    n2 = await ingest_file(**common)
    assert n2 > 0, "Second ingest produced 0 chunks"

    cur = await pg_conn.execute(
        "SELECT COUNT(*) FROM legal_document_chunk "
        "WHERE source_id = %s::uuid AND source_type = 'case_document'",
        (_SOURCE_ID,),
    )
    count_after_second = (await cur.fetchone())[0]

    assert count_after_first == count_after_second, (
        f"Chunk count grew from {count_after_first} to {count_after_second} "
        "on second ingest — upsert idempotency broken"
    )


# ── G-P8a: ingest_status = 'done' after successful ingest ────────────────────

async def test_gp8a_status_done(pg_conn, stub_embed_client, tmp_path):
    """Successful ingest of a non-empty file must set ingest_status = 'done'."""
    from ingest import ingest_file

    txt = tmp_path / "contract.txt"
    txt.write_text(_LEGAL_TEXT, encoding="utf-8")

    await ingest_file(
        conn=pg_conn,
        embed_client=stub_embed_client,
        model_version="test",
        file_path=txt,
        source_type="case_document",
        source_id=_SOURCE_ID,
        case_id=_CASE_ID,
    )

    cur = await pg_conn.execute(
        "SELECT ingest_status FROM legal_case_document WHERE id = %s::uuid",
        (_SOURCE_ID,),
    )
    row = await cur.fetchone()
    assert row is not None, "Source row not found — check seed data"
    assert row[0] == "done", f"Expected ingest_status='done', got {row[0]!r}"


# ── G-P8b: empty file → returns 0, ingest_status = 'error' ──────────────────

async def test_gp8b_empty_file_error_status(pg_conn, stub_embed_client, tmp_path):
    """Ingesting an empty/whitespace-only file returns 0 and sets status='error'."""
    from ingest import ingest_file

    empty = tmp_path / "empty.txt"
    empty.write_text("   \n  ", encoding="utf-8")

    n = await ingest_file(
        conn=pg_conn,
        embed_client=stub_embed_client,
        model_version="test",
        file_path=empty,
        source_type="case_document",
        source_id=_SOURCE_ID,
        case_id=_CASE_ID,
    )

    assert n == 0, f"Expected 0 chunks for empty file, got {n}"

    cur = await pg_conn.execute(
        "SELECT ingest_status FROM legal_case_document WHERE id = %s::uuid",
        (_SOURCE_ID,),
    )
    row = await cur.fetchone()
    assert row is not None, "Source row not found — check seed data"
    assert row[0] == "error", f"Expected ingest_status='error', got {row[0]!r}"


# ── G-P17: log_query inserts exactly one row ──────────────────────────────────

async def test_gp17_query_log_plus_one(pg_conn):
    """log_query must insert exactly one row into legal_rag_query_log."""
    from conftest import DUMMY_VEC
    from db import rls_session
    from retrieve import hybrid_search
    from citation import resolve_citations, log_query

    # Count before (inside the same rollback transaction)
    cur = await pg_conn.execute("SELECT COUNT(*) FROM legal_rag_query_log")
    count_before = (await cur.fetchone())[0]

    async with rls_session(pg_conn, _ATTORNEY_이준호):
        chunks = await hybrid_search(
            conn=pg_conn,
            query_text="소프트웨어 공급계약 해지 손해배상",
            query_embedding=DUMMY_VEC,
        )
        citations = await resolve_citations(conn=pg_conn, chunks=chunks)
        await log_query(
            conn=pg_conn,
            attorney_id=_ATTORNEY_이준호,
            query_text="소프트웨어 공급계약 해지 손해배상",
            query_embedding=DUMMY_VEC,
            citations=citations,
        )

    cur = await pg_conn.execute("SELECT COUNT(*) FROM legal_rag_query_log")
    count_after = (await cur.fetchone())[0]

    assert count_after == count_before + 1, (
        f"Expected query_log count {count_before + 1}, got {count_after}"
    )


# ── G-P19: app_user denied SELECT on legal_attorney ──────────────────────────

async def test_gp19_app_user_denied_legal_attorney(pg_conn):
    """09_grants.sql does NOT grant legal_attorney to app_user.
    Executing SELECT on that table as app_user must raise InsufficientPrivilege.
    """
    import psycopg

    async with pg_conn.transaction():
        await pg_conn.execute("SET LOCAL ROLE app_user")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            await pg_conn.execute("SELECT 1 FROM legal_attorney LIMIT 1")
