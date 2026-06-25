-- =============================================================================
-- legal-rag-mvp / 12_legal_time_entry.sql
-- NEW TABLE: legal_time_entry — 타임시트 (Growth K3 killer-app)
--
-- 소형 로펌 killer-app: 변호사별 업무 시간 기록 → 청구 합계 집계.
-- K1(기일 가디언)·K2(이해충돌) 에 이은 세 번째 killer-app.
-- catalog entity: time-entry. business-system 데모(InMemory)는 이 DDL 없이도 동작하나
-- 실제 self-host 제품(postgres)을 위해 복리 축적(axis-2 ddl).
--
-- ADD ONLY — open-closed migration. idempotent (IF NOT EXISTS / CREATE OR REPLACE).
-- RLS: case-scoped — 기일은 소속 사건의 담당 변호사/파트너에게만 보임 (11_legal_case_deadline 패턴).
-- honest: "자동 청구서 생성·법적 효력" 주장 금지 — "기록 기반 청구 합계 집계"만.
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
-- 1. legal_time_entry 테이블 생성
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS legal_time_entry (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  case_id       UUID        NOT NULL
    REFERENCES legal_case(id) ON DELETE CASCADE,
  employee_id   UUID        NOT NULL,               -- fk-exempt: hr_employee (cross-domain; app-layer)
  work_date     DATE        NOT NULL,
  minutes       INTEGER     NOT NULL
    CHECK (minutes > 0),
  description   TEXT        NOT NULL,
  billable      BOOLEAN     NOT NULL DEFAULT true,
  hourly_rate   INTEGER     NOT NULL
    CHECK (hourly_rate > 0),                        -- KRW/시간 스냅샷
  amount        INTEGER     NOT NULL
    CHECK (amount >= 0),                            -- KRW = round(minutes/60*hourly_rate) 스냅샷
  status        TEXT        NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'submitted', 'billed'))
);

COMMENT ON TABLE  legal_time_entry              IS '변호사별 업무 시간 기록. K3 타임시트·빌링 killer-app. honest: 기록 기반 집계만, 법적 청구 효력 보장 아님.';
COMMENT ON COLUMN legal_time_entry.minutes      IS '업무 시간(분). float 금지 — 정수 분 단위.';
COMMENT ON COLUMN legal_time_entry.hourly_rate  IS 'KRW/시간 스냅샷. 기록 시점 단가 고정.';
COMMENT ON COLUMN legal_time_entry.amount       IS 'KRW = round(minutes/60*hourly_rate). 저장 시 계산, 이후 불변.';
COMMENT ON COLUMN legal_time_entry.status       IS 'draft(초안) | submitted(제출) | billed(청구됨).';

-- ─────────────────────────────────────────────
-- 2. updated_at 자동 갱신 트리거 (set_updated_at() 은 baseline DDL 에서 생성됨)
-- ─────────────────────────────────────────────
CREATE OR REPLACE TRIGGER trg_legal_time_entry_updated_at
  BEFORE UPDATE ON legal_time_entry
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- 3. 인덱스
-- ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_legal_time_entry_case_id
  ON legal_time_entry (case_id);
CREATE INDEX IF NOT EXISTS idx_legal_time_entry_employee_id
  ON legal_time_entry (employee_id);
CREATE INDEX IF NOT EXISTS idx_legal_time_entry_status
  ON legal_time_entry (status);

-- ─────────────────────────────────────────────
-- 4. RLS: case-scoped — 소속 사건의 담당 변호사/파트너만 (11_legal_case_deadline 패턴)
-- ─────────────────────────────────────────────
ALTER TABLE legal_time_entry ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_time_entry FORCE ROW LEVEL SECURITY;

CREATE POLICY "rls_legal_time_entry_select"
  ON legal_time_entry
  FOR SELECT
  TO app_user
  USING (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_time_entry.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

CREATE POLICY "rls_legal_time_entry_insert"
  ON legal_time_entry
  FOR INSERT
  TO app_user
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_time_entry.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

CREATE POLICY "rls_legal_time_entry_update"
  ON legal_time_entry
  FOR UPDATE
  TO app_user
  USING (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_time_entry.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_time_entry.case_id
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
-- DROP POLICY  IF EXISTS "rls_legal_time_entry_select" ON legal_time_entry;
-- DROP POLICY  IF EXISTS "rls_legal_time_entry_insert" ON legal_time_entry;
-- DROP POLICY  IF EXISTS "rls_legal_time_entry_update" ON legal_time_entry;
-- ALTER TABLE  legal_time_entry DISABLE ROW LEVEL SECURITY;
-- DROP TRIGGER IF EXISTS trg_legal_time_entry_updated_at ON legal_time_entry;
-- DROP INDEX   IF EXISTS idx_legal_time_entry_case_id;
-- DROP INDEX   IF EXISTS idx_legal_time_entry_employee_id;
-- DROP INDEX   IF EXISTS idx_legal_time_entry_status;
-- DROP TABLE   IF EXISTS legal_time_entry;
