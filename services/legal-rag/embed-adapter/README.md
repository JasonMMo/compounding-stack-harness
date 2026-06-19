# embed-adapter

Thin FastAPI shim that translates the legal-rag embed contract into
HuggingFace TEI (Text Embeddings Inference) native calls.

## Why this exists

`embed_client.py` in the legal-rag app expects a specific JSON shape.
TEI's native API returns a bare 2-D float array. This adapter bridges
the gap without modifying either side.

## Contract (matches embed_client.py byte-for-byte)

| Method | Path | Request body | Response body |
|--------|------|--------------|---------------|
| POST | `/embed` | `{"text": str}` | `{"embedding": [float x 768], "model": str}` |
| POST | `/embed/batch` | `{"texts": [str, ...]}` | `{"embeddings": [[float x 768], ...], "model": str}` |
| GET | `/health` | — | `{"status": "ok"}` (HTTP 200) |

## Asymmetric Prefix — Caller-Split Invariant

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

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TEI_BASE_URL` | `http://tei:80` | Base URL of the TEI container |
| `EMBED_MODEL_NAME` | `intfloat/multilingual-e5-base` | Model version string returned in `"model"` field |
| `EMBED_QUERY_PREFIX` | `query: ` | Prefix for `POST /embed` (single, query head) |
| `EMBED_PASSAGE_PREFIX` | `passage: ` | Prefix for `POST /embed/batch` (passage head) |

## Backend: TEI native API

TEI exposes `POST /embed`:
- Request: `{"inputs": str | [str]}`
- Response: `[[float, ...], ...]` (bare 2-D array)

This adapter prefixes each string with the appropriate asymmetric prefix
(`EMBED_QUERY_PREFIX` for `/embed`, `EMBED_PASSAGE_PREFIX` for `/embed/batch`),
calls TEI, validates each vector is exactly 768-dim, and wraps the result in the
contract's object shape.

## Model

`intfloat/multilingual-e5-base` — 768-dim, supports Korean + English.
TEI downloads the model from HuggingFace Hub on first startup (cached in
`tei-data` volume). Subsequent restarts use the local cache.

## Running locally

```bash
TEI_BASE_URL=http://localhost:8081 uvicorn app:app --port 8080
```

## Tests

```bash
cd services/legal-rag/embed-adapter
pip install -r requirements.txt
pytest tests/ -v
```
