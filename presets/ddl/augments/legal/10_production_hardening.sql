-- =============================================================================
-- legal-rag-mvp / 10_production_hardening.sql
-- PRODUCTION 최소 권한 게이트 (Production Least-Privilege Gate)
--
-- 목적(Purpose):
--   프리뷰 티어는 postgres 슈퍼유저 단축 경로로 동작한다(의도적 허용).
--   이 파일은 법무법인 self-host 프로덕션 배포에서 app_service 롤이
--   테이블 소유자가 아닌 최소 권한 DB 로그인으로 동작하도록 강제한다.
--
--   The preview tier runs as the postgres superuser shortcut (documented,
--   acceptable). This file is the production gate: it ensures app_service
--   operates with only the explicit privileges the ingest/login code requires
--   and no more — even when a separate owner role owns the DDL objects.
--
-- 적용 순서(Apply order): AFTER 09_grants.sql
-- 적용 제외(NOT applied in): deploy/preview/legal-rag.apply-schema.sh
--   → 프리뷰 apply 스크립트는 이 파일을 의도적으로 포함하지 않는다.
--   → Preview apply-schema.sh intentionally excludes this file.
-- 실행 역할(Run as): superuser or the role that owns the schema objects
--   (needs ALTER ROLE and GRANT privilege; not app_service itself).
-- Idempotent: ALTER ROLE and GRANT are both idempotent. Safe to re-run.
-- =============================================================================


-- =============================================================================
-- §1. 방어적 속성 제거 (Defensive attribute strip)
-- =============================================================================
-- app_service 에서 불필요한 슈퍼유저 계열 속성을 제거한다.
-- Strip any elevated attributes that app_service should never hold in production.
--
-- ⚑ BYPASSRLS 는 의도적으로 유지한다 (see below).
--   BYPASSRLS is DELIBERATELY RETAINED — do NOT remove it.
--   이유(Reason):
--     1. ingest pipeline: legal_document_chunk 청크를 '모든' 사건에 걸쳐 기록.
--        RLS 는 사건-변호사 스코프로 행을 제한하므로, ingest 가 RLS 를 통과하면
--        다른 사건의 청크를 INSERT/UPDATE 할 수 없게 된다.
--        Ingest writes chunks across ALL cases; RLS case-attorney scoping would
--        block cross-case INSERT/UPDATE if enforced on app_service.
--     2. login lookup: legal_attorney 테이블은 app_user 에 부여되지 않는다
--        (패스워드 해시 보호). app_service 가 BYPASSRLS 로 직접 읽는다.
--        Login lookup reads legal_attorney which is never granted to app_user
--        (password_hash protection). app_service reads it via BYPASSRLS.
--   BYPASSRLS ≠ 슈퍼유저 / BYPASSRLS ≠ superuser.
--   테이블 소유·스키마 변경 권한이 전혀 없는 롤도 BYPASSRLS 를 가질 수 있다.
--   A role can hold BYPASSRLS with zero DDL or ownership privilege.
ALTER ROLE app_service
  NOSUPERUSER
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION;
-- NOLOGIN / LOGIN 은 여기서 건드리지 않는다.
-- Production 배포 시 연산자가 직접 LOGIN + PASSWORD 를 설정한다 (§3 참조).
-- LOGIN/NOLOGIN is not set here; the operator sets it at creation time (see §3).


-- =============================================================================
-- §2. app_service 명시적 최소 권한 부여
--     (Explicit least-privilege GRANTs for app_service)
-- =============================================================================
-- 이 GRANT 블록은 프로덕션에서 별도 owner 롤이 DDL 객체를 소유할 때에도
-- app_service 가 정확히 필요한 연산만 수행할 수 있도록 보장한다.
-- These grants ensure app_service can perform exactly the operations its code
-- exercises even when a separate role (not app_service) owns the tables in
-- production — decoupling app_service from table ownership entirely.

-- ── 스키마 사용 (Schema access) ──────────────────────────────────────────────
GRANT USAGE ON SCHEMA public TO app_service;

-- ── legal_attorney: 로그인 조회 전용 (login lookup — SELECT only) ────────────
-- app_user 에는 절대 부여하지 않는다 (password_hash 보호).
-- NEVER granted to app_user (protects password_hash).
GRANT SELECT ON legal_attorney TO app_service;

-- ── legal_precedent: 인용 해소 + 인제스트 출처 검증 (citation resolve + ingest) ─
GRANT SELECT ON legal_precedent TO app_service;

-- ── legal_case_document: 인제스트 상태 갱신 (ingest status update) ─────────────
-- SELECT: 인제스트 출처-존재 검증 및 인용 해소용.
--         Source-existence validation during ingest + citation resolve.
GRANT SELECT ON legal_case_document TO app_service;
-- UPDATE: ingest_status, ingested_at 컬럼만 — 열 범위 한정 부여.
--         Column-scoped to only the two ingest-tracking columns.
--         확인 근거: 04_case_document_augment.sql §3 에서 두 컬럼 모두 확인됨.
--         Verified in: 04_case_document_augment.sql §3 (both columns confirmed).
GRANT UPDATE (ingest_status, ingested_at) ON legal_case_document TO app_service;

-- ── legal_document_chunk: 인제스트 upsert (ingest upsert ON CONFLICT) ─────────
-- SELECT + INSERT + UPDATE 모두 필요 (ON CONFLICT DO UPDATE 패턴).
-- All three required for ON CONFLICT DO UPDATE (upsert) pattern.
GRANT SELECT, INSERT, UPDATE ON legal_document_chunk TO app_service;

-- ── 명시적 비부여 항목 (Intentionally NOT granted) ───────────────────────────
-- legal_rag_query_log : INSERT 는 app_user/rls_session 경로로만 실행된다.
--   Query-log INSERT runs exclusively under app_user (rls_session path).
--   app_service 가 쿼리 로그를 직접 기록하는 코드 경로는 없다.
-- legal_case, legal_case_party : app_service 코드 경로에서 접근하지 않는다.
-- DDL (CREATE/DROP/ALTER TABLE) : 절대 부여하지 않는다.
-- DELETE on any table : 부여하지 않는다.


-- =============================================================================
-- §3. 운영자 안내 (Operator note — documentation only, no DDL executed)
-- =============================================================================
-- 프로덕션 self-host 설치 시 아래 패턴을 권고한다.
-- Recommended pattern for production self-host installation:
--
--   -- (a) 별도 소유자 롤: DDL 마이그레이션만 사용, 앱에서는 사용 안 함.
--   --     Separate owner role: used only for DDL migrations, never by the app.
--   CREATE ROLE app_owner LOGIN PASSWORD '...' NOSUPERUSER NOCREATEDB NOCREATEROLE;
--   -- 또는 기존 postgres 슈퍼유저 계정을 마이그레이션 전용으로 사용.
--   -- Or use the existing postgres superuser exclusively for migrations.
--
--   -- (b) app_service: 앱 백엔드 런타임 전용, 테이블을 소유하지 않음.
--   --     app_service: app backend runtime only, owns NO tables.
--   CREATE ROLE app_service LOGIN PASSWORD '강력한_패스워드_여기' -- change me
--     NOSUPERUSER NOCREATEDB NOCREATEROLE BYPASSRLS;
--   -- BYPASSRLS 유지 이유: §1 주석 참조.
--   -- Retain BYPASSRLS: see §1 comment for rationale.
--
--   -- (c) DDL 객체 소유권: app_owner (또는 postgres) 가 모든 테이블을 소유.
--   --     DDL ownership: app_owner (or postgres) owns all tables.
--   --     app_service 는 소유자여서는 안 된다 — 소유자는 묵시적으로 DROP/ALTER
--   --     권한을 갖게 되므로 최소 권한 원칙에 위배된다.
--   --     app_service must NOT own tables — owner implies DROP/ALTER privilege,
--   --     violating least-privilege.
--   --
--   -- REASSIGN OWNED 및 app_owner 생성은 이 파일에서 실행하지 않는다.
--   -- 어느 롤이 객체를 소유할지는 법무법인별 연산자 결정 사항이다.
--   -- REASSIGN OWNED and CREATE ROLE app_owner are NOT executed here.
--   -- Which role owns DDL objects is an operator decision per firm.


-- =============================================================================
-- §4. 검증 쿼리 (Verification queries — run after apply)
-- =============================================================================

-- 롤 속성 확인: rolbypassrls=t, 나머지 모두 f 이어야 한다.
-- Role attributes: expect rolbypassrls=t, all others f.
-- SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolbypassrls
--   FROM pg_roles
--  WHERE rolname = 'app_service';
-- 기대값(Expected): f, f, f, t

-- 테이블 권한 확인 (Table-level grants for app_service):
-- SELECT grantee, table_name, privilege_type
--   FROM information_schema.role_table_grants
--  WHERE grantee = 'app_service'
--  ORDER BY table_name, privilege_type;
-- 기대 행(Expected rows):
--   legal_attorney          | SELECT
--   legal_case_document     | SELECT
--   legal_case_document     | UPDATE   ← column-scoped; table-level entry appears here
--   legal_document_chunk    | INSERT
--   legal_document_chunk    | SELECT
--   legal_document_chunk    | UPDATE
--   legal_precedent         | SELECT
-- (열 범위 UPDATE 는 information_schema.role_column_grants 에서도 확인 가능)
-- (Column-scoped UPDATE also visible in information_schema.role_column_grants)
-- SELECT grantee, table_name, column_name, privilege_type
--   FROM information_schema.role_column_grants
--  WHERE grantee = 'app_service'
--  ORDER BY table_name, column_name;
-- 기대 행(Expected rows):
--   legal_case_document | ingest_status | UPDATE
--   legal_case_document | ingested_at   | UPDATE
