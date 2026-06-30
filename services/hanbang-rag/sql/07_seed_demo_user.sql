-- =============================================================================
-- hanbang-rag / 07_seed_demo_user.sql
-- SEED: 데모 계정 1건 (hanbang_rag_user).
--
-- TODO(D1→engineer/CISO):
--   password_hash 플레이스홀더를 실제 bcrypt 해시로 교체 후 적용.
--   생성 방법 (psql 또는 Python):
--     psql:   SELECT crypt('YOUR_DEMO_PASSWORD', gen_salt('bf', 12));
--     Python: import bcrypt; bcrypt.hashpw(b'YOUR_DEMO_PASSWORD', bcrypt.gensalt(12))
--   생성된 해시를 아래 password_hash 값으로 교체.
--   절대 평문 비밀번호를 이 파일에 커밋하지 마라.
--
-- 데모 사용자 UUID는 고정값 사용:
--   JWT mint 시 sub = 이 id. Coolify 환경변수 HANBANG_RAG_DEMO_USER_ID 와 일치 필요.
--   UUID는 임의 고정값 — 운영 환경에서 재생성 권장.
-- =============================================================================

INSERT INTO hanbang_rag_user (id, email, password_hash, role)
VALUES (
  'a1b2c3d4-e5f6-7890-abcd-ef1234567890',   -- 고정 데모 UUID (JWT sub)
  'demo@hanbang-rag.local',
  -- TODO: 아래 플레이스홀더를 실제 bcrypt 해시로 교체 (CISO 게이트 전 필수)
  '$2b$12$PLACEHOLDER_REPLACE_WITH_REAL_BCRYPT_HASH_BEFORE_DEPLOY',
  'admin'                                     -- 데모: ingest + search 전권
)
ON CONFLICT (email) DO NOTHING;

-- =============================================================================
-- 적용 후 확인
-- =============================================================================
-- SELECT id, email, role, created_at FROM hanbang_rag_user;
--
-- JWT mint 테스트 (Python):
--   from services.hanbang_rag.auth import mint_token
--   token = mint_token('a1b2c3d4-e5f6-7890-abcd-ef1234567890', secret='DEV_SECRET')
--   print(token)
