# services/legal-rag/Dockerfile
# Build context: REPO ROOT (compose: context: .)
# Coolify clones the whole repo; this Dockerfile is referenced as:
#   build:
#     context: .
#     dockerfile: services/legal-rag/Dockerfile

##############################################################################
# Stage 1 — legal-pro React build (Node 20, multi-stage)
# Produces /src/frontend/adapters/legal-pro/dist/ (static assets, base=/pro/)
#
# REPO_ROOT resolution:
#   __dirname = /src/frontend/adapters/legal-pro/scripts
#   resolve(__dirname, '..','..','..','..') = /src   ← REPO_ROOT
#   codegen.mjs  reads: /src/middle/contract/error/codes.yaml
#   build-tokens reads: /src/services/legal-rag/web/styles/tokens.css
#                       /src/services/legal-rag/web/styles/app.css
#                       /src/presets/themes/legal-pro/tokens.css
#   All three COPY blocks below satisfy these paths exactly.
##############################################################################
FROM node:20-slim AS frontend-builder

WORKDIR /src

# prebuild dependencies — repo-root subtrees read by codegen.mjs and build-tokens.mjs.
# These must be present before `npm run build` (prebuild runs codegen then build-tokens).
COPY middle/contract/ ./middle/contract/
COPY presets/themes/legal-pro/ ./presets/themes/legal-pro/
COPY services/legal-rag/web/styles/ ./services/legal-rag/web/styles/

# Adapter deps (layer-cache: copy lock files before full source)
COPY frontend/adapters/legal-pro/package.json frontend/adapters/legal-pro/package-lock.json ./frontend/adapters/legal-pro/
WORKDIR /src/frontend/adapters/legal-pro
RUN npm ci --prefer-offline

# Full adapter source (scripts/, src/, index.html, tsconfig, vite.config.ts)
COPY frontend/adapters/legal-pro/ ./

RUN npm run build   # prebuild: codegen.mjs → build-tokens.mjs → tsc+vite → dist/

##############################################################################
# Stage 2 — FastAPI legal-rag runtime
##############################################################################
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

# Copy legal-pro React dist → web/pro/ (served at /pro by api.py StaticFiles mount)
# Source path mirrors WORKDIR in Stage 1: /src/frontend/adapters/legal-pro/dist/
COPY --from=frontend-builder /src/frontend/adapters/legal-pro/dist ./web/pro

# Non-root security: create appuser, chown workdir, drop privileges.
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
