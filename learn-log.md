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
| L2 JDBC | NOT_SETUP | — |
| L3 build | NOT_SETUP | — |
| L4 live | NOT_SETUP | — |

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

## §5 — Environment Notes

- 2026-05-29: founding. Sibling repo `business-fullstack-creater` 에서 메타 자산만 승계. Nexacro/uiadapter 의존 0.
- 결정 사항 (CTO): Frontend / Backend 는 pluggable, Middle 만 stable. customer profile `stack.frontend` / `stack.backend` 키로 교체.
- 결정 사항 (Founder + CTO): 첫 vertical 은 시장 데이터로 결정 (M2 첫 고객 산업 → M3 vertical 진입).

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

### Growth-4 (2026-05-29) — 4-인격 → 6-인격 확장 + learn-log per-agent 분리

- **인격**: CEO (제안) + CTO (수용·설계)
- **Axis touched**: creater (agent 인격 2 신설), 헌장 (CLAUDE.md §1 + AGENTS.md + partnership-charter §1·§2·§8)
- **Milestone**: M0 마무리 (팀 구조 재설계)
- **Revenue/cost**: infra only / 본 세션 1회 Opus 4.7
- **Why (1줄)**: learn-log 무거워져 main context 가 goal 보다 디테일에 빠짐 — 인격별 ledger 로 상세 분리, main 은 1줄 rollup 으로 유지
- **상세**: [cto.md#Growth-4](docs/learn-logs/cto.md)
- **결정 (CEO 직접)**: 인격 분리 트리거. CTO 가 수용·설계로 미러
- **Open loops**: trade-off 보강 토론 (G-9 후보 — main learn-log 행 길이/수 가드), engineer/QA 첫 spawn 은 M1 진입 시

### Growth-5a (2026-05-29) — Growth-4 trade-off 보강 (G-9 + 슬림 spec + Integrator 의무 + 분기 synthesis)

- **인격**: CTO (단독, CEO 추천안 위임)
- **Axis touched**: creater (G-9 가드), 헌장 (charter §3 #5), learn-logs (synthesis-template)
- **Milestone**: M0 완전 마무리 (Growth-4 trade-off 4 항목 잠금)
- **Revenue/cost**: infra only / 본 세션 turns ~30, Opus 4.7 단독
- **Why (1줄)**: 인격 분리 trade-off (narrative 손실 + discovery 비용) 를 main §6 슬림 cap + 분기 synthesis + CTO Integrator 의무로 묶어 구조적으로 잠금
- **상세**: [cto.md#Growth-5a](docs/learn-logs/cto.md), [qa.md#Growth-5a](docs/learn-logs/qa.md)
- **결정 (CTO Auto, CEO 위임 "추천안으로 가자")**: (a) 슬림 포맷 spec + (c) 분기 synthesis 템플릿 + (d) G-9 가드 + (f) charter §3 Integrator step
- **Open loops**: CEO 회수 질문 4건 (Growth-5b 일부 해소), M1 entry (G-1/G-2 활성화), CDO tokens.md

### Growth-5b (2026-05-29) — charter v1.3 (private master push CTO 자동화) + repo 첫 GitHub 등재

- **인격**: CEO (직접 제안) + CTO (실행·동기화)
- **Axis touched**: 헌장 (charter §3 #3 + §8, CLAUDE.md §9, AGENTS.md), 외부 시스템 (github.com/JasonMMo/compounding-stack-harness private)
- **Milestone**: M0 후 자산 (push 룰 정렬)
- **Revenue/cost**: infra only / push 1회, gh repo create 1회 / 본 세션 turns ~10
- **Why (1줄)**: private 단계 push 마찰 ↓ + public 전환 시 사전 확인 룰 자동 재발효 — 조건부 룰로 reversibility 보존
- **상세**: [cto.md#Growth-5b](docs/learn-logs/cto.md)
- **결정 (CEO 직접)**: "charter §6 의 master 푸시를 자동으로 변경하자" → charter v1.3 으로 §3 #3 조건부화 (visibility 게이팅)
- **Open loops**: public 전환 시점 = CMO 회수 질문 #3 (OSS/상용 분리선) 결정과 연동

### Growth-5c (2026-05-29) — CDO tokens.md M0 인수 + CTO 4 escalation 응답

- **인격**: CDO (산출물) + CTO (escalation 응답·Integrator)
- **Axis touched**: design (docs/design/tokens.md 신규), 헌장 (token versioning compliance test 정책)
- **Milestone**: M0 후 자산 (디자인 토큰 single source)
- **Revenue/cost**: infra only / Sonnet 4.6 subagent 1회 + Opus 4.7 결정 ~5 turns
- **Why (1줄)**: M2 첫 페르소나 demo 인수 조건이 토큰 정의 없이 못 풀림 — raw→semantic→persona 2층 + WCAG AA + KWCAG 2.1 floor 박음
- **상세**: [cdo.md#Growth-5c](docs/learn-logs/cdo.md), [cto.md#Growth-5c](docs/learn-logs/cto.md)
- **결정 (CTO Auto, 4 escalation)**: Q1 dark mode 보류 (M2 게이트) / Q2 i18n = adapter / Q3 token compliance test YES / Q4 CEO `breakpoint.tablet:768px` 추가 — tokens.md §11
- **Open loops**: brand color (M1 CEO+CMO 게이트), engineer 가 token JSON 파일 생성 (M1 adapter 작업 시), dark mode M2 재평가

### Growth-5d (2026-05-29) — Engineer M1 entry kickoff + CTO 4 contract 표준 박힘

- **인격**: Engineer (산출물) + CTO (escalation 응답·Architect)
- **Axis touched**: middle (wire-v1.yaml 신규 8키), customer (acme-erp.yaml sample profile)
- **Milestone**: M1 진입 (G-4 SKIP→PASS 첫 전환, G-1 dir 등장)
- **Revenue/cost**: infra only / Sonnet 4.6 subagent 1회 ~12 turns + Opus 4.7 결정 ~5 turns
- **Why (1줄)**: M1 첫 deliverable = middle wire-protocol single source + customer profile schema 실 인스턴스, adapter 작업 전제
- **상세**: [engineer.md#Growth-5d](docs/learn-logs/engineer.md), [cto.md#Growth-5d](docs/learn-logs/cto.md)
- **결정 (CTO Auto, 4 escalation)**: Q1 entity.update = PATCH 표준 / Q2 entity.delete 404→success 표준 / Q3 OpenAPI 3.1 migration = 첫 adapter 직후 / Q4 schema v1 secrets 분리 = NO (v2 후보)
- **Open loops**: G-1 SPEC→PASS 활성화 (yaml-key extractor 본문), QA 첫 가동 (compliance test), OpenAPI migration

### Growth-5e (2026-05-29) — CMO 회수 질문 4건 CEO 답변 통합 (Growth-3 open loop 해소)

- **인격**: CEO (직접 답변) + CMO (positioning.md 반영) + CTO (Integrator)
- **Axis touched**: marketing (positioning.md CEO 회수 답변 박힘), 인격 ledger (cmo.md Growth-5e)
- **Milestone**: M0 후 자산 (Growth-3 CMO 4 회수 질문 해소)
- **Revenue/cost**: infra only / Sonnet 4.6 subagent 1회 + Opus 4.7 결정 ~3 turns
- **Why (1줄)**: Growth-3 CMO 가 던진 4 질문이 Growth-5b~5d 작업 동안 답변되지 않으면 M2 게이트 판정 자체가 모호
- **상세**: [cmo.md#Growth-5e](docs/learn-logs/cmo.md), [cto.md#Growth-5e](docs/learn-logs/cto.md)
- **결정 (CEO 직접)**: Q1 가격 deferral (maturity threshold) / Q2 첫 vertical = 첫 paid customer (재확인) / Q3 OSS 분리선 = M2 후 / Q4 M3 landing = CMO+CDO
- **Open loops**: "maturity threshold" 측정 정의 — CTO 가 M1 마무리 Growth 에 박을 후보 (Q1 답변의 정량화)

### Growth-5f (2026-05-29) — colbymchenry/codegraph 설치 (2-step gate + tenant 분리 요구)

- **인격**: CEO (제안+승인) + CTO (Integrator)
- **Axis touched**: 메타 도구 (외부, axis 미정착), 외부 시스템 (npm `@colbymchenry/codegraph` v0.9.7 + local MCP)
- **Milestone**: M1 진입 보조 (자산 측정 도구)
- **Revenue/cost**: infra only / npm install + index 1회 (38 nodes, 62 edges, 420ms) / Opus 4.7 ~5 turns
- **Why (1줄)**: learn-log 인격 분산 후 cross-concern 추적·7축 환류 누락 탐지를 위한 메타 도구 — 채택은 M1 첫 adapter Growth 마무리 4-measurement 후 결정
- **상세**: [cto.md#Growth-5f](docs/learn-logs/cto.md)
- **결정 (CTO 권고안, CEO 위임)**: upstream 채택 (fork 거부) / 2-step gate / 누적 데이터 = 우리 자산 + 고객별 분리 가능 / axis 등록 보류 / install 형태 = local (.mcp.json + .claude/settings.json)
- **Open loops**: M1 첫 adapter Growth 마감 시 4-measurement + adopt/reject + tenant 분리 메커니즘 설계

### Growth-6 (2026-05-29) — 14 generic skill seed 완성 (M1 axis-1 첫 채움)

- **인격**: CTO (포맷 설계·Integrator) + Engineer (14 파일 생성)
- **Axis touched**: skill (`presets/skills/generic/` 신규 — _seed-format.md + 14 *.seed.md)
- **Milestone**: M1 진입 (generic harness 14 도메인 seed catalog 완성, M2 acme-erp demo prerequisite 충족)
- **Revenue/cost**: infra only / Sonnet 4.6 engineer subagent 1회 ~32 turns / 15 파일 15 commits
- **Why (1줄)**: M2 acme-erp demo 의 hard prerequisite — 14 도메인 seed 없이 domain-expert-generic agent 가 DDL/adapter 생성 판단 불가
- **상세**: [cto.md#Growth-6](docs/learn-logs/cto.md), [engineer.md#Growth-6](docs/learn-logs/engineer.md)
- **결정 (CTO Auto)**: Karpathy seed 포맷 = YAML frontmatter(domain/label/version/entities/wire_keys) + 5-section MD; 14 도메인 = hr/finance/logistics/inventory/sales/crm/procurement/production/quality/project/asset/document/approval/reporting
- **Open loops**: DDL catalog 연동 (presets/ddl/catalog.yaml — M1 Priority 다음 단계), G-5 axis 수 2 도달 시 SKIP→PASS 전환 후보, 첫 adapter 2개 (M1 Priority 2)

### Growth-7 (2026-05-29) — 첫 backend adapter (springboot-jakarta) + G-1 활성 + QA 첫 BLOCK→PASS

- **인격**: CTO (설계·contract·Integrator) + Engineer (adapter·G-1·버그수정) + QA (compliance 게이트, 첫 가동)
- **Axis touched**: backend (springboot-jakarta adapter 신규), middle (error/codes.yaml + paging 직렬화 컨벤션 + manifest), creater (G-1 SPEC→active)
- **Milestone**: M1 (첫 pluggable adapter 실증, Backend 축 첫 채움)
- **Revenue/cost**: infra only / Sonnet engineer 3 round + qa 2 round + Opus 결정 ~12 turns / ~30 commits
- **Why (1줄)**: pluggable F/B 차별화의 첫 실증 — wire contract 만으로 generic CRUD backend 가 돌고 compliance 게이트가 작동하는지 증명
- **상세**: [cto.md#Growth-7](docs/learn-logs/cto.md), [engineer.md#Growth-7](docs/learn-logs/engineer.md), [qa.md#Growth-7](docs/learn-logs/qa.md)
- **결정 (CTO Auto + CEO scope)**: backend 먼저 단독(CEO) / error envelope object / paging HTTP flat-underscore 직렬화 / gradle-wrapper.jar 추적 / G-1 검출 정책(재선언 FLAG·참조 ALLOW)
- **Open loops**: frontend vanilla-htmx + tokens JSON (Growth-8), adapter `paging.mode` fallback 제거 cleanup, codegraph 4-measurement (F/B 양 adapter 후 Growth-8 마감 시 — 이번 세션 codegraph 직접 사용 빈약해 데이터 보강 필요)

### Growth-8 (2026-06-01) — 첫 frontend adapter (vanilla-htmx) + CDO 첫 가동 (design tokens) + frontend 계약

- **인격**: CTO (frontend-adapter 계약 설계·Integrator·border-input 판정) + CDO (토큰·a11y, 첫 가동) + Engineer (adapter·CSS 생성기) + QA (frontend compliance 게이트)
- **Axis touched**: frontend (vanilla-htmx adapter 신규 — Frontend 축 첫 채움), design (`design/tokens/` + patterns + a11y 신규 — CDO 산출), middle (frontend-adapter-contract.md — frontend 판 compliance 계약)
- **Milestone**: M1 Priority 2 완료 (F/B 양 adapter 실증 — pluggable 3-tier 양끝 채워짐)
- **Revenue/cost**: infra only / CDO Sonnet 2 round + Engineer 1 round + QA 1 round / 토큰 11 commits + adapter 22 파일
- **Why (1줄)**: pluggable F/B 차별화의 frontend 끝 실증 — 같은 wire contract 로 backend 와 무관하게 generic CRUD UI 가 돌고, 디자인 토큰 단일 진실이 작동
- **상세**: [cto.md#Growth-8](docs/learn-logs/cto.md), [engineer.md#Growth-8](docs/learn-logs/engineer.md), [qa.md#Growth-8](docs/learn-logs/qa.md)
- **결정 (CTO)**: frontend adapter = thin proxy server (req emitter) / F-1~F-4 준수점 / border-input 독립 토큰 (WCAG 1.4.11, CEO 예외) / tokens.css gitignore (파생 산출물) / commit trailer 4.7→4.8 동기화
- **Open loops**: CSRF 프로덕션 하드닝 (M1 dev-mode known-gap → 보안 게이트 Growth-N), `paging.mode` fallback 제거 cleanup, react adapter (M1 잔여), codegraph 4-measurement, HANDOFF.md 삭제 (M1 첫 adapter 완료 = 충족)

### Growth-9 (2026-06-01) — codegraph 2-step gate measurement → 조건부 ADOPT (코드 네비게이션 한정)

- **인격**: CTO 단독 (VP 채택 판정 + Architect scope 박기) — sub-agent 0
- **Axis touched**: 없음 (codegraph 는 메타 도구, axis 미등록 확정). `docs/architecture/codegraph-adoption.md` 신규
- **Milestone**: M1 (Growth-5f 2-step gate 2번째 step 종결 — 도구 거취 확정)
- **Revenue/cost**: infra only / Opus 측정·판정 ~6 turns + codegraph reindex 780ms / 외부 호출 0
- **Why (1줄)**: 외부 도구를 "써보고 측정 후 거취 결정" 하는 reversible 규율의 실증 — install≠adopt, 데이터로 scope 를 잘라낸 판정
- **상세**: [cto.md#Growth-9](docs/learn-logs/cto.md)
- **결정 (CTO)**: 조건부 ADOPT — 코드 네비게이션만 / 거버넌스·결정-ownership DESCOPE (diagnose.py+ledger 단일 진실) / axis 미등록 / `codegraph sync` 운영룰 / tenant=per-repo 재생성 이미 충족. **결정적 측정: markdown·json 미인덱스 → 7축 절반(skill/expert-agent/design) 불가시**
- **Open loops resolved**: codegraph 2-step gate. 남은: ddl catalog (다음, M2 prereq), react/fastapi adapter, maturity threshold 정의

### Growth-10 (2026-06-01) — ddl 축 채움 (56 entity catalog + dialect 렌더 + G-10) + QA L2 첫 가동 BLOCK→PASS

- **인격**: CTO (catalog format spec + G-10 정의) + Engineer (56 entity transcription + 4 dialect + render.py + G-10 본문 + 결함수정) + QA (L2 HSQLDB 게이트, 첫 가동)
- **Axis touched**: ddl (`presets/ddl/catalog.yaml` 56 entity + dialects/ + render.py 신규 — Stage 2 축 첫 채움), creater (G-10 가드 신설)
- **Milestone**: M1 (ddl 축 = M2 acme-erp demo 의 hard prerequisite — entity 스키마 단일 진실 + L2 풀테스트 입력)
- **Revenue/cost**: infra only / Engineer 2 round + QA 2 round (L2 첫 가동) / catalog+dialect+render+guard ~13 파일
- **Why (1줄)**: 14 도메인 56 entity 의 dialect-neutral 스키마가 단일 진실로 박혀야 entity.create 검증·L2 풀테스트·M2 demo 가 성립
- **상세**: [cto.md#Growth-10](docs/learn-logs/cto.md), [engineer.md#Growth-10](docs/learn-logs/engineer.md), [qa.md#Growth-10](docs/learn-logs/qa.md)
- **결정 (CTO)**: neutral 8-type closed set / dialect adapter 분리 (postgres·hsqldb full, mysql·oracle 타입맵 stub) / multi-tenant 컬럼 M5 게이트까지 보류 / build/ gitignore (파생) / G-10 신설 (seed⊆catalog·dangling FK·type closed-set) / patch_schema.py 보존 (QA regression 가드 권고)
- **Cross-agent catch**: QA L2 첫 가동이 라이브 HSQLDB 2.7.4 로 render.py **3 결함 적발** (D1 순환 FK inline, D2 CHECK 식별자 미인용 28건, D3 DEFAULT 순서) → BLOCK. **catalog 는 건전** (QA 가 patched 47/47 로 분리 증명) — renderer 버그임을 정확히 격리. engineer 수정 → raw schema 125 error→0, 48/48 PASS.
- **Open loops resolved**: ddl 축 첫 채움. 남은: adapter 검증 wiring (catalog→InMemoryStore), accounting_period 57번째 entity 후보, react/fastapi adapter

### Growth-11 (2026-06-01) — 2nd backend adapter (fastapi) + 공유 compliance suite 첫 재사용 (adapter-agnostic 실증)

- **인격**: CTO (fastapi 픽·backend 축 manifest·suite 단일화 지시) + Engineer (fastapi adapter) + QA (공유 suite 재사용 검증, 4번째 가동)
- **Axis touched**: backend (fastapi adapter 신규 — 2번째 backend, Java→Python swap), creater (`backend/adapters/INDEX.md` manifest 신규)
- **Milestone**: M1 (pluggable backend 차별화 **실증** — 한 wire contract 가 Spring Boot/Java 17 와 FastAPI/Python 을 동일 구동)
- **Revenue/cost**: infra only / Engineer 1 round + QA 2 round / fastapi adapter ~10 파일 + suite 단일화
- **Why (1줄)**: "stack.backend 한 줄로 교체" 핵심 주장의 실증 — 동일 23-test black-box suite 가 두 런타임에 assertion 변경 0 으로 green
- **상세**: [cto.md#Growth-11](docs/learn-logs/cto.md), [engineer.md#Growth-11](docs/learn-logs/engineer.md), [qa.md#Growth-11](docs/learn-logs/qa.md)
- **결정 (CTO)**: fastapi 픽 (react 보다 — backend swap 이 차별화 직접 실증 + suite 첫 재사용 검증 + axis-7 Python 결합) / G-5 manifest `backend/adapters/INDEX.md` 추가 (fastapi 가 2-asset 트리거) / compliance suite `tests/adapters/_shared/` 단일화 + springboot 는 import shim (중복 즉시 제거, 후속 미룸 거부)
- **Cross-agent catch**: engineer 가 G-5 FAIL 적발 (backend 2 adapter) → CTO manifest 로 해소 (feedback_guards_must_work). QA 의 "identical copy" backward-compat 를 CTO 가 import shim 으로 단일화 지시 — single-source 원칙을 테스트 코드에도 일관 적용. **adapter-agnostic 주장 HELD: 동일 suite Java+Python 양쪽 23/23**
- **Open loops resolved**: M1 backend 2번째 채움, 공유 suite 재사용 검증. 남은: react adapter (M1 frontend 2번째), adapter 검증 wiring

### Growth-12 (2026-06-01) — adapter 검증 wiring (catalog→entity.create) + 가드 회귀 catch

- **인격**: CTO (validation 계약 + 가드 회귀 진단·라우팅) + Engineer (CatalogValidator × 2 adapter + 가드 수정) + QA (DIM-5 게이트)
- **Axis touched**: backend (springboot+fastapi 양쪽 검증 wiring — catalog.yaml 을 런타임 소비), creater (G-6·G-8 build/ 제외 하드닝)
- **Milestone**: M1 (56 entity catalog 를 살아있는 자산으로 — entity.create 가 catalog 스키마 검증, M2 demo 다음 link)
- **Revenue/cost**: infra only / Engineer 2 round (구현+가드수정) + QA 1 round / 양 adapter validator + DIM-5
- **Why (1줄)**: ddl catalog 가 adapter 에 연결돼야 56 entity 가 죽은 스키마가 아니라 실제 검증 게이트로 작동
- **상세**: [cto.md#Growth-12](docs/learn-logs/cto.md), [engineer.md#Growth-12](docs/learn-logs/engineer.md), [qa.md#Growth-12](docs/learn-logs/qa.md)
- **결정 (CTO)**: catalog entity 만 enforce, 미정의 entity_type 은 schema-less 통과 (backward-compat — 기존 23-test 무파손) / required·type·enum·length→VALIDATION_ERROR(422), unique→CONFLICT(409) / 서버컬럼(id·created·updated) 검증 제외 / PATCH 부분검증 (required 생략) / FK 참조검증 후속 / `docs/architecture/validation-contract.md`
- **Cross-agent catch**: 검증 PASS(DIM-5 31/31 양 adapter) 후 **가드 3개 회귀** — CTO 진단: G-1 fastapi 가 422/409 하드코딩(springboot 패리티 위반) = 진짜 소스버그 → loader 경유 수정. G-6·G-8 은 gradle `build/` 생성물(catalog copy 주석의 tenant_id·.class 의 `$`) 오탐 = 스코프 버그 → G-1 과 동일 제외셋으로 정정 (약화 아님, 소스 검출 유지). feedback_guards_must_work 일관 적용.
- **Open loops resolved**: adapter 검증 wiring (Growth-10/11 open loop). 남은: FK 참조 무결성 검증, react adapter
