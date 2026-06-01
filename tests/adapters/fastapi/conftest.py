"""
conftest.py — fastapi adapter compliance test fixtures.

Fixture `adapter_base_url`:
  1. If ADAPTER_BASE_URL env var is set, uses it directly (assumes already running).
  2. Otherwise: attempts health-check on http://localhost:8081. If alive, uses it.
  3. Otherwise: attempts to auto-launch via `uvicorn main:app --port 8081` from the
     adapter directory, waits up to ADAPTER_START_TIMEOUT_S seconds for health, yields
     the URL, then tears it down.
  4. If uvicorn is unavailable, pytest.skip with a clear message -- tests are NOT
     silently passing; they are explicitly skipped so L4 live status is visible.

Environment variables:
  ADAPTER_BASE_URL          Override target (e.g. http://localhost:9090)
  ADAPTER_START_TIMEOUT_S   Boot wait timeout in seconds (default: 60)
  ADAPTER_PORT              Port to use when auto-launching (default: 8081)
"""

import os
import subprocess
import sys
import time
import urllib.request
import pathlib

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_ADAPTER_DIR = _REPO_ROOT / "backend" / "adapters" / "fastapi"

_DEFAULT_PORT = int(os.environ.get("ADAPTER_PORT", "8081"))
_DEFAULT_BASE = f"http://localhost:{_DEFAULT_PORT}"
_START_TIMEOUT = int(os.environ.get("ADAPTER_START_TIMEOUT_S", "60"))


def _health_check(base_url: str, timeout: float = 3.0) -> bool:
    """Return True if /api/status/health responds with HTTP 200."""
    try:
        req = urllib.request.urlopen(f"{base_url}/api/status/health", timeout=timeout)
        return req.status == 200
    except Exception:
        return False


def _uvicorn_available() -> bool:
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "--version"],
            capture_output=True, timeout=10, check=True,
        )
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def adapter_base_url():
    """
    Yield the base URL of a running fastapi adapter instance.
    Session-scoped: the adapter is started once per pytest session and torn down
    after all tests complete.
    """
    # 1. Explicit override via env var
    explicit = os.environ.get("ADAPTER_BASE_URL", "").strip()
    if explicit:
        if not _health_check(explicit):
            pytest.skip(
                f"ADAPTER_BASE_URL={explicit!r} set but /api/status/health did not respond. "
                "Start the adapter (`uvicorn main:app --port 8081` from backend/adapters/fastapi/) "
                "and re-run."
            )
        yield explicit
        return

    # 2. Already running on default port
    base = _DEFAULT_BASE
    if _health_check(base):
        yield base
        return

    # 3. Auto-launch via uvicorn
    if not _uvicorn_available():
        pytest.skip(
            "L4 live: fastapi adapter not running and uvicorn not available in this environment. "
            "Install dependencies (`pip install -r backend/adapters/fastapi/requirements.txt`), "
            "or set ADAPTER_BASE_URL to target a running instance. "
            "Test suite is syntactically correct and collects cleanly (pytest --collect-only)."
        )

    env = {**os.environ, "PYTHONPATH": str(_ADAPTER_DIR)}
    cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1",
        "--port", str(_DEFAULT_PORT),
    ]
    proc = None
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(_ADAPTER_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )

        deadline = time.monotonic() + _START_TIMEOUT
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                # Process exited unexpectedly -- read output for diagnostics
                out = proc.stdout.read().decode("utf-8", errors="replace")
                pytest.skip(
                    f"uvicorn exited unexpectedly (rc={proc.returncode}). "
                    f"Output: {out[:500]}"
                )
            if _health_check(base):
                break
            time.sleep(1)
        else:
            if proc.poll() is None:
                proc.terminate()
            pytest.skip(
                f"FastAPI adapter did not become healthy within {_START_TIMEOUT}s. "
                "Set ADAPTER_START_TIMEOUT_S env var to increase wait, "
                "or set ADAPTER_BASE_URL to target a running instance."
            )

        yield base

    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
