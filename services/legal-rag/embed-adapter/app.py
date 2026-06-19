"""
embed-adapter/app.py — Thin FastAPI shim between legal-rag and HuggingFace TEI.

CONTRACT (from embed_client.py — must satisfy BYTE-FOR-BYTE):
  POST /embed        body: {"text": str}
                     resp: {"embedding": [float x 768], "model": str}
  POST /embed/batch  body: {"texts": [str, ...]}
                     resp: {"embeddings": [[float x 768], ...], "model": str}
  GET  /health       resp: 200 OK

BACKEND: HuggingFace Text Embeddings Inference (TEI)
  TEI native POST /embed:
    request body: {"inputs": str | [str]}
    response:     [[float, ...], ...]   (bare 2-D array, one row per input)

ASYMMETRIC PREFIX INVARIANT:
  intfloat/multilingual-e5-base is trained with asymmetric prefixes:
    - search queries → "query: <text>"    (query projection head)
    - document passages → "passage: <text>"  (passage projection head)

  The HTTP endpoint itself encodes this distinction, based on a VERIFIED
  one-directional caller-usage split:
    - POST /embed       → called ONLY by api.py (search query path)
                          → prefix "query: " (EMBED_QUERY_PREFIX)
    - POST /embed/batch → called ONLY by ingest.py (passage ingest path)
                          → prefix "passage: " (EMBED_PASSAGE_PREFIX)

  This recovers full asymmetric e5 retrieval quality with zero contract change.

  *** INVARIANT WARNING ***
  If a future caller batches search queries via /embed/batch, or single-embeds
  a passage via /embed, this asymmetry silently breaks — the wrong projection
  head is used and retrieval quality degrades. The caller split (api.py search
  vs ingest.py batch) MUST remain one-directional. Enforce at code-review time.

  Changing either prefix after documents are already ingested will invalidate
  all existing embeddings and require a full re-embed of the entire corpus.

ENV VARS:
  TEI_BASE_URL          — base URL of the TEI container, e.g. http://tei:80
  EMBED_MODEL_NAME      — model version string in response "model" field
                          (default: intfloat/multilingual-e5-base)
  EMBED_QUERY_PREFIX    — prefix for POST /embed (single, query path)
                          (default: "query: ")
  EMBED_PASSAGE_PREFIX  — prefix for POST /embed/batch (batch, passage path)
                          (default: "passage: ")
"""
from __future__ import annotations

import logging
import os
from typing import List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

TEI_BASE_URL: str = os.environ.get("TEI_BASE_URL", "http://tei:80").rstrip("/")
EMBED_MODEL_NAME: str = os.environ.get(
    "EMBED_MODEL_NAME", "intfloat/multilingual-e5-base"
)
EMBED_QUERY_PREFIX: str = os.environ.get("EMBED_QUERY_PREFIX", "query: ")
EMBED_PASSAGE_PREFIX: str = os.environ.get("EMBED_PASSAGE_PREFIX", "passage: ")
EMBED_DIM: int = 768

# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="embed-adapter",
    description="TEI shim exposing the legal-rag embed contract",
    docs_url=None,    # no public docs
    redoc_url=None,
    openapi_url=None,
)

# ── Schemas ───────────────────────────────────────────────────────────────────

class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: List[float]
    model: str


class BatchEmbedRequest(BaseModel):
    texts: List[str]


class BatchEmbedResponse(BaseModel):
    embeddings: List[List[float]]
    model: str


# ── TEI caller ────────────────────────────────────────────────────────────────

def _call_tei(inputs: list[str], prefix: str) -> list[list[float]]:
    """Call TEI POST /embed with the given list of strings.

    Each string is prefixed with `prefix` before dispatch.
    Use EMBED_QUERY_PREFIX for single-embed (query path) and
    EMBED_PASSAGE_PREFIX for batch-embed (passage path).
    Returns a list of float vectors (bare TEI response reshaped).

    Raises HTTPException 502 on TEI error or dimension mismatch.
    """
    prefixed = [f"{prefix}{t}" for t in inputs]
    try:
        resp = httpx.post(
            f"{TEI_BASE_URL}/embed",
            json={"inputs": prefixed},
            timeout=30.0,
        )
        resp.raise_for_status()
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Cannot reach TEI backend at {TEI_BASE_URL}: {exc}",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"TEI returned HTTP {exc.response.status_code}: "
                f"{exc.response.text[:200]}"
            ),
        ) from exc

    raw: list[list[float]] = resp.json()

    # Validate dimensions
    for i, vec in enumerate(raw):
        if len(vec) != EMBED_DIM:
            raise HTTPException(
                status_code=502,
                detail=(
                    f"TEI returned vector of dim {len(vec)} at index {i}; "
                    f"expected {EMBED_DIM}. Wrong model?"
                ),
            )

    return raw


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest) -> EmbedResponse:
    """Single-text embedding.

    Contract: {"text": str} → {"embedding": [float x 768], "model": str}
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=422, detail="text must be non-empty")

    vecs = _call_tei([req.text], prefix=EMBED_QUERY_PREFIX)
    return EmbedResponse(embedding=vecs[0], model=EMBED_MODEL_NAME)


@app.post("/embed/batch", response_model=BatchEmbedResponse)
def embed_batch(req: BatchEmbedRequest) -> BatchEmbedResponse:
    """Batch-text embedding.

    Contract: {"texts": [str, ...]} → {"embeddings": [[float x 768], ...], "model": str}
    """
    if not req.texts:
        raise HTTPException(status_code=422, detail="texts must be non-empty")
    for i, t in enumerate(req.texts):
        if not t or not t.strip():
            raise HTTPException(
                status_code=422, detail=f"texts[{i}] is empty"
            )

    vecs = _call_tei(req.texts, prefix=EMBED_PASSAGE_PREFIX)

    if len(vecs) != len(req.texts):
        raise HTTPException(
            status_code=502,
            detail=(
                f"TEI returned {len(vecs)} vectors for {len(req.texts)} inputs"
            ),
        )

    return BatchEmbedResponse(embeddings=vecs, model=EMBED_MODEL_NAME)


@app.get("/health")
def health() -> dict:
    """Health probe — returns 200 if adapter is up."""
    return {"status": "ok"}
