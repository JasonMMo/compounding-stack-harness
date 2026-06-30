-- =============================================================================
-- hanbang-rag / 06_grants.sql
-- GRANT: 최소 권한 원칙 (legal-rag 09_grants.sql 패턴 계승).
--
-- 역할 분리:
--   app_service (BYPASSRLS, pool login): 모든 테이블 소유 — 별도 GRANT 불필요
--   app_user    (RLS enforced, NOLOGIN): 아래 명시된 권한만
--
-- 적용 순서: 01~05 모든 테이블 생성 완료 후.
-- Idempotent: GRANT 는 재실행 안전.
-- =============================================================================

GRANT USAGE ON SCHEMA public TO app_user;

-- ── hanbang_rag_notice ────────────────────────────────────────────────────────
-- 공개 참조데이터: 전 인증 사용자 SELECT 허용.
-- INSERT/UPDATE: app_service(ingest pipeline) 전용 — app_user 미부여.
GRANT SELECT ON hanbang_rag_notice TO app_user;

-- ── hanbang_rag_document_chunk ────────────────────────────────────────────────
-- retrieve.py _FTS_OR_SQL / _ANN_SQL / _FETCH_CHUNKS_SQL 가 SELECT.
-- INSERT/UPDATE: app_service(ingest pipeline) 전용 — app_user 미부여.
GRANT SELECT ON hanbang_rag_document_chunk TO app_user;

-- ── hanbang_rag_user ──────────────────────────────────────────────────────────
-- app_service 전용 (login 엔드포인트 BYPASSRLS 경로).
-- app_user 에게 SELECT 미부여: password_hash 노출 차단.
-- (legal 의 legal_attorney 패턴 동일)

-- ── hanbang_rag_query_log ─────────────────────────────────────────────────────
-- citation.py log_query(): rls_session 내 app_user 로 INSERT.
-- SELECT: RLS policy "rls_hanbang_query_log_select" 가 user_id 격리.
-- UPDATE/DELETE: 미부여 (append-only).
GRANT SELECT, INSERT ON hanbang_rag_query_log TO app_user;

-- No sequence grants: PKs are client-supplied gen_random_uuid().

-- =============================================================================
-- 검증 쿼리 (적용 후 실행)
-- =============================================================================
-- SELECT grantee, table_name, privilege_type
--   FROM information_schema.role_table_grants
--  WHERE grantee = 'app_user'
--  ORDER BY table_name, privilege_type;
