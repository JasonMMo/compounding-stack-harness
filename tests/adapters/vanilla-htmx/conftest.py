"""
conftest.py — vanilla-htmx frontend adapter compliance test fixtures.

Primary mode: in-process Flask test client (no live servers required).
  - `flask_client` fixture: creates the Flask app with _proxy_request mocked.
  - `contract_loader_fixture`: loads ContractLoader from repo middle/contract/.
  - `error_codes`: dict of all codes from codes.yaml (single-source — tests never
    hardcode message_ko or http_status).

L4 live mode (optional): set FRONTEND_BASE_URL env var to a running vanilla-htmx
instance. The `frontend_base_url` fixture handles skip logic identical to
Growth-7's springboot-jakarta conftest pattern.

Environment variables:
  FRONTEND_BASE_URL    Override for L4 live tests (e.g. http://localhost:5000)
  BACKEND_BASE_URL     Used by L4 live tests when checking proxy pass-through
  FRONTEND_PORT        Port to check when probing (default: 5000)
"""

import os
import pathlib
import sys
import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Path setup — make the adapter package importable from any cwd
# ---------------------------------------------------------------------------

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_ADAPTER_ROOT = _REPO_ROOT / "frontend" / "adapters" / "vanilla-htmx"

# Insert adapter root so `import server` and `import contract_loader` work
if str(_ADAPTER_ROOT) not in sys.path:
    sys.path.insert(0, str(_ADAPTER_ROOT))

# Set CONTRACT_DIR so ContractLoader resolves correctly when imported from
# this test directory (auto-detect walk may not reach repo root otherwise)
os.environ.setdefault(
    "CONTRACT_DIR",
    str(_REPO_ROOT / "middle" / "contract"),
)

# ---------------------------------------------------------------------------
# ContractLoader + error_codes (single-source — no hardcoded strings in tests)
# ---------------------------------------------------------------------------

from contract_loader import ContractLoader  # noqa: E402 — after path setup


@pytest.fixture(scope="session")
def contract_loader_fixture() -> ContractLoader:
    """Session-scoped ContractLoader — expensive to build, safe to share."""
    return ContractLoader()


@pytest.fixture(scope="session")
def error_codes(contract_loader_fixture) -> dict:
    """
    Full codes dict from codes.yaml.
    Tests parameterise over this — never hardcode code strings or message_ko.
    """
    return contract_loader_fixture.codes()


# ---------------------------------------------------------------------------
# Flask test client (in-process, mocked _proxy_request)
# ---------------------------------------------------------------------------

@pytest.fixture()
def flask_client(monkeypatch):
    """
    Returns Flask test client with:
      - A session token pre-injected (bypasses _require_login).
      - _proxy_request NOT yet mocked — individual tests patch it as needed.

    Isolation: each test gets a fresh app context. No shared state between tests
    (Growth-7 lesson: autouse fixtures that accumulate state cause false PASSes).
    """
    # Avoid the singleton loader being stale; force CONTRACT_DIR
    os.environ["CONTRACT_DIR"] = str(_REPO_ROOT / "middle" / "contract")

    import importlib
    import server as srv_module

    # Reload to get a clean app instance (prevents inter-test contamination)
    importlib.reload(srv_module)
    app = srv_module.app
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.test_request_context():
            pass
        # Inject a session token so _require_login passes
        with client.session_transaction() as sess:
            sess["token"] = "test-token"
        yield client, srv_module


# ---------------------------------------------------------------------------
# L4 live: frontend_base_url (optional, skip if not running)
# ---------------------------------------------------------------------------

_DEFAULT_FRONTEND_PORT = int(os.environ.get("FRONTEND_PORT", "5000"))
_DEFAULT_FRONTEND_BASE = f"http://localhost:{_DEFAULT_FRONTEND_PORT}"


def _frontend_health_check(base_url: str, timeout: float = 3.0) -> bool:
    try:
        resp = urllib.request.urlopen(f"{base_url}/health", timeout=timeout)
        return resp.status == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def frontend_base_url():
    """
    Yield the base URL of a running vanilla-htmx adapter for L4 live tests.
    Skips (explicit skip, not silent pass) if no adapter is reachable.
    """
    explicit = os.environ.get("FRONTEND_BASE_URL", "").strip()
    if explicit:
        if not _frontend_health_check(explicit):
            pytest.skip(
                f"FRONTEND_BASE_URL={explicit!r} set but /health did not respond. "
                "Start the frontend adapter and re-run."
            )
        yield explicit
        return

    if _frontend_health_check(_DEFAULT_FRONTEND_BASE):
        yield _DEFAULT_FRONTEND_BASE
        return

    pytest.skip(
        "L4 live: vanilla-htmx adapter not running. "
        "Start with `python server.py` from frontend/adapters/vanilla-htmx/ "
        "or set FRONTEND_BASE_URL. "
        "In-process suite (F-1~F-4) runs without a live server."
    )
