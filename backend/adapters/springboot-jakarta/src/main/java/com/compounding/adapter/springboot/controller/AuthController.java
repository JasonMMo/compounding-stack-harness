package com.compounding.adapter.springboot.controller;

import com.compounding.adapter.springboot.contract.ContractLoader;
import com.compounding.adapter.springboot.contract.WireResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * auth.login  → POST /api/auth/login
 * auth.logout → POST /api/auth/logout
 *
 * Auth is intentionally STUB-grade for M1 in-memory adapter.
 * There is no real credential store; a hardcoded demo user is accepted.
 * Real auth (JWT, OAuth2, session store) is a future Growth.
 *
 * Known gap: token validation on entity endpoints is NOT enforced.
 * Tokens are stored in memory only; restart clears them.
 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private static final String DEMO_USERNAME = "demo";
    private static final String DEMO_PASSWORD = "demo";

    /** Active tokens: token → user_id */
    private final Set<String> activeTokens = ConcurrentHashMap.newKeySet();

    private final ContractLoader contractLoader;

    public AuthController(ContractLoader contractLoader) {
        this.contractLoader = contractLoader;
    }

    // ── auth.login ────────────────────────────────────────────────────────────

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, Object> body) {
        String username = (String) body.get("username");
        String password = (String) body.get("password");

        if (username == null || password == null) {
            return WireResponse.error(contractLoader, "BAD_REQUEST");
        }

        if (!DEMO_USERNAME.equals(username) || !DEMO_PASSWORD.equals(password)) {
            return WireResponse.error(contractLoader, "AUTH_FAILED");
        }

        String token = UUID.randomUUID().toString();
        activeTokens.add(token);

        String expiresAt = Instant.now().plus(8, ChronoUnit.HOURS).toString();

        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("token", token);
        resp.put("expires_at", expiresAt);
        resp.put("user_id", "demo-user-1");
        return WireResponse.ok(resp);
    }

    // ── auth.logout ───────────────────────────────────────────────────────────

    @PostMapping("/logout")
    public ResponseEntity<Map<String, Object>> logout(@RequestBody Map<String, Object> body) {
        String token = (String) body.get("token");

        if (token == null) {
            return WireResponse.error(contractLoader, "BAD_REQUEST");
        }

        // idempotent: removing a non-existent token is still success
        activeTokens.remove(token);

        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("success", true);
        return WireResponse.ok(resp);
    }
}
