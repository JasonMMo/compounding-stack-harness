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
