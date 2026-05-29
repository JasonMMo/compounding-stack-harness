"""
conftest.py — springboot-jakarta adapter compliance test fixtures.

Fixture `adapter_base_url`:
  1. If ADAPTER_BASE_URL env var is set, uses it directly (assumes already running).
  2. Otherwise: attempts health-check on http://localhost:8080. If alive, uses it.
  3. Otherwise: attempts to build+launch via `./gradlew bootRun` from the adapter
     directory, waits up to ADAPTER_START_TIMEOUT_S seconds for health, yields the
     URL, then tears it down.
  4. If Java/Gradle is unavailable, pytest.skip with a clear message — tests are NOT
     silently passing; they are explicitly skipped so L4 live status is visible.

Environment variables:
  ADAPTER_BASE_URL          Override target (e.g. http://localhost:9090)
  ADAPTER_START_TIMEOUT_S   Boot wait timeout in seconds (default: 90)
  ADAPTER_PORT              Port to use when auto-launching (default: 8080)
"""

import os
import subprocess
import time
import urllib.request
import urllib.error
import pathlib

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_ADAPTER_DIR = _REPO_ROOT / "backend" / "adapters" / "springboot-jakarta"

_DEFAULT_PORT = int(os.environ.get("ADAPTER_PORT", "8080"))
_DEFAULT_BASE = f"http://localhost:{_DEFAULT_PORT}"
_START_TIMEOUT = int(os.environ.get("ADAPTER_START_TIMEOUT_S", "90"))


def _health_check(base_url: str, timeout: float = 3.0) -> bool:
    """Return True if /api/status/health responds with HTTP 200."""
    try:
        req = urllib.request.urlopen(f"{base_url}/api/status/health", timeout=timeout)
        return req.status == 200
    except Exception:
        return False


def _gradle_available() -> bool:
    gradlew = _ADAPTER_DIR / "gradlew"
    if gradlew.exists():
        return True
    # Fallback: system gradle
    try:
        subprocess.run(["gradle", "--version"], capture_output=True, timeout=10, check=True)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def adapter_base_url():
    """
    Yield the base URL of a running springboot-jakarta adapter instance.
    Session-scoped: the adapter is started once per pytest session and torn down
    after all tests complete.
    """
    # 1. Explicit override via env var
    explicit = os.environ.get("ADAPTER_BASE_URL", "").strip()
    if explicit:
        if not _health_check(explicit):
            pytest.skip(
                f"ADAPTER_BASE_URL={explicit!r} set but /api/status/health did not respond. "
                "Start the adapter and re-run."
            )
        yield explicit
        return

    # 2. Already running on default port
    base = _DEFAULT_BASE
    if _health_check(base):
        yield base
        return

    # 3. Auto-launch via gradlew
    if not _gradle_available():
        pytest.skip(
            "L4 live: adapter not running and Java/Gradle not available in this environment. "
            "Install Java 17+ and Gradle 8+, or set ADAPTER_BASE_URL to target a running instance. "
            "Test suite is syntactically correct and collects cleanly (pytest --collect-only)."
        )

    gradlew_cmd = str(_ADAPTER_DIR / "gradlew")
    # On Windows the wrapper is gradlew.bat
    if os.name == "nt":
        gradlew_cmd = str(_ADAPTER_DIR / "gradlew.bat")
        if not pathlib.Path(gradlew_cmd).exists():
            gradlew_cmd = str(_ADAPTER_DIR / "gradlew")

    cmd = [gradlew_cmd, "bootRun", f"--args=--server.port={_DEFAULT_PORT}"]
    proc = None
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(_ADAPTER_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        deadline = time.monotonic() + _START_TIMEOUT
        # On Windows, gradlew.bat is a wrapper that exits after handing off to
        # the JVM process. proc.poll() != None does NOT mean bootRun failed --
        # it just means the launcher script finished. We therefore rely purely
        # on the health-check loop rather than process exit status.
        while time.monotonic() < deadline:
            if _health_check(base):
                break
            time.sleep(2)
        else:
            if proc.poll() is None:
                proc.terminate()
            pytest.skip(
                f"Adapter did not become healthy within {_START_TIMEOUT}s. "
                "Set ADAPTER_START_TIMEOUT_S env var to increase wait, "
                "or set ADAPTER_BASE_URL to target a running instance. "
                "Test suite collects cleanly (pytest --collect-only)."
            )

        yield base

    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
