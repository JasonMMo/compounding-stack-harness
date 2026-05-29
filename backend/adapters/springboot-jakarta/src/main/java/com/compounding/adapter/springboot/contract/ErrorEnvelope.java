package com.compounding.adapter.springboot.contract;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.Map;

/**
 * Error envelope shape per codes.yaml header:
 *   { "code": "...", "message": "...", "details": {...}? }
 *
 * Wrapped inside the response as: { "error": { ... } }
 * On success, error is null/absent (JsonInclude.NON_NULL).
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record ErrorEnvelope(
    String code,
    String message,
    Map<String, Object> details
) {
    /** Construct with no details payload. */
    public static ErrorEnvelope of(String code, String message) {
        return new ErrorEnvelope(code, message, null);
    }

    /** Construct with a details payload. */
    public static ErrorEnvelope withDetails(String code, String message, Map<String, Object> details) {
        return new ErrorEnvelope(code, message, details);
    }
}
