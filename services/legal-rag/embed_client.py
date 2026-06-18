"""
embed_client.py — HTTP client for local embeddinggemma sidecar.

CONTRACT:
  - Sidecar base URL: env LEGAL_RAG_EMBED_URL (e.g. http://localhost:8080)
  - Single embed:  POST /embed         body: {"text": str}
                   response: {"embedding": [float x 768], "model": str}
  - Batch embed:   POST /embed/batch   body: {"texts": [str, ...]}
                   response: {"embeddings": [[float x 768], ...], "model": str}

No cloud fallback. Sidecar not reachable → raises EmbedSidecarUnavailable.
This is intentional: cloud API usage breaks the "API비0 + 데이터유출0" guarantee.
"""
from __future__ import annotations

import logging
from typing import Sequence

logger = logging.getLogger(__name__)

EMBED_DIM = 768


class EmbedSidecarUnavailable(RuntimeError):
    """Raised when the local embedding sidecar cannot be reached."""


class EmbedDimensionError(ValueError):
    """Raised when sidecar returns a vector of unexpected dimension."""


class EmbedClient:
    """Thin HTTP wrapper around the local embeddinggemma sidecar.

    Lazy-imports httpx so the module is importable without httpx installed
    (unit tests that don't exercise HTTP paths still work).
    """

    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    # ── Internal ──────────────────────────────────────────────────────────────

    def _post(self, path: str, payload: dict) -> dict:
        try:
            import httpx  # lazy import — avoids hard dep for pure-unit tests
        except ImportError as exc:
            raise ImportError(
                "httpx is required for embed_client. "
                "Install it via: pip install httpx"
            ) from exc

        url = f"{self._base_url}{path}"
        try:
            resp = httpx.post(url, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError as exc:
            raise EmbedSidecarUnavailable(
                f"Cannot reach embeddinggemma sidecar at {self._base_url}. "
                "Ensure the sidecar container is running. "
                "Cloud API fallback is intentionally disabled."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise EmbedSidecarUnavailable(
                f"Embedding sidecar returned HTTP {exc.response.status_code}: "
                f"{exc.response.text[:200]}"
            ) from exc
        except Exception as exc:
            raise EmbedSidecarUnavailable(
                f"Unexpected error calling embedding sidecar: {exc}"
            ) from exc

    @staticmethod
    def _validate_vector(vec: list[float], context: str = "") -> list[float]:
        if len(vec) != EMBED_DIM:
            raise EmbedDimensionError(
                f"Expected embedding dim={EMBED_DIM}, got {len(vec)}"
                + (f" ({context})" if context else "")
            )
        return vec

    # ── Public API ────────────────────────────────────────────────────────────

    def embed(self, text: str) -> list[float]:
        """Embed a single text string.

        Returns:
            list[float] of length 768.

        Raises:
            EmbedSidecarUnavailable: sidecar not reachable.
            EmbedDimensionError: sidecar returned wrong dimension.
        """
        if not text or not text.strip():
            raise ValueError("embed() called with empty text.")

        data = self._post("/embed", {"text": text})
        vec = data.get("embedding")
        if not isinstance(vec, list):
            raise EmbedSidecarUnavailable(
                f"Sidecar response missing 'embedding' field: {data}"
            )
        return self._validate_vector(vec, context="single embed")

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed a batch of texts in one sidecar call.

        Args:
            texts: Non-empty sequence of strings. Empty strings raise ValueError.

        Returns:
            list of 768-dim vectors, same order as input.

        Raises:
            EmbedSidecarUnavailable: sidecar not reachable.
            EmbedDimensionError: any returned vector has wrong dimension.
        """
        texts = list(texts)
        if not texts:
            return []
        for i, t in enumerate(texts):
            if not t or not t.strip():
                raise ValueError(f"embed_batch(): empty text at index {i}.")

        data = self._post("/embed/batch", {"texts": texts})
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise EmbedSidecarUnavailable(
                f"Sidecar batch response malformed: expected {len(texts)} embeddings, "
                f"got: {data}"
            )
        return [
            self._validate_vector(vec, context=f"batch index {i}")
            for i, vec in enumerate(embeddings)
        ]

    def health_check(self) -> bool:
        """Return True if sidecar is reachable and healthy.

        Does not raise — used for /health endpoint probe.
        """
        try:
            import httpx

            resp = httpx.get(
                f"{self._base_url}/health", timeout=5.0
            )
            return resp.status_code == 200
        except Exception:
            return False
