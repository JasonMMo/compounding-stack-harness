"""
retrieve.py — hybrid search (FTS + vector ANN + RRF).

Pipeline (CTO confirmed, change requires CTO sign-off):
  Stage 1: FTS   — plainto_tsquery on legal_document_chunk.chunk_text (GIN index)
  Stage 2: ANN   — embedding <=> query_vec (HNSW, cosine) on legal_document_chunk
  Stage 3: RRF   — Reciprocal Rank Fusion, k=60, merges both ranked lists
  Output:  Top-K chunks with rank score, source metadata, case_id

RLS: conn must have rls_session() active (attorney_id SET LOCAL).
     Precedent chunks visible to all. Case_document chunks scoped to attorney.

Korean support: FTS uses 'simple' dictionary (no Korean stemmer needed for pg_bigm
trigram assist which handles subword matching via idx_legal_chunk_fts GIN).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: str           # legal_document_chunk.id (UUID str) — citation anchor
    source_type: str        # 'precedent' | 'case_document'
    source_id: str          # FK UUID str
    case_id: str | None     # UUID str or None (precedent chunks have no case)
    chunk_index: int
    chunk_text: str
    token_count: int | None
    rrf_score: float        # higher = more relevant
    fts_rank: int | None    # rank in FTS result (1-based), None if not in FTS results
    ann_rank: int | None    # rank in ANN result (1-based), None if not in ANN results
    relevance: float | None = None  # cosine similarity: 1 - ANN distance. None if ANN miss.


def _rrf_score(rank: int | None, k: int) -> float:
    """RRF score for a single ranklist entry: 1 / (k + rank)."""
    if rank is None:
        return 0.0
    return 1.0 / (k + rank)


def rrf_merge(
    fts_ids: list[str],
    ann_ids: list[str],
    k: int = 60,
) -> list[tuple[str, float, int | None, int | None]]:
    """Pure RRF merge of two ranked ID lists.

    Args:
        fts_ids: Ordered chunk IDs from FTS (best first).
        ann_ids: Ordered chunk IDs from ANN (best first).
        k:       RRF constant (default 60).

    Returns:
        List of (chunk_id, rrf_score, fts_rank, ann_rank) sorted descending by score.
    """
    all_ids: dict[str, dict[str, Any]] = {}

    for rank, cid in enumerate(fts_ids, start=1):
        all_ids.setdefault(cid, {"fts_rank": None, "ann_rank": None})
        all_ids[cid]["fts_rank"] = rank

    for rank, cid in enumerate(ann_ids, start=1):
        all_ids.setdefault(cid, {"fts_rank": None, "ann_rank": None})
        all_ids[cid]["ann_rank"] = rank

    scored = []
    for cid, ranks in all_ids.items():
        score = _rrf_score(ranks["fts_rank"], k) + _rrf_score(ranks["ann_rank"], k)
        scored.append((cid, score, ranks["fts_rank"], ranks["ann_rank"]))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


# ── SQL templates ──────────────────────────────────────────────────────────────

# Stage 1: FTS candidates
# Uses chunk_text GIN index via to_tsvector('simple', chunk_text).
# RLS policy on legal_document_chunk scopes results automatically.
_FTS_SQL = """
SELECT id::text
FROM legal_document_chunk
WHERE to_tsvector('simple', chunk_text) @@ plainto_tsquery('simple', %s)
  AND embedding IS NOT NULL
ORDER BY ts_rank_cd(to_tsvector('simple', chunk_text),
                    plainto_tsquery('simple', %s)) DESC
LIMIT %s
"""

# Stage 2: ANN candidates
# Uses HNSW index (embedding IS NOT NULL partial index covers only embedded rows).
# pgvector cosine: <=> operator (lower = more similar). ORDER BY ASC → best first.
# distance column (alias) is captured so relevance = 1 - distance can be computed.
_ANN_SQL = """
SELECT id::text, embedding <=> %s::vector AS distance
FROM legal_document_chunk
WHERE embedding IS NOT NULL
ORDER BY distance ASC
LIMIT %s
"""

# Bulk fetch full chunk rows for merged ID list (one round-trip after RRF)
_FETCH_CHUNKS_SQL = """
SELECT
  id::text,
  source_type,
  source_id::text,
  case_id::text,
  chunk_index,
  chunk_text,
  token_count
FROM legal_document_chunk
WHERE id = ANY(%s::uuid[])
"""


async def hybrid_search(
    *,
    conn,               # psycopg AsyncConnection (rls_session active)
    query_text: str,
    query_embedding: list[float],
    top_k: int = 10,
    fts_limit: int = 100,
    ann_limit: int = 100,
    rrf_k: int = 60,
    min_relevance: float = 0.0,
) -> list[RetrievedChunk]:
    """Run hybrid FTS+ANN+RRF search and return top_k chunks.

    IMPORTANT: conn must be inside an rls_session() context manager so that
    app.current_user_id is SET LOCAL. Missing session → 0 rows (RLS fail-safe).

    Args:
        conn:            psycopg AsyncConnection with active RLS session.
        query_text:      Raw query string (Korean/mixed OK).
        query_embedding: 768-dim float vector for semantic search.
        top_k:           Number of chunks to return.
        fts_limit:       Max candidates from FTS stage.
        ann_limit:       Max candidates from ANN stage.
        rrf_k:           RRF constant.
        min_relevance:   Minimum cosine relevance threshold [0.0, 1.0].
                         Results with no FTS match and relevance < min_relevance
                         are discarded. Default 0.0 = filter OFF.

    Returns:
        List of RetrievedChunk ordered by RRF score descending.
    """
    if not query_text.strip():
        raise ValueError("query_text must not be empty.")
    if len(query_embedding) != 768:
        raise ValueError(
            f"query_embedding must be 768-dim, got {len(query_embedding)}"
        )

    # Stage 1: FTS
    fts_cur = await conn.execute(
        _FTS_SQL, (query_text, query_text, fts_limit)
    )
    fts_rows = await fts_cur.fetchall()
    fts_ids = [r[0] for r in fts_rows]
    logger.debug("FTS stage: %d candidates", len(fts_ids))

    # Stage 2: ANN
    ann_cur = await conn.execute(
        _ANN_SQL, (query_embedding, ann_limit)
    )
    ann_rows = await ann_cur.fetchall()
    ann_ids = [r[0] for r in ann_rows]
    # Build {chunk_id: relevance} map. pgvector cosine distance = 1 - similarity.
    ann_relevance: dict[str, float] = {
        r[0]: max(0.0, round(1.0 - float(r[1]), 4)) for r in ann_rows
    }
    logger.debug("ANN stage: %d candidates", len(ann_ids))

    # Stage 3: RRF merge
    merged = rrf_merge(fts_ids, ann_ids, k=rrf_k)
    top_ids = [cid for cid, _, _, _ in merged[:top_k]]

    if not top_ids:
        logger.info("No results after RRF merge for query: %.60s...", query_text)
        return []

    # Fetch full chunk data (one round-trip)
    fetch_cur = await conn.execute(_FETCH_CHUNKS_SQL, (top_ids,))
    chunk_rows = await fetch_cur.fetchall()

    # Build lookup by id
    chunk_map = {row[0]: row for row in chunk_rows}

    # Build response in RRF rank order
    results: list[RetrievedChunk] = []
    for cid, score, fts_rank, ann_rank in merged[:top_k]:
        row = chunk_map.get(cid)
        if row is None:
            # RLS filtered it out (attorney lacks access) — skip silently
            logger.debug("Chunk %s filtered by RLS or missing.", cid)
            continue
        results.append(
            RetrievedChunk(
                chunk_id=row[0],
                source_type=row[1],
                source_id=row[2],
                case_id=row[3],
                chunk_index=row[4],
                chunk_text=row[5],
                token_count=row[6],
                rrf_score=score,
                fts_rank=fts_rank,
                ann_rank=ann_rank,
                relevance=ann_relevance.get(row[0]),
            )
        )

    # Relevance filter: skip ANN-only results below threshold.
    # FTS matches (fts_rank is not None) bypass the threshold — lexical hits always kept.
    if min_relevance > 0.0:
        before = len(results)
        results = [
            c for c in results
            if c.fts_rank is not None
            or (c.relevance is not None and c.relevance >= min_relevance)
        ]
        if len(results) < before:
            logger.debug(
                "Relevance filter (min=%.4f) dropped %d/%d chunks.",
                min_relevance, before - len(results), before,
            )

    logger.info(
        "hybrid_search returned %d chunks (top_k=%d) for query: %.60s...",
        len(results), top_k, query_text,
    )
    return results
