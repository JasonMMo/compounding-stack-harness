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

> **아카이브**: Growth-4 ~ Growth-67 의 slim 엔트리는 [docs/learn-logs/growth-archive.md](docs/learn-logs/growth-archive.md) 로 이동 (G-9 cap 운영, 회전 8차 Growth-89). 회전 정책: slim §6 는 최근 시기 Growth 만 유지, cap 접근 시 오래된 엔트리를 원문 그대로 아카이브로 이동.

> Growth-13 ~ Growth-15 (Growth-34 회전) · Growth-16 ~ Growth-20 (Growth-37 회전) · Growth-21 ~ Growth-32 (Growth-59 회전) · Growth-33 ~ Growth-48 (Growth-64 회전) · Growth-50 ~ Growth-53 (Growth-78 회전) · Growth-54 ~ Growth-67 (Growth-89 회전) 은 `growth-archive.md` 로 이동. 검색: `python scripts/ledger-index.py --symbol <name>` 또는 인격 ledger pointer.

### Growth-68 (2026-06-15) — landing-astro 첫 React-island section variant: glowy-waves hero (21st.dev → 8축 누적)

- **인격/Axis/Milestone**: CTO(카드 선택·통합·시각 게이트·배포) + Engineer(React 아일랜드 인프라·variant 구현·L3) + CDO(비주얼 토큰화) / **theme/section(8축)**·frontend / **M1 GTM**(데모 폴리시 상향)
- **1줄 rollup**: 순수 Astro SSG였던 landing-astro 에 `@astrojs/react`+`framer-motion` 도입(아일랜드 한정, `client:visible` 40KB gzip만 hydrate, 나머지 SSG 유지) → 21st.dev "Glowy Waves Hero"를 **재사용 hero variant `glowy-waves`**로 적응(shadcn Button 제거→토큰 anchor, headline/subhead/cta/pills/stats props 파라미터화, prefers-reduced-motion 준수) → `catalog.yaml` hero.variants 등록 + `site_manifest.py` variant/pills/stats 스레딩(42/42 PASS) → gtm-landing 적용·재배포. hero B급→프리미엄.
- **함정/교훈**: ① 21st.dev 소스는 로그인/버튼 불필요 — Next.js SSR `__next_f.push` 페이로드에 전체 코드 인라인, curl+파싱으로 추출 가능(WebFetch는 SPA 셸만 반환). ② 외부 컴포넌트는 "한 장에 붙이기"(§3 안티패턴)가 아니라 **section variant로 카탈로그 등록**해야 복리. ③ IDE TS "Cannot find module" 진단은 npm install 전 stale LSP — `astro build`(vite 타입인지) 통과가 출고 기준. ④ headline 그래디언트 split이 첫 마침표 의존 → `headline_accent` 슬롯화는 open-loop.
- **상세**: [engineer ledger](docs/learn-logs/engineer.md) · [cdo ledger](docs/learn-logs/cdo.md)
- **결정 메모리**: [[marketing-site-track]]

### Growth-69 (2026-06-15) — glowy-waves hero no-JS 가시성 보강 (dogfood #3 계열 재발 차단)

- **인격/Axis/Milestone**: CTO(진단·검증) + Engineer(수정) / theme/section·frontend / M1 GTM
- **1줄 rollup**: framer-motion `initial="hidden"`(opacity:0)이 `client:visible` SSR HTML 에 baked → **JS 비활성/hydration 실패 시 hero(`<h1>` 포함) opacity:0 불가시**(Growth-66 dogfood #3 와 동일 계열). 수정: hidden variant opacity 0→1, **y/scale 이동만 진입 애니메이션으로 유지**(approach A, transform-only) → no-JS 에서도 콘텐츠 보임. 라이브 검증 no-JS h1 opacity `0→1`, JS-on canvas·demo 정상.
- **함정/교훈**: ① **대소문자 일치 grep false-negative** — 정적 HTML 을 대문자(CSS `uppercase` 결과)로 grep 해 "client-only 렌더, SEO 결함" 으로 오진했으나, 대소문자 무시 재검 결과 pills/stats 텍스트는 **처음부터 전부 SSR**됨(`client:visible`는 hydration만 지연, HTML SSR 유지). 진짜 결함은 SEO 가 아니라 opacity:0 no-JS 가시성이었다 → 정적 산출물 검증은 **case-insensitive + JS-off 렌더(java_script_enabled=False)** 둘 다 필수. ② 모션 진입효과는 opacity 페이드보다 **transform-only** 가 no-JS-safe.
- **상세**: [engineer ledger](docs/learn-logs/engineer.md)
- **결정 메모리**: [[marketing-site-track]]

### Growth-70 (2026-06-15) — 21st.dev 폴리시 컴포넌트 2종 → 재사용 variant 축적 (marquee-3d + carousel)

- **인격/Axis/Milestone**: CTO(카드선택·소스추출·proof캡처·시각/배포 게이트) + Engineer(2 variant 구현·L3·no-JS검증) + CDO(콘텐츠 큐레이션) / **theme/section(8축)**·frontend / M1 GTM(데모 폴리시·proof)
- **1줄 rollup**: ① **logos variant `marquee-3d`** (Shatlyk1011 3D Marquee 적응, deps clsx+tailwind-merge) — 콘텐츠를 로고 아닌 **우리 12개 라이브 생성 데모 스크린샷 월**("Real systems this harness generated", `public/proof/*.jpg` 130KB self-host)로 = 정직한 proof. ② **features variant `carousel`** (0xUrvish Feature Carousel 적응) — `motion/react`→framer-motion, `@hugeicons`→기존 lucide-react(새 의존 0), 외부 unsplash→proof 스샷. 둘 다 `client:visible` 아일랜드, items/images manifest 스레딩(42/42 PASS), no-JS 가시(img opacity 1·첫 feature SSR), gtm-landing 적용·배포. 페이지: hero(glowy)→proof월→feature 카루셀→FAQ→CTA→contact.
- **함정/교훈**: ① **innerText case-transform 재확인** — Chromium `innerText`가 CSS `uppercase`를 반영해, mixed-case 부분일치 검증이 false-negative(Growth-69 grep 교훈의 런타임판). DOM 검증은 case-insensitive 또는 `textContent` 사용. ② Astro island가 prop을 **escaped-slash JSON**으로 직렬화 → 정적 HTML 리터럴 `/proof/` grep 0건이나 no-JS 렌더엔 12 img 존재 → island 검증은 **렌더(Playwright) ground truth**가 grep보다 신뢰. ③ 외부 컴포넌트 적응 표준화: 새 아이콘/모션 의존은 **기존 설치분 재사용**(lucide/framer-motion)으로 치환.
- **상세**: [engineer ledger](docs/learn-logs/engineer.md) · [cdo ledger](docs/learn-logs/cdo.md)
- **결정 메모리**: [[marketing-site-track]]

### Growth-71 (2026-06-15) — impeccable 디자인 SKILL vendoring (CDO craft 엔진 도입)

- **인격/Axis/Milestone**: CTO(검토·결정·중화·배선·커밋) + Engineer(vendoring·감사) + CDO(craft 법규 흡수) / tooling(design 품질)·theme/section / M1(디자인 품질 상향)
- **1줄 rollup**: 디자인 품질 상향 위해 `pbakaus/impeccable`(★38k, Apache-2.0, design language SKILL) 코어를 repo 에 **vendoring**(`.claude/skills/impeccable/` @3.6.0 SHA fff712c, 93파일, LICENSE+NOTICE.vendored.md). 라이브러리 아닌 지식 레이어 — 우리 skill/agent 포맷 그대로. 23 커맨드(craft/audit/critique/layout/colorize/typeset/bolder/delight/polish…). **register Brand/Product = 우리 deliverable_kind marketing-site/business-system 와 동형**. CDO design-agent 에 craft 엔진으로 명문화([design-agent.md](.claude/agents/design-agent.md) "Craft 엔진" 절).
- **함정/교훈**: ① **감사가 실네트워크 1건 적발** — `context.mjs` 가 매 세션 `impeccable.style/api/version` 폴링(UPDATE_AVAILABLE) → no-network auto-path 위반. `.impeccable/config.json {updateCheck:false}` 로 중화(커밋되어 전 운영자·headless 적용, env 보다 견고). 서드파티 vendoring 은 **반드시 네트워크/telemetry/API 감사 후 도입**. ② vendored-pin 규율: 업스트림 재동기화는 `npx` 자동 아닌 수동. ③ **도구가 우리 craft drift 를 사전 차단** — impeccable anti-slop 이 우리 glowy hero(보라 그래디언트+글로우)를 slop 으로 깜 → reconcile 거리(첫 실전 = gtm-landing critique 패스). motion 규칙은 Growth-69 교훈과 글자그대로 동일.
- **상세**: [engineer ledger](docs/learn-logs/engineer.md) · [cdo ledger](docs/learn-logs/cdo.md)
- **결정 메모리**: [[marketing-site-track]] · [[impeccable-design-skill]]

### Growth-72 (2026-06-15) — impeccable 첫 dogfood: critique → typeset de-slop (gtm-landing)

- **인격/Axis/Milestone**: CTO(critique 실행·검증·배포) + Engineer(typeset 실행) + CDO(폰트 결정) / tooling(design)·theme/section / M1
- **1줄 rollup**: vendored impeccable 첫 실전 — `/impeccable critique gtm-landing` (Brand register, NO_PRODUCT_MD 우회) → Design Health **27/40**, **결정론 detector(detect.mjs)가 실슬롭 2건 적발**: ① gradient-text(hero "Zero dev team." — Absolute Ban) ② em-dash 9개. + LLM 적발: 폰트 4/4 reflex-reject(Plus Jakarta/Inter/DM Sans/DM Serif), indigo-glow SaaS first-order reflex. → `/typeset` 패스: 그래디언트 텍스트 제거(솔리드 #C4B5FD), 폰트 → **Bricolage Grotesque(display)+Epilogue(body)** off-reflex contrast-axis 교체(@fontsource-variable self-host, Korean fallback). 라이브 재검증 detector **gradient-text 제거**(em-dash만 잔존), computed font 적용 확인, no-JS opacity 1. critique 스냅샷 `.impeccable/critique/` 영구화(트렌드·polish 백로그).
- **함정/교훈**: ① **도구가 우리 craft drift 를 사전/사후 정확히 적발** — 우리가 의도 적응한 glowy hero 의 그래디언트·제네릭폰트를 dogfood 가 잡음(도구 가치 입증). ② impeccable reflex-reject 폰트 목록에 우리 @fontsource 기본 4종 전부 포함 → 디폴트 폰트=AI 모노컬처 tell. ③ critique 의 결정론 detector 는 grep 사각(em-dash cadence)도 잡음 — vision-QA 보완재.
- **상세**: [engineer ledger](docs/learn-logs/engineer.md) · [cdo ledger](docs/learn-logs/cdo.md)
- **결정 메모리**: [[impeccable-design-skill]] · [[marketing-site-track]]

### Growth-73 (2026-06-15) — critique 백로그 청산: quieter+clarify+polish → 27→30 (Good)

- **인격/Axis/Milestone**: CTO(검증·배포·재critique) + Engineer(3패스) + CDO(이미지 큐레이션) / tooling(design)·theme/section / M1
- **1줄 rollup**: gtm-landing critique 백로그 3건 순차(1→3→2) 단일 빌드·배포로 청산 — `/quieter`(웨이브 opacity/진폭/blur ~절반, radial blob 축소 → indigo-glow 카테고리 반사 완화), `/clarify`(body em-dash 9→0, 콜론/괄호/마침표로), `/polish`(carousel feature 이미지 → non-login richer 샷 edu-program/gtm-landing/construction). 라이브 재critique: **detector CLEAN(0 antipattern)**, Design Health **27→30(Acceptable→Good)**, 트렌드 영구화.
- **함정/교훈**: ① 무충돌 리파인 다건은 **단일 빌드·배포로 배치**가 효율(3패스를 각각 배포하면 오버헤드 3배). ② carousel proof 이미지의 근본 한계: 우리 business-system 데모가 auth-gated라 도메인 충실 dashboard 캡처 불가 — 공개 캡처 중 richest 선택이 최선(목업은 후속). ③ critique→fix→re-critique 트렌드(27→30)가 도구의 복리 루프를 수치로 증명.
- **잔여(open)**: carousel 전용 목업(P2), 연락폼 demo-stub→실엔드포인트(실고객 시), indigo 단색에 보조 accent(/colorize, 선택).
- **상세**: [engineer ledger](docs/learn-logs/engineer.md) · [cdo ledger](docs/learn-logs/cdo.md)
- **결정 메모리**: [[impeccable-design-skill]] · [[marketing-site-track]]

### Growth-74 (2026-06-15) — /colorize: indigo 단색 → 전략적 warm 보조 accent

- **인격/Axis/Milestone**: CTO(색 방향·검증·배포) + CDO(팔레트 전략) + Engineer(토큰·적용) / theme/section·tooling(design) / M1
- **1줄 rollup**: impeccable `/colorize` 로 indigo-monochrome aurora 에 보조 accent 1색 추가 — **`#AB5527` terracotta/burnt-coral**(oklch 52% .135 42, indigo 보색·비-네온·AA). 재사용 토큰 `accent-warm`(aurora theme.yaml) 으로 3곳 절제 적용: ① 차별화 스탯 "0 bits"(시선 유도, 나머지 화이트) ② carousel 활성 인디케이터 ③ FAQ open-state. navy+gold 클리셰·cyan+purple 슬롭·glow 트랩 회피. detector CLEAN 유지, 라이브 "0 bits"=rgb(171,85,39) 확인, contrast AA(5.17:1 FAQ / 3.09:1 대형스탯).
- **함정/교훈**: ① 보조색은 "rainbow vomit" 아니라 **의미/위계 지점만 ≲15% 도징** — 차별화 1포인트에 집중하면 단색 절제 유지하며 시선 유도. ② accent-warm 을 semantic 토큰화 → 전 landing 재사용(복리). ③ 현재 "0 으로 시작하는 스탯값" 휴리스틱으로 강조 — manifest `highlight:true` 플래그가 더 견고(open loop).
- **잔여(open)**: 스탯 강조를 manifest `highlight` 플래그로(휴리스틱 대체), carousel 전용 목업, 연락폼 실엔드포인트.
- **상세**: [cdo ledger](docs/learn-logs/cdo.md) · [engineer ledger](docs/learn-logs/engineer.md)
- **결정 메모리**: [[impeccable-design-skill]] · [[marketing-site-track]]

### Growth-75 (2026-06-15) — 2번째 테마 데모: HOPWELL 맥주 런칭 (harvest 테마) LIVE

- **인격/Axis/Milestone**: CTO(방향·배포·검증) + CDO(harvest 테마 craft) + Engineer(어댑터 멀티테마 픽스) + DevOps(배포) / **theme/section(8축)**·frontend·infra / M1(웹에이전시 데모 다양화)
- **1줄 rollup**: gtm(차가운 indigo-glow)과 **정반대 질감**의 맥주 런칭 랜딩 신설 — 신규 **harvest 테마**(앰버-카퍼 drench + 홉그린 + 포말, OKLCH; Big Shoulders Display + Hanken Grotesk off-reflex; 그레인 텍스처 + 탄산 버블, canvas 아님) + **hopwell 프로파일**(hero `brew` variant + 3 pillar=roasted malt/fresh hops/crisp finish + faq + cta). **https://hopwell.n9n.co.kr** LIVE + landing 포털에 카드 추가(2번째 라이브 테마). detector CLEAN, no-JS 가시, 전 섹션 AA. theme 축이 진짜 복리로 도는 것 2번째 증명.
- **함정/교훈**: ① **빌드 파이프라인이 aurora 하드코딩**이라 harvest 토큰이 덮여 carousel/FAQ가 indigo로 렌더 → `build-tokens-auto.mjs`(manifest의 theme 자동 읽기)로 **theme-aware 빌드** 픽스(전 미래 테마의 전제조건, Docker 무변경). ② **build green·detector CLEAN ≠ 비주얼 정상** — 풀페이지 스크린샷이 3차례 결함 적발(aurora 색 클로버, 거대 셰브론, below-fold 모션 blank). 시각검증 불가결 재확인. ③ 모션 reveal가 headless/below-fold에서 blank → threshold 0 + rootMargin 200px + 800ms fallback(Growth-69 계열 재발). ④ **배포 함정 2종**: `deploy_static_site.py --domain`은 **https:// 스킴 필수**(없으면 422 Invalid URL); docker_compose_domains PATCH 포맷은 `[{"name":svc,"domain":url}]` 배열. ⑤ SSH 터널(8000) 드롭+좀비소켓 점유 시 **다른 로컬 포트(8010)로 재수립** 후 직접 API 호출로 우회.
- **상세**: [devops ledger](docs/learn-logs/devops.md) · [cdo ledger](docs/learn-logs/cdo.md) · [engineer ledger](docs/learn-logs/engineer.md)
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]]

### Growth-76 (2026-06-15) — 첫 구조-다양성 아키타입: A2 에이전시/포트폴리오 (Studio North, atelier 테마) LIVE

- **인격/Axis/Milestone**: CTO(방향·검증·배포·커밋) + CDO(atelier 테마·A2 구성 craft) + Engineer(신규 섹션 type·라우팅) / **theme/section(8축)**·frontend·infra / M1(웹에이전시 데모 다양화)
- **1줄 rollup**: gtm/hopwell이 "색·텍스트만 다른 같은 패턴"이란 CEO 지적 → 진짜 차별은 **페이지 구조**라는 결론(블루프린트 [landing-pattern-matrix](docs/architecture/landing-pattern-matrix.md)). 첫 구조-차별 아키타입 **A2 Creative Agency/Portfolio** 산출: 신규 섹션 type 2종(**gallery** masonry-3col / **story** founder-split) + hero **headline-only** variant + 3번째 테마 **atelier**(잉크블랙 hero + warm-paper + copper, Raleway+Karla off-reflex). 구성=headline-only hero→masonry 갤러리→창업자 split 스토리→single-col 리스트→단일 후기→다크 CTA→미니멀 푸터. **https://studio-north.n9n.co.kr** LIVE + 포털 "준비 중" placeholder를 라이브 카드로 교체. 카탈로그 8→10 type(additive). detector CLEAN, no-JS h1 opacity 1, 전 섹션 AA(잉크/페이퍼 14.2:1).
- **함정/교훈**: ① **theme≠pattern 다양성** — 테마축만으론 의뢰인이 구조 동일성을 간파. 섹션 variant × 페이지 아키타입 × 테마의 곱이 진짜 다양성(CEO는 취향, CTO가 분해·카탈로그화). ② **build green·detector CLEAN ≠ 비주얼 정상** 재확인 — CTA `with-image`가 3.7KB 빈 플레이스홀더(example-corp.jpg) 참조해 흰 박스 렌더 → 실제 콘텐츠 스샷(landing.jpg)으로 교체(풀페이지 스샷이 적발). ③ 8000 좀비소켓은 프로세스 소멸로 kill 불가(커널 누수) → deploy 스크립트 API_BASE를 임시 8010 패치 후 `git checkout` 복구(커밋 오염 방지). ④ 백그라운드 에이전트가 세션 cwd를 landing-astro에 고정 → 상대경로 훅 깨짐, 루트로 Set-Location 복구.
- **잔여(open)**: story `timeline-year` variant items[] 스레딩(A4 때), 갤러리가 dev 대시보드를 "brand work"로 재사용(데모 한정), 매트릭스 잔여 27 variant·A1/A3/A4/A5/A6 아키타입.
- **상세**: [cdo ledger](docs/learn-logs/cdo.md) · [engineer ledger](docs/learn-logs/engineer.md) · [devops ledger](docs/learn-logs/devops.md)
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]]

### Growth-77 (2026-06-16) — A4 아키타입 TERRA(도예 스튜디오) LIVE + 첫 SCROLL-CINEMATIC 섹션 + kiln 테마 + open-loop 종결

- **인격/Axis/Milestone**: CTO(방향·검증·배포) + CDO(kiln 테마·parallax-scroll craft) + Engineer(GalleryParallaxScroll·Lead·timeline-year·hooks 버그) + DevOps(배포·COOLIFY_API_BASE 오픈루프 종결) / **theme/section(8축)**·frontend·infra / M1(웹에이전시 데모 다양화)
- **1줄 rollup**: A4 아키타입(공예/로컬) 첫 인스턴스 **TERRA ceramics** 산출 → **https://terra-ceramics.n9n.co.kr** LIVE(HTTP 200, 4번째 라이브 데모). 신규: 4번째 테마 **kiln**(점토 테라코타+목회재 중성+가마 엠버, Cormorant Garamond+Source Serif 4, OKLCH cream-trap 회피). 첫 **SCROLL-CINEMATIC variant** `gallery/parallax-scroll`(framer-motion useScroll sticky full-viewport 챕터, scroll-driven — gtm·hopwell·studio-north은 전부 static-scroll). 신규 `story/timeline-year` HAVE, `lead/minimal-field` HAVE. 카탈로그 11→13 type. `texture:clay|ash|ember` 센티넬로 사진 0 demo 운영. 2 결함 수정(rules-of-hooks·Growth-69 SSR opacity). `COOLIFY_API_BASE` env 오픈루프 종결. BUILD SUCCESS·71 pytest PASS·impeccable CLEAN·desktop+mobile+no-JS PASS.
- **상세**: [cdo ledger](docs/learn-logs/cdo.md) · [engineer ledger](docs/learn-logs/engineer.md) · [devops ledger](docs/learn-logs/devops.md)
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]]

### Growth-78 (2026-06-16) — A6 아키타입 MERIDIAN(B2B 매니지드IT) LIVE + meridian 테마 + B2B 섹션 3종 + §6 회전 7차

- **인격/Axis/Milestone**: CTO(방향·profile 카피·검증·배포·로깅) + CDO(meridian 테마·B2B 비주얼 게이트) + Engineer(Process·Team·Logos quote-band·라우팅·폰트) / **theme/section(8축)**·frontend·infra / M1(웹에이전시 데모 다양화)
- **1줄 rollup**: A6 아키타입(B2B 서비스/컨설팅) 첫 인스턴스 **MERIDIAN**(매니지드IT·보안 자문) 산출 → **https://meridian.n9n.co.kr** LIVE(HTTP 200, 5번째 라이브 데모, 포털 카드 5장). 신규: 5번째 테마 **meridian**(쿨스톤 화이트 #F7F8F4 + 딥 포레스트그린 #1A5C3A, Syne+DM Sans, navy 반사 회피·AAA 전반). 신규 섹션 타입 2종 `process`(numbered-stack — 진행 단계, 합법적 시퀀스 넘버링)·`team`(headshot-grid — monogram-initials 폴백, 사진 0) HAVE, `logos/quote-band`(로고-수프 대안: 단일 고객 인용 다크 밴드) HAVE. 카탈로그 13 type(process·team 본격 구현). 전 섹션 **Astro-native(React 아일랜드 0)** — quote-band/numbered-stack/headshot-grid 무JS 렌더. BUILD SUCCESS·impeccable CLEAN·desktop+mobile+no-JS PASS(Growth-69)·forest-green 토큰 라이브 확인. §6 회전 7차(Growth-50~53 아카이브, G-9 199→167).
- **상세**: [cdo ledger](docs/learn-logs/cdo.md) · [engineer ledger](docs/learn-logs/engineer.md) · [devops ledger](docs/learn-logs/devops.md)
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]]

### Growth-79 (2026-06-16) — 공식 Anthropic 스킬 5종 검토 → 1종(webapp-testing)만 채택

- **인격/Axis/Milestone**: CTO(스킬 적합성 판정·vendoring·드리프트 차단) / 툴링 / M1(마케팅사이트 트랙 검증 인프라)
- **1줄 rollup**: anthropics/skills 5종 검토. **채택 1**: `webapp-testing`(Playwright `with_server.py` 서버 라이프사이클 + recon-then-action — landing-astro 로컬 pre-deploy E2E 갭; ui_check.py 는 서빙 중 URL 가정, 빌드→serve→Playwright 일괄관리 부재). 순수 테스트 인프라라 drift 0, Apache-2.0 동봉 vendoring. **skip 4** — `frontend-design`(vendored impeccable 의 부분집합·중복→경쟁 가이던스 드리프트), `brand-guidelines`(Anthropic 자사 브랜드 주입 = "고객마다 다른 회사로 보인다" thesis 정면 위배), `theme-factory`(10 프리셋+자체 테마 포맷 = 우리 `presets/themes/` 8축 단일진실과 경쟁→축 파편화), `web-artifacts-builder`(claude.ai 단일HTML 아티팩트용 = Astro SSG→Coolify 배포 타깃과 무관). 판정 원칙: 디자인 가이던스/테마 시스템 중복은 거부(드리프트), 보완적 테스트/인프라만 흡수.
- **결정 메모리**: [[official-skill-adoption-policy]] · [[impeccable-design-skill]]

### Growth-80 (2026-06-16) — A1 아키타입 FLUX(인프라 SaaS) 빌드 + flux 테마 + 신규 섹션 3종, ui_check 7/7 PASS (배포 대기)

- **인격/Axis/Milestone**: CTO(방향·통합·검증·커밋·로깅) + CDO(flux 테마·3 variant 스펙 craft) + Engineer(Stats·bento-mosaic·pull-quote-wall 구현·profile·폰트·반응형 수정) / **theme/section(8축)**·frontend / M1(웹에이전시 데모 다양화)
- **1줄 rollup**: A1 아키타입(SaaS Product Launch) 첫 인스턴스 **FLUX**(가상 개발자 인프라/관측성 SaaS) 산출 — 빌드+로컬 ui_check **7/7 PASS**(배포는 후속). 신규: 6번째 테마 **flux**(amber-gold #8B5E10 단일 액센트 OKLCH H72 미점유 + charcoal flat hero, Space Grotesk+Inter — aurora violet/Bricolage와 hue·폰트·레지스터 3축 분리, 네온/터미널그린 반사 회피). 신규 섹션 타입 **stats**(ticker-band — 카드 박싱 없는 인라인 통계 밴드, 14/14 타입 완성) + variant 2종 **features/bento-mosaic**(불규칙 grid hero카드 2행span)·**testimonial/pull-quote-wall**(전블리드 비대칭 인용). 매트릭스 백로그 #2/#5/#10 종결, HAVE 30. 함정: ① **인라인 grid-template은 @media로 못 덮음** — bento/pull-quote가 모바일 오버플로우(453>390), sentinel 클래스+scoped @media로 이전해 해결(Tailwind 반응형 prefix는 인라인 style 무력). ② logos/horizontal-scroll 텍스트 워드마크 폴백 신설(stock 자산 0 규율, meridian monogram 계승) + site_manifest.py companies[] emit 누락 버그 수정(images[] 동형 passthrough). G-8 PASS, impeccable detector CLEAN, BUILD SUCCESS, desktop+mobile no-JS PASS.
- **잔여(open)**: ① ~~flux-demo LIVE 배포~~ → **Growth-81 에서 종결**. ② pull-quote-wall 등 items[] 기반 variant가 catalog testimonial copy_slots.required(quote/author_name)를 강제당해 profile에 중복 기입 — copy_slots를 variant-aware optional로 완화 검토. ③ A3(Event)·A5(Mobile App) 아키타입.
- **상세**: [cdo ledger](docs/learn-logs/cdo.md) · [engineer ledger](docs/learn-logs/engineer.md)
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]]

### Growth-81 (2026-06-16) — A1 FLUX LIVE 배포 + 포털 6번째 카드 (Growth-80 P0 종결)

- **인격/Axis/Milestone**: CTO(배포·검증·커밋·로깅) + DevOps(Coolify 배포·터널·레지스트리) / **theme/section(8축)**·infra / M1(웹에이전시 데모 다양화)
- **1줄 rollup**: Growth-80 빌드 산출물(HEAD 무변경, git 동일 commit)을 **LIVE 배포** — `flux.n9n.co.kr` (Coolify project=jq25nyzfirch3flp7no2wg3u, app=oyemv0mttkn8eo05xflvc4x2, flux 테마, DEMO_MODE=1). `deploy_static_site.py --slug flux --domain https://flux.n9n.co.kr --compose /deploy/preview/flux.compose.yml --service web`, status=finished, HTTPS 200, 서빙 마크업 검증(stats/bento/pull-quote 전부 present·aurora 누수 0). 6번째 마케팅 데모 — 포털에 ⚡ SaaS 카드 추가 후 **포털 명시 재배포**(Growth-78 교훈 적용, push≠auto-deploy), landing.n9n.co.kr 200·flux 카드 반영 확인. 레지스트리 `infra/registry/flux.yaml`(status=live).
- **함정/교훈**: ① **스테일 테스트 동반 수정** — Growth-80 이 stats 타입(14번째)을 추가했으나 `test_catalog_has_process_team_and_thirteen_total` 이 13 을 단언 → 풀테스트 1 FAIL. 14 로 갱신(빌드 산출이 테스트보다 앞서면 같은 PR 에서 단언 동기화). ② **SSH 터널 안정성** — `ssh -fN` 가 백그라운드 태스크 reaping 시 SIGHUP 으로 소멸(터널 드롭→배포 `tunnel check failed`). PowerShell `Start-Process -WindowStyle Hidden` + `ServerAliveInterval=30 ExitOnForwardFailure=yes` 로 셸 세션과 분리 기동해 해소(Growth-76/77 좀비소켓 계열 후속). FLUX 라이브 검증은 공개 HTTPS 라 터널과 무관.
- **상세**: [devops ledger](docs/learn-logs/devops.md)
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]] · [[push-before-deploy]]

### Growth-82 (2026-06-16) — A3 아키타입 SUMMIT Horizon(이벤트/컨퍼런스) LIVE + ignite 테마 + 신규 variant 3종

- **인격/Axis/Milestone**: CTO(방향·통합·비주얼검증·배포·로깅) + CDO(ignite 테마 craft·variant 설계 스펙·A3 콘텐츠) + Engineer(horizontal-steps·newsletter-inline·four-up 구현·logos/grid 결함 픽스·폰트·profile) + QA(풀테스트 게이트) + DevOps(Coolify 배포·레지스트리) / **theme/section(8축)**·frontend·infra / M1(웹에이전시 데모 다양화)
- **1줄 rollup**: A3 아키타입(Event/Conference) 첫 인스턴스 **SUMMIT Horizon 2026**(가상 개발자 서밋) 산출·**LIVE** — `summit-horizon.n9n.co.kr` (Coolify project=k105u8soe4fergofhdje2nkt, app=jvo3hnfmf2bv8ce10mcj96l0, DEMO_MODE=1). 7번째 마케팅 데모. 신규 **7번째 테마 ignite**(crimson-red #C41E22 OKLCH H≈22 미점유 + off-white canvas, Barlow Condensed 800 + Lato — 기존 6 테마와 hue·폰트·레지스터 분리, 이벤트 긴급감). 신규 variant 3종: **process/horizontal-steps**(가로 번호 스텝+CSS ::after 커넥터, 모바일 세로 stack 붕괴, 무JS), **cta/newsletter-inline**(밴드 내 인라인 이메일 input+submit, DEMO_MODE 스텁), **stats/four-up**(풀블리드 crimson 밴드, 페이지 유일 풀폭 모멘트). 매트릭스 백로그 #9 종결, A3 BUILT 표기. G-8 PASS, diagnose 0 FAIL, pytest 329, ui_check 7/7, BUILD SUCCESS, **풀페이지 9/9 섹션 비주얼 검증**.
- **함정/교훈**: ① **공유 컴포넌트 variant 분기 누락 결함** — `logos/grid` 분기가 companies[] 텍스트 워드마크 폴백을 안 가져 "Logo assets not yet added." 플레이스홀더 노출(stock-asset-0 위반). 폴백이 `horizontal-scroll` 분기에만 있었음. grid 분기에 미러 + company shape 정규화(string·{name,tier} 양립, flux backward-compat). **교훈: 새 아키타입이 기존 컴포넌트의 안 쓰던 variant 분기를 처음 밟으면 그 분기의 무자산 폴백·shape 처리를 반드시 확인**. ② **빌드 green·ui_check 7/7 PASS ≠ 비주얼 정상**(반복 확인) — 풀페이지 스크롤 세그먼트 캡처로만 logos 플레이스홀더 + footer 이메일 오타(summary→summit) 적발. large-file-guard(>10KB) 회피: full_page PNG 대신 뷰포트 스크롤 세그먼트(각 ~30KB)로 분할 캡처. ③ companies 객체형 데이터는 manifest 까지 정상 passthrough — 결함은 순수 렌더 계층.
- **상세**: [cdo ledger](docs/learn-logs/cdo.md) · [engineer ledger](docs/learn-logs/engineer.md) · [devops ledger](docs/learn-logs/devops.md)
- **잔여(open)**: ① **A5(Mobile App)** 아키타입 — `gallery/grid-2x2` 1종만 NEED(four-up 은 이번에 구현돼 재사용). ② pull-quote-wall 등 items[] variant 의 catalog copy_slots variant-aware 완화(P1, 미해결).
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]] · [[push-before-deploy]]

### Growth-83 (2026-06-16) — A5 아키타입 Lumi(컨슈머 습관·집중 앱) LIVE + nova 테마(8번째) + 무사진 grid-2x2 + variant-aware 슬롯 완화(P1/P2 종결)

- **인격/Axis/Milestone**: CTO(방향·통합·근본원인 진단·비주얼검증·per-file 커밋·로깅) + CDO(nova 테마 craft·marquee 대비 다크화·포털 8번째 카드) + Engineer(Hero sentinel·Testimonial grid·Gallery 무사진 목업·Cta 위계·FeatureCarousel SSR·Stats fallback 구현) + QA(풀테스트·6게이트) + DevOps(Coolify 배포·포털 재배포·레지스트리) / **theme/section(8축)**·frontend·infra / M1(웹에이전시 데모 다양화)
- **1줄 rollup**: A5 아키타입(Mobile App) 첫 인스턴스 **Lumi**(가상 습관·집중 컨슈머 앱) 산출·**LIVE** — `lumi.n9n.co.kr` (Coolify project=x7be9f2b7nr1zhykxubn6wwt, app=j10swdnw5tyndidudjnsr04r, DEMO_MODE=1). 8번째 마케팅 데모. 신규 **8번째 테마 nova**(violet-magenta #8B2BE2 OKLCH 미점유 hue + white canvas, Plus Jakarta Sans + Nunito — 모바일 geometric-humanist). **무사진(0 stock) A5 경로 확립**: gallery/grid-2x2 `src`-optional → phone-frame CSS 앱스크린 목업 4종, logos/marquee-3d 는 harness 자체 /proof/*.jpg 자각적 프레이밍 재사용, cta/centered 다운로드 버튼쌍은 copy.secondary_* passthrough(매니페스트 무변경). 매트릭스 A5 BUILT 표기 → A1~A6 6개 아키타입 전부 BUILT. G-8 PASS, diagnose 0 FAIL, pytest 115(site_manifest), BUILD SUCCESS, **풀페이지 8/8 섹션 비주얼 검증**.
- **함정/교훈**: ① **테마 계약 ↔ 컴포넌트 갭(빌드 green·자동검사 통과가 못 잡음)** — nova `cta.centered.bg: surface-2` 가 Cta.astro bgClass(primary/gradient/dark/light 만 보유)에 없어 `bgClass.primary` 폴백 → violet 밴드 위 violet pill(primary)+동일 secondary = 위계 0. 산출 `dist/index.html` 앵커 클래스 직접 grep 으로 근본원인 확정 후, 컴포넌트가 테마 계약을 따르도록 수정(bgClass surface-* 추가 + `cta_secondary_style` 반영 + secondary-lg outline 신설). **교훈: 새 테마가 컴포넌트의 안 쓰던 styleHints 키(bg=surface-2, cta_secondary_style)를 처음 보내면 맵 키 커버리지·미사용 슬롯 처리를 반드시 확인**(Growth-82 ①의 variant 분기 누락과 동형 — 이번엔 theme-key 차원). ② **빌드 green ≠ 비주얼 정상(3연속 확인)** — Hero 빈 우측칼럼·Testimonial 6중1카드·grid-2x2 투명탭바·Cta 위계 0 전부 풀페이지 세그먼트 캡처로만 적발. large-file-guard(>10KB) 회피: 560×440 작은 뷰포트 + zai analyze_image(vision MCP)로 컨텍스트 오염 없이 CTA 재검증. ③ **Growth-69 부분위반 사전적발(QA)** — FeatureCarousel SSR 이 feature 1 설명만 DOM 텍스트, 2·3 은 props JSON 에만 → JS-off 시 1/3 만 노출. `sr-only <ul>` 무조건 렌더로 전 항목 DOM 화. **무차단 권고라도 명시 불변식(Growth-69)이면 커밋·배포 전 수정(임시통과 거부)**.
- **누적 자산**: 8번째 테마 nova(전 고객 재사용), gallery grid-2x2 src-optional 무사진 CSS 목업(전 모바일 데모 재사용), cta secondary 버튼쌍, **site_manifest `variant_overrides` 메커니즘(P2 종결)** — gallery grid-2x2/parallax-scroll `src`-optional + testimonial pull-quote-wall copy_slots variant-aware 완화로 **Growth-80/82 의 P1(items[] variant copy_slots 강제)도 동시 종결**.
- **상세**: [devops ledger](docs/learn-logs/devops.md) · [cdo ledger](docs/learn-logs/cdo.md) · [engineer ledger](docs/learn-logs/engineer.md)
- **잔여(open)**: A1~A6 매트릭스 1차 완성. 다음: variant 커버리지 확대 또는 신규 고객 needs 기반 조합.
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]] · [[push-before-deploy]]

### Growth-84 (2026-06-16) — A7 아키타입 Prism(API observability SaaS) LIVE + prism 테마(9번째) + hero/bento-grid 신규 변형 + §2 stale 정정

- **인격/Axis/Milestone**: CTO(방향·통합·비주얼검증·근본원인 진단·매트릭스 정정·per-file 커밋·로깅) + CDO(prism 테마 craft·hero/bento-grid 스펙·GlassmorphismTrust 레퍼런스 중화·A7 archetype 신설) + Engineer(HeroBentoGrid 구현·ticker-band styleHints.bg honor·full-links 데이터주도·catalog/manifest 스레딩·테스트) + QA(풀테스트·불변식 5종·flux 회귀) + DevOps(배포·레지스트리·포털) / **theme/section(8축)**·frontend·infra / M1(웹에이전시 데모 다양화)
- **1줄 rollup**: A7 아키타입(API Platform/Dev Tool) 첫 인스턴스 **Prism**(가상 API observability SaaS) 산출·LIVE — `prism.n9n.co.kr`. 9번째 마케팅 데모·**9번째 테마 prism**(deep-azure #1B4FA8 OKLCH H≈228 미점유 hue + white canvas, IBM Plex Sans+DM Sans+DM Mono(스탯 전용), AAA 전역). 신규 **hero/bento-grid** 변형(텍스트 좌 7col + stat/proof bento 클러스터 우 5col; GlassmorphismTrust 21st.dev 레퍼런스의 *구조*만 차용하고 다크네온/글래스 미감 중화; 무사진·무JS-가시). §4 백로그 #3 종결. diagnose 0 FAIL, pytest 127, BUILD SUCCESS, **풀페이지 비주얼 검증(hero/bento-grid·ticker-band·footer FIX 재검증 포함)**.
- **함정/교훈**: ① **테마 계약 ↔ 컴포넌트 갭 재발(Growth-83 ①과 동형, theme-key 차원)** — `Stats.astro` ticker-band 가 다크 밴드 전용 하드코딩(`hero-bg-from`+`primary-border`)이라 prism(라이트 테마, hero-bg-from=#F2F5FA)에서 블루 숫자 on 라이트 밴드 ≈1.6:1 대비 실패. CDO 가 `stats.ticker-band.bg: surface-2`(라이트 의도) 지정했으나 컴포넌트가 styleHints.bg 무시가 근본. 컴포넌트가 bg 토큰 honor(surface-*→라이트밴드+primary 숫자 7:1 / 미설정·dark→기존 다크, **flux 회귀 0** — flux 는 bg:dark 명시). **교훈: 라이트 테마가 다크-전용 하드코딩 공유 컴포넌트를 처음 밟으면 색 하드코딩을 styleHints honor 로 일반화**(Cta.astro bgClass 선례와 동형). ② **빌드 green·127 테스트 green ≠ 비주얼 정상(재확인)** — ticker-band 저대비·footer 빈 SUPPORT 컬럼 둘 다 풀페이지 세그먼트 캡처+zai analyze_image(vision MCP)로만 적발. ③ **잠재 결함 동시 수정** — Footer full-links 가 완전 하드코딩(Support=contactHref 없으면 빈 헤더)이라 meridian/flux 등 모든 full-links 데모에 빈컬럼 잠재 → 데이터주도 컬럼 + 빈컬럼 가드로 일반화. ④ **매트릭스 stale 정정** — §2 의 headline-only(A2 studio-north 이미 live)·bento-mosaic·pull-quote-wall 가 NEED 로 오기되어 있던 것을 HAVE 로 환류(34→38 HAVE, 18→14 NEED).
- **누적 자산**: 9번째 테마 prism(전 고객 재사용), **hero/bento-grid 변형 + hero `item_slots`(stat/marquee) 신설**(전 SaaS 데모 재사용), **ticker-band styleHints.bg 일반화**(라이트/다크 테마 양립), **full-links 데이터주도 컬럼 + 빈컬럼 가드**(전 full-links 데모 품질 향상). A1~A7 7개 아키타입 전부 BUILT.
- **상세**: [devops ledger](docs/learn-logs/devops.md) · [cdo ledger](docs/learn-logs/cdo.md) · [engineer ledger](docs/learn-logs/engineer.md)
- **잔여(open)**: A1~A7 BUILT. 잔여 NEED variant 14종(hero/scroll-reveal·features/timeline-horizontal·process/split-animation·gallery/full-bleed-strip·team/headshot-list·faq/categorized·lead/multi-field-card·pricing/comparison-table 등). 다음: 추가 NEED 커버리지 또는 신규 고객 needs 기반 조합.
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]] · [[push-before-deploy]]

### Growth-85 (2026-06-17) — 21st.dev 레퍼런스 6종 CDO triage → AgentPlan만 채택·process/split-animation 중화 구현(NEED→HAVE)

- **인격/Axis/Milestone**: CTO(triage 위임·1순위 범위 결정·비주얼검증·매트릭스 환류·triage 판정 박제·per-file 커밋·로깅) + CDO(6종 impeccable+Growth-69 triage·중화 스펙·accept1/backlog2/reject3 판정) + Engineer(ProcessSplitAnimation 구현·status 토큰 재활용·catalog/manifest 스레딩·한국어 4단계 태스크트리·테스트) + QA(4계층 게이트·불변식 5종·회귀) / **section-variant(frontend 축)** / M1(데모 다양화)
- **1줄 rollup**: 파운더가 드롭한 21st.dev 레퍼런스 6종(PixelLogoGrid/InkReveal/PixelPerfectHero/TableOfContents/Sparkles/AgentPlan)을 CDO 가 불변식 게이트로 triage — **AgentPlan 1종만 채택**해 `process/split-animation` 변형으로 중화 구현(원본 랜덤 상태토글 제거·read-only 고정 status·`<details open>` SSR fallback). A1 flux 데모에 한국어 4단계 태스크트리로 흡수. NEED 14→13. pytest 140, BUILD SUCCESS, 풀페이지 비주얼 검증 PASS, diagnose real-fail 0.
- **함정/교훈**: ① **레퍼런스 무비판 흡수 금지 — triage 가 사전 매핑을 뒤집음**: CTO 사전 가설은 InkReveal→scroll-reveal(△ 가능)·TableOfContents(○)였으나 CDO 가 둘 다 **reject**(InkReveal=Growth-69 위반 canvas 콘텐츠 소멸, TableOfContents=대응 섹션 type 없음), Sparkles=impeccable glow 위반. **교훈: 외부 디자인 자산은 불변식 게이트(Growth-69·impeccable·토큰)를 먼저 통과시키고 채택분만 누적** — [[official-skill-adoption-policy]] 의 "보완만 흡수, 중복·충돌 거부"와 동형. ② **theme-contract↔component gap 함정을 설계 단계에서 사전 차단(Growth-82~84 재발 방지)**: CDO 중화 스펙이 우리 테마에 없는 토큰(`--color-success/warning/danger/fg-*`)을 5-state status 로 썼으나, engineer 브리핑에 "신규 status 팔레트 발명 금지·3-state 축소·기존 토큰 매핑" 명시 → **신규 토큰 0**(text-2=completed/primary=active/text-3=upcoming + 아이콘 shape+aria-label 1차 구분). 갭이 런타임 대비실패로 터지기 전에 토큰 매핑을 위임 prompt 에서 못박은 것이 주효. ③ **Growth-69 정적 검증**: `<details open>` fallback 으로 nested subtask 최심부(스키마 자동 탐색 확인·번 레이트 알림 채널·초기 배포 드라이런)까지 dist HTML 정적 존재 grep 확인 — JS 없이 전체 태스크트리 가시.
- **누적 자산**: **process/split-animation 변형**(마케팅 read-only 중화 패턴 — 인터랙티브 agent-plan UI 를 정적 태스크트리로 변환하는 재사용 레시피) + process `item_slots` subtasks/status/tools 스키마 + **21st.dev 6종 triage 판정 박제**(matrix §4 — out/ 소멸 대비, 재심사·재논쟁 방지). backlog 누적: PixelPerfectHero→hero/pixel-canvas, PixelLogoGrid→logos/pixel-hover-grid(ACCEPT 보류).
- **상세**: [engineer ledger](docs/learn-logs/engineer.md) · [qa ledger](docs/learn-logs/qa.md) · [cdo triage](out/growth-85-triage/cdo-triage.md)(gitignored, 판정은 matrix §4 박제)
- **잔여(open)**: NEED 13종(hero/scroll-reveal·features/timeline-horizontal·gallery/full-bleed-strip·team/headshot-list·faq/categorized·lead/multi-field-card·pricing/comparison-table 등). 21st.dev backlog 2종(pixel-canvas·pixel-hover-grid) — 차기 Growth 후보. 다음: 추가 NEED 커버리지 또는 신규 고객 needs 조합.
- **결정 메모리**: [[marketing-site-track]] · [[official-skill-adoption-policy]] · [[feedback-pushback]]

### Growth-86 (2026-06-17) — 자체 GTM 랜딩 한국어화 + locale 전파 feature + aurora 한국어 디스플레이 폴백

- **인격/Axis/Milestone**: CTO(한글화 결정·CMO 카피 fold-in·locale 배선 설계·폰트 결함 발견·통합·per-file 커밋) + CMO(한국 B2B SaaS 보이스 한국어 카피 재작성·M1 게이팅 준수) + Engineer(site_manifest locale emit·BaseLayout html lang·dispatch 배선·TestLocaleEmit 5케이스) + CDO(aurora family-display 한국어 폴백·비주얼 검증·타 테마 갭 조사) + QA(4계층 게이트·회귀·규율 PASS) + DevOps(재배포·라이브 검증) / **frontend(locale feature)+theme(8축, 폰트)** / M1(리드젠 랜딩 한국 시장 정조준)
- **1줄 rollup**: 우리 자체 플래그십 M1 리드젠 랜딩(gtm-landing, LIVE)이 영어였던 모순 해소 — 전 섹션 카피·SEO 한국어(CMO), `defaults.locale ko-KR`. 부수로 **locale→manifest→`<html lang>` 전파 feature**(하드코딩 `lang="en"` 제거, profile 기반, 영문 데모는 en-US 기본 유지 — open-closed)와 **aurora `family-display` 한국어 시스템폰트 폴백**(헤드라인 글리프 폴백 결함, zero egress). pytest 145(신규 5), `<html lang="ko">` 확인, 비주얼 전 섹션 PASS, diagnose 신규 FAIL 0.
- **함정/교훈**: ① **"한글로 변경"은 카피 교체로 끝나지 않는다 — `<html lang>`·폰트 폴백까지가 진짜 한국어**: BaseLayout `lang="en"` 하드코딩 → 스크린리더 발음 오류·SEO 손실. 하드코딩 수정이 아니라 **profile→manifest→adapter locale 배선**으로 풀어 향후 한국 고객 전체에 누적(우리는 한국 회사 → 대부분 고객이 한국어). ② **빌드 green ≠ 시각적 정상(Growth-82 재확인)**: aurora `family-display`(Bricolage Grotesque)에 한국어 폴백 부재 → 한국어 헤드라인이 OS 임의 폰트로 폴백. body 스택의 한국어 폴백을 display 에 미러링(네트워크 폰트 ✗, self-host thesis 준수). ③ **CDN 폰트 유혹 거부**: 우리 랜딩이 "데이터 외부 반출 없음"을 파는데 한국 웹폰트 CDN @import 추가는 자가모순 → 시스템 폰트 폴백만.
- **누적 자산**: **locale 전파 feature**(marketing-site 어댑터 i18n 기반 — `defaults.locale`→`<html lang>` BCP-47 서브태그, 전 고객 재사용) + aurora 한국어 디스플레이 폴백 + 한국어 GTM 카피(out/gtm-landing/cmo-copy-ko.yaml).
- **상세**: [cdo visual verify](out/gtm-landing/cdo-visual-verify-ko.md) · [qa gate](out/gtm-landing/qa-gate-g86.md) · 커밋 bf0f1d9/9dea246/8797bb8/7a839fb/d4da06d(engineer) · 8d89ab1(cdo) · e623c2b(profile)
- **잔여(open)**: **타 테마 한국어 디스플레이 폴백 누락 3종**(kiln·studio·harvest) — 한국 회사로서 전 테마 동일 수정 필요, backlog. font CDN→fontsource M1 마이그레이션 미완. **모션 트랙(차기, 파운더 승인 방향)**: sanggong식 스크롤 스냅 풀스크린+IO 진입 모션 변형 자산화(progressive enhancement, Growth-69 유지) + "B급 professional" 상한 상향 검토 — 별도 Growth 스코핑 대기.
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]] · [[push-before-deploy]]

### Growth-87 (2026-06-17) — 모션 시스템(progressive-enhancement 스크롤 안무) + self-host 폰트 egress 제거

- **인격/Axis/Milestone**: CTO(블루프린트 박제·CDN egress 결함 적발·통합·per-file 커밋) + CDO(모션 토큰·subtle/rich 다이얼·IO-리빌 G-69 CSS·3변형 디자인·비주얼검증 JS-on/off) + Engineer(scroll-snap 셸·IO 디렉티브·3변형·profile schema·manifest·catalog·테스트12·egress @fontsource 이전) + QA(4계층·G-69·zero-egress·open-closed 게이트) / **frontend(motion feature)+theme(8축 모션토큰)+section-variant 3종** / M1(B급→A급 상한 상향, 한국 프로모션 랜딩 시장 정조준)
- **1줄 rollup**: 파운더가 sanggong.co.kr(한국 랜딩 웹에이전시: fullPage.js+AOS+GSAP)을 지목 → **효과를 클론 아닌 변형 자산으로 누적**. scroll-snap 풀스크린 셸 + IO 진입-리빌 디렉티브(vanilla, 라이브러리0) + 모션 토큰(`--motion-duration/ease/distance/stagger`) + `site.scroll_mode`/`site.motion`(off/subtle/rich) 다이얼 + 신규 변형 3종(hero/scroll-reveal·gallery/full-bleed-strip·stats/pinned-staged) 신설. gtm-landing 파일럿(snap+subtle, hero→scroll-reveal+stats/pinned-staged). 부수로 **Google Fonts CDN egress 제거**(IBM Plex/DM Mono @fontsource self-host) → 전 테마 zero-egress. pytest 380(신규12), 비주얼 JS-on/off PASS(G-69 픽셀 mean_diff=0), dist googleapis 0 hit.
- **함정/교훈**: ① **모션을 G-69와 충돌 없이 = "CSS 기본 가시, JS 있을 때만 애니메이션"**: AOS식 "기본 숨김→JS로 리빌"은 G-69 위반(JS off시 백지). 우리는 역전 — `html.motion-ready [data-reveal]:not(.in-view){opacity:0}` 로 **모션 CSS 전체를 JS-부여 클래스 뒤에 게이팅**. JS off → motion-ready 미부여 → 전부 가시(픽셀 실증 mean_diff=0). ② **"0 bits egress" 파는 랜딩이 Google Fonts를 호출하던 자가모순 적발**: global.css의 무조건 CDN `@import url(fonts.googleapis.com)`(Prism용 기존부채)가 aurora 페이지 dist에도 실려 우리 shopfront가 로드시 외부 호출 — DevTools로 즉시 들통날 신뢰 손상. @fontsource 이전으로 root-cause 제거(전 테마 이득). **교훈: 가치명제(self-host)는 구현 산출물까지 검증해야 — 빌드 dist grep로 egress 실증.** ③ **상한(B급)은 impeccable이 아니라 "모션·구성 부재"가 누름**: impeccable은 floor(유지), 모션이 ceiling lever. 다이얼(off/subtle/rich)로 같은 변형이 보수 B2B·프로모 동시 대응.
- **누적 자산**: **모션 시스템**(scroll-snap 셸 + IO 리빌 디렉티브 + 모션 토큰 + scroll_mode/motion 다이얼 — 전 고객/테마 재사용 i18n급 인프라) + 신규 변형 3종(hero/scroll-reveal·gallery/full-bleed-strip·stats/pinned-staged) + **전 테마 zero-egress 폰트**(self-host 완성). 설계: [motion-system](docs/architecture/motion-system.md).
- **상세**: [cdo spec](out/motion/cdo-motion-spec.md) · [cdo visual g87](out/motion/cdo-visual-verify-g87.md) · [qa gate g87](out/motion/qa-gate-g87.md) · 커밋 548ebc6/67bc620/577cf44/e9dc77f/1046dd3/9186c8d/786c439/2e6759d/2091096/1b823a2(engineer) · 3faf348(cdo 토큰) · ddc87d2/0e3be2e/9ea39f3(egress) · 771db63(블루프린트)
- **잔여(open)**: 변형명 불일치(스펙 pinned-staged vs class stats-pinned) 문서 동기화. gallery/full-bleed-strip은 파일럿 미노출(다음 데모에서 실증 권장). 타 테마 모션 옵트인 확산(현재 gtm-landing만). 타 테마 한국어 디스플레이 폴백 3종(kiln·studio·harvest, G-86 backlog). 모션 G-69 가드 정식화(G-16 후보).
- **결정 메모리**: [[marketing-site-track]] · [[feedback-pushback]] · [[push-before-deploy]]

### Growth-88 (2026-06-17) — rich-motion 파일럿 + 모션 다이얼 진짜 강도 레버화 (flux-demo, meridian)

- **인격/Axis/Milestone**: CTO(설계 결정·트랩 판정·도큐) + Engineer(BaseLayout 리팩터·CSS 토큰 확장·profile 편집·빌드 검증) + CDO(비주얼 회귀체크·snap/island 결함 적발) / **frontend(motion dial 완성)+theme(8축 rich 토큰)** / M1(기존 17개 섹션 카탈로그 전체 격상)
- **1줄 rollup**: 모션 다이얼이 "시스템 스위치"로 오배선돼 있던 것을 "강도 레버"로 통합 — off=레거시 `[data-motion]` 옵저버 단독 / subtle·rich=레거시+신규 `[data-reveal]` IO 슈퍼셋. `html[data-motion="rich"]` 가 `--animation-duration/--translate-y-from/--child-animation-duration` 등 레거시 keyframe vars 까지 스케일 → rich 가 기존 17개 섹션을 실제로 더 굵게 만든다. flux-demo·meridian 에 `motion: rich` 적용(둘 다 normal scroll).
- **함정/교훈**: ① **다이얼 오배선**: 레거시 `[data-motion]` 옵저버가 `else`(motion=off) 브랜치에만 있어 subtle/rich 로 전환 시 기존 애니메이션 소멸(순역행). BaseLayout 에서 레거시 옵저버를 always-load 로 빼고 신규 IO 를 additive — off 바이트 동일 유지. ② **snap+astro-island 함정**: `astro-island{display:contents}` 가 레이아웃 박스를 없애 `scroll-snap-align` 무효 → `.snap-root>astro-island{display:block;min-height:100dvh}` 로 시도했으나 gtm 의 짧은 섬(ProofMarquee3d·FeatureCarousel)을 100dvh 로 강제 → 라이브 flagship 에 ~1200px 공백 회귀. 되돌리고 flux 는 snap 포기·normal scroll 채택. ③ **CDO 회귀체크가 QA 구조게이트 PASS 한 라이브-결합 회귀를 포착** — "빌드 그린·구조 PASS ≠ 라이브 비주얼 무회귀"(Growth-82 규율 재확인). 라이브 사이트 건드리는 CSS 는 build-vs-live 픽셀 비교 필수.
- **누적 자산**: 모션 다이얼 완전 레버화(off/subtle/rich 전 레이어 일관); rich CSS 토큰 5종(`--animation-duration 640ms·--translate-y-from 40px·--child-animation-duration 580ms·--motion-distance -40px·--motion-stagger 110ms`); snap+island 한계 문서화.
- **백로그**: snap 모드는 top-level 섹션이 SSR(비-island)인 프로파일에서만 검증됨(gtm-landing). island-hero + snap 은 per-section opt-in 마커(`data-snap-panel`) 도입 후 지원.
- **커밋**: 782a6d1(BaseLayout) · 5b6d35c(rich 토큰 1차) · 9307f5a(flux scroll_mode:snap 추가) · 1faf503(meridian motion:rich) · 2b86ecb(레거시 dial 배선) · 215b274(snap/island 시도) · d8955a4(island 규칙 롤백) · aab9352(flux snap→normal)

### Growth-89 (2026-06-18) — 숨고 LG U+ 의뢰 거절·재프레임 + Lite 티어 자산화(ai-guide 섹션·bridge 테마) + §6 회전 8차

- **인격/Axis/Milestone**: CTO(시장판정·전략·통합·per-file 커밋·로깅) + CMO(입찰 카피) + CDO(ai-guide 섹션·bridge 테마·telecom seed·wiki 환류) / **theme/section(8축)**·customer / M1 GTM(SMB AI 기능성 웹 포지셔닝)
- **1줄 rollup**: 숨고 3번째 인바운드(LG U+ 판매점 고객유치 랜딩)는 순수 랜딩=레드오션·self-host 쐐기 死문이라 **거절**, 단 채택기준 "AI활용/창의성"을 지렛대로 *임베드 self-host AI(요금제추천·리드수집)* 재프레임 판정 → 그 구조를 [[product-two-tier-selfhost-ai]] **Lite 티어**(검색형 즉답 가이드, $0 API, embeddinggemma 입증)로 제품화. 카탈로그 최초 **기능성 섹션 `ai-guide`** + **bridge 테마**(warm-navy, SMB 리드젠 일반형) + telecom/SMB leadgen seed + wiki 환류(smb-ai-guide-lite). 10 파일당 커밋·푸시(f4e8684~f392922).
- **정직성 경계(신뢰영업)**: "API비 0"="제3자 종량 0"이지 운영비 0 아님(서버 실비)·클라우드 폴백 금지(쐐기 자가붕괴). Pro(생성형) 티어는 병렬사업 ✗ → 게이트된 R&D 스파이크.
- **§6 회전 8차**: Growth-54~67(14 엔트리) 원문수정 0으로 growth-archive.md 이동 + 포인터 갱신(G-9 242→PASS).
- **상세**: [[gtm-positioning-ai-functional]] · [[product-two-tier-selfhost-ai]] · [[marketing-site-track]]
- **Open loops**: deep-research(Verify 중) 결과 → 진입 use case 확정·bridge/seed 실수치 보강·engineer 후속(ai-guide 컴포넌트·로컬임베딩 사이드카·리드 POST·privacy strict·G-69 SSR)/Pro 스파이크 GO. 다음 §6 회전은 cap 재접근 시.

### Growth-90 (2026-06-19) — 법무법인 self-host RAG MVP 빌드 + CISO/QA 게이트 (M3 첫 vertical 착수)

- **인격/Axis/Milestone**: CTO(스코프확정·통합·게이트triage·.patched 검증·per-file 커밋) + DBA(스키마·augment SQL·BYPASSRLS) + Engineer(RAG엔진·JWT인증·테스트) + domain-expert-legal(seed·wiki환류) + PM(WTP킷) + CMO(포지셔닝) + CISO(보안게이트) + QA(풀테스트게이트) / **ddl(augment 신패턴)·middle(RAG)·expert-agent·business docs** / M3(규제업종 법무 첫 vertical)
- **1줄 rollup**: deep-research가 self-host=규제업종 법적필수로 검증한 창끝(법무법인)에 사내문서 RAG MVP 풀빌드. **검색+인용까지만·LLM 생성 0 → 환각0을 chunk.id PK 바인딩으로 구조적 보장**. augment 분리(neutral catalog + postgres overlay SQL)·하이브리드 검색(FTS+ANN+RRF)·RLS 6테이블·로컬 임베딩(클라우드0). 단위테스트 49→86. 커밋 6b0a8a1~2b6d4ee 푸시.
- **정직성/thesis**: 클라우드 폴백 코드경로 0(CISO·QA grep 실증) — "API비0+데이터유출0" 쐐기 구조적 보장. 임베딩 전용(텍스트 생성 아님). SearchResponse에 answer_text 없음.
- **게이트**: CISO CONDITIONAL GO(B-1 API인증부재·B-2 app_service BYPASSRLS) + QA CONDITIONAL PASS(Gap-1 RLS격리·Gap-2 ingest·Gap-3 source실존) → 전부 수정·재검증(86 passed/1 skip). L2/L4+RLS통합 라이브는 Postgres+사이드카 필요 → #8 인프라 게이트.
- **함정/교훈**: ① **서브에이전트 cwd≠repo root → 상대경로 훅 깨짐**: 2개 에이전트 `.patched` 섀도파일·stub훅 폴백 → "0 tests collected" 회귀. 훅 `${CLAUDE_PROJECT_DIR}`화(메인 활성, settings.json 미커밋)·.patched 직접 diff검증으로 복구([[subagent-cwd-hook-fragility]]). ② **서브에이전트 "83 passed" 거짓**: 인증·Gap-3가 비활성 .patched라 미적용 — 활성파일 적용 후 86. 에이전트 "통과" 주장은 직접 재검증 필수.
- **누적 자산**: **axis-2 augment 패턴**(neutral catalog + dialect overlay SQL, 의료/금융 일반화 가능) · legal RAG 서비스 `services/legal-rag/`(JWT/서비스토큰 인증·path-traversal 가드) · seed(판례22·사건12·문서15·데모3 가명) · WTP킷·포지셔닝 · wiki 2p([[legal-rag-mvp-build]]).
- **Open loops**: #5 검색·인용 UI(engineer+CDO) · #8 self-host 런북+데모배포(devops — L2/L4/RLS통합 라이브검증, 운영가이드 DSN·EMBED_URL내부망·query_text암호화(Pro)·TLS 반영) · WTP 인터뷰 3~5곳(PM). DBA가 커밋 아티팩트에 "Growth-48" 오기(실제 90) — 사소, 추후 정정. settings.json `${CLAUDE_PROJECT_DIR}` 커밋 여부 founder 판단.
- **결정 메모리**: [[legal-rag-mvp-build]] · [[gtm-positioning-ai-functional]] · [[subagent-cwd-hook-fragility]]

### Growth-91 (2026-06-19) — 법무 RAG #5 검색·인용 UI + 최소 실제 로그인 (M3 vertical 계속)

- **인격/Axis/Milestone**: CTO(스코프갈림길 결정·코디네이션·CISO triage·per-file 커밋) + DBA(legal_attorney 테이블·FK·RLS·seed 해시) + CDO(ui-spec·tokens/app.css·클래스규약) + Engineer(/auth/login·/cases·vanilla SPA) + CISO(증분표면 집중게이트) / **ddl(legal-attorney)·frontend(vanilla web)·design** / M3
- **1줄 rollup**: #5 UI. `/search`가 JWT 요구하나 발급경로 부재 → founder "최소 실제 로그인" 선택. legal_attorney(bcrypt) + `/auth/login`(app_service 조회→verify→JWT mint) + `/cases`(rls_session 자동격리+ingest 집계) + vanilla SPA(로그인/검색/사건현황, FastAPI StaticFiles). 로그인만으로 RLS 격리(이준호 vs 박서연) 라이브 시연. 단위테스트 86→114.
- **정직성/thesis**: 생성형 답변 영역 0(검색+인용 도구 — 시각언어 정직). 외부 CDN/폰트 0(시스템 한글폰트, self-host). user 관리 = 전 법무법인 재사용 자산(복리).
- **게이트**: CISO 증분표면 CONDITIONAL GO. XSS VERIFIED(서버데이터 textContent/createTextNode만, innerHTML 직조립 0)·JWT(HS256핀·alg=none차단)·로깅(평문비번0)·CORS PASS. 즉시수정 2건: `_DUMMY_HASH` 60바이트 무효→ValueError로 타이밍가드 무력화(유효해시 교체·checkpw=False 실증) · seed 평문 `demo1234!` 주석 제거. rate-limit/health제한/docs는 #8 이월.
- **함정/교훈**: cwd-hook 함정([[subagent-cwd-hook-fragility]]) 재발 0 — 에이전트에 절대경로·`.patched` 금지 명시 선반영. 진단 노이즈(root-context Pyright의 config 모듈 미해석 → jwt_secret/ingest_root "unknown")는 false positive로 식별, 활성 pytest(114)로 실검증.
- **누적 자산**: legal_attorney 테이블+RLS · `/auth/login`·`/cases` 엔드포인트 · vanilla 법무 web UI(`services/legal-rag/web/`) · CDO 법무 디자인 토큰(`design/legal-rag/ui-spec.md`). 커밋 91c67e4~a1ee5da(15 파일 per-file).
- **Open loops**: #8 self-host 런북+데모배포(devops — L2/L4/RLS 라이브검증 + 운영하드닝, CISO 이월분 rate-limit/docs비활성 포함) · WTP 인터뷰 3~5곳(PM). settings.json `${CLAUDE_PROJECT_DIR}` 커밋 여부 founder 판단(미해결).
- **결정 메모리**: [[legal-rag-mvp-build]]

### Growth-92 (2026-06-19) — 법무 RAG #8 self-host 설치 런북 + CISO 이월 하드닝 클로즈 (M3 vertical)

- **인격/Axis/Milestone**: CTO(병렬 wave 코디·문서-코드 불일치 검증·CISO 게이트·per-file 커밋) + DevOps(설치 런북·README 정리·운영 하드닝 7항목) + Engineer(LEGAL_RAG_ENV·/health 분리·prod docs 비활성·하드닝 테스트) + CISO(이월 클로즈 증분게이트) / **creater(런북)·backend(하드닝)** / M3
- **1줄 rollup**: #8 devops 빌드. `docs/runbooks/legal-rag-install.md` 단일 설치 런북(사전요건→PG/pgvector/pg_bigm→DDL+seed→사이드카→기동→하드닝7→데모자격→라이브검증→트러블슈팅). CISO #5 이월 3건 코드/인프라 클로즈. 단위테스트 114→121.
- **정직성/thesis**: 추가 고정 infra 비용 0(기존 단일 VPS Coolify 컨테이너 추가). 실 인프라 필요 단계 전부 [FOUNDER GATE] 명시 — DevOps 인격이 자격증명 없이 임의 배포·시크릿 노출 시도 차단(정직한 경계).
- **게이트**: CISO 증분 CONDITIONAL GO(BLOCK/HIGH 0). 이월 3건 CLOSED — (a) rate-limit=Traefik 미들웨어 5req/min(앱 무의존), (b) /health shallow{status:ok}+/health/detail(X-Service-Token), (c) LEGAL_RAG_ENV=prod 시 docs/redoc/openapi 비활성. 잔존 LOW 2건(배포시 Traefik 라우터 라벨 dead-router 확인·nosymfollow remount 절차)은 founder 배포게이트로.
- **함정/교훈**: 서브에이전트 산출물의 문서-코드 불일치를 커밋 전 실코드 대조로 차단 — 런북 ENV 기본값 `prod`→실제 `dev`, /health "DB핑 수행" 서술→실제 분리됨, LoginResponse 필드 `access_token` 확인. Pyright 가짜양성(config.py:89 env누락·test 미정의변수)은 pytest 121 실측·env='dev' 출력으로 반증. `.patched` 재발 0.
- **누적 자산**: self-host 설치 런북(전 법무법인 재사용) · LEGAL_RAG_ENV prod 토글 · /health/detail 인증분리 패턴 · 하드닝 단위테스트 7종. 커밋 ae13529~a051cef(6 파일 per-file).
- **Open loops**: #8 실 배포·라이브검증(L2/L4/RLS pytest -m postgres) = founder 인프라 게이트 잔존 · WTP 인터뷰 3~5곳(PM). settings.json `${CLAUDE_PROJECT_DIR}` 커밋 여부 founder 판단(미해결).
- **결정 메모리**: [[legal-rag-mvp-build]]

### Growth-93 (2026-06-19) — 법무 RAG 배포차단 B1/B2 클로즈: 앱 Dockerfile + 임베딩 어댑터(TEI/e5) (M3 vertical)

- **인격/Axis/Milestone**: CTO(임베딩 백엔드 결정·caller-split 검증→비대칭 프리픽스 교정·stale Pyright 반증·per-file 커밋) + Engineer(app Dockerfile·embed-adapter shim·compose 실이미지 배선) / **backend(서비스)·creater(compose)** / M3
- **1줄 rollup**: B1 `services/legal-rag/Dockerfile`(python:3.11-slim·비루트·uvicorn) + B2 `services/legal-rag/embed-adapter/`(TEI `intfloat/multilingual-e5-base` 768-dim 래핑 thin FastAPI, embed_client.py 계약 바이트일치, 11 테스트) + B3 compose busybox placeholder→실 embed+tei 서비스 배선. 폐기된 embeddinggemma(공개이미지 없음) 대체.
- **정직성/thesis**: 로컬·클라우드API비0·768 thesis 유지(TEI 로컬 CPU 서빙, 외부호출 0). 실 배포(시크릿볼트·DDL적용·DNS·Coolify)는 전부 [FOUNDER GATE] — engineer는 빌드 산출물만, 자격증명 무접근.
- **함정/교훈**: e5 비대칭성 자유획득 — caller 사용처 1방향 분리 검증(`api.py:154` embed()=검색쿼리, `ingest.py:289` embed_batch()=인제스트 패시지)으로 엔드포인트가 query/passage를 인코딩 → `/embed`="query: "·`/embed/batch`="passage: " 계약변경0으로 풀 검색품질 회복(첫 시도의 대칭 haircut 교정). 진단 stale 식별: Pyright가 편집前 스냅샷 기준 EMBED_PREFIX 미정의·prefix 인자누락 3건 플래그 → 실파일 read로 161/179행 `prefix=` 명시 확인, false. `.patched` 재발 0.
- **누적 자산**: 앱 컨테이너 Dockerfile · 재사용 embed-adapter(TEI shim, 전 벡터검색 버티컬 재사용) · 비대칭 프리픽스 caller-split 불변식(코드리뷰 가드) · preview compose 3→4컨테이너(db+embed+tei+app). 커밋 3faf8c7~cc0908d(10 파일 per-file).
- **Open loops**: 비대칭 프리픽스 선택 QA/domain-expert 사인오프(인제스트 개시 前) · 실 배포·라이브검증(pytest -m postgres) = founder 인프라 게이트 · WTP 인터뷰 3~5곳(PM). TEI 첫부팅 모델다운로드(~1.1GB) start_period 모니터.
- **결정 메모리**: [[legal-rag-mvp-build]]

### Growth-94 (2026-06-19) — 법무 RAG 실 VPS LIVE: TEI→로컬모델 피벗 + 베이스 스키마 갭 해소 + DDL 적용 도구 (M3 vertical)

- **인격/Axis/Milestone**: CTO(라이브 배포 트러블슈팅 통합·TEI 버그 분리진단→피벗 결정·env 함정 5종 순차해결·베이스 스키마 출처 갭 해소·적용체인 정적 의존성 검증·per-file 커밋) + Engineer(embed-adapter TEI→sentence-transformers 재작성) + DBA(pg_bigm graceful-degrade 가드) + DevOps(apply-schema.sh 원샷·런북 정합) / **backend(embed)·ddl(augment 가드)·creater(apply script)** / M3
- **1줄 rollup**: 법무 RAG 가 `legal-rag.n9n.co.kr` 3컨테이너(db+embed+app) LIVE. TEI cpu-1.5 Rust hf-hub `relative URL without a base` 버그 VPS 실증 → embed-adapter 로컬 sentence-transformers(e5-base 768, 이미지 bake, `HF_HUB_OFFLINE=1`) 단일컨테이너 피벗(4→3). 베이스 스키마 갭 해소: `render.py --entities` 4 legal-entity 스코프 → hr_employee FK 오염 0. pg_bigm 가드(auto-degrade). DDL 원샷 `apply-schema.sh`. 런북 stale 4구간 정합.
- **정직성/thesis**: 외부유출0·월API비0 유지(로컬 추론, 외부SaaS 0). 실 배포·DDL적용·시크릿주입 전부 [FOUNDER GATE] — CTO 자격증명 무접근. 시크릿 평문 미기록(env 함정도 founder 가 Coolify 패널에서 수정, 스크립트는 trust-auth docker exec 무암호). 평문 시크릿+외부 Supabase DSN 박힌 stray `.yaml.md` 발견 즉시 차단·삭제·rotate 권고.
- **게이트/검증**: 적용체인 정적 의존성 검증 PASS — 순서(base→01→02~07→08→seed)·RLS 가 미존재 legal_attorney 테이블 무참조(컬럼/롤/세션변수만)·seed FK 링크(attorney UUID 001/002 존재)·행수(attorneys3/cases12/precedents22/parties29/docs15). 로컬 docker 데몬 부재로 dry-run 불가 → 정적검증 + `ON_ERROR_STOP=1` 라이브 가드 + seed 멱등 가드로 대체. G-87 PASS.
- **함정/교훈**: (1) TEI 버그 오인 차단 — standalone 실행 로그로 Rust 다운로더 버그(relative URL)임을 분리, CPU 정상임을 확정 후 피벗. (2) **베이스 스키마 출처 갭** — DDL 런북 서브에이전트가 미존재 `legal-rag` 프로파일 대신 `lawfirm-demo` 렌더(HR 테이블 오염 + `assigned_attorney_id→hr_employee` FK) + 지어낸 scp 키 + grep 밴드에이드 제시 → CTO 가 머지前 차단. 정답=`render.py` 4-entity 스코프(스코프밖 FK 자동 omit, `render.py:render_fk:274 target not in entities → None`), grep 0. (3) env 함정 5종(외부 Supabase DSN·POSTGRES_USER 공백→healthcheck `pg_isready -U ` 깨짐·DSN `<PLACEHOLDER>` 잔존·패스워드 재사용·필수시크릿 공백→app crash-loop→Coolify rollback) 을 라이브 로그로 순차 진단. (4) pg_bigm: grep 스트립 밴드에이드 대신 `pg_available_extensions`/`pg_extension` 가드 DO블록 → 같은 파일이 pgvector-only(preview, plainto_tsquery 폴백)·pg_bigm설치(production, 풀 bigram) 양쪽 동작(복리).
- **누적 자산**: 로컬모델 embed-adapter(외부SaaS 0, 전 벡터검색 버티컬 재사용) · pg_bigm graceful-degrade 가드(전 self-host 재사용) · `render.py` 스코프 렌더 베이스 패턴(타도메인 FK 오염 차단) · `deploy/preview/legal-rag.apply-schema.sh` 원샷 도구(컨테이너/유저 자동탐색·base렌더·검증, 전 법무법인 재사용) · 런북 §4-bis(docker-exec 경로)·§5(로컬모델) 정합. 커밋 853fdf9~b0e578d(피벗+가드+도구, per-file). 이 세션분 af4beac~b0e578d(6 파일).
- **Open loops**: B5 실 적용 — founder 가 VPS 호스트(브라우저 터미널)에서 `apply-schema.sh` 실행 후 라이브검증(curl /health 200·로그인 e2e 이준호/박서연 demo1234!·pytest -m postgres·app restart 로 pool reconnect) = founder VPS 게이트 잔존. WTP 인터뷰 3~5곳(PM). settings.json `${CLAUDE_PROJECT_DIR}` 커밋 여부 founder 판단(미해결).
- **결정 메모리**: [[legal-rag-mvp-build]]

### Growth-95 (2026-06-20) — 법무 RAG 라이브 검증 패스: 잠복결함 3종 발현·수정 (RLS 격리 BLOCK 포함), M3 격리 확정

- **인격/Axis/Milestone**: CTO(라이브 검증 주도·결함 진단·정적↔실측 대조·결함 라우팅·per-file 커밋) + Engineer(db.py SET LOCAL ROLE app_user) + DBA(09_grants 최소권한) + DevOps(apply-schema base 멱등 가드) + CISO(RLS fix 인도게이트 리뷰) / **ddl(grants)·backend(db.py)·creater(apply script)** / M3
- **1줄 rollup**: 실 VPS DDL+seed 적용 후 founder 라이브 검증이 **pytest -m postgres 인프라게이트로 미뤘던 영역의 잠복결함 3종**을 발현·수정: (a) seed PK 무효 UUID(`p…`/`doc…` 의 p·o 가 non-hex)→`f…`/`d0c…` (b) base 멱등결함(render.py plain `CREATE TABLE`)→`to_regclass` 존재가드 (c) **RLS 격리 누수 BLOCK** — app 이 app_service(=POSTGRES_USER 부트스트랩 슈퍼유저, rolsuper=t)로 접속해 `rls_session` 이 `SET ROLE` 누락 → RLS 통째 우회 → 박서연(002)이 12건 전부 봄. 수정: db.py `SET LOCAL ROLE app_user`(트랜잭션 강등) + 09_grants(app_user 권한 0→최소 SELECT/INSERT). **박서연6/이준호12 라이브 검증 통과 → 격리 확정.**
- **정직성/thesis**: RLS 변호사간 격리 = 법무 제품 핵심 보안 보장. **실측(박서연6/이준호12)으로만 검증 인정** — 단위테스트(mock DB)가 통과해도 실 RLS 격리는 미보장임이 실증됨(이전 게이트의 맹점). 시크릿/평문 무기록. app_service 슈퍼유저는 preview 한정(production 하드닝 별도).
- **함정/교훈**: (1) **게이트 갭** — 이전 CISO CONDITIONAL GO(Growth-90~92)가 이 BLOCK 을 통과시킨 원인 = RLS 격리 통합테스트를 인프라게이트로 이연·미실행. **RLS 보유 버티컬의 CISO 인도게이트는 반드시 live(또는 pytest -m postgres) cross-tenant 격리 단언을 포함**(mock 단위 불충분). security-loop SKILL 반영 권장. (2) seed 무효 UUID·base 멱등결함은 실 postgres 첫 적용까지 잠복 — L2(JDBC/HSQLDB)가 postgres-specific 결함을 못 잡음. (3) render.py plain CREATE TABLE → 적용 도구는 테이블존재 가드 필수. (4) 셸: `demo1234!` 의 `!` 가 bash 히스토리 확장(`event not found`) 유발 → `set +H` 또는 single-quote. (5) 부분-seed 후 attorney=3 가드가 reseed 스킵 = 가드 맹점 → TRUNCATE 후 재적용으로 회복.
- **누적 자산**: **RLS role-drop 패턴**(`SET LOCAL ROLE app_user` in rls_session — 전 RLS 버티컬 재사용) · 09_grants 최소권한 템플릿(legal_attorney 제외=credential 격리) · apply-schema `to_regclass` base 멱등 가드 + seed-skip 가드 · seed UUID hex 교정. 커밋 853fdf9~6cbab8d(이 검증패스: seed fixes·db.py·09_grants·apply-schema·runbook, per-file).
- **Open loops**: CISO RLS fix 인도게이트 결과 반영(백그라운드 진행) · **G-88 신설 권장**(seed SQL 무효 UUID 리터럴 가드, `diagnose.py`) · security-loop 에 live RLS 격리단언 게이트 추가 · 데모문서 **ingest**(§4-4, 청크+벡터)로 `/search` 전체 RAG 검증(현재 chunk 0) · production app_service 비-슈퍼유저 하드닝 · WTP 인터뷰 3~5곳(PM).
- **결정 메모리**: [[legal-rag-mvp-build]]

### Growth-96 (2026-06-20) — 법무 RAG 데모 ingest → /search 전체 RAG + 청크계층 RLS 격리 라이브 확정, M3 DEMO-READY

- **인격/Axis/Milestone**: CTO(검증 시나리오 설계·결함 진단·정적↔실측 대조·라우팅·per-file 커밋) + DevOps(ingest-demo·verify-search 원샷 스크립트) + Engineer(psycopg3 executemany 커서 수정 + 테스트 mock 교정) / **creater(스크립트)·backend(ingest.py)·middle(검증)** / M3
- **1줄 rollup**: 데모문서 3종 ingest(12청크)→ hybrid `/search` 가 랭킹청크+인용 반환 + **검색 계층 RLS 격리** 라이브 검증 완료. 라이브 ingest 가 잠복결함 2종 발현·수정: (a) `docker exec` 에 **`-i` 누락** → 컨테이너 `python - <<PY` heredoc 의 stdin 미연결 → 빈 실행·exit0(무출력, 청크0) (b) **psycopg3 `executemany` 는 connection 아닌 cursor 메서드**(`AttributeError`) — mock 이 속성 자동생성해 단위테스트가 은폐. 검증 3단언 전부 PASS: **[A]** 이준호→c001 청크5(의미검색 정확 랭킹) **[B]** 박서연 동일쿼리→c001 **0건**·c012만(검색계층 격리 실증) **[C]** 박서연→c012 청크4(본인사건 가시).
- **정직성/thesis**: **chunk-level RLS**(검색 결과 청크까지 변호사별 격리)는 case-level(`/cases` 목록)과 별개 보장 — 이번에 비로소 실측. Growth-95 가 목록격리였다면 Growth-96 은 검색격리. 시크릿 무기록(service token 컨테이너 env 에서 런타임 read·미echo, demo1234! 는 런북 §8 문서화된 데모전용 리터럴로 python heredoc 내부에만).
- **함정/교훈**: (1) `docker exec` 로 heredoc 파이프 시 **`-i` 필수**(apply-schema 엔 있었으나 신규 스크립트가 누락 — stdin 없으면 `python -` 가 빈 입력 읽고 조용히 exit0). (2) **psycopg3 함정**: `executemany`=cursor 전용, connection 엔 `execute` 단축만 존재(psycopg2→3 마이그레이션 전형). **mock 의 속성 자동생성이 실 API 불일치를 은폐** → Growth-95 "mock 불충분" 재확인: C2(pytest -m postgres)가 이 결함+uuid+RLS 를 한 게이트에서 잡았을 것. (3) 라이브 ingest 가 벗긴 결함은 전부 "실 PG/실 컨테이너 첫 쓰기"에서만 발현 — 정적·mock 불가시. (4) **진단 우선 확정**: text→uuid 가설을 traceback 으로 반증 후 수정 → 비싼 앱 리빌드 1회로 수렴(blind-fix 회피).
- **누적 자산**: **ingest-demo.sh**(컨테이너 자동탐색·문서복사→ingest마운트·서비스토큰 런타임read·`if !` set-e-safe·청크검증) + **verify-search.sh**(2변호사 로그인·A/B/C 격리단언·`!` history-expansion 을 python heredoc 으로 봉인) — 전 법무 데모/설치 재사용 · `cursor.executemany` 패턴 · **`.gitattributes` LF 가드**(`*.sh`/`*.sql` — Windows 재저장發 CRLF 가 VPS 실행 깨는 것 차단) · runbook §4-4(실 UUID 매핑표)·§4-5(검증 절차) 배선. 커밋 59cbbb1~1c83517(per-file).
- **Open loops**: **C2 강화**(pytest -m postgres 통합테스트 — executemany+uuid바인딩+RLS격리 동시 커버, 이번 2결함을 인프라게이트 전에 잡는 단일 게이트) · production app_service 비-슈퍼유저 하드닝(C1) · G-88(seed UUID 가드) · WTP 인터뷰 3~5곳(PM) · `legal_document_chunk` 데모데이터는 컨테이너 재생성 시 ingest-demo 재실행 필요.
- **결정 메모리**: [[legal-rag-mvp-build]]

### Growth-97 (2026-06-20) — 법무 RAG 브라우저 데모 라이브: `/app` SPA 화면전환 복구(`[hidden]` CSS 결함), M3 비전문 구매자 시연 가능 (M3 vertical)
- **1줄 rollup**: 이미 빌드돼 있던 SPA(`web/`, `/app` 마운트, 로그인+검색+사건현황+인용카드+접근성)가 1개 CSS 결함으로 화면전환 불능 → 1줄로 복구해 **브라우저 데모 라이브**. founder Redeploy 후 로그인→검색 전환·A/B 격리 화면시연 확인.
- **근본원인/교훈**: SPA 가 화면·패널·배너 가시성을 HTML `hidden` 속성(`el.hidden=...`)으로 토글하는데 `app.css` 에 전역 `[hidden]` 리셋이 없어, `.login-wrapper`/`.app-root` 의 `display:flex`(author)가 UA `[hidden]{display:none}` 을 덮어 **`hidden` 속성이 무력화**(author cascade > UA). `showScreen()`/패널 토글이 "에러 없이 전환만 안 됨" 증상. 픽스: `[hidden]{display:none !important}` 전역 1줄(normalize.css 표준) — 화면+모든 `.hidden` 토글 일괄 복구. **교훈: author `display` 클래스가 하나라도 있으면 `[hidden]` 전역 리셋은 필수(빠지면 정적·단위테스트 불가시, 브라우저 실행에서만 발현)**.
- **정직성**: 오늘 새 UI 빌드 없음 — CDO 가 이미 빌드해 둔 자산의 막힌 데를 뚫음. 진단은 정적으로 확정(JS 정상 → CSS cascade 위반) 후 design-agent(CDO) 에 1줄 위임, CDO 스킬 자가환류. web/ 는 이미지 bake-in → 적용에 Redeploy 필요(git pull 불충분), 브라우저 CSS 캐시는 강력새로고침으로 무효화.
- **누적 자산**: runbook §4-6(브라우저 데모 경로 `/app` + `[hidden]` 함정노트) · 커밋 cafea04(per-file).
- **Open loops**: 내일 founder 질문 예정 — 관련도(`rrf_score`)·청크 의미·조절 방법(top_k·청크 토큰타깃·RRF k·하이브리드 가중치). [[legal-rag-mvp-build]]

### Growth-98 (2026-06-20) — 법무 통합 제품 D1~D5 페르소나 드래프팅 + DFD 게이트 false-positive 2단 검증 (M3 vertical)
- **1줄 rollup**: `docs/projects/legal/README.md` 골격의 D1~D5 슬롯을 4 페르소나 3-wave 오케스트레이션으로 산출 — D1 기능명세(PM, F-01~F-22+NFR22), D2 유저플로우(PM, 4플로우+screen inventory S-01~S-17), D3 와이어프레임(CDO, 16뷰+theme `legal-pro` 권고), D4 ERD(DBA, 8엔티티/10관계), D5 DFD(DBA P1~P25 + QA §9 검증게이트 21단언). 각 페르소나 envelope-only 반환(subagent-output-protocol)으로 main context 보호.
- **근본원인/교훈**: QA 가 DFD 게이트에서 I-1(임베딩 `passage:`/`query:` prefix 미적용 → BLK-1 merge BLOCK)을 founder 보고 직전까지 올렸으나, **CTO 독립 소스검증 결과 false positive**. prefix 는 메인 `embed_client.py`(thin wrapper, raw text 의도된 전달)가 아니라 **embed-adapter 사이드카**(`embed-adapter/app.py`: `/embed`→query·`/embed/batch`→passage, `_embed_local()` 적용, 불변식 테스트 `test_adapter.py` 보유)가 적용. 호출부 정합(ingest=batch/passage, search=single/query)이며 caller-split 은 **기존 정적 가드 G-87 으로 이미 보호**. QA 가 사이드카+G-87 둘 다 미열람. **교훈: 서브에이전트의 결함 판정(특히 cross-service/사이드카 경계)은 founder-facing 보고 전 CTO 독립검증 필수 — thin wrapper 만 보고 결함 단정 금지**. [[subagent-cross-service-verify]]
- **정직성**: 라이브 검색 prefix·rrf_score 품질 정상 확정(메모리 legal-rag "LIVE·동작" 유효, 품질 미달 아님). 새 코드 0 — 문서 산출 + 거짓 BLOCK 정정만. D5 §9.1/9.2/9.4/9.5 + README §3/§7 의 BLK-1 표기를 "철회(false positive)" 로 일괄 정정.
- **누적 자산**: D1~D5 정식 standalone 문서 5종(`docs/projects/legal/D{1..5}-*.md`) — §2 3중용도(영업·인도물·구현입력). DFD 게이트 = 코드 前 설계검증 + CTO 독립검증 2단 프로세스 패턴 확립.
- **Open loops**: BLOCK 아닌 triage 갭 — 엔드포인트 G-1~G-6(D2), 성능 I-2(FTS+ANN 병렬화), 데이터모델(polymorphic FK·keywords 1NF), 열린질문 Q-1(사건 CRUD 범위)/Q-3(query_text 평문 PIPA). 다음: adapter/theme `legal-pro` 구현 패스. [[legal-unified-product-docs]] [[legal-rag-mvp-build]]
