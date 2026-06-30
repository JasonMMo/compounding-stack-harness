"""
embed-adapter/app.py — FastAPI shim exposing the legal-rag embed contract via
local sentence-transformers inference (model baked into Docker image, offline at
runtime).

CONTRACT (from embed_client.py — must satisfy BYTE-FOR-BYTE):
  POST /embed        body: {"text": str}
                     resp: {"embedding": [float x 768], "model": str}
  POST /embed/batch  body: {"texts": [str, ...]}
                     resp: {"embeddings": [[float x 768], ...], "model": str}
  GET  /health       resp: 200 OK

BACKEND: local sentence-transformers, model baked into image, offline at runtime.
  Model: intfloat/multilingual-e5-base (768-dim, Korean + English).
  The model is loaded once during FastAPI lifespan/startup and held as a global
  singleton. /health returning 200 implies the model is ready.

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
  EMBED_MODEL_ID        — HuggingFace model ID to load (must match baked cache)
                          (default: intfloat/multilingual-e5-base)
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
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

EMBED_MODEL_ID: str = os.environ.get(
    "EMBED_MODEL_ID", "intfloat/multilingual-e5-base"
)
EMBED_MODEL_NAME: str = os.environ.get(
    "EMBED_MODEL_NAME", "intfloat/multilingual-e5-base"
)
EMBED_QUERY_PREFIX: str = os.environ.get("EMBED_QUERY_PREFIX", "query: ")
EMBED_PASSAGE_PREFIX: str = os.environ.get("EMBED_PASSAGE_PREFIX", "passage: ")
EMBED_DIM: int = 768

# ── Global model singleton ────────────────────────────────────────────────────
# Populated by lifespan startup; None until then.
_model = None  # type: ignore[var-annotated]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Load the sentence-transformers model synchronously before serving."""
    global _model
    logger.info("Loading model %s …", EMBED_MODEL_ID)
    from sentence_transformers import SentenceTransformer  # noqa: PLC0415
    _model = SentenceTransformer(EMBED_MODEL_ID)
    logger.info("Model loaded. embed-adapter ready.")
    yield
    # No teardown needed for a CPU model.


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="embed-adapter",
    description="local sentence-transformers shim exposing the legal-rag embed contract",
    docs_url=None,    # no public docs
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
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


# ── Core encode (injectable for tests) ───────────────────────────────────────

def _encode(prefixed_texts: list[str]) -> list[list[float]]:
    """Encode pre-prefixed texts via the global model singleton.

    Returns a list of float vectors.  Tests monkeypatch this function to avoid
    real model inference.
    """
    if _model is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    embeddings = _model.encode(prefixed_texts, normalize_embeddings=True)
    return [vec.tolist() for vec in embeddings]


# ── Local embed helper ────────────────────────────────────────────────────────

def _embed_local(inputs: list[str], prefix: str) -> list[list[float]]:
    """Apply prefix to each input, encode, validate dim, return vectors.

    Raises HTTPException 502 on dimension mismatch.
    """
    prefixed = [f"{prefix}{t}" for t in inputs]
    raw = _encode(prefixed)

    for i, vec in enumerate(raw):
        if len(vec) != EMBED_DIM:
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Model returned vector of dim {len(vec)} at index {i}; "
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

    vecs = _embed_local([req.text], prefix=EMBED_QUERY_PREFIX)
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

    vecs = _embed_local(req.texts, prefix=EMBED_PASSAGE_PREFIX)

    if len(vecs) != len(req.texts):
        raise HTTPException(
            status_code=502,
            detail=(
                f"Model returned {len(vecs)} vectors for {len(req.texts)} inputs"
            ),
        )

    return BatchEmbedResponse(embeddings=vecs, model=EMBED_MODEL_NAME)


@app.get("/health")
def health() -> dict:
    """Health probe — returns 200 if adapter is up and model is loaded."""
    return {"status": "ok"}
