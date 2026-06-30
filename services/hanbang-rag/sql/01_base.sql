-- =============================================================================
-- hanbang-rag / 01_base.sql
-- Shared foundation: updated_at trigger function + DB roles.
-- Must be applied before any table DDL.
-- Idempotent.
-- =============================================================================

-- ── Trigger function: auto-set updated_at on UPDATE ──────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- ── DB roles ──────────────────────────────────────────────────────────────────
-- app_service: pool login role (BYPASSRLS). Used for ingest writes + login.
--   Grant: superuser-lite. Created separately in Coolify/infra provisioning.
--   DDL here is advisory only (role may pre-exist).
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_service') THEN
    CREATE ROLE app_service LOGIN;
    RAISE NOTICE 'Role app_service created.';
  ELSE
    RAISE NOTICE 'Role app_service already exists — skipped.';
  END IF;
END $$;

-- app_user: RLS-enforced read role. rls_session() issues
--   SET LOCAL ROLE app_user  → drops BYPASSRLS for the transaction.
--   Table-level grants are in 06_grants.sql.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
    CREATE ROLE app_user NOLOGIN;
    RAISE NOTICE 'Role app_user created.';
  ELSE
    RAISE NOTICE 'Role app_user already exists — skipped.';
  END IF;
END $$;
