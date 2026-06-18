# legal-rag — Legal RAG MVP Service

FastAPI-based hybrid search (FTS + vector ANN + RRF) over legal precedents
and case documents. **Lite tier: returns ranked chunks + citations only.**
LLM answer generation is NOT implemented — gated to Pro tier.

## Architecture

```
Client → POST /search
           │
           ├─ embed_client.py  ← local embeddinggemma sidecar (HTTP)
           │                      NO cloud API. missing sidecar = 503.
           │
           ├─ retrieve.py      ← Stage 1: FTS (plainto_tsquery)
           │                      Stage 2: ANN (pgvector HNSW cosine)
           │                      Stage 3: RRF(k=60) merge
           │
           ├─ citation.py      ← chunk.id → legal_precedent / legal_case_document
           │                      append to legal_rag_query_log
           │
           └─ Response: ranked chunks + citation metadata
                        (no answer_text — hallucination-free guarantee)
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `LEGAL_RAG_DB_DSN` | YES | — | psycopg3 DSN for `app_service` role |
| `LEGAL_RAG_EMBED_URL` | YES | — | Base URL of local embeddinggemma sidecar |
| `LEGAL_RAG_EMBED_MODEL_VERSION` | no | `embeddinggemma-768` | Recorded in `model_version` column |
| `LEGAL_RAG_CHUNK_TOKENS` | no | `500` | Target tokens per chunk |
| `LEGAL_RAG_CHUNK_OVERLAP` | no | `50` | Overlap tokens between chunks |
| `LEGAL_RAG_RRF_K` | no | `60` | RRF constant k |
| `LEGAL_RAG_TOP_K` | no | `10` | Search results returned |
| `LEGAL_RAG_FTS_LIMIT` | no | `100` | FTS candidate limit before RRF |
| `LEGAL_RAG_ANN_LIMIT` | no | `100` | ANN candidate limit before RRF |
| `LEGAL_RAG_POOL_MIN` | no | `2` | DB pool min connections |
| `LEGAL_RAG_POOL_MAX` | no | `10` | DB pool max connections |

## NO CLOUD FALLBACK

The embedding sidecar (`LEGAL_RAG_EMBED_URL`) must be a locally-running
embeddinggemma or compatible server (768-dim output). Cloud embedding APIs
(OpenAI, Cohere, etc.) are intentionally NOT supported as fallback.

Reason: this service's value proposition requires:
1. API cost = 0 (no per-token charges for embeddings)
2. Data leakage = 0 (legal documents stay on-premise)

Using a cloud embedding API would break both guarantees. Sidecar unreachable
returns HTTP 503 with an explicit error message.

## Sidecar Interface Contract

The local embeddinggemma sidecar must implement:

**Single embed**
```
POST /embed
Content-Type: application/json
{"text": "<string>"}

200 OK
{"embedding": [<float x 768>], "model": "<version-string>"}
```

**Batch embed**
```
POST /embed/batch
Content-Type: application/json
{"texts": ["<string>", ...]}

200 OK
{"embeddings": [[<float x 768>], ...], "model": "<version-string>"}
```

**Health check**
```
GET /health
200 OK  (any body)
```

## Running

```bash
# From repo root
cd services/legal-rag

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LEGAL_RAG_DB_DSN="postgresql://app_service:pw@localhost:5432/legaldb"
export LEGAL_RAG_EMBED_URL="http://localhost:8080"

# Start service
uvicorn api:app --host 0.0.0.0 --port 8000

# API docs (dev only)
open http://localhost:8000/docs
```

## DB Setup

Apply augment SQLs in order (requires existing Growth-24 baseline tables):
```sql
\i presets/ddl/augments/legal/01_extensions.sql
\i presets/ddl/augments/legal/02_legal_case_augment.sql
\i presets/ddl/augments/legal/03_precedent_augment.sql
\i presets/ddl/augments/legal/04_case_document_augment.sql
\i presets/ddl/augments/legal/05_case_party_rls.sql
\i presets/ddl/augments/legal/06_legal_document_chunk.sql
\i presets/ddl/augments/legal/07_rag_query_log.sql
```

## RLS Role Model

- `app_service` role: BYPASSRLS. Used by ingest pipeline for chunk writes.
- `app_user` role: RLS enforced. Every query transaction requires
  `SET LOCAL app.current_user_id = '<attorney_uuid>'` (handled by `db.rls_session()`).
  Missing session → 0 rows returned (fail-safe, not an error).

## Running Tests

```bash
cd services/legal-rag
pytest tests/ -v
# No DB or sidecar required for unit tests.
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness: DB pool + sidecar reachability |
| `POST` | `/ingest` | Ingest file → chunks → embeddings → DB |
| `POST` | `/search` | Hybrid search, return chunks + citations |

See `/docs` (FastAPI OpenAPI UI) for request/response schemas.

## Search Pipeline

1. **FTS stage** — `plainto_tsquery('simple', query)` on `legal_document_chunk.chunk_text`
   via GIN index. Korean subword matching assisted by `pg_bigm` trigram index.
   Returns up to `LEGAL_RAG_FTS_LIMIT` chunk IDs ranked by `ts_rank_cd`.

2. **ANN stage** — `embedding <=> query_vec` cosine distance on HNSW index
   (`idx_legal_chunk_hnsw`). Partial index covers only rows where
   `embedding IS NOT NULL`. Returns up to `LEGAL_RAG_ANN_LIMIT` chunk IDs.

3. **RRF merge** — Reciprocal Rank Fusion with k=60:
   `score(id) = 1/(k + fts_rank) + 1/(k + ann_rank)` (0 if not in a list).
   Top-K scored IDs fetched from DB in one round-trip.

4. **Citation resolution** — each chunk's `source_id` resolved to
   `legal_precedent` (case_number, court, decision_date) or
   `legal_case_document` (title, document_type). Appended to `legal_rag_query_log`.

## Citation Integrity

Every search result is anchored to `legal_document_chunk.id`. The API response
contains only chunk IDs that exist in the DB and pass RLS. No free-text
citation is ever generated — hallucination is structurally impossible
at the Lite tier (no LLM in the response path).
