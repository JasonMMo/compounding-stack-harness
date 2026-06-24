-- =============================================================================
-- legal-rag-mvp / 11_legal_case_deadline.sql
-- NEW TABLE: legal_case_deadline — 기일·기한 가디언 (Growth-127, K1 killer-app)
--
-- 소형 로펌 killer-app: 변호사 최대 리스크인 기일·시효·서면제출 기한 누락을 추적.
-- 로폼(LawForm) 미커버 사건축. self-host·검색형 차별 (wiki: lawform-competitive-analysis).
-- catalog entity: case-deadline. business-system 데모(InMemory)는 이 DDL 없이도 동작하나
-- 실제 self-host 제품(postgres)을 위해 복리 축적(axis-2 ddl).
--
-- ADD ONLY — open-closed migration. idempotent (IF NOT EXISTS / CREATE OR REPLACE).
-- RLS: case-scoped — 기일은 소속 사건의 담당 변호사/파트너에게만 보임 (05_case_party_rls 패턴).
-- =============================================================================

-- Guard: legal_case must exist (parent FK target)
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
-- 1. legal_case_deadline 테이블 생성
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS legal_case_deadline (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  case_id       UUID        NOT NULL
    REFERENCES legal_case(id) ON DELETE CASCADE,
  deadline_type TEXT        NOT NULL
    CHECK (deadline_type IN ('court_date', 'filing', 'statute_of_limitations', 'other')),
  title         TEXT        NOT NULL,
  due_date      DATE        NOT NULL,
  status        TEXT        NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'done', 'missed')),
  assigned_attorney_id UUID NULL,    -- fk-exempt: hr_employee (cross-domain; app-layer)
  notes         TEXT        NULL
);

COMMENT ON TABLE  legal_case_deadline               IS '사건 기일·기한 (court_date/filing/statute_of_limitations). 임박 추적용. honest: "누락 100% 방지" 금지, "임박 알림"만.';
COMMENT ON COLUMN legal_case_deadline.deadline_type IS 'court_date(기일) | filing(서면제출) | statute_of_limitations(시효) | other.';
COMMENT ON COLUMN legal_case_deadline.due_date      IS '기한일. D-7 이내 & status=pending 행을 프론트가 임박 하이라이트.';
COMMENT ON COLUMN legal_case_deadline.status        IS 'pending(대기) | done(완료) | missed(지남). missed 는 회고 기록용.';

-- ─────────────────────────────────────────────
-- 2. updated_at 자동 갱신 트리거 (set_updated_at() 은 baseline DDL 에서 생성됨)
-- ─────────────────────────────────────────────
CREATE OR REPLACE TRIGGER trg_legal_case_deadline_updated_at
  BEFORE UPDATE ON legal_case_deadline
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- 3. 인덱스
-- ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_legal_case_deadline_case_id
  ON legal_case_deadline (case_id);
-- 임박 조회: 대기 상태 + 기한일 정렬 (가장 빈번한 쿼리)
CREATE INDEX IF NOT EXISTS idx_legal_case_deadline_due_pending
  ON legal_case_deadline (due_date)
  WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_legal_case_deadline_status
  ON legal_case_deadline (status);

-- ─────────────────────────────────────────────
-- 4. RLS: case-scoped — 소속 사건의 담당 변호사/파트너만 (05_case_party_rls 패턴)
-- ─────────────────────────────────────────────
ALTER TABLE legal_case_deadline ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_case_deadline FORCE ROW LEVEL SECURITY;

CREATE POLICY "rls_legal_case_deadline_select"
  ON legal_case_deadline
  FOR SELECT
  TO app_user
  USING (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_deadline.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

CREATE POLICY "rls_legal_case_deadline_insert"
  ON legal_case_deadline
  FOR INSERT
  TO app_user
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_deadline.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

CREATE POLICY "rls_legal_case_deadline_update"
  ON legal_case_deadline
  FOR UPDATE
  TO app_user
  USING (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_deadline.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_case_deadline.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

-- No DELETE policy for app_user (audit retention).

-- ─────────────────────────────────────────────
-- Rollback (manual — run in reverse order)
-- ─────────────────────────────────────────────
-- DROP POLICY  IF EXISTS "rls_legal_case_deadline_select" ON legal_case_deadline;
-- DROP POLICY  IF EXISTS "rls_legal_case_deadline_insert" ON legal_case_deadline;
-- DROP POLICY  IF EXISTS "rls_legal_case_deadline_update" ON legal_case_deadline;
-- ALTER TABLE  legal_case_deadline DISABLE ROW LEVEL SECURITY;
-- DROP TRIGGER IF EXISTS trg_legal_case_deadline_updated_at ON legal_case_deadline;
-- DROP INDEX   IF EXISTS idx_legal_case_deadline_case_id;
-- DROP INDEX   IF EXISTS idx_legal_case_deadline_due_pending;
-- DROP INDEX   IF EXISTS idx_legal_case_deadline_status;
-- DROP TABLE   IF EXISTS legal_case_deadline;
