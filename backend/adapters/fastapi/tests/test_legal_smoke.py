"""
test_legal_smoke.py — L1 smoke tests for the legal precedent search router.

Tests the router in isolation using FastAPI TestClient.
No real PostgreSQL required: DATABASE_URL is intentionally unset so the
router falls back to the no-DB path and returns an empty result with a warning.

Run:
    cd backend/adapters/fastapi
    pytest tests/test_legal_smoke.py -v
"""

from __future__ import annotations

import os
import sys
import pathlib

# Add adapter root so imports resolve without installation
_ADAPTER_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ADAPTER_DIR))

# Ensure DATABASE_URL is absent so legal router takes the no-DB fallback path
os.environ.pop("DATABASE_URL", None)

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestLegalPrecedentSearch:
    def test_empty_query_returns_empty_list(self):
        """Empty q param → 200 with items=[]."""
        resp = client.get("/api/legal/precedents/search", params={"q": ""})
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_no_db_returns_empty_with_warning(self):
        """When DATABASE_URL is absent, router returns empty list + warning (not 5xx)."""
        resp = client.get("/api/legal/precedents/search", params={"q": "손해배상"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["items"], list)
        assert data["total"] == 0
        assert "warning" in data

    def test_case_type_filter_accepted(self):
        """case_type query param is accepted; no-DB path still returns 200."""
        resp = client.get(
            "/api/legal/precedents/search",
            params={"q": "계약", "case_type": "civil"},
        )
        assert resp.status_code == 200

    def test_whitespace_only_query_returns_empty(self):
        """Query of only whitespace is treated as empty — returns items=[]."""
        resp = client.get("/api/legal/precedents/search", params={"q": "   "})
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_router_registered_in_app(self):
        """Verify the /api/legal prefix is reachable (router mount check)."""
        # The route exists — even with no DB it responds 200, not 404
        resp = client.get("/api/legal/precedents/search", params={"q": "test"})
        assert resp.status_code != 404
