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


# ── G-P20: bigm LIKE OR-chain 실 실행 — =% 퇴행 가드 ─────────────────────────

async def test_gp20_bigm_like_or_returns_rows(pg_conn, stub_embed_client):
    """pg_bigm LIKE OR-chain이 실 DB에서 행을 반환하는지 검증 (=% 퇴행 방지 게이트).

    확인 내용:
      1. hybrid_search(match_mode='or')가 pg_bigm LIKE 경로를 탔을 때 ≥1 rows 반환.
         과거 =% 경로는 짧은 쿼리 vs 긴 청크에서 구조적으로 0 rows를 반환했음
         (라이브 실측: =% '손해배상' = 0행, tsquery = 22행).
      2. match_mode='and'도 동일하게 ≥1 rows 반환 (AND-chain 무회귀).

    시드 전제: legal_document_chunk 테이블에 '손해배상' 텍스트를 포함한 행이 ≥1개
    존재해야 한다 (미리뷰 DB seed 기준 충족). 시드 없이 실행 시 SKIP 처리.

    Substring-in-token 우위 (LIKE vs tsquery):
      "손해배상"이 "손해배상금" 포함 청크를 잡는지(LIKE 우위)는 시드 텍스트에
      '손해배상금'이 있을 때만 검증 가능. 현재 seed에 해당 텍스트 없으면 이 항목은
      주석으로 유지하고 SKIP — 날조 금지.
      # TODO: '손해배상금' 포함 시드 청크 추가 후 아래 주석 해제
      # assert any("손해배상금" in r.chunk_text for r in results_or), ...
    """
    from conftest import DUMMY_VEC
    from db import rls_session
    import retrieve as _retrieve

    # pg_bigm 실제 설치 여부 확인 — 미설치 시 LIKE 경로 진입 불가, SKIP
    cur = await pg_conn.execute(
        "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname='pg_bigm')"
    )
    bigm_installed = (await cur.fetchone())[0]
    if not bigm_installed:
        pytest.skip("pg_bigm extension not installed — bigm LIKE path not active")

    # 시드 데이터 존재 확인 ('손해배상' 포함 청크 최소 1개)
    cur = await pg_conn.execute(
        "SELECT COUNT(*) FROM legal_document_chunk WHERE chunk_text LIKE %s",
        ("%손해배상%",),
    )
    seed_count = (await cur.fetchone())[0]
    if seed_count == 0:
        pytest.skip(
            "'손해배상' 포함 청크가 DB에 없음 — 시드 없이는 LIKE 경로 검증 불가"
        )

    # _BIGM_AVAILABLE 캐시 리셋 (이 테스트는 실 probe를 통해야 한다)
    original_cache = _retrieve._BIGM_AVAILABLE
    _retrieve._BIGM_AVAILABLE = None
    try:
        async with rls_session(pg_conn, _ATTORNEY_이준호):
            # OR 모드: LIKE OR-chain → ≥1 rows 기대
            results_or = await _retrieve.hybrid_search(
                conn=pg_conn,
                query_text="손해배상",
                query_embedding=DUMMY_VEC,
                top_k=10,
                match_mode="or",
            )
            assert len(results_or) >= 1, (
                "bigm LIKE OR-chain: '손해배상' 검색이 0 rows 반환 — "
                "=% 퇴행 또는 인덱스 문제. "
                f"seed_count={seed_count}, fts_ids가 ANN에 묻혔을 가능성 포함."
            )

            # AND 모드: 단일 토큰이므로 OR과 동일 결과 기대 (≥1)
            results_and = await _retrieve.hybrid_search(
                conn=pg_conn,
                query_text="손해배상",
                query_embedding=DUMMY_VEC,
                top_k=10,
                match_mode="and",
            )
            assert len(results_and) >= 1, (
                "bigm LIKE AND-chain: '손해배상' 단일토큰 검색이 0 rows 반환 — "
                "AND-chain 퇴행. "
                f"seed_count={seed_count}."
            )
    finally:
        _retrieve._BIGM_AVAILABLE = original_cache
