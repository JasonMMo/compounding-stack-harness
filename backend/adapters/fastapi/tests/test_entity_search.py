"""
test_entity_search.py — L1 tests for entity.list free-text `search` param.

Regression guard for the Growth-126 defect: the vanilla-htmx toolbar sends a
free-text `search=<term>` param, but the backend treated any non-reserved key
as an exact field=value filter. Since no record has a field literally named
`search`, EVERY search returned zero rows in EVERY demo. `search` is now a
reserved key handled as a case-insensitive substring match across all fields.

Run:
    cd backend/adapters/fastapi
    pytest tests/test_entity_search.py -v
"""

from __future__ import annotations

import pathlib
import sys

# Adapter root importable without installation
_ADAPTER_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ADAPTER_DIR))

import pytest
from fastapi.testclient import TestClient

from main import app
from store import entity_store


@pytest.fixture(autouse=True)
def _clean_store():
    """Reset the in-memory singleton before each test for isolation."""
    entity_store.clear_all()
    yield
    entity_store.clear_all()


@pytest.fixture()
def client():
    return TestClient(app)


def _create(client: TestClient, etype: str, data: dict) -> str:
    resp = client.post(f"/api/entities/{etype}", json={"data": data})
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest.fixture()
def seeded(client):
    """Seed a small, isolated entity type so other tests are unaffected."""
    etype = "search_fixture"
    _create(client, etype, {"name": "로그인 화면 구현", "status": "todo"})
    _create(client, etype, {"name": "결제 오류 수정", "status": "doing"})
    _create(client, etype, {"name": "문서 검토 요청", "status": "done"})
    return etype


def _list(client, etype, **params):
    resp = client.get(f"/api/entities/{etype}", params=params)
    assert resp.status_code == 200, resp.text
    return resp.json()


class TestEntitySearch:
    def test_search_substring_matches_name(self, client, seeded):
        """A real substring of one record's name returns exactly that record."""
        body = _list(client, seeded, search="결제")
        assert body["total"] == 1
        assert body["items"][0]["name"] == "결제 오류 수정"

    def test_search_is_case_insensitive(self, client):
        etype = "search_case"
        _create(client, etype, {"name": "Refund API"})
        _create(client, etype, {"name": "Login Page"})
        body = _list(client, etype, search="refund")
        assert body["total"] == 1
        assert body["items"][0]["name"] == "Refund API"

    def test_search_matches_any_field(self, client):
        """Term present only in a non-name field still matches (OR across fields)."""
        etype = "search_anyfield"
        _create(client, etype, {"name": "Task A", "status": "blocked"})
        _create(client, etype, {"name": "Task B", "status": "todo"})
        body = _list(client, etype, search="blocked")
        assert body["total"] == 1
        assert body["items"][0]["name"] == "Task A"

    def test_search_no_match_returns_empty(self, client, seeded):
        body = _list(client, seeded, search="존재하지않는키워드")
        assert body["total"] == 0
        assert body["items"] == []

    def test_blank_search_returns_all(self, client, seeded):
        """Empty search term must NOT filter anything out (regression guard)."""
        body = _list(client, seeded, search="")
        assert body["total"] == 3

    def test_no_search_param_returns_all(self, client, seeded):
        body = _list(client, seeded)
        assert body["total"] == 3

    def test_search_combines_with_filter(self, client):
        """`search` applies AFTER an exact `filter` — both narrow the result."""
        etype = "search_plus_filter"
        _create(client, etype, {"name": "로그인 버그", "status": "todo"})
        _create(client, etype, {"name": "로그인 개선", "status": "done"})
        # exact filter status=todo, then substring search 로그인
        body = _list(client, etype, status="todo", search="로그인")
        assert body["total"] == 1
        assert body["items"][0]["status"] == "todo"
