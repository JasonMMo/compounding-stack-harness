-- =============================================================================
-- hanbang-rag / 00_extensions.sql
-- Extensions required before schema creation.
-- Idempotent: IF NOT EXISTS on all statements.
-- =============================================================================

-- pgvector: vector(768) column + HNSW/IVFFlat index support
CREATE EXTENSION IF NOT EXISTS vector;

-- pgcrypto: gen_random_uuid() (UUID v4 PK generation)
--           also provides crypt() / gen_salt() for bcrypt in 04_hanbang_rag_user.sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- pg_bigm (optional): Korean substring FTS acceleration.
--   retrieve.py probes pg_extension at runtime; absent = graceful fallback to
--   simple tsquery path. Do NOT error if not installed.
-- CREATE EXTENSION IF NOT EXISTS pg_bigm;  -- uncomment if pg_bigm is available
