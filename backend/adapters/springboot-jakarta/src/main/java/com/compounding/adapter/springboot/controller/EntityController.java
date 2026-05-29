package com.compounding.adapter.springboot.controller;

import com.compounding.adapter.springboot.contract.ContractLoader;
import com.compounding.adapter.springboot.contract.WireResponse;
import com.compounding.adapter.springboot.store.InMemoryEntityStore;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Wire key → HTTP mapping:
 *   entity.read   → GET    /api/entities/{entity_type}/{id}
 *   entity.list   → GET    /api/entities/{entity_type}
 *   entity.create → POST   /api/entities/{entity_type}
 *   entity.update → PATCH  /api/entities/{entity_type}/{id}   (PATCH semantics)
 *   entity.delete → DELETE /api/entities/{entity_type}/{id}   (idempotent)
 */
@RestController
@RequestMapping("/api/entities")
public class EntityController {

    private final InMemoryEntityStore store;
    private final ContractLoader contractLoader;

    public EntityController(InMemoryEntityStore store, ContractLoader contractLoader) {
        this.store = store;
        this.contractLoader = contractLoader;
    }

    // ── entity.read ───────────────────────────────────────────────────────────

    @GetMapping("/{entity_type}/{id}")
    public ResponseEntity<Map<String, Object>> read(
            @PathVariable("entity_type") String entityType,
            @PathVariable("id") String id) {

        Optional<Map<String, Object>> record = store.findById(entityType, id);
        if (record.isEmpty()) {
            return WireResponse.error(contractLoader, "NOT_FOUND");
        }

        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("entity_type", entityType);
        resp.put("id", id);
        resp.put("data", record.get());
        return WireResponse.ok(resp);
    }

    // ── entity.list ───────────────────────────────────────────────────────────
    // Paging: offset mode supported (page, size). Cursor mode returns BAD_REQUEST.
    // Filter: query params not in the reserved set are applied as field=value filters.
    //
    // BUG-1 fix: null-guard params before any access. Spring injects null (not empty
    //   map) when @RequestParam(required=false) Map receives zero query parameters.
    //   Without the guard, params.getOrDefault() throws NPE before page/size parse.
    //
    // BUG-2 fix: cursor mode detection reads the dedicated query param "paging_mode"
    //   (underscore, not dot). Spring MVC flattens "paging.mode=cursor" into the Map
    //   under key "paging.mode" only when the servlet container does NOT interpret the
    //   dot as a nested-property separator. In practice several containers (and some
    //   test clients) strip or ignore keys containing dots, so the cursor branch was
    //   never reached — callers saw a silent 200 instead of the documented BAD_REQUEST.
    //   Solution: accept BOTH "paging_mode" (preferred, dot-free) AND "paging.mode"
    //   (legacy) so the guard is container-agnostic and never silently falls through.

    @GetMapping("/{entity_type}")
    public ResponseEntity<Map<String, Object>> list(
            @PathVariable("entity_type") String entityType,
            @RequestParam(required = false) Map<String, String> params) {

        // Normalise: treat null params identically to an empty map.
        final Map<String, String> p = (params != null) ? params : Collections.emptyMap();

        // ── BUG-2 fix: cursor mode detection (dot-free key takes priority) ──────
        // Accept "paging_mode" (dot-free, reliable across all containers) and
        // "paging.mode" (original wire-v1 name, works when container preserves dots).
        String pagingMode = p.getOrDefault("paging_mode",
                            p.getOrDefault("paging.mode", "offset"));
        if ("cursor".equals(pagingMode)) {
            return WireResponse.error(contractLoader, "BAD_REQUEST",
                Map.of("reason", "cursor paging not yet implemented; use paging_mode=offset"));
        }

        // ── BUG-1 fix: paging param parse now uses null-safe `p` ─────────────────
        int page = parseIntParam(p, "page", 1);
        int size = parseIntParam(p, "size", 20);
        if (page < 1) page = 1;
        if (size < 1) size = 20;

        // Parse sort params
        String sortField     = p.get("sort.field");
        String sortDirection = p.getOrDefault("sort.direction", "asc");

        // Build filter map: everything that is not a reserved paging/sort key
        Set<String> reservedKeys = Set.of("page", "size",
                                           "paging.mode", "paging_mode",
                                           "cursor",
                                           "sort.field", "sort.direction");
        Map<String, String> filter = new LinkedHashMap<>();
        p.forEach((k, v) -> {
            if (!reservedKeys.contains(k)) filter.put(k, v);
        });

        List<Map<String, Object>> all = store.findAll(entityType);

        // Apply filter (simple string equality on field values)
        List<Map<String, Object>> filtered = all.stream()
            .filter(record -> matchesFilter(record, filter))
            .collect(Collectors.toList());

        // Apply sort
        if (sortField != null) {
            filtered.sort((a, b) -> compareField(a, b, sortField, "desc".equals(sortDirection)));
        }

        // ── offset paging slice ───────────────────────────────────────────────
        // offset = (page - 1) * size   (page is 1-based)
        // slice  = [offset, offset + size)  clamped to total
        int total   = filtered.size();
        int fromIdx = Math.min((page - 1) * size, total);
        int toIdx   = Math.min(fromIdx + size, total);
        List<Map<String, Object>> pageItems = filtered.subList(fromIdx, toIdx);

        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("entity_type", entityType);
        resp.put("items", pageItems);
        resp.put("total", total);
        return WireResponse.ok(resp);
    }

    // ── entity.create ─────────────────────────────────────────────────────────

    @PostMapping("/{entity_type}")
    public ResponseEntity<Map<String, Object>> create(
            @PathVariable("entity_type") String entityType,
            @RequestBody(required = false) Map<String, Object> body) {

        if (body == null) {
            return WireResponse.error(contractLoader, "BAD_REQUEST",
                Map.of("reason", "request body with 'data' field is required"));
        }

        @SuppressWarnings("unchecked")
        Map<String, Object> data = body.containsKey("data")
            ? (Map<String, Object>) body.get("data")
            : body;  // allow flat body for convenience (no double-nesting)

        if (data == null) {
            return WireResponse.error(contractLoader, "BAD_REQUEST",
                Map.of("reason", "'data' field is required"));
        }

        Map<String, Object> created = store.create(entityType, data);

        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("entity_type", entityType);
        resp.put("id", created.get("id"));
        resp.put("data", created);
        return ResponseEntity.status(201).body(resp);
    }

    // ── entity.update (PATCH) ─────────────────────────────────────────────────

    @PatchMapping("/{entity_type}/{id}")
    public ResponseEntity<Map<String, Object>> update(
            @PathVariable("entity_type") String entityType,
            @PathVariable("id") String id,
            @RequestBody(required = false) Map<String, Object> body) {

        if (body == null) {
            return WireResponse.error(contractLoader, "BAD_REQUEST",
                Map.of("reason", "PATCH body with fields to update is required"));
        }

        @SuppressWarnings("unchecked")
        Map<String, Object> patchData = body.containsKey("data")
            ? (Map<String, Object>) body.get("data")
            : body;

        if (patchData == null || patchData.isEmpty()) {
            return WireResponse.error(contractLoader, "BAD_REQUEST",
                Map.of("reason", "'data' field with at least one field to update is required"));
        }

        Optional<Map<String, Object>> updated = store.patch(entityType, id, patchData);
        if (updated.isEmpty()) {
            return WireResponse.error(contractLoader, "NOT_FOUND");
        }

        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("entity_type", entityType);
        resp.put("id", id);
        resp.put("data", updated.get());
        return WireResponse.ok(resp);
    }

    // ── entity.delete (idempotent) ────────────────────────────────────────────

    @DeleteMapping("/{entity_type}/{id}")
    public ResponseEntity<Map<String, Object>> delete(
            @PathVariable("entity_type") String entityType,
            @PathVariable("id") String id) {

        // Idempotent per wire-v1.yaml Growth-5d: missing id → success, not NOT_FOUND
        store.delete(entityType, id);

        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("success", true);
        return WireResponse.ok(resp);
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private boolean matchesFilter(Map<String, Object> record, Map<String, String> filter) {
        for (Map.Entry<String, String> entry : filter.entrySet()) {
            Object val = record.get(entry.getKey());
            if (val == null || !val.toString().equals(entry.getValue())) {
                return false;
            }
        }
        return true;
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    private int compareField(Map<String, Object> a, Map<String, Object> b,
                             String field, boolean desc) {
        Object va = a.get(field);
        Object vb = b.get(field);
        if (va == null && vb == null) return 0;
        if (va == null) return desc ? 1 : -1;
        if (vb == null) return desc ? -1 : 1;

        int cmp;
        if (va instanceof Comparable && vb instanceof Comparable) {
            cmp = ((Comparable) va).compareTo(vb);
        } else {
            cmp = va.toString().compareTo(vb.toString());
        }
        return desc ? -cmp : cmp;
    }

    private int parseIntParam(Map<String, String> params, String key, int defaultVal) {
        if (params == null) return defaultVal;
        String val = params.get(key);
        if (val == null) return defaultVal;
        try { return Integer.parseInt(val); }
        catch (NumberFormatException e) { return defaultVal; }
    }
}
