#!/bin/sh
# scripts/taskflow-seeder/entrypoint.sh
# One-shot init: (1) generate screen-manifest, (2) seed demo data into backend.
# Runs inside the seeder container; exits 0 on success, non-zero on failure.
# Coolify restart: "no" — runs once per deploy.

set -e

REPO_ROOT=/app
SLUG="${PROFILE_SLUG:-taskflow-demo}"
BACKEND="${BACKEND_BASE_URL:-http://backend:8081}"
MANIFEST_OUT="${MANIFEST_OUT:-/data/manifest/screen-manifest.json}"

echo "[seeder] Step 1: generate screen-manifest for profile '${SLUG}'"
cd "${REPO_ROOT}"
python scripts/workflow/scaffold.py --profile "${SLUG}"
# scaffold.py writes to out/<slug>/screen-manifest.json
SRC="out/${SLUG}/screen-manifest.json"
if [ ! -f "${SRC}" ]; then
  echo "[seeder] ERROR: scaffold.py did not produce ${SRC}" >&2
  exit 1
fi
mkdir -p "$(dirname "${MANIFEST_OUT}")"
cp "${SRC}" "${MANIFEST_OUT}"
echo "[seeder] manifest written to ${MANIFEST_OUT}"

echo "[seeder] Step 2: seed ${SLUG} demo data into ${BACKEND}"
python scripts/workflow/seed_loader.py --slug "${SLUG}" --base-url "${BACKEND}"
echo "[seeder] seed complete — exiting cleanly"
