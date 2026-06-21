"""
tests/test_relevance.py — unit tests for ANN relevance capture + threshold filter.

Covers:
  1. relevance = 1 - distance calculation (ANN 2-column mock)
  2. Threshold filter: ANN-only chunk below min_relevance is dropped
  3. FTS-match chunk bypasses threshold (always kept)
  4. min=0.0 → no filtering (all pass)
  5. api /search: CitationOut.relevance serialized in response

No live DB or embedding sidecar required.
"""
from __future__ import annotations

import sys
import os
import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_chunk_row(chunk_id: str) -> tuple:
    """Minimal 7-column chunk row matching _FETCH_CHUNKS_SQL column order."""
    return (
        chunk_id,            # id::text
        "precedent",         # source_type
        str(uuid.uuid4()),   # source_id::text
        None,                # case_id::text
        0,                   # chunk_index
        "텍스트 내용",         # chunk_text
        50,                  # token_count
    )


def _build_mock_conn(fts_ids: list[str], ann_rows: list[tuple], chunk_rows: list[tuple]):
    """Build async conn mock that dispatches by SQL content.

    Handles variable call sequences depending on whether _BIGM_AVAILABLE is cached:
      - pg_bigm probe SQL  → [(False,)]  (pg_bigm absent → OR-tsquery path)
      - SET LOCAL          → []          (no-op response)
      - FTS SQL (to_tsquery / bigm)  → fts_result
      - ANN SQL (embedding <=>)      → ann_rows
      - FETCH_CHUNKS SQL (ANY)       → chunk_rows
    Dispatch by SQL keyword avoids fragility to call-count order changes.
    """
    fts_result = [(row,) for row in fts_ids]  # 1-column tuples

    class _Cur:
        def __init__(self, rows):
            self._rows = rows

        async def fetchall(self):
            return self._rows

    async def _execute(sql, params=None):
        sql_strip = sql.strip().upper()
        if "PG_EXTENSION" in sql_strip:
            # pg_bigm probe — return False so OR-tsquery path is used
            return _Cur([(False,)])
        elif sql_strip.startswith("SET"):
            # SET LOCAL pg_bigm.similarity_limit — no-op
            return _Cur([])
        elif "EMBEDDING <=>" in sql_strip:
            # ANN stage
            return _Cur(ann_rows)
        elif "ANY(" in sql_strip:
            # FETCH_CHUNKS stage
            return _Cur(chunk_rows)
        else:
            # FTS stage (to_tsquery OR bigm)
            return _Cur(fts_result)

    conn = MagicMock()
    conn.execute = _execute
    return conn


# ── Test: relevance = 1 - distance ───────────────────────────────────────────

class TestRelevanceCalculation:
    def test_relevance_equals_one_minus_distance(self):
        """ANN distance 0.2 → relevance 0.8."""
        from retrieve import hybrid_search

        cid = str(uuid.uuid4())
        ann_rows = [(cid, 0.2)]           # (id, distance) 2-column
        chunk_rows = [_make_chunk_row(cid)]
        conn = _build_mock_conn([], ann_rows, chunk_rows)

        results = asyncio.run(
            hybrid_search(
                conn=conn,
                query_text="테스트",
                query_embedding=[0.0] * 768,
                top_k=10,
                min_relevance=0.0,
            )
        )
        assert len(results) == 1
        assert results[0].relevance is not None
        assert abs(results[0].relevance - 0.8) < 1e-4

    def test_relevance_clamped_at_zero(self):
        """Distance > 1.0 (edge case) → relevance clamped to 0.0."""
        from retrieve import hybrid_search

        cid = str(uuid.uuid4())
        ann_rows = [(cid, 1.3)]
        chunk_rows = [_make_chunk_row(cid)]
        conn = _build_mock_conn([], ann_rows, chunk_rows)

        results = asyncio.run(
            hybrid_search(
                conn=conn,
                query_text="테스트",
                query_embedding=[0.0] * 768,
                top_k=10,
                min_relevance=0.0,
            )
        )
        assert len(results) == 1
        assert results[0].relevance == 0.0

    def test_relevance_rounded_to_4_decimals(self):
        """relevance is rounded to 4 decimal places."""
        from retrieve import hybrid_search

        cid = str(uuid.uuid4())
        ann_rows = [(cid, 1 / 3)]        # distance ≈ 0.3333...
        chunk_rows = [_make_chunk_row(cid)]
        conn = _build_mock_conn([], ann_rows, chunk_rows)

        results = asyncio.run(
            hybrid_search(
                conn=conn,
                query_text="테스트",
                query_embedding=[0.0] * 768,
                top_k=10,
                min_relevance=0.0,
            )
        )
        assert len(results) == 1
        # 1 - 1/3 ≈ 0.6667, rounded to 4 places
        assert results[0].relevance == round(1.0 - 1 / 3, 4)


# ── Test: threshold filter ────────────────────────────────────────────────────

class TestRelevanceFilter:
    def test_ann_only_below_threshold_dropped(self):
        """ANN-only chunk with relevance < min_relevance is removed."""
        from retrieve import hybrid_search

        cid = str(uuid.uuid4())
        ann_rows = [(cid, 0.2)]          # relevance = 0.8
        chunk_rows = [_make_chunk_row(cid)]
        conn = _build_mock_conn([], ann_rows, chunk_rows)

        # threshold 0.85 > 0.8 → must be dropped
        results = asyncio.run(
            hybrid_search(
                conn=conn,
                query_text="테스트",
                query_embedding=[0.0] * 768,
                top_k=10,
                min_relevance=0.85,
            )
        )
        assert results == []

    def test_ann_only_above_threshold_kept(self):
        """ANN-only chunk with relevance >= min_relevance passes."""
        from retrieve import hybrid_search

        cid = str(uuid.uuid4())
        ann_rows = [(cid, 0.05)]         # relevance = 0.95
        chunk_rows = [_make_chunk_row(cid)]
        conn = _build_mock_conn([], ann_rows, chunk_rows)

        results = asyncio.run(
            hybrid_search(
                conn=conn,
                query_text="테스트",
                query_embedding=[0.0] * 768,
                top_k=10,
                min_relevance=0.85,
            )
        )
        assert len(results) == 1
        assert results[0].relevance == pytest.approx(0.95, abs=1e-4)

    def test_fts_match_bypasses_threshold(self):
        """FTS-matched chunk is kept even if relevance < min_relevance."""
        from retrieve import hybrid_search

        cid = str(uuid.uuid4())
        # FTS hit + ANN hit with low relevance
        ann_rows = [(cid, 0.3)]          # relevance = 0.7
        chunk_rows = [_make_chunk_row(cid)]
        conn = _build_mock_conn([cid], ann_rows, chunk_rows)

        # threshold 0.85 > 0.7 but FTS hit → must survive
        results = asyncio.run(
            hybrid_search(
                conn=conn,
                query_text="테스트",
                query_embedding=[0.0] * 768,
                top_k=10,
                min_relevance=0.85,
            )
        )
        assert len(results) == 1
        assert results[0].fts_rank == 1   # confirmed FTS match

    def test_min_zero_no_filtering(self):
        """min_relevance=0.0 → all chunks pass regardless of distance."""
        from retrieve import hybrid_search

        ids = [str(uuid.uuid4()) for _ in range(3)]
        ann_rows = [(ids[0], 0.95), (ids[1], 0.5), (ids[2], 0.01)]
        chunk_rows = [_make_chunk_row(cid) for cid in ids]
        conn = _build_mock_conn([], ann_rows, chunk_rows)

        results = asyncio.run(
            hybrid_search(
                conn=conn,
                query_text="테스트",
                query_embedding=[0.0] * 768,
                top_k=10,
                min_relevance=0.0,
            )
        )
        assert len(results) == 3

    def test_rrf_order_preserved_after_filter(self):
        """After filtering, remaining results maintain descending RRF order."""
        from retrieve import hybrid_search

        # Two ANN-only chunks: one above threshold, one below
        id_high = str(uuid.uuid4())
        id_low = str(uuid.uuid4())
        # ANN order: id_high first (rank 1, distance 0.05 → relevance 0.95)
        #            id_low  second (rank 2, distance 0.3  → relevance 0.7)
        ann_rows = [(id_high, 0.05), (id_low, 0.3)]
        chunk_rows = [_make_chunk_row(id_high), _make_chunk_row(id_low)]
        conn = _build_mock_conn([], ann_rows, chunk_rows)

        results = asyncio.run(
            hybrid_search(
                conn=conn,
                query_text="테스트",
                query_embedding=[0.0] * 768,
                top_k=10,
                min_relevance=0.85,   # id_low (0.7) dropped
            )
        )
        assert len(results) == 1
        assert results[0].chunk_id == id_high


# ── Test: api CitationOut.relevance serialization ────────────────────────────

class TestCitationOutRelevance:
    """CitationOut model includes relevance field that round-trips through JSON."""

    def test_citation_out_relevance_field_present(self):
        from api import CitationOut
        cit = CitationOut(
            chunk_id=str(uuid.uuid4()),
            source_type="precedent",
            source_id=str(uuid.uuid4()),
            case_id=None,
            chunk_index=0,
            chunk_text_excerpt="판례 내용",
            rrf_score=0.032,
            relevance=0.8765,
        )
        d = cit.model_dump()
        assert d["relevance"] == pytest.approx(0.8765)

    def test_citation_out_relevance_none_allowed(self):
        """relevance=None is valid (FTS-only hit with no ANN distance)."""
        from api import CitationOut
        cit = CitationOut(
            chunk_id=str(uuid.uuid4()),
            source_type="precedent",
            source_id=str(uuid.uuid4()),
            case_id=None,
            chunk_index=0,
            chunk_text_excerpt="판례",
            rrf_score=0.016,
            relevance=None,
        )
        d = cit.model_dump()
        assert d["relevance"] is None
