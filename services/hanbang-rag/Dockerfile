# services/hanbang-rag/Dockerfile
# Build context: REPO ROOT (compose: context: .)
# Coolify clones the whole repo; this Dockerfile is referenced as:
#   build:
#     context: .
#     dockerfile: services/hanbang-rag/Dockerfile
#
# Single-stage: FastAPI + vanilla SPA. No React build stage (Lite tier).
# The vanilla SPA lives at services/hanbang-rag/web/ and is copied as part of
# `COPY services/hanbang-rag/ .` below — api.py mounts it at /app.

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

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
