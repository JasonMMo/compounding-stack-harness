package com.compounding.adapter.springboot.store;

import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Generic thread-safe in-memory store.
 * Structure: entity_type → (id → field map).
 *
 * No database, no JPA, no DDL-axis integration.
 * That is a later Growth when persistence adapters are wired in.
 *
 * All mutation methods are synchronized on the inner entity-type map so that
 * create/update/delete are atomic per entity type. Reads are lock-free
 * (snapshots returned via Collections.unmodifiableMap).
 */
@Component
public class InMemoryEntityStore {

    // outer map is ConcurrentHashMap (safe for concurrent type-level access);
    // inner maps are synchronized explicitly on mutation.
    private final ConcurrentHashMap<String, Map<String, Map<String, Object>>> store =
        new ConcurrentHashMap<>();

    // ── create ────────────────────────────────────────────────────────────────

    /**
     * Insert a new record. Generates a UUID id, merges server defaults
     * (created_at, updated_at as epoch millis).
     * Returns the persisted record including the generated id field.
     */
    public Map<String, Object> create(String entityType, Map<String, Object> data) {
        String id = UUID.randomUUID().toString();

        Map<String, Object> record = new LinkedHashMap<>();
        record.putAll(data);
        record.put("id", id);
        long now = System.currentTimeMillis();
        record.putIfAbsent("created_at", now);
        record.put("updated_at", now);

        Map<String, Map<String, Object>> typeMap = store.computeIfAbsent(
            entityType, k -> new ConcurrentHashMap<>());

        synchronized (typeMap) {
            typeMap.put(id, record);
        }
        return Collections.unmodifiableMap(new LinkedHashMap<>(record));
    }

    // ── read ──────────────────────────────────────────────────────────────────

    public Optional<Map<String, Object>> findById(String entityType, String id) {
        Map<String, Map<String, Object>> typeMap = store.get(entityType);
        if (typeMap == null) return Optional.empty();
        Map<String, Object> record = typeMap.get(id);
        return record == null
            ? Optional.empty()
            : Optional.of(Collections.unmodifiableMap(new LinkedHashMap<>(record)));
    }

    // ── list ──────────────────────────────────────────────────────────────────

    /**
     * Return all records for a given entity type (no filter/sort applied here —
     * filtering and sorting happen in the controller/service layer).
     */
    public List<Map<String, Object>> findAll(String entityType) {
        Map<String, Map<String, Object>> typeMap = store.get(entityType);
        if (typeMap == null) return Collections.emptyList();

        List<Map<String, Object>> result = new ArrayList<>();
        for (Map<String, Object> record : typeMap.values()) {
            result.add(Collections.unmodifiableMap(new LinkedHashMap<>(record)));
        }
        return Collections.unmodifiableList(result);
    }

    // ── update (PATCH semantics) ───────────────────────────────────────────────

    /**
     * Partial update: only the supplied fields are replaced; absent fields are
     * untouched. Returns the full record after update, or Optional.empty() if
     * the id does not exist (caller maps to NOT_FOUND).
     */
    public Optional<Map<String, Object>> patch(String entityType, String id,
                                                Map<String, Object> patch) {
        Map<String, Map<String, Object>> typeMap = store.get(entityType);
        if (typeMap == null) return Optional.empty();

        synchronized (typeMap) {
            Map<String, Object> existing = typeMap.get(id);
            if (existing == null) return Optional.empty();

            Map<String, Object> updated = new LinkedHashMap<>(existing);
            // apply only the fields in the patch — absent fields unchanged
            patch.forEach((k, v) -> {
                // guard: do not allow overwriting the primary key via patch
                if (!"id".equals(k)) {
                    updated.put(k, v);
                }
            });
            updated.put("updated_at", System.currentTimeMillis());
            typeMap.put(id, updated);
            return Optional.of(Collections.unmodifiableMap(new LinkedHashMap<>(updated)));
        }
    }

    // ── delete (idempotent) ────────────────────────────────────────────────────

    /**
     * Remove a record. Idempotent per wire-v1.yaml Growth-5d standard:
     * if the id does not exist, returns true (not an error).
     */
    public boolean delete(String entityType, String id) {
        Map<String, Map<String, Object>> typeMap = store.get(entityType);
        if (typeMap == null) return true;  // type not seen at all → idempotent success

        synchronized (typeMap) {
            typeMap.remove(id);  // remove returns null if absent — we still return true
        }
        return true;
    }

    // ── test helper ───────────────────────────────────────────────────────────

    /** Clear all data. Only used in tests. */
    public void clearAll() {
        store.clear();
    }
}
