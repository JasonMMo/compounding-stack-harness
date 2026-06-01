"""
tests/test_manifest_loader.py — L1 unit tests for manifest_loader.py.

Verifies:
- ManifestLoader returns no-manifest state when PROFILE_MANIFEST is unset.
- Loads shop-demo manifest when env var points to out/shop-demo/screen-manifest.json.
- entity_fields("sales-order") returns the typed list with expected controls.
- entity_fields for an absent entity returns None (triggers fallback).
- Fields missing optional max_length / unique keys are handled without error.
- hidden_fields returns the correct list.
- label() returns the human-readable entity label.
"""

import os
import pathlib
import sys

import pytest

# Ensure adapter package root is importable
_ADAPTER_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_ADAPTER_ROOT))

# Resolve shop-demo manifest path — repo root is 4 levels up from tests/
_REPO_ROOT = _ADAPTER_ROOT.parent.parent.parent.parent  # …/compounding-stack-harness
_MANIFEST_PATH = _REPO_ROOT / "out" / "shop-demo" / "screen-manifest.json"


# ---------------------------------------------------------------------------
# Helper: fresh loader without polluting module-level singleton
# ---------------------------------------------------------------------------

def _make_loader(path: str | None = None):
    """Instantiate a fresh ManifestLoader; avoids get_manifest_loader() singleton."""
    # Reload to avoid singleton state leaking between tests
    import importlib
    import manifest_loader as ml_mod
    importlib.reload(ml_mod)
    return ml_mod.ManifestLoader(manifest_path=path)


# ---------------------------------------------------------------------------
# No-manifest state (PROFILE_MANIFEST unset)
# ---------------------------------------------------------------------------

class TestNoManifest:
    def test_loader_not_loaded_when_path_absent(self, monkeypatch):
        monkeypatch.delenv("PROFILE_MANIFEST", raising=False)
        loader = _make_loader(path=None)
        assert not loader.is_loaded()

    def test_entity_fields_returns_none_when_not_loaded(self, monkeypatch):
        monkeypatch.delenv("PROFILE_MANIFEST", raising=False)
        loader = _make_loader(path=None)
        assert loader.entity_fields("sales-order") is None

    def test_hidden_fields_returns_empty_when_not_loaded(self, monkeypatch):
        monkeypatch.delenv("PROFILE_MANIFEST", raising=False)
        loader = _make_loader(path=None)
        assert loader.hidden_fields("sales-order") == []

    def test_label_returns_none_when_not_loaded(self, monkeypatch):
        monkeypatch.delenv("PROFILE_MANIFEST", raising=False)
        loader = _make_loader(path=None)
        assert loader.label("sales-order") is None

    def test_entity_keys_empty_when_not_loaded(self, monkeypatch):
        monkeypatch.delenv("PROFILE_MANIFEST", raising=False)
        loader = _make_loader(path=None)
        assert loader.entity_keys() == []

    def test_missing_file_path_gives_not_loaded(self, tmp_path):
        nonexistent = str(tmp_path / "does-not-exist.json")
        loader = _make_loader(path=nonexistent)
        assert not loader.is_loaded()


# ---------------------------------------------------------------------------
# shop-demo manifest loading
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def shop_loader():
    """One ManifestLoader pointed at out/shop-demo/screen-manifest.json."""
    if not _MANIFEST_PATH.is_file():
        pytest.skip(
            f"shop-demo manifest not found at {_MANIFEST_PATH}. "
            "Run: python scripts/workflow/scaffold.py --profile shop-demo"
        )
    import importlib
    import manifest_loader as ml_mod
    importlib.reload(ml_mod)
    return ml_mod.ManifestLoader(manifest_path=str(_MANIFEST_PATH))


class TestShopDemoLoad:
    def test_is_loaded(self, shop_loader):
        assert shop_loader.is_loaded()

    def test_profile_is_shop_demo(self, shop_loader):
        assert shop_loader.profile() == "shop-demo"

    def test_entity_keys_non_empty(self, shop_loader):
        keys = shop_loader.entity_keys()
        assert len(keys) > 0

    def test_sales_order_present(self, shop_loader):
        assert "sales-order" in shop_loader.entity_keys()


# ---------------------------------------------------------------------------
# entity_fields("sales-order")
# ---------------------------------------------------------------------------

class TestSalesOrderFields:
    def test_entity_fields_returns_list(self, shop_loader):
        fields = shop_loader.entity_fields("sales-order")
        assert isinstance(fields, list)
        assert len(fields) > 0

    def test_all_fields_have_required_keys(self, shop_loader):
        fields = shop_loader.entity_fields("sales-order")
        for f in fields:
            assert "name" in f, f"Missing 'name' in {f}"
            assert "control" in f, f"Missing 'control' in {f}"
            assert "required" in f, f"Missing 'required' in {f}"
            assert "label" in f, f"Missing 'label' in {f}"

    def test_controls_are_valid_values(self, shop_loader):
        valid_controls = {"text", "textarea", "number", "date", "datetime", "select", "checkbox", "fk-text"}
        fields = shop_loader.entity_fields("sales-order")
        for f in fields:
            assert f["control"] in valid_controls, (
                f"Field '{f['name']}' has unknown control '{f['control']}'"
            )

    def test_has_select_control_for_status(self, shop_loader):
        fields = shop_loader.entity_fields("sales-order")
        status_field = next((f for f in fields if f["name"] == "status"), None)
        assert status_field is not None, "status field not found in sales-order"
        assert status_field["control"] == "select"
        assert isinstance(status_field.get("options"), list)
        assert len(status_field["options"]) > 0

    def test_has_date_control_for_order_date(self, shop_loader):
        fields = shop_loader.entity_fields("sales-order")
        date_field = next((f for f in fields if f["name"] == "order_date"), None)
        assert date_field is not None, "order_date field not found in sales-order"
        assert date_field["control"] == "date"

    def test_has_number_control_for_total_amount(self, shop_loader):
        fields = shop_loader.entity_fields("sales-order")
        amount_field = next((f for f in fields if f["name"] == "total_amount"), None)
        assert amount_field is not None, "total_amount field not found in sales-order"
        assert amount_field["control"] == "number"

    def test_fk_text_field_has_fk_entity(self, shop_loader):
        """price_list_id is fk-text in sales-order — must carry fk_entity."""
        fields = shop_loader.entity_fields("sales-order")
        fk_fields = [f for f in fields if f["control"] == "fk-text"]
        assert fk_fields, "Expected at least one fk-text field in sales-order"
        for f in fk_fields:
            assert "fk_entity" in f, f"fk-text field '{f['name']}' missing fk_entity"


# ---------------------------------------------------------------------------
# Absent entity → None (triggers fallback)
# ---------------------------------------------------------------------------

class TestAbsentEntity:
    def test_absent_entity_returns_none(self, shop_loader):
        result = shop_loader.entity_fields("nonexistent-entity-xyz")
        assert result is None

    def test_absent_entity_hidden_fields_empty(self, shop_loader):
        result = shop_loader.hidden_fields("nonexistent-entity-xyz")
        assert result == []

    def test_absent_entity_label_none(self, shop_loader):
        result = shop_loader.label("nonexistent-entity-xyz")
        assert result is None


# ---------------------------------------------------------------------------
# Optional field keys: max_length and unique
# ---------------------------------------------------------------------------

class TestOptionalFieldKeys:
    def test_field_without_max_length_ok(self, shop_loader):
        """Fields that lack max_length must not raise — treat as no limit."""
        fields = shop_loader.entity_fields("sales-order")
        for f in fields:
            # Accessing .get("max_length") must never KeyError
            val = f.get("max_length")
            # val is either an int or None — both are acceptable
            assert val is None or isinstance(val, int), (
                f"max_length for '{f['name']}' has unexpected type {type(val)}"
            )

    def test_field_without_unique_ok(self, shop_loader):
        """Fields that lack unique must not raise — treat as not unique."""
        fields = shop_loader.entity_fields("sales-order")
        for f in fields:
            val = f.get("unique")
            assert val is None or isinstance(val, bool), (
                f"unique for '{f['name']}' has unexpected type {type(val)}"
            )

    def test_text_field_with_max_length_present(self, shop_loader):
        """currency field in sales-order has max_length=8 in the catalog."""
        fields = shop_loader.entity_fields("sales-order")
        currency = next((f for f in fields if f["name"] == "currency"), None)
        assert currency is not None, "currency field not found in sales-order"
        assert currency.get("max_length") == 8, (
            f"Expected max_length=8 for currency, got {currency.get('max_length')}"
        )


# ---------------------------------------------------------------------------
# hidden_fields and label
# ---------------------------------------------------------------------------

class TestHiddenAndLabel:
    def test_sales_order_hidden_fields(self, shop_loader):
        hidden = shop_loader.hidden_fields("sales-order")
        assert isinstance(hidden, list)
        assert "id" in hidden
        assert "created_at" in hidden
        assert "updated_at" in hidden

    def test_sales_order_label(self, shop_loader):
        lbl = shop_loader.label("sales-order")
        assert lbl == "Sales Order"

    def test_sales_order_line_fk_text_order_id(self, shop_loader):
        """sales-order-line.order_id must be fk-text with fk_entity=sales-order."""
        fields = shop_loader.entity_fields("sales-order-line")
        assert fields is not None, "sales-order-line not in manifest"
        order_id = next((f for f in fields if f["name"] == "order_id"), None)
        assert order_id is not None, "order_id field not found in sales-order-line"
        assert order_id["control"] == "fk-text"
        assert order_id["fk_entity"] == "sales-order"


# ---------------------------------------------------------------------------
# PROFILE_MANIFEST env var wiring
# ---------------------------------------------------------------------------

class TestEnvVarWiring:
    def test_env_var_loads_manifest(self, monkeypatch):
        if not _MANIFEST_PATH.is_file():
            pytest.skip("shop-demo manifest not generated yet")
        monkeypatch.setenv("PROFILE_MANIFEST", str(_MANIFEST_PATH))
        import importlib
        import manifest_loader as ml_mod
        importlib.reload(ml_mod)
        loader = ml_mod.ManifestLoader()  # reads from env var
        assert loader.is_loaded()
        assert loader.profile() == "shop-demo"
