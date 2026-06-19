-- =============================================================================
-- legal-rag-mvp / 01_extensions.sql
-- Prerequisites: Postgres extensions for FTS + vector search
-- Run once per database (before all other DDL)
-- =============================================================================

-- pgvector: vector similarity search (embedding storage + HNSW/IVFFlat index)
CREATE EXTENSION IF NOT EXISTS vector;

-- pg_bigm: Korean bigram FTS. Guarded — preview tier (pgvector-only image) lacks
-- this extension; there the system degrades to plainto_tsquery (option A). Production
-- self-host with pg_bigm installed gets full substring/bigram quality automatically.
-- Alternative: pgroonga (comment out pg_bigm block and uncomment pgroonga block if preferred)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'pg_bigm') THEN
    CREATE EXTENSION IF NOT EXISTS pg_bigm;
    RAISE NOTICE 'pg_bigm enabled: Korean bigram FTS active';
  ELSE
    RAISE NOTICE 'pg_bigm unavailable: Korean substring search degraded to plainto_tsquery (option A / preview tier)';
  END IF;
END $$;

-- uuid generation (Postgres 13+ built-in; explicit for older versions)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- uncomment if gen_random_uuid() unavailable

-- =============================================================================
-- Shared trigger function for updated_at (create once per DB)
-- =============================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Application role definitions
-- Backend service runs as 'app_service' (bypasses RLS via BYPASSRLS attribute
-- OR by SET SESSION AUTHORIZATION — engineer chooses pattern).
-- Individual attorneys/partners authenticate as 'app_user' (subject to RLS).
-- =============================================================================

-- Roles (idempotent: skip if already exist in your auth system)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_service') THEN
    CREATE ROLE app_service NOLOGIN BYPASSRLS;  -- RLS 우회: ingest pipeline 전용, 개별 변호사 연결은 절대 이 롤 금지
  ELSE
    ALTER ROLE app_service BYPASSRLS;           -- 기존 롤: idempotent 패치
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
    CREATE ROLE app_user NOLOGIN;
  END IF;
END $$;
