-- =============================================================================
-- hanbang-rag / 02_hanbang_rag_notice.sql
-- TABLE: hanbang_rag_notice
-- Purpose: 한방 급여 고시 원문 저장. 공개 참조데이터 — 전 사용자 동일 열람, PII 없음.
--
-- Citation contract (citation.py _RESOLVE_NOTICE_SQL):
--   JOIN ON hanbang_rag_notice.id = hanbang_rag_document_chunk.source_id
--   SELECT notice_number, ministry, issued_date::text, LEFT(summary, 300)
--   All four column names are contract — must match exactly.
--
-- RLS 결정 (CTO 확정):
--   공개 참조데이터이므로 행 단위 격리 불필요. RLS 비활성화.
--   쓰기(INSERT/UPDATE)는 table-level grant 로만 제한:
--     app_service (BYPASSRLS): ingest pipeline — 허용
--     app_user: 06_grants.sql에서 SELECT만 — INSERT/UPDATE 미부여로 차단
--   Phase 2 공개 랜딩 read-only 테넌트 전환 시 CISO 게이트 후 재검토.
-- =============================================================================

CREATE TABLE IF NOT EXISTS hanbang_rag_notice (
  -- ── Identity ───────────────────────────────────────────────────────────────
  id              UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- ── 고시 식별 ──────────────────────────────────────────────────────────────
  -- notice_number: citation.py _RESOLVE_NOTICE_SQL col[0] — 계약 컬럼명
  notice_number   TEXT        NOT NULL,   -- e.g. "보건복지부고시 제2023-123호"

  -- ministry: citation.py _RESOLVE_NOTICE_SQL col[1] — 계약 컬럼명
  ministry        TEXT        NOT NULL,   -- e.g. "보건복지부"

  -- issued_date: citation.py _RESOLVE_NOTICE_SQL col[2] (issued_date::text) — 계약 컬럼명
  issued_date     DATE        NOT NULL,   -- 발령일자

  -- notice_type: 자유 텍스트 (legal의 case_type CHECK 제거됨 — 한방 고시 유형 다양)
  notice_type     TEXT        NULL,       -- e.g. "급여기준", "고시개정" (선택)

  -- ── 내용 ───────────────────────────────────────────────────────────────────
  -- summary: citation.py _RESOLVE_NOTICE_SQL col[3] (LEFT 300) — 계약 컬럼명
  summary         TEXT        NULL,       -- 요약 (citation 표시용, 300자 이내 권장)

  -- full_text: ingest.py가 청크 분할 대상으로 사용하는 원문 전문
  full_text       TEXT        NULL,       -- 고시 원문 전체 (ingest 후 채움)

  -- ── 중복 방지 ──────────────────────────────────────────────────────────────
  CONSTRAINT uq_hanbang_notice_number UNIQUE (notice_number)
);

COMMENT ON TABLE hanbang_rag_notice IS
  '한방 급여 고시 원문. 공개 참조데이터(RLS 없음). '
  'citation.py _RESOLVE_NOTICE_SQL 이 JOIN 하는 테이블: '
  'notice_number / ministry / issued_date / summary 컬럼명은 계약이다.';

COMMENT ON COLUMN hanbang_rag_notice.notice_number IS
  'citation.py _RESOLVE_NOTICE_SQL col[0]. UNIQUE 제약으로 중복 ingest 방지.';
COMMENT ON COLUMN hanbang_rag_notice.issued_date IS
  'citation.py _RESOLVE_NOTICE_SQL col[2]: issued_date::text 로 캐스트. DATE 타입.';
COMMENT ON COLUMN hanbang_rag_notice.summary IS
  'citation.py _RESOLVE_NOTICE_SQL col[3]: LEFT(summary, 300). 300자 초과 저장 가능, 쿼리에서 잘린다.';
COMMENT ON COLUMN hanbang_rag_notice.notice_type IS
  'legal legal_precedent.case_type CHECK 제거됨. 한방 고시 유형은 자유 텍스트.';

-- ── 인덱스 ────────────────────────────────────────────────────────────────────
-- 고시번호 조회 (UNIQUE 인덱스 겸용)
CREATE INDEX IF NOT EXISTS idx_hanbang_notice_number
  ON hanbang_rag_notice (notice_number);

-- 발령일자 범위 조회 (최신 고시 우선 정렬용)
CREATE INDEX IF NOT EXISTS idx_hanbang_notice_issued_date
  ON hanbang_rag_notice (issued_date DESC);

-- ── updated_at 트리거 ─────────────────────────────────────────────────────────
CREATE TRIGGER trg_hanbang_rag_notice_updated_at
  BEFORE UPDATE ON hanbang_rag_notice
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── Rollback ──────────────────────────────────────────────────────────────────
-- DROP TABLE IF EXISTS hanbang_rag_notice CASCADE;
