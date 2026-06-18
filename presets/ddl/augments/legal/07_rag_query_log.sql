-- =============================================================================
-- legal-rag-mvp / 07_rag_query_log.sql
-- NEW TABLE: legal_rag_query_log
-- Purpose: audit trail of every RAG query + cited chunk IDs.
--   - Provides hallucination audit: answer citations recorded as FK-verifiable chunk ids
--   - Enables QA to trace answer ← chunk ← source (precedent.citation / case_document.id)
--   - Cost tracking: tokens_used column for LLM call metering
-- =============================================================================

CREATE TABLE IF NOT EXISTS legal_rag_query_log (
  id              UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- ─── Who asked ────────────────────────────────────────────────────────────
  attorney_id     UUID        NOT NULL,
  -- fk-exempt: cross-domain → hr_employee; enforced at application layer

  -- ─── Context ──────────────────────────────────────────────────────────────
  -- case_id nullable: query may be against global precedent corpus (no case scope)
  case_id         UUID        NULL
    CONSTRAINT fk_rag_query_log_case
      REFERENCES legal_case(id) ON DELETE SET NULL,

  -- ─── Query ────────────────────────────────────────────────────────────────
  query_text      TEXT        NOT NULL,
  query_embedding vector(768) NULL,   -- optional: store for query analytics / dedup

  -- ─── Retrieved chunks (citation integrity anchor) ─────────────────────────
  -- Array of legal_document_chunk.id values returned by vector search.
  -- Stored as TEXT (JSON array) for dialect neutrality; adapter parses.
  -- The answer MUST only reference chunk_ids present in this list — enforced at app layer.
  retrieved_chunk_ids TEXT     NULL,
  -- Human-readable citation list (denorm): e.g. ["대법원 2020다12345", "사건서류 ID=..."]
  citations_summary   TEXT     NULL,

  -- ─── Answer ───────────────────────────────────────────────────────────────
  answer_text     TEXT        NULL,   -- LLM-generated answer (nullable until async completes)
  model_id        VARCHAR(64) NULL,   -- e.g. 'gemma-3-27b-it' or 'gpt-4o-mini'
  tokens_used     INTEGER     NULL,   -- total tokens (prompt + completion) for cost tracking
  latency_ms      INTEGER     NULL,

  -- ─── Status ───────────────────────────────────────────────────────────────
  status          VARCHAR(32) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'completed', 'error')),
  error_message   TEXT        NULL
);

COMMENT ON TABLE legal_rag_query_log IS
  'Append-only audit log of every RAG query. retrieved_chunk_ids forms the citation '
  'contract: the answer layer must only reference chunks from this list. '
  'Enables post-hoc hallucination audit by tracing chunk_id → source document.';

-- ─────────────────────────────────────────────
-- Indexes
-- ─────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_rag_query_log_attorney
  ON legal_rag_query_log (attorney_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_rag_query_log_case
  ON legal_rag_query_log (case_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_rag_query_log_status
  ON legal_rag_query_log (status);

-- ─────────────────────────────────────────────
-- RLS: attorney sees only their own query history
-- ─────────────────────────────────────────────
ALTER TABLE legal_rag_query_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_rag_query_log FORCE ROW LEVEL SECURITY;

CREATE POLICY "rls_rag_query_log_select"
  ON legal_rag_query_log
  FOR SELECT
  TO app_user
  USING (
    attorney_id = current_setting('app.current_user_id', true)::uuid
  );

CREATE POLICY "rls_rag_query_log_insert"
  ON legal_rag_query_log
  FOR INSERT
  TO app_user
  WITH CHECK (
    attorney_id = current_setting('app.current_user_id', true)::uuid
  );

-- No UPDATE / DELETE for app_user (append-only audit log)

-- ─────────────────────────────────────────────
-- updated_at trigger
-- ─────────────────────────────────────────────
CREATE TRIGGER trg_rag_query_log_updated_at
  BEFORE UPDATE ON legal_rag_query_log
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- Rollback
-- ─────────────────────────────────────────────
-- DROP TABLE IF EXISTS legal_rag_query_log;
