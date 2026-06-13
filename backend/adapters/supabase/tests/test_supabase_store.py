"""
tests/test_supabase_store.py — Unit tests for SupabaseEntityStore.

Uses httpx.MockTransport to intercept HTTP calls — no live Supabase project
required. Covers all 6 store methods plus slug→table resolution.

Test matrix:
    create          — returns representation row from PostgREST
    find_by_id hit  — returns first row when PostgREST returns 1-element list
    find_by_id miss — returns None when PostgREST returns empty list
    find_all        — returns full list
    patch hit       — returns updated representation; id stripped from PATCH body
    patch id-strip  — id key absent from the PATCH request body (guard check)
    patch miss      — returns None when PostgREST returns empty list
    delete          — always True (idempotent, even on 0-row match)
    slug→table catalog hit    — "employee" resolves to "hr_employee"
    slug→table catalog fallback — unknown slug uses slug.replace("-","_")

Design:
    MockTransport intercepts at the httpx layer. We swap supabase_store's
    imported _CLIENT with a mock client inside each test. Since _CLIENT is
    imported lazily inside each method (`from supabase_client import _CLIENT`),
    we patch supabase_client._CLIENT directly.

    env vars SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set before
    supabase_client is imported. We set them in conftest-equivalent module-level
    code below.
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from typing import Any
from unittest.mock import patch

# ── bootstrap: set required env vars before importing supabase_client ─────────
# Must happen before any import of supabase_client (which raises on missing vars)
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")

import httpx  # noqa: E402  (after env setup)

# ── ensure supabase adapter dir is on path ────────────────────────────────────
_ADAPTER_DIR = str(
    __import__("pathlib").Path(__file__).resolve().parents[1]
)
if _ADAPTER_DIR not in sys.path:
    sys.path.insert(0, _ADAPTER_DIR)

import supabase_client  # noqa: E402
import supabase_store   # noqa: E402
from supabase_store import SupabaseEntityStore, _resolve_table  # noqa: E402


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_transport(
    responses: list[tuple[int, Any]],
) -> httpx.MockTransport:
    """
    Build an httpx.MockTransport from a list of (status_code, body) pairs.
    Each intercepted request pops the next response from the list.
    body may be a dict/list (JSON-encoded) or bytes.
    """
    _queue = list(responses)

    def _handler(request: httpx.Request) -> httpx.Response:
        if not _queue:
            raise RuntimeError("MockTransport: unexpected request — queue empty")
        status, body = _queue.pop(0)
        if isinstance(body, (dict, list)):
            content = json.dumps(body).encode()
            headers = {"content-type": "application/json"}
        else:
            content = body if isinstance(body, bytes) else str(body).encode()
            headers = {}
        return httpx.Response(status, content=content, headers=headers)

    return httpx.MockTransport(_handler)


def _mock_client(responses: list[tuple[int, Any]]) -> httpx.Client:
    """Return an httpx.Client backed by a mock transport."""
    transport = _make_transport(responses)
    return httpx.Client(
        base_url=supabase_client.BASE_URL,
        headers=supabase_client.AUTH_HEADERS,
        transport=transport,
    )


# ── request inspector helper ──────────────────────────────────────────────────

class _InspectTransport:
    """
    Intercept a single request, capture it, and return a pre-canned response.
    Use this when you need to assert on what was sent to PostgREST.
    """

    def __init__(self, status: int, body: Any) -> None:
        self.captured: httpx.Request | None = None
        self._status = status
        self._body = body

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.captured = request
        body = self._body
        if isinstance(body, (dict, list)):
            content = json.dumps(body).encode()
            headers = {"content-type": "application/json"}
        else:
            content = body if isinstance(body, bytes) else str(body).encode()
            headers = {}
        return httpx.Response(self._status, content=content, headers=headers)

    def as_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=supabase_client.BASE_URL,
            headers=supabase_client.AUTH_HEADERS,
            transport=httpx.MockTransport(self),
        )


# ── test cases ────────────────────────────────────────────────────────────────

class TestSupabaseEntityStore(unittest.TestCase):

    def _store(self) -> SupabaseEntityStore:
        return SupabaseEntityStore()

    # ── create ────────────────────────────────────────────────────────────────

    def test_create_returns_representation_row(self) -> None:
        """create() POSTs data and returns the server-populated row (incl. uuid id)."""
        server_row = {
            "id": "aaa-111",
            "employee_number": "E001",
            "full_name": "Alice",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
        }
        mock = _mock_client([(201, [server_row])])

        with patch.object(supabase_client, "_CLIENT", mock):
            result = self._store().create("employee", {"employee_number": "E001", "full_name": "Alice"})

        self.assertEqual(result["id"], "aaa-111")
        self.assertEqual(result["employee_number"], "E001")
        self.assertIn("created_at", result)

    # ── find_by_id hit ────────────────────────────────────────────────────────

    def test_find_by_id_hit_returns_row(self) -> None:
        """find_by_id() returns the first row when PostgREST returns a 1-item list."""
        row = {"id": "aaa-111", "full_name": "Alice"}
        mock = _mock_client([(200, [row])])

        with patch.object(supabase_client, "_CLIENT", mock):
            result = self._store().find_by_id("employee", "aaa-111")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "aaa-111")

    # ── find_by_id miss ───────────────────────────────────────────────────────

    def test_find_by_id_miss_returns_none(self) -> None:
        """find_by_id() returns None when PostgREST returns an empty list."""
        mock = _mock_client([(200, [])])

        with patch.object(supabase_client, "_CLIENT", mock):
            result = self._store().find_by_id("employee", "nonexistent-id")

        self.assertIsNone(result)

    # ── find_all ──────────────────────────────────────────────────────────────

    def test_find_all_returns_list(self) -> None:
        """find_all() returns all rows from PostgREST as a list."""
        rows = [
            {"id": "aaa-001", "full_name": "Alice"},
            {"id": "aaa-002", "full_name": "Bob"},
        ]
        mock = _mock_client([(200, rows)])

        with patch.object(supabase_client, "_CLIENT", mock):
            result = self._store().find_all("employee")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["full_name"], "Alice")
        self.assertEqual(result[1]["full_name"], "Bob")

    def test_find_all_empty_returns_empty_list(self) -> None:
        """find_all() returns [] when no rows exist."""
        mock = _mock_client([(200, [])])

        with patch.object(supabase_client, "_CLIENT", mock):
            result = self._store().find_all("employee")

        self.assertEqual(result, [])

    # ── patch hit ─────────────────────────────────────────────────────────────

    def test_patch_hit_returns_updated_row(self) -> None:
        """patch() returns the updated representation row on success."""
        updated_row = {"id": "aaa-111", "full_name": "Alice Updated"}
        mock = _mock_client([(200, [updated_row])])

        with patch.object(supabase_client, "_CLIENT", mock):
            result = self._store().patch("employee", "aaa-111", {"full_name": "Alice Updated"})

        self.assertIsNotNone(result)
        self.assertEqual(result["full_name"], "Alice Updated")

    # ── patch: id not overwritable ────────────────────────────────────────────

    def test_patch_strips_id_from_request_body(self) -> None:
        """
        patch() must NOT send 'id' in the PATCH body even if caller includes it.
        Inspect the outgoing request body to confirm id is stripped.
        """
        updated_row = {"id": "aaa-111", "full_name": "Alice"}
        inspector = _InspectTransport(200, [updated_row])

        with patch.object(supabase_client, "_CLIENT", inspector.as_client()):
            self._store().patch("employee", "aaa-111", {"id": "INJECTED", "full_name": "Alice"})

        self.assertIsNotNone(inspector.captured)
        sent_body = json.loads(inspector.captured.content)
        self.assertNotIn("id", sent_body, "id must be stripped from PATCH body")
        self.assertEqual(sent_body.get("full_name"), "Alice")

    # ── patch miss ────────────────────────────────────────────────────────────

    def test_patch_miss_returns_none(self) -> None:
        """patch() returns None when PostgREST returns 0 rows (id not found)."""
        mock = _mock_client([(200, [])])

        with patch.object(supabase_client, "_CLIENT", mock):
            result = self._store().patch("employee", "nonexistent-id", {"full_name": "X"})

        self.assertIsNone(result)

    # ── delete ────────────────────────────────────────────────────────────────

    def test_delete_returns_true(self) -> None:
        """delete() always returns True (idempotent per wire-v1.yaml Growth-5d)."""
        # 204 No Content is a typical PostgREST delete response
        mock = _mock_client([(204, b"")])

        with patch.object(supabase_client, "_CLIENT", mock):
            result = self._store().delete("employee", "aaa-111")

        self.assertTrue(result)

    def test_delete_idempotent_on_missing_id(self) -> None:
        """delete() returns True even when the id does not exist (0-row match)."""
        # PostgREST returns 204 regardless of whether rows were matched
        mock = _mock_client([(204, b"")])

        with patch.object(supabase_client, "_CLIENT", mock):
            result = self._store().delete("employee", "id-that-does-not-exist")

        self.assertTrue(result)

    # ── slug→table: catalog hit ───────────────────────────────────────────────

    def test_resolve_table_catalog_hit(self) -> None:
        """Known catalog slug "employee" must resolve to "hr_employee"."""
        # This checks that catalog.yaml was loaded and the table: field is used.
        table = _resolve_table("employee")
        self.assertEqual(
            table,
            "hr_employee",
            f"Expected 'hr_employee' for slug 'employee', got '{table}'. "
            "Check that catalog.yaml is readable and has employee.table: hr_employee.",
        )

    def test_resolve_table_catalog_hit_department(self) -> None:
        """Known catalog slug "department" must resolve to "hr_department"."""
        table = _resolve_table("department")
        self.assertEqual(table, "hr_department")

    # ── slug→table: catalog fallback ──────────────────────────────────────────

    def test_resolve_table_catalog_fallback_hyphen(self) -> None:
        """Unknown slug with hyphen falls back to slug.replace('-','_')."""
        table = _resolve_table("stock-level")
        # "stock-level" is either in catalog (→ its table:) or falls back to "stock_level"
        # Fallback: hyphens replaced with underscores
        if table != "stock_level":
            # catalog has it — verify it doesn't contain a hyphen
            self.assertNotIn("-", table, "table name must not contain hyphens")
        else:
            self.assertEqual(table, "stock_level")

    def test_resolve_table_unknown_slug_fallback(self) -> None:
        """Completely unknown slug uses replace('-','_') fallback."""
        table = _resolve_table("unknown-entity-xyz-987")
        self.assertEqual(table, "unknown_entity_xyz_987")

    # ── http error surfacing ──────────────────────────────────────────────────

    def test_create_raises_on_5xx(self) -> None:
        """create() raises httpx.HTTPStatusError on server error (status.health can detect)."""
        mock = _mock_client([(500, {"message": "Internal Server Error"})])

        with patch.object(supabase_client, "_CLIENT", mock):
            with self.assertRaises(httpx.HTTPStatusError):
                self._store().create("employee", {"full_name": "Alice"})

    def test_find_all_raises_on_4xx(self) -> None:
        """find_all() raises on 4xx (e.g. table not found in PostgREST)."""
        mock = _mock_client([(404, {"message": "relation not found"})])

        with patch.object(supabase_client, "_CLIENT", mock):
            with self.assertRaises(httpx.HTTPStatusError):
                self._store().find_all("nonexistent-table-xyz")


if __name__ == "__main__":
    unittest.main()
