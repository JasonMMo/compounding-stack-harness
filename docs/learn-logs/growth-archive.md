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
