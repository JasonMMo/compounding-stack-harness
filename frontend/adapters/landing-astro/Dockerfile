# frontend/adapters/landing-astro/Dockerfile
#
# Build context: REPO ROOT (Coolify clones the whole repo; dockerfile path is
#   frontend/adapters/landing-astro/Dockerfile, build context = repo root).
# All COPY paths below are relative to the repo root.
#
# ARGs:
#   PROFILE_SLUG  — customer profile slug (default: gtm-landing).
#                   scaffold.py emits out/${PROFILE_SLUG}/site-manifest.json.
#   DEMO_MODE     — set to "1" to stub the contact form (no backend needed).
#                   Passed as PUBLIC_DEMO_MODE to the Astro build.

# ---------------------------------------------------------------------------
# Stage: build
# ---------------------------------------------------------------------------
FROM node:20-alpine AS build

ARG PROFILE_SLUG=gtm-landing
ARG DEMO_MODE=1

# python3 + pyyaml required by scripts/workflow/scaffold.py
RUN apk add --no-cache python3 py3-yaml

WORKDIR /app

# Copy whole repo (build context = repo root)
COPY . .

# Generate site-manifest for the target profile
RUN python3 scripts/workflow/scaffold.py --profile ${PROFILE_SLUG}

# Work inside the adapter directory for the npm steps
WORKDIR /app/frontend/adapters/landing-astro

# package-lock.json is present in this adapter — use npm ci for reproducible install
RUN npm ci

# Expose manifest path and demo mode to the Astro build
ENV PUBLIC_SITE_MANIFEST=/app/out/${PROFILE_SLUG}/site-manifest.json
ENV PUBLIC_DEMO_MODE=${DEMO_MODE}

# codegen + build-tokens aurora + astro build → dist/
RUN npm run build

# ---------------------------------------------------------------------------
# Stage: final
# ---------------------------------------------------------------------------
FROM nginx:alpine

COPY --from=build /app/frontend/adapters/landing-astro/dist /usr/share/nginx/html

EXPOSE 80
# nginx:alpine default config serves /usr/share/nginx/html with index.html — no extra config needed
