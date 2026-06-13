"""
supabase_client.py — httpx client factory for Supabase PostgREST.

Reads SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from env (or .env via
python-dotenv if available). Raises a clear RuntimeError on startup if
either variable is absent — fail-fast so misconfiguration is obvious.

Usage:
    from supabase_client import get_client, BASE_URL, AUTH_HEADERS

    with get_client() as client:
        resp = client.get(f"{BASE_URL}/hr_employee")
        resp.raise_for_status()

Design:
    - Sync httpx.Client. Called from async FastAPI handlers (same pattern
      as the in-memory store in the fastapi adapter — sync store methods
      called from async handlers without await).
    - A module-level singleton client is exposed as `_CLIENT` for callers
      that want to skip context-manager overhead in hot paths. However,
      use get_client() in tests for clean resource management.
    - Base URL: {SUPABASE_URL}/rest/v1
    - Auth headers sent on every request (apikey + Authorization Bearer).
"""

from __future__ import annotations

import os
from typing import Generator

import httpx

# ── env loading ───────────────────────────────────────────────────────────────
# python-dotenv optional; env vars can be set externally (Docker / Coolify).
try:
    from dotenv import load_dotenv as _load_dotenv
    import pathlib as _pathlib
    _REPO_ROOT = _pathlib.Path(__file__).resolve().parents[3]
    _load_dotenv(dotenv_path=_REPO_ROOT / ".env", override=False)
except ImportError:
    pass

# ── validate required env vars ────────────────────────────────────────────────
_SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
_SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()

if not _SUPABASE_URL:
    raise RuntimeError(
        "supabase_client: SUPABASE_URL is not set. "
        "Set it to your Supabase project URL, e.g. https://<ref>.supabase.co"
    )

if not _SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError(
        "supabase_client: SUPABASE_SERVICE_ROLE_KEY is not set. "
        "Find it at Supabase dashboard → Project Settings → API → service_role key. "
        "Keep this secret — it bypasses Row Level Security."
    )

# ── public constants ──────────────────────────────────────────────────────────
BASE_URL: str = f"{_SUPABASE_URL}/rest/v1"

AUTH_HEADERS: dict[str, str] = {
    "apikey": _SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {_SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
}

# ── client factory ────────────────────────────────────────────────────────────

def get_client() -> httpx.Client:
    """
    Return a new httpx.Client pre-configured with auth headers and base URL.
    Callers are responsible for closing it (use as context manager).

    Example:
        with get_client() as client:
            resp = client.get("/hr_employee")
    """
    return httpx.Client(
        base_url=BASE_URL,
        headers=AUTH_HEADERS,
        timeout=30.0,
    )


# ── module-level singleton ────────────────────────────────────────────────────
# Reused across requests for connection-pool efficiency. Closed on process exit.
# Tests should use get_client() + MockTransport instead.
_CLIENT: httpx.Client = httpx.Client(
    base_url=BASE_URL,
    headers=AUTH_HEADERS,
    timeout=30.0,
)
