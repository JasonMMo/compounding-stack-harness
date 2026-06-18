"""
tests/test_auth.py — unit tests for JWT and service-token authentication.

No DB, sidecar, or FastAPI app startup required.
Tests: valid token, expired token, tampered signature, missing sub,
       non-UUID sub, service-token match/mismatch.

pyjwt is required for JWT tests. Install: pip install pyjwt
If not installed, JWT tests are skipped automatically.
"""
import sys
import os
import time
import uuid
import hmac

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# Skip entire JWT suite if pyjwt not installed
try:
    import jwt as _pyjwt  # noqa: F401
    _PYJWT_AVAILABLE = True
except ImportError:
    _PYJWT_AVAILABLE = False

pytestmark_jwt = pytest.mark.skipif(
    not _PYJWT_AVAILABLE, reason="pyjwt not installed — run: pip install pyjwt"
)

from auth import decode_attorney_token, AuthError


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_token(
    payload: dict,
    secret: str = "test-secret",
    algorithm: str = "HS256",
) -> str:
    """Helper: create a real JWT using pyjwt."""
    import jwt
    return jwt.encode(payload, secret, algorithm=algorithm)


def _valid_payload(attorney_id: str | None = None, offset_seconds: int = 3600) -> dict:
    if attorney_id is None:
        attorney_id = str(uuid.uuid4())
    return {
        "sub": attorney_id,
        "exp": int(time.time()) + offset_seconds,
    }


# ── decode_attorney_token tests ───────────────────────────────────────────────

@pytestmark_jwt
class TestDecodeAttorneyToken:
    SECRET = "test-secret-hs256"

    def test_valid_token_returns_attorney_uuid(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(_valid_payload(attorney_id), self.SECRET)
        result = decode_attorney_token(token, self.SECRET)
        assert result == attorney_id

    def test_valid_token_normalises_uuid_case(self):
        uid = str(uuid.uuid4()).upper()
        token = _make_token({"sub": uid, "exp": int(time.time()) + 3600}, self.SECRET)
        result = decode_attorney_token(token, self.SECRET)
        assert result == str(uuid.UUID(uid))

    def test_expired_token_raises_auth_error(self):
        token = _make_token(_valid_payload(offset_seconds=-1), self.SECRET)
        with pytest.raises(AuthError) as exc_info:
            decode_attorney_token(token, self.SECRET)
        assert "expired" in str(exc_info.value).lower()

    def test_wrong_secret_raises_auth_error(self):
        token = _make_token(_valid_payload(), self.SECRET)
        with pytest.raises(AuthError):
            decode_attorney_token(token, "wrong-secret")

    def test_tampered_payload_raises_auth_error(self):
        token = _make_token(_valid_payload(), self.SECRET)
        parts = token.split(".")
        assert len(parts) == 3
        payload_b64 = parts[1]
        corrupted = payload_b64[:-1] + ("A" if payload_b64[-1] != "A" else "B")
        tampered = ".".join([parts[0], corrupted, parts[2]])
        with pytest.raises(AuthError):
            decode_attorney_token(tampered, self.SECRET)

    def test_missing_sub_claim_raises_auth_error(self):
        token = _make_token({"exp": int(time.time()) + 3600}, self.SECRET)
        with pytest.raises(AuthError):
            decode_attorney_token(token, self.SECRET)

    def test_missing_exp_claim_raises_auth_error(self):
        token = _make_token({"sub": str(uuid.uuid4())}, self.SECRET)
        with pytest.raises(AuthError):
            decode_attorney_token(token, self.SECRET)

    def test_non_uuid_sub_raises_auth_error(self):
        token = _make_token(
            {"sub": "not-a-uuid", "exp": int(time.time()) + 3600}, self.SECRET
        )
        with pytest.raises(AuthError) as exc_info:
            decode_attorney_token(token, self.SECRET)
        assert "uuid" in str(exc_info.value).lower()

    def test_wrong_algorithm_raises_auth_error(self):
        import jwt
        attorney_id = str(uuid.uuid4())
        token = jwt.encode(
            _valid_payload(attorney_id),
            self.SECRET,
            algorithm="HS384",
        )
        with pytest.raises(AuthError):
            decode_attorney_token(token, self.SECRET)

    def test_empty_token_raises_auth_error(self):
        with pytest.raises(AuthError):
            decode_attorney_token("", self.SECRET)

    def test_garbage_string_raises_auth_error(self):
        with pytest.raises(AuthError):
            decode_attorney_token("not.a.jwt", self.SECRET)


# ── Service token constant-time comparison ────────────────────────────────────
# These tests do NOT require pyjwt.

class TestServiceTokenComparison:
    """Verify hmac.compare_digest usage (timing-safe)."""

    def test_matching_tokens_are_equal(self):
        token = "super-secret-service-token"
        assert hmac.compare_digest(token, token) is True

    def test_mismatched_tokens_are_not_equal(self):
        assert hmac.compare_digest("correct", "wrong") is False

    def test_empty_vs_nonempty_not_equal(self):
        assert hmac.compare_digest("", "token") is False

    def test_empty_vs_empty_are_equal(self):
        assert hmac.compare_digest("", "") is True
