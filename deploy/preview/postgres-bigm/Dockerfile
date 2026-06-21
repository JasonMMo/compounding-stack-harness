# deploy/preview/postgres-bigm/Dockerfile
#
# PURPOSE
#   Custom Postgres 16 image with BOTH pgvector AND pg_bigm installed.
#   Replaces pgvector/pgvector:pg16 in legal-rag.compose.yml for Korean
#   bigram FTS support in the preview tier.
#
# WHY SOURCE BUILD
#   No official pre-built image ships pgvector + pg_bigm together.
#   pgvector/pgvector:pg16 already has pgvector compiled in, so we only
#   need to compile pg_bigm on top — avoids rebuilding pgvector from scratch.
#
# PINNED VERSIONS
#   pgvector : inherited from base image (pgvector/pgvector:pg16 — latest stable)
#   pg_bigm  : v1.2-20250903 (latest v1.2 release, stable on PG 16 via PGXS)
#   Source   : https://github.com/pgbigm/pg_bigm/archive/refs/tags/v1.2-20250903.tar.gz
#   NOTE: pg_bigm tags use the form v1.2-YYYYMMDD (NOT semver v1.2.0).
#
# CHECKSUM (SHA-256 of v1.2-20250903.tar.gz — verified against GitHub codeload)
#   4d4fb48161e3f9e99207851299379c83b3e5d1d3c1a07c35f6a3153d577b3142
#   Tag: https://github.com/pgbigm/pg_bigm/releases/tag/v1.2-20250903
#
# BUILD OUTPUT
#   pg_bigm.so, pg_bigm.control, pg_bigm--1.2.sql are installed to the
#   PostgreSQL extension directory by `make USE_PGXS=1 install`.
#   After container starts: CREATE EXTENSION pg_bigm; is available.
#   The actual CREATE EXTENSION call lives in 01_extensions.sql (guarded DO block),
#   so DBA migration runs unchanged — this image just makes it possible.
#
# CACHE NOTE
#   Build deps are removed in the same RUN layer to keep image lean.
#   Docker layer cache means repeat `docker build` skips re-download if
#   the pg_bigm ARGs haven't changed.

FROM pgvector/pgvector:pg16

# -- Pinned pg_bigm version / download coordinates ----------------------------
ARG PGBIGM_VERSION=1.2-20250903
ARG PGBIGM_URL=https://github.com/pgbigm/pg_bigm/archive/refs/tags/v${PGBIGM_VERSION}.tar.gz
ARG PGBIGM_SHA256=4d4fb48161e3f9e99207851299379c83b3e5d1d3c1a07c35f6a3153d577b3142

# -- Build pg_bigm from source (single RUN layer = minimal image delta) -------
RUN set -eux; \
    \
    # 1. Install build-time dependencies only
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        postgresql-server-dev-16 \
        wget \
        ca-certificates; \
    \
    # 2. Download + verify tarball
    wget -qO /tmp/pg_bigm.tar.gz "${PGBIGM_URL}"; \
    echo "${PGBIGM_SHA256}  /tmp/pg_bigm.tar.gz" | sha256sum --check --strict -; \
    \
    # 3. Extract + build + install via PGXS (no pg_config guessing needed)
    tar -xzf /tmp/pg_bigm.tar.gz -C /tmp; \
    cd "/tmp/pg_bigm-${PGBIGM_VERSION}"; \
    make USE_PGXS=1; \
    make USE_PGXS=1 install; \
    \
    # 4. Remove build deps + temp files (keeps image delta small)
    cd /; \
    rm -rf /tmp/pg_bigm.tar.gz "/tmp/pg_bigm-${PGBIGM_VERSION}"; \
    apt-get purge -y --auto-remove \
        build-essential \
        postgresql-server-dev-16 \
        wget; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

# No CMD / ENTRYPOINT override — inherit from pgvector/pgvector:pg16 base
# which inherits from postgres:16 official image (docker-entrypoint.sh).
