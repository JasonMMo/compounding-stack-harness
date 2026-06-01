"""
test_compliance.py -- Adapter compliance test suite (swappable-layers section 6 gate).

STANDARD compliance test set for all backend adapters.
Adapter-agnostic: base URL from adapter_base_url fixture (ADAPTER_BASE_URL env var,
default http://localhost:8080). To target a different adapter:

    ADAPTER_BASE_URL=http://localhost:9090 pytest tests/adapters/springboot-jakarta/ -q

Coverage -- 4 dimensions from swappable-layers section 6:
    [DIM-1] Contract round-trip -- all 8 wire keys exercised end-to-end
    [DIM-2] Error envelope -- shape + code + http_status from codes.yaml (single source)
    [DIM-3] Paging -- offset paging slices + cursor BAD_REQUEST (known gap)
    [DIM-4] Standards -- entity.delete idempotency + entity.update PATCH semantics

Error code catalogue: middle/contract/error/codes.yaml is parsed once at module load.
No HTTP status codes are hardcoded; all expectations derive from codes.yaml.
Entity types use a run-unique prefix to isolate against persistent stores.
"""

import json
import os
import pathlib
import random
import string
import urllib.error
import urllib.request
import uuid

import pytest
import yaml

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_CODES_PATH = _REPO_ROOT / "middle" / "contract" / "error" / "codes.yaml"

with _CODES_PATH.open(encoding="utf-8") as _f:
    _CODES_DOC = yaml.safe_load(_f)

CODES: dict = _CODES_DOC["codes"]


def _http_status(code: str) -> int:
    return CODES[code]["http_status"]


def _request(base_url, method, path, body=None, token=None):
    url = base_url.rstrip("/") + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        status = exc.code
    try:
        parsed = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Non-JSON response: {status} {raw!r}") from exc
    return status, parsed


_RUN_TAG = "".join(random.choices(string.ascii_lowercase, k=6))


def _et(suffix=""):
    sep = "-" + suffix if suffix else ""
    return f"ctest-{_RUN_TAG}{sep}"


def _assert_error_envelope(body, expected_code, *, http_status=None, actual_status=None):
    assert "error" in body, f"Expected error key in body: {body}"
    err = body["error"]
    assert isinstance(err, dict), f"error must be object: {err}"
    assert "code" in err, f"error missing code: {err}"
    assert "message" in err, f"error missing message: {err}"
    assert isinstance(err["message"], str) and err["message"], f"error.message must be non-empty str: {err}"
    assert err["code"] == expected_code, f"Expected code={expected_code!r} got {err['code']!r}: {err}"
    if http_status is not None and actual_status is not None:
        assert actual_status == http_status, (
            f"HTTP status mismatch for {expected_code}: codes.yaml={http_status} adapter={actual_status}"
        )

    if "details" in err:
        assert isinstance(err["details"], dict), f"error.details must be object: {err}"

# ============================================================
# DIM-1 -- Contract round-trip (all 8 wire keys)
# ============================================================

class TestContractRoundTrip:
    def test_status_health(self, adapter_base_url):
        status, body = _request(adapter_base_url, "GET", "/api/status/health")
        assert status == 200, f"Expected 200, got {status}. Body: {body}"
        assert body.get("status") == "ok", f"Expected status=ok: {body}"
        assert "version" in body and body["version"], f"Expected non-empty version: {body}"
        assert body.get("error") is None or "error" not in body

    def test_auth_login_returns_token(self, adapter_base_url):
        status, body = _request(adapter_base_url, "POST", "/api/auth/login",
                                 body={"username": "demo", "password": "demo"})
        assert status == 200, f"Expected 200 on login, got {status}. Body: {body}"
        assert "token" in body and body["token"], f"Expected non-empty token: {body}"
        assert "expires_at" in body, f"Expected expires_at: {body}"
        assert "user_id" in body, f"Expected user_id: {body}"
        assert body.get("error") is None or "error" not in body

    def test_auth_logout(self, adapter_base_url):
        _, login_body = _request(adapter_base_url, "POST", "/api/auth/login",
                                  body={"username": "demo", "password": "demo"})
        token = login_body["token"]
        status, body = _request(adapter_base_url, "POST", "/api/auth/logout",
                                 body={"token": token})
        assert status == 200, f"Expected 200 on logout, got {status}. Body: {body}"
        assert body.get("success") is True, f"Expected success=true on logout: {body}"

    def test_entity_create_returns_id_and_data(self, adapter_base_url):
        et = _et("create")
        status, body = _request(adapter_base_url, "POST", f"/api/entities/{et}",
                                 body={"data": {"name": "Widget", "price": 9.99}})
        assert status == 201, f"Expected 201 Created, got {status}. Body: {body}"
        assert body.get("entity_type") == et, f"entity_type mismatch: {body}"
        assert "id" in body and body["id"], f"Expected non-empty id: {body}"
        assert "data" in body, f"Expected data in response: {body}"
        assert body["data"].get("name") == "Widget", f"Expected name=Widget: {body}"

    def test_entity_read_returns_created_entity(self, adapter_base_url):
        et = _et("read")
        _, cb = _request(adapter_base_url, "POST", f"/api/entities/{et}",
                          body={"data": {"name": "Gadget", "sku": "G-001"}})
        eid = cb["id"]
        status, body = _request(adapter_base_url, "GET", f"/api/entities/{et}/{eid}")
        assert status == 200, f"Expected 200 on read, got {status}. Body: {body}"
        assert body.get("entity_type") == et
        assert body.get("id") == eid
        assert body.get("data", {}).get("name") == "Gadget"
        assert body.get("data", {}).get("sku") == "G-001"
        assert body.get("error") is None or "error" not in body

    def test_entity_list_returns_items_and_total(self, adapter_base_url):
        et = _et("list-basic")
        for i in range(2):
            _request(adapter_base_url, "POST", f"/api/entities/{et}",
                     body={"data": {"seq": i}})
        status, body = _request(adapter_base_url, "GET",
                                 f"/api/entities/{et}?page=1&size=20")
        assert status == 200, f"Expected 200 on list, got {status}. Body: {body}"
        assert body.get("entity_type") == et
        assert "items" in body and isinstance(body["items"], list), f"Expected items array: {body}"
        assert "total" in body and isinstance(body["total"], int), f"Expected int total: {body}"
        assert body["total"] >= 2, f"Expected total >= 2: {body}"

    def test_entity_update_patch_semantics(self, adapter_base_url):
        et = _et("update")
        _, cb = _request(adapter_base_url, "POST", f"/api/entities/{et}",
                          body={"data": {"name": "Original", "price": 10.0, "stock": 50}})
        eid = cb["id"]
        status, body = _request(adapter_base_url, "PATCH", f"/api/entities/{et}/{eid}",
                                 body={"data": {"price": 20.0}})
        assert status == 200, f"Expected 200 on update, got {status}. Body: {body}"
        data = body.get("data", {})
        assert data.get("price") == 20.0, f"Expected updated price=20.0: {data}"
        assert data.get("name") == "Original", f"PATCH must leave name unchanged: {data}"
        assert data.get("stock") == 50, f"PATCH must leave stock unchanged: {data}"

    def test_entity_delete_success(self, adapter_base_url):
        et = _et("delete")
        _, cb = _request(adapter_base_url, "POST", f"/api/entities/{et}",
                          body={"data": {"ref": "D-001"}})
        eid = cb["id"]
        status, body = _request(adapter_base_url, "DELETE", f"/api/entities/{et}/{eid}")
        assert status == 200, f"Expected 200 on delete, got {status}. Body: {body}"
        assert body.get("success") is True, f"Expected success=true: {body}"
        assert body.get("error") is None or "error" not in body

# ============================================================
# DIM-2 -- Error envelope
# ============================================================

class TestErrorEnvelope:
    def test_read_missing_id_returns_not_found(self, adapter_base_url):
        et = _et("err-404")
        fake_id = str(uuid.uuid4())
        status, body = _request(adapter_base_url, "GET", f"/api/entities/{et}/{fake_id}")
        expected_code = "NOT_FOUND"
        _assert_error_envelope(
            body, expected_code,
            http_status=_http_status(expected_code),
            actual_status=status,
        )

    def test_update_missing_id_returns_not_found(self, adapter_base_url):
        et = _et("err-upd-404")
        fake_id = str(uuid.uuid4())
        status, body = _request(adapter_base_url, "PATCH",
                                 f"/api/entities/{et}/{fake_id}",
                                 body={"data": {"name": "Ghost"}})
        expected_code = "NOT_FOUND"
        _assert_error_envelope(
            body, expected_code,
            http_status=_http_status(expected_code),
            actual_status=status,
        )

    def test_auth_bad_credentials_returns_auth_failed(self, adapter_base_url):
        status, body = _request(adapter_base_url, "POST", "/api/auth/login",
                                 body={"username": "demo", "password": "definitely-wrong"})
        expected_code = "AUTH_FAILED"
        _assert_error_envelope(
            body, expected_code,
            http_status=_http_status(expected_code),
            actual_status=status,
        )

    def test_auth_missing_fields_returns_bad_request(self, adapter_base_url):
        status, body = _request(adapter_base_url, "POST", "/api/auth/login", body={})
        expected_code = "BAD_REQUEST"
        _assert_error_envelope(
            body, expected_code,
            http_status=_http_status(expected_code),
            actual_status=status,
        )

    def test_error_envelope_shape(self, adapter_base_url):
        et = _et("err-shape")
        fake_id = str(uuid.uuid4())
        _, body = _request(adapter_base_url, "GET", f"/api/entities/{et}/{fake_id}")
        err = body.get("error", {})
        assert set(err.keys()) >= {"code", "message"}, (
            f"error must have at least code and message: {err}"
        )

# ============================================================
# DIM-3 -- Paging
# ============================================================

class TestPaging:
    _PAGE_SIZE = 3
    _TOTAL_ENTITIES = 7   # > 2 * PAGE_SIZE

    @pytest.fixture(autouse=True)
    def _seed_entities(self, adapter_base_url, request):
        # Use a per-test unique entity_type so repeated fixture invocations
        # across TestPaging methods do NOT accumulate into the same store bucket.
        # _RUN_TAG keeps runs isolated; request.node.name keeps tests isolated
        # within the same run.
        test_slug = request.node.name.replace("[", "-").replace("]", "")[:20]
        self._et = f"ctest-{_RUN_TAG}-pg-{test_slug}"
        self._ids = []
        for i in range(self._TOTAL_ENTITIES):
            _, body = _request(
                adapter_base_url, "POST", f"/api/entities/{self._et}",
                body={"data": {"seq": i, "label": f"item-{i}"}},
            )
            self._ids.append(body["id"])
        self._base = adapter_base_url

    def test_page1_returns_correct_count(self):
        _, body = _request(
            self._base, "GET",
            f"/api/entities/{self._et}?page=1&size={self._PAGE_SIZE}",
        )
        assert body["total"] == self._TOTAL_ENTITIES, (
            f"Expected total={self._TOTAL_ENTITIES}: {body.get('total')}"
        )
        assert len(body["items"]) == self._PAGE_SIZE, (
            f"Page 1 should return {self._PAGE_SIZE} items: {len(body.get('items', []))}"
        )

    def test_page2_returns_correct_count(self):
        _, body = _request(
            self._base, "GET",
            f"/api/entities/{self._et}?page=2&size={self._PAGE_SIZE}",
        )
        assert len(body["items"]) == self._PAGE_SIZE, (
            f"Page 2 should return {self._PAGE_SIZE} items: {len(body.get('items', []))}"
        )

    def test_last_page_returns_remainder(self):
        last_page = (self._TOTAL_ENTITIES + self._PAGE_SIZE - 1) // self._PAGE_SIZE
        remainder = self._TOTAL_ENTITIES % self._PAGE_SIZE or self._PAGE_SIZE
        _, body = _request(
            self._base, "GET",
            f"/api/entities/{self._et}?page={last_page}&size={self._PAGE_SIZE}",
        )
        assert len(body["items"]) == remainder, (
            f"Last page (page={last_page}) should return {remainder} items, got {len(body.get('items', []))}"
        )

    def test_no_overlap_between_page1_and_page2(self):
        _, p1 = _request(self._base, "GET",
                          f"/api/entities/{self._et}?page=1&size={self._PAGE_SIZE}")
        _, p2 = _request(self._base, "GET",
                          f"/api/entities/{self._et}?page=2&size={self._PAGE_SIZE}")
        ids1 = {item.get("id") for item in p1["items"]}
        ids2 = {item.get("id") for item in p2["items"]}
        overlap = ids1 & ids2
        assert not overlap, f"Page 1 and page 2 must not share items. Overlap: {overlap}"

    def test_total_is_consistent_across_pages(self):
        _, p1 = _request(self._base, "GET",
                          f"/api/entities/{self._et}?page=1&size={self._PAGE_SIZE}")
        _, p2 = _request(self._base, "GET",
                          f"/api/entities/{self._et}?page=2&size={self._PAGE_SIZE}")
        assert p1["total"] == p2["total"], (
            f"total inconsistent: p1={p1.get('total')} p2={p2.get('total')}"
        )

    def test_cursor_mode_returns_bad_request(self):
        # Per README Known Gaps: cursor paging not implemented; must return BAD_REQUEST.
        #
        # Query key used: paging_mode=cursor  (dot-free form, adapter preferred key).
        # The engineer fix (BUG-2) accepts both paging_mode= and paging.mode= .
        # wire-v1.yaml defines paging as a nested object (paging.mode), but HTTP
        # query serialisation of nested keys is not yet standardised in this project.
        # OPEN ISSUE (CTO decision): decide canonical HTTP serialisation of paging.*
        # query params (paging_mode vs paging.mode vs JSON body).
        status, body = _request(
            self._base, "GET",
            f"/api/entities/{self._et}?paging_mode=cursor&cursor=some-opaque-value",
        )
        expected_code = "BAD_REQUEST"
        _assert_error_envelope(
            body, expected_code,
            http_status=_http_status(expected_code),
            actual_status=status,
        )

# ============================================================
# DIM-4 -- Standards (wire-v1.yaml Growth-5d)
# ============================================================

class TestStandards:
    def test_delete_idempotent_second_call_is_success(self, adapter_base_url):
        # Create an entity
        et = _et("idem")
        _, cb = _request(adapter_base_url, "POST", f"/api/entities/{et}",
                          body={"data": {"ref": "IDEM-001"}})
        eid = cb["id"]

        # First delete: entity exists
        s1, b1 = _request(adapter_base_url, "DELETE", f"/api/entities/{et}/{eid}")
        assert s1 == 200, f"First delete expected 200, got {s1}. Body: {b1}"
        assert b1.get("success") is True, f"First delete expected success=true: {b1}"
        assert b1.get("error") is None or "error" not in b1

        # Second delete: entity gone -- must still be success (idempotency)
        s2, b2 = _request(adapter_base_url, "DELETE", f"/api/entities/{et}/{eid}")
        assert s2 == 200, (
            f"Second delete (idempotency) expected 200, got {s2}. Body: {b2}. "
            f"COMPLIANCE FAILURE: wire-v1.yaml entity.delete requires idempotency (Growth-5d). "
            f"Repeat delete MUST return success, not 404."
        )
        assert b2.get("success") is True, f"Second delete expected success=true: {b2}"
        assert b2.get("error") is None or "error" not in b2, (
            f"Second delete error envelope must be absent. Got: {b2}. "
            f"Per codes.yaml NOT_FOUND: entity.delete maps 404 to success."
        )

    def test_delete_of_never_created_id_is_success(self, adapter_base_url):
        # Strongest idempotency: cold delete of id never inserted
        et = _et("cold-del")
        fake_id = str(uuid.uuid4())
        status, body = _request(adapter_base_url, "DELETE", f"/api/entities/{et}/{fake_id}")
        assert status == 200, (
            f"Cold delete expected 200 (idempotent), got {status}. Body: {body}. "
            f"COMPLIANCE FAILURE: delete of never-created id must return success."
        )
        assert body.get("success") is True, f"Cold delete expected success=true: {body}"

    def test_patch_changes_only_specified_fields(self, adapter_base_url):
        et = _et("patch")
        _, cb = _request(adapter_base_url, "POST", f"/api/entities/{et}",
                          body={"data": {"name": "Alpha", "price": 100.0,
                                          "stock": 25, "tag": "original"}})
        eid = cb["id"]
        _, pb = _request(adapter_base_url, "PATCH", f"/api/entities/{et}/{eid}",
                          body={"data": {"price": 200.0}})
        data = pb.get("data", {})
        assert data.get("price") == 200.0, f"PATCH: expected price=200.0: {data}"
        assert data.get("name") == "Alpha", f"PATCH: name must be unchanged: {data}"
        assert data.get("stock") == 25, f"PATCH: stock must be unchanged: {data}"
        assert data.get("tag") == "original", f"PATCH: tag must be unchanged: {data}"

    def test_patch_fields_not_nullified_on_read_back(self, adapter_base_url):
        # After PATCH, read-back confirms absent fields are still present
        et = _et("patch-read")
        _, cb = _request(adapter_base_url, "POST", f"/api/entities/{et}",
                          body={"data": {"field_a": "keep", "field_b": "also"}})
        eid = cb["id"]
        # PATCH only field_b
        _request(adapter_base_url, "PATCH", f"/api/entities/{et}/{eid}",
                 body={"data": {"field_b": "changed"}})
        # Read back -- field_a must survive
        _, rb = _request(adapter_base_url, "GET", f"/api/entities/{et}/{eid}")
        data = rb.get("data", {})
        assert data.get("field_a") == "keep", (
            f"PATCH must not nullify absent field_a. Got: {data}"
        )
        assert data.get("field_b") == "changed", f"field_b should be updated: {data}"

import uuid as _uuid_module
def _valid_employee_data(tag):
    return {
        'employee_number': ('EMP-' + _RUN_TAG + '-' + tag)[:64],
        'full_name': 'Test Employee ' + tag,
        'department_id': str(_uuid_module.uuid4()),
        'hire_date': '2024-01-15',
        'status': 'active',
    }
class TestValidation:
    def test_create_missing_required_returns_validation_error(self, adapter_base_url):
        data = _valid_employee_data('s1')
        del data['full_name']
        status, body = _request(adapter_base_url, 'POST', '/api/entities/employee', body={'data': data})
        expected_code = 'VALIDATION_ERROR'
        _assert_error_envelope(body, expected_code, http_status=_http_status(expected_code), actual_status=status)
        fields = body.get('error', {}).get('details', {}).get('fields', {})
        assert 'full_name' in fields, ('S1: ' + str(fields))
    def test_create_bad_enum_returns_validation_error(self, adapter_base_url):
        data = _valid_employee_data('s2')
        data['status'] = 'bogus'
        status, body = _request(adapter_base_url, 'POST', '/api/entities/employee', body={'data': data})
        expected_code = 'VALIDATION_ERROR'
        _assert_error_envelope(body, expected_code, http_status=_http_status(expected_code), actual_status=status)
        fields = body.get('error', {}).get('details', {}).get('fields', {})
        assert 'status' in fields, ('S2: ' + str(fields))
    def test_create_length_exceeded_returns_validation_error(self, adapter_base_url):
        data = _valid_employee_data('s3')
        data['employee_number'] = 'E' * 65
        status, body = _request(adapter_base_url, 'POST', '/api/entities/employee', body={'data': data})
        expected_code = 'VALIDATION_ERROR'
        _assert_error_envelope(body, expected_code, http_status=_http_status(expected_code), actual_status=status)
        fields = body.get('error', {}).get('details', {}).get('fields', {})
        assert 'employee_number' in fields, ('S3: ' + str(fields))
    def test_create_type_mismatch_returns_validation_error(self, adapter_base_url):
        status, body = _request(adapter_base_url, 'POST', '/api/entities/position', body={'data': {'title': 'Analyst-' + _RUN_TAG, 'headcount_limit': 'abc'}})
        expected_code = 'VALIDATION_ERROR'
        _assert_error_envelope(body, expected_code, http_status=_http_status(expected_code), actual_status=status)
        fields = body.get('error', {}).get('details', {}).get('fields', {})
        assert 'headcount_limit' in fields, ('S4: ' + str(fields))
    def test_create_duplicate_unique_returns_conflict(self, adapter_base_url):
        emp_number = 'UNIQ-' + _RUN_TAG + '-s5'
        data = _valid_employee_data('s5')
        data['employee_number'] = emp_number
        s1, b1 = _request(adapter_base_url, 'POST', '/api/entities/employee', body={'data': data})
        assert s1 == 201, ('S5 first: ' + str(b1))
        data2 = _valid_employee_data('s5b')
        data2['employee_number'] = emp_number
        status, body = _request(adapter_base_url, 'POST', '/api/entities/employee', body={'data': data2})
        expected_code = 'CONFLICT'
        _assert_error_envelope(body, expected_code, http_status=_http_status(expected_code), actual_status=status)
        fields = body.get('error', {}).get('details', {}).get('fields', {})
        assert 'employee_number' in fields, ('S5: ' + str(fields))
    def test_create_non_catalog_entity_passes_through(self, adapter_base_url):
        status, body = _request(adapter_base_url, 'POST', '/api/entities/product', body={'data': {'name': 'Widget-' + _RUN_TAG, 'price': 99.99}})
        assert status == 201, ('S6: Got ' + str(status) + str(body))
        assert 'id' in body and body['id'], ('S6 id: ' + str(body))
        assert 'error' not in body, ('S6 err: ' + str(body))
    def test_patch_bad_enum_returns_validation_error(self, adapter_base_url):
        data = _valid_employee_data('s7a')
        s_create, b_create = _request(adapter_base_url, 'POST', '/api/entities/employee', body={'data': data})
        assert s_create == 201, ('S7a setup: ' + str(b_create))
        eid = b_create['id']
        status, body = _request(adapter_base_url, 'PATCH', '/api/entities/employee/' + eid, body={'data': {'status': 'bogus'}})
        expected_code = 'VALIDATION_ERROR'
        _assert_error_envelope(body, expected_code, http_status=_http_status(expected_code), actual_status=status)
        fields = body.get('error', {}).get('details', {}).get('fields', {})
        assert 'status' in fields, ('S7a: ' + str(fields))
    def test_patch_omitting_required_field_is_success(self, adapter_base_url):
        data = _valid_employee_data('s7b')
        s_create, b_create = _request(adapter_base_url, 'POST', '/api/entities/employee', body={'data': data})
        assert s_create == 201, ('S7b setup: ' + str(b_create))
        eid = b_create['id']
        status, body = _request(adapter_base_url, 'PATCH', '/api/entities/employee/' + eid, body={'data': {'hire_date': '2025-06-01'}})
        assert status == 200, ('S7b: must return 200. Got ' + str(status) + str(body))
        assert 'error' not in body, ('S7b err: ' + str(body))
