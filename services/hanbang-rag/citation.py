"""
citation.py — chunk.id → source resolution + citation string assembly + query log.

CITATION INTEGRITY CONTRACT:
  - The only valid citation source is hanbang_rag_document_chunk.id.
  - Resolver looks up source_type / source_id from the chunk row,
    then fetches human-readable metadata from hanbang_rag_notice.
  - No free-text citation is ever invented outside this module.
  - Results are written to hanbang_rag_query_log.retrieved_chunk_ids as a JSON array
    and citations_summary as a JSON-serialized list of resolved citation dicts.

Source type: 'notice' only (한방 고시 단일 — case_document 분기 없음).
Results are structured dicts for the caller (api.py) to format for the client —
this layer does not generate prose answers (Lite tier, hallucination-free guarantee).
"""
from __future__ import annotations

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from retrieve import RetrievedChunk

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    chunk_id: str           # hanbang_rag_document_chunk.id — the citation anchor
    source_type: str        # 'notice'
    source_id: str          # FK UUID (hanbang_rag_notice.id)

    # ── Resolved metadata (from hanbang_rag_notice) ───────────────────────────
    # TODO(D1): Column names confirmed against hanbang_rag_notice DDL once written.
    # Candidate columns: notice_number TEXT, ministry TEXT, issued_date TEXT, summary TEXT
    notice_number: str | None = None   # e.g. "보건복지부고시 제2023-123호"
    ministry: str | None = None        # 소관부처 e.g. "보건복지부"
    issued_date: str | None = None     # 발령일자 e.g. "2023-01-01"
    summary: str | None = None         # 요약 (첫 300자)

    # ── Common ───────────────────────────────────────────────────────────────
    chunk_index: int = 0
    chunk_text_excerpt: str = ""     # first 200 chars for UI preview
    rrf_score: float = 0.0


# ── SQL ───────────────────────────────────────────────────────────────────────

_RESOLVE_NOTICE_SQL = """
SELECT
  lp.notice_number,
  lp.ministry,
  lp.issued_date::text,
  LEFT(lp.summary, 300) AS summary
FROM hanbang_rag_document_chunk ldc
JOIN hanbang_rag_notice lp ON lp.id = ldc.source_id
WHERE ldc.id = %s::uuid
  AND ldc.source_type = 'notice'
"""
# TODO(D1): Verify column names (notice_number / ministry / issued_date / summary)
# against hanbang_rag_notice DDL once written. Adjust field aliases if needed.

_INSERT_QUERY_LOG_SQL = """
INSERT INTO hanbang_rag_query_log
  (user_id, query_text, query_embedding,
   retrieved_chunk_ids, citations_summary, status, latency_ms)
VALUES (%s::uuid, %s, %s::vector, %s, %s, 'completed', %s)
RETURNING id::text
"""
# TODO(D1): hanbang_rag_query_log DDL to be created. No case_id column (고시는 case 범주 없음).


async def resolve_citations(
    *,
    conn,                           # psycopg AsyncConnection (rls_session active)
    chunks: "list[RetrievedChunk]",
) -> list[Citation]:
    """Resolve chunk.id → notice metadata for each retrieved chunk.

    Queries hanbang_rag_notice based on source_type='notice'.
    If a chunk's source row is not found (RLS or deleted), the citation is
    returned with metadata fields set to None (not silently dropped).

    Args:
        conn:   psycopg connection with active rls_session().
        chunks: Ordered list from retrieve.hybrid_search().

    Returns:
        List of Citation objects, same order as input chunks.
    """
    citations: list[Citation] = []

    for chunk in chunks:
        cit = Citation(
            chunk_id=chunk.chunk_id,
            source_type=chunk.source_type,
            source_id=chunk.source_id,
            chunk_index=chunk.chunk_index,
            chunk_text_excerpt=chunk.chunk_text[:200],
            rrf_score=chunk.rrf_score,
        )

        if chunk.source_type == "notice":
            cur = await conn.execute(_RESOLVE_NOTICE_SQL, (chunk.chunk_id,))
            row = await cur.fetchone()
            if row:
                cit.notice_number = row[0]
                cit.ministry = row[1]
                cit.issued_date = row[2]
                cit.summary = row[3]
            else:
                logger.warning(
                    "Could not resolve notice for chunk_id=%s source_id=%s",
                    chunk.chunk_id, chunk.source_id,
                )
        else:
            logger.warning(
                "Unexpected source_type=%r for chunk_id=%s — skipping resolution",
                chunk.source_type, chunk.chunk_id,
            )

        citations.append(cit)

    return citations


async def log_query(
    *,
    conn,                           # psycopg AsyncConnection (rls_session active)
    user_id: str | uuid.UUID,
    query_text: str,
    query_embedding: list[float] | None,
    citations: list[Citation],
    latency_ms: int | None = None,
) -> str:
    """Append a completed search to hanbang_rag_query_log.

    Stores retrieved_chunk_ids as JSON array (citation contract),
    citations_summary as JSON list of resolved citation dicts.

    Args:
        conn:            psycopg connection with active rls_session().
        user_id:         UUID of the querying user.
        query_text:      Original query string.
        query_embedding: 768-dim vector (or None if unavailable).
        citations:       Resolved citations from resolve_citations().
        latency_ms:      Total search latency for cost tracking.

    Returns:
        Created log row id (UUID str).
    """
    chunk_ids_json = json.dumps([c.chunk_id for c in citations])
    citations_json = json.dumps([asdict(c) for c in citations], default=str)

    user_id_str = str(uuid.UUID(str(user_id)))

    cur = await conn.execute(
        _INSERT_QUERY_LOG_SQL,
        (
            user_id_str,
            query_text,
            query_embedding,     # None → NULL; psycopg handles list[float] → vector
            chunk_ids_json,
            citations_json,
            latency_ms,
        ),
    )
    row = await cur.fetchone()
    log_id = row[0] if row else "unknown"
    logger.info(
        "Query logged: log_id=%s user=%s chunks=%d",
        log_id, user_id_str, len(citations),
    )
    return log_id
