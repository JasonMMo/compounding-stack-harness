# embed-adapter/Dockerfile
# Build context: services/legal-rag/embed-adapter  (compose sets context here)
# Port: 8080 (internal only — never exposed outside Coolify uuid-net)
#
# Model bake-in strategy:
#   torch is installed first from the CPU-only PyTorch index to prevent the
#   CUDA variant (several GB) from being pulled in by sentence-transformers.
#   After torch, sentence-transformers is installed, then the model weights are
#   downloaded into /app/.hfcache at build time.  At runtime HF_HUB_OFFLINE=1
#   prevents any network access — the baked weights are used directly.

FROM python:3.11-slim

WORKDIR /app

# ── 1. Base system deps ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
    && rm -rf /var/lib/apt/lists/*

# ── 2. CPU-only torch (must precede sentence-transformers to lock CPU variant) ─
RUN pip install --no-cache-dir \
        torch==2.3.1 \
        --index-url https://download.pytorch.org/whl/cpu

# ── 3. Application requirements (sentence-transformers + fastapi/uvicorn) ─────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── 4. Application source ─────────────────────────────────────────────────────
COPY app.py .

# ── 5. Bake model weights into image (build-time download, offline at runtime) ─
ENV HF_HOME=/app/.hfcache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base')"

# ── 6. Runtime offline flags ──────────────────────────────────────────────────
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    HF_HOME=/app/.hfcache

# ── 7. Non-root security ──────────────────────────────────────────────────────
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
