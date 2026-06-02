# learn-log — QA (CQO)

> Quality gate. 가드 통과 기준·4계층 풀테스트·agent 산출물 감사 인격의 ledger.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 인격 헌장: [`.claude/agents/qa-agent.md`](../../.claude/agents/qa-agent.md).

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Audit target: <감사 대상 — 가드 / 풀테스트 / agent 산출물>
- Pass criteria defined / refined: <통과 기준 결정 사항>
- False PASS / False FAIL risks: <발견·평가한 위험>
- Regression cases: <PASS→FAIL 전환 사례>
- Blocks issued: <머지 차단 카운트>
- Cost: <turns / 추정 $>
```

## §2 — Growth History

(이 인격은 Growth-4 에서 신설됨. 첫 실전 가동은 M1 진입 시 — 4계층 풀테스트 통과 기준 문서화.)

### Growth-5a (2026-05-29) — G-9 통과 기준 위임 검토 (QA agent 미가동, CTO 임시 권한)

- **Audit target**: G-9 가드 (main learn-log §6 슬림 cap)
- **Pass criteria defined / refined** (CTO 가 QA 부재 동안 임시로 박음, QA 첫 가동 시 재검토):
  - 본문 비-blank ≤ 10행 / `### Growth-N` 엔트리
  - 슬림 §6 (divider 이후) 전체 비-blank ≤ 200행
  - 코드 펜스 (```...```) 내부는 카운트 제외 — spec template 이 자기 가드에 안 걸려야 함
- **False PASS / False FAIL risks (CTO 가 미리 노트)**:
  - 거짓 PASS: 한 줄에 긴 prose 가 박히면 줄 수는 통과해도 가독성 손실 — 향후 길이 cap 추가 검토
  - 거짓 FAIL: 코드 펜스 외 인용 블록 (`>`) 은 활성으로 카운트됨, 의도된 행동
- **Regression cases**: 없음 (신설)
- **Blocks issued**: 0 (감사 인격 미가동)
- **Cost**: 0 turns (CTO 가 위임 권한으로 박음)
- **Note**: 본 엔트리는 *위임 결정 기록* 으로, QA agent 가 M1 진입 시 첫 가동되면 본 통과 기준을 인수·재평가한다.

### Growth-7 (2026-05-29) — QA 첫 실전 가동: springboot-jakarta compliance 게이트 BLOCK→PASS

- **Audit target**: 첫 backend adapter (springboot-jakarta) — swappable-layers §6 4-dimension compliance 게이트
- **Pass criteria defined**: black-box HTTP compliance suite (`tests/adapters/springboot-jakarta/`, pytest, `ADAPTER_BASE_URL` 파라미터화 — 모든 backend adapter 재사용 가능). 23 test = DIM-1 contract round-trip(8) + DIM-2 error envelope(5) + DIM-3 paging(6) + DIM-4 Growth-5d 표준(4). http_status 는 codes.yaml 에서 읽어 대조 (테스트도 single-source 준수, 하드코딩 금지).
- **False PASS / False FAIL risks**: cursor 요청 키 `mode` vs adapter `paging_mode` 불일치 적발 → contract HTTP 직렬화 컨벤션 미정 issue 를 CTO 에 에스컬레이션 (flat-underscore 표준으로 해소).
- **Regression cases**: 초기 BLOCK 2건 사후분석 — 일부는 테스트측 결함 (autouse fixture 가 entity_type 누적 오염, cursor 키 불일치). 테스트 수정 + adapter 수정 양측 환류 후 23/23 green.
- **Blocks issued**: 1 (DIM-3 2 FAIL → engineer 수정 → 재검증 해제). CQO 머지 BLOCK 권한 첫 행사.
- **G-9 통과 기준 인수**: CTO 임시 박음 (Growth-5a) → QA 정식 인수, 현행 cap (본문 10 / §6 200) 유지 판정.
- **Cost**: ~2 round Sonnet


### Growth-8 (2026-05-29) — QA 두 번째 실전 가동: vanilla-htmx frontend adapter compliance 게이트 PASS

- **Audit target**: 첫 frontend adapter (vanilla-htmx) — frontend-adapter-contract.md §3~4 4-dimension compliance 게이트
- **Pass criteria defined**:
  - DIM-1 (F-1): entity_list route 가 _proxy_request 에 넘기는 params dict 에 flat-underscore 키 (paging_mode, paging_page, paging_size, paging_cursor, sort_field, sort_direction) 만 포함. dot-notation 키 (paging.mode 등) 부재 필수. 5개 test.
  - DIM-2 (F-3): codes.yaml 의 11개 코드 전부에 대해 mock _proxy_request -> 해당 code 반환 시, 렌더 HTML 에 codes.yaml 의 message_ko 포함. AUTH_REQUIRED/AUTH_EXPIRED 는 /login redirect 검증. retriable 플래그 -> 재시도 힌트 표시/비표시. 22개 test (2개 skip = AUTH redirect codes).
  - DIM-3 (F-2): offset 마지막 페이지 disabled Next 버튼 확인, 비마지막 페이지 Next 링크 확인, cursor 모드 next_cursor 있을 때 Load-more 링크, 없을 때 end 메시지. 4개 test.
  - DIM-4 (F-4): 첫 DELETE 200 -> 삭제 완료 렌더, 두 번째 DELETE (F-4 mapped success) -> 삭제 완료 렌더, _proxy_request unit (404+DELETE -> {success:True}/200), 음성 (404+GET 미재매핑), GET confirm+NOT_FOUND -> success 페이지. 5개 test.
  - L1: frontend/adapters/vanilla-htmx/tests/ subprocess rc=0. 1개 test.
  - L3: build_tokens.py exits 0, tokens.css >= 5 CSS custom property. 2개 test.
  - L4: live adapter /health + /login 검증 (optional, skip if not running). 2개 test (skipped).
  - **총 41개 collected / 37 PASSED / 4 SKIPPED (AUTH redirect x2 + L4 live x2) / 0 FAILED / RC=0**
- **Single-source 준수**: message_ko / retriable / http_status 모두 ContractLoader().codes() 에서 런타임 로드. 코드 문자열 하드코딩 없음. 템플릿 실제 문자열은 template 파일 파싱으로 추출 후 assertion 에 삽입.
- **False PASS / False FAIL risks**:
  - 거짓 PASS 위험: flask_client fixture 가 importlib.reload(server) 로 app 재생성 — 픽스처 간 상태 누적 방지 (Growth-7 교훈 적용). FakeHTTPError 가 b{} 빈 바디 반환 -> _proxy_request 가 {} 를 파싱, 404+DELETE 는 mapping 전에 분기되므로 payload 검사 불필요. 검증됨.
  - 거짓 FAIL 위험: conftest flask_client 가 session token 자동 주입 — _require_login 데코레이터 우회. 없으면 모든 entity route 가 redirect 해 F-1/F-2/F-3/F-4 테스트 전부 false-FAIL.
- **CSRF 부재 (Known Gap)**: engineer README.md 가 M1 dev-mode known-gap 으로 명시. 생산 hardening (flask-wtf 또는 custom CSRF) 는 M1 이후 Growth. 이 게이트의 범위 밖 — CSRF 는 wire-protocol compliance (F-1~F-4) 와 무관한 보안 레이어. QA 스코프: contract compliance. CSRF 는 보안 audit (별도 게이트 예정).
- **Regression cases**: 없음 (신설)
- **Blocks issued**: 0 (37/37 green, 4 explicit skip)
- **Cost**: ~3 round Sonnet


### Growth-10 (2026-06-01) -- L2 HSQLDB gate: DDL catalog smoke, BLOCK (3 renderer defects)

- **Audit target**: DDL axis (Stage 2) -- presets/ddl/catalog.yaml (56 entities, 14 domains) + render.py
- **Runner**: Java + HSQLDB 2.7.4 in-memory JDBC (canonical L2 per CLAUDE.md par-8). No external framework.
  - Entry: python tests/ddl/run_l2.py (generates schema + patches + compiles + runs)
  - Harness: tests/ddl/L2HsqldbSmokeTest.java (47 assertions, single-class)
  - Patch script: tests/ddl/patch_schema.py (3 renderer defect workarounds)
- **Pass criteria (L2 PASS = 의도된 violation 외 0 error)**:
  - S0: All 56 CREATE TABLE DDL loads into HSQLDB in-memory with 0 errors.
  - S1: 30 positive inserts across 14 domains succeed (valid rows only).
  - V1-V11: Each intended violation raises a JDBC SQLException (never silently succeeds).
  - OD1-OD3: ON DELETE SET NULL/RESTRICT/CASCADE behave per catalog declaration.
  - Unintended error on positive insert = BLOCK. Intended violation that does not fire = BLOCK.

- **Smoke matrix result (live run 2026-06-01)**:
  - S0 raw schema: 11 OK / 125 errors -- BLOCK (3 renderer defects)
  - S0 patched: 137 OK / 0 errors -- schema loads cleanly after patch
  - S1 positive inserts: 30/30 PASS
  - V1-V11 violations: 11/11 PASS (PK, UNIQUE, FK-restrict, enum-CHECK, range-CHECK, NOT-NULL, composite-UNIQUE all fire)
  - OD1-OD3 on_delete: 6/6 PASS (SET NULL verified by column value query, RESTRICT by blocked delete, CASCADE by row count)
  - Total: 47 PASS / 3 DEFECT (all renderer bugs, not catalog or test bugs)

- **3 renderer defects found (all in render.py, NOT catalog.yaml)**:
  1. **S0-D1 (forward-FK)**: topological sort emits hr_department before hr_employee, keeping manager_id FK inline. HSQLDB rejects FK to non-existent table at CREATE TABLE time. Fix: detect circular back-edges and defer as ALTER TABLE ADD CONSTRAINT after both tables exist.
  2. **S0-D2 (unquoted CHECK cols)**: render_table() passes catalog constraints[].expr literally without quoting column names. Unquoted identifiers fold to uppercase and fail against quoted lowercase column names. Affects 28 of 72 CHECK constraints. Fix: render.py must parse expr tokens and wrap column names in dialect identifier-quote char.
  3. **S0-D3 (DEFAULT order)**: render_column() emits TYPE NOT NULL DEFAULT value. HSQLDB requires TYPE DEFAULT value NOT NULL (DEFAULT before constraints). Affects 1 column (inventory_item.allow_negative_stock). Fix: render_column() must place DEFAULT before NOT NULL.

- **Scope boundary (DDL vs application layer)**:
  - L2 scope: PK, UNIQUE, FK/on_delete, enum CHECK, range CHECK, NOT NULL. All DDL-encoded per catalog.
  - Out of L2 scope (app layer, per engineer Growth-10): overlapping-leave, headcount enforcement, circular FK prevention, state-machine, immutability, balanced debit/credit, cross-table value comparisons.
  - finance_journal_entry.period_id FK omission: accounting_period not in catalog. Deferred catalog-scope item, not an L2 concern.

- **False PASS / False FAIL risks**:
  - False PASS guard: harness always runs raw schema first, records all 3 defects, exits RC=1 (BLOCK) even when patched load succeeds. Prevents silent acceptance of broken DDL.
  - False FAIL guard: patch_schema.py uses surgical string substitutions tested against 72 CHECK constraints and all known column patterns. No over-patching observed.
  - Known harness limitation: split on ; does not handle semicolons inside DDL string literals. Acceptable for current catalog DDL (no such patterns exist).

- **Regression policy**: when engineer fixes a renderer defect, remove the corresponding patch from patch_schema.py. L2 gate must re-run against raw schema to confirm S0 passes without that patch.
- **Blocks issued**: 1 (L2 BLOCK -- 3 renderer defects in render.py, routed to engineer)
- **Cost**: ~40 turns Sonnet

#### Re-verification (2026-06-01) -- engineer fix applied, verdict flips to PASS

Engineer fixed all 3 renderer defects in render.py:
- D1: topological_order() detects circular back-edges, emits deferred ALTER TABLE after target table.
- D2: _quote_check_expr() added; wraps bare lowercase column tokens in dialect quote char for all constraints[].expr.
- D3: DEFAULT moved before NOT NULL in render_column() parts list.

Re-verification on raw schema (no patch_schema.py applied):
- render.py regenerated: 1034 lines, 0 WARNING in stdout.
- hr_department CREATE TABLE: manager_id FK line ABSENT (column stays, constraint deferred to ALTER TABLE at line 69, after hr_employee at line 50).
- CHECK constraints: CHECK (transit_days > 0 quoted), CHECK (probability >= 0 quoted) -- all column names now use identifier quotes.
- allow_negative_stock: BOOLEAN DEFAULT FALSE NOT NULL -- correct order.

Patch no-op confirmation (all 3 True):
- Patch 1 no-op: True -- inline manager_id FK line absent from raw schema.
- Patch 2 no-op: True -- 0 unquoted-identifier CHECK constraints in raw schema.
- Patch 3 no-op: True -- 0 NOT-NULL-before-DEFAULT occurrences in raw schema.

L2 gate result on raw schema (2026-06-01):
- S0: 137 OK / 0 errors -- PASS (key flip from 11 OK / 125 errors in Growth-10 original run)
- S1: 30/30 PASS
- V1-V11: 11/11 PASS
- OD1-OD3: 6/6 PASS
- Total: 48 PASS / 0 FAIL / 0 DEFECT. RC=0.

**VERDICT: PASS. Merge gate cleared.**

patch_schema.py disposition: KEEP as audit record -- see QA recommendation below.


### Growth-11 (2026-06-01) -- fastapi adapter shared-suite gate: PASS + single-source refactor

- **Audit target**: 두 번째 backend adapter (fastapi) — shared black-box compliance suite, adapter-agnostic claim 검증
- **Pass criteria (shared, inherited from Growth-7)**: 동일 suite (`test_compliance.py` 23 tests, DIM-1~DIM-4), `ADAPTER_BASE_URL=http://localhost:8081` 로 타겟 변경. 모든 assertions 무변경. 0 SKIP / 0 FAIL / RC=0 이면 PASS.
- **Suite execution result (live run 2026-06-01)**:
  - Adapter launched: uvicorn 8081, health OK
  - DIM-1 Contract round-trip (8 tests): 8/8 PASSED
    - status.health, auth.login, auth.logout, entity.create, entity.read, entity.list, entity.update(PATCH), entity.delete
  - DIM-2 Error envelope (5 tests): 5/5 PASSED
    - NOT_FOUND (read + update missing id), AUTH_FAILED (bad creds), BAD_REQUEST (missing fields), envelope shape
  - DIM-3 Paging (6 tests): 6/6 PASSED
    - page1 count, page2 count, last-page remainder (7 items / size 3 = 1 remainder), no overlap, total consistency, cursor=BAD_REQUEST
  - DIM-4 Standards (4 tests): 4/4 PASSED
    - idempotent double-delete, cold delete never-created id, PATCH partial field update, PATCH read-back no nullification
  - **Total: 23/23 PASSED. RC=0. 0 FAILED. 0 SKIPPED.**
- **Adapter-agnostic claim verdict**: HELD. Identical suite (zero assertion changes), Java SpringBoot and Python FastAPI both 23/23. One wire contract drives two backend runtimes identically.
- **False PASS / False FAIL risks**:
  - False PASS guard: in-memory store is test-session-scoped; each test uses `_RUN_TAG` + test-name prefix to isolate entity_types. No cross-test contamination observed (DIM-3 paging seed fixture uses per-test `_et` suffix — Growth-7 isolation fix carries over correctly).
  - False FAIL risk: none identified. Fastapi error codes and http_status are resolved at runtime from `codes.yaml` via `ContractLoader` (G-1). No hardcoded status divergence possible.
  - cursor BAD_REQUEST test: fastapi accepts `paging_mode=cursor` (flat-underscore, preferred key, same as springboot BUG-2 fix). No springboot-specific coupling found.
- **Single-source decision (QA test-policy call)**: OPTION (b) — refactor to adapter-neutral location.
  - Canonical file moved to: `tests/adapters/_shared/test_compliance.py`
  - Parent conftest added: `tests/adapters/conftest.py` — URL-only `adapter_base_url` fixture (reads ADAPTER_BASE_URL env var). Picked up by `_shared/` tests via directory ancestry.
  - FastAPI gate conftest added: `tests/adapters/fastapi/conftest.py` — uvicorn auto-launch, mirrors springboot conftest structure.
  - Shared suite verified: `ADAPTER_BASE_URL=http://localhost:8081 pytest tests/adapters/_shared/ -v` -> 23/23 PASSED. RC=0.
  - Rationale for (b): a test file named after one adapter but gating all backends is a naming lie that will cause future engineer confusion and drift. Two adapters justify the refactor. Cost: low (parent conftest 30 lines, new dirs + README).
  - Dedup CLOSED (Growth-11 follow-up, CTO instruction): `tests/adapters/springboot-jakarta/test_compliance.py` replaced with a 1-line import-star shim: `from tests.adapters._shared.test_compliance import *  # noqa: F401,F403`. Assertions now exist in exactly ONE file. Shim surfaces all 23 test classes under the springboot-jakarta path so the gradle conftest fixture applies; `_shared/` is the canonical source. Both dirs collect 23 (verified `--collect-only`). Live run vs fastapi: 23/23 PASSED RC=0.
  - springboot collect verified post-refactor: 23 tests collected, RC=0. No regression.
- **Regression cases**: none (new adapter, no prior gate)
- **Blocks issued**: 0. 23/23 green on first live run. No defects found.
- **Cost**: ~1 round Sonnet


### Growth-12 (2026-06-01) -- DIM-5 Validation gate: PASS (both adapters identical)

- **Audit target**: DIM-5 validation dimension added to shared compliance suite -- both springboot-jakarta and fastapi must pass identically. Validates that catalog-driven validation (validation-contract.md §3/§4) is correctly wired in both adapter implementations.
- **Pass criteria (QA definition)**:
  - S1 (missing required): POST /api/entities/employee without full_name => VALIDATION_ERROR 422, details.fields contains full_name key.
  - S2 (bad enum): status=bogus => VALIDATION_ERROR 422, details.fields.status present.
  - S3 (length exceeded): employee_number > 64 chars => VALIDATION_ERROR 422, details.fields.employee_number present.
  - S4 (type mismatch): headcount_limit=abc on position (integer field) => VALIDATION_ERROR 422, details.fields.headcount_limit present.
  - S5 (unique collision): same employee_number twice => CONFLICT 409 (NOT VALIDATION_ERROR), details.fields.employee_number present.
  - S6 (schema-less pass-through): entity_type=product (not in catalog) => 201 success, no validation. Backward-compat guard.
  - S7a (PATCH bad enum): PATCH status=bogus => VALIDATION_ERROR 422. Validates partial-update validation path.
  - S7b (PATCH omit required): PATCH body omitting full_name (required on create) => 200 OK. Required check skipped on PATCH (PATCH semantics).
  - http_status for VALIDATION_ERROR and CONFLICT read from codes.yaml via _http_status() -- no hardcoding. Single-source discipline maintained.
  - Run-unique employee_number tags (via _RUN_TAG) prevent cross-test unique collisions. Follows Growth-7 isolation lesson.
- **Suite result -- fastapi (live run 2026-06-01)**:
  - S1 PASSED, S2 PASSED, S3 PASSED, S4 PASSED, S5 PASSED, S6 PASSED, S7a PASSED, S7b PASSED
  - Prior DIM-1~4: 23/23 PASSED (regression: 0)
  - Total: 31/31 PASSED. RC=0. Runtime: ~183s (session-scoped paging fixture creates many entities).
- **Suite result -- springboot-jakarta (live run 2026-06-01)**:
  - S1 PASSED, S2 PASSED, S3 PASSED, S4 PASSED, S5 PASSED, S6 PASSED, S7a PASSED, S7b PASSED
  - Prior DIM-1~4: 23/23 PASSED (regression: 0)
  - Total: 31/31 PASSED. RC=0. Runtime: ~25s (in-memory JVM, already warm).
- **Adapter-agnostic claim for DIM-5**: HELD. Identical 8 assertions, zero divergence between Java SpringBoot and Python FastAPI. Both catalogs loaded at runtime from presets/ddl/catalog.yaml (G-1 compliant). Both error envelopes produce VALIDATION_ERROR/CONFLICT with details.fields per codes.yaml contract.
- **False PASS / False FAIL risks**:
  - False PASS guard: S5 checks CONFLICT (409), not VALIDATION_ERROR (422). The validators correctly split UNIQUE-kind errors (CONFLICT) from INVALID-kind errors (VALIDATION_ERROR). Both adapters implement this split identically. Assertion checks the code string from codes.yaml, not the integer status.
  - False PASS guard: S6 (schema-less) verifies entity_type=product passes THROUGH validation entirely (201), not that it fails silently. If the catalog unexpectedly contained a product entity, this test would act as a regression detector.
  - False FAIL risk: department_id is uuid type (FK existence NOT checked per section 5 scope). Tests supply a random uuid4() value -- both adapters accept any string for uuid fields. No FK validation means the test does not depend on a pre-existing department record.
  - False FAIL risk: S5 unique collision requires the first create to succeed (201). Each test run gets a fresh _RUN_TAG prefix, so no cross-run collision. The UNIQ- prefix is different from the EMP- prefix used in S1~S3, S7a, S7b -- no intra-run collision either.
- **Regression cases**: none. DIM-1~4 all PASSED on both adapters post DIM-5 addition (no suite interference).
- **Blocks issued**: 0. Both adapters passed DIM-5 on first live run. No defects found in either implementation.
- **Cost**: ~3 round Sonnet (significant time spent on bash quoting issue for file append; resolved via triple-single-quote in double-quoted python -c)

### Growth-15 (2026-06-01) — DIM-6 FK 참조 무결성 감사 (PASS-WITH-CAVEAT)

- **감사 대상**: runtime FK 검증 (양 backend CatalogValidator `_check_fk`/`checkFk`) + DIM-6 suite + G-12 가드 + catalog hygiene. push 전 감사.
- **로직 패리티 (Java live 불가 → 적대적 read)**: Python `_check_fk` vs Java `checkFk` 5조건 전수 대조 — (A) fk 블록 없으면 skip(구조적 게이트, 컬럼명/하드리스트 아님), (B) null/absent skip, (C) 부재 참조 → `FieldError.invalid(col, "referenced <entity> not found")` 동일 메시지·INVALID kind, (D) errors 결합 non-fail-fast, (E) http_status codes.yaml 경유(하드코딩 0). **5/5 IDENTICAL, divergence 0**.
- **DIM-5 회귀 수정 판정**: 이전 DIM-5 가 `department_id` 에 fake uuid4() 사용 — 본 ledger Growth-12 엔트리의 "False FAIL risk: FK existence NOT checked per §5" 가정이 **Growth-15 로 뒤집힘** (이제 FK enforce). `_ensure_department()` 로 실 department 생성·id 사용 = **정당 수정** (employee.department_id 는 catalog fk 블록 보유, fake uuid 는 no-FK 시절에만 유효했던 latent 결함). 마스킹 아님 (`s==201` assert 로 setup 실패 시 loud).
- **DIM-6 진정성**: F1~F6 전부 distinct path. F1(negative — bogus carrier_id → 422 + fields.carrier_id "not found", 2-layer assert), F6(fk-exempt journal-entry.period_id → 201, exempt 경계 canary) 이 핵심. hollow 0.
- **재현**: diagnose 12 가드 0 FAIL, G-1/G-12 PASS 확인. fastapi live 37(DIM-1~6)은 implementer 보고치 — 본 세션 server 미기동으로 독립 재현 불가(로직 정확하므로 plausible).
- **Blocks issued**: 0. **CAVEAT carry (regression checkpoint)**: Java `checkFk`+DIM-6 는 live 미실행 (JDK/Gradle 환경 부재). M1 sign-off 전 JDK 환경서 `ADAPTER_BASE_URL=http://localhost:8080 pytest tests/adapters/springboot-jakarta/ -q` → 37 test rc=0 확인 후 이 ledger 에 기록 필수. = 검증 갭(코드는 read 로 정확 증명), 결함 아님.
- **Cost**: ~1 round.

### Growth-16 (2026-06-02) — react frontend adapter 감사 (PASS-WITH-CAVEAT → caveat 클로즈)

- **감사 대상**: react adapter (2nd frontend). push 전 머지 게이트. Node v24 + fastapi 가용.
- **G-1 단일진실 (적대적 grep)**: react `src/` 에서 wire endpoint path / error code 문자열 / http status 정수(404/422/409) / dotted paging 검색 → **하드코딩 0**. 전부 `contract.gen.ts`(생성) 경유. 유일 404 는 DeleteScreen 주석(실행 아님). `/login`·`/entities/:type` 는 **SPA router path**(frontend 내비) — wire endpoint 아니므로 G-1 대상 외. diagnose 4 adapter 47 파일 G-1 PASS.
- **F-1~F-4 검증**: F-1 buildListParams flat-underscore(5 케이스 실 URLSearchParams 단언). F-3 error.code 분기(텍스트 분기 아님)+message_ko Hangul 체크. F-4 404·200 양 경로 mock 단언+UI already-deleted. F-2 offset+cursor+next_cursor forwarding.
- **재현 (QA 직접)**: L1 `npm test` 27 pass/8 skip(env-gated, 진짜 skip). L3 `npm run build` exit 0(dist 생성, tsc strict 클린). L4 미재현(포트/env — implementer 보고 35 @ fastapi). 토큰 hex: `app.css`+`.tsx` raw hex **0**(tokens.gen.css 의 hex 는 생성물=정상). vanilla-htmx 37 무회귀. node_modules 미커밋.
- **CAVEAT 발행 → 클로즈**: F-2 offset-last-page 테스트가 hollow(순수 산술, adapter 미접촉) — PASS-WITH-CAVEAT 발행. CTO 가 즉시 수정 위임 → `hasMorePages` 순수 헬퍼(ListScreen+test 공유) 4 케이스, 27→30 test, fails-closed 증명. **caveat 해소 확인**.
- **Blocks issued**: 0 (BLOCK 사유 없음 — 하드코딩 0, false PASS 0). caveat 1 발행·동일 세션 클로즈.
- **Cost**: ~1 round (L1/L3 재현 + 적대 grep).

### 검증 체크포인트 (2026-06-02) — Java-env sign-off 게이트 CLOSED (Growth-15·16 carry 종결)

- **계기**: 이전 sub-agent 가 "JDK/Gradle 없음"으로 springboot live 를 못 돌렸으나, **메인 머신엔 JDK 21 + Gradle wrapper(`./gradlew`) 존재** (false-negative — system `gradle` 만 찾고 wrapper 미사용). CEO "#1 진행" 지시로 실행.
- **L1/L3 (gradlew)**: `gradlew clean test` — `CatalogValidatorTest` **22 pass**(15→22, Growth-15 FK 7개 첫 실행 전원 PASS) + `EntitySmokeTest` 8 = 30 pass 0 fail. `gradlew build` SUCCESSFUL.
- **L4 springboot DIM-1~6 (port 9081)**: `ADAPTER_BASE_URL=...:9081 pytest tests/adapters/springboot-jakarta/` → **37 PASS rc=0**. DIM-6 F1~F6 전원 PASS = **Growth-15 Java FK carry 종결** (Java 상대 첫 live).
- **L4 react↔springboot**: `BACKEND_BASE_URL=...:9081` → **36 pass / 2 skip**. 2 skip = Vite preview SPA 쉘 테스트(`describe.skipIf(!FRONTEND)`) — wire 계약 아닌 SPA 쉘, **M1 설계상 허용·M2 first-customer 게이트 전 활성 필수**. **Growth-16 carry 종결**.
- **diagnose**: 12 가드 0 real FAIL.
- **발견 (CTO 기록용)**: system PATH JDK 21 ↔ Gradle daemon JDK 17 (`C:\Program Files\Java\jdk-17`). Spring Boot 3.2.5 는 17+ 요구라 무해. JDK21 전용 기능 필요 시 `gradle.properties org.gradle.java.home` 또는 toolchains 갱신.
- **Blocks**: 0. **M1 Java sign-off 게이트 PASS.**

### 검증 체크포인트 (2026-06-02) — vanilla-htmx entity.list 회귀 가드 추가 (L4 가시성 공백 봉합)

- **계기**: 데모 촬영 prep 중 engineer 가 vanilla-htmx `entity_list` 의 실 버그 적발·수정(`6c13137`) — outbound 백엔드 쿼리에 `entity_type` 주입(레코드 필터 오인 → **모든 목록 화면 0행**) + paging 키 contract 불일치. **L4 공유 compliance 가 백엔드 API 만 직접 쳐서 Flask 라우트를 미경유**, 못 잡은 가시성 공백.
- **추가 가드**: `frontend/adapters/vanilla-htmx/tests/test_entity_list_params.py` (`50bebe6`) — Flask test client 로 라우트를 실제 통과시키고 `_proxy_request` 경계를 monkeypatch 로 가로채 outbound `params`/`path` 캡처. **12 케이스**: offset(6)·cursor(3)·sort/search(3). `_CONTRACT_KEYS` 만 유출·`_FORBIDDEN_KEYS`(entity_type/paging_page/paging_size/filter_search/paging_cursor) 무유출 단언.
- **진위(가드가 진짜 잡는가)**: server.py 를 버그 버전으로 일시 revert → 신규 테스트 **RED**(forbidden keys leaked 등 정확 지목), 원복 후 green. 가드 약화 아닌 실효 가드.
- **결과**: fe 스위트 56 pass(44+12) / 21 skip, diagnose 12 가드 0 real FAIL. **learn-log §4 의 "QA 후속(open)" 닫힘.**
- **설계 메모(감사용)**: 모킹 지점 = 라우트가 params 를 넘기는 경계(`_proxy_request`). 안쪽(urllib)이면 URL 인코딩까지 검증해 취약, 바깥(라이브)이면 L4 중복+backend 의존. 경계 캡처가 "라우트가 contract 키만 조립하는가"를 최저비용 직접 핀.

## §3 — Open Loops (이 인격 책임)

- ~~[Growth-15 carry] Java DIM-6 live~~ ✅ **CLOSED 2026-06-02** (springboot 37 PASS, 위 체크포인트). react↔springboot L4 36 PASS 도 동시 종결.
- **[M2 전] Vite preview SPA 테스트 2건 활성** — `FRONTEND_BASE_URL` 세팅 후 react `describe.skipIf(!FRONTEND)` 블록 실행 (M1 허용, M2 first-customer 전 필수).
- 현행 가드 9개 (G-1~G-9) 의 거짓 PASS / 거짓 FAIL 위험 평가 — 첫 가동 시
- G-9 통과 기준 인수·재평가 (CTO 임시 박음 → QA 정식 검토)
- ~~M1 진입 게이트 통과 기준 문서화 — L1~L4 각각의 PASS 정의~~ PARTIAL: L2 PASS 기준 Growth-10 에서 정의됨. L1/L3/L4 는 M1 진입 시 해소 예정.
- regression 이력 섹션 초기화 (이 파일 §4 로 분리 예정)
