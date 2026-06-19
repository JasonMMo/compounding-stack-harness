# services/legal-rag/Dockerfile
# Build context: REPO ROOT (compose: context: .)
# Coolify clones the whole repo; this Dockerfile is referenced as:
#   build:
#     context: .
#     dockerfile: services/legal-rag/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY services/legal-rag/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source (tests/ excluded via .dockerignore is fine;
# tests/ is not excluded in repo-root .dockerignore but we COPY only
# services/legal-rag/ which includes them — acceptable for now because
# they are small. If image size becomes a concern add a .dockerignore
# entry for services/legal-rag/tests/).
COPY services/legal-rag/ .

# Non-root security: create appuser, chown workdir, drop privileges.
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
