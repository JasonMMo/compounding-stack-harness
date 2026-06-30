"""
retrieve.py — hybrid search (FTS + vector ANN + RRF).

Pipeline (CTO confirmed, change requires CTO sign-off):
  Stage 1: FTS   — dual-path Korean keyword search (see below)
  Stage 2: ANN   — embedding <=> query_vec (HNSW, cosine) on hanbang_rag_document_chunk
  Stage 3: RRF   — Reciprocal Rank Fusion, k=60, merges both ranked lists
  Output:  Top-K chunks with rank score, source metadata

RLS: conn must have rls_session() active (user_id SET LOCAL).
     Notice chunks visible to all authenticated users.

Korean FTS — dual-path:
  pg_bigm present:  per-token LIKE chain (gin_bigm_ops accelerated, substring match).
                    OR  mode: (chunk_text LIKE %tok1% OR  chunk_text LIKE %tok2%) — high recall.
                    AND mode: (chunk_text LIKE %tok1% AND chunk_text LIKE %tok2%) — precise.
                    NOTE: =% full-similarity was removed — it scores short-query vs long-chunk
                    structurally near 0 (live: =% '손해배상' = 0 rows, tsquery = 22 rows).
                    LIKE is the correct pg_bigm use: substring match including inside larger
                    Korean tokens (e.g. '손해배상' matches '손해배상금').
  pg_bigm absent:   tsquery fallback via _build_tsquery():
                    OR mode: joins tokens with ' | '.
                    AND mode: joins tokens with ' & '.
                    Single-term: passes through as-is (no ambiguity).

match_mode parameter (hybrid_search):
  'or'  — default; any-term match via LIKE OR-chain (bigm) or tsquery OR (fallback).
  'and' — all-term match via LIKE AND-chain (bigm) or tsquery AND (fallback).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# ── pg_bigm probe ──────────────────────────────────────────────────────────────
_BIGM_AVAILABLE: bool | None = None


async def _probe_bigm(conn) -> bool:
    """Return True if pg_bigm extension is installed. Caches result module-wide."""
    global _BIGM_AVAILABLE
    if _BIGM_AVAILABLE is not None:
        return _BIGM_AVAILABLE
    try:
        cur = await conn.execute(
            "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname='pg_bigm')"
        )
        rows = await cur.fetchall()
        _BIGM_AVAILABLE = bool(rows[0][0]) if rows else False
    except Exception:
        logger.warning("pg_bigm probe failed; falling back to OR-tsquery.", exc_info=True)
        _BIGM_AVAILABLE = False
    logger.info("pg_bigm available: %s", _BIGM_AVAILABLE)
    return _BIGM_AVAILABLE


# ── tokenizer + tsquery / bigm-LIKE builders (pure, testable) ─────────────────


def _tokenize(query_text: str) -> list[str]:
    """Whitespace-split + sanitize (keep ASCII word chars + Korean syllables). Drops empties."""
    out = []
    for tok in query_text.split():
        clean = re.sub(r"[^\w가-힣]", "", tok)
        if clean:
            out.append(clean)
    return out


def _build_tsquery(query_text: str, operator: str) -> str | None:
    """Build a tsquery string from a raw query using the given operator.

    operator must be ' | ' (OR) or ' & ' (AND).
    Returns None if no valid tokens remain (caller should skip FTS stage).
    """
    toks = _tokenize(query_text)
    if not toks:
        return None
    return operator.join(toks)


def _build_or_tsquery(query_text: str) -> str | None:
    """Build an OR-combined tsquery string. Thin wrapper around _build_tsquery."""
    return _build_tsquery(query_text, " | ")


def _build_bigm_like(query_text: str, operator: str) -> tuple[str, list[str]] | None:
    """Build a WHERE fragment + bind params for LIKE-based bigm AND/OR search.

    operator must be 'AND' or 'OR'.
    Returns (where_fragment, like_params) or None if no valid tokens.
    """
    toks = _tokenize(query_text)
    if not toks:
        return None
    frag = "(" + f" {operator} ".join(["chunk_text LIKE %s"] * len(toks)) + ")"
    return frag, [f"%{t}%" for t in toks]


@dataclass
class RetrievedChunk:
    chunk_id: str           # hanbang_rag_document_chunk.id (UUID str) — citation anchor
    source_type: str        # 'notice'
    source_id: str          # FK UUID str (hanbang_rag_notice.id)
    case_id: str | None     # always None for notice chunks
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

# Stage 1-B: FTS via OR-tsquery (pg_bigm absent).
# {case_filter} is replaced at call time with either "" or "AND case_id = %s::uuid".
_FTS_OR_SQL = """
SELECT id::text
FROM hanbang_rag_document_chunk
WHERE to_tsvector('simple', chunk_text) @@ to_tsquery('simple', %s)
  AND embedding IS NOT NULL {case_filter}
ORDER BY ts_rank_cd(to_tsvector('simple', chunk_text), to_tsquery('simple', %s)) DESC
LIMIT %s
"""

# Stage 2: ANN candidates
_ANN_SQL = """
SELECT id::text, embedding <=> %s::vector AS distance
FROM hanbang_rag_document_chunk
WHERE embedding IS NOT NULL {case_filter}
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
FROM hanbang_rag_document_chunk
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
    match_mode: str = "or",
    case_id: str | None = None,
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
        match_mode:      'or' (default) or 'and'.
        case_id:         Not used for notice-only source type (always None).

    Returns:
        List of RetrievedChunk ordered by RRF score descending.
    """
    if match_mode not in ("or", "and"):
        raise ValueError(f"match_mode must be 'or' or 'and', got {match_mode!r}")
    if not query_text.strip():
        raise ValueError("query_text must not be empty.")
    if len(query_embedding) != 768:
        raise ValueError(
            f"query_embedding must be 768-dim, got {len(query_embedding)}"
        )

    if case_id is not None:
        case_filter = "AND case_id = %s::uuid"
        case_params: list[str] = [case_id]
    else:
        case_filter = ""
        case_params = []

    # Stage 1: FTS — dual-path (pg_bigm or tsquery)
    use_bigm = await _probe_bigm(conn)
    fts_ids: list[str] = []

    if use_bigm:
        op = "AND" if match_mode == "and" else "OR"
        built = _build_bigm_like(query_text, op)
        if built is None:
            logger.debug("FTS stage (bigm %s) skipped: no valid tokens in %r", op, query_text)
        else:
            frag, like_params = built
            sql = (
                "SELECT id::text, bigm_similarity(chunk_text, %s) AS sim "
                "FROM hanbang_rag_document_chunk "
                f"WHERE {frag} AND embedding IS NOT NULL {case_filter} "
                "ORDER BY sim DESC LIMIT %s"
            )
            fts_cur = await conn.execute(
                sql, (query_text, *like_params, *case_params, fts_limit)
            )
            fts_rows = await fts_cur.fetchall()
            fts_ids = [r[0] for r in fts_rows]
            logger.debug("FTS stage (bigm %s): %d candidates", op, len(fts_ids))

    else:
        op = " & " if match_mode == "and" else " | "
        ts_query = _build_tsquery(query_text, op)
        if ts_query is None:
            logger.debug("FTS stage skipped: no valid tokens in %r", query_text)
        else:
            fts_cur = await conn.execute(
                _FTS_OR_SQL.format(case_filter=case_filter),
                (ts_query, *case_params, ts_query, fts_limit),
            )
            fts_rows = await fts_cur.fetchall()
            fts_ids = [r[0] for r in fts_rows]
            logger.debug(
                "FTS stage (tsquery=%r, mode=%s): %d candidates",
                ts_query, match_mode, len(fts_ids),
            )

    # Stage 2: ANN
    ann_cur = await conn.execute(
        _ANN_SQL.format(case_filter=case_filter),
        (query_embedding, *case_params, ann_limit),
    )
    ann_rows = await ann_cur.fetchall()
    ann_ids = [r[0] for r in ann_rows]
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

    chunk_map = {row[0]: row for row in chunk_rows}

    results: list[RetrievedChunk] = []
    for cid, score, fts_rank, ann_rank in merged[:top_k]:
        row = chunk_map.get(cid)
        if row is None:
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
