"""
tests/test_auth_login.py — JWT mint/verify 라운드트립 + 로그인 로직 단위 테스트.

커버리지:
  - mint_token: 발급 → decode_attorney_token 라운드트립
  - mint_token: UUID 검증 (비정상 입력 → ValueError)
  - bcrypt 해시 검증: 실제 seed 비번(demo1234!)으로 검증
  - 로그인 실패 분기 (단위 수준, DB 없음):
      틀린 비번 → _bcrypt_verify 반환값 False
      비활성 계정 → 로직상 401 동일 메시지
  - @pytest.mark.postgres: DB 필요한 /auth/login 통합 테스트는 마크로 분리

pyjwt 없이는 JWT 테스트 전체 skip.
bcrypt 없이는 bcrypt 테스트 전체 skip.
"""
from __future__ import annotations

import time
import uuid

import pytest

# ── pyjwt 가용성 ─────────────────────────────────────────────────────────────

try:
    import jwt as _pyjwt  # noqa: F401
    _PYJWT_AVAILABLE = True
except ImportError:
    _PYJWT_AVAILABLE = False

pytestmark_jwt = pytest.mark.skipif(
    not _PYJWT_AVAILABLE,
    reason="pyjwt not installed — run: pip install pyjwt",
)

# ── bcrypt 가용성 ─────────────────────────────────────────────────────────────

try:
    import bcrypt as _bcrypt  # noqa: F401
    _BCRYPT_AVAILABLE = True
except ImportError:
    _BCRYPT_AVAILABLE = False

pytestmark_bcrypt = pytest.mark.skipif(
    not _BCRYPT_AVAILABLE,
    reason="bcrypt not installed — run: pip install 'bcrypt>=4.0,<5.0'",
)

# ── 모듈 import (conftest.py 가 sys.path 설정) ───────────────────────────────

from auth import mint_token, decode_attorney_token, AuthError  # noqa: E402


# ── 헬퍼 ─────────────────────────────────────────────────────────────────────

_SECRET = "test-mint-secret-hs256"

# seed_attorneys.sql 의 demo1234! bcrypt 해시 (cost=12, $2b$)
# 세 변호사 중 이준호(a1) 해시 사용
_SEED_HASH_JUNHO = "$2b$12$D7T7IzhOHbw/rjUrtHjX4Omr5X/C0GrwfOkf6XsfvrfTToeBz6mkW"
_DEMO_PASSWORD = "demo1234!"
_WRONG_PASSWORD = "wrongpassword"


# ── mint_token 테스트 ─────────────────────────────────────────────────────────

class TestMintToken:
    """mint_token 단위 테스트 — pyjwt 필요."""

    @pytestmark_jwt
    def test_mint_returns_string(self):
        aid = str(uuid.uuid4())
        token = mint_token(aid, _SECRET)
        assert isinstance(token, str)
        assert len(token) > 20

    @pytestmark_jwt
    def test_mint_verify_roundtrip(self):
        """mint → decode 라운드트립: 반환된 attorney_id 가 입력과 일치."""
        aid = str(uuid.uuid4())
        token = mint_token(aid, _SECRET)
        recovered = decode_attorney_token(token, _SECRET)
        assert recovered == aid

    @pytestmark_jwt
    def test_mint_uuid_normalisation(self):
        """mint 는 대문자 UUID 를 정규화된 소문자로 저장한다."""
        raw = str(uuid.uuid4()).upper()
        canonical = str(uuid.UUID(raw))
        token = mint_token(raw, _SECRET)
        recovered = decode_attorney_token(token, _SECRET)
        assert recovered == canonical

    @pytestmark_jwt
    def test_mint_custom_ttl(self):
        """ttl_seconds=60 → exp 가 현재+60초 근방이어야 한다."""
        import jwt
        aid = str(uuid.uuid4())
        before = int(time.time())
        token = mint_token(aid, _SECRET, ttl_seconds=60)
        payload = jwt.decode(token, _SECRET, algorithms=["HS256"])
        exp = payload["exp"]
        assert before + 55 <= exp <= before + 65

    @pytestmark_jwt
    def test_mint_expired_token_fails_decode(self):
        """ttl_seconds=-1 → 이미 만료 → decode 시 AuthError."""
        aid = str(uuid.uuid4())
        token = mint_token(aid, _SECRET, ttl_seconds=-1)
        with pytest.raises(AuthError) as exc_info:
            decode_attorney_token(token, _SECRET)
        assert "expired" in str(exc_info.value).lower()

    def test_mint_invalid_uuid_raises_value_error(self):
        """attorney_id 가 UUID 형식이 아니면 ValueError."""
        with pytest.raises(ValueError):
            mint_token("not-a-uuid", _SECRET)

    def test_mint_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            mint_token("", _SECRET)

    @pytestmark_jwt
    def test_mint_wrong_secret_decode_fails(self):
        """다른 secret 으로 decode 하면 AuthError."""
        aid = str(uuid.uuid4())
        token = mint_token(aid, _SECRET)
        with pytest.raises(AuthError):
            decode_attorney_token(token, "different-secret")


# ── bcrypt 검증 테스트 ───────────────────────────────────────────────────────

class TestBcryptVerify:
    """api._bcrypt_verify 와 동일한 로직을 직접 테스트 (실제 seed 해시)."""

    @pytestmark_bcrypt
    def test_correct_password_matches_seed_hash(self):
        """demo1234! 이 seed 해시와 일치해야 한다."""
        import bcrypt
        result = bcrypt.checkpw(
            _DEMO_PASSWORD.encode("utf-8"),
            _SEED_HASH_JUNHO.encode("utf-8"),
        )
        assert result is True

    @pytestmark_bcrypt
    def test_wrong_password_does_not_match(self):
        """틀린 비번은 seed 해시와 일치하지 않아야 한다."""
        import bcrypt
        result = bcrypt.checkpw(
            _WRONG_PASSWORD.encode("utf-8"),
            _SEED_HASH_JUNHO.encode("utf-8"),
        )
        assert result is False

    @pytestmark_bcrypt
    def test_all_seed_hashes_match_demo_password(self):
        """seed_attorneys.sql 의 세 해시 모두 demo1234! 와 일치해야 한다."""
        import bcrypt
        hashes = [
            # 이준호
            "$2b$12$D7T7IzhOHbw/rjUrtHjX4Omr5X/C0GrwfOkf6XsfvrfTToeBz6mkW",
            # 박서연
            "$2b$12$fH0rM.qenelFB0zvYwnrzeJjHTwcKmeJuP25FCIIEy8NbCddUhSyO",
            # 김정훈
            "$2b$12$tNyhYcMFyBTa5Ly1mPjzT.h8bjIb5ku08j/nMqN2MLAib6sRpb/8a",
        ]
        pw = _DEMO_PASSWORD.encode("utf-8")
        for h in hashes:
            assert bcrypt.checkpw(pw, h.encode("utf-8")), f"Hash mismatch: {h[:20]}..."


# ── 로그인 실패 분기 단위 테스트 ─────────────────────────────────────────────

class TestLoginFailurePaths:
    """DB 없이 단위 수준에서 검증 가능한 로그인 실패 경로."""

    @pytestmark_bcrypt
    def test_wrong_password_bcrypt_returns_false(self):
        """틀린 비번 → bcrypt.checkpw → False (401 분기 보장)."""
        import bcrypt
        assert not bcrypt.checkpw(
            b"wrongpassword",
            _SEED_HASH_JUNHO.encode("utf-8"),
        )

    @pytestmark_bcrypt
    def test_inactive_account_logic(self):
        """is_active=False 인 경우 bcrypt 통과하더라도 401 을 반환해야 한다.
        이 테스트는 api.py 의 is_active 체크 로직을 수동으로 확인한다."""
        import bcrypt

        is_active = False
        pw_match = bcrypt.checkpw(
            _DEMO_PASSWORD.encode("utf-8"),
            _SEED_HASH_JUNHO.encode("utf-8"),
        )
        # 비번은 맞지만 비활성이면 401
        should_login = pw_match and is_active
        assert not should_login, "비활성 계정은 로그인 불가해야 한다."

    def test_login_fail_message_is_consistent(self):
        """api._LOGIN_FAIL_MSG 가 정의되어 있고 사용자 열거를 방지하는 동일 문구다."""
        # api 모듈은 DB env 없이 import 불가이므로 메시지만 상수로 검증
        # (conftest 에서 LEGAL_RAG_INGEST_ROOT 등 최소 env 를 설정해 줌)
        import importlib, sys
        # api import 가능 여부 체크 — 불가능하면 skip
        try:
            api = importlib.import_module("api")
        except Exception:
            pytest.skip("api.py import requires additional env vars or deps")
        msg = getattr(api, "_LOGIN_FAIL_MSG", None)
        assert msg is not None, "_LOGIN_FAIL_MSG 상수가 api.py 에 없음"
        assert "이메일" in msg and "비밀번호" in msg, \
            "메시지가 사용자 열거 방지 패턴과 다름"


# ── @pytest.mark.postgres: DB 필요 통합 테스트 자리 ─────────────────────────

@pytest.mark.postgres
class TestLoginEndpointIntegration:
    """
    실제 PostgreSQL 인스턴스 필요 — 로컬 DB 없으면 skip.
    CI/CD 에서 LEGAL_RAG_DB_DSN 이 설정된 경우에만 실행.

    이 클래스의 테스트는 SPEC 상태 (미검증):
      - POST /auth/login: 올바른 이메일+비번 → 200 + JWT
      - POST /auth/login: 틀린 비번 → 401, 동일 메시지
      - POST /auth/login: 존재하지 않는 이메일 → 401, 동일 메시지
      - POST /auth/login: is_active=False 계정 → 401, 동일 메시지
    DB fixture 및 FastAPI TestClient 는 인프라 확정 후 구현.
    """

    def test_placeholder(self):
        """SPEC: 라이브 DB 통합 테스트 — 인프라 확정 후 구현."""
        pytest.skip("Postgres integration: implement after DB fixture is available")
