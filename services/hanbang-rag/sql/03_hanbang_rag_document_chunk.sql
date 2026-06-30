-- =============================================================================
-- hanbang-rag / 03_hanbang_rag_document_chunk.sql
-- TABLE: hanbang_rag_document_chunk
-- Purpose: 청크 단위 임베딩 저장. legal_document_chunk 포크 — 한방 단순화.
--
-- case_id 제거 결정 (DBA/CTO D1 확정):
--   legal_document_chunk 에는 case_id(FK→legal_case) 컬럼이 있었으나,
--   한방 고시는 notice 단일 도메인(case 개념 없음). ingest.py 는 case_id=None 을
--   항상 삽입 중이므로 DDL에서 제거함.
--   ★ ENGINEER 의존성 (D1→D2 이전 필수 패치):
--     1. ingest.py _UPSERT_CHUNK_SQL:
--        - 컬럼 목록에서 "case_id" 제거
--        - VALUES 에서 대응 "%s"(=None) 제거
--        - executemany row tuple 에서 None 값 제거
--     2. retrieve.py _FETCH_CHUNKS_SQL:
--        - "case_id::text," 줄 제거
--        - RetrievedChunk(case_id=row[3], ...) 인덱스 재정렬 (row[3]→chunk_index 등)
--
-- source_type CHECK:
--   'notice' 단일 값 (legal 의 'precedent'|'case_document' 이중 분기 제거).
--
-- RLS 결정 (CTO 확정):
--   공개 참조데이터 + 멀티테넌트 경계 없음 → RLS 비활성화.
--   app_user 는 06_grants.sql 에서 SELECT 만 부여, INSERT/UPDATE 없음.
--   Phase 2 공개 랜딩 read-only 시 CISO 게이트 후 재검토.
--
-- SQL 계약 (retrieve.py / ingest.py / citation.py):
--   _UPSERT_CHUNK_SQL     : source_type, source_id, chunk_index, chunk_text,
--                           token_count, embedding, embedded_at, model_version
--   _DELETE_ORPHAN_CHUNK_SQL: WHERE source_id / source_type / chunk_index >=
--   _FTS_OR_SQL           : to_tsvector('simple', chunk_text) @@ to_tsquery('simple', ...)
--   _ANN_SQL              : embedding <=> %s::vector
--   _FETCH_CHUNKS_SQL     : id, source_type, source_id, chunk_index,
--                           chunk_text, token_count
--   _RESOLVE_NOTICE_SQL   : JOIN ON hanbang_rag_notice.id = source_id
--                           WHERE source_type = 'notice'
--   ON CONFLICT           : (source_id, source_type, chunk_index)
-- =============================================================================

CREATE TABLE IF NOT EXISTS hanbang_rag_document_chunk (
  -- ── Identity ───────────────────────────────────────────────────────────────
  id              UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- ── Source anchor (citation integrity) ────────────────────────────────────
  -- source_type: 한방은 'notice' 단일. CHECK 로 강제.
  source_type     VARCHAR(32) NOT NULL
    CHECK (source_type IN ('notice')),

  -- source_id → hanbang_rag_notice.id
  -- ingest.py: _CHECK_NOTICE_SQL 로 사전 존재 확인 후 upsert
  source_id       UUID        NOT NULL
    CONSTRAINT fk_hanbang_chunk_notice
      REFERENCES hanbang_rag_notice(id) ON DELETE CASCADE,

  -- case_id: 제거됨 (한방 notice 단일 도메인, legal 잔재).
  --   ENGINEER: ingest.py / retrieve.py 패치 필요 (파일 상단 주석 참조).

  -- ── 청크 위치 ──────────────────────────────────────────────────────────────
  chunk_index     INTEGER     NOT NULL,   -- 0-based 위치

  -- chunk_text: FTS 및 FETCH 의 핵심 컬럼 (retrieve.py _FETCH_CHUNKS_SQL col[4])
  chunk_text      TEXT        NOT NULL,

  -- token_count: 실제 토큰 수 (ingest 가 채움, retrieve.py col[5])
  token_count     INTEGER     NULL,

  -- ── Vector embedding ───────────────────────────────────────────────────────
  -- Dimension = 768 (multilingual-e5-base, retrieve.py 에서 len==768 강제 검증)
  -- NULL until ingest sidecar embeds the chunk
  embedding       vector(768) NULL,

  -- ── Ingest 메타데이터 ────────────────────────────────────────────────────────
  embedded_at     TIMESTAMPTZ NULL,
  model_version   VARCHAR(64) NULL,   -- e.g. 'multilingual-e5-base'

  -- ── 유일 제약: (source, index) 쌍으로 upsert ON CONFLICT ────────────────────
  CONSTRAINT uq_hanbang_chunk_source_idx
    UNIQUE (source_id, source_type, chunk_index)
);

COMMENT ON TABLE hanbang_rag_document_chunk IS
  'RAG ingest 단위. 각 행 = 한방 급여 고시 원문의 ~500 토큰 윈도우. '
  'chunk.id 가 citation anchor: 답변은 이 id 를 참조 → hanbang_rag_notice 역추적. '
  'case_id 제거됨(legal 잔재). source_type 은 notice 단일.';

COMMENT ON COLUMN hanbang_rag_document_chunk.source_id IS
  'FK → hanbang_rag_notice.id. ingest.py _CHECK_NOTICE_SQL 이 사전 검증.';
COMMENT ON COLUMN hanbang_rag_document_chunk.embedding IS
  'vector(768): multilingual-e5-base. retrieve.py 에서 len==768 강제 검증.';
COMMENT ON COLUMN hanbang_rag_document_chunk.chunk_text IS
  'FTS 대상 컬럼. retrieve.py to_tsvector(''simple'', chunk_text) 사용.';

-- ── 인덱스 ────────────────────────────────────────────────────────────────────

-- source 별 청크 조회 (ingest re-run + orphan 삭제 대상 탐색)
CREATE INDEX IF NOT EXISTS idx_hanbang_chunk_source
  ON hanbang_rag_document_chunk (source_type, source_id);

-- ANN: HNSW cosine — retrieve.py _ANN_SQL "embedding <=> %s::vector"
-- partial index: embedding IS NOT NULL (미임베딩 행 제외)
CREATE INDEX IF NOT EXISTS idx_hanbang_chunk_hnsw
  ON hanbang_rag_document_chunk USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE embedding IS NOT NULL;

-- FTS fallback: simple config tsquery (retrieve.py _FTS_OR_SQL)
-- retrieve.py: to_tsvector('simple', chunk_text) @@ to_tsquery('simple', ...)
CREATE INDEX IF NOT EXISTS idx_hanbang_chunk_fts
  ON hanbang_rag_document_chunk USING GIN (
    to_tsvector('simple', chunk_text)
  );

-- pg_bigm 한국어 바이그램 GIN (runtime probe, pg_bigm 설치 시 자동 생성)
-- retrieve.py: pg_extension 조회 후 LIKE 체인 경로로 전환
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_bigm') THEN
    EXECUTE $idx$
      CREATE INDEX IF NOT EXISTS idx_hanbang_chunk_bigm
        ON hanbang_rag_document_chunk USING gin (chunk_text gin_bigm_ops)
    $idx$;
    RAISE NOTICE 'idx_hanbang_chunk_bigm: created (pg_bigm active)';
  ELSE
    RAISE NOTICE 'idx_hanbang_chunk_bigm: skipped (pg_bigm not installed — degraded to simple FTS)';
  END IF;
END $$;

-- ── updated_at 트리거 ─────────────────────────────────────────────────────────
CREATE TRIGGER trg_hanbang_chunk_updated_at
  BEFORE UPDATE ON hanbang_rag_document_chunk
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── Rollback ──────────────────────────────────────────────────────────────────
-- DROP TABLE IF EXISTS hanbang_rag_document_chunk CASCADE;
