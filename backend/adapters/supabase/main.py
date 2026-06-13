"""
main.py — Supabase backend adapter entrypoint.

Serves all wire keys from middle/contract/wire-v1.yaml via shared FastAPI
routers from the fastapi adapter, with the only swap being the store module.

Seam mechanism (zero-touch on fastapi adapter):
    1. Import supabase_store (our PostgREST-backed store).
    2. Inject it as sys.modules["store"] BEFORE importing shared routers.
    3. Append the fastapi adapter dir to sys.path so shared routers resolve.
    4. Import routers — their `from store import entity_store` resolves to ours.

Routers included: auth, entity, status.
NOT included: legal (domain-specific to the fastapi demo set — not part of the
wire-v1.yaml contract; excluded per CTO spec).

Open loops:
    - Supabase Auth (GoTrue) integration deferred. Currently reuses demo auth
      from shared routers/auth.py (in-memory demo/demo). Real auth requires
      JWT from GoTrue + per-user RLS policies.
    - L4 live tests not run (no Supabase project configured in CI). Run
      manually with SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY set.

Launch:
    uvicorn main:app --port 8081

Port is env-configurable:
    PORT=9090 uvicorn main:app --port 9090

Default port: 8081 (matches fastapi adapter convention; Growth-7 port-conflict
lesson: springboot-jakarta uses 8080 → use 8081 for Python adapters).
"""

from __future__ import annotations

import os
import pathlib
import sys

# ── env loading ───────────────────────────────────────────────────────────────
# Load .env before any module-level env-var reads (SUPABASE_URL etc.).
try:
    from dotenv import load_dotenv
    _REPO_ROOT_ENV = pathlib.Path(__file__).resolve().parents[3]
    load_dotenv(dotenv_path=_REPO_ROOT_ENV / ".env", override=False)
except ImportError:
    pass

# ── seam: inject supabase_store as the canonical "store" module ───────────────
# This MUST happen before any shared router imports so that
# `from store import entity_store` in entity.py resolves to supabase_store.
import supabase_store  # noqa: E402  (local module in this adapter dir)
sys.modules["store"] = supabase_store  # type: ignore[assignment]

# ── extend sys.path for shared fastapi adapter modules ────────────────────────
# Shared: wire_response, catalog_validator, contract_loader, routers/*
_FASTAPI_DIR = pathlib.Path(__file__).resolve().parent.parent / "fastapi"
sys.path.insert(0, str(_FASTAPI_DIR))

# ── import shared routers (resolve store via sys.modules["store"] above) ──────
from routers import auth, entity, status  # noqa: E402

from fastapi import FastAPI  # noqa: E402

# ── FastAPI application ───────────────────────────────────────────────────────
app = FastAPI(
    title="compounding-stack backend adapter — supabase",
    description=(
        "Supabase/PostgREST implementation of the middle/contract/wire-v1.yaml "
        "wire protocol. Swap-compatible with fastapi and springboot-jakarta "
        "adapters via customer profile stack.backend: supabase."
    ),
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(entity.router)
app.include_router(status.router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8081"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
