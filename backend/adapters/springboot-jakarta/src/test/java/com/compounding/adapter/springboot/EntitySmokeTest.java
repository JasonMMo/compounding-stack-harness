package com.compounding.adapter.springboot;

import com.compounding.adapter.springboot.store.InMemoryEntityStore;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * L3 smoke tests — Spring Boot integration tests via MockMvc.
 * Cover the 4 contract behaviours mandated by Growth-7 task:
 *   1. entity.create → entity.read round-trip
 *   2. entity.delete idempotency (delete twice → both {success:true})
 *   3. entity.update PATCH semantics (absent field unchanged)
 *   4. error mapping (read missing id → 404 with NOT_FOUND envelope)
 */
@SpringBootTest
@AutoConfigureMockMvc
class EntitySmokeTest {

    @Autowired
    MockMvc mvc;

    @Autowired
    InMemoryEntityStore store;

    @BeforeEach
    void clearStore() {
        store.clearAll();
    }

    // ── 1. Create → Read round-trip ───────────────────────────────────────────

    @Test
    @DisplayName("entity.create then entity.read returns same data")
    void createAndRead() throws Exception {
        // Create
        MvcResult createResult = mvc.perform(post("/api/entities/product")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"data": {"name": "Widget", "price": 9.99}}
                    """))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.entity_type").value("product"))
            .andExpect(jsonPath("$.id").isString())
            .andExpect(jsonPath("$.data.name").value("Widget"))
            .andExpect(jsonPath("$.error").doesNotExist())
            .andReturn();

        // Extract generated id from response
        String responseBody = createResult.getResponse().getContentAsString();
        String id = extractJsonString(responseBody, "id");

        // Read back
        mvc.perform(get("/api/entities/product/" + id))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.entity_type").value("product"))
            .andExpect(jsonPath("$.id").value(id))
            .andExpect(jsonPath("$.data.name").value("Widget"))
            .andExpect(jsonPath("$.error").doesNotExist());
    }

    // ── 2. Delete idempotency ─────────────────────────────────────────────────

    @Test
    @DisplayName("entity.delete is idempotent: second delete of missing id → success:true, not 404")
    void deleteIdempotent() throws Exception {
        // Create an entity
        MvcResult cr = mvc.perform(post("/api/entities/order")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"data": {"ref": "ORD-001"}}
                    """))
            .andExpect(status().isCreated())
            .andReturn();
        String id = extractJsonString(cr.getResponse().getContentAsString(), "id");

        // First delete — entity exists
        mvc.perform(delete("/api/entities/order/" + id))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.error").doesNotExist());

        // Second delete — entity is already gone → still success (idempotent)
        mvc.perform(delete("/api/entities/order/" + id))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.error").doesNotExist());
    }

    // ── 3. PATCH semantics (absent field unchanged) ───────────────────────────

    @Test
    @DisplayName("entity.update PATCH: only supplied fields change; absent fields unchanged")
    void patchSemantics() throws Exception {
        // Create with two fields
        MvcResult cr = mvc.perform(post("/api/entities/product")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"data": {"name": "Gadget", "price": 19.99, "stock": 100}}
                    """))
            .andExpect(status().isCreated())
            .andReturn();
        String id = extractJsonString(cr.getResponse().getContentAsString(), "id");

        // PATCH: only update price — stock and name should be unchanged
        mvc.perform(patch("/api/entities/product/" + id)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"data": {"price": 24.99}}
                    """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.price").value(24.99))
            .andExpect(jsonPath("$.data.name").value("Gadget"))    // unchanged
            .andExpect(jsonPath("$.data.stock").value(100))         // unchanged
            .andExpect(jsonPath("$.error").doesNotExist());
    }

    // ── 4. Read missing id → 404 NOT_FOUND envelope ───────────────────────────

    @Test
    @DisplayName("entity.read with missing id returns 404 with NOT_FOUND error envelope")
    void readMissingId() throws Exception {
        mvc.perform(get("/api/entities/invoice/non-existent-id-xyz"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.error").exists())
            .andExpect(jsonPath("$.error.code").value("NOT_FOUND"))
            .andExpect(jsonPath("$.error.message").isString());
    }

    // ── 5. Paging: last page returns remainder (BUG-1 regression) ────────────

    @Test
    @DisplayName("entity.list page=3 size=3 with 7 items returns 1-item remainder")
    void lastPageReturnsRemainder() throws Exception {
        // Seed 7 items
        for (int i = 1; i <= 7; i++) {
            mvc.perform(post("/api/entities/item")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("{\"data\":{\"seq\":" + i + "}}"))
                .andExpect(status().isCreated());
        }

        // page=3, size=3 → offset=6, items[6:7] = 1 record
        mvc.perform(get("/api/entities/item")
                .param("page", "3")
                .param("size", "3"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.total").value(7))
            .andExpect(jsonPath("$.items").isArray())
            .andExpect(jsonPath("$.items.length()").value(1))
            .andExpect(jsonPath("$.error").doesNotExist());
    }

    // ── 6. Paging: list with no query params (null params guard) ─────────────

    @Test
    @DisplayName("entity.list with no query params does not throw NPE — returns page 1 defaults")
    void listNoParams() throws Exception {
        mvc.perform(post("/api/entities/widget")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"data\":{\"name\":\"A\"}}"))
            .andExpect(status().isCreated());

        mvc.perform(get("/api/entities/widget"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.total").value(1))
            .andExpect(jsonPath("$.items.length()").value(1))
            .andExpect(jsonPath("$.error").doesNotExist());
    }

    // ── 7. Cursor mode returns BAD_REQUEST (BUG-2 regression) ─────────────────

    @Test
    @DisplayName("entity.list paging_mode=cursor returns 400 BAD_REQUEST error envelope")
    void cursorModeReturnsBadRequest() throws Exception {
        mvc.perform(get("/api/entities/anything")
                .param("paging_mode", "cursor"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.error").exists())
            .andExpect(jsonPath("$.error.code").value("BAD_REQUEST"))
            .andExpect(jsonPath("$.error.message").isString());
    }

    // ── 8. Health check ───────────────────────────────────────────────────────

    @Test
    @DisplayName("status.health returns ok with contract version")
    void healthCheck() throws Exception {
        mvc.perform(get("/api/status/health"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("ok"))
            .andExpect(jsonPath("$.version").value("1.0.0"))
            .andExpect(jsonPath("$.error").doesNotExist());
    }

    // ── helper ────────────────────────────────────────────────────────────────

    /** Quick JSON string value extractor without pulling in a JSON library. */
    private String extractJsonString(String json, String key) {
        // Find "key":"<value>" — works for simple string values
        String needle = "\"" + key + "\":\"";
        int start = json.indexOf(needle);
        if (start < 0) throw new AssertionError("Key '" + key + "' not found in: " + json);
        start += needle.length();
        int end = json.indexOf("\"", start);
        return json.substring(start, end);
    }
}
