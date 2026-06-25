-- =============================================================================
-- legal-rag-mvp / 13_legal_invoice.sql
-- NEW TABLE: legal_invoice — 청구서 (Growth K3 killer-app)
--
-- 소형 로펌 killer-app: 사건별 타임시트 합계 → 청구서 발행.
-- K3 타임시트·빌링의 청구서 엔티티. catalog entity: case-invoice (키 충돌 방지 — finance.invoice 불가침).
-- business-system 데모(InMemory)는 이 DDL 없이도 동작하나
-- 실제 self-host 제품(postgres)을 위해 복리 축적(axis-2 ddl).
--
-- ADD ONLY — open-closed migration. idempotent (IF NOT EXISTS / CREATE OR REPLACE).
-- RLS: case-scoped — 소속 사건의 담당 변호사/파트너에게만 보임 (11_legal_case_deadline 패턴).
-- honest: "법적 효력 청구서" 주장 금지 — "기록 기반 청구 합계 집계"만.
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
-- 1. legal_invoice 테이블 생성
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS legal_invoice (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  case_id       UUID        NOT NULL
    REFERENCES legal_case(id) ON DELETE CASCADE,
  client_name   TEXT        NOT NULL,               -- 의뢰인 표시명 비정규화 (display snapshot)
  issue_date    DATE        NOT NULL,
  period_start  DATE        NULL,
  period_end    DATE        NULL,
  subtotal      INTEGER     NOT NULL DEFAULT 0
    CHECK (subtotal >= 0),                          -- KRW
  tax           INTEGER     NOT NULL DEFAULT 0
    CHECK (tax >= 0),                               -- KRW 부가세 10%
  total         INTEGER     NOT NULL DEFAULT 0
    CHECK (total >= 0),                             -- KRW = subtotal + tax
  status        TEXT        NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'issued', 'paid'))
);

COMMENT ON TABLE  legal_invoice             IS '사건별 청구서. K3 타임시트·빌링 killer-app. honest: 기록 기반 집계만, 법적 청구 효력 보장 아님.';
COMMENT ON COLUMN legal_invoice.client_name IS '의뢰인 표시명 비정규화 스냅샷. 발행 시점 고정.';
COMMENT ON COLUMN legal_invoice.subtotal    IS 'KRW 공급가액. time_entry.amount 합산.';
COMMENT ON COLUMN legal_invoice.tax         IS 'KRW 부가세 10%. round(subtotal * 0.1).';
COMMENT ON COLUMN legal_invoice.total       IS 'KRW 합계 = subtotal + tax.';
COMMENT ON COLUMN legal_invoice.status      IS 'draft(초안) | issued(발행) | paid(완납).';

-- ─────────────────────────────────────────────
-- 2. updated_at 자동 갱신 트리거 (set_updated_at() 은 baseline DDL 에서 생성됨)
-- ─────────────────────────────────────────────
CREATE OR REPLACE TRIGGER trg_legal_invoice_updated_at
  BEFORE UPDATE ON legal_invoice
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
-- 3. 인덱스
-- ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_legal_invoice_case_id
  ON legal_invoice (case_id);
CREATE INDEX IF NOT EXISTS idx_legal_invoice_status
  ON legal_invoice (status);

-- ─────────────────────────────────────────────
-- 4. RLS: case-scoped — 소속 사건의 담당 변호사/파트너만 (11_legal_case_deadline 패턴)
-- ─────────────────────────────────────────────
ALTER TABLE legal_invoice ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_invoice FORCE ROW LEVEL SECURITY;

CREATE POLICY "rls_legal_invoice_select"
  ON legal_invoice
  FOR SELECT
  TO app_user
  USING (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_invoice.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

CREATE POLICY "rls_legal_invoice_insert"
  ON legal_invoice
  FOR INSERT
  TO app_user
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_invoice.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  );

CREATE POLICY "rls_legal_invoice_update"
  ON legal_invoice
  FOR UPDATE
  TO app_user
  USING (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_invoice.case_id
        AND (
          lc.assigned_attorney_id = current_setting('app.current_user_id', true)::uuid
          OR lc.partner_id        = current_setting('app.current_user_id', true)::uuid
        )
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM legal_case lc
      WHERE lc.id = legal_invoice.case_id
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
-- DROP POLICY  IF EXISTS "rls_legal_invoice_select" ON legal_invoice;
-- DROP POLICY  IF EXISTS "rls_legal_invoice_insert" ON legal_invoice;
-- DROP POLICY  IF EXISTS "rls_legal_invoice_update" ON legal_invoice;
-- ALTER TABLE  legal_invoice DISABLE ROW LEVEL SECURITY;
-- DROP TRIGGER IF EXISTS trg_legal_invoice_updated_at ON legal_invoice;
-- DROP INDEX   IF EXISTS idx_legal_invoice_case_id;
-- DROP INDEX   IF EXISTS idx_legal_invoice_status;
-- DROP TABLE   IF EXISTS legal_invoice;
