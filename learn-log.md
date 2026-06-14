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

> **아카이브**: Growth-4 ~ Growth-12 의 slim 엔트리는 [docs/learn-logs/growth-archive.md](docs/learn-logs/growth-archive.md) 로 이동 (Growth-20, G-9 cap 운영). 회전 정책: slim §6 는 최근 시기 Growth 만 유지, cap 접근 시 오래된 엔트리를 원문 그대로 아카이브로 이동.

> Growth-13 ~ Growth-15 (Growth-34 회전) · Growth-16 ~ Growth-20 (Growth-37 회전) · Growth-21 ~ Growth-32 (Growth-59 회전) · Growth-33 ~ Growth-48 (Growth-64 회전) 은 `growth-archive.md` 로 이동. 검색: `python scripts/ledger-index.py --symbol <name>` 또는 인격 ledger pointer.

### Growth-49 (2026-06-13) — Capacitor axis-4 어댑터 스캐폴드 + PWA Phase 1 완료

- **인격/Axis/Milestone**: CTO (설계) / frontend axis-4 pluggable / M2 — App Store/Play Store 제출 경로 확보
- **Why (1줄)**: PWA가 완성됐으나 iOS App Store는 PWA 배포 불가 → Capacitor native shell이 기존 코드 재작성 없이 스토어 등록 경로를 열어줌
- **작업**: `frontend/adapters/capacitor/` 신설 (capacitor.config.ts — remote server mode, package.json, README, .gitignore). Phase 1 = 기존 `https://edu-program.n9n.co.kr` live URL wrap; Phase 2 = local bundle + native 플러그인. React Native는 M3-M4 유료 고객 퍼포먼스 불만 시점으로 이연. frontend/adapters/INDEX.md capacitor row 추가.
- **커밋**: (이후 별도)
- **교훈 (1줄)**: Capacitor server mode는 웹 코드 변경 없이 스토어 제출 가능 — 단, iOS WebView는 WKWebView 정책(CORS, CSP)이 브라우저보다 엄격하므로 HTTPS + 동일 도메인 API 필수
- **Revenue/cost**: LLM=없음 / infra 변경 없음 / App Store 등록 → M2 고객 확보 접점 확대
- **Open loops**: Capacitor android/ ios/ 플랫폼 추가 (npm install 후) / App Store 아이콘·빌드 서명 / 5개 industry demo Coolify 배포 / Supabase adapter 구현

### Growth-50 (2026-06-13) — 5개 산업 M2 데모 프로필 스캐폴드

- **인격/Axis/Milestone**: CTO (설계) + CMO (데모 포트폴리오) / customer 축 / M2 — 숨고·크몽 영업용 데모 포트폴리오 구축
- **Why (1줄)**: 잠재 고객이 "우리 업종에 맞는 기능이 있나?" 를 바로 확인할 수 있는 산업별 데모가 없으면 전환율 저하 → 5개 데모 프로필로 영업 접점 다각화
- **작업**: `profiles/` 신규 5개 — logistics-demo(물류), distribution-demo(도매유통), construction-demo(건설시공), itservice-demo(IT에이전시), trading-demo(무역수출입). 각 프로필: catalog.yaml 실존 entity만 사용, feedback_url=intake.n9n.co.kr, status=draft. 커밋 5건.
- **커밋**: d8cb723→33fea3c→7b9e39d→aaad26d→28a3449
- **교훈 (1줄)**: 14 baseline domain이 충분히 포괄적이라 5개 산업 중 vertical agent 추가 없이 100% 커버 가능 — manufacturing만 production/quality 도메인 추가 시 vertical 필요
- **Revenue/cost**: LLM=없음 / infra 변경 없음(배포 미완) / 5개 데모 → M2 영업 채널 준비 완료
- **Open loops**: manufacturing-demo 추가(smallmfg-demo 보완) / 5개 데모 seed data 추가 / Supabase adapter 구현

### Growth-51 (2026-06-13) — 5개 산업 데모 + 포털 Coolify 배포 완료

- **인격/Axis/Milestone**: CTO (오케스트레이션) + DevOps / customer 축 / M2 — 숨고·크몽 영업용 데모 포트폴리오 라이브
- **Why (1줄)**: 잠재 고객이 "우리 업종 맞나?" 를 직접 확인할 수 있는 라이브 데모가 없으면 문의 전환율 0% → 6개 URL 동시 오픈으로 업종별 영업 채널 확보
- **작업**: demo-portal (nginx, demo.n9n.co.kr) + 5개 산업 데모 각 Coolify app + 서브도메인 + TLS. in-memory 스토어라 DB 설정 불필요. deploy_to_coolify.py cp949 UnicodeEncodeError 근본 수정 (stdout/stderr reconfigure UTF-8). scaffold.py 동일 수정.
- **커밋**: 426f9a2 ~ 3d4b9db (compose 5 + portal 3 + deploy-fix 2 + scaffold-fix 1)
- **교훈 (1줄)**: FastAPI 어댑터가 in-memory 스토어 → 데모에 DB 불필요. seed JSON 만 있으면 사전 데이터 주입 가능 — 향후 업종별 seed 추가로 "빈 화면" 해소 가능
- **Revenue/cost**: LLM=없음 / VPS 컨테이너 6개 추가 (nginx 1 + fastapi+flask 10) / 데모 포트폴리오 → M2 고객 접점 완성
- **Open loops**: 5개 데모 seed data (빈 화면 개선) / manufacturing-demo 추가 / Supabase adapter 구현 / demo-portal 중복 project 정리(Coolify UI)
### Growth-52 (2026-06-13) — demo.n9n.co.kr 도메인 충돌 수정 + edu-demo 카드 추가

- **인격/Axis/Milestone**: CTO (버그수정) / customer 축 / M2 — 데모 포트폴리오 완성
- **Why (1줄)**: force_domain_override 로 demo.n9n.co.kr 이 edu-program 에도 연결되어 포털 대신 edu-program/home 이 노출 → 즉시 수정
- **작업**: Coolify API PATCH로 edu-program 도메인 edu-program.n9n.co.kr 단독 복구 + 재배포. demo-portal HTML에 edu-demo(대학·교육기관) 6번째 카드 추가. 6개 업종 포털 완성.
- **커밋**: acee3eb
- **교훈 (1줄)**: Coolify force_domain_override 는 대상 앱만 패치하지 않고 기존 앱 도메인도 덮어쓰지 않는다 — 수동 복구 필요
- **Revenue/cost**: LLM=없음 / 재배포 1회 / demo.n9n.co.kr 정상화 → 고객 체험 6개 업종 완비
- **Open loops**: 5개 데모 seed data / manufacturing-demo / Supabase adapter
### Growth-53 (2026-06-13) — 6개 데모 seed data 내장 + 배포

- **인격/Axis/Milestone**: CTO+Engineer / backend 축 / M2 — 데모 품질 향상
- **Why (1줄)**: 데모 앱 빈 화면은 고객 체험 품질을 저하 → 업종별 현실적 샘플 데이터로 즉시 개선
- **작업**: seed-data/{slug}.json 6개 생성(한국 업종 현실 데이터). Dockerfile COPY seed-data/ 추가. 6개 compose SEED_FILE 환경변수 추가. 전체 재배포 HTTP 200 확인.
- **커밋**: 257d1a4~8f6d53d (13 커밋)
- **교훈 (1줄)**: seed data를 repo에 번들하면 서버 SCP 없이 이미지 빌드 시 자동 포함 — bind-mount보다 단순
- **Revenue/cost**: LLM=없음 / 재배포 6회 / 데모 품질 향상 → 영업 접점 강화
- **Open loops**: manufacturing-demo 추가 / Coolify stale app 정리 / Supabase adapter
### Growth-54 (2026-06-13) — manufacturing-demo 추가 + catalog 확장

- **인격/Axis/Milestone**: CTO+Engineer / customer·ddl 축 / M2 — 데모 포트폴리오 7업종
- **Why (1줄)**: 제조업은 국내 SMB 최대 업종 — 포트폴리오 공백 최우선 해소
- **작업**: profiles/manufacturing-demo.yaml (5 도메인, 18 엔티티). catalog.yaml에 production-plan·production-result·ncr 3개 신규 엔티티 추가. seed-data 97레코드. portal 7번째 카드. deploy + HTTP 200.
- **커밋**: d816ff2~17f18da (5 커밋)
- **교훈 (1줄)**: deploy_to_coolify.py는 미커밋 파일이 있으면 compose_raw 로드 실패 — 커밋·푸시 먼저, 배포 나중
- **Revenue/cost**: LLM=없음 / 재배포 2회 / 데모 포트폴리오 7업종 완비
- **Open loops**: Coolify stale app 정리 / Supabase adapter

### Growth-55 (2026-06-13) — Coolify stale app 정리

- **인격/Axis/Milestone**: CTO (infra) / — / M2 — 운영 위생
- **Why (1줄)**: Growth-51 배포 당시 demo-portal이 중복 생성됨 — stale app + 빈 project 제거로 Coolify UI 정리
- **작업**: DELETE /applications/gwdizi7tws4yabv25xnbph0w (HTTP 200). DELETE /projects/xngfun8b14dchdujcwl3898c (HTTP 200). active app s6872cr0asfp02sc0vgw8wi2 생존 확인.
- **커밋**: HANDOFF+learn-log 업데이트만 (코드 변경 없음)
- **Revenue/cost**: LLM=없음 / API 호출 5회 / 운영 부채 해소
- **Open loops**: Supabase adapter

### Growth-56 (2026-06-13) — manifest 디렉터리 버그 수정 + 6개 demo 화면 복구

- **인격/Axis/Milestone**: CTO+Engineer / creater 축 / M2 — 데모 품질
- **Why (1줄)**: 6개 demo app에서 화면이 비어있는 원인이 screen-manifest.json이 파일 아닌 디렉터리로 bind-mount된 버그였음
- **근본원인**: Docker bind-mount race — 컨테이너가 SCP 전에 기동되면 source 경로에 빈 디렉터리 생성. SCP가 그 안에 파일을 넣어 mount가 깨짐. edu-program만 정상이었던 이유: 이전에 별도 SCP 경로로 파일이 이미 있었음.
- **작업**: 서버에서 6개 slug manifest 디렉터리→파일로 수정 (cp→rm→mv). 컨테이너 restart. deploy_to_coolify.py에 SCP 전 `rm -rf {remote_manifest}` 가드 추가.
- **커밋**: 3e9250a (deploy_to_coolify.py fix)
- **교훈 (1줄)**: SCP 대상이 이미 디렉터리면 파일로 덮어쓰지 않고 그 안에 들어간다 — SCP 전 rm -rf 필수
- **Revenue/cost**: LLM=없음 / restart 6회 / 데모 품질 복구
- **Open loops**: Supabase adapter

### Growth-57 (2026-06-13) — 데모 3종 결함 일괄 수정 (화면 공백·계정 표기·테이블 가독성)

- **인격/Axis/Milestone**: CTO+Engineer / frontend·creater 축 / M2 — 데모 품질
- **Why (1줄)**: 고객 향 데모에서 화면 공백·잘못된 로그인 안내·검정 위 검정 글자 3종 동시 발견 — 영업 신뢰도 직결
- **#1 화면 공백**: construction/itservice 컨테이너가 Growth-56 manifest fix 이전(10:38) 생성분이라 stale 디렉터리 inode를 계속 마운트. Coolify `restart`는 컨테이너 recreate 안 함 → `start?force=true`(재clone+recreate)로 해결. 교훈: bind-mount inode 교체엔 restart 부족, force deploy 필요.
- **#2 계정 표기**: portal 카드 8곳 admin/demo1234 → demo/demo (실제 auth.py _DEMO_USERS=demo/demo와 불일치 해소).
- **#3 테이블 가독성**: Pico v2 classless가 prefers-color-scheme:dark 자동감지 → 홀수 row 다크 배경 + td 텍스트(#111827) 겹쳐 검정 위 검정. base.html `data-theme="light"` 강제 + master-table zebra 명시 토큰(odd=surface-1/even=surface-2) 이중 방어. edu(public-sector, Pico 미사용)는 무영향이라 정상이었음.
- **커밋**: f0c1acb(portal) 91f1919(base.html) 267a0b7(app.css)
- **교훈 (1줄)**: 디자인이 라이트 전용이면 <html data-theme="light"> 명시 — Pico/브라우저 다크모드 자동적용이 토큰과 충돌
- **Revenue/cost**: LLM=없음 / force deploy 8회 / 데모 3종 결함 제거
- **Open loops**: Supabase adapter

### Growth-58 (2026-06-13) — Supabase backend adapter (PostgREST) 구현

- **인격/Axis/Milestone**: Engineer (구현) + CTO (seam 설계) / backend 축 / M3 — SaaS 전제(hosted PG)
- **1줄 rollup**: fastapi adapter ZERO-TOUCH, `sys.modules["store"]` 주입 seam으로 공유 라우터 재사용 + PostgREST store만 교체. 16 유닛테스트 green, L4 live 보류(Supabase 프로젝트 미프로비저닝). 커밋 5af6921~6aa0698 (8개).
- **상세**: [engineer ledger Growth-58](docs/learn-logs/engineer.md)
- **Open loops**: L4 live / GoTrue auth / PostgREST pushdown · ~~G-9 §6 200줄 초과~~ → Growth-59 해소

### Growth-59 (2026-06-14) — §6 슬림 회전 4차: Growth-21~32 아카이브 (G-9 FAIL→PASS)

- **인격/Axis/Milestone**: CTO (integrator 유지보수) / 헌장 운영 (§6 회전 정책) / 전 milestone 공통
- **1줄 rollup**: G-9 FAIL(275>200) → Growth-21~32 (12 엔트리, 109 비-blank행) 원문 수정 0으로 [growth-archive.md] 이동 + 그룹 포인터 1줄 갱신. 회전 후 166행 PASS (34행 헤드룸). Growth-20 회전 정책 4번째 적용 (4~12·13~15·16~20 에 이어).
- **상세**: 본 엔트리로 충분 (메커니컬 회전 — Growth-20 정책 그대로). 검색: `ledger-index.py --symbol <name>`
- **결정 (CTO Auto)**: 오래된 것부터 contiguous 이동 (rotation 정책 불변), founding 1~3 은 divider 앞 유지. cut point = Growth-33 (최근 26 엔트리 슬림 유지)
- **Open loops**: 없음 — 다음 회전은 cap 재접근 시

### Growth-60 (2026-06-14) — G-8 가드에 Apple `@Nx` 레티나 에셋 면제 추가

- **인격/Axis/Milestone**: CTO (가드 정밀화) / creater (diagnose.py G-8) / M2 — Capacitor iOS 어댑터 호환
- **1줄 rollup**: Capacitor iOS `AppIcon-512@2x.png` 의 `@` 가 G-8 오탐 → 삭제(빌드 깨짐) 대신 가드 면제. `_APPLE_ASSET_NAME` (`@[123]x(~idiom)?`) AND `*.xcassets` 조상 디렉터리 **이중 게이트** — 그 밖의 `@`·비-ASCII(한글 등)는 여전히 FAIL. negative test 6 케이스 확인. G-8 PASS (621 entries).
- **상세**: 본 엔트리로 충분. §2 G-8 카탈로그 행 갱신
- **결정 (CTO Auto)**: 면제 범위 = `.xcassets` 번들 내부로 한정 (전체 ios 디렉터리 제외 ✗ — 번들 안 진짜 위반 은폐 방지). 코드 generator 버그 아님 (Growth-59 후속의 `${slug}` 와 달리 정당한 Apple 관습)
- **Open loops**: 없음

### Growth-61 (2026-06-14) — G-13 해소: research-loop SKILL 출력 규약 링크 추가

- **인격/Axis/Milestone**: CTO (가드 해소) / creater (research-loop SKILL) / 전 milestone 공통
- **1줄 rollup**: research-loop `## 출력 규약` 에 `subagent-output-protocol.md` 링크 누락 → security-loop 관용구대로 envelope §4 문장 + 링크 추가. G-13 PASS (9 loops). 전 가드 0 FAIL (11 PASS / 2 SPEC).
- **상세**: 본 엔트리로 충분. 링크 타깃 존재 확인, `../../../` depth 다른 loop 와 동일
- **결정 (CTO Auto)**: 기존 `## 출력 규약` 섹션에 링크만 보강 (재작성 ✗) — 최소 임팩트
- **Open loops**: 없음 — 코드 가드 전부 green

### Growth-62 (2026-06-14) — 자율 고객 intake 파이프라인: 파운더 릴레이 제거 + 적격 정책 + needs-fit 게이트

- **인격**: PM (intake 파이프 설계) + CTO (integrator·아키텍처 확정)
- **Axis touched**: customer (intake→profile 자동화)·creater (파이프라인 스크립트·가드)·헌장 (charter v1.7·pm-delivery-loop SKILL)
- **Milestone**: M2 — 첫 고객 전환율 개선 (파운더 릴레이 병목 제거)
- **Revenue/cost**: gap-registry(미충족 리드) → Growth 신호 누적, stall 리드 → cost-report 환류 / 문서화 세션 소량
- **Why (1줄)**: 제출→preview까지 파운더 수동 릴레이 제거; 적격(score≥55·고감도 플래그 없음)→자동, gap=성장 ToDo, audit trail, needs-fit(codex) 게이트, UI 자동체크, pipeline monitor(G-14 SPEC)
- **상세**: [pm.md](docs/learn-logs/pm.md)
- **결정**: CEO+CTO 합의 (v2 ultraplan 반영). Step 5 외부 인도 게이트 불변(CEO 단독, charter §2)
- **Open loops**: P1~P6·P8 코드 구현 (engineer) / G-14 SPEC→PASS (cases/ 첫 엔트리 후)
- **후속 (동일 스레드, 상세 [pm.md](docs/learn-logs/pm.md))**: deploy·ui_check `--entry-path`(`/health` 권위화), monitor·G-14 latest-terminal-wins, needs-fit codex 패스 정식화(`record-verdict` loop closer), playwright 설치, 첫 풀-배포 리허설 — autonomous 배포 3 버그(cp949 child stdout·미커밋 compose·entry-path) 발견·수정, 라이브 200 검증 후 회수

### Growth-63 (2026-06-14) — Pipeline 장애 대응 웹 대시보드 (localhost·LLM 0·PII-free)

- **인격/Axis/Milestone**: Engineer (구현) + CTO (설계·integrator) / creater (Phase 8 모니터) / M2 — 장애 대응 속도
- **1줄 rollup**: CLI 모니터 위 `pipeline_dashboard.py`(127.0.0.1·stdlib·LLM 0) — Incidents triage·노드 칩·실패 drill-in(권장액션+owner+SLA+inline evidence+codex 프롬프트). monitor 투영 재사용(병렬 스토어 ✗), `DEFECT_ACTIONS` 단일 진실 + `aggregate_health` 빈-cases 버그픽스. 111 PASS·가드 0 FAIL. 커밋 `d031800`~`cc810a6`.
- **상세**: [engineer ledger Growth-63](docs/learn-logs/engineer.md)
- **Open loops**: 외부/원격 접속 미결([[todo-external-pipeline-monitor]], 명시 요청 시에만) / 기본 포트 8787 은 HEADROOM 점유 → `--port` 우회

### Growth-64 (2026-06-14) — HANDOFF 오픈루프 3건 완료 (P2 Capacitor·P1 외부모니터·P3 Supabase L4 준비) + §6 5차 회전

- **인격/Axis/Milestone**: CTO (open-loop 종결·integrator) + DevOps (P1 런북, 위임) / frontend·creater·backend 축 / M2~M3
- **P2 (완전 완료)**: Capacitor 어댑터 CLI 8 ↔ core 6 major 불일치 해소 — 전 의존성 `^8.0.0` 정렬, v8 재설치·android 재생성·`cap sync` 검증("Android looking great", assets dir 복구). iOS native 는 Windows 빌드 불가로 생략(macOS 에서 `add:ios`). 커밋물=package.json+package-lock(나머지 gitignored). `672c110`,`a609aef`
- **P1 (스캐폴드 완료, 활성화는 파운더)**: 외부 모니터링 = Cloudflare Tunnel+Access 경로. 런북 `docs/runbooks/external-pipeline-monitor.md` + config 템플릿 + `serve_dashboard.ps1` 런처. 로컬 Windows 대시보드(127.0.0.1:8790) 아웃바운드 노출, 이메일 OTP(파운더 단독), VPS 무관여·PII-free·인바운드 0·월 $0. 인터랙티브(login·Access 앱)는 파운더 몫. `e07fda8`~`15e72b1`
- **P3 (코드 검증·턴키 준비, live 는 파운더)**: Supabase 어댑터 unit 16 PASS 재확인(MockTransport, 네트워크 0). L4 live 는 Supabase 프로젝트 프로비저닝(인터랙티브) 하드블록 → env 템플릿 `infra/secrets/supabase.env.example` + README "L4 Live Activation" 5단계 턴키화. `044445a`,`a5012f9`
- **§6 회전 5차**: G-9 헤드룸 1행 → Growth-33~48(84 non-blank행) 원문수정 0 으로 [growth-archive.md] 이동 + 포인터 갱신. (Growth-20 정책 5번째)
- **Open loops**: ~~P1 cloudflared 활성화~~ → **2026-06-15 LIVE 검증 완료** / ~~P3 L4 smoke~~ → **2026-06-14 L4 PASS** (둘 다 아래 후속). 잔여: P3 GoTrue auth·PostgREST pushdown (M5)
- **후속 (P1 LIVE, 2026-06-15)**: cloudflared 설치+터널 `pipeline-monitor`(e572d631) 생성·DNS·config·Access(OTP, founder 단독) 구성 → `https://pipeline.n9n.co.kr` 엔드투엔드 OTP 로그인 검증. 부팅자동 = cloudflared **Windows 서비스** + 대시보드 **작업 스케줄러 `PipelineDashboard`**(AtLogOn). 기존 n8n 터널 2개와 별개. 시크릿 gitignored. 상세 메모리 [[todo-external-pipeline-monitor]]
- **후속 (P3 Supabase L4 LIVE, 2026-06-14)**: 파운더가 Supabase Free 프로젝트 프로비저닝 → `smoke_test` 테이블 + 볼트 env(`infra/secrets/supabase.env`, gitignored) → `SupabaseEntityStore` create/find/patch/delete + slug→table fallback 실 PostgREST 왕복 **10/10 PASS** (id/created_at/updated_at Postgres populate 확인). Growth-58 L4 오픈루프 종결. README 상태 → L4 live-verified. 비용 $0(Free).

### Growth-65 (2026-06-15) — marketing-site deliverable track 신설 (visual-asset 8번째 축)

- **인격/Axis/Milestone**: CTO(설계·통합·contract 판정) + Engineer(구현) + CDO(테마) / **theme(8번째 축 신설)**·frontend·creater·intake / M1 GTM~M3 (웹에이전시형 신규 고객층)
- **1줄 rollup**: `stack.deliverable_kind` 분기로 marketing-site track 신설 — site-manifest 스키마+scaffold 분기(P1)·테마 라이브러리 aurora/studio+모션8+섹션카탈로그8(P2)·landing-astro(Astro+Tailwind SSG) 어댑터(P3)·vision-QA 게이트 G-15(P4)·intake deliverable_kind 분기+answer→site 매핑(P5). 결정론 codegen 의 비주얼 약점을 **누적 테마 축**으로 전환, B급 professional 자동화. 빌드 SUCCESS·테스트 79(adapter)+76(intake)+14(vision) PASS·diagnose 15가드 0 FAIL.
- **핵심 결정**: 별도 repo ✗(substrate 공유) / 품질 바 **B(professional SMB)**, 부티크 아트디렉션 A 비채택 / 폰트 self-host(Fontsource, CDN 금지) / 연락폼 신규 wire key ✗ → `entity.create`(entity_type=lead) 재사용(open-closed) / 테마 default→aurora flagship.
- **상세**: [engineer ledger](docs/learn-logs/engineer.md) · [CDO ledger](docs/learn-logs/cdo.md) · [pm ledger](docs/learn-logs/pm.md)
- **Open loops**: dogfood(우리 M1 GTM 랜딩) 미빌드 / vision-QA live 채점·테마 레퍼런스샷(첫 인도 시 CDO+QA) / toggle-annual pricing·carousel JS(후속 Growth) / vision-verdict.json 스키마 공식화
- **결정 메모리**: [[marketing-site-track]]
