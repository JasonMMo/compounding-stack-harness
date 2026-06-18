"""
tests/conftest.py — test-level pytest configuration.

Sets environment variable defaults required for modules that
read env vars (config.load() etc.) during test collection or import.
These are only fallbacks — the pytest CLI command may override them:
  LEGAL_RAG_INGEST_ROOT=/tmp LEGAL_RAG_JWT_SECRET=test ... pytest tests/ -q
"""
import os
import sys

# Ensure parent (services/legal-rag/) is on sys.path for all test files
_PARENT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

# Minimal env var defaults so import of config.py / auth.py doesn't fail
# if tests are run without the full env set.
_DEFAULTS = {
    "LEGAL_RAG_INGEST_ROOT": "/tmp",
    "LEGAL_RAG_JWT_SECRET": "test",
    "LEGAL_RAG_SERVICE_TOKEN": "test",
}
for _k, _v in _DEFAULTS.items():
    os.environ.setdefault(_k, _v)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "postgres: integration tests requiring a live Postgres instance",
    )
