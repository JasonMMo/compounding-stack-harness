"""
auth.py — JWT bearer authentication + service-token validation.

B-1 SECURITY CONTRACT:
  /search: attorney identity comes from JWT `sub` claim (Bearer token).
           Body-supplied attorney_id is IGNORED — only token claim used for RLS.
  /ingest: validated by X-Service-Token header == LEGAL_RAG_SERVICE_TOKEN env var.

JWT spec:
  Algorithm : HS256
  Secret    : env LEGAL_RAG_JWT_SECRET (required, service refuses to start if unset)
  Claims    : `sub` (str, UUID of attorney) — used as app.current_user_id for RLS
              `exp` (int, Unix timestamp) — validated automatically by pyjwt
  Header    : Authorization: Bearer <token>

No cloud key fetch. Symmetric HS256 only (self-host constraint).
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Annotated

from fastapi import HTTPException, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


class AuthError(Exception):
    """Internal auth failure — caller converts to HTTPException."""


# ── JWT ───────────────────────────────────────────────────────────────────────

def mint_token(attorney_id: str, secret: str, ttl_seconds: int = 28800) -> str:
    """Create a HS256 JWT for the given attorney UUID.

    Args:
        attorney_id:  UUID string of the attorney (stored in `sub` claim).
        secret:       HS256 signing secret (from settings.jwt_secret).
        ttl_seconds:  Token lifetime in seconds (default 8 hours = 28800).

    Returns:
        Signed JWT string, ready to send in Authorization: Bearer <token>.

    Raises:
        ImportError: pyjwt not installed.
        ValueError:  attorney_id is not a valid UUID.
    """
    try:
        import jwt  # pyjwt — lazy import for mockability in unit tests
    except ImportError as exc:
        raise ImportError(
            "pyjwt is required for JWT auth. Install: pip install pyjwt"
        ) from exc

    # Validate UUID before signing — sub must be a canonical UUID string
    try:
        canonical_id = str(uuid.UUID(str(attorney_id)))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"attorney_id is not a valid UUID: {attorney_id!r}") from exc

    payload = {
        "sub": canonical_id,
        "exp": int(time.time()) + ttl_seconds,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_attorney_token(token: str, secret: str) -> str:
    """Decode and validate a HS256 JWT, return attorney UUID (sub claim).

    Args:
        token:  Raw JWT string (without 'Bearer ' prefix).
        secret: HS256 signing secret (from settings.jwt_secret).

    Returns:
        Canonical UUID string of the attorney (from `sub` claim).

    Raises:
        AuthError: token is expired, tampered, missing sub, or sub is not a UUID.
    """
    try:
        import jwt  # pyjwt — lazy import for mockability in unit tests
    except ImportError as exc:
        raise ImportError(
            "pyjwt is required for JWT auth. Install: pip install pyjwt"
        ) from exc

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"require": ["sub", "exp"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError(f"Invalid token: {exc}") from exc

    sub = payload.get("sub", "")
    try:
        attorney_id = str(uuid.UUID(str(sub)))
    except (ValueError, AttributeError) as exc:
        raise AuthError(
            f"Token `sub` claim is not a valid UUID: {sub!r}"
        ) from exc

    return attorney_id


# ── FastAPI Dependencies ──────────────────────────────────────────────────────

def make_attorney_dep(get_settings_fn):
    """Factory: returns a FastAPI dependency that validates JWT and extracts attorney_id.

    Separated from get_settings to allow unit-testing without app state.

    Args:
        get_settings_fn: callable returning config.Settings (injected at app level).

    Returns:
        FastAPI Depends-compatible async function.
    """
    async def _attorney_dep(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Security(_bearer_scheme),
        ] = None,
    ) -> str:
        """Extract and validate attorney UUID from Bearer JWT.

        Returns:
            Canonical attorney UUID string for use in rls_session().

        Raises:
            HTTPException 401: missing or invalid Authorization header.
            HTTPException 401: expired token.
            HTTPException 403: sub claim is not a valid UUID.
        """
        if credentials is None or not credentials.credentials:
            raise HTTPException(
                status_code=401,
                detail="Authorization: Bearer <token> header is required.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        settings = get_settings_fn()
        try:
            attorney_id = decode_attorney_token(
                credentials.credentials, settings.jwt_secret
            )
        except AuthError as exc:
            msg = str(exc)
            # Expired → 401, UUID issue → 403, others → 401
            if "UUID" in msg:
                raise HTTPException(status_code=403, detail=msg) from exc
            raise HTTPException(
                status_code=401,
                detail=msg,
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        logger.debug("JWT validated for attorney_id=%s", attorney_id)
        return attorney_id

    return _attorney_dep


def make_service_token_dep(get_settings_fn):
    """Factory: returns a FastAPI dependency that validates X-Service-Token header.

    Args:
        get_settings_fn: callable returning config.Settings.

    Returns:
        FastAPI Depends-compatible async function.
    """
    async def _service_token_dep(
        x_service_token: Annotated[str | None, Header(alias="x-service-token")] = None,
    ) -> None:
        """Validate X-Service-Token header for /ingest endpoint.

        Raises:
            HTTPException 401: header missing or token mismatch.
        """
        if not x_service_token:
            raise HTTPException(
                status_code=401,
                detail="X-Service-Token header is required for /ingest.",
            )

        settings = get_settings_fn()
        # Constant-time comparison via hmac.compare_digest to resist timing attacks
        import hmac
        if not hmac.compare_digest(x_service_token, settings.service_token):
            raise HTTPException(
                status_code=401,
                detail="X-Service-Token is invalid.",
            )

    return _service_token_dep
