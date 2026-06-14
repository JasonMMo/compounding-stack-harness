"""test_ui_check.py -- Tier-1 pure/deterministic tests for ui_check.py (LLM 0).

Tests that do NOT require a live browser or external network:
  - derive_check_paths: path derivation from manifest
  - check_http:         HTTP status checks against a local fixture server
  - write_report:       verdict precedence, PII-free JSON, file written

Browser (Playwright) tests are skipped if playwright is not importable.

Run:
  PYTHONIOENCODING=utf-8 python -m pytest scripts/workflow/tests/test_ui_check.py -q
"""
from __future__ import annotations

import http.server
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

# Allow importing ui_check from scripts/workflow/
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from ui_check import (  # noqa: E402
    CheckResult,
    derive_check_paths,
    check_http,
    write_report,
    PLAYWRIGHT_AVAILABLE,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _FixtureHandler(http.server.BaseHTTPRequestHandler):
    """Tiny HTTP handler: /ok -> 200, /boom -> 500, everything else -> 404."""

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/ok":
            body = b"<html><body>ok</body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/boom":
            self.send_response(500)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self) -> None:  # noqa: N802
        if self.path == "/ok":
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args: object) -> None:  # noqa: ANN002
        pass  # suppress server logs in test output


@pytest.fixture(scope="module")
def fixture_server():
    """Spin up a tiny local HTTP server on a free port; yield base_url."""
    server = http.server.HTTPServer(("127.0.0.1", 0), _FixtureHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    yield base_url
    server.shutdown()


# ---------------------------------------------------------------------------
# derive_check_paths tests
# ---------------------------------------------------------------------------


class TestDeriveCheckPaths:
    def test_always_includes_login(self) -> None:
        result = derive_check_paths({})
        assert "/login" in result

    def test_entity_paths_added(self) -> None:
        manifest = {
            "entities": {
                "sales-order": {"domain": "sales", "fields": [], "hidden_fields": []},
                "contact": {"domain": "crm", "fields": [], "hidden_fields": []},
            }
        }
        paths = derive_check_paths(manifest)
        assert "/login" in paths
        assert "/sales-order" in paths
        assert "/contact" in paths

    def test_deduplication(self) -> None:
        # Unlikely in practice, but if an entity key were "login" it should not duplicate
        manifest = {
            "entities": {
                "login": {"domain": "auth", "fields": [], "hidden_fields": []},
                "product": {"domain": "shop", "fields": [], "hidden_fields": []},
            }
        }
        paths = derive_check_paths(manifest)
        assert paths.count("/login") == 1
        assert "/product" in paths

    def test_all_paths_ascii(self) -> None:
        manifest = {
            "entities": {
                "sales-order": {},
                "inventory-item": {},
            }
        }
        paths = derive_check_paths(manifest)
        for p in paths:
            p.encode("ascii")  # raises UnicodeEncodeError if non-ASCII

    def test_two_entities_length(self) -> None:
        manifest = {
            "entities": {
                "alpha": {},
                "beta": {},
            }
        }
        paths = derive_check_paths(manifest)
        # /login + /alpha + /beta = 3
        assert len(paths) == 3

    def test_empty_entities(self) -> None:
        paths = derive_check_paths({"entities": {}})
        assert paths == ["/login"]

    def test_custom_entry_path_root(self) -> None:
        # Apps with no login (e.g. intake) serve their entry at "/".
        paths = derive_check_paths({}, entry_path="/")
        assert paths == ["/"]
        assert "/login" not in paths

    def test_entry_path_normalized_leading_slash(self) -> None:
        paths = derive_check_paths({"entities": {"contact": {}}}, entry_path="dashboard")
        assert paths[0] == "/dashboard"
        assert "/contact" in paths


# ---------------------------------------------------------------------------
# check_http tests
# ---------------------------------------------------------------------------


class TestCheckHttp:
    def test_200_is_pass(self, fixture_server: str) -> None:
        results = check_http(fixture_server, ["/ok"])
        assert len(results) == 1
        r = results[0]
        assert r.status == "PASS"
        assert "200" in r.detail

    def test_404_on_entry_path_is_fail(self, fixture_server: str) -> None:
        # The entry path is strict: a 404 there is a real failure.
        results = check_http(fixture_server, ["/not-found"], entry_path="/not-found")
        assert len(results) == 1
        r = results[0]
        assert r.status == "FAIL"
        assert "404" in r.detail

    def test_404_on_entity_path_is_warn(self, fixture_server: str) -> None:
        # Entity paths (not the entry path) are auth-gated/htmx-partial routes;
        # a 404 there is expected for an unauthenticated check -> WARN, not FAIL.
        results = check_http(fixture_server, ["/ok", "/missing"], entry_path="/ok")
        by = {r.check.split(":")[1]: r for r in results}
        assert by["/ok"].status == "PASS"
        assert by["/missing"].status == "WARN"
        assert "auth-gated" in by["/missing"].detail

    def test_5xx_on_entity_path_is_fail(self, fixture_server: str) -> None:
        # A server error (5xx) on an entity path is a real defect, never downgraded.
        results = check_http(fixture_server, ["/ok", "/boom"], entry_path="/ok")
        by = {r.check.split(":")[1]: r for r in results}
        assert by["/boom"].status == "FAIL"
        assert "500" in by["/boom"].detail

    def test_multiple_paths(self, fixture_server: str) -> None:
        # Default entry_path=/login; /ok and /missing are both entity paths.
        results = check_http(fixture_server, ["/ok", "/missing"])
        statuses = {r.check.split(":")[1]: r.status for r in results}
        assert statuses["/ok"] == "PASS"
        assert statuses["/missing"] == "WARN"  # entity-path 404 -> auth-gated WARN

    def test_connection_error_is_fail(self) -> None:
        # Port 1 is almost certainly not listening
        results = check_http("http://127.0.0.1:1", ["/login"])
        assert results[0].status == "FAIL"

    def test_check_name_format(self, fixture_server: str) -> None:
        results = check_http(fixture_server, ["/ok"])
        assert results[0].check == "http:/ok"


# ---------------------------------------------------------------------------
# write_report tests
# ---------------------------------------------------------------------------


class TestWriteReport:
    def _make_results(self, statuses: list[str]) -> list[CheckResult]:
        return [
            CheckResult(check=f"test:{i}", status=s, detail="detail")
            for i, s in enumerate(statuses)
        ]

    def test_all_pass_verdict(self, tmp_path: Path) -> None:
        results = self._make_results(["PASS", "PASS"])
        report = write_report(results, "test-slug", tmp_path / "test-slug.json")
        assert report["verdict"] == "PASS"

    def test_warn_beats_pass(self, tmp_path: Path) -> None:
        results = self._make_results(["PASS", "WARN", "PASS"])
        report = write_report(results, "test-slug", tmp_path / "test-slug.json")
        assert report["verdict"] == "WARN"

    def test_fail_beats_warn(self, tmp_path: Path) -> None:
        results = self._make_results(["PASS", "WARN", "FAIL"])
        report = write_report(results, "test-slug", tmp_path / "test-slug.json")
        assert report["verdict"] == "FAIL"

    def test_file_written(self, tmp_path: Path) -> None:
        results = self._make_results(["PASS"])
        out = tmp_path / "report.json"
        write_report(results, "slug-a", out)
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["slug"] == "slug-a"

    def test_no_pii_keys(self, tmp_path: Path) -> None:
        """Report must not contain PII-leaking top-level keys."""
        results = self._make_results(["PASS"])
        report = write_report(results, "test-slug", tmp_path / "test.json")
        pii_keys = {"email", "name", "phone", "free_text", "client_id", "revision"}
        assert not pii_keys.intersection(report.keys())

    def test_report_has_required_fields(self, tmp_path: Path) -> None:
        results = self._make_results(["PASS"])
        report = write_report(results, "s", tmp_path / "s.json")
        for key in ("slug", "generated_at", "playwright_available", "viewport_matrix", "results", "verdict"):
            assert key in report, f"Missing key: {key}"

    def test_results_serializable(self, tmp_path: Path) -> None:
        results = self._make_results(["PASS", "FAIL"])
        report = write_report(results, "x", tmp_path / "x.json")
        # Round-trip through JSON
        rt = json.loads(json.dumps(report))
        assert len(rt["results"]) == 2

    def test_parent_dir_created(self, tmp_path: Path) -> None:
        nested = tmp_path / "deep" / "nested" / "report.json"
        results = self._make_results(["PASS"])
        write_report(results, "nested-test", nested)
        assert nested.exists()


# ---------------------------------------------------------------------------
# Playwright smoke test (skipped if not importable)
# ---------------------------------------------------------------------------


def test_playwright_importable_smoke() -> None:
    """Minimal import check when playwright IS available; skip otherwise."""
    pytest.importorskip("playwright", reason="playwright not installed; browser smoke test skipped")

    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    with sync_playwright() as pw:
        assert pw is not None
