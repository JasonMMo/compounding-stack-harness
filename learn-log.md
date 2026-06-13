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
| **G-8** | 파일/디렉터리명에 비-ASCII 또는 unsafe 문자 | CLAUDE.md §10 | `scripts/diagnose.py::g8_ascii_slug` (PASS) |
| **G-9** | main §6 슬림 엔트리가 본문 10행 초과 또는 슬림 §6 200행 초과 | Growth-4 charter | `scripts/diagnose.py::g9_main_log_slim` (PASS, Growth-5a 박힘) |
| **G-10** | ddl catalog 무결성 — seed entity ⊄ catalog / dangling FK / 비-closed-set 타입 | Growth-10 | `scripts/diagnose.py::g10_ddl_catalog_integrity` (PASS, Growth-10 — 56 entity, seed⊆catalog, dangling FK 0, type closed-set) |
| **G-11** | creater orchestrator(`scripts/workflow/*.py`)가 catalog 파싱을 render.py 위임 없이 재선언 | Growth-14 | `scripts/diagnose.py::g11_creater_catalog_single_source` (PASS, Growth-14 — scaffold.py+manifest.py 모두 `load_catalog` import 경유, 로컬 재선언 0) |
| **G-12** | catalog 의 `*_id` 컬럼(PK 제외)이 `fk:` 블록도 `fk-exempt:` 마커도 없음 (silent dangling) | Growth-15 | `scripts/diagnose.py::g12_catalog_fk_hygiene` (PASS, Growth-15 — 79 *_id 스캔. polymorphic/circular 6 + backlog 2 는 fk-exempt 마커, customer_id 는 fk 연결) |
| **G-13** | 인격 loop SKILL(`*-loop/SKILL.md`)이 subagent-output-protocol.md 링크 없음 (반환 경계 드리프트) | Growth-34 | `scripts/diagnose.py::g13_subagent_output_protocol_wired` (PASS, Growth-34 — Growth-33 규약 hardening. 7 loop 스캔, 헤딩 문구 무관·프로토콜 링크 존재만 검사. envelope 크기는 런타임 속성이라 정적 검사 불가, 규약 wiring 만 가드) |

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

> Growth-13 ~ Growth-15 (Growth-34 회전) · Growth-16 ~ Growth-20 (Growth-37 회전) 은 `growth-archive.md` 로 이동. 검색: `python scripts/ledger-index.py --symbol <name>` 또는 인격 ledger pointer.

### Growth-21 (2026-06-11) — 전 인격 실행 절차 skill 화 (5 loop) + knowledge-sync hook

- **인격**: CTO (5 loop skill 작성 + agent 정의서 연결) + Engineer (knowledge_sync hook)
- **Axis touched**: creater (hook 스크립트 + 프로젝트 settings), 헌장 운영 (전 인격 절차 명문화)
- **Milestone**: 전 milestone 공통 (인격 산출 일관성) — PM 패턴 (Growth-18) 의 전 인격 확장
- **Revenue/cost**: hook 0 LLM (컨텍스트 주입만) / loop 당 지식 검색 1~2 turn 증분
- **Why (1줄)**: PM 만 role+skill 분리였고 나머지 5 인격은 정의서만 — 절차·지식 저장소 활용 비명문 + 지식 변경이 skill 에 반영되지 않는 drift 갭 (CEO 지시 2건)
- **상세**: [cto.md#Growth-21](docs/learn-logs/cto.md), [engineer.md#Growth-21](docs/learn-logs/engineer.md)
- **결정 (CTO)**: role 정의서 = *누가/무엇을*, skill = *어떻게/순서* (engineer/qa/marketing/design/domain-expert 5 loop) / 공통 지식 프로토콜 = **시작-검색, 종료-환류** (단일 진실 `knowledge/wiki/README.md`, skill 은 role-특화 포인트만 — DRY) / hook 은 LLM 이 아니므로 skill 직접 수정 대신 **additionalContext 점검 주입** 방식
- **Open loops**: hook 실가동 첫 검증 (다음 지식 변경 시) / CTO integrator 절차 skill 화 여부 (main session 특성상 보류)

### Growth-22 (2026-06-11) — 지식 연계 점검 — 실행 불가 절차 등 3갭 해소 + hook 첫 실가동 검증

- **인격**: CTO (integrator 점검·tools 보강·커버리지 지도) + Engineer (hook ⑤ 항목)
- **Axis touched**: 헌장 운영 (agent tools), creater (hook 체크리스트)
- **Milestone**: 전 milestone 공통 — Growth-21 산출물의 유기 연계 사후 검증 (CEO 지시)
- **Revenue/cost**: 0 LLM 런타임 / 0 infra
- **Why (1줄)**: loop skill 이 지시하는 검색 명령을 4 인격 (pm/cmo/cdo/expert) 이 실행할 수 없었음 (Bash 부재) — 절차와 실행 권한의 불일치 등 연계 갭 3건
- **상세**: [cto.md#Growth-22](docs/learn-logs/cto.md), engineer 커밋 6792efd
- **결정 (CTO)**: ① 4 인격 tools 에 Bash 추가 (qmd·ledger-index 실행 가능화) ② hook 체크리스트 ⑤ `qmd update` (stale 인덱스가 "사례 없음" 거짓 판정 유발 방지) ③ 검색 커버리지 지도 (wiki README — main 원장은 qmd 밖, ledger-index 담당 명시) / **hook 첫 실가동 자기검증**: 본 점검 중 README Edit 에 hook 발화 + ⑤ 포함 확인
- **Open loops**: 없음

### Growth-23 (2026-06-11) — 지식관리 사용자 가이드 + PM 첫 가동 (인터뷰 시트)

- **인격**: CTO (사용자 가이드) + **PM 첫 가동** (인터뷰 시트 + profile 2건 역분석)
- **Axis touched**: 없음 (코드 0) — 가이드 문서 + PM 영업 준비 자산
- **Milestone**: M2 (인터뷰 시트 = 첫 고객 loop step 1 준비물, lead → needs 전환 도구)
- **Revenue/cost**: PM 1 가동 (~\$1) / infra 0
- **Why (1줄)**: 지식관리 체계 (Growth-18~22) 가 도구 6종+규약으로 분산돼 진입 가이드 부재 + PM Initial Task 5 (시트) 가 M2 첫 접촉 전 준비물
- **상세**: [pm.md#Growth-23](docs/learn-logs/pm.md), 가이드 [`docs/guides/knowledge-management-guide.md`](docs/guides/knowledge-management-guide.md)
- **결정 (CTO)**: 가이드는 CEO 비전문 사용 기준 (mermaid 순환 다이어그램 + 검색 결정트리 + 역할별 사용법). 시트는 PM 인격이 자기 skill 따라 작성 (첫 가동) — 질문마다 "이 답이 채우는 profile 칸" 명시, 페르소나당 15분
- **PM 역분석 발견**: needs 크기 = 도메인 선택 수 (2~4) / escalation notes 가 미래 needs 프로브 근거 / auth·locale·billing 은 기능 아닌 조직 레이어 (IT·CEO 인터뷰가 각각 채움)
- **Open loops**: 시트 실전 검증 (M2 첫 인터뷰) / FAQ 위치 신설 (첫 고객 질문 시)

### Growth-24 (2026-06-11) — M3 첫 vertical: legal (법무법인 30명 시나리오)

- **인격**: CTO (설계·A안 확정·honest-promise) + PM (loop #1 시나리오 회전)
- **Axis touched**: expert-agent (domain-expert-legal 신설), skill (legal seed 2종), ddl (catalog legal 4 entity), customer (lawfirm-demo profile), knowledge (wiki 6 페이지 + index)
- **Milestone**: M3 (첫 vertical 착수 — legal)
- **Revenue/cost**: M3 per-agent SaaS 매출 트리거 후보 / wiki 6 페이지 (~\$0.5) / infra 0
- **Why (1줄)**: PM loop #1 첫 시나리오 — 법무법인 업무담당자의 "사건·판례 AI 검색 + 전략 수립" needs → A안(augment) 채택·B안(자동 생성) scope 제외로 honest-promise 원칙 준수
- **상세**: [pm.md#Growth-24](docs/learn-logs/pm.md), [cto.md#Growth-24](docs/learn-logs/cto.md)
- **결정 (CTO)**: A안 = tsvector 1단계 + RAG 2단계, 전략 생성 0 (Growth-17 vaporware 교훈 직접 적용). catalog legal 4 entity(legal-case/precedent/case-party/case-document). wiki dangling 1개(`legal-rag-pattern`) — RAG 설계 완료 시 채움
- **Open loops**: RAG 어댑터 설계 (CTO→engineer) / lawfirm-demo CEO 인터뷰 (A2 예산·A5 보안) / `legal-rag-pattern` wiki 페이지 (RAG 확정 후)

### Growth-25 (2026-06-11) — A안 법무 vertical 전체 구현 (tsvector 검색 + 화면)

- **인격**: CTO (A안 설계 확정) + Engineer (4 파일 신규·2 수정, 49 테스트 PASS)
- **Axis touched**: backend (fastapi legal router + tsvector FTS), frontend (vanilla-htmx /legal/search), creater (setup_lawfirm.py DB 초기화)
- **Milestone**: M3 — legal vertical L4 가동 가능 상태
- **Revenue/cost**: M3 per-agent 매출 트리거 완성 / Engineer 1 round / postgres 로컬 infra
- **Why (1줄)**: Growth-24 A안 설계 → 즉시 구현 — tsvector 1단계 완성, RAG 2단계는 escalation backlog
- **상세**: [cto.md](docs/learn-logs/cto.md), engineer 커밋 `9290b1a..05b259b`
- **결정 (Engineer)**: `DATABASE_URL` 미설정 시 200+warning graceful fallback (dev 환경 gate-free), `'simple'` 사전 (pg_bigm 없이 prefix 매칭)
- **Open loops**: ~~postgres 실가동 확인 (L4)~~ ✅ Growth-26 에서 완료 / RAG 2단계 / CEO 인터뷰 (A2·A5) / `legal-rag-pattern` wiki

### Growth-26 (2026-06-11) — L4 live 통과 + DDL 의존성 순서 버그 픽스

- **인격**: CTO (L4 검증·버그 탐색) + Engineer (render.py·scaffold.py 픽스)
- **Axis touched**: creater (scaffold.py emit_ddl 단일 호출·topo-sort 수정), ddl (render.py --entities 복수 플래그 추가)
- **Milestone**: M3 — legal vertical L4 완전 통과 (acceptance criteria 달성)
- **Revenue/cost**: M3 트리거 완성 증거 확보 / Engineer 1 round
- **Why (1줄)**: Growth-25 이후 postgres 설치·연결 디버깅 → L4 PASS 5/5 확인, scaffold DDL 생성 순서 버그(entity별 단독 render → topo-sort 무력화) 발견 및 픽스
- **결정 (CTO)**: scaffold.py `emit_ddl`을 per-entity subprocess 루프→단일 `--entities` 호출로 교체 (render.py 위상 정렬을 올바르게 활용)
- **Open loops**: RAG 2단계 / CEO 인터뷰 (A2·A5) / `legal-rag-pattern` wiki

### Growth-27 (2026-06-11) — L4 무개입화: .env + preflight + dotenv 자동 로딩

- **인격**: CTO (설계·결정) + Engineer (구현)
- **Axis touched**: creater (`scripts/preflight.py` 신설), backend (fastapi/main.py dotenv), demo (setup_lawfirm.py dotenv)
- **Milestone**: M2 — 고객 self-host 재현성 향상 (개입 없이 L4 재현 가능)
- **Why (1줄)**: Growth-26 에서 PostgreSQL 설치·자격증명·DATABASE_URL export 등 사용자 5회 개입 → 재발 방지를 위해 `.env` 로딩 자동화 + `preflight.py` 사전 점검 도입
- **결정 (CTO)**: `.env` (gitignored) + `.env.example` (committed) 패턴 채택; dotenv 미설치 시 graceful skip; preflight exit-0 == Claude 무개입 L4 진행 가능
- **Open loops**: RAG 2단계 / CEO 인터뷰 (A2·A5) / `legal-rag-pattern` wiki / Docker Compose (DB 설치 의존성 제거, 별도 Growth)

### Growth-28 (2026-06-11) — Docker Compose 로 DB 설치 의존 제거

- **인격**: CTO (설계·결정) + Engineer (구현)
- **Axis touched**: creater (preflight.py 자가복구 안내), infra (docker-compose.yml 신설)
- **Milestone**: M2 — 고객 self-host 온보딩 단순화 (`docker compose up -d` 한 줄)
- **Why (1줄)**: Growth-27 이 자격증명·env 개입을 제거했지만 "PostgreSQL 수동 설치" 자체가 남은 마지막 개입 지점 → compose 한 장으로 봉합
- **결정 (CTO)**: postgres:16-alpine 단일 서비스 + .env 변수 주입 + healthcheck; preflight 실패 메시지가 곧 복구 명령이 되도록 설계
- **한계 (정직)**: 이 호스트는 docker 미설치 — YAML 파싱 검증 + preflight 회귀 (기존 WSL postgres ALL PASS) 까지만. compose 실가동은 docker 보유 환경에서 1회 검증 필요
- **Open loops**: RAG 2단계 / CEO 인터뷰 (A2·A5) / `legal-rag-pattern` wiki / ~~compose 실가동 검증 (docker 환경)~~ → Growth-29 에서 닫힘

### Growth-29 (2026-06-11) — compose 실가동 검증 PASS + subset FK 누출 버그 픽스

- **인격**: CTO (검증·버그 판정) + Engineer (render.py 픽스·회귀 테스트)
- **Axis touched**: infra (compose 실가동 첫 검증), ddl (render.py subset FK omission 픽스), creater (preflight/setup_lawfirm cp949 픽스)
- **Milestone**: M2 — self-host 온보딩 경로가 진짜 fresh 환경에서 무개입 PASS 입증
- **Why (1줄)**: Docker 설치 후 Growth-28 open loop 닫기 — `down -v` fresh volume 에서 setup → preflight ALL PASS → L4 스모크 (`손해배상` 2건) 전 과정 무개입 PASS (docker 29.5.3 / compose v5.1.4)
- **버그 (fresh DB 가 잡음)**: render.py 가 subset 밖 entity (`hr_position`·`crm_contact`) 로의 FK 를 inline `REFERENCES` 로 방출 → fresh DB 에서 CREATE TABLE 연쇄 실패. 기존 WSL DB 는 과거 작업의 잔존 테이블이 버그를 **은폐** (Growth-26 L4 PASS 가 이 위에 서 있었음). 픽스 = `render_table` 에 `all_entities` 대신 `subset` 전달 + deferred ALTER 에 owner/target subset 가드. 헤더의 "omitted" 주석이 이제 구현과 일치.
- **교훈 (1줄)**: "이미 데이터 있는 DB 에서의 PASS" 는 DDL self-containment 를 증명하지 않는다 — fresh-DB 검증을 회귀 테스트로 고정 (`TestSubsetFkOmission`, 27/27 green)
- **부수 픽스**: preflight.py·setup_lawfirm.py 가 PowerShell 기본 콘솔 (cp949) 에서 UnicodeEncodeError 로 죽던 것 → stdout/stderr UTF-8 reconfigure (무개입 원칙: `-X utf8` 수동 플래그도 개입이다)
- **Revenue/cost**: M2 온보딩 신뢰성 / LLM 비용 0 (코드·테스트만)
- **Open loops**: RAG 2단계 / CEO 인터뷰 (A2·A5) / `legal-rag-pattern` wiki / PM loop Step 5 Deliver

### Growth-30 (2026-06-11) — L2 게이트 재가동: 테스트 데이터 FK 어긋남 픽스 → 48/48 PASS

- **인격**: CTO (원인 판정) + QA (L2 게이트 소유) + Engineer (픽스)
- **Axis touched**: ddl (L2 풀테스트 게이트 복구)
- **Milestone**: M2 — 4계층 풀테스트 중 L2 가동 상태 복귀 (Verification Matrix L2 PASS)
- **Why (1줄)**: CEO 가 L2HsqldbSmokeTest.java 의 `crm_contact` 검토 요청 → 실행해 보니 BLOCK (43/3): S1-20 이 존재하지 않는 contact `'cust-001'` 을 참조 (시드는 `'con-001'` 뿐) — S1-21·OD3 연쇄 실패
- **원인**: Growth-10 작성 당시 `sales-order.customer_id` 에 FK 없음 → Growth-15 (G-12 catalog FK hygiene) 가 `customer_id → contact` FK 추가하면서 테스트 데이터가 어긋남. L2 는 상시 실행이 아니라 (Matrix NOT_SETUP) 조용히 깨져 있었음
- **픽스**: `'cust-001'` → `'con-001'` 2곳 (S1-20, OD3-setup) → 48/48 PASS, raw schema load 무패치 통과 (Growth-26 topo 픽스가 HSQLDB 전체 catalog 에서도 유효함을 함께 입증)
- **교훈 (1줄)**: catalog 에 FK 를 추가하는 변경 (G-12 류) 은 L2 테스트 데이터도 함께 회귀시켜야 한다 — 게이트가 안 돌면 어긋남은 침묵한다
- **Revenue/cost**: 풀테스트 게이트 신뢰성 / LLM 비용 0
- **Open loops**: RAG 2단계 / CEO 인터뷰 (A2·A5) / `legal-rag-pattern` wiki / PM loop Step 5 Deliver / L1·L3 Matrix 가동

### Growth-31 (2026-06-11) — PM loop Step 5: lawfirm-demo 인도 패키지 조립 (CEO 승인 대기)

- **인격**: PM (패키지 조립, pm-agent 실가동) + CTO (검수·profile status 결정)
- **Axis touched**: customer (lawfirm-demo profile draft→active), creater 산출물의 고객 전달 형태 첫 정형화 (`docs/delivery/<slug>/` 패턴 신설)
- **Milestone**: M3 — legal vertical 인도 단계 진입 (M2 self-host 온보딩 문서 자산 겸용)
- **Why (1줄)**: Step 4 Verify 완료 상태에서 인도 패키지 (README 셋업 가이드 + acceptance 대조표 AC-1~5 + 데모 시나리오) 를 `docs/delivery/lawfirm-demo/` 로 조립 — honest-promise 검수 통과 (semantic/RAG 은 "범위 외" 명시로만 등장)
- **결정 (CTO)**: ① 인도 패키지 위치 = `docs/delivery/<slug>/` (out/ 은 gitignore 산출물, 전달 문서는 버전 관리 대상) ② profile status draft→active (L4 5종 PASS + 패키지 조립 완료 근거) ③ CTO 검수에서 README 의 bash 전용 inline env 구문에 PowerShell 형 병기 추가
- **PM 발견 갭**: `_precedent_results.html` SSR 경로가 데모에서 미사용 (htmx 응답을 JS 로 렌더) — 기능 영향 없음, engineer 검토 backlog
- **Revenue/cost**: M2/M3 인도 문서 자산 / pm-agent 1 호출 (~31k tokens)
- **Open loops**: **CEO 승인 → 고객 전달** (Step 5 exit 은 고객 수령 확인) / Step 6 Feedback / RAG 2단계 / CEO 인터뷰 (A2·A5) / `legal-rag-pattern` wiki / L1·L3 Matrix 가동 / `_precedent_results.html` SSR 경로 정리

### Growth-32 (2026-06-11) — CISO 인격 신설 (8번째) + lawfirm 인도물 첫 보안 리뷰 PASS

- **인격**: CEO (보안 요구·agent 추가 위임) + CTO (전담 분리 설계·CAVEAT 해소 결정) + CISO (보안 리뷰, 첫 dogfood) + Engineer (CAVEAT 패치)
- **Axis touched**: 조직 (charter v1.5 8-인격, CLAUDE.md §1 동기화), backend (legal.py 에러 누출 픽스), customer (profile security 섹션·billing setup_cost), delivery (security-checklist.md 신설)
- **Milestone**: M3 — legal vertical 인도의 보안 게이트 확립 (법무법인 = 데이터 외부유출 금지 고객)
- **Why (1줄)**: CEO 요구 "보안 결함 없는 인도물" + "보안 담당 agent 필요하면 추가" → 보안을 QA 에 통합하지 않고 전담 8번째 인격(CISO)으로 분리 (기능 PASS 축 ≠ 보안 PASS 축, 첫 고객이 보안 민감)
- **결정 (CEO 위임→CTO)**: ① CISO 전담 신설 (`.claude/agents/security-agent.md` + `security-loop` skill + charter v1.5 + INDEX) ② 인도 sign-off = CEO+PM+QA(기능)+CISO(보안) ③ CAVEAT 3건 당일 해소 (아키텍처 변경 불요, 코드/문서 1~2줄)
- **CISO 첫 리뷰**: PASS-WITH-CAVEAT → PASS. **A5 외부유출 0 확인** (fastapi 외부 호출 0건, tsvector 로컬만). SQLi/XSS/시크릿 0 findings. CAVEAT C1(README 보안경고)·C2(legal.py:137 에러 원문 누출)·C3(.env.example 평문 비번) 해소. fastapi 49 passed.
- **CEO 인터뷰 2문항 채움**: A6 예산=초기 구축비 500만원 일회성 (billing.setup_cost_krw, 월 LLM 은 분리·TBD). A5 보안=on-premise·self-host·무결함 인도 (profile security 섹션)
- **교훈 (1줄)**: 새 agent 정의는 세션 중 spawn 목록에 즉시 등록 안 됨 → 첫 dogfood 는 general-purpose 에 헌장+loop 주입으로 수행 (다음 세션부터 직접 spawn). 보안은 self-host 경계에서 "외부 호출 0" 을 grep 으로 증명하는 게 핵심 증거
- **Revenue/cost**: M2/M3 보안 인도 자산 / 보안 리뷰 ~64k + engineer ~24k tokens
- **Open loops**: legal 검색 엔드포인트 토큰 인증 (M2) / 시크릿 커밋 금지 정적 가드 (G-N 후보) / 의존성 CVE 자동 점검 / CISO 직접 spawn 검증 (다음 세션)

### Growth-33 (2026-06-11) — Subagent Output Protocol: 결과 파일화로 반환 변동비 차단

- **인격**: CEO (작업 방식 변경 결정) + CTO (규약 설계·loop 환류)
- **Axis touched**: 조직/오케스트레이션 (CLAUDE.md §11, 7 loop SKILL `## 출력 규약`), architecture (신규 protocol 문서)
- **Milestone**: M2/M3 — cost-aware-by-design 의 변동비 hedge (고객·인격 수 증가 시 선형 누출 차단)
- **Why (1줄)**: Growth-32 보안 리뷰 ~64k 토큰이 main context 로 통째 유입된 게 단일 변동비 주범 → subagent→main 반환 경계에 "파일로 쓰고 경로+요약 envelope 만 반환" 규약 확립
- **결정 (CEO→CTO)**: ① 단일 진실 `docs/architecture/subagent-output-protocol.md` (임계 ~30줄/2KB, 위치 3종, envelope 4항, CTO spawn 규율) ② 7 loop SKILL 에 `## 출력 규약` 1줄 환류 (8-인격 기본 적용) ③ CLAUDE.md §11 포인터 (ad-hoc agent 는 CTO spawn prompt 명시)
- **교훈 (1줄)**: context-mode 는 subagent *내부* 분석 비용을, output-protocol 은 subagent→main *반환* 비용을 줄인다 — 다른 축. 단일 규약 + 7 포인터로 중복 없이 cross-agent 적용
- **Revenue/cost**: 자체 비용 hedge 자산 (메타) / 이번 작업 토큰 소량 (문서+편집)
- **Open loops**: 실제 효과 측정 + 임계 가드 → **Growth-34 dogfood 에서 해소** (envelope ~10줄 측정 + G-13 wiring 가드 신설)

### Growth-34 (2026-06-11) — Output Protocol dogfood 측정 + G-13 가드 + 인프라 보안 회귀 점검

- **인격**: CTO (dogfood orchestrate·G-13 구현·integrator) + CISO (security-agent 재가동, 인프라 보안 리뷰)
- **Axis touched**: creater/거버넌스 (G-13 가드 = `scripts/diagnose.py`), 보안 (인프라 변경 회귀 리뷰)
- **Milestone**: M2/M3 — Growth-33 변동비 hedge 의 효과 증명 + 회귀 차단
- **Why (1줄)**: Growth-33 규약이 *주장*만 있고 *측정* 없었음 → 같은 실패 모드(security-agent, Growth-32 의 ~64k 유입원)로 재가동해 실제 반환 비용을 측정
- **측정 결과**: 본문 193줄/8KB → `out/analysis/security-infra-review-2026-06-11.md` (gitignored), subagent 내부 58.6k 토큰 격리, **main 반환 = envelope ~10줄** (PASS-WITH-CAVEAT + 경로 + CAV-1/2). Growth-32 ~64k 대비 차단 증명 — 규약 작동
- **G-13 신설 (CTO 직접)**: `g13_subagent_output_protocol_wired` — 7 loop SKILL 의 protocol 링크 정적 검사 (헤딩 무관). envelope 크기는 런타임 속성이라 정적 불가 → wiring 드리프트만 가드. `--check` 후보 G-14 로 재배치
- **보안 발견 (CISO)**: CAV-1 `AuthController.java` demo password (M1 stub, M2 삭제) / CAV-2 `@colbymchenry/codegraph` 1인 메인테이너 (버전 핀 권장). egress 0, 시크릿 노출 0. 둘 다 informational
- **교훈 (1줄)**: 규약은 dogfood 로 *측정*해야 자산이 된다 — 같은 실패 모드 재현이 가장 정직한 증명. 측정이 곧 hardening 가드(G-13)를 낳음
- **Revenue/cost**: 비용 hedge 효과 증명 (메타) / dogfood subagent 58.6k 토큰 (격리됨, main 미유입) + 편집 소량
- **Open loops**: G-14 (`--check` stale-anchor) 구현 시점 미정 / `.npmrc` codegraph 버전 핀 (engineer 후보)

### Growth-35 (2026-06-11) — DevOps 인격 신설 (9번째) + 배포 토폴로지 v1 (1인 비대면 창업 인프라)

- **인격/Axis/Milestone**: CTO (아키텍처·charter integrator) + DevOps (신설, founding) / 거버넌스 (9-인격 charter v1.6)·creater/인프라 (deployment-topology + CI/CD)·customer (디지털 자산 레지스트리) / M2·M3 — 비대면 고객 접점 인프라 토대
- **Why (1줄)**: CEO 가 이 harness 로 숨고/크몽 건당 500만원 1인 비대면 창업 → 인프라·디지털 자산·CI/CD 담당 인격 공백
- **핵심 통찰+결정 (CTO)**: **preview 티어 ≠ production 티어** (self-host=M2 가치 제안 → 최종물은 고객 인프라, n9n.co.kr/VPS 는 설득용 preview 전용). 고객-facing preview 는 노트북 터널 ✗ → **Coolify on Seoul VPS** ($6~12/월) + `*.n9n.co.kr` 와일드카드, 터널은 데모 폴백만. 메신저=숨고/크몽→카톡채널 (커스텀 ✗)
- **신설 자산·경계**: `devops-agent.md` + `devops-loop/SKILL.md`(G-13 PASS) + `deployment-topology.md` + `infra/registry/`(볼트 gitignored) + charter v1.6/INDEX. 경계: engineer=artifact / DevOps=출하·호스팅·추적, CISO=판정 / DevOps=하드닝 실행, 인도설치 PM+CISO 게이트 후
- **교훈 (1줄)**: 새 사업 모델(비대면 창업)이 직무 공백을 드러내면 인격 신설이 정답 — charter "직무별 인격" 철학의 6번째 적용
- **Revenue/cost**: preview 인프라 Hostinger KVM2 $8.99/월(24mo, Singapore) 가동 / 인격 신설·provisioning 은 편집·infra 0
- **provisioning→CI/CD→하드닝→결선 완료 (같은 세션)**: VPS live·SSH 키전용·커널패치 / `*.n9n.co.kr` grey-cloud / Coolify traefik LE 자동 TLS / **Coolify API(write+deploy) 배포 end-to-end 검증**(cicd-smoke HTTPS 200) / **8000 클라우드 방화벽 차단(allow 22/80/443) 실측 → CISO 잔여 0** / **scaffold→preview v1**(engineer: `preview_package.py`+Dockerfile×2, DB 없는 2-container, lawfirm-demo 로컬 `/login`·`/health` 200·manifest 14ent). 보안사고 2회→raw-file 규약. 레시피·상세=topology §4·devops.md
- **Phase 2~자동화 결선 (후속 세션, 같은 Growth)**: Coolify Phase 2 완료 — git-build(`private-deploy-key`+`build_pack=dockercompose`)+manifest persistent-storage RO 마운트로 **lawfirm-demo·shop-demo `.n9n.co.kr` 2 테넌트 live**(독립 검증 HTTPS 200+LE cert). 자동화: `preview_package.py --coolify`(서버 compose 생성)+`deploy_to_coolify.py --slug`(API 4단계+scp+검증 한 줄)+레지스트리 auto-merge(secret_ref 보존). webhook auto-deploy 는 **보류 결정**(Coolify 4.1.2 per-app 필터 부재→repo-push 시 전 테넌트 동시 재배포, 영업 데모 안정성 우선 — 코드는 `--setup-webhook --confirm` 게이트로 보관). **Caddy spike**: 5/5 함정 제거·wildcard DNS-01 cert 0발급·harness 변경 0 으로 기술 우위 확인했으나 **Coolify 유지 결정**(함정이 deploy 스크립트로 이미 캡슐화→전환비용=대시보드 상실+xcaddy+15~30s 다운타임 > 현 이득). 전환 트리거: 테넌트≥5 AND rotate 월1회↑ AND Coolify 함정 미해소. 락인 얕음 입증(artifact portable). 상세=`devops.md`
- **Open loops**: `.npmrc` codegraph 핀·G-14 stale-anchor 가드 (Growth-34 이월) / 실 고객 발굴 (M2 게이트) / 레지스트리 변경분 per-file 커밋 자동화·CISO SECRET_KEY rotate(Coolify UI 수동)

### Growth-36 (2026-06-12) — preview 디자인 경쟁력 (Phase 0+1) + 504 인시던트 2건 근본 해결

- **인격/Axis/Milestone**: CTO (integrator·검증) + CDO (도구 평가·토큰/CSS 적용) + DevOps (인시던트 진단·deploy 수정) / frontend (디자인 토큰 강화)·creater (compose 템플릿·deploy 견고화) / M2 — preview 데모 = 계약 전 설득 자산
- **Why (1줄)**: CEO 지적 — preview 시점은 미계약 상태라 기능+디자인 둘 다 경쟁력 필요
- **CDO 평가→적용 (Phase 0+1)**: 후보 12종 비교 (`out/analysis/design-tooling-eval.md`) → 기준 = node 빌드 0·CDN 1줄·토큰 추출성·MIT. 채택: **Pretendard Variable**(한국 첫인상 최대효과) + **Pico CSS v2 classless**(`--pico-*`→semantic 토큰 remap, 마크업 변경 0) + **Open Props**(motion/shadow 보충). 탈락: DaisyUI/Basecoat(Tailwind 빌드), Preline/SuperDesign(라이선스 NOASSERTION). 중기: Style Dictionary (M1~M2, react adapter 직전)
- **시각 검증 루프**: 로컬 python 직접 기동(Docker off 폴백)+Playwright 스크린샷 → Pico `button[type=submit]{width:100%}` 회귀 1건 발견→`button.btn{width:auto}`+`.login-card` scope 전폭 보존으로 해소
- **결함 3건 연쇄 발견·해결**: (1) tokens.css gitignored 인데 Dockerfile 토큰 빌드 스텝 부재→이미지에 CSS 누락 (COPY design/tokens+RUN build_tokens.py). (2) **504 인시던트**: 1차=Caddy spike 잔재 Caddyfile 이 Traefik file provider 오염(백업 후 삭제+proxy 재시작), 2차=compose 자체 `preview-net` 선언→이중 네트워크→Traefik 이 프록시 미도달 IP 선택하는 bistable(`preview-net` 제거, uuid 넷 단일화). (3) deploy 스크립트 이름-매칭 의존→**registry-first uuid lookup**(구/신 포맷 지원)+description em-dash 가 Coolify validation 422 (ASCII 정화)
- **교훈 (1줄)**: spike 잔재는 spike 종료 시점에 회수해야 한다 — 평가용 파일 하나가 이틀 뒤 영업 자산 전체를 죽였다. + 외부 시스템 매칭은 이름이 아니라 레지스트리 uuid 가 단일 진실
- **Revenue/cost**: LLM=agent 5회 spawn(~34만 tok) / infra 불변 / 영업 자산 품질 상승 (두 데모 Pretendard+Pico live: HTTPS 200+tokens.css 12.5KB+LE cert)
- **Open loops**: Growth-35 이월 전부 / Caddy spike 파일 회수 규약(devops-loop SKILL 반영 후보) / Phase 2 디자인(Franken UI, 계약 후 quality bar)

### Growth-37 (2026-06-12) — 웹 intake 인터페이스: needs 인터뷰 폼 + 의뢰인 레코드 관리 (intake.n9n.co.kr live)

- **인격/Axis/Milestone**: CTO (integrator) + PM (질문 카탈로그) + Engineer (앱·변환기·deploy 견고화) + CDO (UI 감수) + CISO (BLOCK 3건→해소 PASS) / creater (deploy 일반화)·customer (intake→profile 파이프)·신규 1st-party 앱 카테고리 `apps/` / M2 — PM loop step 0~2 디지털화로 영업 루프 단축
- **Why (1줄)**: CEO — "웹으로 사용자의 needs 를 묻고 요구사항을 도출하는 인터페이스" + "의뢰인 정보 저장·관리, 재문의·수정 가능"
- **구현**: `apps/intake/` — questions.yaml(PM 단일 진실, 3 페르소나 분기 30문항, maps_to→profile/needs_note 매핑) + FastAPI(제출→append-only revision, edit_token 재수정, admin Basic auth+lockout, honeypot+rate limit) + `intake_to_profile.py`(schema v1 키만, 불일치는 needs note 시그널) + Pretendard/Pico/Open Props 계승. pytest 11/11
- **게이트·함정**: CISO BLOCK 3건 (Traefik 뒤 client IP 단일 버킷 / admin path traversal / autoescape 미명시)→수정→재검증 PASS — 보안 리뷰 루프 첫 실전 완주. deploy 함정 2건: ① 도메인 서비스명 하드코딩→registry `preview.domain_service` 키 (dry-run 이 잡음) ② `docker_compose_domains` GET=string/PATCH=array 비대칭→422 (body 출력 개선으로 확정)
- **교훈 (1줄)**: 게이트는 비용이 아니라 속도다 — dry-run·CISO 리뷰·스크린샷 검증이 라이브 전에 결함 5건을 잡아 첫 의뢰인 앞 사고를 선제 제거했다
- **Revenue/cost**: LLM=agent 6회 spawn(~64만 tok) / infra=기존 VPS 앱 1개 추가(증분 0원) / admin env 설정 전 404 안전 기본값
- **Open loops**: INTAKE_ADMIN_PASSWORD Coolify env 설정(CEO, F-4 수동) / intake 제출→PM triage 운영 절차 pm-delivery-loop SKILL 반영 / FIX-4 CDN SRI(adapter base.html 포함)·FIX-5 webhook argv / rtk 0.34.3→0.42.x 업그레이드(CEO cargo install)

### Growth-38 (2026-06-12) — 영업 루프 풀사이클 리허설: intake 2건 → triage → 회신 반영 → edu-program preview live

- **인격/Axis/Milestone**: CTO (integrator·직접 deploy) + PM (triage·needs note·draft profile) + domain-expert-generic (교육 매핑 의견서) + Engineer (YAML bool·deploy race 수정) / customer (edu-program profile)·creater (deploy 견고화)·expert-agent (교육 vertical 시그널) / M2 — 숨고/크몽 홍보 전 end-to-end 리허설
- **Why (1줄)**: CEO — "홍보 전에 전체 프로세스를 다시 돌려보고 싶다" (지인이 intake.n9n.co.kr 에 실제 2건 제출)
- **triage**: 건1 (대학 정부사업 — 학생리스트·사업비·학사관리) 수용+follow-up 8문항 / 건2 (B2C 열차예매 앱) 스코프 밖 거절 회신 작성. "인터뷰 없이 profile 작성 금지" 안티패턴 준수 — 학사관리·order·asset 은 미답으로 profile 제외
- **실결함 2건 (리허설이 잡음)**: ① `questions.yaml` 무인용 `value: no` → YAML 1.1 bool 함정, 실제 제출 데이터에 `False` 저장 (quote+로더 방어+회귀 테스트+라이브 재검증) ② push 직후 배포 시 `docker_compose_domains` 422 — Coolify 가 git compose 미적재 상태 race → `_wait_for_compose_raw()` poll+retry 자동 복구
- **회신 반영→live**: postgres 확정 → domains crm/finance/document/reporting draft profile → scaffold 9 entities → **edu-program.n9n.co.kr live** (HTTPS 200·LE cert, push→live 한 회전). idempotent 재실행이 기존 project/app uuid 이름-fallback 재사용 실증
- **domain-expert 의견**: student 는 catalog enum 확장 ✗ → customer overlay (타 고객 의미 오염 방지) / 정부사업비 budget-line·품의·정산보고는 14 baseline 구조적 부재 → `presets/skills/education/` seed 신설 권고 (M3 첫 vertical 후보 시그널)
- **후속 회전 (같은 Growth)**: 10문항 회신 전부 도착 → 7 domains/18 entities 확정 (enrollment=crm lead→contact→project 매핑, domain-expert 권위로 PM 오판 2건 reconcile) / **needs-반영 데모 UI** (profile display→manifest→메뉴·홈 카드·피드백 CTA, harness 레벨) / **intake `/letter/{token}` 안내문 URL 기능** (txt 복사 → URL 전달, make_letter.py) / **demo seed 데이터 기능** (`seed_demo_data.py` manifest→한국어 가상 데이터 결정적 생성 + backend `SEED_FILE` startup 적재 + compose/deploy seed-aware — edu 18 entity 193건 live) / **앱 셸 + 고객 용어 라벨** (CDO 스펙→engineer: 상단바·좌측 도메인 메뉴·active 3px 바·아바타·비인증 미니멀 분기 / entity label 3단계 해석 profile entity_labels>catalog label_ko>영문 — catalog 60 entity label_ko 누적, 사이드바·제목 전부 고객 용어) / 신규 함정 2건: push-직후 deploy 의 compose_raw 422 race (poll+retry 자동 복구) + **manifest bind-mount 디렉터리화** (scp 전 컨테이너 생성 시 docker 가 source 를 dir 로 생성 → 이후 scp 가 dir 안으로 → 복구 = rm+scp+재생성)
- **교훈 (1줄)**: 리허설은 실데이터로만 드러나는 결함을 잡는다 — 스모크 통과한 폼의 bool 함정도, push-직후 race 도, bind-mount 디렉터리화도 실제 의뢰 흐름에서만 나타났다
- **Revenue/cost**: LLM=agent 6회 spawn (리허설 2회전 누적 ~37만 tok) / infra=기존 VPS 앱 1 추가 (증분 0원) / M2 게이트 직전 — 인프라·프로세스 검증 끝, 남은 건 영업
- **Open loops**: 건1 scope-confirm 발송 (CEO — letter URL, 학사관리=사업 범위·LMS=배치 가져오기 단계 동의) / 건2 거절 회신 발송 (CEO) / production self-host 합의 (Vercel 비추천 전달) / education vertical seed 신설 (M3 — budget-line·enrollment·attendance 등 9 entity 후보) / manifest scp 순서 견고화 (deploy 스크립트, devops 후보)

### Growth-39 (2026-06-12 후속 세션) — 아코디언 사이드바 + Hostinger CSS + 테이블 스타일

- **인격/Axis/Milestone**: CTO (integrator) + CDO (디자인 분석·spec) + Engineer (CSS·JS·토큰 구현) / frontend (vanilla-htmx adapter)·design (토큰 파이프라인) / M2 — edu-program.n9n.co.kr UI 품질 상향
- **Why (1줄)**: CEO — "좌측 1차/2차 아코디언 메뉴, Hostinger 수준 CSS, 반응형 UI" + 수평 배열·라이트테마·테이블 스타일 3종 보정 요청
- **구현**: `sidebar-group__header` button + SVG chevron + `sidebar-nav--accordion` (max-height 0→600px CSS transition) + `initAccordion()` JS (localStorage `sidebar-accordion-open` 상태 유지). Hostinger 라이트테마: `--sidebar-item-active-bg: #EEF2FF` / `--sidebar-item-active-text: #4F46E5` / active `::before` left-bar 제거(fill-only) / 트리 indent `border-left 2px + padding-left 20px`. 3단계 반응형: ≥1280px 240px / 769–1279px 56px CSS-only collapse / <768px drawer. 테이블: `.th` `#F8FAFC`·2px 하단선 / `.td` `#F0F0F0` 구분선 / hover `#F8FAFC`(파랑 제거) / 줄무늬 제거 / `table-wrapper` 부드러운 그림자.
- **핵심 버그**: Pico CSS classless 가 `<nav>` 에 `flex-direction: row` 자동 적용 → `display: block` 명시로 차단 (`.app-sidebar`, `.sidebar-group`, `.sidebar-nav { flex-direction: column }`).
- **토큰 파이프라인**: `tokens.css` gitignored → `design/tokens/semantic.json` sidebar 섹션(10 토큰) 추가 → `build_tokens.py` 재생성 → Docker build time 포함.
- **커밋**: 161a61d→046bcbb→fa18df3→56954c2→ccac470→eaa0f5b (6건, pushed). live 검증: 10 sidebar CSS vars PASS, initAccordion PASS, table styles PASS.
- **교훈 (1줄)**: CSS 프레임워크 암묵적 기본값(Pico nav flex-row)은 레이아웃 컴포넌트에 반드시 명시 override — `display: block` 한 줄이 수평 메뉴 버그 전체를 해결한다
- **Revenue/cost**: LLM=CDO+Engineer agent 2회 spawn / infra 변경 없음 / M2 데모 UI 품질 충족
- **Open loops**: 건1 scope-confirm 회신 대기 / 건2 거절 회신 대기 / education vertical seed 신설 (M3) / G-14 stale-anchor 가드 / `.npmrc` codegraph 버전 핀

### Growth-47 (2026-06-13) — UX/Design wiki 환류 (KWCAG + 한국어 UX 관행)

- **인격/Axis/Milestone**: CTO (integrator) + CDO (지식 정리) / design (wiki 축) / M2 — 영업 준비 지식 베이스 완성
- **Why (1줄)**: Growth-40 deep-research 미답 항목(KWCAG·인터랙션 패턴·UX 관행) → wiki 환류 → 실 고객 발굴 전 설계 근거 확보
- **작업**: `design/refrence` 오타 수정 → `design/reference/`. wiki 신규 2페이지: `knowledge/wiki/design/kwcag.md` (KWCAG 2.2 4원칙·명도대비 수치·ARIA 체크리스트·법적 근거) + `knowledge/wiki/design/korean-ux-conventions.md` (Pretendard 타이포·날짜/금액 표기·폼 레이아웃·버튼 텍스트·테이블 인터랙션·검색패널·모달 관행). wiki index 포인터 2개 추가.
- **커밋**: b87d766→c2260c9→18f0d14→79e6a71 (4건, pushed)
- **교훈 (1줄)**: Gemini CLI 미설치 환경에서 외부 리서치 불가 → 훈련 지식으로 KWCAG 2.2·한국 UX 관행 직접 작성 (안정적 표준은 실시간 fetch 없이도 충분)
- **Revenue/cost**: LLM=없음 (직접 작성) / infra 변경 없음 / wiki 2페이지 = 실 고객 접점 전 설계 지식 완비
- **Open loops**: 실 고객 발굴 (M2, 숨고·크몽) / education vertical seed / G-14 stale-anchor

### Growth-48 (2026-06-13) — DBA 인격 신설 (10번째) + Supabase 전략 논의

- **인격/Axis/Milestone**: CTO (전략) + DBA 신설 / ddl 축 강화 / M2 — 소규모 고객 셀프서비스 DB 설계 지원
- **Why (1줄)**: 소규모 고객은 DB 설계 경험이 없어 프로젝트 시작점(ERD→DDL)에서 병목 → DBA agent 가 공백 해소
- **작업**: `.claude/agents/dba-agent.md` 신설 (ERD·정규화·DDL 산출·마이그레이션·catalog.yaml 환류 담당). INDEX.md·CLAUDE.md §1 팀 로스터 갱신. Supabase = 추후 `backend/adapters/supabase/` adapter로 격리 예정 (vendor lock-in 방지).
- **커밋**: 649762e→1f504f3→ca897c6 (3건)
- **교훈 (1줄)**: domain-expert(무엇을 만들지) ↔ DBA(어떻게 저장할지) 분업이 명확해야 소규모 고객 셀프서비스가 가능
- **Revenue/cost**: LLM=없음 / infra 변경 없음 / 소규모 고객 DB 설계 병목 해소 → M2 전환율 개선 기대
- **Open loops**: 5개 industry demo variants / Supabase backend adapter 구현 / G-14 stale-anchor

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
- **Open loops**: 5개 데모 Coolify 배포(서브도메인 확정 필요) / manufacturing-demo 추가(smallmfg-demo 보완) / Supabase adapter 구현
