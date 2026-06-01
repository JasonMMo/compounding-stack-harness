package com.compounding.adapter.springboot;

import com.compounding.adapter.springboot.contract.CatalogValidator;
import com.compounding.adapter.springboot.contract.CatalogValidator.FieldError;
import com.compounding.adapter.springboot.store.InMemoryEntityStore;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * L1 unit tests for CatalogValidator.
 *
 * Uses the full Spring context so processResources has already copied
 * catalog.yaml onto the classpath (same guarantee as production boot).
 *
 * Test catalog entity used: "employee" (has required, enum, length, unique)
 * and "position" (has integer type check: headcount_limit).
 * Schema-less entity: "product" (not in catalog → pass-through).
 *
 * Coverage:
 *   - unknown entity_type (product) → empty errors (pass-through)
 *   - missing required field (full_name) → INVALID error
 *   - bad enum value (status=bogus) → INVALID error
 *   - length exceeded (employee_number > 64 chars) → INVALID error
 *   - wrong type (headcount_limit="abc") → INVALID error
 *   - unique collision (same employee_number twice) → UNIQUE error
 *   - PATCH partial=true skips required check
 *   - PATCH with bad enum → INVALID error
 *   - server columns (id, created_at, updated_at) never required
 *   - all violations collected at once (not fail-fast)
 */
@SpringBootTest
class CatalogValidatorTest {

    @Autowired
    private CatalogValidator validator;

    @Autowired
    private InMemoryEntityStore store;

    @BeforeEach
    void clearStore() {
        store.clearAll();
    }

    // ── backward-compat: unknown entity_type passes through ──────────────────

    @Test
    void unknownEntityType_passesThrough() {
        Map<String, Object> data = Map.of("name", "Widget", "price", 9.99);
        List<FieldError> errors = validator.validate("product", data, false);
        assertTrue(errors.isEmpty(),
            "Non-catalog entity_type must produce zero errors (schema-less pass-through)");
    }

    // ── required check ────────────────────────────────────────────────────────

    @Test
    void missingRequiredField_returnsInvalidError() {
        // employee: full_name is required (nullable: false)
        Map<String, Object> data = Map.of(
            "employee_number", "EMP-001",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "2024-01-15",
            "status",          "active"
            // full_name intentionally omitted
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        assertTrue(errors.stream().anyMatch(e ->
            "full_name".equals(e.field) && e.kind == FieldError.Kind.INVALID),
            "Missing required field full_name must produce INVALID error. Got: " + errors);
    }

    @Test
    void serverColumns_neverRequired() {
        // id, created_at, updated_at absent → must NOT cause required errors
        // (provide all other required fields)
        Map<String, Object> data = Map.of(
            "employee_number", "EMP-002",
            "full_name",       "Jane Doe",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "2024-01-15",
            "status",          "active"
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        boolean serverColRequired = errors.stream().anyMatch(e ->
            "id".equals(e.field) || "created_at".equals(e.field) || "updated_at".equals(e.field));
        assertFalse(serverColRequired,
            "id/created_at/updated_at must never be required from client. Errors: " + errors);
    }

    // ── enum check ────────────────────────────────────────────────────────────

    @Test
    void badEnumValue_returnsInvalidError() {
        Map<String, Object> data = Map.of(
            "employee_number", "EMP-003",
            "full_name",       "John Smith",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "2024-01-15",
            "status",          "bogus"   // not in [active, on-leave, terminated]
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        assertTrue(errors.stream().anyMatch(e ->
            "status".equals(e.field) && e.kind == FieldError.Kind.INVALID),
            "Bad enum value must produce INVALID error on 'status'. Got: " + errors);
    }

    @Test
    void validEnumValue_noError() {
        Map<String, Object> data = Map.of(
            "employee_number", "EMP-004",
            "full_name",       "Alice Green",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "2024-01-15",
            "status",          "on-leave"
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        assertFalse(errors.stream().anyMatch(e -> "status".equals(e.field)),
            "Valid enum value must not produce error. Errors: " + errors);
    }

    // ── length check ─────────────────────────────────────────────────────────

    @Test
    void lengthExceeded_returnsInvalidError() {
        // employee_number: length 64
        String longNumber = "EMP-" + "X".repeat(65); // 69 chars > 64
        Map<String, Object> data = Map.of(
            "employee_number", longNumber,
            "full_name",       "Bob Long",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "2024-01-15",
            "status",          "active"
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        assertTrue(errors.stream().anyMatch(e ->
            "employee_number".equals(e.field) && e.kind == FieldError.Kind.INVALID),
            "Length-exceeded field must produce INVALID error. Got: " + errors);
    }

    @Test
    void lengthExactlyAtLimit_noError() {
        String exactNumber = "E".repeat(64); // exactly 64 chars
        Map<String, Object> data = Map.of(
            "employee_number", exactNumber,
            "full_name",       "Carol Exact",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "2024-01-15",
            "status",          "active"
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        assertFalse(errors.stream().anyMatch(e -> "employee_number".equals(e.field)),
            "Length exactly at limit must not produce error. Errors: " + errors);
    }

    // ── type check ────────────────────────────────────────────────────────────

    @Test
    void wrongType_integer_returnsInvalidError() {
        // position.headcount_limit: type integer
        Map<String, Object> data = Map.of(
            "title",           "Manager",
            "headcount_limit", "abc"   // string instead of integer
        );
        List<FieldError> errors = validator.validate("position", data, false);
        assertTrue(errors.stream().anyMatch(e ->
            "headcount_limit".equals(e.field) && e.kind == FieldError.Kind.INVALID),
            "String value for integer field must produce INVALID error. Got: " + errors);
    }

    @Test
    void booleanRejectedAsInteger() {
        Map<String, Object> data = Map.of(
            "title",           "Engineer",
            "headcount_limit", true   // boolean not accepted as integer
        );
        List<FieldError> errors = validator.validate("position", data, false);
        assertTrue(errors.stream().anyMatch(e ->
            "headcount_limit".equals(e.field) && e.kind == FieldError.Kind.INVALID),
            "Boolean must be rejected for integer field. Got: " + errors);
    }

    @Test
    void validDate_noError() {
        Map<String, Object> data = Map.of(
            "employee_number", "EMP-010",
            "full_name",       "Dave Date",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "2024-03-01",
            "status",          "active"
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        assertFalse(errors.stream().anyMatch(e -> "hire_date".equals(e.field)),
            "Valid YYYY-MM-DD date must not produce error. Errors: " + errors);
    }

    @Test
    void badDate_returnsInvalidError() {
        Map<String, Object> data = Map.of(
            "employee_number", "EMP-011",
            "full_name",       "Eve BadDate",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "not-a-date",
            "status",          "active"
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        assertTrue(errors.stream().anyMatch(e ->
            "hire_date".equals(e.field) && e.kind == FieldError.Kind.INVALID),
            "Invalid date string must produce INVALID error. Got: " + errors);
    }

    // ── unique check → CONFLICT ───────────────────────────────────────────────

    @Test
    void uniqueCollision_returnsUniqueError() {
        // Seed the store with an employee having a specific employee_number
        store.create("employee", Map.of(
            "employee_number", "EMP-UNIQUE-01",
            "full_name",       "First Employee",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "2024-01-01",
            "status",          "active"
        ));

        // Now try to create another with the same employee_number
        Map<String, Object> data = Map.of(
            "employee_number", "EMP-UNIQUE-01",  // collision
            "full_name",       "Second Employee",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "2024-06-01",
            "status",          "active"
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        assertTrue(errors.stream().anyMatch(e ->
            "employee_number".equals(e.field) && e.kind == FieldError.Kind.UNIQUE),
            "Duplicate unique field must produce UNIQUE error. Got: " + errors);
    }

    // ── PATCH partial validation ───────────────────────────────────────────────

    @Test
    void patch_skipsRequiredCheck() {
        // partial=true: supplying only status update, omitting required fields
        Map<String, Object> patch = Map.of("status", "on-leave");
        List<FieldError> errors = validator.validate("employee", patch, true);
        // Should have no INVALID errors for missing required fields
        boolean missingRequired = errors.stream().anyMatch(e ->
            e.kind == FieldError.Kind.INVALID &&
            (e.reason.contains("required") || e.reason.contains("missing")));
        assertFalse(missingRequired,
            "PATCH must not fail for absent required fields. Errors: " + errors);
    }

    @Test
    void patch_badEnum_returnsInvalidError() {
        Map<String, Object> patch = Map.of("status", "nonexistent-status");
        List<FieldError> errors = validator.validate("employee", patch, true);
        assertTrue(errors.stream().anyMatch(e ->
            "status".equals(e.field) && e.kind == FieldError.Kind.INVALID),
            "PATCH with bad enum must still produce INVALID error. Got: " + errors);
    }

    // ── collect ALL violations (not fail-fast) ────────────────────────────────

    @Test
    void multipleViolations_allCollected() {
        // Two INVALID violations simultaneously: bad status + bad hire_date
        Map<String, Object> data = Map.of(
            "employee_number", "EMP-MULTI",
            "full_name",       "Multi Error",
            "department_id",   "00000000-0000-0000-0000-000000000001",
            "hire_date",       "not-a-date",
            "status",          "bogus"
        );
        List<FieldError> errors = validator.validate("employee", data, false);
        long invalidCount = errors.stream().filter(e -> e.kind == FieldError.Kind.INVALID).count();
        assertTrue(invalidCount >= 2,
            "Must collect all field violations, not fail-fast. Expected >= 2 INVALID, got: " + errors);
    }

    // ── FK referential integrity (§5) ─────────────────────────────────────────

    @Test
    void fkCol_bogusId_returnsInvalidError() {
        // route.carrier_id → carrier; no carrier seeded → must fail
        java.util.Map<String, Object> data = new java.util.LinkedHashMap<>();
        data.put("name",            "Test Route");
        data.put("carrier_id",      "00000000-0000-0000-0000-000000000099");
        data.put("origin_hub",      "HUB-A");
        data.put("destination_hub", "HUB-B");
        data.put("transit_days",    3);
        data.put("is_active",       true);
        List<FieldError> errors = validator.validate("route", data, false);
        assertTrue(errors.stream().anyMatch(e ->
            "carrier_id".equals(e.field)
            && e.kind == FieldError.Kind.INVALID
            && e.reason.contains("not found")),
            "Bogus carrier_id must produce INVALID FK error with 'not found'. Got: " + errors);
    }

    @Test
    void fkCol_validId_noError() {
        // Seed a carrier, then validate a route that references it
        java.util.Map<String, Object> carrier = store.create("carrier", Map.of(
            "code",      "CAR-UNIT-01",
            "name",      "Unit Test Carrier",
            "is_active", true
        ));
        String carrierId = (String) carrier.get("id");

        java.util.Map<String, Object> data = new java.util.LinkedHashMap<>();
        data.put("name",            "Test Route Valid");
        data.put("carrier_id",      carrierId);
        data.put("origin_hub",      "HUB-A");
        data.put("destination_hub", "HUB-B");
        data.put("transit_days",    2);
        data.put("is_active",       true);
        List<FieldError> errors = validator.validate("route", data, false);
        assertFalse(errors.stream().anyMatch(e -> "carrier_id".equals(e.field)),
            "Valid FK must produce no carrier_id error. Got: " + errors);
    }

    @Test
    void fkNullable_absent_noError() {
        // position.department_id is nullable: true — omitting it must not produce FK error
        Map<String, Object> data = Map.of("title", "Test Position");
        List<FieldError> errors = validator.validate("position", data, false);
        assertFalse(errors.stream().anyMatch(e -> "department_id".equals(e.field)),
            "Absent nullable FK must produce no FK error. Got: " + errors);
    }

    @Test
    void fkExempt_col_noFkError() {
        // journal-entry.period_id: type uuid, NO fk: block → fk-exempt, never enforced
        java.util.Map<String, Object> data = new java.util.LinkedHashMap<>();
        data.put("entry_date",  "2024-06-01");
        data.put("description", "Test Entry");
        data.put("status",      "draft");
        data.put("period_id",   "00000000-0000-0000-0000-000000000099");
        List<FieldError> errors = validator.validate("journal-entry", data, false);
        assertFalse(errors.stream().anyMatch(e -> "period_id".equals(e.field)),
            "FK-exempt period_id must not produce FK error. Got: " + errors);
    }

    @Test
    void patch_fkCol_bogusId_returnsInvalidError() {
        // PATCH: supplied fk col with bogus id → INVALID
        Map<String, Object> patch = Map.of(
            "carrier_id", "00000000-0000-0000-0000-000000000099"
        );
        List<FieldError> errors = validator.validate("route", patch, true);
        assertTrue(errors.stream().anyMatch(e ->
            "carrier_id".equals(e.field) && e.kind == FieldError.Kind.INVALID),
            "PATCH with bogus FK must produce INVALID error. Got: " + errors);
    }

    @Test
    void patch_fkCol_absent_noError() {
        // PATCH: carrier_id absent → no FK check (absent = no change)
        Map<String, Object> patch = Map.of("transit_days", 5);
        List<FieldError> errors = validator.validate("route", patch, true);
        assertFalse(errors.stream().anyMatch(e -> "carrier_id".equals(e.field)),
            "PATCH with fk col absent must not produce FK error. Got: " + errors);
    }

    @Test
    void fkError_collectedWithOtherErrors() {
        // FK error collected alongside type error — not fail-fast
        java.util.Map<String, Object> data = new java.util.LinkedHashMap<>();
        data.put("name",            "Multi-Error Route");
        data.put("carrier_id",      "00000000-0000-0000-0000-000000000099"); // bogus fk
        data.put("origin_hub",      "HUB-A");
        data.put("destination_hub", "HUB-B");
        data.put("transit_days",    "bad"); // type error: should be integer
        data.put("is_active",       true);
        List<FieldError> errors = validator.validate("route", data, false);
        boolean hasFkError   = errors.stream().anyMatch(e ->
            "carrier_id".equals(e.field) && e.kind == FieldError.Kind.INVALID);
        boolean hasTypeError = errors.stream().anyMatch(e ->
            "transit_days".equals(e.field) && e.kind == FieldError.Kind.INVALID);
        assertTrue(hasFkError,   "FK error must be collected. Got: "   + errors);
        assertTrue(hasTypeError, "Type error must also be collected. Got: " + errors);
    }
}
