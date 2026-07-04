# Growth Archive Vol.01 — Growth-4 ~ Growth-60

> `growth-archive.md`(인덱스) 산하 볼륨. 원문 무수정 이동. 규약: `docs/learn-logs/README.md`.

## Growth-4 ~ Growth-12 (2026-05-29 ~ 2026-06-01, 이동: Growth-20)

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

## Growth-13 ~ Growth-15 (2026-06-01, 이동: Growth-34)

### Growth-13 (2026-06-01) — self-improve 인덱스 (ledger-index) — think-grid 아이디어 흡수, 인프라 비채택

- **인격**: CTO (think-grid 평가·설계 계약·integrator 판정·환류) + Engineer (ledger-index.py 구현·검증)
- **Axis touched**: creater (self-improve 도구 — `scripts/ledger-index.py` 신규, diagnose.py 형제)
- **Milestone**: M1 (지식 누적 메커니즘 자체의 확장성 — 인격 증가·Growth 누적에도 cross-agent 통합이 O(전체)→O(관련))
- **Revenue/cost**: 0 LLM / 0 신규 infra (stdlib sqlite3) / Engineer 1 round + codegraph DB read-only 재사용
- **Why (1줄)**: 시간순 prose 원장(Σ860줄, 증가)을 통째로 읽던 cross-agent 통합을 `--symbol` scoped 조회로 — context-weight + 교차정보 통증의 공통 뿌리 해소
- **상세**: [cto.md#Growth-13](docs/learn-logs/cto.md), [engineer.md#Growth-13](docs/learn-logs/engineer.md)
- **결정 (CTO)**: think-grid 의 *아이디어*(심볼 앵커+백링크 검색)만 채택, *인프라*(sync-graph.js codegraph→.md mirror / Obsidian 의존 / node+sqlite3) **비채택** — 방금 token-savior→codegraph 로 없앤 "코드그래프 2개" redundancy 재발 방지. `.context/` dormant skeleton (0-byte, untracked) 은 우리 docs/learn-logs/ 와 중복이라 미채택. `_index.json` 은 gitignore(재생성 캐시, generated_from_commit=HEAD 가 커밋마다 stale → noisy diff 회피) — 초안 §4 commit 제안을 CTO 번복.
- **Cross-agent catch**: Engineer 가 `--symbol` 을 file-anchor basename 까지 확장 (CatalogValidator 가 body 백틱 아닌 Files-touched 경로에만 등장) → CTO integrator 승인 (검색 의도 부합, guards-must-work 데이터 silent 손실 금지와 일치). codegraph 교차검증으로 unverified 61 도 drop 없이 보존 — stale 앵커 탐지(`--check`)는 G-11 가드 후보로 남김.
- **Open loops resolved**: self-improve context-weight (CEO 제기). 남은: `--check` 의 G-11 가드 승격 여부, `/contribute-back` 에 인덱스 재빌드 hook, (선택) Obsidian `--md` 시각화

### Growth-14 (2026-06-01) — expert-agent end-to-end demo (creater 축 첫 채움 + 화면 초안 실증)

- **인격**: CTO (7축 결합 설계·옵션 공격검증·integrator·live agent 큐레이션 실행·환류) + Engineer (scaffold.py/manifest.py/frontend typed-form/G-11 구현) + QA (Phase 1 포맷 게이트 PASS) + axis-7 domain-expert-generic (live profile 큐레이션)
- **Axis touched**: creater (`scripts/workflow/scaffold.py`+`manifest.py` 신규 — 빈 orchestrator 축 첫 채움), frontend (vanilla-htmx manifest-driven typed form), expert-agent (catalog-aware 정렬), customer (`profiles/shop-demo.yaml`+`smallmfg-demo.yaml`)
- **Milestone**: M2 핵심 인수("당일 화면 초안") 실증 — 비전문가 needs → agent 큐레이션 → 실 entity 필드 화면
- **Revenue/cost**: M2 라이선스 게이트 직접 기여 / Engineer 3 round + agent 1 큐레이션 / 결정적 경로 0 LLM
- **Why (1줄)**: 6축은 자산화됐으나 엮는 orchestrator 부재로 end-to-end 증명 불가 — creater 축을 thin 하게 채워 7축을 화면까지 연결
- **상세**: [cto.md#Growth-14](docs/learn-logs/cto.md), [engineer.md#Growth-14](docs/learn-logs/engineer.md)
- **결정 (CTO)**: 옵션 B(field-aware) 채택 — A(generic 폼)는 가치 미증명, C(LLM 결정적 경로)는 테스트 불가. manifest 는 catalog 파생 derived artifact(`out/`, gitignore), wire contract 불변(프로토콜에 고객 entity 결합 금지). agent baseline 표 catalog 14 에 1:1 동기화(phantom entity 가 acme-erp 깨뜨린 근본원인 제거).
- **Cross-agent catch**: live agent 가 needs 의 `attendance`(출퇴근)가 catalog 미구현임을 스스로 잡아 escalation 보류 — catalog-aware 원칙 작동 확인. `sales-order.customer_id` 가 fk 블록 없어 text 분류 = FK 무결성 갭(별도 백로그) 실증.
- **Open loops**: acme-erp 비호환(domains customer/order ⊄ catalog) **CEO 결정 대기**(삭제 vs catalog 키로 수정) / react adapter(frontend 2nd) / FK 참조무결성 검증(G-12 후보) / `--serve` 자동기동

### Growth-15 (2026-06-01) — FK 참조 무결성 (catalog hygiene + G-12 + runtime 양 backend DIM-6)

- **인격**: CTO (3-part 설계·dangling/polymorphic 분류 결정·integrator) + Engineer (catalog 주석·G-12·양 validator·DIM-6) + QA (PASS-WITH-CAVEAT — 양 backend 로직 패리티 적대 검증)
- **Axis touched**: ddl (catalog FK hygiene 주석 + customer_id→contact fk), creater (G-12 가드), backend (양 adapter CatalogValidator FK 체크), middle (validation-contract §5 deferred→구현)
- **Milestone**: M1 검증 완결성 — Growth-12 가 명시 deferred 한 FK 참조 무결성 해소
- **Revenue/cost**: 0 신규 infra / Engineer 2 round(+1 재개) + QA 1 / acme-erp·shop-demo 재scaffold ripple
- **Why (1줄)**: Growth-14 가 `customer_id` dangling 을 실증 → catalog hygiene(정적) + runtime FK(동적) 양면 해소, "진짜 검증" 스토리 완성
- **상세**: [cto.md#Growth-15](docs/learn-logs/cto.md), [engineer.md#Growth-15](docs/learn-logs/engineer.md), [qa.md#Growth-15](docs/learn-logs/qa.md)
- **결정 (CTO)**: `*_id`-no-fk 10개를 polymorphic/circular(7, fk-exempt 마커)·backlog(machine/period, entity 미존재→domain-expert)·genuine(customer_id→contact fk) 로 분류 — catalog **성장**은 비포함. G-12 는 마커 기반(polymorphic false-positive 회피). runtime FK = fk 선언 컬럼만 enforce(exempt skip), VALIDATION_ERROR 재사용(신규 코드 0).
- **Cross-agent catch**: Engineer 가 CTO 목록 밖 10번째 컬럼(`report-output.triggered_by_id`) 발견·분류 + 오기(inspection-plan) 교정. QA 가 DIM-5 회귀(fake department_id)를 정당 수정으로 판정·Java live 미실행 caveat 명시.
- **Open loops**: **Java DIM-6 live 미실행 (JDK 환경 부재) — M1 sign-off 전 `pytest tests/adapters/springboot-jakarta/` 37 green 확인 + qa.md 기록 필수** / machine·accounting-period entity 신설(domain-expert) / ledger-index `--check`→G-13 후보 / react adapter (다음)

## Growth-16 ~ Growth-20 (2026-06-02 ~ 2026-06-11, 이동: Growth-37)

### Growth-16 (2026-06-02) — 2nd frontend adapter (react) — frontend 측 pluggability 완성

- **인격**: CTO (stack 결정·설계·integrator·QA caveat 즉시 클로즈) + Engineer (Vite+React18+TS adapter 20-파일 빌드 + F-2 hollow test 교체) + QA (PASS-WITH-CAVEAT — G-1 하드코딩 적대 grep, F-1~F-4 진위, 토큰 hex 0)
- **Axis touched**: frontend (`frontend/adapters/react/` 신규 — Stage 4 frontend 축 2번째, pluggability frontend 측 실증), creater (frontend INDEX.md manifest, G-5 트리거)
- **Milestone**: M1 — pluggable F/B 4-corner 완성 (backend springboot+fastapi × frontend vanilla-htmx+react)
- **Revenue/cost**: M1 baseline 완성도 / Engineer 1 빌드(background, 20 커밋)+1 fix / Node v24 가용으로 caveat 0 (Java 와 대비)
- **Why (1줄)**: backend 측 pluggability 는 증명됐으나(2 adapter) frontend 측은 vanilla-htmx 1개뿐 — react 로 "contract 만 stable, F 교체" 를 frontend 에서도 실증
- **상세**: [cto.md#Growth-16](docs/learn-logs/cto.md), [engineer.md#Growth-16](docs/learn-logs/engineer.md), [qa.md#Growth-16](docs/learn-logs/qa.md)
- **결정 (CTO, VP 위임)**: stack 확정 — Vite+React18+TS / **contract = 빌드타임 codegen**(wire-v1+codes→generated TS, 재구현 아닌 소비, G-1 클린) / **토큰 = CSS custom property**(frontend-adapter-contract §7 open fork 해소 — CSS-in-JS 아님, 공유 토큰 파이프라인 일관) / Vite proxy → BACKEND_BASE_URL / manifest typed-form(Growth-14) 런타임 fetch+generic fallback.
- **Cross-agent catch**: QA 가 F-2 offset-last-page 테스트가 hollow(순수 산술, adapter 미접촉)임을 적발 → CTO 가 즉시 engineer 에 위임, `hasMorePages` 순수 헬퍼 추출(ListScreen+test 공유, single-source) 30 test green 으로 클로즈. SPA router path 와 wire endpoint 구분 명확화(G-1 스코프).
- **Open loops**: react L4 는 fastapi 상대 검증됨(35) — springboot 상대 react L4 는 Java 환경서(위 Growth-15 carry 와 동일 게이트) / vue·nexacro adapter(M2 후) / react persona ceo·it 분기 미니멀(후속) / maturity threshold 정량화

### Growth-17 (2026-06-02) — GTM 피벗: demo-video 시나리오(CMO) + honest-marketing ops-pack 갭 적발

- **인격**: CMO (6-scene demo-video 시나리오·제작법($22)·배포 훅 작성) + CTO (integrator: Scene 4 sign-off / Scene 5 vaporware 적발 / 3-doc 동기화)
- **Axis touched**: 없음 (코드 0) — 비즈니스/마케팅 문서. M1 기술 성숙 후 첫 GTM 산출물
- **Milestone**: M1→M2 게이트 (demo 영상 + qualified lead). 기술 측 6/6 MET, GTM 측 시동
- **Revenue/cost**: demo 영상 = M2 pricing 공개 게이트의 GTM 절반 / 제작비 $22 1-shot (OBS+DaVinci+ElevenLabs+YouTube unlisted+Loom) / LLM·infra 추가 0
- **Why (1줄)**: M1 기술 성숙 달성 → CEO 가 GTM 피벗 확정, 비전문 3-페르소나가 "우리도 되나?" 라고 묻게 만드는 demo 영상이 M2 진입의 GTM 절반
- **상세**: [cmo.md#Growth-17](docs/learn-logs/cmo.md), [cto.md#Growth-17](docs/learn-logs/cto.md)
- **Cross-agent catch (honest-marketing G 정신)**: CTO 가 Scene 5(self-host)의 ops-pack(docker-compose+Vault+Keycloak SSO)이 **repo 에 미존재**함을 적발 — positioning.md 가 이를 IT-담당자 **M1 인수 기준**으로 명시했으나 미구현 (hero profile `vault_agent:false`). vaporware 하드 제약 위반 → CEO 판정.
- **결정 (CEO, 2026-06-02)**: ① ops-pack → **M2 deliverable 이관** (M1 기술 성숙 T-1~T-6 6/6 유지, ops-pack 불포함이 maturity 안 막음). ② demo Scene 5 **cut → ~3:00 영상** (live-verified 능력만, 로드맵 캐비엣보다 강함). positioning.md + revenue-roadmap.md 인수 triple 동기화.
- **Open loops**: demo 영상 실제 촬영(CEO 결정 대기: CTA URL / CEO voice Scene6 / publish 타이밍 / 샘플데이터 산업) / qualified lead 5건 / ops-pack 구축(M2) / Scene 4 react+springboot live 촬영(검증 완료, 촬영만)

### Growth-18 (2026-06-11) — 7번째 인격 PM 신설 (delivery loop) + LLM Wiki 방법론 리서치

- **인격**: CTO (역할·skill 설계, charter v1.4, LLM Wiki 리서치·채택안) — PM 인격은 CEO 직접 제안으로 신설
- **Axis touched**: 없음 (코드 0) — 조직/프로세스. PM 은 수요 측 loop 로 7축 환류 (step 7 contribute-back) 를 트리거하는 메타 역할
- **Milestone**: M2 (first paid customer — needs 발굴→인도 절차가 qualified lead 의 계약 전환 실행 경로)
- **Revenue/cost**: PM loop 1회전 \$2~5 가이드, 월 \$50 budget / 신규 infra 0
- **Why (1줄)**: 지금까지 공급 측 (자산 자율 성장) 만 있었고, 고객 질의로 needs 를 발굴·인도·환류하는 수요 측 절차가 부재 — CEO 가 PM 인격 + 실행 skill 신설 지시
- **상세**: [pm.md#Growth-18](docs/learn-logs/pm.md), [cto.md#Growth-18](docs/learn-logs/cto.md)
- **결정 (CEO 제안, CTO 실행)**: `pm-agent.md` + `pm-delivery-loop` skill (8단계, contribute-back 종료 게이트) / charter v1.4 (매트릭스 PM 열 + delivery sign-off 합의 행) / PM↔domain-expert 경계 = "무엇이 필요한가" vs "도메인적으로 무엇인가" / 커밋 trailer 모델 Fable 5 전환 (CEO /model 전환의 정직한 기록, Growth-8 전례)
- **Open loops**: **LLM Wiki 채택안 CEO 결정 대기** ([`docs/architecture/llm-wiki-adoption.md`](docs/architecture/llm-wiki-adoption.md) — knowledge/wiki + index.md + read-side 규약, zero-infra) / PM 인터뷰 질문 시트 초안 / PM 첫 실전 loop (M2 첫 고객)

### Growth-19 (2026-06-11) — LLM Wiki 채택 실행 — knowledge/wiki 골격 + qmd 검색 + 지식그래프

- **인격**: CTO (Phase 1·2 직접 + Phase 3 설계·위임) + Engineer (build_graph.py) — Growth-18 open loop 의 CEO 승인 ("진행하자", 인프라 차용 §6 추천 포함)
- **Axis touched**: creater (`scripts/wiki/build_graph.py` + qmd 검색 인프라), customer (`knowledge/wiki/` — 고객·도메인 횡단 지식 축적 위치 신설)
- **Milestone**: M2 (고객 지식 재사용 자산화 — 2번째 고객 한계비용 하락) + M3 (vertical agent 지식 기반)
- **Revenue/cost**: 신규 API 비용 0 (qmd 는 on-device GGUF) / ingest 당 LLM 증분 ~\$0.1
- **Why (1줄)**: 지식 축적 (쓰기) 과 context 비대화 (읽기) 의 공통 해법으로 Karpathy LLM-wiki 패턴 + qmd 채택 — 우리가 이미 가진 절반 (seed·learn-log·ledger-index) 에 빈 절반 (wiki·index·검색) 을 채움
- **상세**: [cto.md#Growth-19](docs/learn-logs/cto.md), [engineer.md#Growth-19](docs/learn-logs/engineer.md)
- **결정 (CTO)**: log.md 신설 안 함 (learn-log 단일 진실) / graph 는 derived → `out/` gitignore / CDN 0 self-contained HTML (사내망) / qmd embed 시맨틱은 선택 후속 / PATH 의 bun 고아 qmd shim 제거 (Windows 함정, cto.md 상세) / PM loop step 7 = wiki ingest 트리거 명문화
- **Open loops**: qmd embed 선택 실행 / qmd MCP·plugin 연결 / 첫 실전 ingest (M2 첫 고객 loop #1) / PM 인터뷰 질문 시트 (Growth-18 carry)

### Growth-20 (2026-06-11) — §6 슬림 회전 정책 (growth-archive) + ledger-index glob 확장

- **인격**: CTO (회전 정책·아카이브 이동) + Engineer (ledger-index glob 확장)
- **Axis touched**: creater (ledger-index 소스 확장), 헌장 운영 (§6 회전 정책 신설)
- **Milestone**: 전 milestone 공통 — 지식 누적 메커니즘 자체의 확장성 (Growth-13 계보)
- **Revenue/cost**: 0 LLM 런타임 / 0 infra
- **Why (1줄)**: G-9 슬림 cap 198/200 임계 — Growth-21 기록 불가 직전인데 회전 메커니즘이 없었음
- **상세**: [cto.md#Growth-20](docs/learn-logs/cto.md), [engineer.md#Growth-20](docs/learn-logs/engineer.md)
- **결정 (CTO Auto)**: Growth-4~12 를 **원문 수정 0 으로** [growth-archive.md](docs/learn-logs/growth-archive.md) 이동 + §6 포인터 1줄 (70/200 회복). founding 1~3 은 divider 앞 유지 (G-9 비카운트). 회전 정책 상설화: cap 접근 시 오래된 slim 엔트리부터 동일 절차. ledger-index 고정목록→glob (pm.md·archive silent 누락 동시 해소)
- **Open loops**: 없음 — 다음 회전은 cap 재접근 시

## Growth-21 ~ Growth-32 (2026-06-11, 이동: Growth-59)

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

## Growth-33 ~ Growth-48 (2026-06-11~13, 이동: Growth-64)

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

## Growth-50 ~ Growth-53 (2026-06-13, move: Growth-78 rotation)

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

## Growth-54 ~ Growth-67 (2026-06-13 ~ 2026-06-15, 이동: Growth-89)

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
