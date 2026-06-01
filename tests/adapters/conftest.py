"""
conftest.py -- Common adapter fixtures (parent of all adapter subdirs).

Provides the base `adapter_base_url` fixture: reads ADAPTER_BASE_URL env var
only (no auto-launch). Adapter-specific conftests (springboot-jakarta/, fastapi/)
override this fixture with auto-launch capability.

Usage (any adapter, already running):
    ADAPTER_BASE_URL=http://localhost:8080 pytest tests/adapters/_shared/ -v
    ADAPTER_BASE_URL=http://localhost:8081 pytest tests/adapters/_shared/ -v

Usage (adapter-specific gate with auto-launch):
    pytest tests/adapters/springboot-jakarta/ -v   # gradlew auto-launch
    pytest tests/adapters/fastapi/ -v              # uvicorn auto-launch
"""

import os
import urllib.request
import pytest


def _health_check(base_url: str, timeout: float = 3.0) -> bool:
    try:
        req = urllib.request.urlopen(f"{base_url}/api/status/health", timeout=timeout)
        return req.status == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def adapter_base_url():
    """
    Yield the base URL of a running backend adapter.
    Reads ADAPTER_BASE_URL env var. No auto-launch.
    Override in adapter-specific conftest for auto-launch.
    """
    explicit = os.environ.get("ADAPTER_BASE_URL", "").strip()
    if not explicit:
        pytest.skip(
            "ADAPTER_BASE_URL not set. Set it to a running adapter URL, "
            "or invoke via an adapter-specific gate dir for auto-launch."
        )

    if not _health_check(explicit):
        pytest.skip(
            f"ADAPTER_BASE_URL={explicit!r} set but /api/status/health did not respond. "
            "Start the adapter and re-run."
        )

    yield explicit
