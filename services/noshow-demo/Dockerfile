# services/noshow-demo/Dockerfile
# Build context: REPO ROOT (compose: context: .)
# Coolify clones the whole repo; this Dockerfile is referenced as:
#   build:
#     context: .
#     dockerfile: services/noshow-demo/Dockerfile
#
# Single-stage: FastAPI + vanilla JS SPA (no build step). SQLite lives
# in-container at /data/noshow.db — no volume mount, wiped on every
# restart/redeploy and every NOSHOW_RESET_INTERVAL_SECONDS (see db.py).

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY services/noshow-demo/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source
COPY services/noshow-demo/ .

# Non-root security: create appuser, own /app and the SQLite data dir.
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

USER appuser

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
