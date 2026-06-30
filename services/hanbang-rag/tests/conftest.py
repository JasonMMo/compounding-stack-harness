"""
tests/conftest.py — test-level pytest configuration for hanbang-rag.

Sets environment variable defaults required for modules that
read env vars (config.load() etc.) during test collection or import.
"""
import os
import sys

# Ensure parent (services/hanbang-rag/) is on sys.path for all test files
_PARENT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

# Minimal env var defaults so import of config.py / auth.py doesn't fail
# if tests are run without the full env set.
_DEFAULTS = {
    "HANBANG_RAG_INGEST_ROOT": "/tmp",
    "HANBANG_RAG_JWT_SECRET": "test",
    "HANBANG_RAG_SERVICE_TOKEN": "test",
    "HANBANG_RAG_DB_DSN": "postgresql://u:p@localhost:5432/d",
    "HANBANG_RAG_EMBED_URL": "http://localhost:8080",
}
for _k, _v in _DEFAULTS.items():
    os.environ.setdefault(_k, _v)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "postgres: integration tests requiring a live Postgres instance",
    )


# ── Postgres integration fixtures ─────────────────────────────────────────────

import pytest  # noqa: E402 — must come after env defaults are set above


DUMMY_VEC: list = [0.1] * 768
"""768-dim deterministic stub embedding. Non-zero so cosine similarity is defined."""


def _require_pg_dsn() -> str:
    """Return HANBANG_RAG_DB_DSN_POSTGRES or skip the test if unset."""
    dsn = os.environ.get("HANBANG_RAG_DB_DSN_POSTGRES", "").strip()
    if not dsn:
        pytest.skip(
            "HANBANG_RAG_DB_DSN_POSTGRES not set — postgres integration skipped"
        )
    return dsn


class _StubEmbedClient:
    """Drop-in embed client that never contacts the sidecar."""

    def embed_batch(self, texts: list) -> list:
        return [[0.1] * 768 for _ in texts]

    def embed(self, text: str) -> list:
        return [0.1] * 768


@pytest.fixture
def stub_embed_client():
    """Embed client stub: returns deterministic 768-dim vectors, no HTTP call."""
    return _StubEmbedClient()


@pytest.fixture
async def pg_conn():
    """Function-scoped async fixture: live Postgres connection wrapped in a
    force-rollback transaction so every test leaves the DB pristine.

    Skips automatically when HANBANG_RAG_DB_DSN_POSTGRES is unset or
    psycopg_pool is not installed.
    """
    dsn = _require_pg_dsn()

    try:
        from psycopg_pool import AsyncConnectionPool  # type: ignore[import]
    except ImportError:
        pytest.skip("psycopg_pool not installed")

    pool = AsyncConnectionPool(conninfo=dsn, min_size=1, max_size=2, open=False)
    await pool.open()
    try:
        async with pool.connection() as conn:
            async with conn.transaction(force_rollback=True):
                yield conn
    finally:
        await pool.close()
