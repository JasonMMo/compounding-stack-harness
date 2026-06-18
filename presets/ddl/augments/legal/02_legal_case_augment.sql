-- =============================================================================
-- legal-rag-mvp / 02_legal_case_augment.sql
-- Augments existing legal_case table (Growth-24 baseline).
-- ADD ONLY — no DROP, no ALTER TYPE; open-closed migration.
-- =============================================================================

-- Guard: run only if legal_case exists (demo-compat)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_name = 'legal_case'
  ) THEN
    RAISE EXCEPTION 'legal_case table not found — run Growth-24 baseline DDL first';
  END IF;
END $$;

-- ─────────────────────────────────────────────
-- 1. FTS column: pre-computed tsvector (Korean bigram via pg_bigm)
--    Covers: title + summary for intra-case keyword search
-- ─────────────────────────────────────────────
ALTER TABLE legal_case
  ADD COLUMN IF NOT EXISTS fts_vector tsvector
    GENERATED ALWAYS AS (
      to_tsvector('simple',
        coalesce(title, '') || ' ' || coalesce(summary, '')
      )
    ) STORED;

-- GIN index on generated tsvector (supports plainto_tsquery / phraseto_tsquery)
CREATE INDEX IF NOT EXISTS idx_legal_case_fts
  ON legal_case USING GIN (fts_vector);

-- pg_bigm trigram index: enables LIKE '%keyword%' on Korean without full parser
CREATE INDEX IF NOT EXISTS idx_legal_case_title_bigm
  ON legal_case USING GIN (title gin_bigm_ops);

-- ─────────────────────────────────────────────
-- 2. RLS columns: row-ownership for per-attorney isolation
--    (assigned_attorney_id already exists; no new column needed)
--    partner_id: senior attorney can see all cases in their group
-- ─────────────────────────────────────────────
ALTER TABLE legal_case
  ADD COLUMN IF NOT EXISTS partner_id UUID NULL;
-- fk-exempt: partner_id → hr_employee (cross-domain; enforced at application layer)

COMMENT ON COLUMN legal_case.partner_id IS
  'Senior partner who supervises this case. RLS: partners see all cases where partner_id = their id OR assigned_attorney_id = their id.';

-- ─────────────────────────────────────────────
-- 3. RLS: enable + policies
-- ─────────────────────────────────────────────
ALTER TABLE legal_case ENABLE ROW LEVEL SECURITY;

-- app_service bypasses all RLS (ingest, admin, backend service role)
ALTER TABLE legal_case FORCE ROW LEVEL SECURITY;

-- Policy A: attorney sees cases assigned to them
CREATE POLICY "rls_legal_case_attorney_select"
  ON legal_case
  FOR SELECT
  TO app_user
  USING (
    assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
    OR partner_id = current_setting('app.current_user_id', true)::uuid
  );

-- Policy B: attorney can insert cases they are assigned to
CREATE POLICY "rls_legal_case_attorney_insert"
  ON legal_case
  FOR INSERT
  TO app_user
  WITH CHECK (
    assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
  );

-- Policy C: attorney or partner can update their own cases
CREATE POLICY "rls_legal_case_attorney_update"
  ON legal_case
  FOR UPDATE
  TO app_user
  USING (
    assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
    OR partner_id = current_setting('app.current_user_id', true)::uuid
  )
  WITH CHECK (
    assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
    OR partner_id = current_setting('app.current_user_id', true)::uuid
  );

-- No DELETE policy: cases are never deleted (legal audit requirement)

-- ─────────────────────────────────────────────
-- 4. updated_at trigger
-- ─────────────────────────────────────────────
CREATE TRIGGER trg_legal_case_updated_at
  BEFORE UPDATE ON legal_case
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- Rollback (save as 02_legal_case_augment_rollback.sql before applying)
-- ─────────────────────────────────────────────
-- DROP POLICY IF EXISTS "rls_legal_case_attorney_select" ON legal_case;
-- DROP POLICY IF EXISTS "rls_legal_case_attorney_insert" ON legal_case;
-- DROP POLICY IF EXISTS "rls_legal_case_attorney_update" ON legal_case;
-- ALTER TABLE legal_case DISABLE ROW LEVEL SECURITY;
-- DROP INDEX IF EXISTS idx_legal_case_fts;
-- DROP INDEX IF EXISTS idx_legal_case_title_bigm;
-- ALTER TABLE legal_case DROP COLUMN IF EXISTS fts_vector;
-- ALTER TABLE legal_case DROP COLUMN IF EXISTS partner_id;
-- DROP TRIGGER IF EXISTS trg_legal_case_updated_at ON legal_case;
