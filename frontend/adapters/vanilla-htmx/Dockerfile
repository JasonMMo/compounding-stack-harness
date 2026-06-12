# frontend/adapters/vanilla-htmx/Dockerfile
# Build context: repo root (docker build -f frontend/adapters/vanilla-htmx/Dockerfile .)
#
# Runtime layout inside image:
#   WORKDIR = /app
#   adapter files (server.py, contract_loader.py, ...)  → /app/
#   templates/                                          → /app/templates/
#   static/                                             → /app/static/
#   middle/contract/                                    → /app/middle/contract/
#
# contract_loader.py resolution:
#   CONTRACT_DIR env var is set by compose → /app/middle/contract/ ✓
#   (fallback walkup from /app also finds /app/middle/contract/ without env var)
#
# PROFILE_MANIFEST is injected at runtime via compose env + host volume bind.
# Rationale: manifest is a scaffold-time artifact per profile slug.
# Baking it into the image would require one image per customer — that defeats
# pluggability. Volume bind at compose run time is the simplest correct choice.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY frontend/adapters/vanilla-htmx/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy adapter source files (server.py, contract_loader.py, manifest_loader.py, etc.)
COPY frontend/adapters/vanilla-htmx/ ./

# Copy design tokens and generate tokens.css at build time.
# tokens.css is .gitignored (generated artifact) so it is absent from the git clone;
# token_css_generator._tokens_dir() walks up from /app and finds /app/design/tokens/.
# UI_THEME: "saas" (default, Pico+tokens) | "public-sector" (KRDS CDN, Pico skipped)
ARG UI_THEME=saas
COPY design/tokens/ ./design/tokens/
RUN python build_tokens.py --ui-theme $UI_THEME

# Copy runtime contract dependency
COPY middle/contract/ ./middle/contract/

EXPOSE 5000

CMD ["python", "server.py"]
