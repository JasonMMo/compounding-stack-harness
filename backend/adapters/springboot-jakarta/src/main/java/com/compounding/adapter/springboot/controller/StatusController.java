package com.compounding.adapter.springboot.controller;

import com.compounding.adapter.springboot.contract.ContractLoader;
import com.compounding.adapter.springboot.contract.WireResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * status.health → GET /api/status/health
 *
 * Liveness probe. For M1 in-memory adapter there are no downstream
 * dependencies so status is always "ok".
 * Future: add checks for DB, LLM proxy, etc. as adapters are wired in.
 */
@RestController
@RequestMapping("/api/status")
public class StatusController {

    private final ContractLoader contractLoader;

    public StatusController(ContractLoader contractLoader) {
        this.contractLoader = contractLoader;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("status", "ok");
        resp.put("version", contractLoader.wireVersion());
        resp.put("checks", List.of(
            Map.of("name", "in-memory-store", "status", "ok"),
            Map.of("name", "contract-loader", "status", "ok")
        ));
        return WireResponse.ok(resp);
    }
}
