#!/usr/bin/env bash
# deploy/preview/legal-rag.apply-schema.sh
#
# PURPOSE: Apply DDL + seed to the Coolify-managed pgvector container for legal-rag preview.
#          Base stage guarded by a table-exists check (render.py emits plain CREATE TABLE);
#          augment stage idempotent (IF NOT EXISTS / DO blocks); seed stage guarded by an
#          attorney-count check. The whole script is safely re-runnable.
#
# BASE DDL: rendered on-the-fly via render.py scoped to 4 legal entities only
#   (legal-case, precedent, case-party, case-document). This omits HR FK pollution.
#   Exact render command:
#     python presets/ddl/render.py --dialect postgres \
#       --entities legal-case,precedent,case-party,case-document
#   Run inside a throwaway python:3.11-slim container to avoid host-pyyaml dependency.
#
# pg_bigm NOTE: pgvector:pg16 image does NOT include pg_bigm.
#   01_extensions.sql auto-degrades to plainto_tsquery (preview option A). No manual skip needed.
#
# USAGE: bash deploy/preview/legal-rag.apply-schema.sh [db-container-name]
#   Run from repo root. Container name is auto-discovered if not provided.
#
# REQUIRED: Docker on the host. Repo must be cloned on the VPS host.
# NO PASSWORDS: relies on trust auth via docker exec (loopback, no network exposure).

set -euo pipefail

# ── 1. REPO ROOT ──────────────────────────────────────────────────────────────
REPO_ROOT="$(git rev-parse --show-toplevel)"
echo "[1/9] Repo root: $REPO_ROOT"

# ── 2. DISCOVER DB CONTAINER ──────────────────────────────────────────────────
PROJECT_UUID="gwpba3e8j8upf9v0swf96wkt"

if [ "${1:-}" != "" ]; then
  DB_CONTAINER="$1"
  echo "[2/9] DB container (from arg): $DB_CONTAINER"
else
  DB_CONTAINER="$(docker ps --format '{{.Names}}' \
    | grep "^db-${PROJECT_UUID}" | head -1 || true)"
  if [ -z "$DB_CONTAINER" ]; then
    echo "ERROR: no running container matching 'db-${PROJECT_UUID}*' found."
    echo "       Pass the container name as the first argument:"
    echo "         bash deploy/preview/legal-rag.apply-schema.sh <container-name>"
    exit 1
  fi
  echo "[2/9] DB container (auto-discovered): $DB_CONTAINER"
fi

# ── 3. DISCOVER POSTGRES_USER ─────────────────────────────────────────────────
PG_USER="$(docker exec "$DB_CONTAINER" printenv POSTGRES_USER)"
echo "[3/9] POSTGRES_USER: $PG_USER"
DB_NAME="legaldb"

# ── 4. APPLY HELPER ───────────────────────────────────────────────────────────
apply() {
  local label="$1"
  local file="$2"
  echo "  --> applying: $label"
  docker exec -i "$DB_CONTAINER" \
    psql -U "$PG_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 \
    < "$file"
}

apply_stdin() {
  local label="$1"
  echo "  --> applying: $label (stdin)"
  docker exec -i "$DB_CONTAINER" \
    psql -U "$PG_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1
}

# ── 5. RENDER + APPLY BASE DDL (guarded — render.py emits plain CREATE TABLE, not IF NOT EXISTS)
# Probe: to_regclass returns NULL (→ 'f') if table absent, 't' if present.
# set -e tolerant via 2>/dev/null || echo f.
EXISTS_CASE="$(docker exec "$DB_CONTAINER" \
  psql -U "$PG_USER" -d "$DB_NAME" -t -A \
  -c "SELECT to_regclass('public.legal_case') IS NOT NULL;" 2>/dev/null || echo f)"
EXISTS_CASE="${EXISTS_CASE// /}"

if [ "$EXISTS_CASE" = "t" ]; then
  echo "[4-5/9] base tables already present — skipping render + base apply"
else
  echo "[4/9] Rendering base DDL via throwaway python container ..."
  BASE_DDL="$(docker run --rm \
    -v "$REPO_ROOT":/w \
    -w /w \
    python:3.11-slim \
    sh -c 'pip install -q pyyaml && python presets/ddl/render.py --dialect postgres --entities legal-case,precedent,case-party,case-document')"

  echo "  --> base DDL rendered ($(echo "$BASE_DDL" | wc -l) lines)"

  echo "[5/9] Applying base DDL ..."
  echo "$BASE_DDL" | apply_stdin "base (legal_case, legal_precedent, legal_case_party, legal_case_document)"
fi

# ── 6. APPLY AUGMENTS 01-08 (STRICT ORDER) ───────────────────────────────────
echo "[6/9] Applying augments 01-08 ..."
AUGMENTS_DIR="$REPO_ROOT/presets/ddl/augments/legal"

apply "01_extensions (vector ext + pg_bigm guard + roles)" \
  "$AUGMENTS_DIR/01_extensions.sql"
apply "02_legal_case_augment" \
  "$AUGMENTS_DIR/02_legal_case_augment.sql"
apply "03_precedent_augment" \
  "$AUGMENTS_DIR/03_precedent_augment.sql"
apply "04_case_document_augment" \
  "$AUGMENTS_DIR/04_case_document_augment.sql"
apply "05_case_party_rls" \
  "$AUGMENTS_DIR/05_case_party_rls.sql"
apply "06_legal_document_chunk" \
  "$AUGMENTS_DIR/06_legal_document_chunk.sql"
apply "07_rag_query_log" \
  "$AUGMENTS_DIR/07_rag_query_log.sql"
apply "08_legal_attorney (FK legal_case -> legal_attorney)" \
  "$AUGMENTS_DIR/08_legal_attorney.sql"
apply "09_grants (app_user RLS privileges)" \
  "$AUGMENTS_DIR/09_grants.sql"

# ── 7. APPLY SEEDS (FK DEPENDENCY ORDER) ──────────────────────────────────────
SEED_DIR="$AUGMENTS_DIR/seed"

# Idempotency guard: only seed_attorneys.sql has ON CONFLICT DO NOTHING; the others do not.
# Probe the current attorney count. Use || echo 0 so set -e does not fire if the table
# somehow doesn't exist yet (shouldn't happen by step 7, but safe to guard anyway).
ATTY_COUNT="$(docker exec "$DB_CONTAINER" \
  psql -U "$PG_USER" -d "$DB_NAME" -t -A \
  -c "SELECT COUNT(*) FROM legal_attorney;" 2>/dev/null || echo 0)"
ATTY_COUNT="${ATTY_COUNT// /}"  # trim whitespace

if [ "$ATTY_COUNT" = "3" ]; then
  echo "[7/9] seeds already present (attorneys=3) — skipping reseed"
else
  echo "[7/9] Applying seeds (running as superuser -> RLS bypassed) ..."
  apply "seed_attorneys (3 rows — FK target, must be first)" \
    "$SEED_DIR/seed_attorneys.sql"
  apply "seed_precedents (22 rows)" \
    "$SEED_DIR/seed_precedents.sql"
  apply "seed_cases (12 cases + 29 parties)" \
    "$SEED_DIR/seed_cases.sql"
  apply "seed_case_documents (15 rows)" \
    "$SEED_DIR/seed_case_documents.sql"
fi

# ── 8. VERIFY ─────────────────────────────────────────────────────────────────
echo "[8/9] Running verification queries ..."

VERIFY_SQL="
SELECT
  (SELECT COUNT(*) FROM legal_attorney)       AS attorneys,
  (SELECT COUNT(*) FROM legal_case)           AS cases,
  (SELECT COUNT(*) FROM legal_precedent)      AS precedents,
  (SELECT COUNT(*) FROM legal_case_party)     AS parties,
  (SELECT COUNT(*) FROM legal_case_document)  AS documents;

SELECT extname FROM pg_extension WHERE extname IN ('vector','pg_bigm');

SELECT rolname, rolbypassrls, rolsuper
  FROM pg_roles WHERE rolname IN ('app_service','app_user');

SELECT relrowsecurity, relforcerowsecurity
  FROM pg_class WHERE relname='legal_case';
"

RESULT="$(echo "$VERIFY_SQL" | docker exec -i "$DB_CONTAINER" \
  psql -U "$PG_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -t -A -F '|')"

echo "$RESULT"

# ── 9. PASS/FAIL SUMMARY ─────────────────────────────────────────────────────
echo ""
echo "[9/9] PASS/FAIL summary"

COUNTS="$(echo "$VERIFY_SQL" | docker exec -i "$DB_CONTAINER" \
  psql -U "$PG_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 \
  -c "SELECT
        (SELECT COUNT(*) FROM legal_attorney)       AS attorneys,
        (SELECT COUNT(*) FROM legal_case)           AS cases,
        (SELECT COUNT(*) FROM legal_precedent)      AS precedents,
        (SELECT COUNT(*) FROM legal_case_party)     AS parties,
        (SELECT COUNT(*) FROM legal_case_document)  AS documents;" \
  -t -A -F '|')"

ATTORNEYS="$(echo "$COUNTS" | awk -F'|' '{print $1}')"
CASES="$(echo     "$COUNTS" | awk -F'|' '{print $2}')"
PRECEDENTS="$(echo "$COUNTS" | awk -F'|' '{print $3}')"
PARTIES="$(echo   "$COUNTS" | awk -F'|' '{print $4}')"
DOCUMENTS="$(echo "$COUNTS" | awk -F'|' '{print $5}')"

PASS=true

check() {
  local label="$1" actual="$2" expected="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  PASS  $label: $actual"
  else
    echo "  FAIL  $label: got $actual, expected $expected"
    PASS=false
  fi
}

check "attorneys"  "$ATTORNEYS"  "3"
check "cases"      "$CASES"      "12"
check "precedents" "$PRECEDENTS" "22"
check "parties"    "$PARTIES"    "29"
check "documents"  "$DOCUMENTS"  "15"

# pg_bigm should be ABSENT in preview
BIGM_COUNT="$(docker exec "$DB_CONTAINER" \
  psql -U "$PG_USER" -d "$DB_NAME" -t -A \
  -c "SELECT COUNT(*) FROM pg_extension WHERE extname='pg_bigm';")"
if [ "$BIGM_COUNT" = "0" ]; then
  echo "  PASS  pg_bigm: correctly ABSENT (preview auto-degraded to plainto_tsquery)"
else
  echo "  WARN  pg_bigm: PRESENT (unexpected on pgvector-only image — verify image)"
fi

VECTOR_COUNT="$(docker exec "$DB_CONTAINER" \
  psql -U "$PG_USER" -d "$DB_NAME" -t -A \
  -c "SELECT COUNT(*) FROM pg_extension WHERE extname='vector';")"
if [ "$VECTOR_COUNT" = "1" ]; then
  echo "  PASS  vector extension: present"
else
  echo "  FAIL  vector extension: ABSENT — 01_extensions.sql may have failed"
  PASS=false
fi

RLS="$(docker exec "$DB_CONTAINER" \
  psql -U "$PG_USER" -d "$DB_NAME" -t -A -F'|' \
  -c "SELECT relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname='legal_case';")"
RLS_ON="$(echo "$RLS" | awk -F'|' '{print $1}')"
FORCE_ON="$(echo "$RLS" | awk -F'|' '{print $2}')"
if [ "$RLS_ON" = "t" ] && [ "$FORCE_ON" = "t" ]; then
  echo "  PASS  legal_case RLS: relrowsecurity=t, relforcerowsecurity=t"
else
  echo "  FAIL  legal_case RLS: relrowsecurity=$RLS_ON, relforcerowsecurity=$FORCE_ON (expected t,t)"
  PASS=false
fi

echo ""
if [ "$PASS" = "true" ]; then
  echo "=========================================="
  echo "  ALL CHECKS PASSED. Schema + seed ready."
  echo "  Next step: §5 embed-adapter health, then §4-4 ingest demo docs."
  echo "=========================================="
else
  echo "=========================================="
  echo "  ONE OR MORE CHECKS FAILED. See FAIL lines above."
  echo "  The DB state is partially applied — fix the error and re-run (idempotent)."
  echo "=========================================="
  exit 1
fi
