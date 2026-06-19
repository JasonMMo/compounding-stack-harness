#!/usr/bin/env bash
# deploy/preview/legal-rag.ingest-demo.sh
#
# PURPOSE: Load the 3 demo documents into legal_document_chunk (with embeddings)
#          so /search has data to return for the verify-search script.
#
# FOUNDER GATE: This script only WRITES to the running preview stack.
#   Do NOT attempt to run docker/ssh/deploy from a local machine — run on the VPS host.
#
# USAGE: bash deploy/preview/legal-rag.ingest-demo.sh [app-container-name] [db-container-name]
#   Run from repo root. Both container names are auto-discovered if not provided.
#
# IDEMPOTENT: The /ingest endpoint uses ON CONFLICT DO NOTHING (or upsert) on source_id.
#   Re-running this script is safe — existing chunks are overwritten/skipped, not duplicated.
#
# REQUIRED: Docker on the host. Repo must be cloned on the VPS host.
#   App container must be running and healthy (uvicorn on 0.0.0.0:8000 inside container).
#   App image is python:3.11-slim — no curl. All HTTP done via docker exec python heredoc.

set -euo pipefail

# ── 1. REPO ROOT ──────────────────────────────────────────────────────────────
REPO_ROOT="$(git rev-parse --show-toplevel)"
echo "[1/5] Repo root: $REPO_ROOT"

# ── 2. DISCOVER APP + DB CONTAINERS ──────────────────────────────────────────
PROJECT_UUID="gwpba3e8j8upf9v0swf96wkt"

if [ "${1:-}" != "" ]; then
  APP_CONTAINER="$1"
  echo "[2/5] App container (from arg): $APP_CONTAINER"
else
  APP_CONTAINER="$(docker ps --format '{{.Names}}' \
    | grep "^app-${PROJECT_UUID}" | head -1 || true)"
  if [ -z "$APP_CONTAINER" ]; then
    echo "ERROR: no running container matching 'app-${PROJECT_UUID}*' found."
    echo "       Pass the container name as the first argument:"
    echo "         bash deploy/preview/legal-rag.ingest-demo.sh <app-container> [db-container]"
    exit 1
  fi
  echo "[2/5] App container (auto-discovered): $APP_CONTAINER"
fi

if [ "${2:-}" != "" ]; then
  DB_CONTAINER="$2"
  echo "[2/5] DB container (from arg): $DB_CONTAINER"
else
  DB_CONTAINER="$(docker ps --format '{{.Names}}' \
    | grep "^db-${PROJECT_UUID}" | head -1 || true)"
  if [ -z "$DB_CONTAINER" ]; then
    echo "ERROR: no running container matching 'db-${PROJECT_UUID}*' found."
    echo "       Pass the db container name as the second argument:"
    echo "         bash deploy/preview/legal-rag.ingest-demo.sh <app-container> <db-container>"
    exit 1
  fi
  echo "[2/5] DB container (auto-discovered): $DB_CONTAINER"
fi

# ── 3. COPY DEMO DOCS TO INGEST BIND MOUNT ───────────────────────────────────
echo "[3/5] Copying demo docs to host ingest directory ..."
INGEST_HOST_DIR="/data/legal-rag/ingest"
DEMO_DOCS_DIR="$REPO_ROOT/presets/ddl/augments/legal/seed/demo_docs"

mkdir -p "$INGEST_HOST_DIR"

for fname in \
  complaint_hanbit_vs_miraesolution.txt \
  contract_software_supply.txt \
  brief_alphatech_copyright.txt
do
  cp -f "$DEMO_DOCS_DIR/$fname" "$INGEST_HOST_DIR/$fname"
  echo "  --> copied: $fname"
done

echo "  Ingest dir contents:"
ls -lh "$INGEST_HOST_DIR"

# ── 4. READ SERVICE TOKEN ─────────────────────────────────────────────────────
echo "[4/5] Reading LEGAL_RAG_SERVICE_TOKEN from app container ..."
SERVICE_TOKEN="$(docker exec "$APP_CONTAINER" printenv LEGAL_RAG_SERVICE_TOKEN)"
if [ -z "$SERVICE_TOKEN" ]; then
  echo "ERROR: LEGAL_RAG_SERVICE_TOKEN is empty in container $APP_CONTAINER"
  exit 1
fi
# Print masked token (first 4 + last 4 chars only)
TOKEN_LEN="${#SERVICE_TOKEN}"
if [ "$TOKEN_LEN" -gt 8 ]; then
  TOKEN_PREVIEW="${SERVICE_TOKEN:0:4}...${SERVICE_TOKEN: -4}"
else
  TOKEN_PREVIEW="<token>"
fi
echo "  Token: $TOKEN_PREVIEW (length=$TOKEN_LEN)"

# ── 5. INGEST EACH DOCUMENT VIA APP HTTP ─────────────────────────────────────
echo "[5/5] Posting documents to /ingest (via python inside app container) ..."

PASS=true

# The SERVICE_TOKEN is passed via `docker exec -e TOKEN=` so it is never
# interpolated into the heredoc text. Each ingest runs inside the app container
# (python:3.11-slim has no curl). `if ! docker exec ...` keeps the failure path
# set -e-safe so the SUMMARY block always prints (PASS=false is accumulated).

# Doc 1: complaint_hanbit_vs_miraesolution.txt
if ! docker exec \
  -e TOKEN="$SERVICE_TOKEN" \
  -e DOC_FILENAME="complaint_hanbit_vs_miraesolution.txt" \
  -e DOC_SOURCE_ID="d0c00000-0001-0001-0001-000000000001" \
  -e DOC_CASE_ID="c0000000-0001-0001-0001-000000000001" \
  "$APP_CONTAINER" python - <<'PY'
import urllib.request
import urllib.error
import json
import os
import sys

token      = os.environ["TOKEN"]
filename   = os.environ["DOC_FILENAME"]
source_id  = os.environ["DOC_SOURCE_ID"]
case_id    = os.environ["DOC_CASE_ID"]
file_path  = f"/data/legal-docs/{filename}"

payload = json.dumps({
    "file_path":   file_path,
    "source_type": "case_document",
    "source_id":   source_id,
    "case_id":     case_id,
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/ingest",
    data=payload,
    headers={
        "Content-Type":    "application/json",
        "X-Service-Token": token,
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8")
        status = resp.status
        d = json.loads(body)
        chunks = d.get("chunks_upserted", d.get("chunks_inserted", "?"))
        print(f"  PASS  [1/3] complaint_hanbit_vs_miraesolution  status={status}  chunks_upserted={chunks}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"  FAIL  [1/3] HTTP {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
PY
then
  PASS=false
fi

# Doc 2: contract_software_supply.txt
if ! docker exec \
  -e TOKEN="$SERVICE_TOKEN" \
  -e DOC_FILENAME="contract_software_supply.txt" \
  -e DOC_SOURCE_ID="d0c00000-0001-0001-0001-000000000002" \
  -e DOC_CASE_ID="c0000000-0001-0001-0001-000000000001" \
  "$APP_CONTAINER" python - <<'PY'
import urllib.request
import urllib.error
import json
import os
import sys

token      = os.environ["TOKEN"]
filename   = os.environ["DOC_FILENAME"]
source_id  = os.environ["DOC_SOURCE_ID"]
case_id    = os.environ["DOC_CASE_ID"]
file_path  = f"/data/legal-docs/{filename}"

payload = json.dumps({
    "file_path":   file_path,
    "source_type": "case_document",
    "source_id":   source_id,
    "case_id":     case_id,
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/ingest",
    data=payload,
    headers={
        "Content-Type":    "application/json",
        "X-Service-Token": token,
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8")
        status = resp.status
        d = json.loads(body)
        chunks = d.get("chunks_upserted", d.get("chunks_inserted", "?"))
        print(f"  PASS  [2/3] contract_software_supply  status={status}  chunks_upserted={chunks}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"  FAIL  [2/3] HTTP {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
PY
then
  PASS=false
fi

# Doc 3: brief_alphatech_copyright.txt
if ! docker exec \
  -e TOKEN="$SERVICE_TOKEN" \
  -e DOC_FILENAME="brief_alphatech_copyright.txt" \
  -e DOC_SOURCE_ID="d0c00000-0001-0001-0001-000000000015" \
  -e DOC_CASE_ID="c0000000-0001-0001-0001-000000000012" \
  "$APP_CONTAINER" python - <<'PY'
import urllib.request
import urllib.error
import json
import os
import sys

token      = os.environ["TOKEN"]
filename   = os.environ["DOC_FILENAME"]
source_id  = os.environ["DOC_SOURCE_ID"]
case_id    = os.environ["DOC_CASE_ID"]
file_path  = f"/data/legal-docs/{filename}"

payload = json.dumps({
    "file_path":   file_path,
    "source_type": "case_document",
    "source_id":   source_id,
    "case_id":     case_id,
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/ingest",
    data=payload,
    headers={
        "Content-Type":    "application/json",
        "X-Service-Token": token,
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8")
        status = resp.status
        d = json.loads(body)
        chunks = d.get("chunks_upserted", d.get("chunks_inserted", "?"))
        print(f"  PASS  [3/3] brief_alphatech_copyright  status={status}  chunks_upserted={chunks}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"  FAIL  [3/3] HTTP {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
PY
then
  PASS=false
fi

# ── VERIFY: chunk count + per-source breakdown ─────────────────────────────────
echo ""
echo "  Verifying chunk counts in DB ..."
PG_USER="$(docker exec "$DB_CONTAINER" printenv POSTGRES_USER)"

CHUNK_COUNT="$(docker exec "$DB_CONTAINER" \
  psql -U "$PG_USER" -d legaldb -t -A \
  -c "SELECT COUNT(*) FROM legal_document_chunk;" 2>/dev/null || echo 0)"
CHUNK_COUNT="${CHUNK_COUNT// /}"

echo ""
echo "  Per-source chunk breakdown:"
docker exec "$DB_CONTAINER" \
  psql -U "$PG_USER" -d legaldb \
  -c "SELECT source_id, COUNT(*) AS chunks FROM legal_document_chunk GROUP BY source_id ORDER BY source_id;"

# ── PASS/FAIL SUMMARY ─────────────────────────────────────────────────────────
echo ""
echo "[SUMMARY] PASS/FAIL"

if [ "$CHUNK_COUNT" -gt 0 ] 2>/dev/null; then
  echo "  PASS  total chunks in legal_document_chunk: $CHUNK_COUNT"
else
  echo "  FAIL  total chunks in legal_document_chunk: $CHUNK_COUNT (expected > 0)"
  PASS=false
fi

echo ""
if [ "$PASS" = "true" ]; then
  echo "============================================================"
  echo "  ALL CHECKS PASSED. Demo documents ingested."
  echo "  NOTE: Re-running is safe — /ingest is idempotent (ON CONFLICT upsert)."
  echo "  Next step: bash deploy/preview/legal-rag.verify-search.sh"
  echo "============================================================"
else
  echo "============================================================"
  echo "  ONE OR MORE CHECKS FAILED. See FAIL lines above."
  echo "  Check app container logs: docker logs $APP_CONTAINER --tail 50"
  echo "  Re-run after fixing (script is idempotent)."
  echo "============================================================"
  exit 1
fi
