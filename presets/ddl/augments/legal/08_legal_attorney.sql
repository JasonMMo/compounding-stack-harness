-- =============================================================================
-- legal-rag-mvp / 08_legal_attorney.sql
-- NEW TABLE: legal_attorney — 변호사 인증 테이블 (로그인용)
-- Growth-48+: CTO 결정 — 최소 실제 로그인 (email + bcrypt password_hash)
-- ADD ONLY — open-closed migration. idempotent (IF NOT EXISTS / CREATE OR REPLACE).
-- =============================================================================

-- =============================================================================
-- [DBA RLS 설계 결정 — 근거]
--
-- 접근 시나리오:
--   (A) 로그인 엔드포인트: app_service(BYPASSRLS) 가 email로 행 조회 → bcrypt 검증
--       → 성공 시 app.current_user_id := attorney.id 를 세션에 SET LOCAL
--   (B) 세션 중 프로파일 조회: 본인 행만 SELECT 허용 (role / display_name 표시용)
--   (C) 파트너는 감독 관계상 본인 + 자기 소속 어소시에이트 행도 조회 가능
--   (D) INSERT / UPDATE / DELETE: app_service 전용.
--       사용자 자가가입 없음 — 관리자(app_service) 프로비저닝 전용.
--
-- 결론:
--   app_service → BYPASSRLS (전체 접근, 로그인 검증 포함)
--   app_user SELECT → 본인(id = current_user_id) OR 같은 파트너 그룹
--     (partner_id = current_user_id  → 파트너가 소속 어소시에이트 조회)
--     (partner_id = (SELECT partner_id FROM legal_attorney WHERE id = current_user_id)
--      → 같은 파트너 소속 동료 어소시에이트 조회 — 실무상 불필요; 배제)
--   단순화: 본인 행 + 자기가 감독하는 어소시에이트 행 (파트너만) SELECT 허용.
--   app_user INSERT/UPDATE/DELETE: 정책 없음 (app_service 전용).
-- =============================================================================

-- ─────────────────────────────────────────────
-- 1. legal_attorney 테이블 생성
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS legal_attorney (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  email         TEXT        NOT NULL,
  password_hash TEXT        NOT NULL,           -- bcrypt $2b$ hash; min cost 12
  display_name  TEXT        NOT NULL,
  partner_id    UUID        NULL
    REFERENCES legal_attorney(id)               -- self-ref: 감독 파트너 (시니어)
      ON DELETE SET NULL
      DEFERRABLE INITIALLY DEFERRED,            -- circular insert 방지 (파트너 자기 참조 우회)
  role          TEXT        NOT NULL DEFAULT 'attorney'
    CHECK (role IN ('attorney', 'partner')),
  is_active     BOOLEAN     NOT NULL DEFAULT true,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT uq_legal_attorney_email UNIQUE (email)
);

COMMENT ON TABLE  legal_attorney               IS '변호사 계정. 로그인·RLS 세션 발급 전용. 자가가입 없음 — app_service 프로비저닝 전용.';
COMMENT ON COLUMN legal_attorney.password_hash IS 'bcrypt $2b$ cost>=12. 평문 저장 금지.';
COMMENT ON COLUMN legal_attorney.partner_id    IS '자기 참조 FK — 감독 파트너 UUID. 파트너 본인은 NULL.';
COMMENT ON COLUMN legal_attorney.role          IS 'attorney(어소시에이트) | partner(파트너/시니어). CHECK 제약.';

-- ─────────────────────────────────────────────
-- 2. updated_at 자동 갱신 트리거
--    set_updated_at() 함수는 Growth-24 baseline DDL 에서 생성됨.
-- ─────────────────────────────────────────────
CREATE OR REPLACE TRIGGER trg_legal_attorney_updated_at
  BEFORE UPDATE ON legal_attorney
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- 3. 인덱스
-- ─────────────────────────────────────────────
-- 로그인 경로 (email 조회): B-Tree (UNIQUE 이미 인덱스 생성)
-- 파트너별 어소시에이트 조회
CREATE INDEX IF NOT EXISTS idx_legal_attorney_partner_id
  ON legal_attorney (partner_id)
  WHERE partner_id IS NOT NULL;

-- 활성 변호사 필터 (관리 UI, active-only 조회)
CREATE INDEX IF NOT EXISTS idx_legal_attorney_is_active
  ON legal_attorney (is_active);

-- ─────────────────────────────────────────────
-- 4. RLS
-- ─────────────────────────────────────────────
ALTER TABLE legal_attorney ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_attorney FORCE ROW LEVEL SECURITY;

-- 4-A. app_user SELECT: 본인 OR 자기가 감독하는 어소시에이트
--   ① 본인: id = current_user_id
--   ② 파트너가 소속 어소시에이트 조회: partner_id = current_user_id
CREATE POLICY "rls_legal_attorney_select"
  ON legal_attorney
  FOR SELECT
  TO app_user
  USING (
    id            = current_setting('app.current_user_id', true)::uuid
    OR partner_id = current_setting('app.current_user_id', true)::uuid
  );

-- 4-B. INSERT / UPDATE / DELETE: app_user 에게 정책 없음 → 전면 차단
--   app_service 는 BYPASSRLS 이므로 별도 정책 불필요.

-- ─────────────────────────────────────────────
-- 5. FK 정합성 판단 — legal_case.assigned_attorney_id / partner_id
-- ─────────────────────────────────────────────
-- [DBA 결정]
--   legal_case.assigned_attorney_id / partner_id 는 현재 raw UUID (FK 없음).
--   legal_attorney 도입 후 이 컬럼들에 FK를 추가하는 것이 정합적이다.
--   그러나 seed 로드 순서 상 attorneys → cases 순서를 보장해야 FK 위반이 없다.
--   seed/seed_attorneys.sql 이 seed_cases.sql 보다 먼저 실행되는 한
--   아래 ALTER 는 안전하다.
--
--   단, 이 파일은 DDL augment이므로 ALTER를 여기에 포함하면
--   재실행(idempotent) 시 이미 FK가 존재할 경우 오류가 난다.
--   → 별도 IF NOT EXISTS guard 패턴 적용.
-- ─────────────────────────────────────────────

DO $$
BEGIN
  -- assigned_attorney_id FK
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE constraint_name = 'fk_legal_case_assigned_attorney'
      AND table_name = 'legal_case'
  ) THEN
    ALTER TABLE legal_case
      ADD CONSTRAINT fk_legal_case_assigned_attorney
        FOREIGN KEY (assigned_attorney_id)
        REFERENCES legal_attorney(id)
        ON DELETE RESTRICT;
  END IF;

  -- partner_id FK
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE constraint_name = 'fk_legal_case_partner'
      AND table_name = 'legal_case'
  ) THEN
    ALTER TABLE legal_case
      ADD CONSTRAINT fk_legal_case_partner
        FOREIGN KEY (partner_id)
        REFERENCES legal_attorney(id)
        ON DELETE SET NULL;
  END IF;
END $$;

-- ─────────────────────────────────────────────
-- Rollback (manual — run in reverse order)
-- ─────────────────────────────────────────────
-- ALTER TABLE legal_case DROP CONSTRAINT IF EXISTS fk_legal_case_assigned_attorney;
-- ALTER TABLE legal_case DROP CONSTRAINT IF EXISTS fk_legal_case_partner;
-- DROP POLICY  IF EXISTS "rls_legal_attorney_select" ON legal_attorney;
-- ALTER TABLE legal_attorney DISABLE ROW LEVEL SECURITY;
-- DROP TRIGGER IF EXISTS trg_legal_attorney_updated_at ON legal_attorney;
-- DROP INDEX   IF EXISTS idx_legal_attorney_partner_id;
-- DROP INDEX   IF EXISTS idx_legal_attorney_is_active;
-- DROP TABLE   IF EXISTS legal_attorney;
