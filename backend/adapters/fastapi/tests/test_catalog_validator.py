"""
tests/test_catalog_validator.py — L1 unit tests for catalog_validator.py

Coverage mirrors CatalogValidatorTest.java exactly (behavioral parity guarantee):
    - unknown entity_type → schema-less pass-through (backward-compat gate)
    - missing required field → INVALID error
    - server columns (id/created_at/updated_at) never required
    - bad enum value → INVALID error
    - valid enum value → no error
    - length exceeded → INVALID error
    - length exactly at limit → no error
    - wrong type (integer field receives string) → INVALID error
    - boolean rejected as integer
    - valid date → no error
    - bad date string → INVALID error
    - unique collision → UNIQUE error
    - PATCH partial=True skips required check
    - PATCH with bad enum → INVALID error
    - multiple violations collected at once (not fail-fast)

No live server required — pure unit tests against catalog_validator module and a
real InMemoryEntityStore instance (same in-memory semantics as production).
"""

from __future__ import annotations

import sys
import pathlib

# Ensure the fastapi adapter root is on sys.path so imports work
# when running `pytest` from the adapter directory or the repo root.
_ADAPTER_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_ADAPTER_ROOT) not in sys.path:
    sys.path.insert(0, str(_ADAPTER_ROOT))

import pytest
from catalog_validator import CatalogValidator, FieldError
from store import InMemoryEntityStore


@pytest.fixture()
def store() -> InMemoryEntityStore:
    s = InMemoryEntityStore()
    return s


@pytest.fixture()
def validator() -> CatalogValidator:
    # Use the module singleton — already loaded at import time.
    from catalog_validator import catalog_validator
    return catalog_validator


# ── backward-compat: unknown entity_type passes through ─────────────────────

def test_unknown_entity_type_passes_through(validator, store):
    data = {"name": "Widget", "price": 9.99}
    errors = validator.validate("product", data, partial=False, store=store)
    assert errors == [], (
        "Non-catalog entity_type must produce zero errors (schema-less pass-through). "
        f"Got: {errors}"
    )


def test_unknown_entity_type_passes_through_partial(validator, store):
    errors = validator.validate("ctest-abc123", {"field": "value"}, partial=True, store=store)
    assert errors == [], f"Any run-prefixed test entity_type must pass through. Got: {errors}"


# ── required check ────────────────────────────────────────────────────────────

def test_missing_required_field_returns_invalid(validator, store):
    # employee: full_name is required (nullable: false)
    data = {
        "employee_number": "EMP-001",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-01-15",
        "status":          "active",
        # full_name intentionally omitted
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    invalid_fields = [e.field for e in errors if e.kind == "INVALID"]
    assert "full_name" in invalid_fields, (
        f"Missing required full_name must produce INVALID error. Got: {errors}"
    )


def test_server_columns_never_required(validator, store):
    # Provide all real required fields but omit id/created_at/updated_at
    data = {
        "employee_number": "EMP-002",
        "full_name":       "Jane Doe",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-01-15",
        "status":          "active",
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    server_col_errors = [e for e in errors if e.field in ("id", "created_at", "updated_at")]
    assert server_col_errors == [], (
        f"id/created_at/updated_at must never be required. Errors: {server_col_errors}"
    )


# ── enum check ────────────────────────────────────────────────────────────────

def test_bad_enum_value_returns_invalid(validator, store):
    data = {
        "employee_number": "EMP-003",
        "full_name":       "John Smith",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-01-15",
        "status":          "bogus",  # not in [active, on-leave, terminated]
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    assert any(e.field == "status" and e.kind == "INVALID" for e in errors), (
        f"Bad enum must produce INVALID on 'status'. Got: {errors}"
    )


def test_valid_enum_value_no_error(validator, store):
    data = {
        "employee_number": "EMP-004",
        "full_name":       "Alice Green",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-01-15",
        "status":          "on-leave",
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    status_errors = [e for e in errors if e.field == "status"]
    assert status_errors == [], (
        f"Valid enum 'on-leave' must not produce error. Got: {status_errors}"
    )


# ── length check ──────────────────────────────────────────────────────────────

def test_length_exceeded_returns_invalid(validator, store):
    # employee_number: length 64 — use 65 chars
    long_number = "EMP-" + "X" * 65  # 69 chars > 64
    data = {
        "employee_number": long_number,
        "full_name":       "Bob Long",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-01-15",
        "status":          "active",
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    assert any(e.field == "employee_number" and e.kind == "INVALID" for e in errors), (
        f"Length-exceeded employee_number must produce INVALID. Got: {errors}"
    )


def test_length_exactly_at_limit_no_error(validator, store):
    exact_number = "E" * 64  # exactly 64 chars
    data = {
        "employee_number": exact_number,
        "full_name":       "Carol Exact",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-01-15",
        "status":          "active",
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    empno_errors = [e for e in errors if e.field == "employee_number"]
    assert empno_errors == [], (
        f"Length exactly at limit must not produce error. Got: {empno_errors}"
    )


# ── type check ────────────────────────────────────────────────────────────────

def test_wrong_type_integer_returns_invalid(validator, store):
    # position.headcount_limit: type integer
    data = {
        "title":           "Manager",
        "headcount_limit": "abc",  # string, not integer
    }
    errors = validator.validate("position", data, partial=False, store=store)
    assert any(e.field == "headcount_limit" and e.kind == "INVALID" for e in errors), (
        f"String value for integer field must produce INVALID. Got: {errors}"
    )


def test_boolean_rejected_as_integer(validator, store):
    data = {
        "title":           "Engineer",
        "headcount_limit": True,  # bool not accepted as integer
    }
    errors = validator.validate("position", data, partial=False, store=store)
    assert any(e.field == "headcount_limit" and e.kind == "INVALID" for e in errors), (
        f"Boolean must be rejected for integer field. Got: {errors}"
    )


def test_valid_date_no_error(validator, store):
    data = {
        "employee_number": "EMP-010",
        "full_name":       "Dave Date",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-03-01",
        "status":          "active",
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    date_errors = [e for e in errors if e.field == "hire_date"]
    assert date_errors == [], f"Valid date must not produce error. Got: {date_errors}"


def test_bad_date_returns_invalid(validator, store):
    data = {
        "employee_number": "EMP-011",
        "full_name":       "Eve BadDate",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "not-a-date",
        "status":          "active",
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    assert any(e.field == "hire_date" and e.kind == "INVALID" for e in errors), (
        f"Invalid date string must produce INVALID. Got: {errors}"
    )


# ── unique check → UNIQUE kind ────────────────────────────────────────────────

def test_unique_collision_returns_unique_error(validator, store):
    # Seed an employee record directly into the store
    store.create("employee", {
        "employee_number": "EMP-UNIQUE-01",
        "full_name":       "First Employee",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-01-01",
        "status":          "active",
    })

    # Attempt to validate a second record with the same employee_number
    data = {
        "employee_number": "EMP-UNIQUE-01",  # collision
        "full_name":       "Second Employee",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-06-01",
        "status":          "active",
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    assert any(e.field == "employee_number" and e.kind == "UNIQUE" for e in errors), (
        f"Duplicate unique field must produce UNIQUE error. Got: {errors}"
    )


def test_unique_no_collision_no_error(validator, store):
    store.create("employee", {
        "employee_number": "EMP-SOLO-01",
        "full_name":       "Only Employee",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-01-01",
        "status":          "active",
    })
    data = {
        "employee_number": "EMP-SOLO-02",  # different, no collision
        "full_name":       "Another Employee",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-06-01",
        "status":          "active",
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    unique_errors = [e for e in errors if e.kind == "UNIQUE"]
    assert unique_errors == [], (
        f"No collision should produce no UNIQUE errors. Got: {unique_errors}"
    )


# ── PATCH partial validation ───────────────────────────────────────────────────

def test_patch_skips_required_check(validator, store):
    # partial=True: only status field supplied — required fields absent
    patch = {"status": "on-leave"}
    errors = validator.validate("employee", patch, partial=True, store=store)
    # Must have no INVALID errors for missing required fields
    required_errors = [
        e for e in errors
        if e.kind == "INVALID" and ("required" in e.reason or "missing" in e.reason)
    ]
    assert required_errors == [], (
        f"PATCH must not fail for absent required fields. Errors: {required_errors}"
    )


def test_patch_bad_enum_returns_invalid(validator, store):
    patch = {"status": "nonexistent-status"}
    errors = validator.validate("employee", patch, partial=True, store=store)
    assert any(e.field == "status" and e.kind == "INVALID" for e in errors), (
        f"PATCH with bad enum must still produce INVALID. Got: {errors}"
    )


def test_patch_valid_enum_no_error(validator, store):
    patch = {"status": "terminated"}
    errors = validator.validate("employee", patch, partial=True, store=store)
    status_errors = [e for e in errors if e.field == "status"]
    assert status_errors == [], (
        f"PATCH with valid enum must not produce error. Got: {status_errors}"
    )


# ── collect ALL violations (not fail-fast) ────────────────────────────────────

def test_multiple_violations_all_collected(validator, store):
    # bad status + bad hire_date simultaneously
    data = {
        "employee_number": "EMP-MULTI",
        "full_name":       "Multi Error",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "not-a-date",
        "status":          "bogus",
    }
    errors = validator.validate("employee", data, partial=False, store=store)
    invalid_errors = [e for e in errors if e.kind == "INVALID"]
    assert len(invalid_errors) >= 2, (
        f"Must collect all field violations (not fail-fast). Expected >= 2 INVALID. Got: {errors}"
    )


# ── no-store call (unique check skipped when store=None) ─────────────────────

def test_validate_without_store_skips_unique(validator):
    # When store is None, unique check is skipped — caller must pass store for unique
    data = {
        "employee_number": "EMP-NO-STORE",
        "full_name":       "No Store Employee",
        "department_id":   "00000000-0000-0000-0000-000000000001",
        "hire_date":       "2024-01-15",
        "status":          "active",
    }
    # Should not raise — just skips unique checks
    errors = validator.validate("employee", data, partial=False)  # no store kwarg
    unique_errors = [e for e in errors if e.kind == "UNIQUE"]
    assert unique_errors == [], (
        f"Without store, no UNIQUE errors should be produced. Got: {unique_errors}"
    )
