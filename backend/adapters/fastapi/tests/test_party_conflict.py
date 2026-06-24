"""
test_party_conflict.py — L1 tests for K2 conflict-of-interest check (Growth-127).

project.search-similar is generalized with an `entity_type` param (default "task").
K2 reuses the same similarity engine over `case-party` to surface name-match
candidates before engagement. Honesty: results are candidates, not a verdict.

Run:
    cd backend/adapters/fastapi
    pytest tests/test_party_conflict.py -v
"""

from __future__ import annotations

import pathlib
import sys

_ADAPTER_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ADAPTER_DIR))

import pytest
from fastapi.testclient import TestClient

from main import app
from store import entity_store


@pytest.fixture(autouse=True)
def _clean_store():
    entity_store.clear_all()
    yield
    entity_store.clear_all()


@pytest.fixture()
def client():
    return TestClient(app)


def _seed_parties(client: TestClient) -> None:
    # Seed the store directly — bypasses case_id FK validation; this suite
    # exercises the search path, not create-time validation.
    for data in (
        {"name": "주식회사 에이비씨솔루션", "role": "plaintiff", "case_id": "c1"},
        {"name": "홍길동", "role": "defendant", "case_id": "c2"},
        {"name": "김철수", "role": "witness", "case_id": "c3"},
    ):
        entity_store.create("case-party", data)


def _seed_tasks(client: TestClient) -> None:
    for data in ({"name": "로그인 버그"}, {"name": "결제 오류"}):
        entity_store.create("task", data)


class TestPartyConflict:
    def test_entity_type_case_party_matches_by_name(self, client):
        _seed_parties(client)
        r = client.get(
            "/api/project/search-similar",
            params={"query_text": "홍길동", "entity_type": "case-party"},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert "mode" in body  # honesty badge always present
        names = [it.get("name") for it in body["items"]]
        assert "홍길동" in names

    def test_default_entity_type_is_task(self, client):
        """Omitting entity_type preserves original task behaviour (open-closed)."""
        _seed_parties(client)
        _seed_tasks(client)
        r = client.get("/api/project/search-similar", params={"query_text": "버그"})
        assert r.status_code == 200, r.text
        names = [it.get("name") for it in r.json()["items"]]
        # task candidates only — case-party names must not leak into default search
        assert "홍길동" not in names

    def test_post_body_entity_type(self, client):
        _seed_parties(client)
        r = client.post(
            "/api/project/search-similar",
            json={"query_text": "주식회사", "entity_type": "case-party", "top_n": 5},
        )
        assert r.status_code == 200, r.text
        assert r.json()["total"] >= 1

    def test_blank_query_returns_empty(self, client):
        _seed_parties(client)
        r = client.get(
            "/api/project/search-similar",
            params={"query_text": "  ", "entity_type": "case-party"},
        )
        assert r.status_code == 200
        assert r.json()["total"] == 0
