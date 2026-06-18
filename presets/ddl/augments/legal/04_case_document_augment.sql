-- =============================================================================
-- legal-rag-mvp / 04_case_document_augment.sql
-- Augments existing legal_case_document table (Growth-24 baseline).
-- Adds: content_text column (extracted text), tsvector FTS, RLS (case-scoped).
-- ADD ONLY — open-closed.
-- NOTE: actual vector embedding lives in legal_document_chunk (file 05).
--       case_document is the document-level anchor; chunk is the ingest unit.
-- =============================================================================

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_name = 'legal_case_document'
  ) THEN
    RAISE EXCEPTION 'legal_case_document table not found — run Growth-24 baseline DDL first';
  END IF;
END $$;

-- ─────────────────────────────────────────────
-- 1. Extracted text: plain text pulled from PDF/DOCX by ingest pipeline
--    NULL until ingest processes the file.
-- ─────────────────────────────────────────────
ALTER TABLE legal_case_document
  ADD COLUMN IF NOT EXISTS content_text TEXT NULL;

COMMENT ON COLUMN legal_case_document.content_text IS
  'Full extracted text of the document (from PDF/DOCX). Populated by ingest pipeline. NULL = not yet processed.';

-- ─────────────────────────────────────────────
-- 2. FTS over title + content_text (document-level keyword search)
-- ─────────────────────────────────────────────
ALTER TABLE legal_case_document
  ADD COLUMN IF NOT EXISTS fts_vector tsvector
    GENERATED ALWAYS AS (
      to_tsvector('simple',
        coalesce(title, '') || ' ' || coalesce(content_text, '') || ' ' || coalesce(notes, '')
      )
    ) STORED;

CREATE INDEX IF NOT EXISTS idx_legal_case_document_fts
  ON legal_case_document USING GIN (fts_vector);

-- ─────────────────────────────────────────────
-- 3. Ingest tracking columns
-- ─────────────────────────────────────────────
ALTER TABLE legal_case_document
  ADD COLUMN IF NOT EXISTS ingest_status VARCHAR(32) NULL
    CHECK (ingest_status IN ('pending', 'processing', 'done', 'error'));

ALTER TABLE legal_case_document
  ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMPTZ NULL;

COMMENT ON COLUMN legal_case_document.ingest_status IS
  'Text extraction + chunk embedding pipeline status. NULL = never submitted.';

-- ─────────────────────────────────────────────
-- 4. RLS: a document is visible only to attorneys on the parent case
--    Relies on legal_case RLS being consistent with case_id FK.
--    Implementation: subquery join back to legal_case.
-- ─────────────────────────────────────────────
ALTER TABLE legal_case_document ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_case_document FORCE ROW LEVEL SECURITY;

CREATE POLICY "rls_legal_case_document_select"
  ON legal_case_document
  FOR SELECT
  TO app_user
  USING (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_document.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

CREATE POLICY "rls_legal_case_document_insert"
  ON legal_case_document
  FOR INSERT
  TO app_user
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_document.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

-- No UPDATE / DELETE policy for app_user: documents are append-only (legal audit)

-- ─────────────────────────────────────────────
-- 5. updated_at trigger
-- ─────────────────────────────────────────────
CREATE TRIGGER trg_legal_case_document_updated_at
  BEFORE UPDATE ON legal_case_document
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- Rollback
-- ─────────────────────────────────────────────
-- DROP POLICY IF EXISTS "rls_legal_case_document_select" ON legal_case_document;
-- DROP POLICY IF EXISTS "rls_legal_case_document_insert" ON legal_case_document;
-- ALTER TABLE legal_case_document DISABLE ROW LEVEL SECURITY;
-- DROP INDEX IF EXISTS idx_legal_case_document_fts;
-- ALTER TABLE legal_case_document DROP COLUMN IF EXISTS fts_vector;
-- ALTER TABLE legal_case_document DROP COLUMN IF EXISTS content_text;
-- ALTER TABLE legal_case_document DROP COLUMN IF EXISTS ingest_status;
-- ALTER TABLE legal_case_document DROP COLUMN IF EXISTS ingested_at;
-- DROP TRIGGER IF EXISTS trg_legal_case_document_updated_at ON legal_case_document;
