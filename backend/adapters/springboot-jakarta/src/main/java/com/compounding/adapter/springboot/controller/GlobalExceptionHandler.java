package com.compounding.adapter.springboot.controller;

import com.compounding.adapter.springboot.contract.ContractLoader;
import com.compounding.adapter.springboot.contract.WireResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;
import java.util.logging.Logger;

/**
 * Translates unhandled exceptions into wire-compliant error envelopes.
 * Error codes are looked up via ContractLoader (driven by codes.yaml).
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = Logger.getLogger(GlobalExceptionHandler.class.getName());

    private final ContractLoader contractLoader;

    public GlobalExceptionHandler(ContractLoader contractLoader) {
        this.contractLoader = contractLoader;
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<Map<String, Object>> handleUnreadableBody(HttpMessageNotReadableException ex) {
        return WireResponse.error(contractLoader, "BAD_REQUEST",
            Map.of("reason", "Request body is missing or malformed JSON."));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGeneral(Exception ex) {
        log.severe("Unhandled exception: " + ex.getMessage());
        return WireResponse.error(contractLoader, "INTERNAL");
    }
}
