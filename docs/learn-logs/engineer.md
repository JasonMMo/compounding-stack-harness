# learn-log — Engineer

> Implementation hand. CTO 가 결정한 설계를 코드로 옮기는 인격의 ledger.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 인격 헌장: [`.claude/agents/engineer-agent.md`](../../.claude/agents/engineer-agent.md).

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Files touched: <경로 list>
- Implementation choices: <변수명·구조·error handling 등 인격 단독 결정>
- Tests added: <4계층 중 어느 layer>
- Catches surfaced: <CTO/QA 에 던진 escalation 신호>
- Cost: <turns / 추정 $>
```

## §2 — Growth History

### Growth-5d (2026-05-29) — M1 entry kickoff: wire-v1 contract + acme-erp profile

- Files touched:
  - `middle/contract/wire-v1.yaml` (신규 — 8 wire 키 정의)
  - `profiles/acme-erp.yaml` (신규 — sample ERP customer profile)
  - `docs/learn-logs/engineer.md` (this ledger)
- Implementation choices:
  - **Format: plain YAML (not OpenAPI 3.1)** — OpenAPI 3.1은 장기 목표(swappable-layers.md §8)이나, adapter 없는 M1 진입 시점에 toolchain 의존을 도입하는 것은 과도한 선행 투자. 순수 YAML로 시작해 키 구조를 확정한 뒤 CTO 결정으로 OpenAPI 로 migration.
  - **Key namespace: `<domain>.<verb>` 2-segment** — `auth.login`, `entity.read` 등. 3-segment(`entity.customer.read`)로 하면 지금은 더 명확하지만 generic contract가 도메인 수만큼 중복 선언되는 구조가 됨. entity_type을 request 필드로 받는 방식이 더 DRY.
  - **8키 선택**: auth.login, auth.logout, entity.read, entity.list, entity.create, entity.update, entity.delete, status.health — 14 generic domain 전부에서 공통으로 쓰이는 최소 집합. `entity.patch` vs `entity.update` → PATCH semantics를 update로 통일 (CTO에 escalation point 참조).
  - **`entity.delete` idempotent: true** — 동일 id를 두 번 DELETE해도 "없으면 success" 반환이 표준 REST 관행. adapter가 404를 성공으로 처리해야 함 — CTO/QA 확인 필요.
  - **profile comment에서 `yaml.safe_load` 문자열 제거** — G-4 guard가 파일 내 텍스트를 grep하므로, 주석에 해당 문자열이 있으면 오탐. "plain YAML parser dump pipeline"으로 대체.
  - **`auth.sso_client_secret: ${ACME_SSO_CLIENT_SECRET}`** — secrets 섹션 없이 auth 블록에 직접 포함. schema _README 예시(`datasource.password`)와 일관성 유지, 별도 secrets key는 CTO 결정 후 추가.
- Tests added: NONE (L1 pytest 대상 파일 없음 — contract/profile은 데이터 파일). G-4 guard pass = 사실상 L0 smoke.
- Catches surfaced (CTO escalation):
  1. `entity.update` PATCH vs PUT semantics — 현재 PATCH로 구현했으나 adapter가 PUT full-replace를 기대하는 경우 contract 변경 필요. CTO 판정 요청.
  2. `entity.delete` idempotency — 404-as-success 표준화 여부. adapter마다 다를 수 있음. contract에 명문화 필요.
  3. OpenAPI 3.1 migration timing — M1 첫 adapter 직전? 직후? CTO 결정 필요.
  4. `auth` 블록을 customer profile `secrets` 섹션으로 분리할지 — 현재 auth.sso_client_secret이 auth 블록에 있음. 별도 `secrets:` 키 추가는 schema v2 변경.
- Cost: ~12 turns / ~$0.5 추정

### Growth-7 (2026-05-29) — 첫 backend adapter springboot-jakarta + G-1 가드 구현 + paging 버그수정

- **Built**: `backend/adapters/springboot-jakarta/` — Spring Boot 3.2.5 Jakarta, 8 wire key REST, generic in-memory store, `ContractLoader` 런타임 contract 로드 (G-1 준수 — code set/status 하드코딩 0), error envelope 매핑. BUILD SUCCESSFUL, smoke 8/8, gradle wrapper 포함.
- **wire-v1.yaml fix**: 응답 error 필드 8곳 string→envelope object (codes.yaml 정합). error_envelope 공통 블록 추가.
- **G-1 활성**: `diagnose.py::g1` 본문 — codes.yaml code→http_status 쌍 로드 후 adapter 소스에서 동일줄 재선언 검출. ALLOW 필터 (주석/`andExpect`/`description`/`message`/import). springboot adapter PASS. False-negative 기록: 인접 2줄 분할 재선언 (v1 단일줄만).
- **버그수정 (QA BLOCK 환류)**: BUG-1 `list()` params null-guard 누락 → `emptyMap()` 정규화. BUG-2 cursor mode silent 200 → BAD_REQUEST (ContractLoader 경유). 회귀 테스트 3종.
- **Catch (CTO escalation)**: paging HTTP 직렬화 키 — Spring MVC 가 `paging.mode` dot-notation 을 param Map 에 누락 → CTO 가 flat-underscore (`paging_mode`) 표준 결정.
- **Cost**: ~3 round Sonnet / ~30 commits

### Growth-8 (2026-05-29) — 첫 frontend adapter: vanilla-htmx

- Files touched:
  - `frontend/adapters/vanilla-htmx/contract_loader.py` (신규 — ContractLoader.java 동형 Python 구현)
  - `frontend/adapters/vanilla-htmx/token_css_generator.py` (신규 — design/tokens/*.json → CSS custom props 생성기)
  - `frontend/adapters/vanilla-htmx/build_tokens.py` (신규 — L3 build step, tokens.css 출력)
  - `frontend/adapters/vanilla-htmx/server.py` (신규 — Flask thin server, 6 화면, reverse proxy, F-1~F-4)
  - `frontend/adapters/vanilla-htmx/templates/base.html` (신규 — persona switcher 포함 base layout)
  - `frontend/adapters/vanilla-htmx/templates/login.html` (신규)
  - `frontend/adapters/vanilla-htmx/templates/list.html` (신규 — offset/cursor 페이징 both modes)
  - `frontend/adapters/vanilla-htmx/templates/detail.html` (신규 — detail+edit form)
  - `frontend/adapters/vanilla-htmx/templates/create.html` (신규)
  - `frontend/adapters/vanilla-htmx/templates/delete_confirm.html` (신규 — 2단계 확인)
  - `frontend/adapters/vanilla-htmx/templates/delete_success.html` (신규 — F-4 idempotent success)
  - `frontend/adapters/vanilla-htmx/templates/error.html` (신규 — F-3 error.code 분기)
  - `frontend/adapters/vanilla-htmx/templates/health.html` (신규)
  - `frontend/adapters/vanilla-htmx/static/css/app.css` (신규 — semantic token var() 전용, hex 0개)
  - `frontend/adapters/vanilla-htmx/static/css/tokens.css` (생성물 — build_tokens.py 산출, 245 lines, 227 props)
  - `frontend/adapters/vanilla-htmx/tests/test_contract_loader.py` (신규 — L1 38개 중 일부)
  - `frontend/adapters/vanilla-htmx/tests/test_token_css_generator.py` (신규 — L1 38개 중 일부)
  - `frontend/adapters/vanilla-htmx/requirements.txt` (신규)
  - `frontend/adapters/vanilla-htmx/README.md` (신규 — backend adapter README 구조 mirror)
  - `docs/learn-logs/engineer.md` (this ledger)

- Implementation choices:
  - **Stack: Python + Flask** — stdlib http.server는 Jinja2 없어 템플릿 직접 구현 필요. Flask는 pip 1개, Jinja2 번들 포함, pytest repo와 언어 일관성. Heavy deps (Django, FastAPI) 없음. "single language for thin server" 충족.
  - **contract_loader.py**: ContractLoader.java 동형 — 생성자에서 YAML 로드, `get_loader()` 싱글턴. `message_ko(code)`, `is_retriable(code)`, `http_status_for(code)`, `wire_keys()` helpers. G-1: 에러 코드 문자열 하드코딩 0.
  - **F-1 flat-underscore**: `entity_list` route에서 `params` dict를 `paging_mode`, `paging_page`, `paging_size`, `paging_cursor`, `sort_field`, `sort_direction` 키로 직접 구성. `_proxy_request`는 pass-through. dot-notation 없음.
  - **F-2 paging**: offset 기본, cursor 모드 UI toggle. `next_cursor` 응답 → 다음 요청 `paging_cursor` 파라미터.
  - **F-3 error envelope**: `_render_error()` — `payload["error"]["code"]`로 분기, `loader.message_ko(code)` 사용. message text 분기 0. retriable 코드에 retry hint 렌더.
  - **F-4 idempotent delete**: `_proxy_request()` 에서 `method == "DELETE" and status == 404` → `{"success": True}` 200 합성. api_proxy pass-through도 동일 처리.
  - **CSS generator**: `_flatten_raw()` / `_flatten_semantic()` / `_flatten_persona()` 3개 walker. 참조 해소: `_resolve_ref()` — `{color.accent.600}` → raw dict traverse → "#2563EB". font shorthand 5종 skip (`_FONT_SHORTHAND_KEYS`). `_meta`/`_density`/`note`/`_`-prefix key strip. persona 파일의 `_border-input-note` key → strip 처리 (`key.startswith("_")`). 생성 결과: 245 lines, 227 CSS custom properties.
  - **app.css**: semantic var() 전용 — raw hex 0. G-1 analog (CDO 원칙 #1 준수). test_app_css_contains_no_raw_hex 으로 자동 검증.
  - **두 단계 delete 확인**: button.md a11y 요건 (KWCAG 3.3.4) — GET /delete → 확인 폼 → POST /delete → success.

- Tests added:
  - **L1** 38 tests PASS — `test_contract_loader.py` (startup, error code helpers, wire keys, G-1 spot-check), `test_token_css_generator.py` (raw layer, semantic resolution, persona overrides, strip rules, ref resolver unit, app.css hex check)
  - **L3** PASS — `python build_tokens.py` → tokens.css 생성 exit 0

- Catches surfaced (CTO 에스컬레이션 없음):
  - ops.json에 CSS override 키가 없음 (ops IS semantic baseline per persona meta). persona block 생성 시 빈 pairs → block 생략. 정상 동작.
  - `font.size-4xl` raw key 없음 → success icon에 fallback value `30px` 사용. semantic에 4xl 없으므로 app.css에서 var(--font-size-4xl, 30px) 방어적 처리.
  - htmx inline partial update는 M1 범위 외 (full page reload 방식). README Known Gaps 기록.
  - CSRF protection 미구현 — M1 dev-mode 한정. README Known Gaps 기록. Production 전 추가 필요 — CTO/QA 인지.

- Cost: ~30 turns / ~$2 추정

### Growth-10 (2026-06-01) — DDL axis (Stage 2): catalog.yaml 56 entities + dialects + render.py + G-10

- Files touched:
  - `presets/ddl/catalog.yaml` (신규 — 56 entities, 14 domains, dialect-neutral)
  - `presets/ddl/dialects/postgres.yaml` (신규 — production default dialect)
  - `presets/ddl/dialects/hsqldb.yaml` (신규 — L2 test dialect)
  - `presets/ddl/dialects/mysql.yaml` (신규 — M1 stub)
  - `presets/ddl/dialects/oracle.yaml` (신규 — M1 stub)
  - `presets/ddl/render.py` (신규 — catalog + dialect → CREATE TABLE DDL, topological order)
  - `presets/ddl/build/hsqldb-schema.sql` (생성물 — render.py --dialect hsqldb, 1032 lines)
  - `scripts/diagnose.py` (G-10 함수 + 등록)
  - `docs/learn-logs/engineer.md` (this ledger)

- Implementation choices:
  - **Type mapping decisions**:
    - `number` fields (seed) → `decimal(18,4)` — monetary amounts need fixed precision. 18 digits covers typical financial amounts; scale 4 follows GAAP practice for extended-precision currencies.
    - `reorder_point` / `estimated_value` / `amount` (non-monetary) → `decimal(14,4)` — operational quantities don't need 18 digits; 14 is enough for any realistic stock/project figure.
    - `weight_kg` / `quantity_*` fields → `decimal(14,4)` — logistics and inventory quantities need fractional precision (e.g. 12.500 kg).
    - `hours` fields → `decimal(8,2)` — max 999999.99 hours; 2 decimal places sufficient.
    - `string` with no length specified → `length: 255` (dialect `defaults.string_length`).
    - `estimated_delivery` (shipment) → `timestamp` not `date` — seed says "iso8601"; carrier ETAs carry time-of-day precision.
    - `recipient_ids`, `enum_values` (reporting) → `text` stored as JSON string — no ARRAY type in the neutral 8-type vocabulary. Application layer parses/serialises.
  - **FK decisions**:
    - `finance_invoice.counterparty_id` — cross-domain (crm_contact or procurement_vendor); FK omitted in DDL, application-layer responsibility.
    - `sales_sales_order.customer_id` — cross-domain to crm_contact; FK omitted.
    - `document_document.current_version_id` — circular dependency with document_version; FK omitted to avoid table-order deadlock. Set after first upload.
    - `production_operation.machine_id` — references an external resource registry not in this catalog; FK omitted.
    - `approval_request` subject_type/subject_id — polymorphic; FK omitted.
    - `quality_inspection_plan` reference_id — polymorphic; FK omitted.
    - `reporting_report_output.triggered_by_id` — polymorphic (employee or schedule); FK omitted.
    - All intra-catalog FKs (same-domain + cross-domain where target exists) are fully declared.
  - **Constraints that are DDL vs application-layer**:
    - DDL CHECKs encoded: `end_date >= start_date`, `amount > 0`, `quantity > 0`, `probability 0-100`, `progress_pct 0-100`, `allocated_hours > 0`, `quantity_planned > 0`, `scheduled_end >= scheduled_start` (3-way NULL-safe), `transit_days > 0`, `default_useful_life_years > 0`, `current_book_value >= 0`, etc.
    - Application-layer only (NOT encoded in DDL): overlapping-leave check, headcount_limit enforcement, circular FK prevention (department/task/BOM), state-machine transitions, immutability rules (posted journal, tracking events, stock movements, etc.), partial-unique patterns (one default price list per currency, one published doc version), balanced debit/credit, payment sum <= invoice total, cross-table value comparisons (salvage_value < acquisition_cost).
  - **Topological sort in render.py**: DFS post-order on FK graph. Self-references (department.parent_id → department) handled by skipping self-loops in deps. Circular FK detection emits a warning without crashing.
  - **YAML syntax bug**: 4 columns had no space between key and `{` (`tracking_url_template:{`, `default_useful_life_years:{`, `accumulated_depreciation:{`, `default_retention_days:{`). Found and fixed during YAML parse validation.
  - **HSQLDB type notes**: UUID → VARCHAR(36), TEXT → LONGVARCHAR. Both confirmed valid HSQLDB 2.x syntax.
  - **Oracle ON DELETE RESTRICT**: Oracle does not support explicit RESTRICT keyword; mapped to RESTRICT in dialect yaml with a comment noting it falls back to default behaviour.
  - **G-10 guard parser**: uses frontmatter regex (no full YAML parse of seed body) — reads between first and second `---` lines, extracts `entities:` list items. Handles all 14 seeds correctly.

- Tests added:
  - **G-10 PASS** (L0 guard): 56 catalog entities, 56 seed entity refs, 0 dangling FKs, 0 type violations.
  - **render.py L3 smoke**: `python presets/ddl/render.py --dialect hsqldb` → 1032-line `hsqldb-schema.sql`, exit 0.
  - Full guard suite: G-1~G-10 all PASS or SPEC (no regressions).
  - SPEC: L2 HSQLDB schema+seed load smoke — QA runs this against actual HSQLDB once L2 harness is activated (command: `python presets/ddl/render.py --dialect hsqldb > presets/ddl/build/hsqldb-schema.sql`).

- Catches surfaced: none escalated to CTO.
  - `finance_journal_entry.period_id` has no FK in catalog — accounting period is not a seed entity. Documented in catalog comment; wire validation will resolve at adapter layer. CTO may want to add `accounting_period` as a 57th entity in a future Growth, but this is within scope of current spec.

- Cost: ~25 turns / ~$1.5 추정

#### Growth-10 fix (2026-06-01) — render.py D1/D2/D3 — QA L2 HSQLDB gate BLOCK 해소

QA가 HSQLDB 2.7.4 in-memory live 로드에서 3개 defect 발견 (catalog.yaml 무결 — 47/47 constraint PASS 확인). `render.py` 3곳 수정:

- **D3 (DEFAULT placement)**: `render_column()`에서 NOT NULL 뒤에 DEFAULT를 붙이는 순서 오류. SQL 표준 + HSQLDB 2.x 모두 `TYPE DEFAULT v NOT NULL` 요구. DEFAULT 블록을 NOT NULL 앞으로 이동. 영향: `inventory_item.allow_negative_stock`. 결과: `BOOLEAN DEFAULT FALSE NOT NULL`.
- **D2 (CHECK expr unquoted identifiers)**: explicit CHECK 분기가 catalog expr verbatim 출력 → HSQLDB unquoted lowercase fold → column 못 찾음 (28 CHECKs FAIL). `_quote_check_expr(expr, q)` 헬퍼 추가 + `import re`. bare lowercase 토큰을 dialect quote로 감쌈; SQL 키워드(`IS/NULL/OR/AND/NOT/IN/TRUE/FALSE`) 제외. 결과: `"probability" >= 0 AND "probability" <= 100`, `"end_date" >= "start_date"` 등.
- **D1 (circular back-edge FK inline)**: `hr_department.manager_id → hr_employee` FK를 CREATE TABLE 인라인에 두면 hr_employee 미생성 상태라 FAIL. `topological_order()` 반환형을 `(ordered, deferred_fks)` 으로 변경 — position 배열로 back-edge 감지. `render_table(deferred_fk_cols)` 파라미터로 인라인 skip. `main()`에서 target table emit 직후 `ALTER TABLE ... ADD FOREIGN KEY;` 출력. 일반화됨 (임의 back-edge 처리).
- `tests/ddl/patch_schema.py` — 3개 patch 전부 no-op. 파일 보존 (QA 이력, CTO 결정에 따름).
- `presets/ddl/build/hsqldb-schema.sql` 재생성 완료 (56 tables + ALTER TABLE 1개).
- G-10 PASS / 전체 guard suite PASS / 무 regression.
- Fix cost: ~8 turns / ~$0.3 추정

### Growth-11 (2026-06-01) — 두 번째 backend adapter: fastapi (Python)

- Files touched:
  - `backend/adapters/fastapi/contract_loader.py` (신규 — ContractLoader.java 동형 Python 구현)
  - `backend/adapters/fastapi/wire_response.py` (신규 — WireResponse.java 동형: ok/error builders)
  - `backend/adapters/fastapi/store.py` (신규 — InMemoryEntityStore.java 동형: threading.Lock per bucket)
  - `backend/adapters/fastapi/routers/auth.py` (신규 — auth.login + auth.logout)
  - `backend/adapters/fastapi/routers/entity.py` (신규 — entity 5키 CRUD, paging, filter, sort)
  - `backend/adapters/fastapi/routers/status.py` (신규 — status.health)
  - `backend/adapters/fastapi/main.py` (신규 — FastAPI app 조립, uvicorn entrypoint)
  - `backend/adapters/fastapi/requirements.txt` (신규 — fastapi, uvicorn[standard], pyyaml)
  - `backend/adapters/fastapi/tests/test_smoke.py` (신규 — L1 16 tests PASS)
  - `backend/adapters/fastapi/README.md` (신규 — springboot README 구조 mirror)
  - `docs/learn-logs/engineer.md` (this ledger)

- Stack: **FastAPI + Uvicorn**. Python 3.11+, pyyaml 6.0. No ORM, no DB — in-memory store only (M1).

- ContractLoader Python 구현 방법 (G-1 준수):
  - `_REPO_ROOT = _ADAPTER_DIR.parents[2]` 로 `middle/contract/` 경로 계산 — 하드코딩 없음.
  - `yaml.safe_load()` 로 codes.yaml + wire-v1.yaml 읽기.
  - `http_status_for(code)` / `message_for(code)` / `wire_version()` — Java ContractLoader 동형 API.
  - 모듈 레벨 싱글턴 `contract = ContractLoader()` — `@PostConstruct` 동형.
  - G-1 guard (diagnose.py::g1) 스캔 결과: PASS. 코드→status 재선언 0건.
  - 주의: smoke test 의 `assert http_status == 404` 패턴이 G-1 오탐을 유발함 — codes.yaml 직접 로드 후 loop 비교 방식으로 회피.

- 핵심 준수 포인트 구현:
  - **flat-underscore paging**: `entity.py::list_entities`가 `request.query_params`를 dict로 받아 `paging_mode`, `page`, `size`, `sort_field`, `sort_direction` 언더스코어 키로 직접 접근. `paging.mode` legacy도 fallback 수용 (BUG-2 패턴).
  - **cursor mode → BAD_REQUEST**: `paging_mode == "cursor"` 분기에서 `wire_response.error("BAD_REQUEST")` — codes.yaml에서 http_status 400 조회. springboot 동일 동작.
  - **offset 마지막 페이지 correct count**: `from_idx = min((page-1)*size, total)`, `to_idx = min(from_idx+size, total)` — 7 items, page=3, size=3 → to_idx=7, from_idx=6, len=1. BUG-1 패턴 동일 해소.
  - **idempotent delete**: `store.delete()` 내부 `bucket.pop(id_, None)` — 없는 키 no-op. 항상 True 반환 → 컨트롤러 `{"success": True}` 200 반환. 두 번 DELETE도 두 번 모두 성공.
  - **PATCH semantics**: `store.patch()` — `for k, v in patch_data.items(): if k != "id": updated[k] = v`. 공급된 필드만 교체, 비공급 필드 유지, `id` 보호.
  - **error envelope**: `wire_response.error(code)` → `{"error": {"code": ..., "message": ...}}`. success response에는 `error` 키 없음. details가 있을 때만 `"details"` 키 추가.

- Port 선택: **8081** (springboot-jakarta = 8080; Growth-7 port conflict 경험 반영). `PORT` env var로 재구성 가능.

- Launch command: `uvicorn main:app --port 8081` (adapter 디렉터리에서)

- Tests added:
  - **L1 16 tests PASS** — `test_smoke.py`: store CRUD + PATCH + idempotent delete + offset paging off-by-one + no-overlap + ContractLoader round-trip
  - **G-1 PASS** — diagnose.py G-1 guard: 3 adapter, 26 source file 스캔, violation 0

- QA 공유 suite 실행 방법:
  ```
  # Terminal 1
  cd backend/adapters/fastapi && uvicorn main:app --port 8081
  # Terminal 2
  ADAPTER_BASE_URL=http://localhost:8081 pytest tests/adapters/springboot-jakarta/ -v
  ```

- Catches surfaced: 없음. escalation 없음.
  - FastAPI의 `async def` 라우터에서 `dict[str, Any] | None = None` 파라미터가 body absent 시 None을 주입 — springboot의 `@RequestBody(required=false)` 동형. 정상 동작 확인.
  - `@router.post("/{entity_type}", status_code=201)` 데코레이터 status_code가 `wire_response.ok()` 내부 JSONResponse의 status_code에 의해 override됨 → `JSONResponse(..., status_code=201)` 명시로 해결.

- Cost: ~15 turns / ~$0.8 추정

## §3 — Open Loops (이 인격 책임)

- ~~M1 진입 시 첫 spawn — `middle/contract/` 첫 wire 키 schema 파일 작성~~ ✅ Growth-5d 완료
- ~~`scripts/diagnose.py` G-1 SPEC → PASS 전환~~ ✅ Growth-7 완료 (code→status 재선언 검출)
- adapter `paging.mode` fallback 제거 — flat-underscore 단일 표준 정착 시 (Growth-8 후보)
- ~~frontend vanilla-htmx adapter 구현 (Growth-8) + CDO tokens.md → tokens JSON 생성~~ ✅ Growth-8 완료
- ~~DDL axis: catalog.yaml 56 entities + dialects + render.py + G-10~~ ✅ Growth-10 완료
- `scripts/diagnose.py` G-2 SPEC → 활성 전환 시 함수 본문 보강 (profile path extractor)
- CTO escalation 4건 응답 대기 (Growth-5d Decision Log 참조)
- L2 HSQLDB schema+seed smoke harness 활성화 — QA 주도 (command: `python presets/ddl/render.py --dialect hsqldb > presets/ddl/build/hsqldb-schema.sql`)
- wire `entity.create` → catalog 검증 wiring — 후속 Growth (Growth-10 scope 외)
- ~~fastapi backend adapter (Growth-11)~~ ✅ 완료 — QA 공유 suite pass 대기 중
- fastapi adapter: cursor paging 구현 — Growth-N (BAD_REQUEST 현재 동작, springboot 동일)
