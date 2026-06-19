# embed-adapter

FastAPI shim that exposes the legal-rag embed contract via local
sentence-transformers inference.  The model is baked into the Docker image at
build time and runs fully offline at runtime.

## Why this exists

`embed_client.py` in the legal-rag app expects a specific JSON shape.
sentence-transformers returns numpy arrays.  This adapter bridges the gap
without modifying either side, and applies the asymmetric e5 prefixes that
neither the app nor the DB layer should know about.

## Contract (matches embed_client.py byte-for-byte)

| Method | Path | Request body | Response body |
|--------|------|--------------|---------------|
| POST | `/embed` | `{"text": str}` | `{"embedding": [float x 768], "model": str}` |
| POST | `/embed/batch` | `{"texts": [str, ...]}` | `{"embeddings": [[float x 768], ...], "model": str}` |
| GET | `/health` | — | `{"status": "ok"}` (HTTP 200) |

## Asymmetric Prefix — Caller-Split Invariant (G-87)

`intfloat/multilingual-e5-base` is an asymmetric model with two projection heads:
- **Search queries** — prefix `"query: <text>"` (query head)
- **Document passages** — prefix `"passage: <text>"` (passage head)

This adapter uses **proper asymmetric prefixes** because the HTTP endpoint
itself encodes the query/passage distinction, based on a verified
one-directional caller-usage split:

| Endpoint | Caller | Prefix applied |
|----------|--------|----------------|
| `POST /embed` (single) | `api.py` search path only | `EMBED_QUERY_PREFIX` = `"query: "` |
| `POST /embed/batch` | `ingest.py` passage path only | `EMBED_PASSAGE_PREFIX` = `"passage: "` |

This recovers full asymmetric e5 retrieval quality with zero contract change.

**Invariant warning:** If a future caller batches search queries via `/embed/batch`,
or single-embeds a passage via `/embed`, the wrong projection head is used and
retrieval quality degrades silently. The caller split (api.py search vs ingest.py
batch) **must remain one-directional** — enforce at code-review time.

**Changing either prefix after documents are already ingested invalidates all
existing embeddings and requires a full re-embed of the entire corpus.**

## Backend: local sentence-transformers, model baked in, offline at runtime

- Library: `sentence-transformers>=3.0.0`
- Model: `intfloat/multilingual-e5-base` (768-dim, Korean + English)
- `normalize_embeddings=True` — cosine-consistent vectors, compatible with pgvector `<=>`
- Model is downloaded into `/app/.hfcache` **at Docker build time** via a `RUN python -c "..."` layer.
- At runtime `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` prevent any outbound HF network calls.
- The model is loaded synchronously in the FastAPI lifespan startup hook.
  `/health` returning 200 implies the model singleton is fully loaded and ready.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_MODEL_ID` | `intfloat/multilingual-e5-base` | HF model ID to load (must match baked cache) |
| `EMBED_MODEL_NAME` | `intfloat/multilingual-e5-base` | Model version string returned in `"model"` field |
| `EMBED_QUERY_PREFIX` | `query: ` | Prefix for `POST /embed` (single, query head) |
| `EMBED_PASSAGE_PREFIX` | `passage: ` | Prefix for `POST /embed/batch` (passage head) |

## Image size / RAM

- Base python:3.11-slim + torch CPU + sentence-transformers + model weights: **~1.5 GB image**.
- RAM at runtime: ~400–500 MB (model in CPU RAM, no GPU).

## Running locally (without Docker)

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
uvicorn app:app --port 8080
```

## Tests

```bash
cd services/legal-rag/embed-adapter
pip install -r requirements.txt
pytest tests/ -v
```

Tests use `monkeypatch` on `app._encode` — no real model inference required.
