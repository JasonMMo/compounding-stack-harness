"""
auth.py — JWT bearer authentication + service-token validation.

B-1 SECURITY CONTRACT:
  /search: user identity comes from JWT `sub` claim (Bearer token).
           Body-supplied user_id is IGNORED — only token claim used for RLS.
  /ingest: validated by X-Service-Token header == HANBANG_RAG_SERVICE_TOKEN env var.

JWT spec:
  Algorithm : HS256
  Secret    : env HANBANG_RAG_JWT_SECRET (required, service refuses to start if unset)
  Claims    : `sub` (str, UUID of user) — used as app.current_user_id for RLS
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

def mint_token(user_id: str, secret: str, ttl_seconds: int = 28800) -> str:
    """Create a HS256 JWT for the given user UUID.

    Args:
        user_id:      UUID string of the user (stored in `sub` claim).
        secret:       HS256 signing secret (from settings.jwt_secret).
        ttl_seconds:  Token lifetime in seconds (default 8 hours = 28800).

    Returns:
        Signed JWT string, ready to send in Authorization: Bearer <token>.

    Raises:
        ImportError: pyjwt not installed.
        ValueError:  user_id is not a valid UUID.
    """
    try:
        import jwt  # pyjwt — lazy import for mockability in unit tests
    except ImportError as exc:
        raise ImportError(
            "pyjwt is required for JWT auth. Install: pip install pyjwt"
        ) from exc

    # Validate UUID before signing — sub must be a canonical UUID string
    try:
        canonical_id = str(uuid.UUID(str(user_id)))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"user_id is not a valid UUID: {user_id!r}") from exc

    payload = {
        "sub": canonical_id,
        "exp": int(time.time()) + ttl_seconds,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_user_token(token: str, secret: str) -> str:
    """Decode and validate a HS256 JWT, return user UUID (sub claim).

    Args:
        token:  Raw JWT string (without 'Bearer ' prefix).
        secret: HS256 signing secret (from settings.jwt_secret).

    Returns:
        Canonical UUID string of the user (from `sub` claim).

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
        user_id = str(uuid.UUID(str(sub)))
    except (ValueError, AttributeError) as exc:
        raise AuthError(
            f"Token `sub` claim is not a valid UUID: {sub!r}"
        ) from exc

    return user_id


# ── FastAPI Dependencies ──────────────────────────────────────────────────────

def make_user_dep(get_settings_fn):
    """Factory: returns a FastAPI dependency that validates JWT and extracts user_id.

    Args:
        get_settings_fn: callable returning config.Settings (injected at app level).

    Returns:
        FastAPI Depends-compatible async function.
    """
    async def _user_dep(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Security(_bearer_scheme),
        ] = None,
    ) -> str:
        """Extract and validate user UUID from Bearer JWT.

        Returns:
            Canonical user UUID string for use in rls_session().

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
            user_id = decode_user_token(
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

        logger.debug("JWT validated for user_id=%s", user_id)
        return user_id

    return _user_dep


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
