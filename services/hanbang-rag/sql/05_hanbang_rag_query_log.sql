-- =============================================================================
-- hanbang-rag / 05_hanbang_rag_query_log.sql
-- TABLE: hanbang_rag_query_log
-- Purpose: 검색 쿼리 감사 로그 + citation 계약 앵커.
--
-- citation.py _INSERT_QUERY_LOG_SQL 계약 (1:1 컬럼 매핑 필수):
--   INSERT INTO hanbang_rag_query_log
--     (user_id, query_text, query_embedding,
--      retrieved_chunk_ids, citations_summary, status, latency_ms)
--   VALUES (%s::uuid, %s, %s::vector, %s, %s, 'completed', %s)
--   RETURNING id::text
--
-- RLS 결정 (CTO 확정):
--   데모는 단일 계정 → per-user 격리 실익 적음.
--   단순 open-read 대신 user_id 기준 SELECT 격리를 선택:
--     이유: ① legal 패턴 재사용으로 버그 리스크 최소화
--           ② Phase 2 멀티계정 전환 시 RLS 재구현 불필요
--           ③ 데모 단일계정이라도 정책이 있으면 RLS 검증이 쉬워짐
--   INSERT: app_user WITH CHECK (user_id = current_setting(...)) — citation.py 호출자
--   SELECT: app_user USING (user_id = current_setting(...))
--   UPDATE/DELETE: 미부여 (append-only 감사 로그)
--
-- legal_rag_query_log 대비 제거된 컬럼:
--   - attorney_id → user_id 로 대체 (generic UUID)
--   - case_id (한방은 case 개념 없음)
--   - answer_text / model_id / tokens_used (Lite tier — 생성 없음)
--   - error_message (status='completed' 고정 INSERT, 에러 시 미삽입)
-- =============================================================================

CREATE TABLE IF NOT EXISTS hanbang_rag_query_log (
  -- ── Identity ───────────────────────────────────────────────────────────────
  id              UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- ── 요청자 ─────────────────────────────────────────────────────────────────
  -- user_id: citation.py INSERT col[0] (%s::uuid) — 계약 컬럼명
  -- FK to hanbang_rag_user.id (SET NULL on delete: 계정 삭제 시 로그 보존)
  user_id         UUID        NOT NULL
    CONSTRAINT fk_hanbang_query_log_user
      REFERENCES hanbang_rag_user(id) ON DELETE SET NULL,

  -- ── 질의 ───────────────────────────────────────────────────────────────────
  -- query_text: citation.py INSERT col[1] — 계약 컬럼명
  query_text      TEXT        NOT NULL,

  -- query_embedding: citation.py INSERT col[2] (%s::vector) — 계약 컬럼명
  -- vector(768): 쿼리 분석 / dedup 용. NULL 허용(embed 실패 시 로그 보존).
  query_embedding vector(768) NULL,

  -- ── Citation 계약 앵커 ─────────────────────────────────────────────────────
  -- retrieved_chunk_ids: citation.py INSERT col[3] — 계약 컬럼명
  -- JSON array of hanbang_rag_document_chunk.id (UUID strings)
  -- 감사: 답변이 이 목록 밖의 청크를 참조하면 hallucination
  retrieved_chunk_ids TEXT    NULL,

  -- citations_summary: citation.py INSERT col[4] — 계약 컬럼명
  -- JSON list of resolved Citation dicts (notice_number/ministry/issued_date 포함)
  citations_summary   TEXT    NULL,

  -- ── 상태 / 성능 ────────────────────────────────────────────────────────────
  -- status: citation.py INSERT 에서 'completed' 고정 삽입
  status          VARCHAR(32) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'completed', 'error')),

  -- latency_ms: citation.py INSERT col[5] — 계약 컬럼명
  latency_ms      INTEGER     NULL
);

COMMENT ON TABLE hanbang_rag_query_log IS
  'Append-only 감사 로그. citation.py log_query() 가 매 검색마다 INSERT. '
  'retrieved_chunk_ids = citation contract anchor: 답변은 이 chunk id 목록만 참조 가능. '
  'legal_rag_query_log 대비 case_id / answer_text / model_id 제거 (Lite tier).';

COMMENT ON COLUMN hanbang_rag_query_log.user_id IS
  'citation.py INSERT col[0]. RLS current_setting(app.current_user_id) 와 대조.';
COMMENT ON COLUMN hanbang_rag_query_log.retrieved_chunk_ids IS
  'citation.py: JSON array of hanbang_rag_document_chunk.id UUID strings. '
  'Hallucination 감사 앵커 — 답변이 이 목록 밖 chunk 를 인용하면 계약 위반.';
COMMENT ON COLUMN hanbang_rag_query_log.status IS
  'citation.py INSERT 에서 ''completed'' 고정. pending 초기값은 비동기 확장 예비.';

-- ── 인덱스 ────────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_hanbang_query_log_user
  ON hanbang_rag_query_log (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_hanbang_query_log_status
  ON hanbang_rag_query_log (status);

-- ── RLS ───────────────────────────────────────────────────────────────────────
ALTER TABLE hanbang_rag_query_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE hanbang_rag_query_log FORCE ROW LEVEL SECURITY;

-- SELECT: 자신의 쿼리 로그만
CREATE POLICY "rls_hanbang_query_log_select"
  ON hanbang_rag_query_log
  FOR SELECT
  TO app_user
  USING (
    user_id = current_setting('app.current_user_id', true)::uuid
  );

-- INSERT: citation.py log_query() 호출 (rls_session 활성 상태)
--   WITH CHECK: 삽입 행의 user_id 가 세션 user_id 와 일치해야 함
CREATE POLICY "rls_hanbang_query_log_insert"
  ON hanbang_rag_query_log
  FOR INSERT
  TO app_user
  WITH CHECK (
    user_id = current_setting('app.current_user_id', true)::uuid
  );

-- UPDATE/DELETE: 미부여 (append-only 감사 로그)

-- ── updated_at 트리거 ─────────────────────────────────────────────────────────
CREATE TRIGGER trg_hanbang_query_log_updated_at
  BEFORE UPDATE ON hanbang_rag_query_log
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── Rollback ──────────────────────────────────────────────────────────────────
-- DROP TABLE IF EXISTS hanbang_rag_query_log CASCADE;
