"""test_scaffold.py — Phase 1 scaffold + manifest tests.

Layers covered:
  L1 (pytest): manifest column classification, hidden fields, determinism.
  L1 (pytest): scaffold validation (good profile + bad entity key → rc=1).
  L1 (dogfood): actually run scaffold.py --profile shop-demo and verify artifacts.

Run:
  pytest scripts/workflow/tests/test_scaffold.py -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WORKFLOW_DIR = REPO_ROOT / "scripts" / "workflow"
RENDER_DIR = REPO_ROOT / "presets" / "ddl"

# Ensure manifest + render are importable
if str(WORKFLOW_DIR) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_DIR))
if str(RENDER_DIR) not in sys.path:
    sys.path.insert(0, str(RENDER_DIR))

from manifest import build_manifest, _HIDDEN_NAMES  # noqa: E402
from render import load_catalog  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def catalog():
    return load_catalog()


@pytest.fixture(scope="session")
def shop_entity_keys():
    return ["contact", "sales-order", "sales-order-line"]


@pytest.fixture(scope="session")
def shop_manifest(catalog, shop_entity_keys):
    return build_manifest("shop-demo", shop_entity_keys, catalog)


# ---------------------------------------------------------------------------
# Manifest: hidden fields
# ---------------------------------------------------------------------------

class TestHiddenFields:
    def test_id_is_hidden(self, shop_manifest):
        for entity_key, entity in shop_manifest["entities"].items():
            assert "id" in entity["hidden_fields"], (
                f"{entity_key}: 'id' must be in hidden_fields"
            )

    def test_created_at_is_hidden(self, shop_manifest):
        for entity_key, entity in shop_manifest["entities"].items():
            assert "created_at" in entity["hidden_fields"], (
                f"{entity_key}: 'created_at' must be in hidden_fields"
            )

    def test_updated_at_is_hidden(self, shop_manifest):
        for entity_key, entity in shop_manifest["entities"].items():
            assert "updated_at" in entity["hidden_fields"], (
                f"{entity_key}: 'updated_at' must be in hidden_fields"
            )

    def test_hidden_fields_not_in_fields(self, shop_manifest):
        for entity_key, entity in shop_manifest["entities"].items():
            field_names = {f["name"] for f in entity["fields"]}
            for hidden in entity["hidden_fields"]:
                assert hidden not in field_names, (
                    f"{entity_key}: hidden field '{hidden}' must not appear in fields"
                )

    def test_hidden_names_set_contents(self):
        assert _HIDDEN_NAMES == frozenset({"id", "created_at", "updated_at"})


# ---------------------------------------------------------------------------
# Manifest: enum → select with options
# ---------------------------------------------------------------------------

class TestEnumControl:
    def test_contact_type_is_select(self, shop_manifest):
        contact = shop_manifest["entities"]["contact"]
        ct_field = next((f for f in contact["fields"] if f["name"] == "contact_type"), None)
        assert ct_field is not None, "contact.contact_type field must be present"
        assert ct_field["control"] == "select"
        assert ct_field["options"] == ["prospect", "customer", "partner", "vendor"]

    def test_sales_order_status_is_select(self, shop_manifest):
        so = shop_manifest["entities"]["sales-order"]
        status_field = next((f for f in so["fields"] if f["name"] == "status"), None)
        assert status_field is not None, "sales-order.status field must be present"
        assert status_field["control"] == "select"
        assert "draft" in status_field["options"]
        assert "cancelled" in status_field["options"]

    def test_enum_options_are_list(self, shop_manifest):
        for entity_key, entity in shop_manifest["entities"].items():
            for field in entity["fields"]:
                if field["control"] == "select":
                    assert isinstance(field["options"], list), (
                        f"{entity_key}.{field['name']}: options must be list"
                    )
                    assert len(field["options"]) > 0, (
                        f"{entity_key}.{field['name']}: options must be non-empty"
                    )


# ---------------------------------------------------------------------------
# Manifest: FK → fk-text with fk_entity
# ---------------------------------------------------------------------------

class TestFkControl:
    def test_sales_order_line_order_id_is_fk_text(self, shop_manifest):
        sol = shop_manifest["entities"]["sales-order-line"]
        order_id_field = next((f for f in sol["fields"] if f["name"] == "order_id"), None)
        assert order_id_field is not None, "sales-order-line.order_id must be present"
        assert order_id_field["control"] == "fk-text"
        assert order_id_field["fk_entity"] == "sales-order"
        assert order_id_field["note"] == "FK dropdown deferred (M1)"

    def test_sales_order_line_item_id_is_fk_text(self, shop_manifest):
        sol = shop_manifest["entities"]["sales-order-line"]
        item_id_field = next((f for f in sol["fields"] if f["name"] == "item_id"), None)
        assert item_id_field is not None, "sales-order-line.item_id must be present"
        assert item_id_field["control"] == "fk-text"
        assert item_id_field["fk_entity"] == "item"

    def test_contact_owner_id_is_fk_text(self, shop_manifest):
        contact = shop_manifest["entities"]["contact"]
        owner_field = next((f for f in contact["fields"] if f["name"] == "owner_id"), None)
        assert owner_field is not None, "contact.owner_id must be present"
        assert owner_field["control"] == "fk-text"
        assert owner_field["fk_entity"] == "employee"

    def test_fk_text_has_fk_entity_key(self, shop_manifest):
        for entity_key, entity in shop_manifest["entities"].items():
            for field in entity["fields"]:
                if field["control"] == "fk-text":
                    assert "fk_entity" in field, (
                        f"{entity_key}.{field['name']}: fk-text must have fk_entity"
                    )
                    assert field["fk_entity"], (
                        f"{entity_key}.{field['name']}: fk_entity must be non-empty"
                    )


# ---------------------------------------------------------------------------
# Manifest: required reflects nullable
# ---------------------------------------------------------------------------

class TestRequired:
    def test_required_reflects_nullable(self, catalog, shop_entity_keys):
        all_entities = catalog["entities"]
        manifest = build_manifest("shop-demo", shop_entity_keys, catalog)
        for entity_key in shop_entity_keys:
            ent = all_entities[entity_key]
            columns = ent.get("columns", {})
            entity_manifest = manifest["entities"][entity_key]
            field_map = {f["name"]: f for f in entity_manifest["fields"]}
            for col_name, col_def in columns.items():
                if col_name in _HIDDEN_NAMES:
                    continue
                nullable = col_def.get("nullable", True)
                expected_required = not nullable
                field = field_map.get(col_name)
                assert field is not None, (
                    f"{entity_key}.{col_name}: field missing from manifest"
                )
                assert field["required"] == expected_required, (
                    f"{entity_key}.{col_name}: required={field['required']} "
                    f"but nullable={nullable} in catalog"
                )

    def test_contact_full_name_required(self, shop_manifest):
        contact = shop_manifest["entities"]["contact"]
        fn_field = next((f for f in contact["fields"] if f["name"] == "full_name"), None)
        assert fn_field is not None
        assert fn_field["required"] is True

    def test_contact_email_not_required(self, shop_manifest):
        contact = shop_manifest["entities"]["contact"]
        email_field = next((f for f in contact["fields"] if f["name"] == "email"), None)
        assert email_field is not None
        assert email_field["required"] is False


# ---------------------------------------------------------------------------
# Manifest: determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_build_twice_identical_dict(self, catalog, shop_entity_keys):
        m1 = build_manifest("shop-demo", shop_entity_keys, catalog)
        m2 = build_manifest("shop-demo", shop_entity_keys, catalog)
        assert m1 == m2, "Two build_manifest() calls must return identical dicts"

    def test_build_twice_identical_bytes(self, catalog, shop_entity_keys):
        m1 = build_manifest("shop-demo", shop_entity_keys, catalog)
        m2 = build_manifest("shop-demo", shop_entity_keys, catalog)
        j1 = json.dumps(m1, indent=2, sort_keys=False)
        j2 = json.dumps(m2, indent=2, sort_keys=False)
        assert j1 == j2, "Two build_manifest() serializations must be byte-identical"

    def test_profile_and_catalog_version_present(self, shop_manifest):
        assert shop_manifest["profile"] == "shop-demo"
        assert "catalog_version" in shop_manifest
        assert shop_manifest["catalog_version"] == "1.0"


# ---------------------------------------------------------------------------
# Scaffold: validation guards
# ---------------------------------------------------------------------------

class TestScaffoldValidation:
    def test_shop_demo_validates_ok(self, tmp_path):
        """shop-demo profile has only valid catalog keys — must exit 0."""
        result = subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "shop-demo",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"scaffold.py --profile shop-demo failed:\n{result.stderr}"
        )

    def test_bad_entity_returns_rc1(self, tmp_path):
        """A profile with a nonexistent entity key must return rc=1 and name the key."""
        # Write a minimal bad profile to tmp_path
        bad_profile_path = REPO_ROOT / "profiles" / "_test-bad-entity.yaml"
        bad_profile_path.write_text(
            "version: 1\n"
            "customer:\n"
            "  slug: _test-bad-entity\n"
            "  display: Test\n"
            "  status: draft\n"
            "  industry: generic\n"
            "stack:\n"
            "  frontend: vanilla-htmx\n"
            "  backend: fastapi\n"
            "ddl:\n"
            "  dialect: postgres\n"
            "  schema: test\n"
            "  idempotent_strategy: on_conflict\n"
            "domains:\n"
            "  - slug: sales\n"
            "    display: Sales\n"
            "    entities: [nonexistent-entity-xyz]\n"
            "    seen_at: 2026-06-01\n",
            encoding="utf-8",
        )
        try:
            result = subprocess.run(
                [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
                 "--profile", "_test-bad-entity",
                 "--out", str(tmp_path)],
                capture_output=True, text=True,
                cwd=str(REPO_ROOT),
            )
            assert result.returncode == 1, (
                "scaffold.py must return rc=1 for missing entity key"
            )
            assert "nonexistent-entity-xyz" in result.stderr, (
                f"Error message must name the missing key. stderr:\n{result.stderr}"
            )
        finally:
            bad_profile_path.unlink(missing_ok=True)

    def test_missing_profile_returns_rc1(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "does-not-exist-profile",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 1


# ---------------------------------------------------------------------------
# Dogfood: run scaffold for real and verify artifacts
# ---------------------------------------------------------------------------

class TestDogfoodScaffold:
    def test_scaffold_produces_sql(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "shop-demo",
             "--dialect", "postgres",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, f"scaffold failed:\n{result.stderr}"
        sql_path = tmp_path / "shop-demo" / "ddl" / "postgres.sql"
        assert sql_path.exists(), "postgres.sql must be created"
        sql_content = sql_path.read_text(encoding="utf-8")
        # At least one CREATE TABLE must be present
        assert "CREATE TABLE" in sql_content, "DDL must contain CREATE TABLE"
        # Spot-check: crm_contact table
        assert "crm_contact" in sql_content, "DDL must contain crm_contact table"

    def test_scaffold_produces_manifest(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "shop-demo",
             "--dialect", "postgres",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, f"scaffold failed:\n{result.stderr}"
        manifest_path = tmp_path / "shop-demo" / "screen-manifest.json"
        assert manifest_path.exists(), "screen-manifest.json must be created"

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["profile"] == "shop-demo"
        assert "contact" in manifest["entities"]
        assert "sales-order" in manifest["entities"]
        assert "sales-order-line" in manifest["entities"]

    def test_manifest_matches_classification_rules(self, tmp_path):
        subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "shop-demo",
             "--dialect", "postgres",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
            check=True,
        )
        manifest = json.loads(
            (tmp_path / "shop-demo" / "screen-manifest.json").read_text(encoding="utf-8")
        )
        # contact.contact_type → select
        contact = manifest["entities"]["contact"]
        ct = next(f for f in contact["fields"] if f["name"] == "contact_type")
        assert ct["control"] == "select"
        # sales-order.order_number → text with unique
        so = manifest["entities"]["sales-order"]
        on_field = next(f for f in so["fields"] if f["name"] == "order_number")
        assert on_field["control"] == "text"
        assert on_field.get("unique") is True
        # sales-order-line.order_id → fk-text
        sol = manifest["entities"]["sales-order-line"]
        oid = next(f for f in sol["fields"] if f["name"] == "order_id")
        assert oid["control"] == "fk-text"
        assert oid["fk_entity"] == "sales-order"

    def test_manifest_determinism_across_scaffold_runs(self, tmp_path):
        """Two scaffold invocations must produce byte-identical manifest."""
        out1 = tmp_path / "run1"
        out2 = tmp_path / "run2"
        for out in (out1, out2):
            subprocess.run(
                [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
                 "--profile", "shop-demo",
                 "--out", str(out)],
                capture_output=True, text=True,
                cwd=str(REPO_ROOT),
                check=True,
            )
        m1 = (out1 / "shop-demo" / "screen-manifest.json").read_text(encoding="utf-8")
        m2 = (out2 / "shop-demo" / "screen-manifest.json").read_text(encoding="utf-8")
        assert m1 == m2, "Two scaffold runs must produce byte-identical manifests"
