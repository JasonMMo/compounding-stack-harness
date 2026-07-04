# Growth Archive — main learn-log §6 slim 회전분

> `learn-log.md` §6 의 G-9 cap (200행) 운영을 위해 회전된 slim 엔트리 원문. **내용 수정 없이 그대로 이동** — 상세는 각 엔트리의 인격 ledger pointer 참조. founding 3건 (Growth-1~3 full 포맷) 은 main §6 divider 앞에 유지. 검색: `python scripts/ledger-index.py --symbol <name>` 또는 `qmd search -c docs`.

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

### Growth-66 (2026-06-15) — marketing-site track dogfood: 우리 자신의 M1 GTM 랜딩 + 3 실버그 수정

- **인격/Axis/Milestone**: CTO(통합·프로필·검증·커밋) + CMO(카피) + Engineer(파이프라인·모션·캡처 수정) / theme·frontend·creater / **M1 GTM**(랜딩=리드수집 자산, M1→M2 게이팅 "lead 5건")
- **1줄 rollup**: `profiles/gtm-landing.yaml`(deliverable_kind=marketing-site, theme=aurora) 로 우리 제품의 M1 GTM 랜딩을 track 으로 실제 산출(dogfood) — scaffold→site-manifest→landing-astro build→ui_check PASS(7/7)·desktop+mobile 풀페이지 시각 검증. Growth-65 가 만든 track 을 처음 end-to-end 로 태움.
- **dogfood 가 잡은 3 실버그(전부 수정)**: ① 반복 항목 미전달 — catalog→manifest→router 에 `items[]` 슬롯 부재로 feature 카드/FAQ 가 컴포넌트 데모 placeholder 로 렌더 → catalog `item_slots` + manifest 통과·검증 + router 전달 신설. ② `/favicon.svg` 404 — 어댑터에 `public/` 자산 부재 → 테마중립 기본 favicon 배포. ③ **stagger-children 모션이 컨테이너 영구 은닉** — `el.children` 만 reveal 하고 `el` 자신의 motion-hidden 미제거 → Features/Logos(둘다 기본 stagger) 가 모든 방문자에게 opacity:0. + reduced-motion 도 below-fold 은닉(a11y 결함). → 컨테이너 항상 reveal + reduced-motion 시 미은닉, ui_check 캡처도 reduced_motion 적용(vision-QA 신뢰성).
- **핵심 결정**: 정직성 — testimonial/구체 pricing 제외(M1 pricing 게이트), logos 제외(파트너 로고 자산 無 → placeholder 회피) / 트레일러 실제 co-author=Opus 4.8 반영(§9) / 교훈: **뷰포트 스크린샷만으론 below-fold 결함 못 잡음 — 풀페이지 캡처 필수**(ui_check viewport 검사가 hero 만 봐서 ②③ 놓칠 뻔).
- **상세**: [engineer ledger](docs/learn-logs/engineer.md) · [CDO ledger](docs/learn-logs/cdo.md)
- **결정 메모리**: [[marketing-site-track]]

### Growth-67 (2026-06-15) — 정적 marketing-site preview 레인 + n9n 공개 데모 2종 LIVE

- **인격/Axis/Milestone**: CTO(통합·배포 결정·검증) + Engineer(데모-스텁·Dockerfile) + DevOps(배포 레인·레지스트리) / frontend·creater·infra / **M1 GTM**(고객 시연 자산)
- **1줄 rollup**: marketing-site 는 정적 SSG(백엔드 無)라 기존 `deploy_to_coolify.py`(business-system: screen-manifest+SECRET_KEY+/login) 레인 불가 → **정적 preview 레인 신설**: 멀티스테이지 Dockerfile(scaffold+astro→nginx, ARG PROFILE_SLUG/DEMO_MODE) + `deploy_static_site.py`(demo-portal 스크립트 일반화, idempotent). **gtm-landing.n9n.co.kr**(우리 M1 GTM 랜딩, aurora) + **landing.n9n.co.kr**(랜딩 데모 인덱스 포털, demo-portal 형제) 2종 Coolify 배포·HTTPS 200·콘텐츠 검증 PASS.
- **함정/교훈**: ① Git Bash **MSYS 경로 변환** — CLI 인자 `/deploy/...`가 `C:/Program Files/Git/deploy/...`로 둔갑해 Coolify 422(format invalid). `MSYS_NO_PATHCONV=1`로 해소(하드코딩 Python 스크립트는 무사했던 이유). ② 연락폼 데모-스텁: `PUBLIC_DEMO_MODE=1` → 제출 시 네트워크 호출 없이 성공 메시지(백엔드 없는 시안에서 깨진 폼 방지), 실 POST 경로는 비데모 빌드에서 불변.
- **자산 레지스트리**: `infra/registry/{gtm-landing,landing-portal}.yaml` (status=live, coolify uuid 기록)
- **상세**: [devops ledger](docs/learn-logs/devops.md) · [engineer ledger](docs/learn-logs/engineer.md)
- **결정 메모리**: [[marketing-site-track]] · [[infra-stack]]

## Growth-68 ~ Growth-134 (2026-06-15 ~ 2026-06-30, 이동: Growth-143)

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

### Growth-99 (2026-06-20) — 한국어 형태소 분석기(pg_bigm/pgroonga) "조건부 장착·기본 비활성" 설계 근거 follow-up 박음 (M3 vertical)
- **1줄 rollup**: founder 질문("형태소 분석기 적용을 왜 미뤘나")에 코드 독립검증 후 답 — 미적용이 아니라 **조건부 opt-in + 기본 비활성**. 런타임 FTS 는 `to_tsvector('simple', …)`(형태소 없음, `retrieve.py`/06_chunk.sql:86), pg_bigm 는 `01_extensions.sql:14-22` 가 `pg_available_extensions` 가드로 감싸 있으면 켜고 없으면 plainto_tsquery degrade, pgroonga 는 주석 대안만.
- **유보 근거 4종(CTO 판단, follow-up 트리거 명시)**: ①preview/데모 티어 pgvector-only 이미지 호환 — 필수 의존으로 걸면 데모 깨짐(G-4 round-trip 정신, 환경차를 강결합화 금지) ②**하이브리드라 한계효용 낮음** — `'simple'` 토큰화 약점(동의어·어미변화)을 e5-base ANN 이 상쇄, RRF 병합이 두 약점 보완(`legal-rag-pattern.md §2`) → 형태소 분석기 marginal gain 이 FTS-only 대비 작음 ③운영비용 — pgroonga 별도 빌드+큰 이미지, mecab-ko 사전 운영부담, 데모 12청크엔 premature ④비-블로킹 — 정밀도 gap 인지·문서화됨, follow-up 일 뿐 게이트 차단 아님. **트리거: 한국어 substring recall 이 ANN 으로도 안 잡히는 실쿼리가 실고객 코퍼스(M2/M3)에서 발생하는 시점.**
- **정직성**: 새 코드 0 — 설계 근거 환류만. 메모리 legal-rag "미검증 리스크" 한국어 FTS 항목과 정합. [[legal-rag-mvp-build]] [[subagent-cross-service-verify]]

### Growth-100 (2026-06-20) — 법무 RAG 원문보기 슬라이드오버 구현(GET /documents + drawer) + founder 데이터제안 카테고리/저작권 정정 (M3 vertical)
- **1줄 rollup**: founder 요청("판례 데이터 추가 + 원문보기 우측 슬라이드 레이어, bigcase.ai 참고, 타당성 검토")에 대해 — **UI 기능은 구현, law.go.kr 실데이터 수집은 founder 결정 보류**로 갈라 진행(외출 중 "진행 가능하면 진행" 승인). engineer 위임 구현: `api.py` `GET /documents/{source_type}/{source_id}`(JWT+`rls_session` 강제, precedent=full_text/holding fallback, case_document=content_text·RLS 자동격리, 행없음→404 존재미노출 fail-safe) + web drawer(우측 translateX 슬라이드, role=dialog/aria-modal/포커스트랩/ESC·백드롭, 기존 tokens.css 준수). 이미 있던 `aria-disabled` "원문 보기 →" 버튼 활성화. 단위 118→**134 passed/4 skip**(CTO `rtk proxy pytest` 독립 재실행 검증), 5파일 per-file 커밋 2d7a5b9~0bd67b0 푸시.
- **타당성 검토 3분기(CTO)**: ①UI 슬라이드오버=타당(법률검색 표준 master-detail, 버튼 이미 stub, 원문직접표시=인용무결성 강화·생성아님=thesis정합) ②**"판례를 seed_case_documents.sql에 추가"=대상파일 오류** — 그 파일은 판례 아니라 **사건서류**(소장·준비서면, 가명필수=의뢰인비밀·CISO룰), 판례는 별도 `seed_precedents.sql`(22건 가상). law.go.kr엔 판결문만 존재(소장 없음) ③**law.go.kr 실데이터 자동수집=보류** — 판결문 자체는 저작권 비보호(저작권법§7)나 사이트 약관·편집저작권·"api 사용안함" 룰 + outward-facing ToS리스크 → 명시승인 전 미실행. **기능 구현엔 새 데이터 불요**(precedent.full_text 이미 채워짐).
- **검증/진단**: app.js 진단 `openDocDrawer not found`(line422)는 편집중 stale 스냅샷 — 함수선언 hoist(174정의/623참조) + `/search` 응답에 source_type/source_id 실존(api.py:198-199, retrieve.py:110) 소스레벨 정합 확인. Python import 에러는 app-dir 런타임해석 Pyright false-positive.
- **founder 게이트(복귀 후)**: ①브라우저 실검증(web/ bake-in→Redeploy 필요, drawer 표시·full_text·**박서연→이준호 사건문서 404 격리** 화면, Growth-97류 정적불가) ②law.go.kr/실판례 데이터 정책 결정 ③CDO drawer 비주얼 리뷰 ④cross-attorney 404 격리 실DB 통합테스트(C2 `pytest -m postgres` 자리 마련됨). [[legal-rag-mvp-build]]

### Growth-101 (2026-06-21) — 법무 RAG C2 postgres 통합테스트 6종 + C1 production 최소권한 하드닝 DDL (M3 vertical)
- **인격/Axis/Milestone**: CTO(스코프 확정·내부소스 정독·2-레인 병렬 위임·통합검증·per-file 커밋·푸시) + Engineer(C2 테스트 5+1) + DBA(C1 하드닝 DDL) / **backend(테스트)·ddl(하드닝)** / M3. 8커밋 1b27f1f..1b6b181 origin/master 푸시.
- **1줄 rollup**: Growth-100 게이트④ + open-loop(C2 `pytest -m postgres`, C1 production app_service 비-슈퍼유저) 동시 종결. **C2**: D5-dfd §9.5 흡수목록 6종 구현(미구현 6→0) — G-P7 재인제스트 멱등(upsert COUNT 불변)·G-P8a/b ingest_status done/error 전이·G-P17 `/search`→query_log +1·G-P19 app_user→legal_attorney `InsufficientPrivilege`·G-P15 RLS 검색격리(이준호 c001 가시/박서연 0건, verify-search.sh A/B의 pytest 등가). 공용 픽스처 `conftest.py`: `pg_conn` force_rollback 트랜잭션(DB 무오염)+`stub_embed_client`(사이드카 미접속·외부 API 0)+`DUMMY_VEC`. `LEGAL_RAG_DB_DSN_POSTGRES` DSN 게이트 — 미설정 시 자동 skip, 라이브 실행은 founder. **C1**: `presets/ddl/augments/legal/10_production_hardening.sql`(ADD-ONLY·production 전용·프리뷰 apply-schema 미포함) — `ALTER ROLE app_service NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION`(BYPASSRLS만 의도적 유지=ingest 교차사건 write+legal_attorney 로그인 read 필수, ≠슈퍼유저), 소유권 미의존 최소 GRANT(legal_attorney SELECT·chunk SELECT/INSERT/UPDATE·case_document SELECT+UPDATE(ingest_status,ingested_at) 열범위·precedent SELECT), query_log 비부여.
- **검증/진단**: 단위 **188 passed/10 skipped**(10 skip = postgres 마크 전량 DSN 미설정 자동 skip, 수집오류 0). `-m postgres` 단독도 10 skip 클린. Pyright 경고는 전부 false-positive — `ingest_file(**common)` dict-unpacking이 keyword-only 시그니처를 정적해석 못해 str→param 오인(런타임 정상), `import psycopg` 미해소는 dev env 부재(라이브 venv 존재, G-P19는 함수내 lazy import), stub `embed(text)` 미사용 인자=실 EmbedClient 인터페이스 일치용. docker 데몬 미가동이라 로컬 실 PG 미기동 — founder-gate skip 패턴(런북 §9 선례) 채택.
- **문서 환류**: 런북 §7 하드닝 7→8항목(#8 production 최소권한 절차+rolsuper 검증+G-P19 회귀게이트). D5-dfd §9.2 6행 미구현→구현됨·계수 미구현 0, §9.5 단언↔테스트파일 매핑표.
- **Open loops**: C2 6종 **라이브 실행은 founder 게이트**(실 PG+seed+ingest 필요, preview DB 준비됨) · C1 production 별도 owner 롤 분리(REASSIGN OWNED)는 법무법인별 연산자 결정(DDL은 문서화만) · G-88(seed UUID 가드)·WTP 인터뷰 3~5곳(PM) 미해결 잔존. [[legal-rag-mvp-build]] [[legal-rag-korean-lexical-pass]]

### Growth-102 (2026-06-21) — 법무 통합 제품 별도 adapter 결정 + `legal-pro` React 어댑터 Phase A 빌드 (M3 vertical)
- **인격/Axis/Milestone**: CTO(adapter 갈림길 확정·스코프 페이즈분리·검증 독립실행·검색계약 검수·푸시·원장) + Engineer(스캐폴드·검색화면 포팅·16 per-file 커밋) / **frontend** / M3. founder 가 stack 결정(AskUserQuestion): CTO 권장(라이브 vanilla-JS SPA 승격) 기각, **React+Vite 별도 어댑터** 택함.
- **1줄 rollup**: 법무 통합 제품(사건관리+판례검색)의 §5 미확정 갈림길 해소 — vanilla-htmx 위 theme 레이어 ✗, **별도 `frontend/adapters/legal-pro/` (React+Vite, `react` 어댑터 변형)** 로 확정. 동기: 7 데모가 한 디자인(vanilla-htmx)이라 의뢰자에게 "하나처럼" 보이는 약점 → legal 을 시각적으로 다른 프리미엄 제품으로. **Phase A**(차단없음) 빌드: 스캐폴드(package/vite/tsconfig/codegen/build-tokens) + legal-pro 테마 baked-in(build-tokens.mjs 가 `services/legal-rag/web/styles` 3 CSS 연결 — 라이브가 단일 진실, 재발산 방지) + `PrecedentSearchScreen.tsx`(app.js → React/TS 포팅) + LoginScreen(JWT). **Phase B**(사건관리 CRUD) = `/cases` G-1~G-6 미구현 + Q-1 스코프 미확정에 차단, App.tsx/README 에 마킹. 중간 contract 읽기전용(codegen 은 legal-rag 실 FastAPI 경로 + error 카탈로그만 읽음, 제너릭 wire 미사용).
- **검증/진단**: **L3 build PASS (CTO 독립 재실행)** — `npm run codegen && build:tokens && tsc --noEmit && vite build`, 38 모듈, dist(CSS 27.11kB/JS 175.08kB) 696ms. node_modules 존재 확인. IDE 진단(`process`/`vite`/`test does not exist`/`js-yaml` 미선언)은 LSP 가 빌드 tsconfig 대신 앱 tsconfig 로 vite.config·node 스크립트 해석한 false-positive — 실 `tsc --noEmit` clean. **검색 응답계약 보존 검수**(PrecedentSearchScreen 정독): `관련도 round(relevance*100)%`(rrf_score 폴백만)·citation `key=chunk_id` 1:1·환각0(반환 인용만)·키워드일치 뱃지(fts_rank)·"출처 인용만 제공" 무생성 note·AND·OR·empty/error/sidecar-down 모두 충실. 원문보기 alert()·사건필터 select 은 Phase B TODO 마킹.
- **문서 환류**: README §5 "미확정"→"확정"(별도 adapter + 페이즈표). 메모리 [[legal-unified-product-docs]] adapter 결정 블록.
- **Open loops**: Phase B 사건관리 CRUD(`/cases` G-1~G-6 엔드포인트 backend 선행 + Q-1 CRUD 범위 PM/founder 확정) · 원문보기 드로어(openDocDrawer, `/documents` 검증 필요) · legal-pro 어댑터 단위테스트 미작성(react 어댑터엔 4종 존재 — 후속) · L4 live(배포 후 HTTP) 미실행. [[legal-rag-mvp-build]] [[marketing-site-track]]

### Growth-103 (2026-06-21) — 법무 RAG `/cases` 읽기 backend 뚫기 + G-4 페이지네이션 (Phase B 부분 해제, M3)
- **인격/Axis/Milestone**: CTO(읽기/쓰기 스코프 분할·기존 라우트 감사 위임·pytest 독립검증·construction-site 정독으로 Pyright FP 기각·푸시·원장) + Engineer(페이지네이션 구현·테스트 23종) / **backend** / M3. 5커밋 dffcde0..f4a594b.
- **1줄 rollup**: legal-pro Phase B(사건관리 화면) 차단요인 중 **읽기측 해제**. 감사 결과 `GET /cases`·`GET /cases/{id}`(G-1)·`GET /documents`(G-3)는 **이미 구현돼 있었음**(Growth-100 포함) — 재구현 회피. 신규는 **G-4 페이지네이션**만: `GET /cases` 에 `limit`/`offset`(기본 50/0·최대 200) + COUNT(*) 진짜 total, `POST /search` 에 `offset`(기본0·≤500, RRF **후** 슬라이스로 랭킹·인용 1:1 불변). 전부 `rls_session`(app_user) 내 실행, 슈퍼유저 bypass 없음. **쓰기측(`POST/PATCH /cases`=G-2)은 Q-1(사건 CRUD 범위) 미확정에 의도적 보류** — list_cases docstring TODO.
- **검증/진단**: **pytest tests/ 211 passed/11 skipped (CTO 독립 재현, 0 실패)**, 11 skip=postgres-mark DSN 게이트. Pyright "offset/limit 인자 누락"(api.py 444/720/722/742)은 **stale-line FP** — 실 construction site `CasesResponse(cases,total,limit,offset)`(464)·`SearchResponse(...,offset=eff_offset)`(758)은 전 필드 명시, 모델은 `Field(0)`/`Field(50)` 기본값 보유(필수는 total). 진단 라인은 engineer 편집 중간상태 기준(720/722/742는 현재 log_query/CitationOut 위치). 테스트의 possibly-unbound FP 는 기존 lazy-import 패턴. embed-adapter 수집에러는 무관 기존파일(9bfaa12).
- **문서 환류**: D2 §9 갭표 동기화 후속(G-1 기구현·G-3 no-gap·G-4 해소·G-2 Q-1 보류) — 소규모 follow-up. 메모리 [[legal-unified-product-docs]].
- **Open loops**: G-2 쓰기(`POST/PATCH /cases`)=Q-1 사건 CRUD 범위 PM/founder 확정 선행 · legal-pro Phase B 사건화면(읽기 endpoint 준비됨, 프런트 위임 가능) · 페이지네이션 RLS 격리 라이브 실행=founder(postgres-mark) · D2 갭표 동기화. [[legal-rag-mvp-build]]

### Growth-104 — legal-pro Phase B 사건관리 read 화면 (기획 스펙 → 구현)

**맥락**: founder 가 A안(Phase B 프런트) 택함 + "legal-rag 때 적용한 기획단계 문서 작성하고 진행". D1~D5(제품 전체)는 이미 있어 0부터 재생성은 낭비 → **Phase B 구현 슬라이스용 빌드 스펙**을 PM 산출(D1~D5 관련 단면을 구현 계약으로 응축).

**기획 (PM, e101cbd)**: `docs/projects/legal/phase-b-spec.md` — CasesScreen(목록·페이지네이션) + CaseDetailScreen(상세·문서목록) read-only. 데이터 바인딩 표를 라이브 `api.py` CaseOut(8필드)/CaseDetailResponse(9필드)/CaseDocumentItem(4필드)와 1:1 정합(**CTO 독립검증 — 추측 0**). 생성/수정(G-2)은 Q-1 보류 out-of-scope 명시. 보존계약 4종(RLS·G-4·citation 1:1·middle 읽기전용) + AC-01~10. README §5 Phase B 를 read(차단해소·구현중)/write(Q-1보류) 분리(e9c4b9e).

**CTO 가 OQ 확정**: page size limit=20 / 전체 라우트 전환 / `?case_id=` query-param / 파트너캡션 제외(JWT claim 부재).

**구현 (engineer, 45c2bb9..a3057c8, 5커밋)**: wire.ts(apiListCases/apiGetCase) · CasesScreen · CaseDetailScreen · App.tsx(라우트·탭) · PrecedentSearchScreen(`?case_id=` 최소연결). L3 `npm run build` PASS(40 modules, CTO 재현 807ms). AC-01~10 코드 충족.

**가드 발동 — stale 진단 + 눈속임 의심 2건 다 CTO 직접 기각**:
1. 빌드 직후 LSP 가 App.tsx(CasesScreen/CaseDetailScreen/useLocation never read)·PrecedentSearchScreen(useSearchParams/selectedCaseId never read) 5건 "unused" 경보 → **소스 직접 읽어 전부 사용 확인**(144/152/50행, 244/299행). 편집 중간 스냅샷 stale FP. [[subagent-cross-service-verify]] 패턴 재현.
2. case_id 연동이 프런트만이고 백엔드 미필터면 "사건필터" 뱃지가 눈속임일 위험 → `api.py:712` 가 `hybrid_search(case_id=req.case_id)` 로 **검색 자체를 사건범위로 필터**(로그도 727행 기록) 확인. 연동 실제.

**revenue**: M3(법무 첫 버티컬) flagship 진전. **cost**: API 미사용(로컬 build·소스검증만). 잔여: L4 라이브(dist→Coolify 배포), 페이지네이션 라이브 단언(시드 ~6건/변호사라 20페이지서 미발화), G-2 write=Q-1 선행, 원문 drawer=G-3.

### Growth-105 — legal-pro L4 배포 준비 (전략 A: /pro 동일오리진) + Dockerfile 결함 가드

**맥락**: founder "배포부터". DevOps 가 서빙전략 + 설정 산출.

**전략 A (DevOps 권고·CTO 승인)**: legal-rag FastAPI 가 `/pro` 에 legal-pro dist 를 StaticFiles 로 추가 서빙(api.py:880 조건부 `if os.path.isdir`, 기존 `/app` 패턴과 일관). **동일 오리진 → CORS 0**, 새 서브도메인·Traefik 라우터 불필요. vite `base=/pro/` + BrowserRouter `basename=/pro` 정렬. multi-stage Dockerfile(Node20 build stage → dist 를 web/pro 로 COPY).

**가드 발동 — 배포 깨질 결함 CTO 적발**: DevOps 1차 산출(5커밋)이 **build 재검증 없이** 끝났고, Dockerfile Stage 1 이 어댑터를 `/src` 에 직접 COPY → prebuild(codegen/build-tokens)의 `REPO_ROOT=resolve(__dirname,'..'×4)` 가 `/` 로 해석 → `/middle`·`/presets`·`/services/legal-rag/web/styles` 부재 → **컨테이너 빌드 실패**. 로컬 `npm run build` 는 PASS(repo 경로 존재)라 founder 가 Redeploy 눌렀을 때만 깨지는 함정. CTO 가 REPO_ROOT 손계산 + prebuild 경로참조 grep 으로 근본원인 확정 → DevOps 에 repo-레이아웃 보존 COPY 구조 지시 → 수정(6aae618: 어댑터를 `/src/frontend/adapters/legal-pro` 에 두고 REPO_ROOT→`/src`, 의존 서브트리 3종 COPY). .dockerignore 가 그 경로 미배제 확인. 교훈: **빌드설정 변경은 변경한 환경(컨테이너)에서 재현해야 — 로컬 PASS 가 컨테이너 PASS 를 보장 안 함**. [[subagent-cross-service-verify]] 의 "thin wrapper 보고 단정 금지" 와 짝.

**라이브 트리거 경계**: 외부 API/SSH 금지(founder 룰) → DevOps 산출 = 로컬설정+절차문서+커밋까지, 실제 Coolify Redeploy 는 founder 실행. 절차: `deploy/preview/legal-pro.md`. **cost**: API 미사용. **revenue**: M3 flagship 데모 라이브화 직전. 잔여: founder Redeploy → `/pro` 스모크(7항목) → 통과 시 L4 종결.

### Growth-106 — legal-pro G-2 사건 쓰기: Q-1 확정 + C1(사건 메타 CRUD) 구현
- **Q-1 확정**(founder): 사건 쓰기 범위 = 사건+당사자+문서첨부, 삭제 영구배제(법적 감사), 생성자=담당변호사 본인. 원문보기(G-3)는 phase 2.
- **DDL/RLS 선완비 발견**: `02/04/05_*.sql` 에 case/case_party/case_document app_user INSERT·UPDATE RLS 정책 이미 존재 → G-2는 API 레이어만 추가(신규 DDL 0). 문서는 append-only(UPDATE/DELETE 정책 부재).
- **PM 빌드스펙** `docs/projects/legal/g2-write-spec.md`: 3 sub-phase(C1 메타/C2 당사자/C3 문서첨부+비동기ingest) 독립머지, AC-01~12(RLS 음성 4종 포함), CISO 업로드 게이트.
- **C1 구현**(engineer, 9커밋 381d5da..1226d61): `POST /cases`+`PATCH /cases/{id}`(api.py, rls_session SET LOCAL·assigned_attorney_id 서버주입·404 존재은폐) + CaseCreate/EditScreen + wire.ts + 라우트(/cases/new·:id/edit 정적우선) + 진입버튼. AC-01 PASS(pytest 244·npm build 0err). RLS 라이브 AC는 @pytest.mark.postgres 보류(founder DSN 게이트).
- **CTO 가드**: (a) 엔지니어가 DDL 불일치 보고(case_type CHECK에 other 없음) → 스펙 정합 수정(OQ-12). (b) 엔지니어가 API↔DB 실컬럼 교정(description→summary, opened_at→filed_date). (c) diagnostics 대량 발생했으나 전부 확정 FP(pydantic Field기본값·lazy import·stale never-read), App.tsx 라우트 실연결·RLS 주입 직접 소스검증.
- **CTO 판정**: OQ-11(party 노출) = C2에서 CaseDetailResponse에 parties 가산(additive, documents 패턴).
- 다음: C2(당사자 CRUD) → C3(문서첨부+ingest, CISO 게이트). C1 라이브 RLS AC는 founder DSN 실행.

### Growth-107 — legal-pro G-2 C2(당사자 parties CRUD, PII) 구현 + CTO 회귀 적발

- **범위**: G-2 sub-phase C2 — 당사자 등록/수정. `POST /cases/{case_id}/parties`·`PATCH /cases/{case_id}/parties/{party_id}` + 신규 `CasePartyOut`/`CasePartyCreateIn`/`CasePartyUpdateIn` 모델 + `CaseDetailResponse.parties` 가산(OQ-11 additive) + CaseDetailScreen 인라인 PartyPanel + wire/codegen. engineer 7커밋(86d1d0a..acffa0c).
- **DDL 선완비**: 05_case_party_rls.sql(RLS-only augment)에 select/insert/update 정책 이미 존재, role CHECK = plaintiff/defendant/witness/opposing-counsel/expert-witness. 신규 DDL 0.
- **CTO spec-vs-DDL 판정**: 스펙 name 256자·notes 2000자 → 렌더 컬럼 VARCHAR(255) 초과. C1 case_type 'other'와 동형, **DDL 충실하게 name·notes 255 cap** 확정(catalog `string` maxlen 미지정→렌더 기본 255, postgres 빌드 미체크인). pydantic max_length=255.
- **PII RLS→404 존재은폐 경계(CTO 직접 소스검증)**: create_party = RLS INSERT WITH CHECK EXISTS(legal_case 소유) 위반 → psycopg 예외 "policy" 매칭 → 404(타 변호사는 부모 case 비가시→EXISTS false→위반). update_party = RLS UPDATE USING 조용히 0행 + 이후 SELECT None → 404. 양쪽 사건·party 존재 은폐 확정.
- **CTO 회귀 적발(핵심)**: 엔지니어가 C1+C2 테스트 파일만 돌려 "70 passed" 보고했으나, CTO 전체 스위트 재현 → **2 fail**. get_case_detail에 parties SELECT(3번째 execute) 추가가 Phase B `test_case_detail_endpoint.py` 깨뜨림 — (a) mock 미갱신으로 `notes=pr[4]` IndexError, (b) "필드 불변" 단언이 새 parties 필드 미반영. **프로덕션 코드는 정상**(실 SELECT 5컬럼), 테스트 픽스처 staleness. 동일 엔지니어 재디스패치 → acffa0c 수정(parties fetchall mock + 필드셋 가산 + parties 라운드트립 단언). CTO 재현 **281 passed/17 skipped/0 fail**.
- **diagnostics 전부 확정 FP**: wire.ts party_create 미존재(실제 contract.gen.ts:19-20 존재)·CaseDetailScreen PartyPanel/handleRefresh never-read(line 568 렌더링·466 사용)·pydantic Field/lazy import possibly-unbound — npm build 0 error·pytest green로 교차확인.
- **하드닝 노트(향후)**: create_party 예외 substring 매칭("check"/"permission")은 pydantic 선검증 덕에 안전하나 psycopg SQLSTATE 42501(InsufficientPrivilege) 타입 캐치가 더 견고.
- **교훈**: 엔지니어 self-test 범위가 변경 파일에만 국한되면 cross-file 회귀를 놓침. CTO 게이트는 **반드시 전체 스위트 재현** — envelope의 "N passed"를 부분 스위트로 신뢰 금지. [[subagent-cross-service-verify]] 연장.
- 다음: C3(문서첨부+비동기 ingest, CISO 게이트) → 그 후 phase 2 G-3(원문보기). C2 라이브 RLS AC-05~07은 founder DSN 실행(@pytest.mark.postgres).

### Growth-108 — legal-pro G-2 C3(문서첨부+비동기 ingest) CISO 게이트 통과 + 푸시

- **범위**: G-2 sub-phase C3 — `POST /cases/{case_id}/documents`(멀티파트 업로드 → INSERT-before-write → FastAPI BackgroundTasks 비동기 ingest). engineer 9커밋(5bd1da9..c1c4047) + CTO 후속 4커밋(69d057e..544030f). config.storage_root·_sanitize_filename·_build_storage_key(uuid 접두 ≤255)·realpath+commonpath 경로방어·CaseDetailScreen DocumentUploadPanel(AC-11 5s 폴링)·python-multipart 의존성.
- **CTO 설계 정련**: 스펙 대비 INSERT 먼저(rls_session) → 파일 디스크 쓰기 순서. RLS 거부 시 고아 파일 0. 비동기 ingest는 fresh app_service(BYPASSRLS) 커넥션(요청 핸들러 커넥션 재사용 금지) + 예외 시 별도 커넥션으로 status=error(column-scoped grant 내).
- **CTO 잠복결함 적발(cross-cutting)**: 09_grants.sql에 app_user가 GRANT SELECT만 보유 — legal_case/party/document INSERT·UPDATE grant 부재. Postgres는 RLS 평가 前 table privilege 검사 → C1/C2/C3 쓰기가 실DB에서 "permission denied"로 전멸. 라이브 AC가 founder DSN 게이트(미실행)+유닛 mock이라 가려짐. dba-agent가 3 GRANT 추가(64e2480, 별도 푸시), document는 INSERT-only(append-only 04 정합).
- **CISO 게이트(PASS, BLOCK 0)**: `docs/projects/legal/security/c3-upload-review.md`. 경로탐색 이중방어·확장자(x.pdf.exe→거부)·RLS 404 존재은폐·BackgroundTask 격리·외부egress 0 PASS. CAVEAT 4건 중 **2건 본 패스에서 해결**: D(substring→psycopg 타입캐치 SQLSTATE 42501, 69d057e) + G(python-multipart>=0.0.18 CVE-2024-53498, ace99cb). A(file.read 무제한 OOM)·AC-12(영구볼륨)→deploy/legal-pro.md §9 배포가이드(544030f). C(magic bytes 미검증, Low)→보류.
- **CAVEAT-D 환류(C1/C2/C3 3회 반복 가드의무)**: RLS 위반 판별을 예외 메시지 substring("policy"/"check"/"rls"/"permission")에서 `psycopg.errors.InsufficientPrivilege`(42501) 타입캐치로 교체 — CHECK제약(23514) 오탐 제거. create_case(Unique→409, 42501→403)·create_party·upload(42501→404). psycopg.errors는 ModuleNotFoundError 폴백(prod 항상 존재).
- **CTO 검증 함정 2건**: (a) 직전 세션 CTO pytest "No tests collected"는 **영속 cwd가 services/legal-rag**라 rootdir 오판 — 올바른 디렉터리에서 313 passed/19 skipped 재현(이후 subshell `(cd …)`로 cwd 보존). (b) 같은 영속 cwd가 상대경로 PreToolUse 훅(large_file_guard/output_filter)을 깨뜨려 Bash/Read 데드락 → **PowerShell Set-Location으로 공유 세션 cwd 리셋**해 복구(메모리 subagent-cwd-hook-fragility 재현, 메인세션도 영향). 교훈: Bash `cd X &&`는 영속 — 항상 subshell 또는 절대경로.
- **검증**: CTO 전체 스위트 재현 **313 passed / 0 fail / 19 skipped**(타입캐치 후 회귀 0). 라이브 RLS AC-08/AC-10(@pytest.mark.postgres)은 founder DSN+STORAGE_ROOT 게이트.
- 다음: **phase 2 G-3 원문보기** — founder가 "원래 되던 기능(구 /app openDocDrawer)"으로 지적. 백엔드 `GET /documents/{source_type}/{source_id}`(api.py:1587) + `.doc-drawer` CSS 완비, React 어댑터 wire/컴포넌트만 미배선(PrecedentSearchScreen alert 스텁). 판례(full_text)는 즉시 동작 가능, 사건문서(content_text)는 OQ-10 의존. C3 라이브 AC·Coolify 영구볼륨은 founder.

### Growth-109 — legal-pro G-3 판례 원문보기 드로어 React 재배선 + 푸시

- **범위**: phase 2 G-3 — founder가 "원래 되던 기능인데 안붙어있다"로 지적한 판례 원문보기. 구 vanilla SPA(`/app` web/app.js openDocDrawer)가 React 어댑터 이관 시 `alert(...)` 스텁으로 회귀한 것. engineer 3파일(e11e869 DocDrawer 신규 / 863e9cb wire / b047399 PrecedentSearchScreen). 백엔드 `GET /documents`(api.py:1587)·`.doc-drawer__*` CSS는 완비 상태라 미변경, React wire/컴포넌트/버튼만 배선.
- **구현**: (1) wire.ts `apiGetDocument` — `LEGAL_RAG_ENDPOINTS.document_read` 상수 치환(encodeURIComponent)+Bearer(legalRequest 경유), `DocumentReadOut`는 백엔드 `DocumentResponse`(api.py:283) 12필드 1:1 미러, legalRequest에 404→`code='NOT_FOUND'` 분기 추가(기존 INTERNAL 덮어쓰기 수정). (2) DocDrawer.tsx 신규 — loading/error/success 3상태, 404 전용 메시지, ESC·백드롭 닫기, is-open 트랜지션, 판례 메타행+holding fallback 뱃지, case_document body 미충전(OQ-10) 안내. (3) PrecedentSearchScreen — alert 스텁 제거→drawerTarget state+openDrawer/closeDrawer, CitationCard에 onOpenDrawer 전달, DocDrawer 조건부 렌더.
- **CTO 통합검증(envelope 독립검증)**: engineer가 "build PASS"라 보고했고 IDE 진단은 `onOpenDrawer` 미배선/미사용을 표시(stale, 편집 중 스냅샷 — 라인번호도 최종본과 불일치). **직접 4중 확인**: ① 실제 파일 read로 렌더구역 배선 확인(491·499-505) ② `npm run build` 재실행 → tsc 0 err·vite 43 modules PASS ③ 백엔드 DocumentResponse 12필드 ↔ DocumentReadOut 1:1 grep 대조 ④ `.doc-drawer__*` 13클래스 tokens.gen.css 실존 grep 확인. 전부 정합. [[subagent-cross-service-verify]] 적용 — envelope "build PASS"도 stale 진단과 충돌 시 재현 필수.
- **결과**: 판례(full_text) 즉시 동작 = "원래 되던 기능" 회복. 사건문서(content_text) 원문은 OQ-10(content_text 충전) 의존 보류 — DocDrawer는 양 source_type 일반화, case_document 빈본문 시 안내문. CaseDetailScreen 사건문서 버튼(aria-disabled) 미변경.
- 다음: 라이브 검증은 founder Coolify Redeploy(C3+G-3 동반 반영, STORAGE_ROOT=/data/legal-docs/case-uploads 기존 영구마운트 하위로 설정 완료) 후 `/pro/search` 원문보기 스모크. C3 라이브 RLS AC·STEP3 업스트림 바디제한(Traefik buffering, CAVEAT-A)은 founder/후속.

### Growth-110 — legal G-2 C3 라이브 첫 배포 3갭 해소 (문서업로드 end-to-end LIVE)
- 트리거: founder 라이브(/pro) 테스트에서 G-2 쓰기 4건 실패 → CTO 코드 핑거프린트 진단. **코드는 정상, 전부 배포환경 갭 3개**.
- 갭1 **DB grant 미적용**: 09_grants.sql INSERT/UPDATE(L27-29) 라이브 미반영(앱 Redeploy는 DDL 미실행 — DDL-in-repo≠live-DB). 증상 사건생성403(api.py:828)/당사자추가404(1038)/당사자수정500(update_party는 42501 catch 無). 확증: role_table_grants에 app_user의 query_log INSERT만 존재. 수정: Coolify db Terminal서 GRANT 6줄 한줄씩 재적용(웹터미널 heredoc 깨짐 → -c 분리).
- 갭2 **compose passthrough 누락**: app environment에 LEGAL_RAG_STORAGE_ROOT 매핑 부재 → 컨테이너 미주입 → 500(api.py:1273). 수정 커밋 e5d7dd9.
- 갭3 **bind-mount 비-root 쓰기**: appuser(Dockerfile:67) vs root소유 /data/legal-rag/ingest → 파일쓰기 except 500(api.py:1338-1355). 수정: 호스트 `mkdir+chmod 0777 case-uploads`(preview; prod는 chown UID+0750). redeploy 불요·존속.
- 환류: 런북 deploy/preview/legal-pro.md §9 재구성(b6353c4). compose 패스스루 e5d7dd9/3eae1a3.
- 결과: founder 4건 전부 라이브 PASS. 문서 pending→done(폴링 5회=정상). 인격: CTO 진단·integrator, DevOps 런북·compose(위임), CISO 0777 preview-caveat.
- §6 rollup: [Growth-110] G-2 C3 라이브 3갭(grant/compose-env/bind-perm) 해소 → 문서업로드 LIVE. → docs/learn-logs/{devops,security}.md

### Growth-111 — legal-pro G-3 판례 원문보기 라이브 스모크 PASS (phase 2 종결)
- 트리거: founder Redeploy 후 `/pro/search` 판례검색 → [원문 보기] 라이브 확인 = "정상적으로 보인다". Growth-109 React 재배선(DocDrawer/wire/PrecedentSearchScreen)이 실배포에서 동작 확증.
- 결과: **phase 2 G-3 end-to-end 종결** — 판례(full_text) 드로어 즉시 표시 = 구 vanilla `/app openDocDrawer` 기능 React 어댑터(`/pro`)에서 완전 회복. 사건문서(content_text) 본문은 설계대로 OQ-10(content_text 충전) 의존 보류, DocDrawer 안내문 표시.
- 라이브 검증 0추가 코드 — Growth-109 재배선 + Growth-110 동반 Redeploy로 이미 반영. founder 스모크가 최종 게이트.
- 잔여(후속·founder 게이트): 라이브 RLS AC(AC-08/10, founder DSN @pytest.mark.postgres)·STEP3 Traefik 바디제한(CAVEAT-A, prod 전 필수)·OQ-10 case_document content_text 충전·prod bind-mount 하드닝(chmod 0777→chown UID+0750).
- §6 rollup: [Growth-111] G-3 원문보기 `/pro` 라이브 PASS → 통합 법무제품(G-2 쓰기 + G-3 원문보기 + 판례 RAG검색) end-to-end LIVE.

### Growth-112 — lawfirm-demo 메인 데모 격상: 4도메인 가상 데이터 + 포털 카드 재포지셔닝
- 방향(founder): lawfirm-demo(법무법인 전반 업무 메뉴)를 **메인 데모**로, legal-pro(`/pro` RAG)는 **killer app 링크**로. 포털 법무 카드 1장 + lawfirm-demo 내부 양쪽(배너+메뉴) 크로스링크. 두 앱은 물리적 별개(다른 배포·DB·로그인)임을 정직 표기.
- 포털 카드: 이미 repo 커밋됨(8dcbf8d)이나 demo-portal 미배포로 라이브 부재 → 문구 강화(통합 업무관리+AI 판례검색 부각, 358e52e). founder Redeploy 시 반영.
- B1 데이터(DBA 위임): 14테이블 4도메인(legal/hr/document/approval) 스키마 전부 존재·데이터만 공백 확인. 가명 30인 법무법인 증분 시드 `scripts/demo/seed_lawfirm_full.py`(신규 1083줄) + setup_lawfirm.py importlib 연동. 부서5/직원14/판례12/사건10/당사자28/사건문서22/카테고리6/문서10/버전14/접근규칙8/결재요청7/단계13/결재자14/결정10. 멱등(ON CONFLICT DO NOTHING), 컬럼은 out DDL 1:1.
- **CTO 게이트 결함 적발**: DBA가 `py_compile PASS`로 보고했으나 Pyright 진단이 `_E3` 미정의 노출. py_compile은 문법만 검사 → module-level dict 평가 시 NameError로 시드 전멸. `_E3`→`_EMP3`(베이스 직원) 수정 + **실제 import 검증**(모든 모듈스코프 리터럴 평가) 재게이트 통과. 교훈: 시드/리터럴 스크립트 검증은 py_compile 불충분 → import 실행 필수. [[subagent-cross-service-verify]] 연장.
- 라이브 적용은 founder(`DATABASE_URL=... python scripts/demo/setup_lawfirm.py`, no-SSH/API 경계).
- 다음: B2 killer-app 링크(배너+메뉴) → D1~D5 문서(데이터 기준) → DFD 검증 → 영업/인도물 패키징.
- §6 rollup: [Growth-112] lawfirm-demo 메인 데모화 — 4도메인 가상데이터 시드 + 포털 카드 강화(killer app legal-pro 부각).

### Growth-113 — lawfirm-demo killer-app 크로스링크(B2): env 구동 배너+사이드바 양쪽

- **B2 완료**: lawfirm-demo 화면 상단 배너 + 좌측 메뉴 양쪽에 "AI 판례검색 ↗" 링크 → legal-pro(`legal-rag.n9n.co.kr/pro`). founder "양쪽" 요구 충족.
- **개방-폐쇄 설계**: base.html(전 데모 공유) 하드코딩 대신 `KILLER_APP_URL` env 구동 조건부(기존 MASTER_DETAIL_ENTITIES env 패턴 답습). lawfirm-demo compose env에만 배선 → 그 데모에만 노출, 타 데모 무영향. 향후 타 프로파일도 env 한 줄 재사용. 4커밋(server 59e20da/base cbf8953/css d5c13c6/compose 602c6b9).
- **정직 표기**: target=_blank rel=noopener + "외부 시스템 · 별도 로그인 필요"(SSO 아님 — 물리적 별개 배포·DB·로그인).
- **CTO 게이트**: engineer 산출 독립 검증 — server.py g_killer_app(인증 한정·미설정 None) 정확, base.html 삽입 위치 정확, app.css 참조 토큰 전부 tokens.css 실존 확인(--color-primary-subtle/--color-text-on-primary 등), AST+Jinja PASS. 표시된 Pyright 진단은 기존 Flask 타입 쿼크(무관).
- engineer 보고 KILLER_APP_URL 후보가 루트(`/`)였으나 CTO가 killer app 실체=legal-pro `/pro`로 정정 배선.
- **founder 액션**: lawfirm-demo Coolify Redeploy → 배너/사이드바 라이브. (env는 compose에 배선됨 — 수동 입력 불요)
- §6 rollup: [Growth-113] lawfirm-demo killer-app 크로스링크(B2) — env(KILLER_APP_URL) 구동 배너+사이드바 양쪽, legal-pro /pro 연결. B2 종결, D1~D5 문서 단계 진입 대기.

### Growth-114 — lawfirm-demo D1~D5 문서 5종 + DFD 검증(결함 1 적발, BLK-D5-8)

- **D1~D5 전 문서 완성**(docs/projects/lawfirm-demo/): D1 기능명세(402)·D2 유저플로우(503)·D3 와이어프레임(439)·D4 ERD(552)·D5 DFD(724). 전부 **실제 시드 데이터 + 실제 server.py 라우트 + 실제 out DDL 기준**, killer-app 경계(별개 DB·SSO없음) 정직 표기. 3중용도(영업·인도물·구현입력).
- **CTO 독립 게이트 전건 수행**: D2 라우트 ↔ server.py 1:1, D4 ERD의 FK·ON DELETE 정책 ↔ out DDL **정확 일치**(assigned_attorney_id RESTRICT, principal_id/subject_id 다형+UNIQUE/인덱스, CASCADE/RESTRICT/SET NULL), D3 셸 ↔ base.html(g_killer_app 조건부) 정합. 날조 0.
- **DFD 검증(QA)**: D5 34 검증포인트 정적 감사(seed↔DDL). scripts/demo/dfd_verify.py(160줄, 외부DB 불요 import 검증) rc=0, 시드 FK 무결성 전항목 OK. 25 PASS / 1 FAIL / 9 N-A(인증·런타임 → founder 라이브검증 이관).
- **DEFECT-1(CTO 확인)**: `presets/ddl/catalog.yaml:1349` approval-decision.step_id `on_delete: restrict` ↔ 부모 체인(approval-step.request_id cascade:1309, approver.step_id cascade:1329) 불일치 → decision 존재하는 결재요청 삭제 시 cascade가 RESTRICT 리프에서 막혀 FK 위반. generic baseline catalog 결함. **수정 방향은 설계 판단**(cascade-all 단순화 vs decision 불변성 audit). 데모엔 cascade 권장(1줄+regen). QA BLOCK 정당.
- **flaky 교훈**: design-agent 대용량 단일 Write 2회 stream-idle timeout → 읽기 2개 한정+≤350줄 집약 지시로 3회차 성공(439줄). 큰 산출 서브에이전트는 입력·분량 타이트 제약이 안정적.
- **founder 액션**: ① DEFECT-1 수정 방향 결정 ② demo-portal/lawfirm-demo Redeploy ③ 시드 라이브 적용. 잔여: DEFECT-1 fix+regen, 패키징(영업/인도물).
- §6 rollup: [Growth-114] lawfirm-demo D1~D5 문서 5종 완성(실데이터 기준·CTO 게이트 전건) + DFD 정적검증(dfd_verify.py, 25P/1F/9NA) — DEFECT-1(approval cascade 불일치, catalog:1349) 적발·BLOCK. 패키징·fix 대기.

### Growth-115 — DEFECT-1 수정: approval-decision CASCADE 통일 + 회귀 가드 강화 (BLK-D5-8 RESOLVED)

- **founder 승인**: "CTO 의견에 동의" → DEFECT-1 cascade 수정 착수.
- **근본 위치는 catalog**: out DDL 직접수정이 아니라 `presets/ddl/catalog.yaml` approval-decision 엔티티 수정(단일 진실, regen 산출). 복리식 축적 — 전 프로파일 재발 방지.
- **CTO 게이트가 최초 QA 권고를 정정**: D5 보고서 초안 권고는 "step_id 만 CASCADE, approver_id 는 RESTRICT 유지(approver 단독삭제 방지)"였으나 **체인을 완전히 못 푼다**. catalog 정의순서상 approval_approver 가 approval_decision 보다 먼저 생성 → PG 가 approval_step cascade 시 approver 를 먼저 삭제 → 그 시점 살아있는 decision.approver_id RESTRICT 즉시 발동 → 재차단. 따라서 **두 FK 모두 CASCADE**(CTO 원안 "cascade 로 통일"과 일치). 서브에이전트(QA)/문서의 권고도 CTO 독립검증 대상이라는 [[subagent-cross-service-verify]] 패턴 재확인.
- **수정 3파일**: ① catalog.yaml step_id+approver_id restrict→cascade(5639a8f) ② dfd_verify.py VP-P8-07 가드 강화(0faaae4) ③ DFD 보고서 BLOCK→PASS(99e7433). out DDL 은 scaffold.py regen(gitignored).
- **회귀 가드 교훈**: 기존 VP-P8-07 은 `'ON DELETE CASCADE' in DDL` 부분일치 → DEFECT-1 을 **스크립트가 못 잡았다**(보고서 FAIL 은 QA 수동판정). approval_decision CREATE TABLE 블록 파싱해 두 FK 모두 CASCADE 직접확인하도록 교체. 약한 substring 가드 = false PASS 위험 패턴.
- **재검증**: `dfd_verify.py` rc=0, RESULT PASS=35 / FAIL=0 / N-A=9. VP-P8-07 PASS.
- **guard 노트**: diagnose.py G-8/G-9/G-12 FAIL 은 선존(G-12 위반=document-chunk/rag-query-log 엔티티, approval 무관). 내 변경은 fk 마커 보존·on_delete 값만 변경 → G-12 무영향 확인.
- **잔여**: 패키징(PM/CMO 영업·인도물), 9 N-A 라이브검증(founder Redeploy 후).
- §6 rollup: [Growth-115] DEFECT-1 수정 — catalog approval-decision 두 FK CASCADE 통일(QA 초안권고 CTO 정정: approver_id 도 cascade라야 체인 무결) + VP-P8-07 회귀가드 강화. dfd_verify rc=0/35P·0F. BLK-D5-8 RESOLVED.

### Growth-116 — lawfirm-demo 패키징: 인도 README + 영업 원페이저 (PM/CMO 병렬)

- **잔여 1 패키징 종결**: lawfirm-demo 메인데모 인도 패키지 2종 산출. PM/CMO 병렬 위임(다른 파일 → 충돌 없음).
- **PM**: `docs/projects/lawfirm-demo/README.md` — D1~D5+검증보고서 6문서 인덱스 표, 3페르소나(CEO/업무담당자/IT)별 관심문서 안내, 메인데모↔legal-pro 관계도(ASCII)+정직성 경계(별개 배포·DB·SSO아님), 구 `docs/delivery/lawfirm-demo/`(FTS 단독) 포함·확장 관계, founder Redeploy 잔여액션, 보안경고(CAVEAT-A Traefik 바디제한).
- **CMO**: `docs/projects/lawfirm-demo/sales-onepager.md` — 핵심 가치제안, 페르소나별 베네핏, self-host vs SaaS 비교표, 5분 영업 데모 스크립트(4도메인 순회→killer-app 핸드오프), 정직 고지 인라인(생성형 아님·SSO 미지원).
- **CTO 게이트(독립 소스검증)**: ① README D1~D5+검증보고서 링크 6건 전부 실존 ② 시드 수치·DFD결과(PASS=35/FAIL=0/N-A=9) 정확 ③ CMO 마케팅 주장 `GET /health` 의심→`frontend/adapters/vanilla-htmx/server.py:735` 실존 확인(날조 아님) ④ 판례 드로어·하이브리드 검색 모두 기실현 기능. 날조 0.
- **교훈**: 마케팅 산출물의 기능 주장은 [[subagent-cross-service-verify]]대로 CTO가 소스 1건씩 확인(/health 실존 검증). 영업 카피라도 검증가능성이 신뢰자산.
- **잔여**: 9 N-A 라이브검증(인증·런타임) — founder가 demo-portal/lawfirm-demo Redeploy + 시드 라이브 적용 후. (코드/문서 측 lawfirm-demo 메인데모 트랙 종결, 이후는 founder 게이트)
- §6 rollup: [Growth-116] lawfirm-demo 패키징 종결 — 인도 README(PM)+영업 원페이저(CMO) 병렬 산출, CTO 게이트 전건(링크 실존·시드수치·/health 소스확인). 잔여=founder Redeploy 후 9 N-A 라이브검증.

### Growth-117 — lawfirm-demo 라이브 시드 배선: SEED_FILE 경로(in-memory 백엔드 적재)

- **stale 가정 적발(CTO probe)**: "#3 시드 라이브 적용 = `DATABASE_URL=... setup_lawfirm.py`"는 부정확. 소스 확인 결과 라이브 lawfirm-demo(Coolify)는 저장소 2분리 — business 엔티티(사건/문서/결재)=백엔드 `InMemoryEntityStore`(SEED_FILE json 또는 wire), 판례검색=`legal.py`→postgres. **라이브 compose엔 postgres·DATABASE_URL·SEED_FILE 전무.** demo/demo 직접 로그인 probe로 `/entities/legal-case` 0건·`/legal/search` "결과없음" = 양 스토어 빈 셸 확정. founder가 Coolify Environment 탭 확인 → DATABASE_URL/SEED_FILE 미설정 교차확인.
- **경로 결정**: Option A(SEED_FILE) 채택. B(lawfirm-demo 자체 postgres 판례 FTS)는 **killer-app(legal-pro, LIVE)이 AI 판례검색을 이미 커버 → 중복**이라 생략. 데모 흐름의 판례검색=legal-pro 핸드오프.
- **기존 인프라 재사용**: `seed-data/*.json`(7개 데모 선례) + Dockerfile이 `seed-data/`→`/app/seed-data/` 굽음(line33) + `store._load_seed_file`(SEED_FILE env). **빠진 건 lawfirm-demo.json 하나뿐.** scp·bind-mount 불요(이미지 빌드시 베이크) → founder Redeploy만.
- **engineer 산출(3파일)**: ① `scripts/demo/gen_seed_lawfirm_json.py` 생성기(base+new 14엔티티 직렬화, 건수 self-assert, 멱등, 실제 import 검증) ② `seed-data/lawfirm-demo.json` 173건 ③ compose backend `SEED_FILE` env. 6ad481c/c09b018/10b8c2c.
- **CTO 게이트(독립 검증, envelope 불신)**: entity_type 키 manifest 14개 1:1, id 전건 유니크, 레코드 필드 manifest 부합, **FK 무결성 11종 dangling 0**(legal-case.assigned_attorney_id·case-party.case_id·approver.step_id·approval-decision.approver_id·document.current_version_id 등), `store._load_seed_file` 독립 dry-run 173건 무경고. Pyright 진단 4건(importlib Optional None-access)→`sys.path` import 패턴(dfd_verify 동일)으로 정리.
- **교훈**: manager_id/current_version_id처럼 **postgres POST-INSERT UPDATE로 채우는 값은 in-memory 스토어(UPDATE 없음)에선 최초 로드 시점에 backfill** 필수. postgres 시드 ≠ in-memory 시드(스토어 의미론 차이). [[subagent-cross-service-verify]]대로 FK 무결성·store 호환을 CTO가 직접 재현.
- **잔여**: founder lawfirm-demo Coolify Redeploy → 4도메인 라이브 데이터 확인 → 9 N-A 라이브검증.
- §6 rollup: [Growth-117] lawfirm-demo 라이브 시드 배선 — stale 가정(setup_lawfirm postgres) 적발·정정, Option A(SEED_FILE in-memory) 채택(B는 killer-app 중복 생략). 생성기+173건 json+compose env, CTO 게이트 FK 11종 dangling0·store dry-run 무경고. founder Redeploy 대기.

### Growth-118 — lawfirm-demo 라이브 종결: Redeploy + 9 N-A 라이브검증

- **founder Redeploy 완료**: 4도메인 라이브 데이터 렌더·legal-pro 링크 동작 확인. SEED_FILE 자동 적재 확증(CTO probe: /entities/legal-case 10행·/entities/approval-request 7행 approved4/in-progress1/pending1/rejected1).
- **9 N-A 라이브검증(CTO HTTP probe, demo/demo)**: 7 PASS — VP-P1-01 틀린비번 401+한글, P1-02 무세션 302, P1-03(proxy) 무효토큰 302, P1-04 로그아웃후 옛쿠키 302(서버세션무효화), P1-05 4도메인14엔티티+killer배너, P3-03 없는키워드 200+"결과없음"(에러아님), P5-04 ingest done→pending store.patch 무가드 허용(비파괴 소스검증). **2 N-A 유지**: P8-08/09 결재 워크플로 자동전이 — **generic CRUD에 상태머신 부재**(status 수동필드), 결함 아니라 business-system 산출물 범위. DFD 작성자 "app layer runtime" N-A와 일치.
- **정직 고지**: 실 결재 워크플로 전이 원하면 백엔드 커스텀 로직(별도 기능). 시드 다양상태로 데모 화면은 사실적.
- **검증 비파괴 원칙**: P5-04는 라이브 시드 훼손 회피 위해 store.patch 소스 의미론으로 검증(throwaway 레코드 주입 회피). founder가 막 데모 가동한 환경 존중.
- **lawfirm-demo 메인데모 트랙 완전 종결**: 정적 35 PASS + 라이브 7 PASS, 미해결 결함 0. D1~D5 문서·DFD·DEFECT-1 fix·패키징(README/원페이저)·라이브 시드·라이브검증 전부 완료. M1 generic harness baseline 기여.
- §6 rollup: [Growth-118] lawfirm-demo 라이브 종결 — Redeploy 후 9 N-A 라이브검증 7 PASS/2 N-A(워크플로 범위). 시드 라이브 확증(case10·approval7). 메인데모 트랙 완전 종결, 미해결 결함 0.

### Growth-119 — legal-rag pg_bigm 라이브 활성화 → OR `=%` 퇴행 적발·DROP 롤백 → OR→LIKE 재배선 + 테스트 사각 폐쇄

- **활성화 시도→퇴행 적발**: founder가 pg_bigm `CREATE EXTENSION`+인덱스+Redeploy 했더니 검색 키워드 뱃지가 **사라짐**. CTO 라이브 진단(psql): `chunk_text =% '손해배상'`(sim_limit 0.1)=**0행** vs tsquery=**22행**. 근본: retrieve.py OR+bigm이 `=%`(문자열 **전체** 유사도)를 써서 짧은쿼리 vs 긴 500토큰 청크에 구조적 0 → pg_bigm 켜면 OR이 tsquery보다 **퇴행**. Growth-99의 "한계효용 낮음" 경고가 실측으로 확인.
- **즉시 롤백**: founder `DROP EXTENSION pg_bigm CASCADE` + Redeploy → probe=False → tsquery 복귀(손해배상 22건·뱃지 회복). 볼륨 보존이라 extension 재생성 쉬움.
- **꼼꼼한 수정(engineer)**: OR/AND bigm 분기를 단일 `if use_bigm`으로 병합, 둘 다 `_build_bigm_like(query, op)`의 **LIKE 부분문자열 + bigm_similarity 랭킹** 사용(AND 분기가 이미 정답 템플릿이었음). LIKE는 한국어 토큰내부 부분문자열(손해배상금→손해배상)까지 잡아 tsquery보다 우위. 죽은 `_FTS_BIGM_SQL`·`_BIGM_SIMILARITY_LIMIT`·`SET LOCAL` 제거. 3커밋 df8862e/48ba7a2/32e446f 푸시.
- **★ 테스트 사각 폐쇄(핵심 교훈)**: `test_case_scoped_search`가 pg_bigm=False 강제라 **hybrid_search의 bigm 경로가 단위에서 한 번도 안 돌아** `=%%` 이스케이프(1차)·`=%` 의미론 퇴행(2차)을 둘 다 놓쳤다. ① `test_bigm_search_path.py`(신규) — `_BIGM_AVAILABLE=True` 패치+conn mock으로 OR/AND FTS SQL에 LIKE 포함·`=%` 부재 assert(8케이스, 회귀가드) ② `test_postgres_integration.py` — DSN 게이트 실 bigm LIKE OR ≥1행 검증. **mock-only 테스트는 라이브 경로를 못 잡는다 → 통합테스트로 실경로 게이트 필수**.
- **CTO 게이트(envelope 불신, 직접 재실행)**: retrieve.py 정독(병합분기 LIKE 정확·`=%` 실행코드 0=주석만), Pyright `_FTS_BIGM_SQL undefined` 진단은 stale(병합 중간상태) 확인, 단위 **321 passed/0 failed**, postgres 20 skip 클린(psycopg false-positive). `_build_or_tsquery` 잔존은 test_fts_or_tsquery가 import(죽은코드 아님).
- **인프라 함정**: 서브에이전트 pytest가 cwd≠repo root라 Bash 훅(상대경로 scripts/hooks) 데드락 → PowerShell 툴로 우회([[subagent-cwd-hook-fragility]]).
- **정직 한계**: "계약해지"↔"계약 해지"(띄어쓰기 복합어)는 LIKE로도 안 풀림(literal 부재) — 정규화 또는 ANN 영역. pg_bigm은 substring-in-token만 개선. 활성화 ROI는 Growth-99 판단대로 제한적.
- **잔여(founder 배포)**: extension 재생성(`CREATE EXTENSION pg_bigm`+인덱스) → legal-rag app Redeploy(코드변경=재빌드 필요) → OR "손해배상" 뱃지 회복+substring 우위 확인.
- §6 rollup: [Growth-119] legal-rag pg_bigm OR `=%` 퇴행(라이브 0 vs tsquery 22) 적발·DROP 롤백·OR→LIKE 재배선 수정 + mock 사각 폐쇄(bigm-path 단위+postgres 통합테스트). 321 passed. founder 재배포 대기. Growth-99 한계효용 경고 실증.

### Growth-120 — 큐드 태스크 관리 프리셋 3-Phase (협업 코어 + 칸반 + Lite-AI), 14커밋

- **발단**: 패션 인바운드發 큐드 결정([[queued-task-mgmt-preset]]) 착수. gate(deep-research salvage) clear. CTO 발견 — **greenfield 아님**: catalog `project` 도메인(task 상태머신·assignee·subtask 이미 존재) **확장**. founder 가 차별화 3레이어(칸반+활동로그+Lite-AI) 전부 선택.
- **P1 복리 코어**: catalog 협업 5엔티티(task-comment/attachment/label/label-link/activity)+task.priority(DBA, 타입드 FK·polymorphic 회피) → seed v1.1 환류(칸반 상태머신 선환류) → `taskflow-demo.yaml` 프로파일. scaffold rc=0 10테이블. **교훈: render는 profile entities만 emit → M:N 조인은 화면 없어도 profile에 명시해야 DDL 완결(FK-closure로 안 잡힘, link→label 방향).**
- **P2 칸반 보드(차별화)**: `board_descriptor`(status enum 자동 board-enabled, per-entity 하드코딩 0=open-closed) + `/board` 라우트 + `_TASK_STATUS_MACHINE`(seed 1:1) + board.html(HTML5 DnD+htmx, var(--*)만) + 보드토글. 26테스트(무효전이 422). 기존 화면 무회귀.
- **P3 Lite-AI(스코프 레퍼런스, founder 택)**: `search-similar` 서비스 — EmbeddingProvider Protocol + LocalEmbeddingProvider(TASKFLOW_EMBED_URL env·stdlib urllib·**클라우드 URL 하드코딩/폴백 0**) + trigram Jaccard 렉시컬 폴백(순수 python) + 순수 python 코사인. 응답 `mode` 명시=정직 라벨링. 30테스트. **전역룰(api 미사용·$0) 준수**, [[product-two-tier-selfhost-ai]] Lite 티어 정렬.
- **CTO 게이트(envelope 불신, 매 Phase 직접 재실행)**: catalog FK 9건 실존, board 상태머신 seed 대조, P3 클라우드 호출 0 grep + board 26/search 30 테스트 독립 재실행. Pyright 신규진단 전건 기존 false-positive(@app.context_processor 등) 판별.
- **인프라 함정 재발·해법**: `cd vanilla-htmx` 가 Bash·PowerShell **공유 cwd** 둘 다 오염 → 훅 deadlock. PowerShell `Set-Location` 절대경로 복구, 이후 pytest는 `(cd … && pytest)` 서브셸 또는 Push/Pop-Location 격리. [[subagent-cwd-hook-fragility]] 강화.
- **잔여(비차단)**: 프론트 search-similar mode 뱃지 surface(CDO) · `project.search-similar` middle contract 와이어키 등록 · 보드 컬럼색상 토큰(CDO)·모바일 터치 DnD·fragment 부분재렌더 · taskflow SEED_FILE 데모데이터 · TEI 라이브 검증(founder DSN 게이트, legal-rag TEI 재사용).
- §6 rollup: [Growth-120] 큐드 태스크 관리 프리셋 3-Phase — P1 협업 코어(catalog 5엔티티+seed+프로파일, render=profile-scope 교훈), P2 칸반 보드(open-closed board view-kind+상태머신, 26테스트), P3 Lite-AI search-similar(로컬임베딩+렉시컬폴백, 클라우드0·$0, 30테스트). 14커밋 푸시. CTO 매-Phase 독립검증. 기존 project 도메인 확장(복리), 신규 도메인 날조 0.

### Growth-121 — taskflow-demo 데모 라이브化: 선언적 시드(51레코드) + 프론트 search-similar surface, 6커밋

**맥락**: Growth-120 에서 taskflow-demo 3-Phase(협업+칸반+Lite-AI) 코드 완성. founder "데모데이터+프론트 surface 로 라이브 시연 가능하게". 백엔드 search 라우터는 `entity_store.find_all("task")` 에서 라이브 후보를 읽음 → seed_loader 로 들어간 태스크가 그대로 검색대상. 프론트는 `/api/*` 패스스루 프록시 보유(단 JSON → htmx 스왑용 서버렌더 fragment 필요).

- **시드**(`profiles/seed/taskflow-demo.seed.yaml`, 51레코드): smallmfg-demo 스키마 준용 선언적 fixture. 의존순서(dept→emp→project→milestone→label→task→link→comment→activity), FK `{$ref}`, id/타임스탬프 server-set. 칸반 데모용 5상태 전부 분산(todo4·in-progress4·blocked3·done5·cancelled1, progress_pct 상태정합), Lite-AI 데모용 태스크명 4테마(인증/결제/UI/인프라) 클러스터링. dry-run OK 51 refs resolvable.
- **프론트 surface**(server.py `/tasks/similar` 라우트 + similar_results.html fragment + board.html 검색박스 + app.css `.similar-*` + test_similar.py 11테스트): 백엔드 search-similar 프록시 후 서버렌더. **mode 배지 honesty** — semantic→"AI 의미검색"(accent), lexical→"키워드 검색"(muted) 배타적 분기, lexical 절대 AI 라벨링 안 함. 검색박스 entity_type=='task' 게이팅(보드 제너릭). 빈쿼리 무프록시, non-200 graceful.
- **CTO 독립검증**: dry-run 51 refs(utf-8 재실행, 내 콘솔 cp949 함정 회피) + 배지 honesty grep + 37테스트(11 similar+26 board 무회귀) + git status 스코프(backend/ 무수정 확인). 6커밋 파일별 푸시.
- **교훈**: ①프론트 htmx 는 JSON 아닌 HTML 스왑 → 패스스루 프록시 있어도 서버렌더 fragment 라우트 별도 필요(board 패턴 재사용). ②Windows 콘솔 cp949 → seed_loader dry-run 은 `PYTHONIOENCODING=utf-8` 필수(— em-dash 인코딩 실패). ③배지 honesty 는 코드 주석+배타적 Jinja 분기+테스트(lexical 결과에 "AI 의미검색" 부재 단언) 3중으로 박음.
- **잔여(비차단·founder 런타임 게이트)**: ①라이브 seed_loader 실행(백엔드 :8080 기동 후 POST, founder DSN/런타임) ②TEI 연결시 mode=semantic 실증(현재 env 미설정→lexical) ③search box list 뷰에도 노출 검토 ④`project.search-similar` middle contract 와이어키 등록.
- §6 rollup: [Growth-121] taskflow-demo 라이브化 — 선언적 시드 51레코드(5상태 분산+4테마 클러스터, dry-run OK) + 프론트 search-similar surface(서버렌더 fragment, mode 배지 honesty 3중 방어, task 게이팅). 6커밋. CTO 독립검증(스코프 backend 무수정+37테스트+배지 grep). 라이브 실행만 founder 런타임 게이트 잔여.

### Growth-122 — taskflow-demo Coolify 라이브 배포 + F-5 폼 타입 coercion 결함 수정, 3커밋

**맥락**: Growth-121 에서 taskflow-demo 라이브化(시드+surface) 코드 완성. founder "데모를 서버에서 고객에게 시연하고 싶다" → Coolify 배포 산출물 생산 + 라이브 배포(founder 실행) + 첫 폼 편집에서 드러난 일반 결함 수정.

- **배포 산출물**(devops, 5파일): `deploy/preview/taskflow-demo.compose.yml`(3서비스 — backend:8081 + **seeder 1회성** + frontend:5000, 헬스게이트 체인) + `scripts/taskflow-seeder/{Dockerfile,entrypoint.sh}`(backend healthy 대기→scaffold.py manifest 생성→공유볼륨→seed_loader 51건) + `infra/registry/taskflow-demo.yaml` + `docs/runbooks/taskflow-demo-deploy.md`. **인메모리 store 매 redeploy 재시드 = 시연마다 깨끗한 데이터**(의도). **gitignored manifest → seeder 가 빌드시 생성해 named volume 으로 frontend 전달**(lawfirm host bind-mount 디렉터리화 함정 회피).
- **CTO 독립검증으로 critical 결함 적발**(devops envelope 는 success 보고): compose healthcheck 가 `/health` 를 쳤으나 실제 라우트는 `/api/status/health`(status 라우터 prefix). 그대로면 **backend 영원히 unhealthy→seeder 미실행→frontend 미기동 데드락**. → Edit 수정 + 런북 smoke 예시 2건(`/health`, `entities/board_task`) 동반 수정. [[subagent-cross-service-verify]] 재확인 — thin wrapper 만 보고 success 단정 금지, cross-service 경계는 CTO 가 독립 소스검증.
- **라이브 배포(founder 실행, deploy_to_coolify.py)**: project `tmxqpuzxk4uywv67bhywnnty`/app `q1378vp78qvwfv5hh5hzv80o`, https://taskflow-demo.n9n.co.kr. registry manifest_server_path=null → SCP 자동 skip(seeder 설계 정합). TLS 첫 배포시 Traefik DEFAULT CERT(자가서명)→2분 후 LE 발급 정상(타이밍, lawfirm/shop 동일). DNS 는 `*.n9n.co.kr` 와일드카드 상설로 무선결([[infra-stack]] 갱신, 재질문 금지).
- **F-5 결함 — 폼→contract 타입 coercion**(라이브 첫 편집서 발현): project 편집 저장 → `422 budget: must be a number (decimal)`. **근본원인**: vanilla-htmx `entity_update`/`entity_create_post` 가 `request.form.items()` 를 **문자열 그대로** 백엔드 전송. 백엔드 `catalog_validator.py:247` decimal 검증은 int/float 만 허용·문자열 거부. seed_loader 경로(YAML 숫자)는 통과했으나 브라우저 폼 경로에서 드러남 = **taskflow 한정 아닌 어댑터 일반 결함**(decimal/integer/boolean 모두). **수정**: manifest 필드타입 구동 `_coerce_form_value`/`_coerce_form_data` 헬퍼(server.py) — integer→int, decimal→정수면 int 아니면 float(금액 float 정밀도 회피), boolean→truthy, 그 외 문자열, ValueError→원본유지(백엔드 명확 422 위임). **budget 하드코딩 아닌 타입 구동=복리**(모든 프로필 숫자/불린 필드 자동 적용). **백엔드 strict 는 설계의도이므로 무수정** — 어댑터가 contract 에 맞춰 보내는 게 원칙.
- **CTO 독립검증(founder payload 활용)**: founder 가 실제 /edit payload 제공(`created_at=1782271380918&...&budget=44999999`). ①Pyright "_coerce_form_data not accessed" 오탐 의심 → 두 핸들러(line 618/678) 호출 직접 확인 ②payload 의 id/created_at/updated_at 가 2차 timestamp 422 일으킬 리스크 → manifest `hidden_fields:['id','created_at','updated_at']` 실측으로 핸들러 `k not in hidden` 필터링 확증 ③field types 로 budget→int 44999999 변환·나머지 문자열 정합 추적. 116 passed(1 pre-existing hex FAIL 무관). **재배포 후 라이브 정상 동작 확인(founder)**.
- **교훈**: ①폼 어댑터는 HTTP 폼=전부 문자열 → strict wire contract 앞단에서 **manifest 타입 구동 coercion 필수**(특정 필드 하드코딩 금지). ②founder 가 준 실제 payload 는 cross-field 리스크(hidden 필터·2차 검증) 추적의 1급 단서 — 단일 에러 메시지만 보지 말고 payload 전체로 후속 결함 예측. ③Pyright "not accessed" 는 Flask 데코레이터·stale 분석서 오탐 빈발 → 실제 호출부 grep 으로 반증.
- §6 rollup: [Growth-122] taskflow-demo Coolify 라이브 배포(taskflow-demo.n9n.co.kr, seeder 재시드 패턴, manifest named-volume) + CTO 가 compose healthcheck 데드락 결함 적발·수정 + F-5 폼 타입 coercion 일반결함 수정(manifest 구동, 어댑터가 strict contract 에 맞춤). founder payload 로 hidden 필터 2차검증. 재배포 후 라이브 정상. 3커밋.

### Growth-123 — taskflow project.search-similar 와이어키 contract 등록 (Growth-121 잔여 ④), 3커밋

**맥락**: Growth-121 에서 taskflow-demo Lite-AI 유사검색 프론트 surface 완성. 백엔드 라우터(`routers/task_search.py`)는 동작했으나 와이어 키 `project.search-similar` 가 **어댑터-로컬**(docstring 에 "pending contract registration" TODO)이라 middle single-source 미등록 = 복리 축적 누락. founder "와이어키 등록부터 하자(가장 짧음)".

- **contract 등록**(`middle/contract/wire-v1.yaml`, +58줄): `project` 도메인 신설(auth/entity 비즈니스 그룹과 status 인프라 사이). `project.search-similar` 키 — request `query_text`(req)/`exclude_id`/`top_n`(default 5, adapter clamp 1~50), response `mode`(semantic|lexical, ALWAYS present)/`items`(score+full entity)/`total`/`error`. `idempotent: true`(read-only). **honesty contract 명문화** — lexical 결과를 AI/semantic 으로 라벨링 금지, mode 배지 표시 의무, cloud API cost zero(self-host embed/local fallback). 헤더 namespace 주석에 hyphenated multi-word verb(search-similar) 허용 명시.
- **라우터 docstring 갱신**(`task_search.py`): "pending registration" TODO 제거 → "registered in wire-v1.yaml, Growth-123" 참조로. README(`middle/contract/README.md`) 키 카운트 8→9, 도메인 목록에 project 추가.
- **CTO 검증**: 라우터 실제 모양과 contract 1:1 대조(GET/POST 양쪽 query_text/exclude_id/top_n, _run_search 빈쿼리 lexical no-op, 500 error envelope). YAML 파싱 OK(9키). **G-1 wire-protocol single-source 가드 PASS**. task_search 테스트 30 passed 무회귀.
- **교훈**: ①어댑터가 먼저 동작하고 contract 가 뒤따르는 패턴은 정상이나, "pending registration" docstring TODO 는 복리 누락 신호 — 동작 확인 즉시 single-source 승격. ②contract 는 코드 모양을 그대로 박는 게 아니라 honesty/idempotent/clamp 같은 **불변 계약**을 명문화하는 자리(특히 mode 배지 의무는 코드 주석만으론 약함 → contract 박제).
- **잔여(taskflow Growth-121)**: ③ search box list 뷰 노출 검토(CTO), ② TEI 연결 시 mode=semantic 실증(founder env 게이트).
- §6 rollup: [Growth-123] taskflow `project.search-similar` 와이어키 등록 — 어댑터-로컬→middle wire-v1 single-source 승격(project 도메인 신설, mode honesty/idempotent/clamp 계약 박제). 라우터 TODO 제거·README 8→9. G-1 PASS, 30테스트 무회귀. 3커밋 푸시.

### Growth-124 — taskflow 유사검색 바 list-뷰 노출 + 공유 partial 추출 (Growth-121 잔여 ③), 7커밋

**맥락**: Growth-121 에서 taskflow Lite-AI 유사검색을 **board.html 에만** 인라인으로 surface. founder "이어서 마무리" → 잔여 ③ list 뷰 노출. board 인라인 블록을 그대로 복붙하면 중복 누적 = 복리 위반 → **공유 partial 추출 후 board+list 양쪽 include** 방식 채택.

- **공유 partial**(`templates/_similar_search.html`, 신규): board 인라인 블록(15줄)을 self-gated partial 로 추출. `{% if entity_type == 'task' %}` 게이트를 partial **내부**에 두어 include 를 무조건화(비-task 는 무출력) — 호출부가 게이트 중복 안 함. honesty: mode 배지는 fragment(similar_results.html)가 유지하므로 partial 은 입력바만.
- **배선**: board.html 인라인 → include 리팩터(기능 동일). list.html + list-master-detail + list-modal + list-top-bottom **4개 list 레이아웃 전부**에 include 추가(task 가 env 로 어느 레이아웃에 배정돼도 동일 기대 충족). list 의 기존 substring 툴바와는 **별개** — 그건 entity.list filter(부분일치), 이건 Lite-AI 의미/키워드 유사도(wire `project.search-similar`, mode 배지).
- **테스트**(test_similar.py +3): `/entities/task` 바 노출 / `/board/task` 무회귀 / `/entities/department` 미노출(self-gate 검증). Flask 테스트 클라이언트(mock _proxy_request).
- **CTO 검증 함정 회피**: standalone Jinja 렌더 스모크가 base.html 미충족 컨텍스트(Flask context_processor 의 manifest 전역 부재)로 content 블록 비어 **False 오판** → Flask 테스트 클라이언트로 전환해 실재 검증. **템플릿 검증은 standalone Jinja 아닌 app test_client 가 정답**(context_processor 의존). 119 passed(1 pre-existing hex FAIL 무관, app.css 무수정).
- **교훈**: ①두 번째 surface 추가 = 복붙 신호 → 즉시 partial 추출(게이트는 partial 내부로 끌어와 호출부 무조건화). ②Jinja 템플릿 검증을 standalone Environment 로 하면 base.html 의 context_processor 전역이 비어 블록이 통째로 누락돼 false negative — Flask `app.test_client()` 사용. ③`git -C <repo>` 는 Bash persisted-cwd 훅 깨짐([[subagent-cwd-hook-fragility]])을 우회하는 안정 패턴.
- **잔여(taskflow Growth-121)**: ② TEI 연결 시 mode=semantic 실증(founder env 게이트)만 남음.
- §6 rollup: [Growth-124] taskflow 유사검색 바 list-뷰 노출(4 레이아웃 전부) — board 인라인 블록을 self-gated 공유 partial(_similar_search.html)로 추출해 board+list include. substring 툴바와 별개 Lite-AI 유사도. +3 테스트(노출/무회귀/미노출). standalone Jinja false negative 함정 → Flask test_client 전환. 7커밋.

### Growth-125 — taskflow mode=semantic 실현: embed-adapter 재사용 + provider 비대칭 재배선 (Growth-121 잔여 ②), 5커밋

**맥락**: Growth-121~124 로 Lite-AI 유사검색 contract·프론트·테스트 완성. 잔여 ② "TEI 연결 시 mode=semantic 실증"만 남음 — 백엔드는 `TASKFLOW_EMBED_URL` 미설정 시 lexical 폴백이라 라이브가 "키워드 검색" 배지뿐. founder "mode=semantic 으로 해보자". CTO 분석: 백엔드 provider 는 **native TEI 형식**(`{"inputs"}`→`[[...]]`)인데, 우리 8축 자산 legal-rag embed-adapter 는 다른 규약(`{"text"}`/`{"embedding"}`, `/embed/batch`). founder 결정 A= **embed-adapter 재사용**(한국어 e5·오프라인·복리 우선, provider 수정 감수).
- **provider 재배선**(`services/task_search.py`): `EmbeddingProvider` 프로토콜 `embed(texts)` → **`embed_query(text)`+`embed_passages(texts)` 비대칭 2-메서드**(G-87 e5 query/passage head). `LocalEmbeddingProvider` 가 `TASKFLOW_EMBED_URL` **베이스 URL** 에 `/embed`(query head)·`/embed/batch`(passage head) 부착, stdlib urllib 만. `search_similar` 의미경로: 검색어→embed_query, 후보 task→embed_passages(빈 텍스트는 `(제목 없음)` 치환해 adapter 422 회피). taskflow 가 G-87 비대칭 분리의 **새 one-directional caller**(검색어=query·task=passage 의미적으로 정확히 부합).
- **인프라**(`taskflow-demo.compose.yml`): `embed` 서비스 추가(legal-rag embed-adapter 빌드 재사용, multilingual-e5-base baked·오프라인·internal-only). backend env `TASKFLOW_EMBED_URL=http://embed:8080`. **backend depends_on embed 일부러 생략** — embed 미가동/워밍업(~60s) 중에도 backend 는 lexical 로 즉시 서빙, healthy 되면 semantic 으로 전환(honesty-fallback resilience 보존). Coolify net 격리로 legal-rag embed 공유 불가 → 본 스택 자체 인스턴스(RAM +~500MB, registry cost_note 환류).
- **검증**: task_search L1 30 passed(fake provider 도 2-메서드로 갱신, query/passage 분리). G-1 wire PASS. compose YAML 유효(4서비스). 잔존 3 FAIL(G-8 out/·G-9 §6누적·G-12 legal FK)은 전부 기존·무관.
- **교훈**: ①provider 규약을 맞출 때 "단일 embed 로 query+passage 한방"은 G-87 비대칭 head 를 silently 깨뜨림 → 프로토콜 자체를 query/passage 2-메서드로 분리해 caller 가 교차 못 하게 강제. ②사이드카는 backend 와 hard depends_on 결합하지 말 것 — graceful-fallback 설계의 resilience(미가동 시 lexical)가 오케스트레이션 레벨에서 사라짐.
- **잔여**: L4 live `mode=semantic` 실증 — Coolify 재배포(embed 이미지 빌드 ~수분) 후 `taskflow-demo.n9n.co.kr` 검색에서 "AI 의미검색" 배지 확인(push 자동배포 또는 founder redeploy). taskflow Growth-121 잔여 전부 종결.
- §6 rollup: [Growth-125] taskflow mode=semantic 실현 — legal-rag embed-adapter(한국어 e5) 재사용, provider 를 비대칭 embed_query/embed_passages(G-87 query/passage head) 로 재배선. compose embed 사이드카+TASKFLOW_EMBED_URL=http://embed:8080(depends_on 생략=lexical resilience 보존). L1 30 PASS·G-1 PASS. **L4 live PASS** — 재배포 후 	askflow-demo.n9n.co.kr 검색이 'AI 의미검색'(semantic, cosine top 86%) 확증, lexical-distinct 쿼리 3종 전부 semantic. taskflow Growth-121 잔여 전부 종결. 5커밋.

### Growth-126 — entity.list 자유텍스트 `search` 결함 수정: 전 데모 검색 0건 → 부분일치 (G-126), 5커밋

**맥락**: founder "데모 포털 카드의 데모들 전부 검색이 안 된다". CTO 진단 — vanilla-htmx 공유 리스트 툴바의 자유텍스트 "검색…" 박스가 `?search=<term>` 전송하나, 백엔드 entity.list 가 비예약키를 **exact field=value 필터**로 처리 → 레코드에 없는 `search` 필드에 매칭 → **모든 업종 데모에서 검색 시 0건**(공유 어댑터 결함, taskflow 한정 아님).
- **수정**: `search` 를 예약키로 승격, 전 필드값 대소문자무시 substring(OR) 매치를 `filter` 이후 적용. fastapi(`routers/entity.py` _matches_search)+springboot(`EntityController.java` matchesSearch) 양 어댑터 파리티. contract(`wire-v1.yaml`)에 `search` 필드 명문화(어댑터는 exact 필터 금지 — 없는 필드라 0건).
- **테스트**: fastapi L1 7케이스(부분일치/대소문자/비-name OR/무매치0/공백·미지정 전체반환 회귀가드/filter결합) + `_shared` 컴플라이언스 1케이스(양 어댑터 라이브). fastapi 전체 86 passed. G-1 PASS.
- **검증 한계**: springboot 미배포(전 데모 fastapi) → L3 gradle 은 오프라인 플러그인 미캐시·무네트워크 룰로 본 환경 미검증, 변경은 matchesFilter 패턴 1:1 미러+컴플라이언스 라이브 가드로 보증.
- **교훈**: UI 가 노출한 기능(자유텍스트 검색)이 백엔드 계약에 없으면 "조용히 0건"으로 죽는다 — 비예약키=exact-filter 라는 어댑터 디폴트가 자유텍스트 박스와 충돌. 새 입력 표면은 contract 예약키+의미 정의가 선행돼야.
- **잔여(founder)**: 9개 데모 Coolify 재배포(공유 fastapi 백엔드 재빌드로 픽업).
- §6 rollup: [Growth-126] entity.list 자유텍스트 `search` 결함 — 비예약키 exact-filter 오용으로 전 업종 데모 검색 0건. `search` 예약키 승격+전필드 substring(OR, filter 이후) fastapi+springboot 파리티, contract 명문화. fastapi 86 passed+컴플라이언스 가드. 교훈: UI 노출 기능이 계약에 없으면 조용히 0건. founder 9데모 재배포 잔여. 5커밋.
### Growth-127 — 소형 로펌 killer-app 2종(K1 기일 가디언·K2 이해충돌 검사) + 로폼 경쟁분석, 15커밋

**맥락**: founder "소형 법무법인 타겟 killer app 추가 — 로폼(business.lawform.io) 분석해 needs 도출, 로폼 구독 SaaS 와 경쟁 회피·in-house 완성형으로". CTO 분석(wiki synthesis 환류 [[lawform-competitive-analysis]]): 로폼=계약(contract)축·생성형·클라우드구독·대기업법무팀/개인 → **소형 로펌의 사건(case)축은 사각지대**. 정면충돌(CLM·계약생성) 회피, 사건축·검색형·self-host 로 우회. founder 선택 K1+K2 둘 다.
- **K1 기일·기한 가디언**: catalog `case-deadline`(legal, FK case_id→legal-case)+DDL augment `11_legal_case_deadline.sql`(신규테이블·case-scoped RLS)+profile/seed 12건(임박4·미래5·지남1·완료2). vanilla-htmx 리스트 임박(D-7·pending) 하이라이트(server.py imminent_ids + list.html tr--imminent + app.css warning 토큰), 종료상태 제외. honest: "누락 방지" 아님 "임박 표시".
- **K2 이해충돌 검사**: `project.search-similar` 를 `entity_type` 파라미터(기본 task, open-closed)로 일반화 → `case-party` 이름 유사검색 재사용. wire contract 명문화. case-party 리스트에 conflict 위젯(_similar_search.html 분기)+conflict_results.html(mode 배지·"후보일 뿐 최종판단 변호사" 면책). embed 사이드카 재사용(미설정 시 lexical 폴백).
- **검증**: fastapi 90 passed(K2 4 신규). 라이브 로컬: case-deadline 12건 서빙·conflict "박서연" 5건. scaffold lawfirm-demo 15엔티티 정상. py_compile OK. app.css 기존 raw-hex 3줄(834-836) 토큰 교정(가드 부분개선). G-1 PASS, 신규 G-12 위반 0.
- **잔여(founder)**: ①lawfirm-demo Coolify 재배포(공유 fastapi+프론트 재빌드) ②**manifest scp**(out/lawfirm-demo/screen-manifest.json → /data/coolify/manifests/lawfirm-demo/, case-deadline nav 노출 필수) ③seed 기일 날짜 2026-06 앵커(시간경과 시 임박 퇴색 — 주기 갱신).
- **교훈**: 경쟁 SaaS 와 같은 축에서 싸우지 말고 사각지대(사건축)를 self-host 완성형으로 — 차별화=기능 더하기 아니라 축 바꾸기. 기존 검색엔진을 entity_type 파라미터 하나로 새 killer-app(이해충돌)으로 재사용=복리.
- §6 rollup: [Growth-127] 소형로펌 killer-app K1 기일가디언(case-deadline entity+DDL+임박 하이라이트)·K2 이해충돌검사(search-similar→entity_type 일반화로 case-party 재사용). 로폼=계약/구독/생성형, 사각지대=사건축 → self-host 검색형 우회([[lawform-competitive-analysis]]). fastapi 90 passed·라이브로컬 PASS. 잔여 founder: 재배포+manifest scp. 15커밋.

### Growth-127 후속 — manifest scp→seeder 전환 + 칸반 카드 셀렉트 full-width 결함 수정

- **manifest 공급 scp→seeder 전환** (푸시 b79f1ec): scp publickey denied(no-SSH 경계) → 제너릭 `scripts/manifest-generator/`(Dockerfile+entrypoint, scaffold→공유볼륨, manifest-only ∵ SEED_FILE) + lawfirm compose 를 host bind-mount→공유볼륨 seeder 패턴 전환. scp 영구 제거, 나머지 8 scp-데모 재사용 자산.
- **칸반 카드 상태 셀렉트 full-width 결함** (푸시 ed726d0): founder "칸반 카드 width 100%". CTO 라이브 probe — 카드/컬럼 정상(컨테이너 flex, 컬럼 240px, 3컬럼12카드). 진짜 원인=제너릭 엔티티 카드 상태변경 `<select class="form-input board-card__move-select">`가 `.form-input{width:100%}`(app.css:683) 상속, `.board-card__move-select` width 미정의 → 셀렉트가 카드 폭 전체로. task 엔티티=버튼이라 무관, lawfirm 6 board 엔티티 전부 제너릭→전 카드 증상. 수정: `display:inline-block;width:auto;max-width:100%`(정의순서상 .form-input 뒤→승리). board L1 26 passed. 교훈: 공유 폼 유틸클래스(.form-input)를 컴팩트 컨텍스트(카드/툴바)에 재사용 시 width override 누락이 조용한 레이아웃 결함.
- §6 rollup: [Growth-127 후속] manifest scp→in-cluster seeder 영구전환(b79f1ec, 8데모 재사용) + 칸반 카드 상태셀렉트 full-width 결함 수정(ed726d0, .form-input width:100% 상속 차단). board L1 26 PASS. founder 잔여: lawfirm-demo Redeploy.


### Growth-128 — 소형 로펌 killer-app K3 타임시트·빌링 (time-entry·case-invoice 엔티티 + 청구 롤업), 11커밋

**맥락**: K1(기일 가디언)·K2(이해충돌) 종결 후 founder가 K3 타임시트·빌링 선택 — 시간당 청구는 소형 로펌 수익 핵심, 사건축 자연 동반. CTO 설계 → engineer-agent(sonnet) 위임, K1(case-deadline) 누적 패턴 1:1 미러.

- **신규 엔티티 2**: `time-entry`(table legal_time_entry — case_id FK cascade·employee_id cross-domain fk-exempt[K1 assigned_attorney 관습]·minutes/hourly_rate/amount integer·billable·status[draft/submitted/billed]) + `case-invoice`(table legal_invoice — client_name·subtotal/tax/total·status[draft/issued/paid]). DDL 12/13 = K1 case-scoped RLS(ENABLE+FORCE, attorney/partner)·set_updated_at 트리거·인덱스·idempotent ADD-ONLY 미러.
- **Killer 기능(K1 imminent_ids 미러)**: server.py entity_list가 entity_type=="time-entry"일 때 billable_total/unbilled_total(status!=billed)/total_minutes 롤업 계산(billable 타입 강제변환) → list.html 청구 요약 배너 + tr--unbilled 미청구 하이라이트. 개방-폐쇄(time-entry 가드). honest: "기록 기반 청구 합계 집계"만, 자동 청구서 생성·법적 효력 주장 금지.
- **시드**: time-entry 25(billable 23·status 혼합)·case-invoice 6(부가세 10% 정합). amount=round(분/60×시급) 0오류, FK dangling 0.
- **CTO 게이트 — CRITICAL 적발/수정**: engineer가 신규 엔티티를 `invoice` 키로 명명 → **기존 finance 도메인 `invoice`(finance_invoice)와 같은 /entities 매핑에서 YAML 키 충돌**. PyYAML이 로드 전 중복키 dedupe → finance_invoice 소실·payment.invoice_id FK 오염되나 **G-10이 dedupe된 결과만 봐서 PASS(silent 결함)**. CTO 독립 yaml.safe_load 검증으로 적발([[subagent-cross-service-verify]] 재확인). 신규 엔티티 `invoice`→`case-invoice` 리네임(finance 불가침, 5파일 일관: catalog·profile·seed gen·seed json·DDL 주석)으로 복구. 재검증: invoice→finance_invoice·case-invoice→legal_invoice 공존 확정.
- **검증**: fastapi 90·billing L1 13·board L1 26 green, scaffold rc=0(17엔티티 manifest), diagnose 신규 FAIL 0. 11커밋(2c3f062).
- **교훈**: 멀티도메인 catalog에 엔티티 추가 시 **전역 키 유일성**을 먼저 확인(도메인 prefix 관습 case-/legal- 활용). YAML 중복키는 파서가 조용히 삼켜 가드를 우회 — CTO는 safe_load 후 키 존재를 직접 단언해야 한다.
- **잔여 founder**: lawfirm-demo Coolify Redeploy(frontend+backend 재빌드, seeder가 manifest 재생성) → time-entry·case-invoice nav 등장 + 청구 롤업 배너 라이브.
- §6 rollup: [Growth-128] K3 타임시트·빌링 — time-entry·case-invoice 엔티티+DDL(K1 RLS 미러)+청구 롤업 배너(billable/unbilled/총시간, imminent_ids 패턴). CTO 게이트가 invoice↔finance_invoice YAML 키 충돌(G-10 우회 silent 결함) 적발→case-invoice 리네임 복구. fastapi 90·billing 13·board 26 green. 11커밋.

### Growth-129 — lawfirm-demo 헤더 좌우 여백 "반영 안 됨"의 2중 결함 규명 + headless 검증 하니스 skill화

**맥락**: founder가 lawfirm-demo `/board/case-deadline` 글로벌 헤더의 좌우 여백이 Redeploy+캐시삭제 후에도 그대로고 "browser 사이즈에 비례해 여백이 늘고 준다 / 반영이 안됐어, 남의 다리 긁는 기분"이라 재점검 요청. 처음 padding(48→24px) 가설은 틀렸다 — 고정 px는 뷰포트-비례 여백을 못 만든다. 추측 중단, 라이브 DOM 측정으로 전환.

- **결함 ①(반영을 가로막던 enabler)**: vanilla-htmx PWA 서비스워커 `/static/sw.js`(전 데모 공통)가 `/static/css|js`를 **cache-first + 고정 캐시명 `csh-v1`**로 서빙 → sw.js 무변경+캐시명 고정이라 브라우저가 SW 재설치 안 함 → 옛 app.css 영구 서빙. HTML(network-first)은 신선, CSS(cache-first)만 stale인 **비대칭**이 결정적 단서. 수정: 전부 **network-first(+오프라인 폴백)**, `csh-v1→csh-v2` bump로 activate가 독성 캐시 일괄 삭제 (commit 87091ac). 이후 Redeploy는 새로고침 1회로 항상 반영.
- **결함 ②(진짜 시각 원인)**: Pico CSS v2 classless가 **body 직계 `<header>`/`<footer>`에 reading-container max-width**(xxl 1450px) + 가운데정렬을 자동 적용 → 뷰포트 1822px에서 헤더가 1450px로 좁아지고 좌측 186px 여백(비례)이 생김. app-layout grid를 `minmax(0,1fr)`로 풀폭 만든 이전 수정(디자인 수정-4)은 무효 — grid **컬럼**만 풀폭, 헤더 **아이템**의 Pico max-width는 별개. 직계 아닌 `<main class=app-main>`(app-body div 안)은 Pico `body>main` 미적용 → 본문은 멀쩡, 헤더만 좁은 이유. 수정: `.app-header,.app-footer,.app-header-minimal { max-width:none; width:100%; margin-inline:0 }`. class 셀렉터(0,1,0) > Pico `:where()`(0,0,0)라 `!important` 불필요 (commit f252336, 디자인 수정-6).
- **왜 SW만 고치고 reload해도 안 변했나**: 새 CSS가 닿아도 그 CSS 자체에 헤더 수정이 없었음(②가 아직 미커밋). 두 결함은 founder 체감상 상호의존 — ①이 새 CSS를 브라우저까지 보내고, ②가 실제 여백을 제거.
- **측정 증거**(라이브 로그인 demo/demo, vw=1822): BEFORE 헤더 `{x:186, w:1450}` → 후보 CSS 주입 AFTER `{x:0, w:1822, 로고 x:61}` = 풀폭, 좌측 여백 0. **배포 0회로 수정을 증명.**
- **반복 작업 skill화**: 이 측정-주입 워크플로(puppeteer-core@23 `$TEMP/node_modules` + 로컬 Chrome, 라이브 로그인, getBoundingClientRect/getComputedStyle 측정, 후보 CSS `addStyleTag` 주입으로 redeploy 전 증명)를 `.claude/skills/htmx-demo-verify/`(SKILL.md + scripts/verify_live_css.mjs)로 추출. 기존 webapp-testing(로컬 Playwright)과 구분 — 이건 **이미 배포된 라이브** 데모 검증 + 배포 전 CSS 주입 증명. "디자인 수정 반영 안 됨" 3대 원인(SW stale / Pico max-width / push 누락) 변별표 동봉.
- **전파**: 두 수정 모두 공통 vanilla-htmx 어댑터 → 전 ~10개 라이브 데모가 각 Redeploy 시 흡수. 진단법 메모리 2종 환류([[pwa-sw-stale-cache]], [[pico-container-maxwidth-shell]]).
- **잔여 founder**: lawfirm-demo Redeploy 1회(새 sw.js + 새 app.css 둘 다) → 새로고침 1회로 헤더 풀폭 확인. SW 잔류 시 F12→Application→Service Workers→Unregister 후 reload.
- **교훈**: "배포가 안 보인다"는 추측 금지 — 라이브 DOM을 측정하고 후보 CSS를 주입해 증명한 뒤 커밋한다. 뷰포트-비례 여백 = max-width 컨테이너(고정 px padding 아님). HTML은 되는데 CSS만 안 되면 SW stale.
- §6 rollup: [Growth-129] lawfirm 헤더 여백 2중 결함 규명 — PWA SW stale 캐시(87091ac, network-first+csh-v2) + Pico 컨테이너 max-width(f252336, .app-* max-width:none). headless Chrome으로 x=186 w=1450→x=0 w=1822 측정 증명. 반복 검증 워크플로 → htmx-demo-verify skill 추출. 메모리 2종 환류. 전 데모 공통.

### Growth-130 — claude.ai/design ↔ repo 분리·통합 아키텍처 (deep-research 기반 설계 박제)

**맥락**: founder "디자인 조정 반복작업·시간 과다 + axis-8 산출물 밋밋. claude.ai/design 기능 활용 needs. 단 클라우드 분리 + 고객 복제본(구조변경0·데이터누출0) 가능해야". CTO 진단: 밋밋함은 구조적(토큰 재색칠+고정 variants), 시간싱크는 배포-왕복. claude-design=배포없는 즉시-렌더 craft 엔진이나 경계 선결. deep-research 하니스 가동(8 findings, 3-vote adversarial).

- **연구 확정 제약**: Claude Design = 유료티어·**BAA 제외(beta)**·기본 학습허용(opt-out 카브아웃2) → PII 절대 업로드금지(C2~C4). DTCG 토큰 2025.10(W3C CG, Rec 아님)·Style Dictionary v5+ include/source·Storybook Package Composition·vercel/platforms는 런타임라우팅(우린 빌드타임 정적이 우월).
- **아키텍처 4파트**(`docs/architecture/design-cloud-bridge.md`): (A)분리경계=클라우드 authoring-only/넘는것은 DTCG 토큰JSON뿐, 우리 raw→semantic→theme.yaml 계층이 곧 경계(신표준0) (B)정규화 게이트=CDO가 클라우드 컴포넌트를 catalog variant+토큰으로 분해해야 머지(직접붙임=복리붕괴) (C)복제본=빌드타임 물리격리(landing-astro SSG+고객 theme/profile 주입, 구조변경0) (D)CI가드 5종(업로드스코프·클라우드결합누출·교차테넌트누출·DTCG스키마·정규화게이트).
- **환류**: wiki synthesis [[claude-design-cloud-boundary]] + source [[deep-research-design-cloud-2026-06]] + index 2줄. 원본 `out/`(gitignored).
- **잔여**: ~~Phase2 가드5종~~(WP-2) · ~~Phase3 복제본 CLI~~(WP-3) · ~~WP-4 파일럿 측정~~(A/B 종결: cloud craft 2~3분 vs baseline 25분, 충실도 HIGH·normalize LOW, 라이브 픽셀 양 arm PASS, 판정=재사용 섹션 craft 한정 도입+repo 시각검증 훅 완화, design-loop SKILL 박제) **종결**. **잔여 = founder 채택결정 게이트**: 채택 시 → 신규 variant 로 landing-astro 병존 빌드(production Pricing.astro 덮어쓰기 ✗)·shadow 2종 theme.yaml 등록·scoped-CSS vs Tailwind 컨벤션 CDO 판정·net-new 섹션 재측정. legal 고객엔 BAA beta졸업 재검증 전 PII 금지.
- §6 rollup: [Growth-130] claude.ai/design 분리·통합 아키텍처 박제 — deep-research(BAA제외·학습기본·DTCG·Style Dictionary v5+·빌드타임 물리격리) 기반. 경계=토큰JSON, 정규화 게이트, 복제본 누출0·결합0·구조변경0, CI가드5종 후보. 문서+wiki 3페이지 환류. 구현은 후속 Phase.

### Growth-131 — HTMX swap/settle 전환 프리셋 (vanilla net-new 모션 역량)

**맥락**: 정찰이 "최고 레버리지 후속"으로 지목 — landing-astro 페이지 전환에 대응하는 vanilla-htmx 콘텐츠-스왑 전환. 기존 어댑터는 motion 토큰을 소비하되(Growth-130g) 스왑은 전부 무전환 스냅(`hx-swap=innerHTML` 다수).

- **신설**: `static/css/swap-transitions.css` — opt-in `.swap-fade/-up/-down/-slide-in` + `.swap-stagger`. library-free, `--motion-*` 토큰 구동, base.html 링크.
- **2단계 메커니즘**: IN=삽입-트리거 1회성 CSS animation(`.swap-* > *`, settle 타이밍 무의존 → footgun 회피, JS innerHTML 덮어쓰기 화면에도 작동) / OUT=`.htmx-swapping` opacity 페이드(`hx-swap` 에 `swap:120ms` 명시 시 가시).
- **불변식**: resting opacity 항상 1(opacity:0 은 keyframe from·htmx-swapping 한정) → G-69 no-JS-visible 유지. `prefers-reduced-motion` 전용 블록이 transform·stagger·duration 전면 중화(WCAG 2.3.3). 미적용 화면 byte-identical(motion off 기본 계승).
- **토큰 환류**: 미사용이던 `--motion-stagger-base` 첫 소비(계단식 6단계 캡). 신규 design 토큰 0(adapter-local `--swap-distance:8px`, motion-distance 승격 여지 주석).
- **데모 2곳**: `legal_precedent_search.html`(#results=fade-up+stagger) · `list-master-detail.html`(#detail-panel=slide-in, 행 swap:120ms).
- **검증**: L3 토큰빌드 PASS · L1 132 pass(잔여 1 fail=app.css hex, 무관 기존) · 가드 신규위반 0(FAIL 3건 out/·ledger·legal catalog 전부 기존) · CSS 브레이스 24/24·6 토큰참조 실존·키프레임 4종 정합.
- §6 rollup: [Growth-131] HTMX swap/settle 전환 프리셋 신설(swap-transitions.css) — opt-in fade/slide+stagger, motion 토큰 구동, IN=삽입트리거(settle footgun 회피)·OUT=htmx-swapping, G-69+reduced-motion 안전, --motion-stagger 첫 소비, 데모 2곳. landing 페이지전환 대응 vanilla net-new.

### Growth-131 라이브 검증 (lawfirm-demo redeploy 후, htmx-demo-verify headless Chrome)

- **fade-up+stagger LIVE PASS**: `/legal/search` 실제 htmx 검색 스왑에서 `#results` 자식이 `swap-in-up` 발화·토큰해석 280ms 확증. Stage0(에셋 200·`@keyframes swap-in-up`·`.swap-stagger` 라이브 서빙, SW stale 아님·push 반영) + 스타일시트 라이브 적용 PASS. (8/9 체크)
- **slide-in 라이브 미행사 — 코드결함 아님/deploy-config**: lawfirm-demo 에 `MASTER_DETAIL_ENTITIES` env 미설정 → `/type1`→`/home` 리다이렉트, 전 legal 엔티티가 `list.html`(plain)로 렌더(master-detail/top-bottom/modal 전부 false, server.py:567 `entity_type in _MD_ENTITIES` 게이트). slide-in CSS 계약은 로컬 headless 픽스처 13/13(swap-in-x·280ms)로 증명필. 라이브 확인하려면 founder가 `MASTER_DETAIL_ENTITIES=legal-case` 설정+redeploy.
- **부수 결함 환류(79a685e)**: htmx-demo-verify 로그인 패턴이 `/api/auth/login`(백엔드 JSON 토큰, Set-Cookie 없음) POST → 세션 미설정 → 인증 대상 대신 `/login` 페이지를 조용히 측정하던 결함. `/login` 폼 제출(세션쿠키)로 교정·라이브 스모크(`.app-header` x:0 w:1822) 확증. 메모리 [[htmx-demo-verify-skill]] 환류.
- §6 rollup: [Growth-131-verify] fade-up+stagger 라이브 PASS(/legal/search 실 htmx 스왑, swap-in-up 280ms). slide-in 은 lawfirm-demo MASTER_DETAIL_ENTITIES 미설정으로 라이브 미행사(코드 OK, config 갭). htmx-demo-verify 로그인 결함(/api/auth/login→/login 폼) 교정 환류.

### Growth-131 live-verify 종결 (slide-in 게이트 해소)
- founder가 lawfirm-demo에 `MASTER_DETAIL_ENTITIES=legal-case` env 추가 + redeploy → 이전 검증의 config-gap 해소.
- `verify_live_swap.mjs` 재실행 **12/12 PASS** (이전 8/9 → slide-in Stage2 4-check 전부 GREEN).
- Stage2: `/type1` master-detail 도달, `#detail-panel`=`swap-slide-in`, **실제 행 클릭 htmx swap에서 `swap-in-x` 발화 + duration 280ms(`--motion-duration-base` 토큰 해석)** 확증.
- 결론: swap-transitions.css 두 프리셋(fade-up/stagger, slide-in) 모두 라이브에서 실제 htmx swap에 행사됨. 코드 결함 0, 잔여 config-gap 0. Growth-131 end-to-end LIVE 종결.

### Growth-131b — reduced-motion override xslow 누락 a11y 갭 수정 (하드코딩→토큰셋 파생)
- CTO가 wiki 환류(Growth-131) 중 적발: reduced-motion override가 `--motion-duration-xslow`(640ms 페이지레벨 전환)를 붕괴 안 시킴. 원인=override 토큰 목록 하드코딩(fast/base/slow/intro 4종)이 토큰셋과 드리프트.
- 결함 2곳: `token_css_generator.py`(vanilla, py) + `build-tokens.mjs`(react, js) 동일 하드코딩. landing-astro는 token-override 없음(컴포넌트별 처리, 무관).
- 근본 수정(engineer): 하드코딩 4줄 → `sem_pairs`/`semPairs`에서 `--motion-duration-*` 접두 필터·정렬 순회로 파생. **신규 duration 토큰 자동 커버, 재발 불가**(open-closed).
- 재생성 검증: vanilla tokens.css L385-389 + react tokens.gen.css L274-278 모두 5종(xslow 포함) 붕괴 확인. pytest 26 passed(기존 무관 app.css raw-hex 1 fail 유지), diagnose 새 FAIL 0. wiki motion-tokens.md §3 INFERRED→EXTRACTED 해소.
### Growth-131c — ledger-index incremental cache (누적-민감 재파싱 제거) + create-context-graph 거부 결정
- founder가 create-context-graph(Neo4j Labs, github.com/neo4j-labs/create-context-graph)를 3-검색 앞단/메모리 대체 후보로 제시. CTO 측정으로 진단 후 거부.
- 측정(Measure-Command 분해): qmd "느림"=바이너리 spawn ~335ms 고정비(BM25 실검색 ~30ms, 누적 무관). 유일한 누적-민감 비용=ledger-index의 평면원장(190KB+360KB) 전체 재파싱 ~160ms. Neo4j는 둘 다 못 고침(서버왕복 추가)+self-host/cost-aware wedge 정면충돌+codegraph SQLite 중복.
- 차용한 아이디어("그래프 메모리 증분 갱신")만 흡수: `ledger-index.py` build_index에 content-hash(sha256) 캐시(`_index.cache.json`, gitignored). parse+extract만 캐시(파일내용 순수함수), codegraph 검증·전역 dedup·정렬은 매번 신선. mtime 아닌 content-hash(checkout 견고).
- 정확성: HEAD 원본과 `_index.json` byte-identical(sha256 c7022ec8, 콜드·웜 동일) 독립 검증. in-proc build_index 콜드 85ms→웜 31ms(2.7x). diagnose 새 FAIL 0. 커밋 41e413c(ledger-index.py)+805d7b1(.gitignore) 푸시.
- 환류: wiki concepts/asset-search-architecture.md 신설(누적 자산 3-tier 검색 + 측정 프로파일 + 결정), index.md +1줄, qmd wiki 재색인(asset-search 검색 85% 확인). 사용자 최초 질문("누적 자산 검색 방식")의 커버리지 갭 종결.
- Files touched:
  - `scripts/ledger-index.py`
  - `.gitignore`
  - `knowledge/wiki/concepts/asset-search-architecture.md`
  - `knowledge/wiki/index.md`

### Growth-132 — 한방 RAG 데모 D0: services/hanbang-rag/ 포크 (legal-rag → 한방 버티컬)
- CTO greenlight 3결정(테이블 hanbang_rag_*, auth+단일데모계정, FastAPI독립+postgres/embed공유) 확정 후 D0 착수. engineer-agent 위임.
- **재구현 금지 준수**: ingest/retrieve/citation/auth/db/embed_client/config + embed-adapter 카피 후 최소 SQL 교체만. 검색 파이프라인(FTS+ANN+RRF) 완전 재사용.
- **테이블 네이밍(founder 확정)**: `hanbang_rag_notice` / `hanbang_rag_document_chunk` / `hanbang_rag_user` / `hanbang_rag_query_log` (서비스 슬러그=테이블 프리픽스 일치).
- **단일 소스타입 단순화**: legal-rag의 precedent+case_document 2갈래 → 한방 고시(notice) 1갈래. ingest의 _CHECK_CASE_DOC/_UPDATE_CASE_DOC_STATUS 분기·citation의 _RESOLVE_CASE_DOC 분기·Citation case 필드 전부 제거. Citation 메타=고시번호/소관부처/발령일자/요약.
- **D0 범위 경계**: api.py(D1 신규작성)·web/(D3 카피교체) 의도적 제외 — legal 엔티티 의존성이 pytest를 깨뜨리므로 파이프라인 코어+단위테스트만.
- **CTO 통합검증(보고 비신뢰, 독립 재현)**: ①잔존 legal_ 테이블 참조 0(주석 3건뿐) ②hanbang_rag_ 34곳 적용 ③pytest **29 passed** 독립 재현 ④api.py/web 부재 확인. PASS.
- 커밋: 실질변경 3파일(ingest/retrieve/citation) 단독 + 복사본 3그룹(인프라/embed-adapter/tests) = 8커밋. master 푸시(8485419..a953a71).
- **D1 미결(인계)**: hanbang_rag_notice 컬럼스키마 확정→citation SELECT/Citation 매핑 검증, document_chunk의 case_id 컬럼 잔재 제거여부, hanbang_rag_query_log/hanbang_rag_user DDL 신규작성, api.py 신규작성(/search,/ingest,/health,/auth/login,/documents/notice/*).
- 비용: postgres·embed-adapter 공유로 신규 월비용 ≈ FastAPI 컨테이너 1개+서브도메인. M3(첫 버티컬→두번째) 기여.
### Growth-133 — 한방 RAG 데모 D1: DDL(4테이블) + api.py 신규 + case_id legal 잔재 정리
- DBA가 contract-first DDL 작성: D0 코드가 SELECT/INSERT하는 컬럼을 역도출해 `services/hanbang-rag/sql/` 8파일(00_extensions~07_seed). 매핑표 불일치 0(citation/ingest/retrieve/auth의 모든 SQL ↔ DDL 컬럼 1:1).
- **4테이블**: hanbang_rag_notice(고시번호/소관부처/발령일자/notice_type TEXT/요약/전문) · hanbang_rag_document_chunk(vector(768) HNSW cosine + FTS simple GIN, source_type='notice' CHECK) · hanbang_rag_user(bcrypt) · hanbang_rag_query_log.
- **RLS 단순화(CTO 지침)**: 한방 고시=공개 참조데이터(PII 0, 전 사용자 동일열람) → notice/chunk RLS 비활성(legal 청크격리 RLS 미포팅), 쓰기제한은 grant(app_user INSERT 미부여)로. query_log만 user_id RLS(Phase 2 멀티계정 대비·legal 패턴 재사용). 향후 공개 랜딩 테넌트는 CISO 게이트 후 재검토.
- **case_id legal 잔재 clean 제거**: DBA가 DDL에서 제거 → engineer가 코드 정합. ingest UPSERT 9→8컬럼, retrieve _FETCH_CHUNKS_SQL row 재인덱싱(case_id 제거로 row[3]=chunk_index/row[4]=chunk_text/row[5]=token_count)·case_filter 고정 빈값·RetrievedChunk 필드 제거. CTO가 grep으로 제거범위 확인 후 결정(테스트 1곳만 검증=contained).
- **engineer cwd-hook-fragility 재발**: Read/Edit 차단으로 직접수정 불가 → fail-safe 패치스크립트(`_patch_d1_case_id.py`, 미발견시 sys.exit(1)) 작성. **CTO가 라인별 검토 후 적용** — 결함 적발: open(w) newline 미지정 → Windows LF→CRLF 변환. 적용 후 3파일 LF 정규화로 교정. 메모리 [[subagent-cwd-hook-fragility]] 재확증.
- **api.py 신규(~310줄)**: legal api.py(63KB) 모델로 lean 재작성. /auth/login(hanbang_rag_user+JWT)·/health·/health/detail·/ingest(notice 고정, service token)·/search(retrieve→citation→log_query, rls_session)·/documents/notice/{id}(full_text 원문, 인터뷰 신뢰전달). case/party/attorney/document-upload 엔드포인트 전부 제외. retrieve/citation/ingest/auth/db 와이어만(재구현 0).
- **CTO 통합검증**: case_id 잔재 0(주석조차)·py_compile 8모듈 OK·pytest **29 passed**·DDL↔코드 불일치 0. api.py L115 pyright(**docs_kwargs None 추론)·import 미해결은 config/추론 아티팩트(런타임 무해, py_compile/pytest 통과)→D3 pyrightconfig 정리.
- 커밋: DDL 2그룹(schema/grants+seed) + api.py + ingest/retrieve/test 단독 = 6커밋 푸시.
- **D2 미결**: VPS corpus 수집(fetch_hanbang_admrul.py, 고시 4건)→XML파싱→hanbang_rag_notice INSERT→/ingest. sql/ DB적용(psql/Coolify). bcrypt 실해시(CISO). 배포env 5종(DSN/EMBED_URL/JWT_SECRET/SERVICE_TOKEN/INGEST_ROOT). catalog.yaml 환류 후보="공개 참조데이터+RAG 청크" 패턴(CTO 승인 후).
### Growth-134 — 한방 RAG 데모 D2(일부): corpus 라이브 수집 (founder "corpus만 먼저" 게이트)
- founder가 D2 진행을 "corpus만 먼저 수집"으로 선택(DB적용·ingest·배포는 DSN/Coolify 준비 시점까지 대기). CTO가 VPS(187.77.140.157) SSH로 실수집 수행.
- **스크립트 업그레이드**(fetch_hanbang_admrul.py): PoC(본문 1건 증명) → 다건 수집 + manifest.json(ingest 연결). engineer 설계 위임했으나 cwd-hook로 파일 못읽어 **dict 키 불일치**(부처명/법령일련번호 vs 실제 ministry/seq) → CTO(integrator)가 실제 키로 보정 적용(PowerShell, engineer 구조적 blind).
- **핵심 발견 — admrul API 본문 구조**: law.go.kr `lawService.do?target=admrul&ID=<일련번호>&type=XML`이 고시별로 다르게 반환. 건강보험 「요양급여 세부사항」·「행위 급여·비급여 목록표 및 상대가치점수」는 **개정문(thin, ~3K자, 별표 미포함)만** → 데모 corpus 부적합. 의료급여수가·비급여보고·의료기술분류는 **전문(rich, 180~720K자)** 반환. **큐레이션 정답=키워드+제목필터 ✗, 검증된 seq 직접지정 ○**(TARGET_SEQS 상수).
- **버그 수정**: empty-detector(`"없습니다" in decoded`)가 1MB 정상문서를 부분문자열 매칭으로 오탐 거부 → `len<300 or (len<2000 and marker)` 로 수정. 의료급여수가 720K 수신 회복.
- **수집 corpus 3건(~1.97MB, 전부 보건복지부 고시 원문)**: 의료급여수가 기준(720K, 추나12·한방38·한의7) + 비급여 진료비용 보고(544K, 추나13·약침3·첩약1) + 보건의료기술 분류체계(183K, 한의5). manifest.json(seq/name/ministry/date/char_count/xml_file) parse_detail_meta로 본문 XML서 메타 추출. VPS out/corpus/hanbang/.
- **데모-적합 caveat(founder 보고)**: 수집 corpus는 **의료급여+비급여**가 중심, 페르소나(한의원 청구담당)의 주력인 **건강보험 요양급여/상대가치점수 전문은 API 한계로 미수집**. 실제 한방 급여 내용(추나/약침/한방)은 풍부해 "고시 원문 검색" 데모 신뢰전달엔 충분하나, 건강보험 상대가치 corpus 보강은 follow-up(별표 별도 API 또는 HIRA 경로).
- 커밋: fetch 스크립트 다건화(ed5126b 직전)+큐레이션(bf19557). 3커밋 푸시.
- **D2 잔여(founder 게이트)**: shared postgres에 sql/ 8파일 적용(DSN) → XML 파싱→hanbang_rag_notice INSERT(manifest 기반)→/ingest 청킹·임베딩. bcrypt 실해시(CISO). 배포env 5종은 D3. VPS 잔여 probe 파일(probe*.py) 정리 필요(무해, OC 비내장).
