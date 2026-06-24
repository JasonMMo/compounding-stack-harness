# scripts/taskflow-seeder/Dockerfile
# One-shot seeder container for taskflow-demo.
# Build context: repo root (Coolify clones whole repo, build context = clone root)
#
# Responsibilities:
#   1. Run scaffold.py --profile taskflow-demo  → generates out/taskflow-demo/screen-manifest.json
#   2. Copy manifest to shared volume at $MANIFEST_OUT
#   3. Run seed_loader.py --slug taskflow-demo --base-url $BACKEND_BASE_URL  → 51 records
#
# Container exits 0 on success. Compose restart: "no".

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

# Seeder needs: PyYAML (scaffold.py + seed_loader.py) + requests (seed_loader HTTP)
RUN pip install --no-cache-dir pyyaml>=6.0 requests>=2.31

# Copy repo structure needed by scaffold.py and seed_loader.py
COPY scripts/ ./scripts/
COPY profiles/ ./profiles/
COPY presets/ ./presets/
COPY middle/contract/ ./middle/contract/

RUN chmod +x scripts/taskflow-seeder/entrypoint.sh

ENTRYPOINT ["sh", "scripts/taskflow-seeder/entrypoint.sh"]
