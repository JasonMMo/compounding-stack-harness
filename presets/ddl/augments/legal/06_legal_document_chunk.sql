-- =============================================================================
-- legal-rag-mvp / 06_legal_document_chunk.sql
-- NEW TABLE: legal_document_chunk
-- Purpose: chunk-level embeddings for RAG ingest (precedents + case documents).
-- Each chunk is a ~500-token window of a parent document or precedent full_text.
-- Citation anchor: chunk.source_id (FK to legal_precedent.id OR legal_case_document.id)
--   + source_type discriminator. Answer citations resolve to a concrete DB PK —
--   hallucination is impossible if answer only uses chunk.id as reference.
-- =============================================================================

CREATE TABLE IF NOT EXISTS legal_document_chunk (
  -- ─── Identity ─────────────────────────────────────────────────────────────
  id              UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- ─── Source anchor (citation integrity) ───────────────────────────────────
  -- source_type discriminates between 'precedent' and 'case_document'
  source_type     VARCHAR(32) NOT NULL
    CHECK (source_type IN ('precedent', 'case_document')),

  -- source_id → legal_precedent.id  when source_type = 'precedent'
  -- source_id → legal_case_document.id  when source_type = 'case_document'
  -- FK is logically enforced at application layer (polymorphic)
  source_id       UUID        NOT NULL,

  -- case_id: denormalized for RLS performance (avoids double-join for case_document chunks)
  -- NULL for precedent chunks (precedents are firm-wide)
  case_id         UUID        NULL
    CONSTRAINT fk_legal_document_chunk_case
      REFERENCES legal_case(id) ON DELETE CASCADE,

  -- ─── Chunk position ───────────────────────────────────────────────────────
  chunk_index     INTEGER     NOT NULL,  -- 0-based position within source document
  chunk_text      TEXT        NOT NULL,  -- raw chunk content (500 tokens target)
  token_count     INTEGER     NULL,      -- actual token count (populated by ingest)

  -- ─── Vector embedding ─────────────────────────────────────────────────────
  -- Dimension = 768 (embeddinggemma / nomic-embed-text)
  -- NULL until ingest sidecar processes the chunk
  embedding       vector(768) NULL,

  -- ─── Ingest metadata ──────────────────────────────────────────────────────
  embedded_at     TIMESTAMPTZ NULL,
  model_version   VARCHAR(64) NULL,  -- e.g. 'nomic-embed-text-v1.5' — for re-embed on model change

  -- ─── Unique constraint: one chunk per (source, index) ─────────────────────
  CONSTRAINT uq_legal_document_chunk_source_idx UNIQUE (source_id, source_type, chunk_index)
);

COMMENT ON TABLE legal_document_chunk IS
  'RAG ingest unit. Each row = one ~500-token window of a precedent or case document. '
  'chunk.id is the citation anchor: RAG answers must reference this id, which resolves '
  'back to source_id (precedent or case_document) for hallucination-free attribution.';

COMMENT ON COLUMN legal_document_chunk.source_id IS
  'FK to legal_precedent.id (source_type=precedent) or legal_case_document.id (source_type=case_document). '
  'Enforced at application layer (polymorphic).';

COMMENT ON COLUMN legal_document_chunk.embedding IS
  'Vector embedding of chunk_text. Dim=768 (embeddinggemma local sidecar). '
  'Populated by engineer-implemented ingest pipeline — schema only defines storage.';

-- ─────────────────────────────────────────────
-- Indexes
-- ─────────────────────────────────────────────

-- Lookup chunks by source document (batch retrieval for ingest re-run)
CREATE INDEX IF NOT EXISTS idx_legal_chunk_source
  ON legal_document_chunk (source_type, source_id);

-- Lookup chunks by case (RLS scoped case_document search)
CREATE INDEX IF NOT EXISTS idx_legal_chunk_case
  ON legal_document_chunk (case_id);

-- Vector ANN: HNSW (cosine) for semantic search
-- Requires embedding IS NOT NULL — partial index skips unembedded rows
CREATE INDEX IF NOT EXISTS idx_legal_chunk_hnsw
  ON legal_document_chunk USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE embedding IS NOT NULL;

-- FTS on chunk_text (fallback keyword search within chunks)
CREATE INDEX IF NOT EXISTS idx_legal_chunk_fts
  ON legal_document_chunk USING GIN (
    to_tsvector('simple', chunk_text)
  );

-- ─────────────────────────────────────────────
-- RLS: chunk visibility mirrors source document
--   precedent chunks: all app_users (firm-wide knowledge)
--   case_document chunks: only attorneys on the parent case
-- ─────────────────────────────────────────────
ALTER TABLE legal_document_chunk ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_document_chunk FORCE ROW LEVEL SECURITY;

-- Rule 1: precedent chunks are readable by all authenticated users
CREATE POLICY "rls_legal_chunk_precedent_select"
  ON legal_document_chunk
  FOR SELECT
  TO app_user
  USING (source_type = 'precedent');

-- Rule 2: case_document chunks follow parent case attorney ownership
CREATE POLICY "rls_legal_chunk_case_doc_select"
  ON legal_document_chunk
  FOR SELECT
  TO app_user
  USING (
    source_type = 'case_document'
    AND EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_document_chunk.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

-- INSERT/UPDATE/DELETE: app_service only (ingest pipeline)
-- No app_user write policy = denied by default

-- ─────────────────────────────────────────────
-- updated_at trigger
-- ─────────────────────────────────────────────
CREATE TRIGGER trg_legal_document_chunk_updated_at
  BEFORE UPDATE ON legal_document_chunk
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- Rollback
-- ─────────────────────────────────────────────
-- DROP TABLE IF EXISTS legal_document_chunk;
