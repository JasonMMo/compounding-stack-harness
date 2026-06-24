"""
test_task_search.py — L1 unit tests for services/task_search.py

Scenarios:
  1. TASKFLOW_EMBED_URL unset → lexical mode, deterministic results
  2. TASKFLOW_EMBED_URL set + provider monkeypatched → semantic mode, top_n order correct
  3. Embedding call fails → lexical fallback (graceful)
  4. exclude_id removes the specified candidate
  5. Empty candidates list → graceful empty result
  6. Empty query_text → graceful empty result

Run (from repo root):
    python -m pytest backend/adapters/fastapi/tests/test_task_search.py -v

All tests are self-contained: no running server, no network calls, no cloud API.
"""

from __future__ import annotations

import math
import os
import sys
import pathlib

# Ensure the adapter root is on sys.path so imports resolve without installation
_ADAPTER_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ADAPTER_DIR))

import pytest

from services.task_search import (
    EmbeddingProvider,
    LocalEmbeddingProvider,
    _lexical_score,
    _trigrams,
    _cosine,
    search_similar,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TASKS = [
    {
        "id": "task-1",
        "name": "Fix login bug",
        "description": "Users cannot log in after password reset",
        "status": "todo",
    },
    {
        "id": "task-2",
        "name": "Implement dark mode",
        "description": "Add toggle for dark theme in user settings",
        "status": "in-progress",
    },
    {
        "id": "task-3",
        "name": "Database migration script",
        "description": "Write migration to add index on email column",
        "status": "todo",
    },
    {
        "id": "task-4",
        "name": "Update password reset email template",
        "description": "Refresh the transactional email design for password reset flow",
        "status": "todo",
    },
    {
        "id": "task-5",
        "name": "Performance tuning",
        "description": "Optimise slow SQL queries on the reports page",
        "status": "in-progress",
    },
]


# ---------------------------------------------------------------------------
# Helper: a fake EmbeddingProvider for monkeypatching
# ---------------------------------------------------------------------------

class _FixedEmbeddingProvider:
    """
    Returns pre-defined embeddings so tests are deterministic.
    Mirrors the asymmetric provider contract: embed_query(text) for the search
    query, embed_passages(texts) for the candidate tasks (G-87 query/passage).
    All embeddings are 4-dimensional vectors (different per text index).
    """

    def __init__(self, query_vec: list[float], passage_vecs: list[list[float]]) -> None:
        self._query_vec = query_vec
        self._passage_vecs = passage_vecs

    def embed_query(self, text: str) -> list[float]:
        return self._query_vec

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        if len(texts) > len(self._passage_vecs):
            raise ValueError(
                f"Fake provider only has {len(self._passage_vecs)} passage embeddings"
            )
        return self._passage_vecs[: len(texts)]


class _FailingEmbeddingProvider:
    """Always raises RuntimeError to test graceful fallback."""

    def embed_query(self, text: str) -> list[float]:
        raise RuntimeError("Simulated embedding endpoint failure")

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        raise RuntimeError("Simulated embedding endpoint failure")


# ---------------------------------------------------------------------------
# 1. Lexical mode when TASKFLOW_EMBED_URL is unset
# ---------------------------------------------------------------------------

class TestLexicalMode:
    def test_returns_lexical_mode_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("password reset", TASKS, top_n=5)
        assert result["mode"] == "lexical"

    def test_lexical_results_are_deterministic(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        r1 = search_similar("password reset", TASKS, top_n=3)
        r2 = search_similar("password reset", TASKS, top_n=3)
        assert [i["id"] for i in r1["items"]] == [i["id"] for i in r2["items"]]

    def test_lexical_top_n_respected(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("password reset", TASKS, top_n=2)
        assert len(result["items"]) <= 2

    def test_lexical_scores_descending(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("password reset", TASKS, top_n=5)
        scores = [i["score"] for i in result["items"]]
        assert scores == sorted(scores, reverse=True)

    def test_lexical_items_contain_score_field(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("login bug", TASKS, top_n=3)
        for item in result["items"]:
            assert "score" in item
            assert 0.0 <= item["score"] <= 1.0

    def test_lexical_relevant_task_scores_higher(self, monkeypatch):
        """'Fix login bug' should outscore 'dark mode' when querying 'login'."""
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("login", TASKS, top_n=5)
        ids = [i["id"] for i in result["items"]]
        # task-1 (Fix login bug) should appear before task-2 (dark mode)
        assert "task-1" in ids
        pos_login = ids.index("task-1")
        if "task-2" in ids:
            pos_dark = ids.index("task-2")
            assert pos_login < pos_dark

    def test_env_empty_string_also_falls_back(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_EMBED_URL", "")
        result = search_similar("database", TASKS, top_n=5)
        assert result["mode"] == "lexical"


# ---------------------------------------------------------------------------
# 2. Semantic mode with monkeypatched provider
# ---------------------------------------------------------------------------

class TestSemanticMode:
    def _make_provider_and_embeddings(self):
        """
        Build a deterministic fake provider where:
          embed[0] = query embedding (aligned with task-1 and task-4)
          embed[1..5] = candidate embeddings (task-1..task-5 order matches TASKS)
        We set task-1 to be closest to query (cosine ~1.0), task-5 farthest.
        """
        # 4-dim vectors; we'll set them to be distinct
        query_vec = [1.0, 0.0, 0.0, 0.0]
        task_vecs = [
            [1.0, 0.0, 0.0, 0.0],   # task-1: identical to query → cosine 1.0
            [0.0, 1.0, 0.0, 0.0],   # task-2: orthogonal → cosine 0.0
            [0.5, 0.5, 0.0, 0.0],   # task-3: partial overlap
            [0.9, 0.1, 0.0, 0.0],   # task-4: close to query
            [0.0, 0.0, 1.0, 0.0],   # task-5: orthogonal → cosine 0.0
        ]
        return _FixedEmbeddingProvider(query_vec, task_vecs)

    def test_returns_semantic_mode_when_provider_set(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_EMBED_URL", "http://localhost:9999")
        provider = self._make_provider_and_embeddings()
        result = search_similar("login", TASKS, top_n=5, _provider=provider)
        assert result["mode"] == "semantic"

    def test_semantic_top_n_order_correct(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_EMBED_URL", "http://localhost:9999")
        provider = self._make_provider_and_embeddings()
        result = search_similar("login", TASKS, top_n=3, _provider=provider)
        ids = [i["id"] for i in result["items"]]
        # task-1 (cosine 1.0) must be first, task-4 (0.9x) second
        assert ids[0] == "task-1"
        assert ids[1] == "task-4"

    def test_semantic_top_n_count_respected(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_EMBED_URL", "http://localhost:9999")
        provider = self._make_provider_and_embeddings()
        result = search_similar("login", TASKS, top_n=2, _provider=provider)
        assert len(result["items"]) == 2

    def test_semantic_scores_descending(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_EMBED_URL", "http://localhost:9999")
        provider = self._make_provider_and_embeddings()
        result = search_similar("login", TASKS, top_n=5, _provider=provider)
        scores = [i["score"] for i in result["items"]]
        assert scores == sorted(scores, reverse=True)

    def test_semantic_score_field_present(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_EMBED_URL", "http://localhost:9999")
        provider = self._make_provider_and_embeddings()
        result = search_similar("login", TASKS, top_n=5, _provider=provider)
        for item in result["items"]:
            assert "score" in item


# ---------------------------------------------------------------------------
# 3. Embedding failure → lexical fallback
# ---------------------------------------------------------------------------

class TestEmbeddingFailureFallback:
    def test_falls_back_to_lexical_on_provider_failure(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_EMBED_URL", "http://localhost:9999")
        failing = _FailingEmbeddingProvider()
        result = search_similar("database migration", TASKS, top_n=5, _provider=failing)
        assert result["mode"] == "lexical"

    def test_fallback_still_returns_results(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_EMBED_URL", "http://localhost:9999")
        failing = _FailingEmbeddingProvider()
        result = search_similar("database migration", TASKS, top_n=3, _provider=failing)
        assert len(result["items"]) > 0

    def test_fallback_scores_descending(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_EMBED_URL", "http://localhost:9999")
        failing = _FailingEmbeddingProvider()
        result = search_similar("migration", TASKS, top_n=5, _provider=failing)
        scores = [i["score"] for i in result["items"]]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# 4. exclude_id removes the candidate
# ---------------------------------------------------------------------------

class TestExcludeId:
    def test_excluded_id_not_in_results(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar(
            "password reset", TASKS, top_n=5, exclude_id="task-1"
        )
        ids = [i["id"] for i in result["items"]]
        assert "task-1" not in ids

    def test_exclude_nonexistent_id_is_noop(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result_without = search_similar("login", TASKS, top_n=5)
        result_with = search_similar("login", TASKS, top_n=5, exclude_id="no-such-id")
        assert len(result_with["items"]) == len(result_without["items"])

    def test_exclude_only_candidate_returns_empty(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        single = [{"id": "only", "name": "Only task", "description": ""}]
        result = search_similar("task", single, top_n=5, exclude_id="only")
        assert result["items"] == []


# ---------------------------------------------------------------------------
# 5. Empty candidates → graceful
# ---------------------------------------------------------------------------

class TestEmptyCandidates:
    def test_empty_candidates_returns_empty_items(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("login", [], top_n=5)
        assert result["items"] == []

    def test_empty_candidates_has_mode_field(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("login", [], top_n=5)
        assert "mode" in result


# ---------------------------------------------------------------------------
# 6. Empty query_text → graceful
# ---------------------------------------------------------------------------

class TestEmptyQuery:
    def test_empty_string_returns_empty(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("", TASKS, top_n=5)
        assert result["items"] == []

    def test_whitespace_only_returns_empty(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("   ", TASKS, top_n=5)
        assert result["items"] == []

    def test_empty_query_has_mode_field(self, monkeypatch):
        monkeypatch.delenv("TASKFLOW_EMBED_URL", raising=False)
        result = search_similar("", TASKS, top_n=5)
        assert "mode" in result


# ---------------------------------------------------------------------------
# Unit tests for internal helpers
# ---------------------------------------------------------------------------

class TestTrigrams:
    def test_short_string_single_gram(self):
        assert _trigrams("ab") == {"ab"}

    def test_empty_string_empty_set(self):
        assert _trigrams("") == set()

    def test_three_char_single_gram(self):
        assert _trigrams("abc") == {"abc"}

    def test_four_char_two_grams(self):
        grams = _trigrams("abcd")
        assert "abc" in grams and "bcd" in grams


class TestCosine:
    def test_identical_vectors(self):
        v = [1.0, 2.0, 3.0]
        assert abs(_cosine(v, v) - 1.0) < 1e-9

    def test_orthogonal_vectors(self):
        assert _cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_zero_vector_returns_zero(self):
        assert _cosine([0.0, 0.0], [1.0, 2.0]) == 0.0
