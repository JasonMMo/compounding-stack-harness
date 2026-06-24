#!/bin/sh
# scripts/manifest-generator/entrypoint.sh
# Generic one-shot manifest generator (manifest-only — no data seeding).
#
# Use for any demo whose backend gets its data from a baked SEED_FILE
# (in-memory store) rather than HTTP seeding. It runs scaffold.py for the
# given profile and copies the resulting screen-manifest.json onto a shared
# volume that the frontend mounts read-only. This removes the host bind-mount
# + manual scp step entirely: a plain Coolify Redeploy regenerates the manifest
# from current git (so new entities appear in nav automatically).
#
# Contrast with scripts/taskflow-seeder/ which ALSO HTTP-seeds records — use
# this lighter generator when SEED_FILE already supplies the data.
#
# Runs inside the manifest container; exits 0 on success, non-zero on failure.
# Coolify restart: "no" — runs once per deploy.

set -e

REPO_ROOT=/app
SLUG="${PROFILE_SLUG:?PROFILE_SLUG is required}"
MANIFEST_OUT="${MANIFEST_OUT:-/data/manifest/screen-manifest.json}"

echo "[manifest-gen] generate screen-manifest for profile '${SLUG}'"
cd "${REPO_ROOT}"
python scripts/workflow/scaffold.py --profile "${SLUG}"

# scaffold.py writes to out/<slug>/screen-manifest.json
SRC="out/${SLUG}/screen-manifest.json"
if [ ! -f "${SRC}" ]; then
  echo "[manifest-gen] ERROR: scaffold.py did not produce ${SRC}" >&2
  exit 1
fi

mkdir -p "$(dirname "${MANIFEST_OUT}")"
cp "${SRC}" "${MANIFEST_OUT}"
echo "[manifest-gen] manifest written to ${MANIFEST_OUT} — exiting cleanly"
