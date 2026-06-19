#!/usr/bin/env bash
# deploy/preview/legal-rag.verify-search.sh
#
# PURPOSE: Prove that hybrid /search returns ranked chunks + citations, AND that
#          RLS isolates chunks at the search layer per attorney.
#          Three assertions:
#            A. 이준호 (partner, sees all 12 cases) gets c001 chunks for supply-contract query.
#            B. 박서연 (sees c007-c012 only) gets ZERO c001 chunks for same query.
#            C. 박서연 gets c012 chunks for the copyright query (proves she sees her own data).
#
# FOUNDER GATE: Run on the VPS host. Do NOT run docker/ssh from a local machine.
#
# USAGE: bash deploy/preview/legal-rag.verify-search.sh [app-container-name]
#   Run from repo root. Container name is auto-discovered if not provided.
#
# IDEMPOTENT / RE-RUNNABLE: Read-only assertions against live data. Safe to re-run anytime.
#
# SECURITY NOTE: The demo password literal demo1234! is kept ONLY inside python string
#   literals within the heredoc — never in a bash double-quoted string where ! would
#   trigger bash history expansion. No secret is written to the script file.
#
# PREREQUISITES: legal-rag.ingest-demo.sh must have run successfully first
#   (legal_document_chunk must contain data).

set -euo pipefail

# ── 1. REPO ROOT ──────────────────────────────────────────────────────────────
REPO_ROOT="$(git rev-parse --show-toplevel)"
echo "[1/6] Repo root: $REPO_ROOT"

# ── 2. DISCOVER APP CONTAINER ─────────────────────────────────────────────────
PROJECT_UUID="gwpba3e8j8upf9v0swf96wkt"

if [ "${1:-}" != "" ]; then
  APP_CONTAINER="$1"
  echo "[2/6] App container (from arg): $APP_CONTAINER"
else
  APP_CONTAINER="$(docker ps --format '{{.Names}}' \
    | grep "^app-${PROJECT_UUID}" | head -1 || true)"
  if [ -z "$APP_CONTAINER" ]; then
    echo "ERROR: no running container matching 'app-${PROJECT_UUID}*' found."
    echo "       Pass the container name as the first argument:"
    echo "         bash deploy/preview/legal-rag.verify-search.sh <app-container>"
    exit 1
  fi
  echo "[2/6] App container (auto-discovered): $APP_CONTAINER"
fi

# ── 3. LOGIN — 이준호 (partner, sees all 12 cases) ────────────────────────────
echo "[3/6] Logging in as 이준호 (lee.junho@example-lawfirm.kr) ..."

# Password demo1234! lives only in the python string literal below — never in bash.
JUNHO_TOKEN="$(docker exec "$APP_CONTAINER" python - <<'PY'
import urllib.request
import urllib.error
import json
import sys

payload = json.dumps({
    "email":    "lee.junho@example-lawfirm.kr",
    "password": "demo1234!",
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/auth/login",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        d = json.loads(resp.read().decode("utf-8"))
        token = d.get("access_token") or d.get("token") or d.get("jwt")
        if not token:
            print(f"PARSE_ERROR: keys={list(d.keys())}", file=sys.stderr)
            sys.exit(1)
        print(token)
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"LOGIN_FAIL HTTP {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
PY
)"

if [ -z "$JUNHO_TOKEN" ]; then
  echo "ERROR: could not obtain JWT for 이준호"
  exit 1
fi
echo "  OK  JWT obtained for 이준호"

# ── 4. LOGIN — 박서연 (sees c007-c012 only) ───────────────────────────────────
echo "[4/6] Logging in as 박서연 (park.seoyeon@example-lawfirm.kr) ..."

SEOYEON_TOKEN="$(docker exec "$APP_CONTAINER" python - <<'PY'
import urllib.request
import urllib.error
import json
import sys

payload = json.dumps({
    "email":    "park.seoyeon@example-lawfirm.kr",
    "password": "demo1234!",
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/auth/login",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        d = json.loads(resp.read().decode("utf-8"))
        token = d.get("access_token") or d.get("token") or d.get("jwt")
        if not token:
            print(f"PARSE_ERROR: keys={list(d.keys())}", file=sys.stderr)
            sys.exit(1)
        print(token)
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"LOGIN_FAIL HTTP {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
PY
)"

if [ -z "$SEOYEON_TOKEN" ]; then
  echo "ERROR: could not obtain JWT for 박서연"
  exit 1
fi
echo "  OK  JWT obtained for 박서연"

# ── 5. RUN ASSERTIONS ─────────────────────────────────────────────────────────
echo "[5/6] Running search assertions A / B / C ..."
echo ""

C001="c0000000-0001-0001-0001-000000000001"
C012="c0000000-0001-0001-0001-000000000012"

PASS=true

# ── Assertion A: 이준호 + supply-contract query → c001 chunks present ──────────
echo "  [A] 이준호 + '소프트웨어 공급계약 해지 손해배상 기회손실'"
echo "      EXPECT: total_results > 0  AND  at least one citation.case_id == $C001"

RESULT_A="$(docker exec \
  -e JUNHO_TOKEN="$JUNHO_TOKEN" \
  -e C001="$C001" \
  "$APP_CONTAINER" python - <<'PY'
import urllib.request
import urllib.error
import json
import os
import sys

token = os.environ["JUNHO_TOKEN"]
c001  = os.environ["C001"]

payload = json.dumps({
    "query": "소프트웨어 공급계약 해지 손해배상 기회손실",
    "top_k": 5,
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/search",
    data=payload,
    headers={
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {token}",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        d = json.loads(resp.read().decode("utf-8"))
        total   = d.get("total_results", len(d.get("results", d.get("citations", []))))
        items   = d.get("results", d.get("citations", d.get("chunks", [])))
        case_ids = list({item.get("case_id") or item.get("metadata", {}).get("case_id", "") for item in items})
        has_c001 = c001 in case_ids
        print(f"total={total} case_ids={case_ids} has_c001={has_c001}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP_ERROR {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
PY
)"

A_TOTAL="$(echo "$RESULT_A" | grep -oP 'total=\K[0-9]+' || echo 0)"
A_CASE_IDS="$(echo "$RESULT_A" | grep -oP "case_ids=\K\[[^\]]*\]" || echo '[]')"
A_HAS_C001="$(echo "$RESULT_A" | grep -oP 'has_c001=\K\w+' || echo false)"

if [ "$A_TOTAL" -gt 0 ] 2>/dev/null && [ "$A_HAS_C001" = "True" ]; then
  echo "  PASS  [A] total_results=$A_TOTAL  case_ids=$A_CASE_IDS  c001 present=YES"
else
  echo "  FAIL  [A] total_results=$A_TOTAL  case_ids=$A_CASE_IDS  c001 present=$A_HAS_C001"
  echo "        (expected total>0 AND c001 in case_ids)"
  PASS=false
fi

echo ""

# ── Assertion B: 박서연 + SAME query → zero c001 citations ────────────────────
echo "  [B] 박서연 + '소프트웨어 공급계약 해지 손해배상 기회손실'"
echo "      EXPECT: 0 citations referencing case_id == $C001 (RLS chunk isolation)"

RESULT_B="$(docker exec \
  -e SEOYEON_TOKEN="$SEOYEON_TOKEN" \
  -e C001="$C001" \
  "$APP_CONTAINER" python - <<'PY'
import urllib.request
import urllib.error
import json
import os
import sys

token = os.environ["SEOYEON_TOKEN"]
c001  = os.environ["C001"]

payload = json.dumps({
    "query": "소프트웨어 공급계약 해지 손해배상 기회손실",
    "top_k": 5,
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/search",
    data=payload,
    headers={
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {token}",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        d = json.loads(resp.read().decode("utf-8"))
        total   = d.get("total_results", len(d.get("results", d.get("citations", []))))
        items   = d.get("results", d.get("citations", d.get("chunks", [])))
        case_ids = list({item.get("case_id") or item.get("metadata", {}).get("case_id", "") for item in items})
        c001_count = sum(1 for item in items
                         if (item.get("case_id") or item.get("metadata", {}).get("case_id", "")) == c001)
        print(f"total={total} c001_count={c001_count} case_ids={case_ids}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP_ERROR {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
PY
)"

B_TOTAL="$(echo "$RESULT_B" | grep -oP 'total=\K[0-9]+' || echo 0)"
B_C001_COUNT="$(echo "$RESULT_B" | grep -oP 'c001_count=\K[0-9]+' || echo 99)"
B_CASE_IDS="$(echo "$RESULT_B" | grep -oP "case_ids=\K\[[^\]]*\]" || echo '[]')"

if [ "$B_C001_COUNT" = "0" ]; then
  echo "  PASS  [B] total_results=$B_TOTAL  c001 citations=0  case_ids=$B_CASE_IDS"
  echo "        (RLS correctly excludes c001 chunks for 박서연)"
else
  echo "  FAIL  [B] total_results=$B_TOTAL  c001 citations=$B_C001_COUNT  case_ids=$B_CASE_IDS"
  echo "        (expected 0 c001 citations — RLS chunk isolation BROKEN)"
  PASS=false
fi

echo ""

# ── Assertion C: 박서연 + copyright query → c012 chunks present ───────────────
echo "  [C] 박서연 + '소스코드 저작권 침해 의거성 실질적 유사성'"
echo "      EXPECT: total_results > 0  AND  at least one citation.case_id == $C012"

RESULT_C="$(docker exec \
  -e SEOYEON_TOKEN="$SEOYEON_TOKEN" \
  -e C012="$C012" \
  "$APP_CONTAINER" python - <<'PY'
import urllib.request
import urllib.error
import json
import os
import sys

token = os.environ["SEOYEON_TOKEN"]
c012  = os.environ["C012"]

payload = json.dumps({
    "query": "소스코드 저작권 침해 의거성 실질적 유사성",
    "top_k": 5,
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/search",
    data=payload,
    headers={
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {token}",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        d = json.loads(resp.read().decode("utf-8"))
        total   = d.get("total_results", len(d.get("results", d.get("citations", []))))
        items   = d.get("results", d.get("citations", d.get("chunks", [])))
        case_ids = list({item.get("case_id") or item.get("metadata", {}).get("case_id", "") for item in items})
        has_c012 = c012 in case_ids
        print(f"total={total} case_ids={case_ids} has_c012={has_c012}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP_ERROR {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
PY
)"

C_TOTAL="$(echo "$RESULT_C" | grep -oP 'total=\K[0-9]+' || echo 0)"
C_CASE_IDS="$(echo "$RESULT_C" | grep -oP "case_ids=\K\[[^\]]*\]" || echo '[]')"
C_HAS_C012="$(echo "$RESULT_C" | grep -oP 'has_c012=\K\w+' || echo false)"

if [ "$C_TOTAL" -gt 0 ] 2>/dev/null && [ "$C_HAS_C012" = "True" ]; then
  echo "  PASS  [C] total_results=$C_TOTAL  case_ids=$C_CASE_IDS  c012 present=YES"
else
  echo "  FAIL  [C] total_results=$C_TOTAL  case_ids=$C_CASE_IDS  c012 present=$C_HAS_C012"
  echo "        (expected total>0 AND c012 in case_ids)"
  PASS=false
fi

# ── 6. PASS/FAIL SUMMARY ─────────────────────────────────────────────────────
echo ""
echo "[6/6] PASS/FAIL summary"
echo ""

if [ "$PASS" = "true" ]; then
  echo "  PASS  [A] 이준호 retrieves c001 supply-contract chunks"
  echo "  PASS  [B] 박서연 sees 0 c001 chunks (RLS chunk-level isolation confirmed)"
  echo "  PASS  [C] 박서연 retrieves c012 copyright chunks (own case visible)"
  echo ""
  echo "============================================================"
  echo "  ALL ASSERTIONS PASSED."
  echo "  /search hybrid retrieval + RLS chunk isolation are working."
  echo "  legal-rag preview is DEMO-READY."
  echo "============================================================"
else
  echo "  (see FAIL lines above for details)"
  echo ""
  echo "============================================================"
  echo "  ONE OR MORE ASSERTIONS FAILED."
  echo "  Triage order:"
  echo "    1. Confirm ingest ran: bash deploy/preview/legal-rag.ingest-demo.sh"
  echo "    2. Check app logs:     docker logs $APP_CONTAINER --tail 80"
  echo "    3. Check RLS policy:   bash deploy/preview/legal-rag.apply-schema.sh"
  echo "============================================================"
  exit 1
fi
