package com.compounding.adapter.springboot.contract;

import com.fasterxml.jackson.annotation.JsonInclude;
import org.springframework.http.ResponseEntity;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Builder for wire-protocol-compliant response bodies.
 * Success: payload fields at top level, no "error" key (or null).
 * Failure: { "error": { "code", "message", "details"? } }
 *
 * Keeps response construction in one place rather than scattered across controllers.
 */
public final class WireResponse {

    private WireResponse() {}

    /** Build a success ResponseEntity from a plain field map. */
    public static ResponseEntity<Map<String, Object>> ok(Map<String, Object> fields) {
        return ResponseEntity.ok(fields);
    }

    /**
     * Build an error ResponseEntity.
     * HTTP status is resolved from ContractLoader (driven by codes.yaml).
     */
    public static ResponseEntity<Map<String, Object>> error(
            ContractLoader loader, String code) {
        return error(loader, code, null);
    }

    public static ResponseEntity<Map<String, Object>> error(
            ContractLoader loader, String code, Map<String, Object> details) {

        int httpStatus = loader.httpStatusFor(code);
        String message = loader.messageFor(code);

        ErrorEnvelope envelope = details != null
            ? ErrorEnvelope.withDetails(code, message, details)
            : ErrorEnvelope.of(code, message);

        Map<String, Object> body = new LinkedHashMap<>();
        body.put("error", envelope);

        return ResponseEntity.status(httpStatus).body(body);
    }
}
