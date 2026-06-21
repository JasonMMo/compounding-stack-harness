-- =============================================================================
-- legal-rag-mvp / 09_grants.sql
-- GRANT: minimal table-level privileges for app_user (RLS-enforced attorney path)
-- Purpose: After `SET LOCAL ROLE app_user` (engineer RLS fix), Postgres requires
--   table-level SELECT before RLS policies (02-07) can even evaluate. Without these
--   grants, every attorney-scoped query fails with "permission denied for table".
--   app_service already owns all tables (BYPASSRLS path for ingest + login) and is
--   untouched. Row-level filtering is still enforced by the RLS policies in 02-07;
--   these grants are table-level access only — they do NOT widen what rows app_user
--   can see.
-- Idempotent: GRANT is naturally idempotent (re-running is safe).
-- Apply order: AFTER 08_legal_attorney.sql (all tables must exist first).
-- =============================================================================

GRANT USAGE ON SCHEMA public TO app_user;

-- Read tables touched under rls_session:
--   /cases  : legal_case, legal_case_document
--   /search : legal_document_chunk, legal_precedent, legal_case_document
--   legal_case_party included for completeness / future use; RLS still constrains rows.
GRANT SELECT ON legal_case, legal_case_document, legal_case_party, legal_precedent, legal_document_chunk TO app_user;

-- Write paths (C1 사건 / C2 당사자 / C3 문서첨부): app_user 가 RLS WITH CHECK 정책에
-- 도달하려면 table-level INSERT/UPDATE grant 가 선행돼야 한다 (Postgres 는 RLS 평가 전
-- table privilege 를 먼저 검사). 이 grant 는 "시도 가능" 권한일 뿐, 어느 행을 쓸 수
-- 있는지는 02/04/05 의 RLS WITH CHECK 정책이 계속 강제한다 (행 노출 확대 0).
GRANT INSERT, UPDATE ON legal_case        TO app_user;  -- C1 create_case / update_case
GRANT INSERT, UPDATE ON legal_case_party  TO app_user;  -- C2 create_party / update_party
GRANT INSERT          ON legal_case_document TO app_user;  -- C3 문서 업로드 (append-only: UPDATE/DELETE 정책 없음)

-- /search logs each query as app_user (append-only audit trail).
-- RLS policy in 07_rag_query_log.sql limits SELECT to own rows.
-- UPDATE/DELETE intentionally withheld.
GRANT SELECT, INSERT ON legal_rag_query_log TO app_user;

-- NOTE: legal_attorney is deliberately NOT granted to app_user.
--   Login runs exclusively as app_service (BYPASSRLS). app_user must never
--   be able to read password_hash or any attorney credential row.

-- No sequence grants: all PKs are client-supplied UUIDs (gen_random_uuid()).

-- =============================================================================
-- Verification: run after apply to confirm grants are in effect.
-- =============================================================================
-- SELECT grantee, table_name, privilege_type
--   FROM information_schema.role_table_grants
--  WHERE grantee = 'app_user'
--  ORDER BY table_name;
