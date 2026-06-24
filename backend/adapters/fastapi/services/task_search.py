"""
services/task_search.py — Lite-AI semantic-like issue search service.

Wire key: project.search-similar (registered in middle/contract/wire-v1.yaml, Growth-123)

Design:
  - EmbeddingProvider protocol: embed_query(text) + embed_passages(texts)
    (asymmetric e5 query/passage heads, G-87).
  - LocalEmbeddingProvider: reuses the legal-rag embed-adapter sidecar
    (multilingual-e5-base, 768-dim, model baked in, offline) via TASKFLOW_EMBED_URL
    base url, stdlib urllib.request ONLY — no httpx, no numpy, no cloud API deps
    (8th-axis asset reuse, Growth-125).
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
    """
    Asymmetric embedding provider interface (e5 query/passage split, G-87).

    A search query and a stored task are embedded through DIFFERENT projection
    heads, so the provider exposes two methods instead of a single embed():
      - embed_query    → the user's search text (query head)
      - embed_passages → the candidate tasks    (passage head)
    """

    def embed_query(self, text: str) -> Embedding:
        """Return one embedding vector for a search query (query head)."""
        ...

    def embed_passages(self, texts: list[str]) -> list[Embedding]:
        """Return one embedding vector per candidate passage (passage head)."""
        ...


# ---------------------------------------------------------------------------
# LocalEmbeddingProvider — reuses the legal-rag embed-adapter contract
# (8th-axis asset reuse, Growth-125). stdlib urllib.request only, no cloud.
# ---------------------------------------------------------------------------

class LocalEmbeddingProvider:
    """
    Talks to the legal-rag embed-adapter sidecar (multilingual-e5-base, 768-dim,
    Korean+English, model baked into the image, fully offline at runtime).

    Contract (matches services/legal-rag/embed-adapter/app.py byte-for-byte):
      POST {base}/embed        {"text": str}        -> {"embedding": [float...]}   (query head)
      POST {base}/embed/batch  {"texts": [str,...]} -> {"embeddings": [[float...]]} (passage head)

    TASKFLOW_EMBED_URL is the BASE url (e.g. http://embed:8080); paths are
    appended here.  If the env var is unset, this provider is not instantiated
    (see _resolve_provider() which handles the lexical-fallback decision).

    Asymmetric prefix invariant (G-87): the adapter applies "query: " on /embed
    and "passage: " on /embed/batch.  taskflow is a NEW one-directional caller —
    search text MUST go through embed_query, candidate tasks through
    embed_passages.  Crossing them silently degrades retrieval quality.

    No external dependencies. Uses stdlib urllib.request + json. No cloud API
    URL is hardcoded here or elsewhere in this module.
    """

    def __init__(self, embed_url: str) -> None:
        self._base = embed_url.rstrip("/")

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        import urllib.request

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url=f"{self._base}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode("utf-8")
        except Exception as exc:
            raise RuntimeError(f"Embedding endpoint call failed: {exc}") from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Embedding endpoint returned non-JSON: {body[:200]}"
            ) from exc

    def embed_query(self, text: str) -> Embedding:
        """POST /embed (query head). Returns one float vector."""
        result = self._post("/embed", {"text": text})
        vec = result.get("embedding") if isinstance(result, dict) else None
        if not isinstance(vec, list) or not vec:
            raise RuntimeError(
                f"Embedding /embed response missing 'embedding': {str(result)[:200]}"
            )
        return [float(x) for x in vec]

    def embed_passages(self, texts: list[str]) -> list[Embedding]:
        """POST /embed/batch (passage head). Returns one float vector per input."""
        if not texts:
            return []
        result = self._post("/embed/batch", {"texts": texts})
        vecs = result.get("embeddings") if isinstance(result, dict) else None
        if not isinstance(vecs, list) or len(vecs) != len(texts):
            raise RuntimeError(
                f"Embedding /embed/batch malformed: expected {len(texts)} vectors, "
                f"got {str(result)[:200]}"
            )
        return [[float(x) for x in vec] for vec in vecs]


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
        # Attempt semantic embedding — asymmetric heads (G-87): query text via
        # the query head, candidate tasks via the passage head. Empty candidate
        # text is replaced with a placeholder so the adapter (which 422s on empty
        # input) never fails the whole batch over one untitled task.
        texts = [_candidate_text(c) or "(제목 없음)" for c in pool]
        try:
            query_embed = provider.embed_query(query_text)
            candidate_embeds = provider.embed_passages(texts)
            if len(candidate_embeds) != len(texts):
                raise RuntimeError(
                    f"Expected {len(texts)} embeddings, got {len(candidate_embeds)}"
                )
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
