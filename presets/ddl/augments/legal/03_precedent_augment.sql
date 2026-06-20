-- =============================================================================
-- legal-rag-mvp / 03_precedent_augment.sql
-- Augments existing legal_precedent table (Growth-24 baseline).
-- Adds: tsvector FTS + pgvector embedding column + RLS (public read, admin write).
-- ADD ONLY — open-closed.
-- =============================================================================

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_name = 'legal_precedent'
  ) THEN
    RAISE EXCEPTION 'legal_precedent table not found — run Growth-24 baseline DDL first';
  END IF;
END $$;

-- ─────────────────────────────────────────────
-- 1. FTS: tsvector over holding + keywords (primary search surface)
-- ─────────────────────────────────────────────
ALTER TABLE legal_precedent
  ADD COLUMN IF NOT EXISTS fts_vector tsvector
    GENERATED ALWAYS AS (
      to_tsvector('simple',
        coalesce(holding, '') || ' ' || coalesce(keywords, '')
      )
    ) STORED;

-- GIN index for tsvector FTS (supports @@ operator with plainto_tsquery)
CREATE INDEX IF NOT EXISTS idx_legal_precedent_fts
  ON legal_precedent USING GIN (fts_vector);

-- pg_bigm index on holding for Korean substring search.
-- Only created when pg_bigm is actually installed (see 01_extensions.sql guard).
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_bigm') THEN
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_legal_precedent_holding_bigm ON legal_precedent USING GIN (holding gin_bigm_ops)';
  END IF;
END $$;

-- ─────────────────────────────────────────────
-- 2. pgvector: semantic embedding of holding text
--    Dimension = 768 (intfloat/multilingual-e5-base output dim).
--    Engineer fills this column via ingest pipeline — NULL until embedded.
--    HNSW index: better recall + faster build than IVFFlat for < 1M rows.
-- ─────────────────────────────────────────────
ALTER TABLE legal_precedent
  ADD COLUMN IF NOT EXISTS holding_embedding vector(768) NULL;

COMMENT ON COLUMN legal_precedent.holding_embedding IS
  'Semantic embedding of holding text. Populated by ingest sidecar (multilingual-e5-base local). NULL = not yet embedded. Dim=768.';

-- HNSW index: approximate nearest neighbor (cosine distance)
-- m=16, ef_construction=64 are conservative defaults; tune upward for larger corpus
CREATE INDEX IF NOT EXISTS idx_legal_precedent_hnsw
  ON legal_precedent USING hnsw (holding_embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- ─────────────────────────────────────────────
-- 3. Embedding metadata: track ingest status without extra table
-- ─────────────────────────────────────────────
ALTER TABLE legal_precedent
  ADD COLUMN IF NOT EXISTS embedded_at TIMESTAMPTZ NULL;

COMMENT ON COLUMN legal_precedent.embedded_at IS
  'Timestamp when holding_embedding was last populated. NULL = pending ingest.';

-- ─────────────────────────────────────────────
-- 4. RLS: precedents are firm-wide knowledge (all attorneys read)
--    Write is restricted to app_service (ingest pipeline + admin)
-- ─────────────────────────────────────────────
ALTER TABLE legal_precedent ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_precedent FORCE ROW LEVEL SECURITY;

-- All authenticated app_users can read any precedent
CREATE POLICY "rls_legal_precedent_user_select"
  ON legal_precedent
  FOR SELECT
  TO app_user
  USING (true);

-- Only app_service can insert/update/delete precedent rows
-- (No app_user INSERT/UPDATE/DELETE policy = denied by default)

-- ─────────────────────────────────────────────
-- 5. updated_at trigger
-- ─────────────────────────────────────────────
CREATE TRIGGER trg_legal_precedent_updated_at
  BEFORE UPDATE ON legal_precedent
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- Rollback
-- ─────────────────────────────────────────────
-- DROP POLICY IF EXISTS "rls_legal_precedent_user_select" ON legal_precedent;
-- ALTER TABLE legal_precedent DISABLE ROW LEVEL SECURITY;
-- DROP INDEX IF EXISTS idx_legal_precedent_hnsw;
-- DROP INDEX IF EXISTS idx_legal_precedent_fts;
-- DROP INDEX IF EXISTS idx_legal_precedent_holding_bigm;
-- ALTER TABLE legal_precedent DROP COLUMN IF EXISTS holding_embedding;
-- ALTER TABLE legal_precedent DROP COLUMN IF EXISTS embedded_at;
-- ALTER TABLE legal_precedent DROP COLUMN IF EXISTS fts_vector;
-- DROP TRIGGER IF EXISTS trg_legal_precedent_updated_at ON legal_precedent;
