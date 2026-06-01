package com.compounding.adapter.springboot.contract;

import com.compounding.adapter.springboot.store.InMemoryEntityStore;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;
import org.yaml.snakeyaml.Yaml;

import jakarta.annotation.PostConstruct;
import java.io.InputStream;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

/**
 * CatalogValidator — runtime DDL catalog-driven input validator.
 *
 * Reads presets/ddl/catalog.yaml from the classpath at startup (G-1 compliant —
 * no schema data hardcoded; catalog is the single source of truth).
 *
 * Contract (validation-contract.md §2, §3, §4, §5):
 *   entity_type ∈ catalog  →  enforce schema (required / type / enum / length / unique / fk)
 *   entity_type ∉ catalog  →  schema-less pass-through (backward-compat)
 *
 * validate(entityType, data, partial) → List<FieldError>
 *   partial=false (create): required + type + enum + length + unique + fk
 *   partial=true  (update): type + enum + length + unique + fk (supplied cols only)
 *
 * Server-populated columns excluded from required check: id, created_at, updated_at.
 * Unique and FK checks query the InMemoryEntityStore (injected).
 *
 * FK check (§5):
 *   Only columns with an explicit `fk:` block are enforced; fk-exempt columns skipped.
 *   Absent or null fk value → skipped. Non-null → look up fk.entity in store by id.
 *   Not found → INVALID error: "referenced <fk.entity> not found".
 *   Error code stays VALIDATION_ERROR (dangling FK is a field violation, not CONFLICT).
 *   Single-source: fk targets read from catalog, never hardcoded.
 *
 * Callers split on error kind:
 *   any FieldError with kind=UNIQUE  → CONFLICT (409)
 *   any FieldError with kind=INVALID → VALIDATION_ERROR (422)
 *   collect ALL violations before returning (not fail-fast).
 */
@Component
public class CatalogValidator {

    private static final Logger log = Logger.getLogger(CatalogValidator.class.getName());

    /** Columns that the server generates — never required from the client. */
    private static final java.util.Set<String> SERVER_COLUMNS =
        java.util.Set.of("id", "created_at", "updated_at");

    private final InMemoryEntityStore store;

    /** Parsed catalog: entity_type → entity definition map. */
    private Map<String, Object> catalogEntities = Collections.emptyMap();

    public CatalogValidator(InMemoryEntityStore store) {
        this.store = store;
    }

    @PostConstruct
    public void load() {
        Map<String, Object> doc = loadYaml("catalog/catalog.yaml");
        @SuppressWarnings("unchecked")
        Map<String, Object> entities = (Map<String, Object>) doc.get("entities");
        if (entities == null || entities.isEmpty()) {
            // Warn but do not crash — backward-compat: unknown types pass through anyway.
            log.warning("CatalogValidator: catalog/catalog.yaml loaded but 'entities' map is empty.");
            catalogEntities = Collections.emptyMap();
        } else {
            catalogEntities = Collections.unmodifiableMap(entities);
            log.info("CatalogValidator: loaded " + catalogEntities.size()
                + " catalog entities from catalog.yaml");
        }
    }

    // ── public API ────────────────────────────────────────────────────────────

    /**
     * Validate data against the catalog schema for entityType.
     *
     * @param entityType the entity type key (e.g. "employee")
     * @param data       the client-supplied field map
     * @param partial    true = PATCH (skip required check); false = create (full check)
     * @param currentId  for unique checks during update: the id being updated (excluded
     *                   from collision detection). Pass null for create.
     * @return list of field errors; empty = pass. Never null.
     */
    public List<FieldError> validate(String entityType, Map<String, Object> data,
                                     boolean partial, String currentId) {
        @SuppressWarnings("unchecked")
        Map<String, Object> entityDef = (Map<String, Object>) catalogEntities.get(entityType);
        if (entityDef == null) {
            // Not in catalog → schema-less pass-through (backward-compat).
            return Collections.emptyList();
        }

        @SuppressWarnings("unchecked")
        Map<String, Object> columns = (Map<String, Object>) entityDef.get("columns");
        if (columns == null) {
            return Collections.emptyList();
        }

        List<FieldError> errors = new ArrayList<>();

        for (Map.Entry<String, Object> colEntry : columns.entrySet()) {
            String colName = colEntry.getKey();

            // Server-populated columns are never validated from client input.
            if (SERVER_COLUMNS.contains(colName)) {
                continue;
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> colDef = (Map<String, Object>) colEntry.getValue();
            if (colDef == null) continue;

            String colType   = str(colDef.get("type"));
            boolean nullable = !Boolean.FALSE.equals(colDef.get("nullable"));
            Object  value    = data.get(colName);
            boolean present  = data.containsKey(colName);

            // ── required check (create only) ────────────────────────────────
            if (!partial && !nullable && (!present || value == null)) {
                errors.add(FieldError.invalid(colName, "required field is missing or null"));
                // Skip further checks for this column — value is absent.
                continue;
            }

            // Skip remaining checks if value is not present (PATCH) or is null and nullable.
            if (!present || value == null) {
                continue;
            }

            // ── type check ──────────────────────────────────────────────────
            String typeError = checkType(colName, colType, value, colDef);
            if (typeError != null) {
                errors.add(FieldError.invalid(colName, typeError));
                // Skip length/enum if type is wrong — avoids misleading messages.
                continue;
            }

            // ── enum check ──────────────────────────────────────────────────
            if ("enum".equals(colType)) {
                @SuppressWarnings("unchecked")
                List<Object> values = (List<Object>) colDef.get("values");
                if (values != null) {
                    String strVal = value.toString();
                    boolean found = values.stream().anyMatch(v -> v.toString().equals(strVal));
                    if (!found) {
                        errors.add(FieldError.invalid(colName,
                            "must be one of " + values));
                    }
                }
                // enum type: skip length check (not applicable)
                continue;
            }

            // ── length check (string only) ───────────────────────────────────
            if (("string".equals(colType) || "text".equals(colType))
                    && value instanceof String s) {
                Object lenObj = colDef.get("length");
                if (lenObj instanceof Integer maxLen) {
                    if (s.length() > maxLen) {
                        errors.add(FieldError.invalid(colName,
                            "exceeds maximum length of " + maxLen));
                    }
                } else if (lenObj instanceof Number n) {
                    int maxLen = n.intValue();
                    if (s.length() > maxLen) {
                        errors.add(FieldError.invalid(colName,
                            "exceeds maximum length of " + maxLen));
                    }
                }
            }
        }

        // ── unique checks (after all field-level checks) ──────────────────────
        // Run even if there are already INVALID errors, per collect-all contract.
        List<FieldError> uniqueErrors = checkUnique(entityType, columns, data, currentId);
        errors.addAll(uniqueErrors);

        // ── FK referential integrity (§5) ─────────────────────────────────────
        // Only columns with an explicit `fk:` block; fk-exempt columns skipped.
        List<FieldError> fkErrors = checkFk(columns, data);
        errors.addAll(fkErrors);

        return Collections.unmodifiableList(errors);
    }

    /** Convenience overload for create (no currentId). */
    public List<FieldError> validate(String entityType, Map<String, Object> data, boolean partial) {
        return validate(entityType, data, partial, null);
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    /**
     * Returns a human-readable error string if the value fails the neutral type check,
     * or null if it passes.
     *
     * Type vocabulary (catalog-format.md §type):
     *   uuid      → any non-empty string (format check not enforced — FK values come as UUIDs)
     *   string    → String
     *   text      → String
     *   integer   → int/long (Number but not boolean, not float with fractional part)
     *   decimal   → Number (int or floating-point, not boolean)
     *   boolean   → Boolean (strict — JSON true/false, not 0/1 strings)
     *   date      → String parseable as YYYY-MM-DD (LocalDate)
     *   timestamp → String parseable as ISO-8601 (any variant accepted by Instant.parse
     *               or LocalDate as fallback)
     *   enum      → deferred to enum-values check (type check just requires String)
     */
    private String checkType(String colName, String colType, Object value,
                             Map<String, Object> colDef) {
        if (colType == null) return null;

        switch (colType) {
            case "uuid":
            case "string":
            case "text":
                if (!(value instanceof String)) {
                    return "must be a string";
                }
                break;

            case "integer":
                // Must be a Number but NOT a Boolean, and must have no fractional part.
                if (value instanceof Boolean) {
                    return "must be an integer (boolean is not accepted)";
                }
                if (!(value instanceof Number)) {
                    return "must be an integer";
                }
                {
                    double d = ((Number) value).doubleValue();
                    if (d != Math.floor(d) || Double.isInfinite(d) || Double.isNaN(d)) {
                        return "must be an integer (fractional number is not accepted)";
                    }
                }
                break;

            case "decimal":
                if (value instanceof Boolean) {
                    return "must be a number (boolean is not accepted)";
                }
                if (!(value instanceof Number)) {
                    return "must be a number (decimal)";
                }
                break;

            case "boolean":
                if (!(value instanceof Boolean)) {
                    return "must be a boolean (true or false)";
                }
                break;

            case "date":
                if (!(value instanceof String)) {
                    return "must be a date string in YYYY-MM-DD format";
                }
                try {
                    LocalDate.parse((String) value);
                } catch (DateTimeParseException e) {
                    return "must be a valid date in YYYY-MM-DD format";
                }
                break;

            case "timestamp":
                if (!(value instanceof String)) {
                    return "must be a timestamp string in ISO-8601 format";
                }
                {
                    String ts = (String) value;
                    boolean ok = false;
                    try { java.time.Instant.parse(ts); ok = true; } catch (Exception ignored) {}
                    if (!ok) {
                        try { LocalDate.parse(ts); ok = true; } catch (Exception ignored) {}
                    }
                    if (!ok) {
                        return "must be a valid ISO-8601 timestamp";
                    }
                }
                break;

            case "enum":
                // enum values are strings; just verify it is a String here.
                // The actual allowed-values check is done separately.
                if (!(value instanceof String)) {
                    return "must be a string (enum value)";
                }
                break;

            default:
                // Unknown type — pass through (forward-compat).
                break;
        }
        return null;
    }

    /**
     * Check FK referential integrity for columns with an explicit `fk:` block.
     *
     * Rules (validation-contract.md §5):
     *   - Columns without `fk:` key → fk-exempt; skipped.
     *   - Value absent or null → skipped (nothing to verify).
     *   - Non-null value → look up fk.entity in store by id; not found → INVALID.
     *   - Error message: "referenced <fk.entity> not found".
     *   - Returns INVALID-kind errors (VALIDATION_ERROR, not CONFLICT).
     *   - Single-source: fk targets read from catalog, never hardcoded.
     */
    @SuppressWarnings("unchecked")
    private List<FieldError> checkFk(Map<String, Object> columns, Map<String, Object> data) {
        List<FieldError> errors = new ArrayList<>();

        for (Map.Entry<String, Object> colEntry : columns.entrySet()) {
            String colName = colEntry.getKey();
            if (SERVER_COLUMNS.contains(colName)) continue;

            Map<String, Object> colDef = (Map<String, Object>) colEntry.getValue();
            if (colDef == null) continue;

            // Only enforce columns that have an explicit `fk:` block.
            Object fkRaw = colDef.get("fk");
            if (fkRaw == null || !(fkRaw instanceof Map)) continue;
            Map<String, Object> fkBlock = (Map<String, Object>) fkRaw;

            Object value = data.get(colName);
            if (value == null || !data.containsKey(colName)) continue;

            String refEntity = str(fkBlock.get("entity"));
            if (refEntity == null || refEntity.isEmpty()) continue;

            String refId = value.toString();
            if (store.findById(refEntity, refId).isEmpty()) {
                errors.add(FieldError.invalid(colName, "referenced " + refEntity + " not found"));
            }
        }
        return errors;
    }

    /**
     * Check all unique columns in the entity's schema against existing store records.
     * For update: exclude the record being updated (currentId).
     * Returns UNIQUE-kind FieldErrors.
     */
    private List<FieldError> checkUnique(String entityType, Map<String, Object> columns,
                                          Map<String, Object> data, String currentId) {
        List<FieldError> errors = new ArrayList<>();

        for (Map.Entry<String, Object> colEntry : columns.entrySet()) {
            String colName = colEntry.getKey();
            if (SERVER_COLUMNS.contains(colName)) continue;

            @SuppressWarnings("unchecked")
            Map<String, Object> colDef = (Map<String, Object>) colEntry.getValue();
            if (colDef == null) continue;

            if (!Boolean.TRUE.equals(colDef.get("unique"))) continue;

            Object newVal = data.get(colName);
            if (newVal == null) continue;

            // Scan existing records for a collision.
            List<Map<String, Object>> all = store.findAll(entityType);
            String newValStr = newVal.toString();
            for (Map<String, Object> record : all) {
                // Exclude the record being updated from the collision check.
                if (currentId != null && currentId.equals(record.get("id"))) continue;

                Object existing = record.get(colName);
                if (existing != null && existing.toString().equals(newValStr)) {
                    errors.add(FieldError.unique(colName, "must be unique"));
                    break; // one collision per column is enough
                }
            }
        }
        return errors;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> loadYaml(String classpathResource) {
        try {
            ClassPathResource resource = new ClassPathResource(classpathResource);
            try (InputStream is = resource.getInputStream()) {
                Yaml yaml = new Yaml();
                Map<String, Object> result = yaml.load(is);
                return result != null ? result : Collections.emptyMap();
            }
        } catch (Exception e) {
            throw new IllegalStateException(
                "CatalogValidator: failed to load " + classpathResource
                    + " — " + e.getMessage(), e);
        }
    }

    private static String str(Object o) {
        return o != null ? o.toString() : null;
    }

    // ── FieldError ────────────────────────────────────────────────────────────

    /** Represents a single field-level validation error. */
    public static final class FieldError {

        public enum Kind { INVALID, UNIQUE }

        public final String field;
        public final String reason;
        public final Kind   kind;

        private FieldError(String field, String reason, Kind kind) {
            this.field  = field;
            this.reason = reason;
            this.kind   = kind;
        }

        public static FieldError invalid(String field, String reason) {
            return new FieldError(field, reason, Kind.INVALID);
        }

        public static FieldError unique(String field, String reason) {
            return new FieldError(field, reason, Kind.UNIQUE);
        }

        @Override
        public String toString() {
            return kind + "[" + field + "]: " + reason;
        }
    }
}
