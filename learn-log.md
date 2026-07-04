# learn-log.md — compounding-stack-harness

> 복리식 축적의 활동 원장. 모든 Growth 가 어느 축에 살을 붙였고, 어느 milestone 에 기여했는지 1줄 기록.
>
> **Growth-4 이후 (2026-05-29~)**: §6 는 Growth 당 1줄 + 인격 ledger pointer 만. 상세는 각 인격의 `docs/learn-logs/<role>.md` 에 기록. 인격 ledger 목록: [CTO](docs/learn-logs/cto.md) · [Engineer](docs/learn-logs/engineer.md) · [QA](docs/learn-logs/qa.md) · [CMO](docs/learn-logs/cmo.md) · [CDO](docs/learn-logs/cdo.md).
>
> **Growth-1~3 (historical)**: 단일-CTO 시대 verbose 포맷 그대로 보존 (retroactive 분리 안 함).

## §0 — Axis Ownership Card (7축)

| 축 | owner 디렉터리 | 검증 게이트 | 현재 자산 |
|---|---|---|---|
| skill | `presets/skills/` | seed.md schema check | (M1 채움 예정) |
| ddl | `presets/ddl/` | dialect smoke (HSQLDB/PG) | (M1 채움 예정) |
| middle | `middle/contract/` | contract round-trip test | (M1 채움 예정) |
| frontend | `frontend/adapters/` | adapter compliance test | (M1 채움 예정) |
| backend | `backend/adapters/` | adapter compliance test | (M1 채움 예정) |
| creater | `.claude/commands/` + `scripts/workflow/` | diagnose.py guards | (M0 — 골격만) |
| customer | `profiles/` | profile v1 schema validation | (M0 — schema 만) |
| expert-agent | `.claude/agents/domain-expert-*` | INDEX.md 권위 참조 check | (M0 — generic 만) |

## §1 — Verification Matrix

| Layer | Status | Last Run |
|---|---|---|
| L1 pytest | NOT_SETUP | — |
| L2 JDBC | PASS | 2026-06-11 (full catalog 60 entities, HSQLDB 48/48, raw load 무패치) |
| L3 build | NOT_SETUP | — |
| L4 live | PASS | 2026-06-11 (lawfirm-demo, 손해배상·자백·위약금 5종) |
| 보안 리뷰 (CISO) | PASS | 2026-06-11 (lawfirm-demo 인도물, A5 외부유출 0 + CAVEAT 3건 해소) |

## §2 — Trap Catalog (재번호)

이전 repo 의 18 trap guards 는 [`docs/inherited-wisdom/`](docs/inherited-wisdom/) 에 7 메타 교훈으로 정리됨. 이 repo 의 G-1 ~ G-7 은 그 7 lesson 1:1 매핑. G-8 부터는 이 repo 고유 컨벤션.

가드 runner: [`scripts/diagnose.py`](scripts/diagnose.py) — `python scripts/diagnose.py` 로 전부, `... G-1,G-7` 로 부분 실행, `--list` 로 카탈로그.

| ID | 신호 | 출처 | 가드 위치 |
|---|---|---|---|
| **G-1** | wire-protocol 키가 middle/contract 밖에서 재선언됨 | Lesson 1 | `scripts/diagnose.py::g1_wire_protocol_single_source` (PASS, Growth-7 활성 — codes.yaml code→http_status 재선언 정적 검출, springboot-jakarta adapter green) |
| **G-2** | 컨텍스트 경로 문자열이 declaring file 외에 hardcode | Lesson 2 | `scripts/diagnose.py::g2_context_path_consistency` (SPEC, 첫 profile 후 활성) |
| **G-3** | 새 진입점이 CLI 함수 호출 / subprocess 대신 재구현 | Lesson 3 | `scripts/diagnose.py::g3_single_source_delegation` (SPEC, 첫 새 entrypoint 후 활성) |
| **G-4** | profile YAML 의 `${ENV_VAR}` 가 round-trip 시 손실 | Lesson 4 | `scripts/diagnose.py::g4_envvar_round_trip` (PASS, Growth-5d acme-erp.yaml 후 활성) |
| **G-5** | 축이 2개 이상 자산을 가졌는데 manifest (INDEX/_README) 없음 | Lesson 5 | `scripts/diagnose.py::g5_asset_exposure_harness` (PASS, Growth-7 middle+skill manifest — glob `**/*.seed.md` 강화) |
| **G-6** | 다테넌트/SaaS 힌트가 M5 게이트 전에 코드 진입 | Lesson 6 | `scripts/diagnose.py::g6_self_host_single_mode` (PASS, `.m5-saas-gate-open` 로 해제) |
| **G-7** | 매출 로드맵 milestone 에 페르소나·시간 표현 누락 | Lesson 7 | `scripts/diagnose.py::g7_persona_driven_gating` (PASS 2026-05-29 Growth-3: positioning.md → roadmap 페르소나 인수 라인으로 해소) |
| **G-8** | 파일/디렉터리명에 비-ASCII 또는 unsafe 문자 | CLAUDE.md §10 | `scripts/diagnose.py::g8_ascii_slug` (PASS, Growth-60 — Apple `@Nx` 레티나 에셋은 `*.xcassets` 번들 안에서만 면제 `_APPLE_ASSET_NAME`; 그 밖의 `@`·비-ASCII 는 여전히 검출) |
| **G-9** | main §6 슬림 엔트리가 본문 10행 초과 또는 슬림 §6 200행 초과 | Growth-4 charter | `scripts/diagnose.py::g9_main_log_slim` (PASS, Growth-5a 박힘) |
| **G-10** | ddl catalog 무결성 — seed entity ⊄ catalog / dangling FK / 비-closed-set 타입 | Growth-10 | `scripts/diagnose.py::g10_ddl_catalog_integrity` (PASS, Growth-10 — 56 entity, seed⊆catalog, dangling FK 0, type closed-set) |
| **G-11** | creater orchestrator(`scripts/workflow/*.py`)가 catalog 파싱을 render.py 위임 없이 재선언 | Growth-14 | `scripts/diagnose.py::g11_creater_catalog_single_source` (PASS, Growth-14 — scaffold.py+manifest.py 모두 `load_catalog` import 경유, 로컬 재선언 0) |
| **G-12** | catalog 의 `*_id` 컬럼(PK 제외)이 `fk:` 블록도 `fk-exempt:` 마커도 없음 (silent dangling) | Growth-15 | `scripts/diagnose.py::g12_catalog_fk_hygiene` (PASS, Growth-15 — 79 *_id 스캔. polymorphic/circular 6 + backlog 2 는 fk-exempt 마커, customer_id 는 fk 연결) |
| **G-13** | 인격 loop SKILL(`*-loop/SKILL.md`)이 subagent-output-protocol.md 링크 없음 (반환 경계 드리프트) | Growth-34 | `scripts/diagnose.py::g13_subagent_output_protocol_wired` (PASS, Growth-34 — Growth-33 규약 hardening. 7 loop 스캔, 헤딩 문구 무관·프로토콜 링크 존재만 검사. envelope 크기는 런타임 속성이라 정적 검사 불가, 규약 wiring 만 가드) |
| **G-14** | intake 파이프라인: qualify 케이스가 SLA 초과 stall 이거나 node FAIL 상태 | Phase-8 monitor (CLAUDE.md §10) | `scripts/diagnose.py::g14_intake_pipeline_health` (SPEC — infra/registry/cases/ 첫 케이스 도착 시 활성) |
| **G-15** | marketing-site 케이스가 vision-QA 미통과(verdict≠PASS) 상태로 DELIVERED | Growth-65 | `scripts/diagnose.py::g15_marketing_site_visual_gate` (SPEC — infra/registry/cases/ 에 deliverable_kind=marketing-site 첫 케이스 도착 시 활성. ui_check `--full-vision` → CDO/QA zai-mcp 채점 → verdict PASS 필수) |
| **G-16** | claude.ai/design 업로드 스코프 위반 — staging/design-sync 컴포넌트에 PII(email/RRN/전화)·시크릿키(AWS/Anthropic/Google)·금지경로(apps/intake/data·infra/secrets) 참조 | Growth-130 | `scripts/diagnose.py::g16_design_upload_scope` (SPEC — staging/design-sync 첫 컴포넌트 sync 시 활성. 무명 컴포넌트만 클라우드 업로드 = BAA제외·학습기본 정책) |
| **G-17** | 인도물(복제본·landing-astro src·테마)에 클라우드 결합 흔적 — claude.ai/DesignSync/design-sync 토큰(대소문자 무관) | Growth-130 | `scripts/diagnose.py::g17_cloud_coupling_leak` (PASS — clean repo 30파일 0결합. vendor lock-in 차단) |
| **G-18** | 고객 복제본 번들에 타 테넌트 slug 누출 — out/replicas/<slug> 안에서 다른 고객 slug 토큰경계 매칭 | Growth-130 | `scripts/diagnose.py::g18_cross_tenant_leak` (SPEC — out/replicas/ 복제본 빌드(WP-3) 도착 시 활성) |
| **G-19** | 경계 토큰 override 가 DTCG semantic 화이트리스트 위반 — staging *.tokens.json 키 ⊄ design/tokens/semantic.json(+landing extras) | Growth-130 | `scripts/diagnose.py::g19_dtcg_schema` (SPEC — *.tokens.json sync 시 활성, scripts/design/dtcg_schema.py 연동. DTCG=W3C CG draft, Rec 아님) |
| **G-20** | synced 컴포넌트 raw HTML 의 production 직붙임 — frontend/presets 경로에 'design-sync:staging' provenance 마커 | Growth-130 | `scripts/diagnose.py::g20_normalization_gate` (PASS — clean repo 125파일 0마커. 정규화 게이트 우회=axis-8 붕괴 차단) |
| **G-21** | Shell 컴포넌트 conformance 위반 — 격리 sibling(harness-design-system) `components/*/index.html` 텍스트노드/aria-label·placeholder·title·alt 가 `{{슬롯}}` 마커도 `_structural-allowlist.txt`(UI chrome 닫힌집합)도 아닌 Hangul/단어 텍스트(=도메인 잔존) | Growth-130 v2 | `scripts/diagnose.py::g21_shell_conformance` (**PASS** — 5 셸 0위반, chrome 12종. stdlib HTMLParser, demo-heading/demo-desc/svg/script/style 스킵. **allowlist=fail-safe**(누락 시 BLOCK) → denylist(FORBIDDEN_PATTERNS, 2차)가 못 잡는 미래 도메인 용어 누출(Growth-130 사고 클래스) 원천 차단. SPEC if sibling repo absent) |
| **G-22** | ledger/아카이브 파일 비대 — `learn-log.md`·`docs/learn-logs/**/*.md`(생성물 `_index*` 제외) 가 90KB 초과 = 100KB Read-skip 한도 접근(원장이 자기 도구로 안 읽히는 상태) | Growth-144 | `scripts/diagnose.py::g22_ledger_size_cap` (**PASS** — 17파일 검사. 해소법 = 2단계 아카이브 규약 `docs/learn-logs/README.md`: live 64KB 회전 / 볼륨 80KB 닫기) |
| **G-87** | legal-rag embed 호출이 비대칭 e5 prefix 불변식 위반 — api.py 가 `.embed_batch(` 호출하거나 ingest.py 가 bare `.embed(` 호출 | Growth-93 | `scripts/diagnose.py::g87_embed_caller_split` (**SPEC** — 첫 production ingest 로 유효성 확인 전까지 SPEC. 현재 clean state 에서 PASS 확인. SKIP if services/legal-rag/ absent) |

상태 코드: **PASS** 통과 / **FAIL** 위반 검출 / **SKIP** 검사 대상 부재 (이 시점) / **SPEC** 검출 로직 다음 milestone 에 박힘.

## §3 — Reserved

## §4 — Trap Counter

| 시점 | 활성 가드 수 | 비고 |
|---|---|---|
| 2026-05-29 (M0 founding) | 0 | 이전 repo 18개와 무관 |
| 2026-05-29 (Growth-2 G-1~G-8 박기) | 8 | G-1~G-3 SPEC / G-4 SKIP / G-5 SKIP / G-6 PASS / G-7 **FAIL** (M0~M5 페르소나 누락 6건) / G-8 PASS |
| 2026-05-29 (Growth-3 G-7 해소) | 8 | G-1~G-3 SPEC / G-4~G-6 SKIP / **G-7 PASS** (M0~M5 6 milestone 페르소나+시간 박힘) / G-8 PASS |
| 2026-05-29 (Growth-5a G-9 박음) | 9 | + **G-9 PASS** (Growth-4 슬림 엔트리 9 non-blank lines, cap 10) — 인격 분리 후 main 비대 가드 |
| 2026-05-29 (Growth-7 G-1 활성) | 9 | **G-1 SPEC→PASS** (adapter contract 재선언 검출, springboot-jakarta 1 adapter green) / G-4·G-5 SKIP→PASS 카탈로그 동기화 (실 상태 반영) / G-2·G-3 만 SPEC 잔존 |
| 2026-06-01 (Growth-8 frontend adapter) | 9 | 가드 추가 0 — 전 9개 green 유지. **G-1 이 2 adapter (backend+frontend) 스캔, 둘 다 PASS** (frontend contract_loader.py 가 contract 재선언 0). G-5 design 축은 tokens/README.md manifest 로 통과 |
| 2026-06-01 (Growth-10 ddl catalog) | 10 | **G-10 신설 PASS** (ddl catalog 무결성 — 56 entity seed⊆catalog, dangling FK 0, type closed-set). QA L2 첫 가동이 라이브 HSQLDB 로 render.py 3 결함 BLOCK→fix (catalog 건전, renderer 버그) |
| 2026-06-01 (Growth-11 fastapi adapter) | 10 | 가드 추가 0. **G-5 FAIL→PASS** (backend 축 2 adapter 도달 → `backend/adapters/INDEX.md` manifest 추가, fastapi 가 트리거). G-1 이 3 adapter 26 파일 스캔 PASS |
| 2026-06-01 (Growth-12 검증 wiring) | 10 | 가드 추가 0. **G-1 FAIL→PASS** (fastapi 검증기가 422/409 하드코딩 → codes.yaml loader 경유로 수정, springboot 패리티 복원). **G-6·G-8 build/ 스코프 정정** (생성 `build/` 의 catalog copy·.class 오탐 → G-1 과 동일 제외셋 적용, 소스 무영향) |
| 2026-06-01 (Growth-14 end-to-end demo) | 11 | **G-11 신설 PASS** (creater catalog single-source — workflow 스크립트 load_catalog 재선언 금지, fails-closed 임시 위반파일로 증명). Growth-13 이 G-11 후보로 적어둔 ledger-index `--check` 는 미구현 상태였으므로 **G-12 후보로 재배치** (가드 번호는 구현 시점 확정). 전 11개 0 real FAIL (G-2/G-3 SPEC 잔존) |
| 2026-06-01 (Growth-15 FK 무결성) | 12 | **G-12 신설 PASS** (catalog FK hygiene — `*_id` 는 fk OR fk-exempt 마커, fails-closed 증명). catalog 10 dangling 분류(polymorphic/circular 7·backlog 2·customer_id→contact fk). runtime FK 검증 양 backend (DIM-6) — fastapi live 37 green, **springboot 코드 패리티 QA 확인·live 미실행(JDK 환경 부재, M1 sign-off 전 필수)**. ledger-index `--check` 는 **G-13 후보**로 밀림 (→ Growth-34 에서 G-13 을 output-protocol 가드가 선점, `--check` 는 **G-14 후보**로 재배치 — 가드 번호는 구현 시점 확정). 전 12개 0 real FAIL |
| 2026-06-02 (Growth-16 react adapter) | 12 | 가드 추가 0 — 전 12개 green 유지. **G-1 이 4 adapter (springboot/fastapi/vanilla-htmx/react) 47 파일 스캔 PASS** (react 가 contract 를 빌드타임 codegen 으로만 소비, 하드코딩 0). **G-5**: `frontend/adapters/INDEX.md` 추가 (frontend 축 2 adapter 도달 트리거). react L1 30 / L3 build / L4 35 (fastapi 상대) green |
| 2026-06-02 (Java-env sign-off 검증) | 12 | 가드·코드 변경 0 (순수 검증). JDK21+gradlew 로 **Growth-15·16 Java carry 종결**: springboot gradlew test 30(CatalogValidatorTest 22 incl FK 7) + **DIM-1~6 live 37 PASS** + react↔springboot L4 36 PASS(2 skip=Vite preview, M2 전 활성). M1 Java sign-off 게이트 PASS. 상세 [qa.md 검증 체크포인트](docs/learn-logs/qa.md) |
| 2026-06-02 (Growth-17 G-7 정밀화) | 12 | 가드 추가 0. **G-7 FAIL→PASS** (잠복 FAIL 발견·해소): Task #2 가 추가한 "## M1 Maturity Threshold" prose 섹션을 G-7 이 milestone 인수 블록으로 오분류 (heading 이 `M1` 로 시작) → persona+time 룰 적용해 FAIL 이었으나 diagnose 미재실행으로 미발각. **fix**: milestone 필터를 `M\d+\s+—` (숫자 직후 em-dash) 로 좁혀 M0~M5 만, threshold 정의 섹션 제외 — 가드 약화 아닌 오분류 교정. 부수: ops-pack M1→M2 이관 시 빠진 M1 인수 time token 을 "30분 안에" 로 복원(내용 해소). 12개 0 real FAIL 복귀 |
| 2026-06-02 (데모 촬영 prep — vanilla-htmx 버그) | 12 | 가드 추가 0, 가드 0 real FAIL 유지. **실 버그 fix** (engineer, 데모 prep 중 발견): vanilla-htmx `entity_list` 가 `entity_type` 을 백엔드 쿼리에 주입 → 백엔드가 레코드 필터로 처리해 **모든 목록 화면 0행**(빈 상태) 렌더 + paging 키(`paging_page/size`) contract 불일치(`page/size/cursor`). Scene 3A 촬영 차단 결함. **L4 가시성 공백**: 공유 compliance 가 백엔드 API 직접 호출, Flask 목록 라우트 미경유로 미발각. fix 후 employee/asset/maintenance 목록이 시드 실렌더, fe unit 44 + L4 fastapi 37 PASS. **QA 후속 RESOLVED**: `test_entity_list_params.py` 추가(12 케이스 — Flask 라우트 통과해 outbound params 캡처, contract 키만/forbidden 키 무유출 핀). revert→RED 진위 확인. fe 56 green. L4 가시성 공백을 라우트-경계 테스트로 봉합 |
| 2026-06-11 (Growth-34 dogfood — output protocol 가드) | 13 | **G-13 신설 PASS** (subagent output protocol wired — 7 loop SKILL 이 subagent-output-protocol.md 링크 보유, 헤딩 문구 무관). 계기: Growth-33 규약을 같은 실패 모드(security-agent)로 **dogfood 측정** — 인프라 보안리뷰 재실행 시 본문 193줄/8KB → `out/analysis/` 파일, subagent 내부 58.6k 토큰 격리, main 반환은 envelope ~10줄(판정+경로+CAVEAT 2). Growth-32 의 ~64k main 유입 대비 변동비 차단 증명. envelope 크기는 런타임 속성이라 정적 가드 불가 → **규약 wiring 드리프트**를 G-13 으로 가드. ledger-index `--check` 후보는 G-14 로 재배치. 전 13개 0 real FAIL (G-2/G-3 SPEC 잔존) |
| 2026-06-14 (자율 intake 파이프라인 — Phase 7 문서화) | 14 | + **G-14 SPEC** — 자율 intake 파이프라인 건전성 가드 (qualify stall/fail 검출). `scripts/diagnose.py::g14_intake_pipeline_health` (infra/registry/cases/ 첫 케이스 도착 시 활성, 현재 SPEC). |
| 2026-06-15 (marketing-site track Phase 4 — vision-QA 게이트) | 15 | + **G-15 SPEC** — marketing-site 케이스 vision-QA 필수 게이트 (deliverable_kind=marketing-site AND triage_status=delivered → verdict PASS 없으면 FAIL). `scripts/diagnose.py::g15_marketing_site_visual_gate` (첫 marketing-site 케이스 도착 전 SPEC). `ui_check.py --full-vision` 비전 리뷰 request 생성 구현 (LLM 0). `design/vision-qa-rubric.yaml` 8기준 루브릭 신설. |
| 2026-06-19 (Growth-93 — G-87 embed caller split 가드) | 16 | + **G-87 SPEC** — legal-rag 비대칭 e5 prefix 불변식 기계 가드 (api.py: .embed_batch 금지 / ingest.py: bare .embed 금지). `scripts/diagnose.py::g87_embed_caller_split` (현재 clean state PASS, 첫 production ingest 후 SPEC→PASS 확정). |
| 2026-06-26 (Growth-130 — Design-Cloud Bridge WP-1+WP-2) | 21 | + **G-16~G-20 (5종 신설)** — claude.ai/design 클라우드 경계 안전망. G-16 업로드스코프(PII/시크릿 차단, SPEC)·G-17 클라우드결합누출(인도물 0결합, PASS)·G-18 교차테넌트누출(복제본 slug격리, SPEC)·G-19 DTCG스키마(토큰 화이트리스트, SPEC)·G-20 정규화게이트(직붙임 차단, PASS). worktree(design/cloud-bridge)→master 머지. QA WP-2 게이트 MERGE-OK, 단위테스트 24종 PASS. clean repo G-17/G-20 PASS·나머지 SPEC(타깃 미착지). 설계 docs/architecture/design-cloud-bridge-execution-plan.md. |
| 2026-06-26 (Growth-130 — Design-Cloud Bridge WP-3) | 21 | 가드 추가 0. **build_replica.py 신설** (scripts/design/) — 고객 복제본 빌드타임 물리격리 + 누출 3종 게이트(G-17/G-18/PII 재사용, 재구현 0). **G-18 SPEC→PASS 활성** (hopwell/harvest 실증 109파일 번들, 누출 0). open-closed(scaffold.py·landing-astro npm build 호출만). Style Dictionary v5+ 평가=현행 build-tokens.mjs 유지(동치·의존성0, cost-aware). QA WP-3 게이트 MERGE-OK, 단위테스트 30 passed. |
| 2026-06-26 (Growth-130 — Design-Cloud Bridge WP-4 파일럿) | 21 | 가드 추가 0. **claude.ai/design A/B 파일럿 측정 종결** — pricing 섹션 1건 cloud craft vs repo 코드 baseline. ① 제작 cloud 2~3분 1-shot vs baseline ~25분(blind 3 cycle), ② export 충실도 HIGH(Props/variant/DEC-3/data-loop 보존·기존 semantic 토큰명 소비·a11y 무료), ③ normalize 부담 LOW(cloud self-normalize→normalize.py 스켈레톤 redundant), ④ 라이브 픽셀검증 양 arm 4통증 전부 PASS(headless Chrome, cloud 미세 우위 lift/divider). 판정=**재사용 섹션 craft 한정 도입 + repo 시각검증 훅 완화(레버2), 전체 UI layer 이전 ✗**. 토큰: cloud 신규 shadow 2종=theme.yaml 후보(인라인 fallback 렌더, semantic 직등록 ✗). design-loop SKILL '클라우드 craft 브리지' 절차 박제. production 무손상(staging만). net-new 섹션 미검증=후속 caveat. |
| 2026-06-26 (Growth-131 — legal-rag 데모 craft) | 21 | 가드 추가 0. **legal-rag /app 검색 데모 UI craft** (경로A 로컬, 클라우드/외부 0). 라이브 headless 진단(이준호 partner 5화면)→5수정: ①excerpt 아티팩트 제거(seed 데모문서 ====구분선·ingest메타 정제 + app.js sanitizeExcerpt 렌더타임 이중방어, 카운트·하이라이트 cleanExcerpt 정합) ②0-매치 단어뱃지 숨김(matched==0 미생성, '0/N=실패' 오독 차단) ③빈 검색화면 예시질의 칩 4개(CDO pill craft, 죽은화면→권유형) ④검색창↔버튼 그룹핑(align-self:stretch) ⑤search-input spellcheck=false(한글 법률어 물결선 제거). **로컬 fetch-stub headless 렌더 검증 PASS**(verify_local.mjs — /auth·/search stub으로 SPA 로직변경을 재배포 전 픽셀증명, htmx-demo-verify를 legal-rag SPA로 확장). 6커밋 per-file 푸시(4d83d22..23192d9). **founder 게이트: app Redeploy + 데모 재인제스트**(픽스처 정제는 재인제스트로만 라이브 청크 반영, render sanitize는 Redeploy만으로 표시 정제). |

| 2026-06-27 (Growth-130 — Design-Cloud Bridge v2 WP-A~C) | 22 | **G-21 신설 PASS** (shell conformance) — 구조적 분리 v2 핵심 게이트. 진단: 디자인 sibling 셸이 도메인 텍스트를 inline 하드코딩(business-system 경로는 wire-contract(라벨0)+screen-manifest로 이미 분리 달성, 디자인 레이어만 퇴행) → 누출 방지가 절차적(스크럽+denylist)일 수밖에 없던 근본원인. WP-A/B: 5 셸을 `{{슬롯}}` 템플릿+중립 corpus(`fixtures/synthetic.json`)로 리팩터(잔존 legal 어휘 계약해지/위약금/임대차/면책/불법행위/과실 완전 제거 — 이전 스크럽이 못 잡은 denylist 누락분). WP-C: G-21=allowlist conformance(텍스트=마커|chrome), **denylist→allowlist 패러다임 전환**(fail-safe, 미래 도메인 용어 누락 누출 원천 차단). 적대적 검증: dirty 스니펫(상속재산/판결문/진료기록=현 denylist 부재 용어) 2위반 검출, clean/scaffolding/chrome 오탐 0. sibling 16커밋, main G-21+import 1커밋. v1 산출물(G-16~20) 전부 유지. |
| 2026-07-05 (Growth-144 — ledger 2단계 아카이브) | 23 | **G-22 신설 PASS** (ledger size cap 90KB, 17파일) — growth-archive.md 가 265KB(100KB Read-skip 한도 2.6배)로 비대해 원장이 자기 도구로 안 읽히는 상태를 적발한 부류의 재발 방지. 적용: growth-archive 볼륨 4개(01~04, 각 ≤80KB) 분할+인덱스 전환, engineer.md 79KB→22KB (Growth-5d~70 → archive/engineer-01.md). 규약 = docs/learn-logs/README.md (live 64KB 회전 / 볼륨 80KB 닫기 / 90KB 가드) |

## §5 — Environment Notes

- 2026-05-29: founding. Sibling repo `business-fullstack-creater` 에서 메타 자산만 승계. Nexacro/uiadapter 의존 0.
- 결정 사항 (CTO): Frontend / Backend 는 pluggable, Middle 만 stable. customer profile `stack.frontend` / `stack.backend` 키로 교체.
- 결정 사항 (Founder + CTO): 첫 vertical 은 시장 데이터로 결정 (M2 첫 고객 산업 → M3 vertical 진입).
- 결정 사항 (Founder, 2026-06-02): **1차 타겟 ICP = "IT 솔루션 도입 불가 규모의 소형 업체·스타트업"** (대략 1~30명, 전산팀 없음, 산업 무관·상한 가변). "시작은 작게" — 중·대형은 의도적 제외, M3 후 확장. positioning.md §1/§2/§3 narrowing 반영. demo `smallmfg-demo`(50명)는 시청자 노출 수치 아님(정렬 OK). 단일 기준 = positioning.md + memory `project_icp`.

## §6 — Growth History

### Growth-1 (2026-05-29) — Founding constitution + 4-인격 팀 구성

- **Axis touched**: creater (orchestration 골격), expert-agent (generic 인스턴스), customer (schema), business docs, partnership (CEO+CTO+CMO+CDO 4-인격)
- **Milestone**: M0
- **Revenue contribution**: infra only (매출 발생 전 founding 단계)
- **Cost impact**: none (LLM 호출 발생 전)
- **변경 표면**:
  - 헌장: `CLAUDE.md`, `AGENTS.md`, `README.md`, `learn-log.md`
  - 아키텍처: `docs/architecture/swappable-layers.md`
  - 비즈니스: `docs/business/{revenue-roadmap,cost-monitoring,partnership-charter}.md`
  - 유산: `docs/inherited-wisdom/README.md`
  - Agent 정의: `.claude/agents/{domain-expert-generic,marketing-agent,design-agent}.md`
  - Customer: `profiles/_README.md`
  - 기타: `.gitignore`
- **Why**:
  - 이전 repo `business-fullstack-creater` 의 79 Growth 경험을 7 메타 교훈으로 추출
  - Nexacro/uiadapter 강결합을 폐기, Frontend/Backend pluggable + middle contract single-source 로 재정렬
  - axis-7 expert-agent 도입 (도메인 전문가 인간 영입 없이 시작)
  - 사용자 추가 요청 (mid-flight): marketing-agent (CMO) + design-agent (CDO) 인격 추가 — 우리에게도 사용자에게도 없는 직무 결손을 AI 인격으로 메움
  - 비용 모니터링 + 매출 로드맵을 헌장 단계부터 박음 (사후 추가는 항상 비싸다)
- **Next**:
  - M0 잔여: marketing/positioning.md 초안 (CMO), design/tokens 초안 (CDO), 7 lesson → G-1~G-7 가드 박기 (CTO)
  - M1 진입: 14 공통 도메인 baseline preset, middle contract v1, springboot-jakarta + vanilla-htmx adapter, generic expert-agent demo
- **Decision log (양자 합의 항목)**:
  - 4-인격 팀 구성 — CEO+CTO 합의 (2026-05-29)
  - 첫 vertical 결정 방식: 사전 선택 금지, M2 첫 paid customer 산업으로 결정 — CEO+CTO+CMO 합의 (charter §게이트)

### Growth-2 (2026-05-29) — 7 lesson → G-1~G-7 + G-8 ASCII slug 가드 박힘

- **Axis touched**: creater (diagnose runner 골격), inherited-wisdom 7 lesson 이 검출 코드로 환생
- **Milestone**: M0 마무리 (CTO 단독 작업)
- **Revenue contribution**: infra only — 가드는 매출 보호 자산 (drift = 무상 cost)
- **Cost impact**: none (LLM 호출 0, infra 의존 0, pure Python stdlib)
- **변경 표면**:
  - 신규: [`scripts/diagnose.py`](scripts/diagnose.py) — 8 guard 함수 + CLI (전체/부분/`--list`/`--json`)
  - 갱신: [`learn-log.md §2`](learn-log.md) Trap Catalog 8행, §4 Trap Counter 8개 활성 row
  - 갱신: [`CLAUDE.md §10`](CLAUDE.md) 컨벤션 — G-1/G-2 임시번호 폐기, §2 카탈로그 single source 로
- **Why**:
  - Growth-1 Next 의 "7 lesson → G-1~G-7 가드 박기" 이행
  - 번호 충돌 해소 (CLAUDE.md §10 의 임시 G-1/G-2 가 inherited-wisdom 의 lesson 매핑과 일관성 안 맞음) — lesson 1:1 매핑 우선, ASCII slug 는 G-8 로 이동
  - 가드를 M1 진입 *전* 박는 것의 효용: M1 구현 중 같은 함정에 다시 안 빠짐 (이전 repo 79 Growth 가 retroactive 가드로 흘린 비용 회피)
  - G-1~G-3, G-6 의 검출 대상이 아직 없으므로 SPEC/SKIP — 가드 정의는 박혔고 활성화는 해당 axis 첫 자산 도착 시
- **Catch (가드가 박히자마자 일한 사례)**:
  - **G-7 FAIL** — `docs/business/revenue-roadmap.md` M0~M5 6개 milestone 블록 모두 페르소나(CEO/업무담당자/IT-담당자) + 시간 표현이 빠짐. Lesson 7 ("페르소나-driven gating") 의 정면 위반. → Task #6 으로 분리 (CMO 영역, marketing/positioning.md 가 페르소나를 정의한 *후* roadmap 에 박는 게 의존 순서).
- **Next**:
  - Growth-3 후보 (CMO): `docs/marketing/positioning.md` 초안 + 그 페르소나를 roadmap M0~M5 에 박아 G-7 해소
  - Growth-4 후보 (CDO): `docs/design/tokens.md` 초안
  - M1 진입: G-1/G-2 가 SPEC 에서 활성으로 전환되도록 `middle/contract/` 첫 키 + 첫 customer profile 작성
- **Decision log**:
  - G-1~G-7 = inherited-wisdom 7 lesson 1:1 매핑, G-8 = CLAUDE.md §10 ASCII slug — CTO 단독 결정 (CEO 사전 승인 "그대로 진행해" 2026-05-29)
  - G-7 위반은 즉시 silence 하지 않고 FAIL 상태 유지 — "가드가 발견한 진짜 issue 를 0으로 만들기 위해 가드를 약화시키지 않는다" 의 첫 적용 사례

### Growth-3 (2026-05-29) — CMO 첫 배치 + roadmap 페르소나 인수 (G-7 해소)

- **Axis touched**: marketing (CMO 첫 산출물 `docs/marketing/positioning.md`), business (revenue-roadmap M0~M5 페르소나 인수 라인 박힘), creater (diagnose.py `_TIME_PAT` 한국어 표현 보강)
- **Milestone**: M0 마무리 (CMO 첫 가동 + G-7 PASS 전환)
- **Revenue contribution**: infra only — 페르소나 정의가 M1~M5 매출 시점의 "누가 무엇을 어느 시간 안에 한다" 인수 조건이 됨 (사후 정의는 항상 비싸다)
- **Cost impact**: none (CMO 1 subagent 호출 1회 — Sonnet 4.6, infra 의존 0)
- **변경 표면**:
  - 신규: [`docs/marketing/positioning.md`](docs/marketing/positioning.md) — 1줄 약속 + 3 페르소나 카드 (CEO/업무담당자/IT-담당자) + 3대 차별화 페르소나별 번역 + M0~M5 페르소나-시간 triple + CEO 회수 질문 4
  - 갱신: [`docs/business/revenue-roadmap.md`](docs/business/revenue-roadmap.md) — M0~M5 각 milestone 에 "페르소나 인수" 라인 박힘 (CMO 산출물의 triple 을 roadmap 게이트로 직접 인용)
  - 갱신: [`scripts/diagnose.py`](scripts/diagnose.py) — `_TIME_PAT` 한국어 시간 표현 보강 ("주일"/"개월"/"년" 추가, 긴 토큰 우선 alternation 으로 "1주일" 같은 표현 정확히 매칭)
  - 갱신: §2 G-7 row FAIL→PASS, §4 Growth-3 row 추가
- **Why**:
  - Task #6 (Growth-2 의 G-7 FAIL 후속) 의 의존 순서 처리: 페르소나가 먼저 *비즈니스 정의* 로 박혀야 roadmap 의 페르소나 인수 라인이 라벨이 아닌 *측정 가능한 게이트* 가 된다
  - CMO 가 4-인격 팀 모델에서 처음 실제로 가동 — Growth-1 에서 CMO 인격을 추가만 해두고 가동은 안 했었음, 이번이 첫 실전 배치
  - G-7 의 regex 가 한국어 word boundary 한계로 "1주일" 을 놓침 (greedy "주" 매칭 + Korean char 사이 `\b` 미동작) — 진짜 issue 였으므로 regex 를 약화시키지 않고 길이 우선 alternation 으로 정밀화
- **Catch**:
  - CMO 가 M2 "당일 화면 초안" 약속이 M1 의 generic preset + middle contract 파이프라인 없이는 못 지킨다고 경고 → M1 작업 시 "domain-expert agent 인터뷰 → preset 큐레이션 → 화면 초안" 의 end-to-end 자동화가 게이트
  - CMO 의 4 회수 질문 (가격대 확정, 첫 vertical 시그널, OSS/상용 분리선 합의 시점, M3 vertical landing page 책임자) 은 CEO 결정 대기 — Growth-4 이후 풀릴 항목
- **Next**:
  - Growth-4 후보 (CDO): `docs/design/tokens.md` 초안 — 3 페르소나별 UI 톤·접근성·페르소나 디스플레이 토큰 매핑
  - Growth-5 후보 (CEO): CMO 회수 질문 4건 결정
  - M1 진입: `middle/contract/` 첫 wire 키 + 첫 customer profile 작성 (G-1/G-2 SPEC→활성 전환)
- **Decision log**:
  - Task #6 실행 순서: positioning.md (CMO) → roadmap 패치 (CTO) → G-7 PASS — CEO 추천안 승인 (2026-05-29 "추천안으로 하자")
  - G-7 regex 약화 금지 + 한국어 표현 정밀화 — CTO 단독 결정 ("guards-must-work" 원칙의 두 번째 적용)

---

**Growth-4 부터 1줄 + pointer 포맷** (G-9 가드: 본문 비-blank ≤10행/엔트리, 슬림 §6 전체 ≤200행):

```
### Growth-N (YYYY-MM-DD) — <한 줄 제목>
- **인격**: <주도 인격> (+ 합의 인격)
- **Axis touched**: <축 / 헌장 / 인격 변경 중>
- **Milestone**: <M0~M5 중>
- **Revenue/cost**: <매출 영향> / <세션 비용 추정 — 모델·turns>
- **Why (1줄)**: <왜 이 Growth 가 발생했는가>
- **상세**: [<role>.md#Growth-N](docs/learn-logs/<role>.md)  ← 인격 ledger pointer (필수)
- **결정**: <CEO 직접 / CTO Auto / 양자 합의> + 1줄 근거
- **Open loops**: <남은 일·다음 Growth 후보>
```

CTO 의무 (charter §3 #5): 매 Growth 종료 마지막 step 에 위 1줄+pointer entry 를 main §6 에 직접 작성 (integrator 마무리).

> **아카이브**: Growth-4 ~ Growth-134 의 slim 엔트리는 [docs/learn-logs/growth-archive.md](docs/learn-logs/growth-archive.md) 로 이동 (G-9 cap 운영, 회전 9차 Growth-143). 회전 정책: slim §6 는 최근 시기 Growth 만 유지, cap 접근 시 오래된 엔트리를 원문 그대로 아카이브로 이동.

> Growth-13 ~ Growth-15 (Growth-34 회전) · Growth-16 ~ Growth-20 (Growth-37 회전) · Growth-21 ~ Growth-32 (Growth-59 회전) · Growth-33 ~ Growth-48 (Growth-64 회전) · Growth-50 ~ Growth-53 (Growth-78 회전) · Growth-54 ~ Growth-67 (Growth-89 회전) · Growth-68 ~ Growth-134 (Growth-143 회전) 은 `growth-archive.md` 로 이동. 검색: `python scripts/ledger-index.py --symbol <name>` 또는 인격 ledger pointer.

### Growth-135 (2026-06-30) — 한방 RAG D2 라이브 종결
- VPS legal-rag postgres(legaldb) 재사용 결정(Supabase 반론 후 self-host 일관). 스키마 00~06 적용(vector+pgcrypto, app_user 최소권한, legal테이블 무변경 순수추가), 데모계정 bcrypt 시드(crypt(), 평문 repo 미커밋). corpus 적재: scripts/corpus/ingest_hanbang_notices.py(실 ingest.py 청킹 재사용) 일회성 컨테이너로 coolify net(db+embed:8080 e5-base) 직접접근 → 고시 3건/**781청크 전부 768d 임베딩**. 검증: notices=3/chunks=781/embedded=781, FTS 추나4·약침1·상대가치11(첩약0=simple-FTS 부분문자열 미스, ANN/pg_bigm 보완 예정). embed 30s타임아웃→batch8+timeout120 detached. D3 공개배포(hanbang-rag.n9n.co.kr) 미진입(outward-facing 확인 대기).
### Growth-136 (2026-06-30) — 한방 RAG D3 공개배포 LIVE
- `hanbang-rag.n9n.co.kr`. 토폴로지: app-only 컨테이너가 legal-rag 기존 db(legaldb 781청크)+embed(e5-base) external network(gwpba3e8…) 재사용(중복0·legal배포 비결합·DSN app_service=공개고시라 RLS불요). web SPA = legal `/app` vanilla 슬림화(탭/사건현황/사건상세/사건필터 제거 → 로그인+검색+고시원문드로어, 한방카피, engineer-agent 778줄 node --check OK). Dockerfile uvicorn화, api `/app` StaticFiles 마운트, `deploy/preview/hanbang-rag.compose.yml`(Traefik 라벨+/auth/login ratelimit). 수동 docker compose 빌드·기동(Coolify 토큰 불요, VPS `.env` 시크릿 미커밋, DNS는 wildcard *.n9n.co.kr 기존). 라이브 검증 PASS(`deploy/preview/hanbang-rag.verify-search.py`): /health ok·/app 200·로그인(role=admin)·5시나리오 검색 각5건 정확인용(추나/비급여보고/본인부담/상대가치/보건의료기술분류)·고시원문 591KB. **부수성과: cwd-hook 트랩 영구수정**(`.claude/settings.json` 훅 3종 `${CLAUDE_PROJECT_DIR}` 절대경로화 → 서브에이전트·cd 무관). 잔여: Coolify 정식등록(founder 선택사항, compose 커밋됨)·corpus 표형식 청크정제·WTP 인터뷰(유일 제품게이트).
### Growth-137 (2026-06-30) — 한방 corpus 표·서식 청크 정제
- law.go.kr 별표(첨부 표·서식)가 박스드로잉 문자(─━│┃┼)로 표를 그려 임베딩·FTS·발췌문 오염(전체 문자의 78~86%가 노이즈). `scripts/corpus/ingest_hanbang_notices.py` 에 `clean_admrul_text()` 추가(engineer-agent 위임, CTO 실corpus 3건 검증) — 순수 괘선줄 제거 + 테두리→공백(셀 텍스트 보존) + 용지규격 보일러플레이트 제거, `parse_xml` body 에 적용. VPS one-off 컨테이너(gwpba3e8 net, DSN app env서 변수전달=stdout노출0) 재인제스트: **청크 781→125**(84%↓, 고밀도 실내용), 박스문자 chunk·full_text 모두 0, orphan 0(ON CONFLICT+orphan삭제 정합성). 5시나리오 라이브 재검증 PASS·발췌문 청결(상대가치 쿼리→"제1장 의료급여수가의 기준 및 그 계산방법…" 정확착지, 드로어 full_text 591K→132K 정제판). 런북 §7 해소·§8 재인제스트 절차 신설. 잔여: pg_bigm 한국어 바이그램(legal-rag 공유이미지 트랙)·WTP 인터뷰(유일 제품게이트).
### Growth-138 (2026-07-01) — 한방 RAG D4
- WTP 인터뷰 키트. founder가 원장 대상 WTP 인터뷰(유일 제품게이트)에 인쇄해 쓰는 실전 도구 `docs/business/hanbang-wtp-interview-kit.md`(PM 위임 작성, CTO 검토·교정). 6섹션: 목적·가설/대상표본(원장3+청구담당2 최소5)/라이브데모 5시나리오 시연+페인질문/비앵커링 WTP 프로빙(현행대안 정량→self-host 중요도→van Westendorp 4질문→결정권자·예산주기)/반론 대응 6종(맥챗무료론·HIRA포털·설치귀찮음 등 변별)/응답 캡처 템플릿+wiki 환류경로. **CTO 교정 3건**: ①kill-criteria를 가격 임계값(근거0·앵커링/자기충족 위험)→**페인 신호 기반**으로 교체(소요≤5분+반려≤1건 or 무료대안 충분; van Westendorp는 수집만, 보류 게이트 아님—가격밴드는 결과물) ②§4(d)에 EMR 번들 질문 추가(GTM OQ "번들vs독립" 충족, 별도트랙 불요) ③시나리오5 쿼리 라이브 검증→"보건의료기술 분류체계"로 교정(변형 "분류 한방"은 비급여 코드표 오착지). **5시나리오 정확 쿼리 라이브 전수확인**(실인터뷰 빈결과 방지). D4 인터뷰-준비 게이트 충족, 잔여=founder WTP 인터뷰 실행 + 마케팅 랜딩 풀빌드(CDO, D4+ 별도트랙).
### Growth-139 (2026-07-01) — 한방 RAG 피벗
- 건보 급여기준 검색 → 자보(자동차보험) 삭감 채널 재조준. founder가 D4 WTP 키트 검토 중 근본 반론 제기(①정책·수가변경 저빈도 ②공개데이터에 self-host 무의미 ③무료 AI가 대부분 무료 제공) → CTO가 deep-research(101 agent) 실행해 반론 검증 → **반론 편에 근거**: 삭감 페인 '크기' 미확증(삭감통계 claim 전원 기각), 확증된 실 분쟁은 전부 자보 채널(건보 아님, 한의협·한방병협 2023 공동성명·서정철 원장 자보사 환수소송 승소), Q3 무료AI 정확도 완전 미조사, self-host 법적필연성 반대방향(소상공인 10인미만 개보법 최소조치 면제), 한의맥이 청구 base 독점하나 삭감방어 백지. 환류 `knowledge/wiki/sources/deep-research-hanbang-billing-pivot-2026-07.md`(+index, 커밋 61ed16c/492e071 푸시). founder 결정=한방 유지+자보 재조준. **Phase1(저비용·수요 선검증)**: WTP 키트를 자보 삭감 페인으로 v2 재작성(pm-agent 위임, CTO 7체크포인트 PASS·섀도파일0)=`docs/business/hanbang-wtp-interview-kit.md` fac71c6, 자보 데모 안 만들고 건보 데모를 능력시연으로만 쓰며 자보 페인 구두 프로빙 → corpus 재구축 전 demand 검증. **Phase2(인터뷰 신호 게이트)**: 원장 자보 삭감페인+WTP 확인 시 자보 corpus 재인제스트+데모 재조준. 미검증: 자보 삭감 사이즈·WTP·self-host명분. 잔여 저비용 옵션: Q3 무료AI 한국 급여기준 정확도 CTO 자체 스팟체크. memory `hanbang-rag-vertical-gate` 피벗 반영.
### Growth-140 (2026-07-01) — 제로베이스 RAG 수익 파이프라인 deep-research (산업무관·엔드투엔드, 108 agent·6.2M tok·~117분·25 sources·3-vote 검증). founder "제로베이스에서 RAG로 수익 낼 파이프라인" 요청 → 범위 확정(완전 산업/스택 무관 + 엔드투엔드: 버티컬선정→GTM→유닛이코노믹스). **확증 8건**: 파일럿지옥(커스텀 5%만 프로덕션·외부구매 2배, MIT NANDA/中), 고위험 전문서비스 코파일럿 실매출(Harvey 법률 $100M→$300M ARR 10개월·Hebbia 금융 15배/高), 엔터프라이즈검색(Glean $100M→$300M 15개월/高), **이기는 GTM+과금=고단가 seat($1,200/석·월)+12개월계약+최소석수+land-expand+전직전문가 하이터치CS(高)**, 기존SaaS 하이브리드 헤지(65% seat+usage미터·순수 usage/outcome 이행 0/高), 속도-마진 상충(Supernova 2년 $125M·마진~0 vs Shooting Star ~60%/高), 마진레버(프롬프트캐싱 90%↓/高), 벡터DB 원가실측(Pinecone $50-500/월/高). **기각 10건**: a16z발 "해자 전무"·"앱마진 50-60%"·outcome과금 미채택 등 비관서사 다수 adversarial 기각 → 낙관·비관 둘 다 미확증, 해자문제 미해결. **CTO 함의**: ①확증 WTP는 고위험 전문영역뿐, 우리 자산 중 legal 버티컬만 시장정렬(한방 SMB는 또 반대편) ②우리 차별화(self-host·API비0·저터치)가 이기는 GTM(하이터치·전직전문가CS·고ACV)과 정면충돌
- self-host는 규제세일즈포인트일뿐 수익엔진 아님 ③usage/outcome 과금 시장에 없음→seat/연간+land-expand 기본 ④속도-마진 상충이 우리 헤지철학(로컬임베딩·캐싱)과 정렬하나 성장 느림 정직인정 ⑤최대리스크=프론티어가 버티컬 정확도 따라잡으면 RAG 커모디티, 해자는 코드 아닌 고객 워크플로 락인(Harvey도 자체모델 폐기). 환류 `knowledge/wiki/sources/deep-research-rag-revenue-pipeline-2026-07.md`(+index, 4422d51/288c791). 잔여: legal WTP 인터뷰(미검증 게이트)·1인+AI팀에서 하이터치CS를 AI-agent CS로 대체 가능한가.
### Growth-141 (2026-07-02) — 수익 접근 근본 전환
- market-first 기회사냥 폐기, 검증수요-먼저 서비스 온램프. 세션 아크: ①벤치마크 헌트(108 agent)=새 SMB 버티컬 없음+금융 후보는 founder 통찰 "1인 기업에 책임 위임 안 함"으로 사망→**liability-sink-test 지배축 신설**(메모리) ②모바일 현금흐름 헤지=deep-research 하니스 2회 실패(~11M tok, 적대적 verify가 산업추정치 전량 기각)→**추정치 랭킹=구성적 단일 에이전트** 방법론 확정(메모리 deep-research-harness-fit), 한국 셀러 AI 유틸 확정했으나 수요 프로브에서 상세페이지 서브니치 사망(Gency/셀러비서 선점, AI툴 검색수요 미미, 검증수요는 done-for-you 외주) ③founder "3연패면 접근이 틀렸다"+제로우위 프로필(고객·네트워크·도메인 전무, 런웨이 6~12개월) 공개→**새 방법=검증수요-먼저 마켓플레이스 대행**(현금+도메인엣지+후기를 벌어 쌓고 나중에 제품화, 서비스=온램프). 첫 아레나(founder 확정)=SMB AI 자동화 셀업. 그라운딩 1회(단일 에이전트, 크몽/Fiverr/ieumax 직접페치): 범용 "AI 챗봇" 크몽 356리스팅 0리뷰 레드오션 vs 업종명시 "예약·상담 자동화" gig만 5.0★ 전환 → **첫 오퍼=미용실/피부관리실 예약·노쇼 자동화**(셋업 30~50만+월 5~13만, 채널=크몽 니치다운 무료데모+아프니까사장이다 168만). 환류 `knowledge/wiki/sources/smb-ai-services-first-offer-2026-07.md`(+index). 메모리 revenue-approach-reframe(모바일 트랙 흡수종료). legal-rag·hanbang 기존 베팅 유지(병렬 온램프). 잔여: founder 첫 gig 실행(도구 데모 1개→크몽 프로필→관찰 노트), 대행 산출물의 preset 복리 등록.
### Growth-142 (2026-07-02) — 노쇼가드 LIVE
- 첫 서비스 오퍼(미용실 예약·노쇼 자동화)의 공개 데모+영업 킷 end-to-end 구축. founder "demo 잘 만들어 ieumax처럼 공개하고 크몽·숨고 등록" 지시 → 4-인격 병렬(CTO 스펙/CMO gig킷/engineer 앱/CDO 랜딩). **산출**: ①스펙 `docs/business/noshow-demo-spec.md`(30초 시연 시나리오·시뮬 경계·6h 리셋) ②CMO `docs/business/noshow-gig-kit.md`(크몽 제목 3안 전부 업종명시형·3단 티어 셋업 29/39/49만+월 5/8/13만 내장·무료데모 loss-leader·네이버예약 변별 FAQ·숨고 견적템플릿·랜딩 7섹션 실카피) ③engineer `services/noshow-demo/`(FastAPI+SQLite app-only·데모클록 빨리감기·리마인더 dedup·취소→대기 자동채움·노쇼위험 파생판정·pytest 8) ④CDO 랜딩(gig킷 카피 verbatim 조판·카카오옐로우·Playwright 3뷰포트 검증). **CTO 통합 감사 2건 적발**: 노쇼위험 판정규칙 스펙 누락(데모는 응답채널 없어 "무응답" 규칙 불성립→발송완료+슬롯-1h 파생판정으로 재정의), engineer 보정 미배선(grep 실측 engine만 1곳→4파일 배선 재지시, subagent-cross-service-verify 패턴 재확인). **배포**: noshow.n9n.co.kr 수동 compose(hanbang 런북 패턴, ssh키=n9n_preview_ed25519), 시크릿 0·외부의존 0·API비 0. **라이브 검증 PASS**: 4페이지 200, 시드 노쇼위험 뱃지 1건(조노쇼), 예약생성→확인메시지, 빨리감기→리마인더 4건, 취소→대기채움(이대기 fulfilled+offer/filled 2메시지), 422=입력검증 정상. 검증 오염 후 재시작으로 시드 초기화. 23커밋 푸시(파일당). M2/M3보다 앞선 서비스-온램프 트랙(Growth-141) 매출 게이트 기여. 잔여=founder: 크몽/숨고 계정·gig 등록(킷 §A/§B)·30초 시연영상(스펙 §2 시나리오).

### Growth-143 (2026-07-05) — 시스템 위생 감사 + P1 해소: 가드 부패 4종·설정 부채 정리

- **인격**: CTO (감사 subagent 3종: config / repo-systems / 신기능)
- **Axis touched**: creater (diagnose·learn-log 운영), ddl (catalog fk-exempt 4)
- **Milestone**: 전 milestone 지원 (내부 효율·가드 신뢰 회복)
- **Revenue/cost**: 직접 매출 0 / Fable 5 1세션 + 감사 subagent 3
- **Why (1줄)**: founder "시스템 점검" 요청 — 3방향 감사에서 위생 부채(가드 FAIL 방치·설정 중복·문서-실물 불일치) 발견
- **상세**: [cto.md#Growth-143](docs/learn-logs/cto.md)
- **결정**: founder 승인 ("P1부터 해소하자") + 세부 실행 CTO Auto
- **Open loops**: 홈(C:/Users/cubis) 커밋0 가짜 git repo 삭제(founder 확인), 비활성 플러그인 4종 uninstall(founder), P2 5건(훅 오버헤드·토큰절약 4종 정책·compose 템플릿화·ledger 아카이브·모델 역할표)

### Growth-144 (2026-07-05) — P2 일괄 해소: 훅 슬림화·토큰정책·deploy 템플릿·G-22 ledger 캡

- **인격**: CTO (글로벌 설정·ledger·가드) + DevOps (deploy 템플릿)
- **Axis touched**: creater (G-22 가드·아카이브 규약), deploy (traefik 템플릿 등록)
- **Milestone**: 전 milestone 지원 (세션당 오버헤드·원장 기계가독성)
- **Revenue/cost**: 직접 매출 0 / **비용 절감**: Bash 툴콜당 훅 프로세스 ~9→~3 (사운드훅 27등록 삭제 + token-optimizer per-call 7종 비활성 + headroom MCP 상주 제거)
- **Why (1줄)**: founder P2 승인 — 같은 목적 도구 중복 활성은 절약이 아니라 spawn 비용, 원장은 100KB Read 한도 앞에서 자기 도구로 안 읽힘
- **산출**: 홈 phantom .git 삭제(커밋0 확증 후) / TOKEN-POLICY.md(RTK+context-mode 2종 체제) / deploy/templates/traefik-labels.tpl.yml+README(변형 A/B, 3벌 라벨과 캐논 일치 CTO 검증) / 2단계 아카이브 규약(README)+growth-archive 볼륨 4분할+engineer 79→22KB+**G-22 신설 PASS**
- **결정**: 모델 역할표 "Orchestration/Planning=Opus" 행 유지 (founder 확정)
- **상세**: [cto.md#Growth-144](docs/learn-logs/cto.md) · [devops.md](docs/learn-logs/devops.md)
- **Open loops**: 비활성 플러그인 uninstall(founder, token-optimizer 포함 5종으로 증가)

### Growth-145 (2026-07-05) — 토큰스택 v2 레인 재배치: 4종 활용 최대화 (겹침 없는 전용 레인)

- **인격**: CTO
- **Axis touched**: creater (글로벌 도구 배치 정책)
- **Milestone**: 전 milestone 지원 (컨텍스트 품질·컴팩션 생존성)
- **Revenue/cost**: 직접 매출 0 / read형 툴콜당 TO 훅 spawn 2–3회 재도입 (컴팩션 가이던스 피더 대가 — v1 슬림 대비 증가, 원 4종 동시활성 대비 감소: bash_hook·per-call quality-cache·checkpoint 3종 컷 유지)
- **Why (1줄)**: founder 지시 "4종 각 장점 최대화, 이벤트 전후·리소스 접근 유형별 배치" — v1 전면 슬림과 원 중복활성의 양립해 = 도구별 전용 레인
- **산출**: TOKEN-POLICY.md v2(레인 소유권 테이블+리소스→도구 매트릭스) / token-optimizer **vendored 사본**(~/.claude/vendored/, 플러그인 disabled 유지·cache sweep 면역) 선별 18/21훅 수동 등록 / headroom MCP(0.24.0) on-demand 재등록 / 런처 env 고정으로 `CLAUDE_PLUGIN_DATA` 타 플러그인 누수(codex 오배송 실측) 차단 / 가이던스 파이프라인 end-to-end 실검증(세션특화 PRESERVE/DROP 재현)
- **결정**: Bash 재작성 축은 RTK 단독 (TO bash_hook 미등록) — 같은 레인 이중 개입만 금지, 고유가치는 살린다
- **상세**: [cto.md#Growth-145](docs/learn-logs/cto.md)
- **Open loops**: 다음 세션 훅 적용 확인(현 세션은 구 등록 유지), 비활성 플러그인 uninstall(founder — 단 token-optimizer는 데이터 디렉터리 유지 필요, uninstall 시 vendored 훅의 store가 사라짐)
