"""test_compliance.py -- vanilla-htmx frontend adapter compliance gate (Growth-8).

Gate dimensions (frontend-adapter-contract.md section 3-4):
  DIM-1  F-1  Flat-underscore query serialization
  DIM-2  F-3  Error envelope rendering (all 11 codes in codes.yaml)
  DIM-3  F-2  Paging: offset last-page + cursor mode
  DIM-4  F-4  Idempotent delete
  L1     Engineer unit tests pass (rc=0)
  L3     build_tokens.py exits 0, tokens.css non-empty

Single-source: message_ko from codes.yaml -- not hardcoded.
No autouse fixtures (Growth-7 lesson: accumulate state -> false PASS).
"""

import pathlib
import subprocess
import sys
import urllib.error
from io import BytesIO
from unittest.mock import patch

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_ADAPTER_ROOT = _REPO_ROOT / "frontend" / "adapters" / "vanilla-htmx"

import os
os.environ.setdefault("CONTRACT_DIR", str(_REPO_ROOT / "middle" / "contract"))
if str(_ADAPTER_ROOT) not in sys.path:
    sys.path.insert(0, str(_ADAPTER_ROOT))


def _load_all_error_codes():
    from contract_loader import ContractLoader
    return list(ContractLoader().codes().items())

_ALL_ERROR_CODES = _load_all_error_codes()
_ALL_ERROR_CODE_IDS = [c for c, _ in _ALL_ERROR_CODES]
_REDIRECT_CODES = {"AUTH_REQUIRED", "AUTH_EXPIRED"}


# =============================================================================
# DIM-1 -- F-1 Flat-underscore query serialization
# =============================================================================

class TestF1FlatUnderscoreSerializer:
    """
    entity_list route must build params with flat-underscore keys.
    paging_mode, paging_page, paging_size, paging_cursor, sort_field, sort_direction
    -- never dot-notation (paging.mode etc.).
    This is the exact defect class caught in Growth-7 backend gate.
    """

    def _capture_params(self, flask_client, qs):
        client, srv = flask_client
        captured = {}

        def fake_proxy(method, path, params=None, body=None, token=None):
            captured.update(params or {})
            return {"items": [], "total": 0, "next_cursor": None}, 200

        with patch.object(srv, "_proxy_request", side_effect=fake_proxy):
            resp = client.get("/entities/customer?" + qs)
            assert resp.status_code == 200, (
                "entity_list returned %d -- route crashed" % resp.status_code
            )
        return captured

    def test_offset_paging_flat_keys_present(self, flask_client):
        params = self._capture_params(flask_client, "paging_mode=offset&paging_page=2&paging_size=10")
        assert "paging_mode" in params, "paging_mode missing"
        assert "paging_page" in params, "paging_page missing"
        assert "paging_size" in params, "paging_size missing"
        assert "paging.mode" not in params, "F-1 VIOLATION: dot-notation paging.mode"
        assert "paging.page" not in params, "F-1 VIOLATION: dot-notation paging.page"
        assert "paging.size" not in params, "F-1 VIOLATION: dot-notation paging.size"

    def test_offset_paging_values_correct(self, flask_client):
        params = self._capture_params(flask_client, "paging_mode=offset&paging_page=3&paging_size=15")
        assert params["paging_mode"] == "offset"
        assert str(params["paging_page"]) == "3"
        assert str(params["paging_size"]) == "15"

    def test_cursor_paging_flat_keys(self, flask_client):
        params = self._capture_params(flask_client, "paging_mode=cursor&paging_cursor=tok_abc123&paging_size=20")
        assert "paging_mode" in params
        assert "paging_cursor" in params
        assert params["paging_mode"] == "cursor"
        assert params["paging_cursor"] == "tok_abc123"
        assert "paging_page" not in params, "F-1: cursor must not send paging_page"
        assert "paging.cursor" not in params, "F-1 VIOLATION: dot-notation paging.cursor"

    def test_sort_flat_keys(self, flask_client):
        params = self._capture_params(flask_client, "paging_mode=offset&sort_field=name&sort_direction=desc")
        assert "sort_field" in params, "sort_field missing"
        assert "sort_direction" in params, "sort_direction missing"
        assert params["sort_field"] == "name"
        assert params["sort_direction"] == "desc"
        assert "sort.field" not in params, "F-1 VIOLATION: dot-notation sort.field"
        assert "sort.direction" not in params, "F-1 VIOLATION: dot-notation sort.direction"

    def test_no_dot_notation_keys_ever(self, flask_client):
        params = self._capture_params(
            flask_client,
            "paging_mode=offset&paging_page=1&paging_size=5&sort_field=id&sort_direction=asc"
        )
        forbidden = {"paging.mode", "paging.page", "paging.size", "paging.cursor", "sort.field", "sort.direction"}
        violations = forbidden & set(params.keys())
        assert not violations, "F-1 VIOLATION: dot-notation keys found: %s" % violations


# =============================================================================
# DIM-2 -- F-3 Error envelope rendering
# =============================================================================

class TestF3ErrorEnvelopeRendering:
    """
    For each of the 11 codes in codes.yaml:
      1. Mock _proxy_request -> error envelope with that code.
      2. Assert rendered HTML contains message_ko (read from codes.yaml, not hardcoded).
      3. AUTH_REQUIRED/AUTH_EXPIRED: assert redirect to /login.
      4. retriable=true: retry hint rendered. retriable=false: not rendered.
    """

    @pytest.mark.parametrize("code,entry", _ALL_ERROR_CODES, ids=_ALL_ERROR_CODE_IDS)
    def test_error_code_renders_message_ko(self, flask_client, code, entry):
        message_ko = entry.get("message_ko", "")
        message_en = entry.get("message", "")
        http_status = entry.get("http_status", 500)
        client, srv = flask_client

        def fake_proxy(method, path, params=None, body=None, token=None):
            return {"error": {"code": code, "message": message_en}}, http_status

        with patch.object(srv, "_proxy_request", side_effect=fake_proxy):
            resp = client.get("/entities/customer")

        if code in _REDIRECT_CODES:
            assert resp.status_code in (301, 302), (
                "F-3: %s must redirect to login, got %d" % (code, resp.status_code)
            )
            location = resp.headers.get("Location", "")
            assert "login" in location, (
                "F-3: %s redirect must go to /login, got %r" % (code, location)
            )
            return

        html = resp.data.decode("utf-8", errors="replace")
        assert message_ko in html, (
            "F-3 FAIL: message_ko for %s not in HTML. Expected: %r" % (code, message_ko)
        )

    @pytest.mark.parametrize("code,entry", _ALL_ERROR_CODES, ids=_ALL_ERROR_CODE_IDS)
    def test_retriable_hint_matches_codes_yaml(self, flask_client, code, entry):
        if code in _REDIRECT_CODES:
            pytest.skip("%s redirects" % code)
        retriable = bool(entry.get("retriable", False))
        message_en = entry.get("message", "")
        http_status = entry.get("http_status", 500)
        client, srv = flask_client

        def fake_proxy(method, path, params=None, body=None, token=None):
            return {"error": {"code": code, "message": message_en}}, http_status

        with patch.object(srv, "_proxy_request", side_effect=fake_proxy):
            resp = client.get("/entities/customer")

        if resp.status_code in (301, 302):
            pytest.skip("%s redirected" % code)

        html = resp.data.decode("utf-8", errors="replace")
        RETRY_HINT = "잠시 후 다시 시도하세요."
        if retriable:
            assert RETRY_HINT in html, "F-3: retriable %s must render retry hint" % code
        else:
            assert RETRY_HINT not in html, "F-3: non-retriable %s must NOT render retry hint" % code


# =============================================================================
# DIM-3 -- F-2 Paging (offset last-page + cursor mode)
# =============================================================================

class TestF2Paging:
    """F-2: adapter emits both offset and cursor paging modes correctly."""

    def _get_list(self, flask_client, qs, mock_response):
        client, srv = flask_client

        def fake_proxy(method, path, params=None, body=None, token=None):
            return mock_response, 200

        with patch.object(srv, "_proxy_request", side_effect=fake_proxy):
            resp = client.get("/entities/customer?" + qs)
        return resp

    def test_offset_last_page_next_button_disabled(self, flask_client):
        """Last page (page=3 of 3): Next must be a disabled button."""
        # total=25, size=10 -> 3 pages total; page=3 is the last page
        resp = self._get_list(
            flask_client,
            "paging_mode=offset&paging_page=3&paging_size=10",
            {"items": [{"id": "1", "name": "x"}], "total": 25},
        )
        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        assert "disabled" in html, "F-2: last-page must render disabled Next button"

    def test_offset_non_last_page_has_next_link(self, flask_client):
        """Page 1 of 5: active Next link to page 2 must be rendered."""
        resp = self._get_list(
            flask_client,
            "paging_mode=offset&paging_page=1&paging_size=10",
            {"items": [{"id": str(i)} for i in range(10)], "total": 50},
        )
        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        assert "paging_page=2" in html, "F-2: page 1 of 5 must link to paging_page=2"

    def test_cursor_with_next_cursor_shows_load_more(self, flask_client):
        """Cursor + next_cursor: Load-more link with cursor token rendered."""
        resp = self._get_list(
            flask_client,
            "paging_mode=cursor&paging_size=5",
            {"items": [{"id": str(i)} for i in range(5)], "total": 0, "next_cursor": "cursor_tok_xyz"},
        )
        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        assert "cursor_tok_xyz" in html, "F-2: cursor token must appear in Load-more link"
        assert "더 불러오기" in html, "F-2: Load-more button must render"

    def test_cursor_without_next_cursor_shows_end_message(self, flask_client):
        """Cursor + no next_cursor: end-of-data message rendered, no Load-more."""
        resp = self._get_list(
            flask_client,
            "paging_mode=cursor&paging_size=5",
            {"items": [{"id": "1"}], "total": 0, "next_cursor": None},
        )
        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        assert "모든 데이터를 불러왔습니다." in html, "F-2: end-of-data message must render"
        assert "더 불러오기" not in html, "F-2: no Load-more when no next_cursor"


# =============================================================================
# DIM-4 -- F-4 Idempotent delete
# =============================================================================

class TestF4IdempotentDelete:
    """
    F-4: entity.delete is idempotent.
    First-call (200) and second-call (404 -> success) both render success page.
    User must never see NOT_FOUND for a delete operation.
    """

    def test_first_delete_renders_success(self, flask_client):
        client, srv = flask_client

        def fake_proxy(method, path, params=None, body=None, token=None):
            return {"success": True}, 200

        with patch.object(srv, "_proxy_request", side_effect=fake_proxy):
            resp = client.post("/entities/customer/42/delete")

        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        assert "삭제 완료" in html, "F-4: first DELETE must render success page"

    def test_second_delete_also_renders_success(self, flask_client):
        client, srv = flask_client

        def fake_proxy(method, path, params=None, body=None, token=None):
            return {"success": True}, 200

        with patch.object(srv, "_proxy_request", side_effect=fake_proxy):
            resp = client.post("/entities/customer/42/delete")

        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        assert "삭제 완료" in html, "F-4: second DELETE must also render success"

    def test_proxy_404_delete_maps_to_success_unit(self, flask_client):
        """Unit: _proxy_request maps HTTP 404+DELETE -> {success: True}, 200."""
        client, srv = flask_client

        class FakeHTTPError(urllib.error.HTTPError):
            def __init__(self):
                super().__init__(
                    url="http://fake/api/entities/customer/42",
                    code=404, msg="Not Found", hdrs={},
                    fp=BytesIO(b"{}"),
                )
            def read(self):
                return b"{}"

        with patch("urllib.request.urlopen", side_effect=FakeHTTPError()):
            payload, status = srv._proxy_request(
                "DELETE", "/api/entities/customer/42", token="test-token"
            )

        assert status == 200, "F-4: _proxy_request 404+DELETE must -> 200, got %d" % status
        assert payload.get("success") is True, "F-4: payload must be {success: True}"

    def test_proxy_404_get_not_remapped(self, flask_client):
        """Negative: 404+GET must NOT be remapped to success."""
        client, srv = flask_client

        class FakeHTTPError(urllib.error.HTTPError):
            def __init__(self):
                super().__init__(
                    url="http://fake/api/entities/customer/99",
                    code=404, msg="Not Found", hdrs={},
                    fp=BytesIO(b"{}"),
                )
            def read(self):
                return b"{}"

        with patch("urllib.request.urlopen", side_effect=FakeHTTPError()):
            payload, status = srv._proxy_request(
                "GET", "/api/entities/customer/99", token="test-token"
            )

        # 404+GET must NOT be mapped to success -- status stays 404
        assert status == 404, "F-4: 404+GET must NOT be remapped; got %d" % status
        # payload is {} (empty body from fake) -- no success key
        assert payload.get("success") is not True, "F-4: 404+GET must NOT return success"

    def test_delete_confirm_get_not_found_shows_success(self, flask_client):
        """GET delete confirm when entity already gone: success page, not error page."""
        client, srv = flask_client

        def fake_proxy(method, path, params=None, body=None, token=None):
            return {"error": {"code": "NOT_FOUND", "message": "not found"}}, 404

        with patch.object(srv, "_proxy_request", side_effect=fake_proxy):
            resp = client.get("/entities/customer/99/delete")

        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        assert "오류 발생" not in html, "F-4: NOT_FOUND delete must NOT show error page"
        assert "삭제" in html, "F-4: NOT_FOUND delete must show deletion page"


# =============================================================================
# L1 -- Engineer unit tests (subprocess gate)
# =============================================================================

class TestL1EngineerUnitTests:
    """Run frontend/adapters/vanilla-htmx/tests/ as subprocess. Gate: rc=0."""

    def test_l1_engineer_unit_tests_pass(self):
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
            cwd=str(_ADAPTER_ROOT),
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, (
            "L1: Engineer unit tests FAILED (rc=%d). stdout: %s stderr: %s"
            % (result.returncode, result.stdout[:500], result.stderr[:500])
        )


# =============================================================================
# L3 -- build_tokens.py (CSS build gate)
# =============================================================================

class TestL3TokensBuild:
    """L3: build_tokens.py exits 0, tokens.css has >= 5 CSS custom properties."""

    def test_l3_build_tokens_exits_zero(self):
        result = subprocess.run(
            [sys.executable, "build_tokens.py"],
            cwd=str(_ADAPTER_ROOT),
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, (
            "L3: build_tokens.py failed (rc=%d). stdout: %s stderr: %s"
            % (result.returncode, result.stdout[:500], result.stderr[:500])
        )

    def test_l3_tokens_css_non_empty_with_custom_properties(self):
        tokens_css = _ADAPTER_ROOT / "static" / "css" / "tokens.css"
        assert tokens_css.exists(), "L3: tokens.css not found at %s" % tokens_css
        content = tokens_css.read_text(encoding="utf-8")
        assert len(content.strip()) > 0, "L3: tokens.css is empty"
        prop_count = content.count("--")
        assert prop_count >= 5, (
            "L3: tokens.css has %d custom properties, expected >= 5" % prop_count
        )


# =============================================================================
# L4 live -- optional, skipped if not running
# =============================================================================

class TestL4Live:
    """Live smoke against running vanilla-htmx adapter. Skipped when not reachable."""

    def test_l4_health_returns_200(self, frontend_base_url):
        import urllib.request
        resp = urllib.request.urlopen(frontend_base_url + "/health", timeout=5)
        assert resp.status == 200, "L4: /health returned %d" % resp.status

    def test_l4_login_page_loads(self, frontend_base_url):
        import urllib.request
        resp = urllib.request.urlopen(frontend_base_url + "/login", timeout=5)
        assert resp.status == 200
        html = resp.read().decode("utf-8", errors="replace")
        assert "로그인" in html or "login" in html.lower(), (
            "L4: /login must render a login form"
        )
