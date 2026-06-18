-- =============================================================================
-- legal-rag-mvp / 05_case_party_rls.sql
-- Augments existing legal_case_party table (Growth-24 baseline).
-- PII isolation: case_party rows visible only to the owning case's attorneys.
-- No structural column additions — RLS-only augment.
-- ADD ONLY — open-closed.
-- =============================================================================

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_name = 'legal_case_party'
  ) THEN
    RAISE EXCEPTION 'legal_case_party table not found — run Growth-24 baseline DDL first';
  END IF;
END $$;

-- ─────────────────────────────────────────────
-- RLS: PII containment — party data (name, contact_id) locked to case attorneys
-- ─────────────────────────────────────────────
ALTER TABLE legal_case_party ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_case_party FORCE ROW LEVEL SECURITY;

CREATE POLICY "rls_legal_case_party_select"
  ON legal_case_party
  FOR SELECT
  TO app_user
  USING (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_party.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

CREATE POLICY "rls_legal_case_party_insert"
  ON legal_case_party
  FOR INSERT
  TO app_user
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_party.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

CREATE POLICY "rls_legal_case_party_update"
  ON legal_case_party
  FOR UPDATE
  TO app_user
  USING (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_party.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_party.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

-- No DELETE policy for app_user

-- ─────────────────────────────────────────────
-- updated_at trigger
-- ─────────────────────────────────────────────
CREATE TRIGGER trg_legal_case_party_updated_at
  BEFORE UPDATE ON legal_case_party
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- Rollback
-- ─────────────────────────────────────────────
-- DROP POLICY IF EXISTS "rls_legal_case_party_select" ON legal_case_party;
-- DROP POLICY IF EXISTS "rls_legal_case_party_insert" ON legal_case_party;
-- DROP POLICY IF EXISTS "rls_legal_case_party_update" ON legal_case_party;
-- ALTER TABLE legal_case_party DISABLE ROW LEVEL SECURITY;
-- DROP TRIGGER IF EXISTS trg_legal_case_party_updated_at ON legal_case_party;
