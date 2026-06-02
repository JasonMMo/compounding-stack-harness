"""
tests/test_entity_list_params.py — L1 regression guard for entity.list outbound
query-parameter mapping (commit 6c13137 bug).

Why this file exists:
  The vanilla-htmx `entity_list` Flask route assembles the query params it sends
  to the backend and hands them to `_proxy_request`. A bug (fixed in 6c13137)
  made the route send:
    - `entity_type` as a query key  → backend entity.list treats any non-reserved
      key as a record FILTER → every list screen rendered the empty state (0 rows);
    - `paging_page` / `paging_size`  → backend reads `page` / `size`, so paging was
      silently ignored;
    - `filter_search`                → backend filters on `search`.
  The L4 _shared compliance suite never caught this: it hits the backend API
  directly and never traverses this Flask route. So the param-mapping was unpinned.

What this pins:
  We mock `server._proxy_request` (the single seam where the route's assembled
  params leave the frontend) and assert the EXACT outbound query keys for offset,
  cursor, sort, and search modes. The real Flask route is exercised end-to-end
  (test client → @_require_login → entity_list → _proxy_request), no live backend.

  Contract keys that MUST go out (see middle/contract + _shared compliance suite:
  page=, size=, paging_mode=, cursor=, sort_field=, sort_direction=, search=).
  Legacy/wrong keys that MUST NOT go out: entity_type, paging_page, paging_size,
  filter_search, paging_cursor.

  entity_type is verified to travel in the URL PATH only (not the query dict).
"""

import pathlib
import sys

import pytest

# Ensure the adapter package root is importable (same pattern as sibling tests).
_ADAPTER_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_ADAPTER_ROOT))

import server  # noqa: E402


# Query keys the backend contract accepts (entity.list).
_CONTRACT_KEYS = {
    "paging_mode", "page", "size", "cursor",
    "sort_field", "sort_direction", "search",
}
# Legacy / buggy keys that must never be sent (each caused the 6c13137 defect).
_FORBIDDEN_KEYS = {
    "entity_type", "paging_page", "paging_size", "filter_search", "paging_cursor",
}


@pytest.fixture
def client(monkeypatch):
    """
    Flask test client with a captured _proxy_request.

    Returns (client, captured) where `captured` is a dict populated with the
    method/path/params the route handed to _proxy_request. The backend is NOT
    contacted — _proxy_request is replaced with a stub returning an empty list.
    """
    captured: dict = {}

    def _fake_proxy(method, path, params=None, body=None, token=None):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = dict(params or {})
        captured["body"] = body
        # Minimal valid entity.list payload so the route renders without error.
        return {"entity_type": "employee", "items": [], "total": 0}, 200

    monkeypatch.setattr(server, "_proxy_request", _fake_proxy)

    server.app.config["TESTING"] = True
    c = server.app.test_client()
    with c.session_transaction() as sess:
        sess["token"] = "test-token"  # satisfy @_require_login
    return c, captured


# ---------------------------------------------------------------------------
# Offset mode (the default — Scene 3A employee list)
# ---------------------------------------------------------------------------

class TestOffsetParams:
    def test_offset_sends_page_and_size(self, client):
        c, captured = client
        resp = c.get("/entities/employee")
        assert resp.status_code == 200
        params = captured["params"]
        assert params.get("paging_mode") == "offset"
        assert params.get("page") == "1"
        assert params.get("size") == "20"

    def test_offset_does_not_send_entity_type(self, client):
        """The root cause of the empty-list bug: entity_type leaked as a filter."""
        c, captured = client
        c.get("/entities/employee")
        assert "entity_type" not in captured["params"]

    def test_entity_type_travels_in_path_only(self, client):
        c, captured = client
        c.get("/entities/employee")
        assert captured["path"] == "/api/entities/employee"

    def test_offset_does_not_send_legacy_keys(self, client):
        c, captured = client
        c.get("/entities/employee?paging_page=2&paging_size=50")
        params = captured["params"]
        # Route reads paging_page/paging_size from the request and must REMAP
        # them onto page/size — never forward the legacy keys.
        assert "paging_page" not in params
        assert "paging_size" not in params
        assert params.get("page") == "2"
        assert params.get("size") == "50"

    def test_no_forbidden_keys_leak(self, client):
        c, captured = client
        c.get("/entities/asset?paging_page=1&paging_size=20")
        leaked = _FORBIDDEN_KEYS & set(captured["params"])
        assert not leaked, f"Forbidden keys leaked to backend: {leaked}"

    def test_only_contract_keys_go_out(self, client):
        c, captured = client
        c.get("/entities/employee")
        extra = set(captured["params"]) - _CONTRACT_KEYS
        assert not extra, f"Non-contract keys sent to backend: {extra}"


# ---------------------------------------------------------------------------
# Cursor mode (F-2)
# ---------------------------------------------------------------------------

class TestCursorParams:
    def test_cursor_sends_cursor_and_size(self, client):
        c, captured = client
        c.get("/entities/employee?paging_mode=cursor&paging_cursor=abc123&paging_size=15")
        params = captured["params"]
        assert params.get("paging_mode") == "cursor"
        assert params.get("cursor") == "abc123"
        assert params.get("size") == "15"

    def test_cursor_does_not_send_paging_cursor_key(self, client):
        c, captured = client
        c.get("/entities/employee?paging_mode=cursor&paging_cursor=abc123&paging_size=15")
        params = captured["params"]
        assert "paging_cursor" not in params
        assert "entity_type" not in params

    def test_cursor_only_contract_keys(self, client):
        c, captured = client
        c.get("/entities/employee?paging_mode=cursor&paging_cursor=abc123&paging_size=15")
        extra = set(captured["params"]) - _CONTRACT_KEYS
        assert not extra, f"Non-contract keys sent in cursor mode: {extra}"


# ---------------------------------------------------------------------------
# Sort + search mapping
# ---------------------------------------------------------------------------

class TestSortAndSearch:
    def test_sort_keys_passthrough(self, client):
        c, captured = client
        c.get("/entities/employee?sort_field=full_name&sort_direction=desc")
        params = captured["params"]
        assert params.get("sort_field") == "full_name"
        assert params.get("sort_direction") == "desc"

    def test_search_maps_to_search_not_filter_search(self, client):
        c, captured = client
        c.get("/entities/employee?search=kim")
        params = captured["params"]
        assert params.get("search") == "kim"
        assert "filter_search" not in params

    def test_search_absent_when_blank(self, client):
        c, captured = client
        c.get("/entities/employee")
        assert "search" not in captured["params"]
