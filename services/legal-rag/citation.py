"""
citation.py — chunk.id → source resolution + citation string assembly + query log.

CITATION INTEGRITY CONTRACT:
  - The only valid citation source is legal_document_chunk.id.
  - Resolver looks up source_type / source_id from the chunk row,
    then fetches human-readable metadata from legal_precedent OR legal_case_document.
  - No free-text citation is ever invented outside this module.
  - Results are written to legal_rag_query_log.retrieved_chunk_ids as a JSON array
    and citations_summary as a JSON-serialized list of resolved citation dicts.

Both precedent and case_document citations are returned as structured dicts so
the caller (api.py) can format them for the client — this layer does not
generate prose answers (Lite tier, hallucination-free guarantee).
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
    chunk_id: str           # legal_document_chunk.id — the citation anchor
    source_type: str        # 'precedent' | 'case_document'
    source_id: str          # FK UUID

    # ── Resolved metadata (from source table) ────────────────────────────────
    # Precedent fields (source_type='precedent')
    case_number: str | None = None   # e.g. "대법원 2020다12345"
    court: str | None = None
    decision_date: str | None = None
    holding_summary: str | None = None

    # Case document fields (source_type='case_document')
    document_title: str | None = None
    document_type: str | None = None
    case_id: str | None = None

    # ── Common ───────────────────────────────────────────────────────────────
    chunk_index: int = 0
    chunk_text_excerpt: str = ""     # first 200 chars for UI preview
    rrf_score: float = 0.0


# ── SQL ───────────────────────────────────────────────────────────────────────

_RESOLVE_PRECEDENT_SQL = """
SELECT
  lp.case_number,
  lp.court,
  lp.decision_date::text,
  LEFT(lp.holding, 300) AS holding_summary
FROM legal_document_chunk ldc
JOIN legal_precedent lp ON lp.id = ldc.source_id
WHERE ldc.id = %s::uuid
  AND ldc.source_type = 'precedent'
"""

_RESOLVE_CASE_DOC_SQL = """
SELECT
  lcd.title AS document_title,
  lcd.document_type,
  lcd.case_id::text
FROM legal_document_chunk ldc
JOIN legal_case_document lcd ON lcd.id = ldc.source_id
WHERE ldc.id = %s::uuid
  AND ldc.source_type = 'case_document'
"""

_INSERT_QUERY_LOG_SQL = """
INSERT INTO legal_rag_query_log
  (attorney_id, case_id, query_text, query_embedding,
   retrieved_chunk_ids, citations_summary, status, latency_ms)
VALUES (%s::uuid, %s::uuid, %s, %s::vector, %s, %s, 'completed', %s)
RETURNING id::text
"""


async def resolve_citations(
    *,
    conn,                           # psycopg AsyncConnection (rls_session active)
    chunks: "list[RetrievedChunk]",
) -> list[Citation]:
    """Resolve chunk.id → source metadata for each retrieved chunk.

    Queries legal_precedent or legal_case_document based on source_type.
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
            case_id=chunk.case_id,
            chunk_index=chunk.chunk_index,
            chunk_text_excerpt=chunk.chunk_text[:200],
            rrf_score=chunk.rrf_score,
        )

        if chunk.source_type == "precedent":
            cur = await conn.execute(_RESOLVE_PRECEDENT_SQL, (chunk.chunk_id,))
            row = await cur.fetchone()
            if row:
                cit.case_number = row[0]
                cit.court = row[1]
                cit.decision_date = row[2]
                cit.holding_summary = row[3]
            else:
                logger.warning(
                    "Could not resolve precedent for chunk_id=%s source_id=%s",
                    chunk.chunk_id, chunk.source_id,
                )

        elif chunk.source_type == "case_document":
            cur = await conn.execute(_RESOLVE_CASE_DOC_SQL, (chunk.chunk_id,))
            row = await cur.fetchone()
            if row:
                cit.document_title = row[0]
                cit.document_type = row[1]
                cit.case_id = row[2]
            else:
                logger.warning(
                    "Could not resolve case_document for chunk_id=%s source_id=%s",
                    chunk.chunk_id, chunk.source_id,
                )

        citations.append(cit)

    return citations


async def log_query(
    *,
    conn,                           # psycopg AsyncConnection (rls_session active)
    attorney_id: str | uuid.UUID,
    query_text: str,
    query_embedding: list[float] | None,
    citations: list[Citation],
    case_id: str | uuid.UUID | None = None,
    latency_ms: int | None = None,
) -> str:
    """Append a completed search to legal_rag_query_log.

    Stores retrieved_chunk_ids as JSON array (citation contract),
    citations_summary as JSON list of resolved citation dicts.

    Args:
        conn:            psycopg connection with active rls_session().
        attorney_id:     UUID of the querying attorney.
        query_text:      Original query string.
        query_embedding: 768-dim vector (or None if unavailable).
        citations:       Resolved citations from resolve_citations().
        case_id:         Optional scoping case UUID.
        latency_ms:      Total search latency for cost tracking.

    Returns:
        Created log row id (UUID str).
    """
    chunk_ids_json = json.dumps([c.chunk_id for c in citations])
    citations_json = json.dumps([asdict(c) for c in citations], default=str)

    attorney_id_str = str(uuid.UUID(str(attorney_id)))
    case_id_str = str(uuid.UUID(str(case_id))) if case_id else None

    cur = await conn.execute(
        _INSERT_QUERY_LOG_SQL,
        (
            attorney_id_str,
            case_id_str,
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
        "Query logged: log_id=%s attorney=%s chunks=%d",
        log_id, attorney_id_str, len(citations),
    )
    return log_id
