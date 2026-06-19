"""
tests/test_hardening.py — CISO #8 하드닝 단위 테스트.

커버리지:
  1. /health shallow liveness: 인증 없이 {"status": "ok"} 200 반환.
  2. prod 모드 docs 비활성화: LEGAL_RAG_ENV=prod 시 /docs /redoc /openapi.json 404.
  3. dev 모드 docs 활성화: LEGAL_RAG_ENV=dev(기본) 시 /docs 200.

FastAPI TestClient 사용 (httpx 기반, DB/사이드카 불필요 — lifespan 은 bypass).
"""
from __future__ import annotations

import contextlib
import os
import sys

import pytest
from fastapi.testclient import TestClient


# ── 헬퍼: lifespan 을 no-op 으로 패치한 TestClient ──────────────────────────────

@contextlib.contextmanager
def _no_lifespan_client(app):
    """Context manager: patches app's lifespan to a no-op, returns TestClient.

    Starlette ≤ 0.37 does not have a lifespan=off parameter on TestClient.
    We patch router.lifespan_context directly so DB/sidecar startup is skipped.
    """
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _noop_lifespan(app):
        yield

    original = app.router.lifespan_context
    app.router.lifespan_context = _noop_lifespan
    try:
        with TestClient(app, raise_server_exceptions=True) as client:
            yield client
    finally:
        app.router.lifespan_context = original


# ── /health shallow liveness 테스트 ────────────────────────────────────────────

class TestHealthShallow:
    """GET /health returns {"status":"ok"} without auth, no internal state."""

    def test_health_returns_200_ok(self):
        import api as api_mod
        with _no_lifespan_client(api_mod.app) as client:
            resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_body_is_shallow(self):
        """Response must have status=ok and must NOT expose db_pool or embed_sidecar."""
        import api as api_mod
        with _no_lifespan_client(api_mod.app) as client:
            resp = client.get("/health")
        body = resp.json()
        assert body.get("status") == "ok"
        assert "db_pool" not in body, "/health must not expose db_pool"
        assert "embed_sidecar" not in body, "/health must not expose embed_sidecar"

    def test_health_no_auth_required(self):
        """No Authorization or X-Service-Token needed for /health."""
        import api as api_mod
        with _no_lifespan_client(api_mod.app) as client:
            resp = client.get("/health")
        # Must not be 401 or 403
        assert resp.status_code not in (401, 403)


# ── prod モード docs 비활성화 테스트 ────────────────────────────────────────────

class TestProdDocs:
    """LEGAL_RAG_ENV=prod → /docs /redoc /openapi.json all return 404."""

    @pytest.fixture()
    def prod_app(self, monkeypatch):
        """Re-import api.py with LEGAL_RAG_ENV=prod to get a fresh app instance."""
        monkeypatch.setenv("LEGAL_RAG_ENV", "prod")
        # Remove cached module so import picks up new env
        for mod_name in list(sys.modules.keys()):
            if mod_name in ("api", "config"):
                del sys.modules[mod_name]
        import api as api_mod  # noqa: PLC0415
        yield api_mod.app
        # Cleanup: remove again so other tests get the default env app
        for mod_name in ("api", "config"):
            sys.modules.pop(mod_name, None)

    def test_docs_404_in_prod(self, prod_app):
        with _no_lifespan_client(prod_app) as client:
            assert client.get("/docs").status_code == 404

    def test_redoc_404_in_prod(self, prod_app):
        with _no_lifespan_client(prod_app) as client:
            assert client.get("/redoc").status_code == 404

    def test_openapi_json_404_in_prod(self, prod_app):
        with _no_lifespan_client(prod_app) as client:
            assert client.get("/openapi.json").status_code == 404


# ── dev 모드 docs 활성화 테스트 ────────────────────────────────────────────────

class TestDevDocs:
    """LEGAL_RAG_ENV=dev (기본) → /docs 200."""

    @pytest.fixture()
    def dev_app(self, monkeypatch):
        monkeypatch.setenv("LEGAL_RAG_ENV", "dev")
        for mod_name in list(sys.modules.keys()):
            if mod_name in ("api", "config"):
                del sys.modules[mod_name]
        import api as api_mod  # noqa: PLC0415
        yield api_mod.app
        for mod_name in ("api", "config"):
            sys.modules.pop(mod_name, None)

    def test_docs_200_in_dev(self, dev_app):
        with _no_lifespan_client(dev_app) as client:
            assert client.get("/docs").status_code == 200
