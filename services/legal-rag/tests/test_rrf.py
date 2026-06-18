"""
tests/test_rrf.py — unit tests for rrf_merge() (pure function, no DB/sidecar).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from retrieve import rrf_merge, _rrf_score


class TestRrfScore:
    def test_none_rank_returns_zero(self):
        assert _rrf_score(None, k=60) == 0.0

    def test_rank_1_k60(self):
        assert abs(_rrf_score(1, 60) - 1 / 61) < 1e-9

    def test_rank_100_k60(self):
        assert abs(_rrf_score(100, 60) - 1 / 160) < 1e-9

    def test_higher_rank_gives_higher_score(self):
        assert _rrf_score(1, 60) > _rrf_score(2, 60) > _rrf_score(100, 60)


class TestRrfMerge:
    def test_empty_both_lists_returns_empty(self):
        result = rrf_merge([], [], k=60)
        assert result == []

    def test_fts_only(self):
        fts = ["a", "b", "c"]
        result = rrf_merge(fts, [], k=60)
        ids = [r[0] for r in result]
        # All FTS items present
        assert set(ids) == {"a", "b", "c"}
        # Sorted by score descending
        scores = [r[1] for r in result]
        assert scores == sorted(scores, reverse=True)
        # "a" (rank 1) should have highest score
        assert result[0][0] == "a"

    def test_ann_only(self):
        ann = ["x", "y", "z"]
        result = rrf_merge([], ann, k=60)
        assert result[0][0] == "x"

    def test_overlapping_id_gets_combined_score(self):
        # "a" appears at rank 1 in both → highest combined score
        fts = ["a", "b", "c"]
        ann = ["a", "d", "e"]
        result = rrf_merge(fts, ann, k=60)
        top = result[0]
        assert top[0] == "a"
        # Score = 1/(60+1) + 1/(60+1) = 2/61
        expected = 2 / 61
        assert abs(top[1] - expected) < 1e-9

    def test_non_overlapping_lists_union(self):
        fts = ["a", "b"]
        ann = ["c", "d"]
        result = rrf_merge(fts, ann, k=60)
        ids = {r[0] for r in result}
        assert ids == {"a", "b", "c", "d"}

    def test_fts_rank_and_ann_rank_recorded(self):
        fts = ["a", "b"]
        ann = ["b", "c"]
        result = rrf_merge(fts, ann, k=60)
        by_id = {r[0]: r for r in result}
        # "a" only in fts (rank 1), ann_rank None
        assert by_id["a"][2] == 1   # fts_rank
        assert by_id["a"][3] is None  # ann_rank
        # "b" in both
        assert by_id["b"][2] == 2   # fts_rank 2
        assert by_id["b"][3] == 1   # ann_rank 1
        # "c" only in ann
        assert by_id["c"][2] is None
        assert by_id["c"][3] == 2

    def test_k_parameter_changes_scores(self):
        fts = ["a"]
        r_k60 = rrf_merge(fts, [], k=60)
        r_k10 = rrf_merge(fts, [], k=10)
        # k=10 gives higher score (1/11 > 1/61)
        assert r_k10[0][1] > r_k60[0][1]

    def test_result_sorted_descending(self):
        fts = ["a", "b", "c", "d"]
        ann = ["d", "c", "b", "a"]
        result = rrf_merge(fts, ann, k=60)
        scores = [r[1] for r in result]
        assert scores == sorted(scores, reverse=True)
