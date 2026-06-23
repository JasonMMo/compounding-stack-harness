"""
tests/test_similar.py — L1 unit tests for /tasks/similar htmx fragment.

Covers:
1. Blank query → "검색어를 입력하세요" prompt, no proxy call.
2. Semantic result → "AI 의미검색" badge + score percentage in fragment.
3. Lexical result → "키워드 검색" badge, "AI 의미검색" NOT present.
4. Empty items with non-blank query → "유사한 태스크가 없습니다".
5. Proxy non-200 → error line rendered, route still returns HTTP 200.
"""

import importlib
import json
import pathlib
import sys
import unittest.mock as mock

import pytest

# ---------------------------------------------------------------------------
# Path setup — adapter root must be importable
# ---------------------------------------------------------------------------

_ADAPTER_ROOT = pathlib.Path(__file__).parent.parent  # …/vanilla-htmx/
_REPO_ROOT = _ADAPTER_ROOT.parent.parent.parent        # …/compounding-stack-harness/
_TASKFLOW_MANIFEST = _REPO_ROOT / "out" / "taskflow-demo" / "screen-manifest.json"

sys.path.insert(0, str(_ADAPTER_ROOT))


# ---------------------------------------------------------------------------
# Flask test client fixture — mirrors test_board.py pattern
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def flask_client():
    """Flask test client with mock backend.

    Uses taskflow-demo manifest when available; falls back to no-manifest mode
    so the similar-task route tests can run without scaffold.
    """
    import os
    if _TASKFLOW_MANIFEST.is_file():
        os.environ["PROFILE_MANIFEST"] = str(_TASKFLOW_MANIFEST)
    else:
        os.environ.pop("PROFILE_MANIFEST", None)
    os.environ["BACKEND_BASE_URL"] = "http://localhost:19999"  # no real backend

    import manifest_loader as ml_mod
    ml_mod._manifest_loader = None
    importlib.reload(ml_mod)

    import server as srv_mod
    importlib.reload(srv_mod)

    srv_mod.app.config["TESTING"] = True
    srv_mod.app.config["SECRET_KEY"] = "test-secret"

    with srv_mod.app.test_client() as client:
        with client.session_transaction() as sess:
            sess["token"] = "test-token"
            sess["user_id"] = "testuser"
        yield client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_proxy(monkeypatch, payload: dict, status: int = 200):
    """Monkeypatch server._proxy_request to return (payload, status)."""
    import server as srv_mod
    monkeypatch.setattr(srv_mod, "_proxy_request",
                        lambda *a, **kw: (payload, status))


# ---------------------------------------------------------------------------
# 1. Blank query — no proxy call, prompt rendered
# ---------------------------------------------------------------------------

class TestSimilarBlankQuery:
    def test_blank_q_renders_prompt(self, flask_client, monkeypatch):
        """GET /tasks/similar with no q → renders '검색어를 입력하세요', no proxy."""
        import server as srv_mod
        call_log = []

        def _spy(*a, **kw):
            call_log.append(a)
            return {}, 200

        monkeypatch.setattr(srv_mod, "_proxy_request", _spy)
        response = flask_client.get("/tasks/similar")
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "검색어를 입력하세요" in html
        assert call_log == [], "proxy must NOT be called for blank query"

    def test_whitespace_only_q_treated_as_blank(self, flask_client, monkeypatch):
        """q='   ' (whitespace) is treated as blank → prompt, no proxy."""
        import server as srv_mod
        call_log = []

        def _spy(*a, **kw):
            call_log.append(a)
            return {}, 200

        monkeypatch.setattr(srv_mod, "_proxy_request", _spy)
        response = flask_client.get("/tasks/similar?q=+++")
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "검색어를 입력하세요" in html
        assert call_log == []


# ---------------------------------------------------------------------------
# 2. Semantic result — "AI 의미검색" badge + score
# ---------------------------------------------------------------------------

class TestSimilarSemantic:
    def test_semantic_badge_present(self, flask_client, monkeypatch):
        """mode=semantic → fragment contains 'AI 의미검색' badge."""
        _mock_proxy(monkeypatch, {
            "mode": "semantic",
            "items": [
                {"id": "t1", "name": "로그인 구현", "status": "todo", "score": 0.91}
            ],
            "total": 1,
        })
        response = flask_client.get("/tasks/similar?q=로그인")
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "AI 의미검색" in html

    def test_semantic_score_percentage(self, flask_client, monkeypatch):
        """Score 0.91 → '91%' appears in fragment."""
        _mock_proxy(monkeypatch, {
            "mode": "semantic",
            "items": [
                {"id": "t1", "name": "로그인 구현", "status": "todo", "score": 0.91}
            ],
            "total": 1,
        })
        response = flask_client.get("/tasks/similar?q=로그인")
        assert response.status_code == 200
        assert b"91%" in response.data

    def test_semantic_task_link_present(self, flask_client, monkeypatch):
        """Task name is rendered as a link to /entities/task/<id>."""
        _mock_proxy(monkeypatch, {
            "mode": "semantic",
            "items": [
                {"id": "t1", "name": "로그인 구현", "status": "todo", "score": 0.91}
            ],
            "total": 1,
        })
        response = flask_client.get("/tasks/similar?q=로그인")
        html = response.data.decode("utf-8")
        assert "/entities/task/t1" in html
        assert "로그인 구현" in html


# ---------------------------------------------------------------------------
# 3. Lexical result — correct badge, NO "AI 의미검색"
# ---------------------------------------------------------------------------

class TestSimilarLexical:
    def test_lexical_badge_present(self, flask_client, monkeypatch):
        """mode=lexical → fragment contains '키워드 검색' badge."""
        _mock_proxy(monkeypatch, {
            "mode": "lexical",
            "items": [
                {"id": "t2", "name": "회원가입 폼", "status": "in-progress", "score": 0.75}
            ],
            "total": 1,
        })
        response = flask_client.get("/tasks/similar?q=회원")
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "키워드 검색" in html

    def test_lexical_no_ai_badge(self, flask_client, monkeypatch):
        """mode=lexical → 'AI 의미검색' MUST NOT appear (honesty contract)."""
        _mock_proxy(monkeypatch, {
            "mode": "lexical",
            "items": [
                {"id": "t2", "name": "회원가입 폼", "status": "in-progress", "score": 0.75}
            ],
            "total": 1,
        })
        response = flask_client.get("/tasks/similar?q=회원")
        html = response.data.decode("utf-8")
        assert "AI 의미검색" not in html

    def test_lexical_score_percentage(self, flask_client, monkeypatch):
        """Score 0.75 → '75%' appears for lexical result."""
        _mock_proxy(monkeypatch, {
            "mode": "lexical",
            "items": [
                {"id": "t2", "name": "회원가입 폼", "status": "in-progress", "score": 0.75}
            ],
            "total": 1,
        })
        response = flask_client.get("/tasks/similar?q=회원")
        assert b"75%" in response.data


# ---------------------------------------------------------------------------
# 4. Empty items with non-blank query
# ---------------------------------------------------------------------------

class TestSimilarEmpty:
    def test_empty_items_renders_no_results_message(self, flask_client, monkeypatch):
        """Backend returns empty items → '유사한 태스크가 없습니다'."""
        _mock_proxy(monkeypatch, {"mode": "semantic", "items": [], "total": 0})
        response = flask_client.get("/tasks/similar?q=존재하지않는태스크")
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "유사한 태스크가 없습니다" in html


# ---------------------------------------------------------------------------
# 5. Proxy non-200 → error rendered, route returns HTTP 200
# ---------------------------------------------------------------------------

class TestSimilarProxyError:
    def test_non_200_renders_error_gracefully(self, flask_client, monkeypatch):
        """Backend 503 → fragment shows error text; route itself returns 200."""
        _mock_proxy(monkeypatch,
                    {"error": {"code": "UNAVAILABLE", "message": "down"}},
                    status=503)
        response = flask_client.get("/tasks/similar?q=테스트")
        # Route must return 200 so htmx swap works (graceful degradation)
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        # Fragment must not be empty — some error text rendered
        assert len(html.strip()) > 0

    def test_non_200_no_exception_bubbles(self, flask_client, monkeypatch):
        """Non-200 must never cause a 5xx from the /tasks/similar route itself."""
        _mock_proxy(monkeypatch,
                    {"error": {"code": "INTERNAL", "message": "crash"}},
                    status=500)
        response = flask_client.get("/tasks/similar?q=크래시")
        assert response.status_code == 200
