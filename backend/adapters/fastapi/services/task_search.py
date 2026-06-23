"""
services/task_search.py — Lite-AI semantic-like issue search service.

Wire key (future): project.search-similar
TODO: Register 'project.search-similar' in middle/contract/wire-v1.yaml
      once the contract owner decides on the stable wire key shape.
      This module is adapter-level only for now.

Design:
  - EmbeddingProvider protocol: embed(texts) -> list[list[float]]
  - LocalEmbeddingProvider: calls TASKFLOW_EMBED_URL (TEI / embedding gemma)
    via stdlib urllib.request ONLY — no httpx, no numpy, no cloud API deps.
  - Fallback: trigram Jaccard lexical similarity (pure Python, 0 external deps)
    activated when TASKFLOW_EMBED_URL is unset OR embedding call fails.
  - search_similar() returns results with a 'mode' field ("semantic"|"lexical")
    so the UI can display an honest badge (pattern: legal-rag keyword badge).

Honesty boundary:
  - Cloud API: ZERO. TASKFLOW_EMBED_URL is env-injected and expected to point
    to a local self-hosted endpoint (TEI, Ollama, etc.). No cloud URL is
    ever hardcoded or used as a fallback.
  - When mode="lexical", the caller knows this is NOT vector similarity.
    Do not claim or display "AI similarity" when mode is "lexical".

$0 boundary: server runtime cost only. No per-request LLM/cloud API cost.
"""

from __future__ import annotations

import json
import logging
import math
import os
from typing import Any, Protocol, runtime_checkable

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Typing helpers
# ---------------------------------------------------------------------------

Embedding = list[float]


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Minimal embedding provider interface."""

    def embed(self, texts: list[str]) -> list[Embedding]:
        """Return one embedding vector per input text (same order, same length)."""
        ...


# ---------------------------------------------------------------------------
# LocalEmbeddingProvider — stdlib urllib.request only, no cloud fallback
# ---------------------------------------------------------------------------

class LocalEmbeddingProvider:
    """
    Posts texts to a local TEI / embedding-gemma endpoint.

    URL is taken exclusively from TASKFLOW_EMBED_URL env var.
    If the env var is unset, this provider should not be instantiated
    (use _resolve_provider() which handles the fallback decision).

    No external dependencies. Uses stdlib urllib.request + json.
    No cloud API URL is hardcoded here or elsewhere in this module.
    """

    def __init__(self, embed_url: str) -> None:
        self._url = embed_url.rstrip("/")

    def embed(self, texts: list[str]) -> list[Embedding]:
        """
        POST {"inputs": texts} to the TEI endpoint.

        Returns list of float vectors, one per input text.
        Raises RuntimeError on any network/parse failure (caller catches).
        """
        import urllib.request

        payload = json.dumps({"inputs": texts}).encode("utf-8")
        req = urllib.request.Request(
            url=self._url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode("utf-8")
        except Exception as exc:
            raise RuntimeError(f"Embedding endpoint call failed: {exc}") from exc

        try:
            result = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Embedding endpoint returned non-JSON: {body[:200]}") from exc

        # TEI returns either [[...]] (batch) or [float, ...] (single).
        # Normalise to always list[list[float]].
        if not result:
            raise RuntimeError("Embedding endpoint returned empty result")
        if isinstance(result[0], list):
            return [list(map(float, vec)) for vec in result]
        # Single-item batch returned as flat list of floats
        return [list(map(float, result))]


# ---------------------------------------------------------------------------
# Lexical fallback — trigram Jaccard, pure Python, 0 external deps
# ---------------------------------------------------------------------------

def _trigrams(text: str) -> set[str]:
    """Return the set of character trigrams for a string (lowercased)."""
    t = text.lower()
    if len(t) < 3:
        return {t} if t else set()
    return {t[i : i + 3] for i in range(len(t) - 2)}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _lexical_score(query: str, candidate_text: str) -> float:
    """Trigram Jaccard between query and candidate_text."""
    return _jaccard(_trigrams(query), _trigrams(candidate_text))


# ---------------------------------------------------------------------------
# Cosine similarity — pure Python, no numpy
# ---------------------------------------------------------------------------

def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def _cosine(a: list[float], b: list[float]) -> float:
    na, nb = _norm(a), _norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return _dot(a, b) / (na * nb)


# ---------------------------------------------------------------------------
# Provider resolution
# ---------------------------------------------------------------------------

def _resolve_provider() -> EmbeddingProvider | None:
    """
    Return a LocalEmbeddingProvider if TASKFLOW_EMBED_URL is set, else None.
    None means lexical fallback will be used.
    """
    url = os.environ.get("TASKFLOW_EMBED_URL", "").strip()
    if not url:
        return None
    return LocalEmbeddingProvider(url)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _candidate_text(candidate: dict[str, Any]) -> str:
    """Concatenate name + description fields for a task candidate."""
    parts = []
    name = candidate.get("name", "")
    desc = candidate.get("description", "")
    if name:
        parts.append(str(name))
    if desc:
        parts.append(str(desc))
    return " ".join(parts)


def search_similar(
    query_text: str,
    candidates: list[dict[str, Any]],
    top_n: int = 5,
    exclude_id: str | None = None,
    *,
    _provider: EmbeddingProvider | None = None,
) -> dict[str, Any]:
    """
    Rank candidates by similarity to query_text.

    Parameters
    ----------
    query_text   : search query string
    candidates   : list of entity dicts (each must have at least 'id' field)
    top_n        : maximum results to return (default 5)
    exclude_id   : optional entity id to exclude from results
    _provider    : override for testing (None = auto-resolve from env)

    Returns
    -------
    {
        "mode": "semantic" | "lexical",
        "items": [
            {"id": ..., "score": float (0–1), ...all candidate fields},
            ...
        ]
    }

    Honesty: mode is always explicitly set. Callers MUST surface this to the
    user so they know whether results are vector-based or keyword-based.
    """
    if not query_text or not query_text.strip():
        return {"mode": "lexical", "items": []}

    query_text = query_text.strip()

    # Apply exclude_id filter
    pool = [c for c in candidates if c.get("id") != exclude_id]

    if not pool:
        return {"mode": "lexical", "items": []}

    # Resolve provider (env-driven; lexical if None or call fails)
    provider = _provider if _provider is not None else _resolve_provider()

    mode = "lexical"
    scores: list[float] = []

    if provider is not None:
        # Attempt semantic embedding
        texts = [_candidate_text(c) for c in pool]
        try:
            all_texts = [query_text] + texts
            all_embeds = provider.embed(all_texts)
            if len(all_embeds) != len(all_texts):
                raise RuntimeError(
                    f"Expected {len(all_texts)} embeddings, got {len(all_embeds)}"
                )
            query_embed = all_embeds[0]
            candidate_embeds = all_embeds[1:]
            scores = [_cosine(query_embed, ce) for ce in candidate_embeds]
            mode = "semantic"
        except Exception as exc:  # noqa: BLE001
            log.warning(
                "task_search: embedding call failed (%s) — falling back to lexical",
                exc,
            )
            scores = []

    if mode == "lexical":
        # Deterministic lexical fallback
        scores = [_lexical_score(query_text, _candidate_text(c)) for c in pool]

    # Rank and return top_n
    ranked = sorted(
        zip(scores, pool),
        key=lambda t: t[0],
        reverse=True,
    )[:top_n]

    items = []
    for score, candidate in ranked:
        item = dict(candidate)
        item["score"] = round(score, 6)
        items.append(item)

    return {"mode": mode, "items": items}
