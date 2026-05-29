package com.compounding.adapter.springboot.contract;

import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;
import org.yaml.snakeyaml.Yaml;

import jakarta.annotation.PostConstruct;
import java.io.InputStream;
import java.util.Collections;
import java.util.Map;
import java.util.logging.Logger;

/**
 * Loads middle/contract/ YAML files from the classpath at startup.
 * G-1 compliance: the adapter reads the contract; it does NOT redeclare
 * error codes or schema definitions as Java constants.
 *
 * Contract files are copied into resources/contract/ by build.gradle.kts
 * processResources task (from ../../../middle/contract relative to adapter root).
 */
@Component
public class ContractLoader {

    private static final Logger log = Logger.getLogger(ContractLoader.class.getName());

    /** Raw parsed codes.yaml map: code → {http_status, message, message_ko, retriable, description} */
    private Map<String, Object> codesMap = Collections.emptyMap();

    /** Raw parsed wire-v1.yaml top-level map */
    private Map<String, Object> wireMap = Collections.emptyMap();

    @PostConstruct
    public void load() {
        codesMap = loadYaml("contract/error/codes.yaml");
        wireMap  = loadYaml("contract/wire-v1.yaml");

        @SuppressWarnings("unchecked")
        Map<String, Object> codes = (Map<String, Object>) codesMap.get("codes");
        if (codes == null || codes.isEmpty()) {
            throw new IllegalStateException(
                "ContractLoader: contract/error/codes.yaml loaded but 'codes' map is empty. " +
                "Check processResources copy path in build.gradle.kts.");
        }
        log.info("ContractLoader: loaded " + codes.size() + " error codes from codes.yaml");

        String wireVersion = (String) wireMap.get("version");
        log.info("ContractLoader: wire-v1 contract version = " + wireVersion);
    }

    /**
     * Returns the HTTP status integer for a given error code string.
     * Falls back to 500 if the code is not in the catalog (defensive — should not happen).
     */
    public int httpStatusFor(String code) {
        @SuppressWarnings("unchecked")
        Map<String, Object> codes = (Map<String, Object>) codesMap.get("codes");
        if (codes == null) return 500;

        @SuppressWarnings("unchecked")
        Map<String, Object> entry = (Map<String, Object>) codes.get(code);
        if (entry == null) return 500;

        Object status = entry.get("http_status");
        if (status instanceof Integer i) return i;
        if (status instanceof Number n) return n.intValue();
        return 500;
    }

    /**
     * Returns the English message for a given error code string.
     * Falls back to a generic message if the code is not found.
     */
    public String messageFor(String code) {
        @SuppressWarnings("unchecked")
        Map<String, Object> codes = (Map<String, Object>) codesMap.get("codes");
        if (codes == null) return "An error occurred.";

        @SuppressWarnings("unchecked")
        Map<String, Object> entry = (Map<String, Object>) codes.get(code);
        if (entry == null) return "An error occurred (" + code + ").";

        Object msg = entry.get("message");
        return msg != null ? msg.toString() : "An error occurred.";
    }

    /**
     * Returns the contract version string from wire-v1.yaml.
     */
    public String wireVersion() {
        Object v = wireMap.get("version");
        return v != null ? v.toString() : "unknown";
    }

    // ── internal helpers ──────────────────────────────────────────────────────

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
                "ContractLoader: failed to load " + classpathResource + " — " + e.getMessage(), e);
        }
    }
}
