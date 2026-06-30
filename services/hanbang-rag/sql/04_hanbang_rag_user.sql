-- =============================================================================
-- hanbang-rag / 04_hanbang_rag_user.sql
-- TABLE: hanbang_rag_user
-- Purpose: 데모 로그인 계정. auth.py 는 JWT-only (DB 직접 조회 없음).
--          api.py /auth/login 이 email/password → bcrypt 검증 → JWT mint 에 사용.
--
-- auth.py 계약:
--   auth.py 는 DB 를 직접 조회하지 않는다 (HS256 JWT decode 전담).
--   login 엔드포인트(api.py)가 app_service 커넥션으로 이 테이블을 SELECT 한다:
--     SELECT id, password_hash, role
--     FROM hanbang_rag_user
--     WHERE email = %s
--   반환값: id → JWT sub claim, role → 응용 권한 제어.
--
-- RLS 결정:
--   app_service(BYPASSRLS) 만 접근. app_user 에게 SELECT 미부여 (06_grants.sql).
--   password_hash 노출 방지 — legal 의 legal_attorney 패턴 동일.
--   RLS 활성화하지 않음(app_user 가 이 테이블에 접근할 경로 없음으로 충분).
-- =============================================================================

CREATE TABLE IF NOT EXISTS hanbang_rag_user (
  -- ── Identity ───────────────────────────────────────────────────────────────
  id              UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- ── 인증 ───────────────────────────────────────────────────────────────────
  -- email: api.py login 에서 WHERE email = %s 조회 — 유일성 필수
  email           TEXT        NOT NULL,
  CONSTRAINT uq_hanbang_user_email UNIQUE (email),

  -- password_hash: bcrypt 60자 ($2b$...). pgcrypto crypt() 검증.
  --   api.py: crypt(input_pw, password_hash) = password_hash
  password_hash   TEXT        NOT NULL,

  -- role: JWT payload 에 포함하지 않음(서버측 검증용).
  --   'admin'  — ingest + search 전권
  --   'viewer' — search 전용 (데모 계정 기본값)
  role            VARCHAR(32) NOT NULL DEFAULT 'viewer'
    CHECK (role IN ('admin', 'viewer'))
);

COMMENT ON TABLE hanbang_rag_user IS
  '데모 로그인 계정. app_service 전용 — app_user grant 없음. '
  'auth.py 는 JWT-only; api.py /auth/login 만 이 테이블을 SELECT 한다. '
  'password_hash = bcrypt (pgcrypto crypt 검증).';

COMMENT ON COLUMN hanbang_rag_user.password_hash IS
  'bcrypt 해시. 예: crypt(''plaintext'', gen_salt(''bf'', 12)). '
  '07_seed_demo_user.sql 에 플레이스홀더 — 실해시는 engineer/CISO 가 채운다.';
COMMENT ON COLUMN hanbang_rag_user.role IS
  'admin: ingest + search. viewer: search only. 데모 계정 기본값 = viewer.';

-- ── 인덱스 ────────────────────────────────────────────────────────────────────
-- UNIQUE 인덱스가 email 조회 커버 (별도 인덱스 불필요)

-- ── updated_at 트리거 ─────────────────────────────────────────────────────────
CREATE TRIGGER trg_hanbang_user_updated_at
  BEFORE UPDATE ON hanbang_rag_user
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── Rollback ──────────────────────────────────────────────────────────────────
-- DROP TABLE IF EXISTS hanbang_rag_user CASCADE;
