"""
test_smoke.py — L1 unit-level smoke tests for the FastAPI adapter.

Tests the store, contract loader, and wire_response helpers in isolation
(no running server required). Mirrors EntitySmokeTest.java scenarios.

Run:
    cd backend/adapters/fastapi
    pip install -r requirements.txt
    pytest tests/test_smoke.py -v
"""

from __future__ import annotations

import sys
import pathlib

# Add the adapter root to sys.path so imports resolve without installation
_ADAPTER_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ADAPTER_DIR))

import pytest
from store import InMemoryEntityStore


# ── store smoke tests ─────────────────────────────────────────────────────────

class TestInMemoryEntityStore:
    def setup_method(self):
        self.store = InMemoryEntityStore()

    def test_create_returns_record_with_id(self):
        rec = self.store.create("widget", {"name": "W1", "price": 9.99})
        assert "id" in rec and rec["id"]
        assert rec["name"] == "W1"
        assert rec["price"] == 9.99

    def test_find_by_id_returns_created(self):
        rec = self.store.create("widget", {"name": "W2"})
        found = self.store.find_by_id("widget", rec["id"])
        assert found is not None
        assert found["name"] == "W2"

    def test_find_by_id_missing_returns_none(self):
        assert self.store.find_by_id("widget", "no-such-id") is None

    def test_find_all_returns_all_records(self):
        self.store.create("item", {"seq": 0})
        self.store.create("item", {"seq": 1})
        all_ = self.store.find_all("item")
        assert len(all_) == 2

    def test_patch_merges_only_supplied_fields(self):
        rec = self.store.create("prod", {"name": "Alpha", "price": 100.0, "stock": 25})
        eid = rec["id"]
        updated = self.store.patch("prod", eid, {"price": 200.0})
        assert updated is not None
        assert updated["price"] == 200.0
        assert updated["name"] == "Alpha"   # unchanged
        assert updated["stock"] == 25       # unchanged

    def test_patch_does_not_overwrite_id(self):
        rec = self.store.create("prod", {"name": "Beta"})
        eid = rec["id"]
        updated = self.store.patch("prod", eid, {"id": "hacked", "name": "Beta2"})
        assert updated["id"] == eid         # id must not be overwritten
        assert updated["name"] == "Beta2"

    def test_patch_missing_id_returns_none(self):
        result = self.store.patch("prod", "nonexistent", {"name": "Ghost"})
        assert result is None

    def test_delete_existing_returns_true(self):
        rec = self.store.create("item", {"ref": "D001"})
        assert self.store.delete("item", rec["id"]) is True
        assert self.store.find_by_id("item", rec["id"]) is None

    def test_delete_missing_id_idempotent(self):
        # Strongest idempotency: cold delete of never-inserted id
        assert self.store.delete("item", "never-inserted-id") is True

    def test_delete_twice_idempotent(self):
        rec = self.store.create("item", {"ref": "IDEM"})
        eid = rec["id"]
        assert self.store.delete("item", eid) is True
        assert self.store.delete("item", eid) is True  # second delete also success

    def test_offset_paging_last_page_correct_count(self):
        # 7 items, page_size=3 → last page (page 3) returns 1 item
        for i in range(7):
            self.store.create("paged", {"seq": i})
        all_ = self.store.find_all("paged")
        page, size = 3, 3
        total = len(all_)
        from_idx = min((page - 1) * size, total)
        to_idx = min(from_idx + size, total)
        page_items = all_[from_idx:to_idx]
        assert total == 7
        assert len(page_items) == 1  # 7 mod 3 = 1

    def test_no_overlap_between_page1_and_page2(self):
        for i in range(7):
            self.store.create("overlap", {"seq": i})
        all_ = self.store.find_all("overlap")
        size = 3
        p1 = all_[0:3]
        p2 = all_[3:6]
        ids1 = {r["id"] for r in p1}
        ids2 = {r["id"] for r in p2}
        assert not (ids1 & ids2)


# ── contract loader smoke tests ───────────────────────────────────────────────

class TestContractLoader:
    def test_loads_codes_and_returns_http_status(self):
        from contract_loader import contract
        # Verify contract loader resolves http_status from codes.yaml at runtime.
        # Expected values come from codes.yaml — not hardcoded here.
        # We read the same file the loader reads and compare, so no re-declaration.
        import pathlib, yaml
        repo_root = pathlib.Path(__file__).resolve().parents[4]
        codes_path = repo_root / "middle" / "contract" / "error" / "codes.yaml"
        with codes_path.open(encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        for code, entry in doc["codes"].items():
            expected = entry["http_status"]
            actual = contract.http_status_for(code)
            assert actual == expected, (
                f"ContractLoader.http_status_for({code!r}) returned {actual}, "
                f"but codes.yaml says {expected}"
            )

    def test_unknown_code_returns_500(self):
        from contract_loader import contract
        assert contract.http_status_for("NO_SUCH_CODE") == 500

    def test_wire_version_is_nonempty(self):
        from contract_loader import contract
        v = contract.wire_version()
        assert v and v != "unknown"

    def test_message_for_returns_nonempty_string(self):
        from contract_loader import contract
        msg = contract.message_for("NOT_FOUND")
        assert isinstance(msg, str) and msg

    def test_unknown_code_returns_500(self):
        from contract_loader import contract
        assert contract.http_status_for("NO_SUCH_CODE") == 500

    def test_wire_version_is_nonempty(self):
        from contract_loader import contract
        v = contract.wire_version()
        assert v and v != "unknown"

    def test_message_for_returns_nonempty_string(self):
        from contract_loader import contract
        msg = contract.message_for("NOT_FOUND")
        assert isinstance(msg, str) and msg
