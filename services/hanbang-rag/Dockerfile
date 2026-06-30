# services/hanbang-rag/Dockerfile
# Build context: REPO ROOT (compose: context: .)
# Coolify clones the whole repo; this Dockerfile is referenced as:
#   build:
#     context: .
#     dockerfile: services/hanbang-rag/Dockerfile
#
# D0 simplification: legal-pro React build stage removed.
# Vanilla SPA (web/) will be added in D3.
# D3 TODO: COPY services/hanbang-rag/web/ ./web/

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY services/hanbang-rag/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source
COPY services/hanbang-rag/ .

# Non-root security: create appuser, chown workdir, drop privileges.
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# D1 TODO: CMD targets api:app once api.py is written.
CMD ["python", "-m", "pytest", "--co", "-q"]
