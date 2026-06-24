"""
tests/test_form_coercion.py — L1 unit tests for form-value type coercion.

Why this file exists:
  HTTP form submissions deliver all values as strings. The backend contract
  (catalog_validator.py) enforces strict Python types for decimal/integer/boolean
  fields and rejects strings with a 422 error.  _coerce_form_value and
  _coerce_form_data (added in the F-5 fix) translate form strings to the
  correct Python types before the payload is forwarded to the backend.

What this pins:
  - decimal "5000000"  → int 5000000   (whole-number — avoids float precision loss)
  - decimal "1000.50"  → float 1000.5
  - integer "42"       → int 42
  - boolean "true"/"1"/"on"/"yes" → True; "false"/"0"/"" corner cases
  - string/text/date/enum fields  → unchanged (str)
  - bad numeric string ("abc")    → original string returned (backend 422 path)
  - empty values                  → excluded upstream (not passed to coercion)
  - _coerce_form_data: manifest-driven; no-manifest mode leaves all as str
"""

import pathlib
import sys
import json
import os

import pytest

# Ensure the adapter package root is importable (same pattern as sibling tests).
_ADAPTER_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_ADAPTER_ROOT))

# Resolve taskflow-demo manifest (decimal/integer/boolean fields available)
_REPO_ROOT = _ADAPTER_ROOT.parent.parent.parent.parent  # …/compounding-stack-harness
_TASKFLOW_MANIFEST = _REPO_ROOT / "out" / "taskflow-demo" / "screen-manifest.json"


# ---------------------------------------------------------------------------
# _coerce_form_value — pure unit tests (no manifest required)
# ---------------------------------------------------------------------------

import server  # noqa: E402  — imports the adapter; side-effects at module level


class TestCoerceFormValue:
    """Tests for the _coerce_form_value(v, field_type) helper."""

    # ---- decimal -------------------------------------------------------

    def test_decimal_whole_number_becomes_int(self):
        """Whole-number decimal strings (e.g. budget "5000000") must become int."""
        assert server._coerce_form_value("5000000", "decimal") == 5000000
        assert isinstance(server._coerce_form_value("5000000", "decimal"), int)

    def test_decimal_fractional_becomes_float(self):
        """Fractional decimal strings must become float."""
        result = server._coerce_form_value("1000.50", "decimal")
        assert result == pytest.approx(1000.50)
        assert isinstance(result, float)

    def test_decimal_zero_whole(self):
        assert server._coerce_form_value("0", "decimal") == 0
        assert isinstance(server._coerce_form_value("0", "decimal"), int)

    def test_decimal_zero_fractional(self):
        result = server._coerce_form_value("0.00", "decimal")
        assert result == pytest.approx(0.0)
        assert isinstance(result, float)

    def test_decimal_bad_string_returns_original(self):
        """Non-numeric string → return as-is so backend produces clear 422."""
        assert server._coerce_form_value("abc", "decimal") == "abc"

    # ---- integer -------------------------------------------------------

    def test_integer_string_becomes_int(self):
        assert server._coerce_form_value("42", "integer") == 42
        assert isinstance(server._coerce_form_value("42", "integer"), int)

    def test_integer_zero(self):
        assert server._coerce_form_value("0", "integer") == 0

    def test_integer_bad_string_returns_original(self):
        assert server._coerce_form_value("3.14", "integer") == "3.14"

    # ---- boolean -------------------------------------------------------

    def test_boolean_true_variants(self):
        for v in ("true", "True", "TRUE", "1", "on", "ON", "yes", "YES"):
            assert server._coerce_form_value(v, "boolean") is True, f"expected True for {v!r}"

    def test_boolean_false_variants(self):
        for v in ("false", "False", "0", "off", "no", ""):
            assert server._coerce_form_value(v, "boolean") is False, f"expected False for {v!r}"

    # ---- passthrough types ---------------------------------------------

    def test_string_field_unchanged(self):
        assert server._coerce_form_value("hello world", "string") == "hello world"

    def test_text_field_unchanged(self):
        assert server._coerce_form_value("multi\nline", "text") == "multi\nline"

    def test_date_field_unchanged(self):
        assert server._coerce_form_value("2025-01-15", "date") == "2025-01-15"

    def test_timestamp_field_unchanged(self):
        v = "2025-01-15T09:00:00"
        assert server._coerce_form_value(v, "timestamp") == v

    def test_enum_field_unchanged(self):
        assert server._coerce_form_value("active", "enum") == "active"

    def test_uuid_field_unchanged(self):
        v = "550e8400-e29b-41d4-a716-446655440000"
        assert server._coerce_form_value(v, "uuid") == v

    def test_unknown_type_unchanged(self):
        """Any unrecognised type must be returned as-is."""
        assert server._coerce_form_value("anything", "xyzzy") == "anything"


# ---------------------------------------------------------------------------
# _coerce_form_data — manifest-driven integration
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def taskflow_manifest_path():
    if not _TASKFLOW_MANIFEST.is_file():
        pytest.skip(
            f"taskflow-demo manifest not found at {_TASKFLOW_MANIFEST}. "
            "Run: python scripts/workflow/scaffold.py --profile taskflow-demo"
        )
    return str(_TASKFLOW_MANIFEST)


@pytest.fixture
def taskflow_server(monkeypatch, taskflow_manifest_path):
    """Reload server with PROFILE_MANIFEST pointing at taskflow-demo."""
    import importlib
    monkeypatch.setenv("PROFILE_MANIFEST", taskflow_manifest_path)
    import manifest_loader as ml_mod
    importlib.reload(ml_mod)
    # Re-point server.manifest to a fresh loader
    fresh_loader = ml_mod.ManifestLoader(manifest_path=taskflow_manifest_path)
    monkeypatch.setattr(server, "manifest", fresh_loader)
    return server


class TestCoerceFormDataManifestDriven:
    """_coerce_form_data uses manifest field types — no field names hard-coded."""

    def test_budget_decimal_whole_becomes_int(self, taskflow_server):
        """project.budget (type=decimal) "5000000" → int 5000000."""
        result = taskflow_server._coerce_form_data({"budget": "5000000"}, "project")
        assert result["budget"] == 5000000
        assert isinstance(result["budget"], int)

    def test_budget_decimal_fractional_becomes_float(self, taskflow_server):
        """project.budget (type=decimal) "1000.50" → float 1000.5."""
        result = taskflow_server._coerce_form_data({"budget": "1000.50"}, "project")
        assert result["budget"] == pytest.approx(1000.50)
        assert isinstance(result["budget"], float)

    def test_progress_pct_integer(self, taskflow_server):
        """task.progress_pct (type=integer) "75" → int 75."""
        result = taskflow_server._coerce_form_data({"progress_pct": "75"}, "task")
        assert result["progress_pct"] == 75
        assert isinstance(result["progress_pct"], int)

    def test_estimated_hours_decimal(self, taskflow_server):
        """task.estimated_hours (type=decimal) "8.5" → float 8.5."""
        result = taskflow_server._coerce_form_data({"estimated_hours": "8.5"}, "task")
        assert result["estimated_hours"] == pytest.approx(8.5)

    def test_string_field_unchanged(self, taskflow_server):
        """project.name (type=string) must pass through as str."""
        result = taskflow_server._coerce_form_data({"name": "Alpha Project"}, "project")
        assert result["name"] == "Alpha Project"
        assert isinstance(result["name"], str)

    def test_bad_numeric_string_preserved_for_backend_422(self, taskflow_server):
        """Non-numeric in a decimal field → original str (backend produces clear 422)."""
        result = taskflow_server._coerce_form_data({"budget": "not-a-number"}, "project")
        assert result["budget"] == "not-a-number"

    def test_no_manifest_mode_leaves_all_as_str(self, monkeypatch):
        """When manifest not loaded, all values must remain strings (pre-fix behaviour)."""
        import importlib
        import manifest_loader as ml_mod
        # Ensure PROFILE_MANIFEST is absent so ManifestLoader(manifest_path=None)
        # does not pick it up from a previous fixture that set the env var.
        monkeypatch.delenv("PROFILE_MANIFEST", raising=False)
        importlib.reload(ml_mod)
        no_manifest = ml_mod.ManifestLoader(manifest_path=None)
        monkeypatch.setattr(server, "manifest", no_manifest)
        raw = {"budget": "5000000", "name": "X"}
        result = server._coerce_form_data(raw, "project")
        assert result == raw  # dict equality; all values still str

    def test_multiple_fields_mixed_types(self, taskflow_server):
        """Realistic project create form: name(str) + budget(decimal)."""
        raw = {"name": "Beta", "budget": "2500000"}
        result = taskflow_server._coerce_form_data(raw, "project")
        assert result["name"] == "Beta"
        assert isinstance(result["name"], str)
        assert result["budget"] == 2500000
        assert isinstance(result["budget"], int)
