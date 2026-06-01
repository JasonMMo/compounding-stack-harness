"""
routers/auth.py — auth domain router.

Wire key → HTTP mapping:
  auth.login  → POST /api/auth/login
  auth.logout → POST /api/auth/logout

Demo credentials: username=demo, password=demo (M1 stub, same as springboot adapter).
Tokens stored in module-level dict; invalidated on logout.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

import wire_response

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory token store: token → {user_id, expires_at}
_tokens: dict[str, dict[str, Any]] = {}

_DEMO_USERS = {"demo": "demo"}
_TOKEN_TTL_SECONDS = 86400  # 24 h


# ── auth.login ────────────────────────────────────────────────────────────────

@router.post("/login")
async def login(body: dict[str, Any] | None = None) -> JSONResponse:
    if body is None:
        body = {}

    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        return wire_response.error("BAD_REQUEST", {"reason": "username and password are required"})

    expected = _DEMO_USERS.get(username)
    if expected is None or expected != password:
        return wire_response.error("AUTH_FAILED")

    token = str(uuid.uuid4())
    now = int(time.time())
    expires_at_ts = now + _TOKEN_TTL_SECONDS
    expires_at_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(expires_at_ts))
    user_id = f"user-{username}"

    _tokens[token] = {"user_id": user_id, "expires_at": expires_at_ts}

    return wire_response.ok(
        {
            "token": token,
            "expires_at": expires_at_iso,
            "user_id": user_id,
        }
    )


# ── auth.logout ───────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout(body: dict[str, Any] | None = None) -> JSONResponse:
    if body is None:
        body = {}

    token = body.get("token")
    if not token:
        return wire_response.error("BAD_REQUEST", {"reason": "token is required"})

    # Idempotent: discard the token if present; no error if already gone
    _tokens.pop(token, None)

    return wire_response.ok({"success": True})
