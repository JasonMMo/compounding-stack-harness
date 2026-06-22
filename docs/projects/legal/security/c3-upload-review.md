# CISO Security Review: G-2 C3 Document Upload + Async Ingest

Reviewer: CISO (security-agent) | Date: 2026-06-22 | Verdict: PASS-WITH-CAVEAT

---

## 1. Threat Surface

| Surface | Source | Trust |
|---|---|---|
| Upload endpoint | multipart/form-data: file + fields | Untrusted (post-JWT) |
| Filename | file.filename (client) | Untrusted (traversal origin) |
| File body | file.read() binary | Untrusted (pre-validation) |
| DB INSERT | rls_session(conn, attorney_id) | Trusted (RLS WITH CHECK) |
| Disk write | uuid-prefixed path under storage_root | Trusted (realpath+commonpath) |
| BackgroundTask | app_service BYPASSRLS fresh conn | Internal trusted |
| External network | local embed sidecar only | No external egress |

---

## 2. History Search

- Growth-95: BYPASSRLS RLS bypass BLOCK resolved by rls_session SET LOCAL ROLE app_user.
- C1/C2: SQLSTATE 42501 direct-catch unimplemented. Same substring match pattern in C3 (Item D, 3rd occurrence).

---

## 3. Secret Scan

- No .env in services/legal-rag. Root .gitignore lines 40-41 list .env.
- git log --all --diff-filter=A: no .env commit history.
- config.py: jwt_secret/service_token/db_dsn via _require() env-only. No plaintext.
- api.py bcrypt dummy hash: timing-guard public value, not a credential.
- 10_production_hardening.sql sec 3: password placeholder is comment text, not DDL.

RESULT: Secret exposure = 0. PASS.

---

## 4. Vulnerability Classes

### A. Size-check Order (Memory DoS) -- CAVEAT-A

Location: api.py:1270

    content = await file.read()           # entire body loaded
    if len(content) > _UPLOAD_MAX_BYTES:  # fires AFTER full load

- No ContentSizeLimitMiddleware in middleware stack.
- Chunked-encoding >=21 MiB fully buffered before limit fires.
- Self-host single-tenant internal-network: not BLOCK-level risk.
- Recommendation: client_max_body_size 22m in Traefik/nginx upstream. Add to deployment guide.

VERDICT: CAVEAT-A (non-blocking)

---

### B. Path Traversal -- PASS

Locations: api.py:457-474, api.py:477-486, api.py:1283-1291

1. os.path.basename(): strips all dir separators (Unix and Windows). ../../../etc/passwd -> passwd.
2. _SAFE_FILENAME_RE: null byte and Unicode path-separators -> _.
3. uuid4().hex_ prefix: sanitized name cannot introduce new path segments.
4. Dual guard: realpath(root)+realpath(target) then commonpath==root. Symlink escape blocked.

VERDICT: No vulnerability. PASS.

---

### C. Extension / Content-Type Validation -- CAVEAT-C

Locations: api.py:429, 432-438, 1253-1267

1. Double-extension (x.pdf.exe): splitext -> .exe -> allowlist reject -> 400. PASS.
2. application/octet-stream in _ALLOWED_CONTENT_TYPES: intentional (no false-positive rejection).
3. Magic bytes not verified before disk write. No execution path; parser vuln needed for exploit.
- Recommendation: python-magic or manual header check (%PDF- for pdf, PK zip for docx).

VERDICT: CAVEAT-C (non-blocking)

---

### D. RLS->404 Substring Match -- CAVEAT-D

Location: api.py:1330-1335

Current code: any(kw in str(exc).lower() for kw in ("policy","check","permission","rls"))

Issues:
1. Keyword "check" appears in CHECK constraint violations (SQLSTATE 23514).
   document_type DDL mismatch could yield false-positive 404 (low practical risk).
2. psycopg3 wrapping: RLS message visibility in str(exc) version-dependent.
3. THIRD OCCURRENCE: same caveat in C1 and C2. Guard threshold met.

Recommended fix:
    from psycopg import errors as pg_errors
    except pg_errors.InsufficientPrivilege:
        raise HTTPException(status_code=404, ...)
Catches SQLSTATE 42501 only; CHECK constraint (23514) is a separate class.

VERDICT: CAVEAT-D (non-blocking) -- GUARD PROPOSAL G-N+1

---

### E. Background Ingest Isolation -- PASS

Locations: api.py:1140-1187, ingest.py:257-258, 10_production_hardening.sql:85

1. case_id re-validation: validate_source_exists() on doc_id in ingest_file. Integrity layer beyond INSERT-time RLS.
2. Connection isolation: fresh pool.connection() (app_service BYPASSRLS). No shared conn.
3. Column-scoped grant alignment: GRANT UPDATE (ingest_status, ingested_at) to app_service (line 85).
   _UPDATE_CASE_DOC_STATUS_SQL updates exactly those two columns. In alignment. PASS.
4. Error path: separate err_conn. Ingest rollback cannot corrupt error-status write.
5. OQ-9 (pending stranded on restart): operational concern, not a security defect.

VERDICT: No vulnerability. PASS.

---

### F. Secret / PII Log Exposure -- PASS

- api.py:1290: logs root+target to server log on path-safety violation; HTTP response generic.
- api.py:1352-1353: logs doc_id+storage_path; client gets generic 500.
- Original filename not in DB/response; only sanitized+uuid storage_key persisted.
- ingest.py:317: source_id UUID + chunk count only. No file content.

VERDICT: No PII/path external exposure. PASS.

---

### G. Dependency CVE -- CAVEAT-G

Target: requirements.txt:23 -- python-multipart>=0.0.9,<1.0

- CVE-2024-53498 (python-multipart < 0.0.18): ReDoS in multipart boundary parser.
  Lower bound 0.0.9 allows vulnerable versions 0.0.9 through 0.0.17.
- No lockfile; fresh pip install may pull vulnerable version.
- Recommendation: Raise to >=0.0.18, or add pip-compile lockfile.

VERDICT: CAVEAT-G (non-blocking)

---

## 5. Data Boundary (A5 Constraint)

| Flow | Verdict |
|---|---|
| File body -> disk | Internal persistent volume only. No egress. |
| File body -> embed sidecar | Local/internal sidecar (config.py: No cloud fallback). |
| Legal document -> external LLM | No path. Lite tier, no generation step. |

A5 CONSTRAINT PASS. Customer data does not exit the self-hosted network.

---

## 6. RLS Live Isolation Status

Static analysis only (live DB access prohibited per scope constraint).
Design: rls_session(B) INSERT into case_A -> InsufficientPrivilege -> 404.
Live gate = founder (pytest -m postgres, Growth-101 DSN pattern).

---

## 7. CISO Gate: AC-08 through AC-12

| AC | Verdict | Basis |
|---|---|---|
| AC-08 Upload success, RLS positive | PASS (design) | rls_session + WITH CHECK, INSERT-before-write |
| AC-09 Security rejects | PASS | Extension allowlist, commonpath dual guard |
| AC-10 RLS negative (cross-attorney) | PASS (design) | rls_session(B) INSERT case_A -> 404 |
| AC-11 ingest_status polling | QA scope | Out of CISO scope |
| AC-12 Volume mount | DevOps scope (OQ-7 open) | Cannot judge; infra |

---

## 8. Final Verdict

PASS-WITH-CAVEAT

BLOCK items: none.

| ID | Location | Risk | Priority |
|---|---|---|---|
| CAVEAT-A | api.py:1270 | Memory DoS if no upstream size cap | Medium |
| CAVEAT-C | api.py:432-438 | No magic bytes check; parser attack surface | Low |
| CAVEAT-D | api.py:1330-1335 | Substring check false-positive; 3rd occurrence | Medium |
| CAVEAT-G | requirements.txt:23 | CVE-2024-53498 in python-multipart range | Medium |

Guard Proposal G-N+1 (mandatory -- 3rd occurrence C1/C2/C3):
  RLS violations must be caught as psycopg.errors.InsufficientPrivilege type, not substring
  match. Substring "check" is not exclusive to RLS (also matches SQLSTATE 23514).

---

## 9. OQ-8 CISO Verdict

mime_type and file_size_bytes columns: not a security requirement.
Improves legal audit trail (D1 F-07). DBA augment candidate; not a C3 blocker.

---

## 10. Self-host Deployment Checklist Additions

- Traefik/nginx upstream: client_max_body_size 22m -- CAVEAT-A
- LEGAL_RAG_STORAGE_ROOT on persistent volume; verify file survival after restart -- AC-12/OQ-7
- storage_root: chmod 700, app_service OS user only
- python-multipart >= 0.0.18 at deploy time (pip list | grep python-multipart) -- CAVEAT-G
