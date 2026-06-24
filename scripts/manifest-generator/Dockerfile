# scripts/manifest-generator/Dockerfile
# Generic one-shot manifest generator (manifest-only — no data seeding).
# Build context: repo root (Coolify clones whole repo, build context = clone root)
#
# Responsibilities:
#   1. Run scaffold.py --profile $PROFILE_SLUG  → out/<slug>/screen-manifest.json
#   2. Copy manifest to shared volume at $MANIFEST_OUT
#
# Container exits 0 on success. Compose restart: "no".
# Reusable by any SEED_FILE-backed demo (lawfirm-demo, construction-demo, ...).

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

# scaffold.py needs PyYAML only (no HTTP seeding here).
RUN pip install --no-cache-dir pyyaml>=6.0

# Copy repo structure needed by scaffold.py (profile → catalog → DDL + manifest)
COPY scripts/ ./scripts/
COPY profiles/ ./profiles/
COPY presets/ ./presets/
COPY middle/contract/ ./middle/contract/

RUN chmod +x scripts/manifest-generator/entrypoint.sh

ENTRYPOINT ["sh", "scripts/manifest-generator/entrypoint.sh"]
