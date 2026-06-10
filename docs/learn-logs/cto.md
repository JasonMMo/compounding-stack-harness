# learn-log — CTO

> Architect / VP / Integrator. 7축 설계·contract 결정·일일 의사결정·cross-agent catch 의 단일 점검소. 코드 직접 작성은 engineer 에 위임.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 이 파일은 CTO 가 닿은 Growth 의 상세.

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Role here: <CTO 가 한 역할 — Architect / VP / Integrator 중>
- Decisions made: <단독 결정 + 합의 결정>
- Cross-agent catches: <다른 인격 영역에 던진 신호>
- Escalations: <CEO 에 올린 항목>
- Cost of my decisions: <LLM/infra 영향>
```

## §2 — Growth History (CTO 만의 관점)

### Growth-4 (2026-05-29) — 4-인격 → 6-인격 확장 + learn-log per-agent 분리

- **Role here**: Integrator (인격 경계 재설계) + Architect (learn-log 구조 변경)
- **Decisions made**:
  - 인격 분리 트리거 채택 — CEO 제안 "learn-log 가 무거워져 main context 가 길어진다" 에 동의
  - engineer-agent / qa-agent 2 인격 신설, CTO 에서 구현 권한 + 통과 기준 권한 분리
  - learn-log 구조: main 은 §0~§4 + §6 1줄 rollup, 인격별 상세는 `docs/learn-logs/<role>.md`
  - Growth-1~3 historical 보존 (retroactive 분리 안 함) — git history churn 회피, 새 포맷은 Growth-4 부터
  - CTO 잔존 책임 명시: Architect + VP + Integrator (코드 작성 ✗, 가드 *정의* O, 가드 *본문* ✗, 가드 *통과 기준* ✗)
- **Cross-agent catches**: 없음 (이 Growth 가 만든 게 인격 자체)
- **Escalations**: 없음 — CEO 제안을 CTO 가 receive 한 사례, 역방향
- **Cost of my decisions**:
  - LLM: 본 세션 1회 (Opus 4.7) — Growth-3 후 연속 작업
  - Infra: 0 (.claude/agents 2 파일 + docs/learn-logs 5 파일 + 헌장 3 파일 갱신)
  - 향후 비용 영향: agent 분리 후 subagent 호출 패턴 변경 — 예상 budget engineer \$100/월 + QA \$40/월 (per agent file 추정치)

### Growth-5a (2026-05-29) — Growth-4 trade-off 4 항목 잠금

- **Role here**: Integrator (인격 분리의 후속 위험 잠금) + Architect (G-9 + 슬림 spec 박기) + VP (charter §3 #5 정식화)
- **Decisions made (CEO 위임 "추천안으로 가자")**:
  - (a) 슬림 포맷 spec block 박음 — divider 직후 7-field 코드 펜스, 각 Growth 가 "어디서 시작·뭐가 들어가야 하는지" 시각적 가이드
  - (c) `docs/learn-logs/synthesis-template.md` 박음 — 분기당 1 페이지 cross-인격 narrative 복원소
  - (d) G-9 가드 박음 — 본문 비-blank ≤10행/엔트리, 슬림 §6 전체 ≤200행. 코드 펜스는 검출 제외 (spec template 자체가 자기 가드에 안 걸리도록)
  - (f) charter §3 #5 "Integrator 마무리 step" 추가 — main §6 슬림 엔트리는 *CTO 단독 작성*. 인격 ledger 상세는 각자 쓰되 main rollup 은 한 손이 잡는다
  - charter §8 v1.2 row 추가 — Growth-5a 변경 이력
- **Cross-agent catches**: 없음 (CTO 자기 영역 잠금)
- **Escalations**: 없음 — CEO 가 "추천안" 으로 위임함
- **Cost of my decisions**:
  - LLM: 본 세션 turns ~30, Opus 4.7 단독 (subagent 호출 0)
  - Infra: 0 (diagnose.py 함수 1 추가 + 6 파일 갱신·생성)
  - 향후 비용 영향: G-9 가 매 PR 마다 학습 비용 0 으로 main §6 비대를 막음 — 인격 분리 ROI 의 보험

### Growth-5b (2026-05-29) — charter v1.3 (private master push 자동화) + GitHub 첫 등재

- **Role here**: VP (charter §3 #3 조건부화 설계) + Integrator (3 파일 동기화 + repo 외부 등재)
- **Decisions made**:
  - CEO 직접 제안 "master 푸시를 자동으로" 수용. 단, **public 전환 시 사전 확인 룰 자동 재발효** 조건부 룰로 박음 — reversibility 보존
  - Repo visibility: **private** (CMO 회수 #3 OSS/상용 분리선 미정 — public 전환은 cheap, private→public 후엔 인덱싱 회수 비쌈)
  - Repo 이름: `compounding-stack-harness` (로컬과 동일)
  - Description: "Expert-agent-driven self-host full-stack codegen harness. 7-axis compounding..." — positioning.md 한 줄 약속 압축
  - 3 파일 동기화 순서: charter (근거 문서) → CLAUDE.md → AGENTS.md (각 파일당 별도 커밋)
- **Cross-agent catches**: CMO 회수 질문 #3 (OSS/상용 분리선) 이 public 전환 시점을 결정한다 — 두 결정이 묶임
- **Escalations**: 없음 — CEO 가 먼저 제안한 변경
- **Cost of my decisions**:
  - LLM: 본 세션 turns ~10, Opus 4.7 단독
  - Infra: github.com private repo 1개 (free tier)
  - 향후: public 전환 즉시 charter §3 #3 룰 자동 재발효 — 코드 변경 0, 의미론적 게이팅

### Growth-5c (2026-05-29) — CDO tokens.md M0 인수 + 4 escalation 응답

- **Role here**: Integrator (CDO ↔ adapter contract 정합성 판정) + Architect (token versioning 정책 박음)
- **Decisions made (8 escalation 중 CDO 4 분량)**:
  - **Q1 Dark mode 정책 (보류, M2 게이트)** — M0~M1 에는 light 만. M2 첫 고객의 IT 페르소나 실제 사용 패턴 확인 후 결정. CDO 추천 `.theme-dark.persona-it` 2층 scope 안은 메모로 보존. 이유: dark token set 추가 = Nexacro XTHEME 파일 2배 — adapter 출하 전 결정은 비용·정보 부족.
  - **Q2 i18n label 소유권 (adapter)** — token 층은 시각만, `<html lang>` + label 자체는 customer profile + adapter 가 관리. `locale.*` token group 추가 안 함. 이유: contract 단순성 유지, KWCAG 3.1.1 은 adapter 가 lang attr 주입으로 충족.
  - **Q3 Token versioning adapter compliance test 포함 (YES)** — raw→semantic 분리가 이론상 격리하지만 actual value 변경 (brand color M1 교체) 도 compliance test 가 verify. 첫 adapter 등록 시 test fixture 에 token snapshot 포함 — engineer 가 M1 adapter 작업 시 구현.
  - **Q4 CEO 페르소나 mobile breakpoint (추가)** — `breakpoint.tablet: 768px` 박음. CEO 페르소나가 < 768px 일 때 `type.size-kpi` 40px → 28px, `space.section-gap` 48px → 32px override. iPad 사용 시 KPI 가 viewport 압도 회피. CDO 가 tokens.md §3.1 + §8 에 breakpoint row 박음.
- **Cross-agent catches**: 없음 (CDO 산출물 수용)
- **Escalations**: 없음 — CDO 가 던진 4건 모두 CTO Auto 결정
- **Cost of my decisions**: LLM 본 세션 turns ~5, Opus 4.7. Infra 0. 향후 영향: M2 dark mode 결정 시 token set 추가 비용 +1 day; M1 adapter compliance test fixture 추가 +0.5 day

### Growth-5d (2026-05-29) — Engineer M1 entry kickoff + 4 escalation 응답 (contract 표준 박힘)

- **Role here**: Architect (contract semantics 표준화) + Integrator (engineer ↔ QA 인계점 판정)
- **Decisions made (Engineer escalation 4건)**:
  - **Q1 `entity.update` PATCH vs PUT** — **PATCH semantics 표준** 유지. absent field = unchanged. PUT full-replace 가 필요한 adapter 는 wrapper 패턴 (`entity.update` 호출 전에 full body 합성)으로 contract 변경 없이 구현. 이유: partial update 가 더 일반적·적은 데이터·optimistic concurrency 와 결합 쉬움.
  - **Q2 `entity.delete` 404-as-success** — **표준화 (idempotent: true 유지)**. adapter compliance test 가 "2회 호출 → 둘 다 success" 검증. backend 가 강한 404 던지면 adapter 가 success 로 매핑. 이유: REST 관행 일치 + 멱등성이 contract 약속의 일부.
  - **Q3 OpenAPI 3.1 migration timing** — **첫 adapter 직후 (M1 후반)**. adapter 구현 경험으로 schema 갭 발견 후 migration. 이전 migration 은 toolchain 의존만 도입하고 학습 0. wire-v1.yaml 은 M1 동안 plain YAML 유지.
  - **Q4 `auth` secrets 분리 (schema v1 = NO, v2 검토)** — 현재 형태 (`auth.sso_client_secret: ${ENV_VAR}`) 유지. G-4 가 round-trip 안전을 이미 보장. 별도 `secrets:` top-level 은 schema v2 후보 (회수 #: customer profile 이 5+ block 늘어나면 재검토).
- **Cross-agent catches**: QA 에 던질 신호 — entity.delete 404-success + entity.update PATCH 가 adapter compliance test 의 첫 2 row. QA 미가동이라 cto.md 기록만, M1 QA 가동 시 인계.
- **Escalations**: 없음 — Engineer 가 던진 4건 모두 CTO Auto 결정
- **Cost of my decisions**: LLM ~5 turns Opus 4.7. Infra 0 (Engineer 가 wire-v1.yaml 에 PATCH/404 결정 inline 반영). 향후: OpenAPI migration 첫 adapter 후 +1 day, schema v2 (secrets 분리) 는 5+ customer profile 도달 시 0.5 day.

### Growth-5e (2026-05-29) — CMO 회수 질문 4건 답변 통합 (Growth-3 open loop 해소)

- **Role here**: Integrator (CEO 답변 → positioning.md / charter 정렬)
- **Decisions made (CEO 직접 답변 처리)**:
  - **Q1 가격대 ($10k~$30k 보류)** — CEO "1번으로 가고싶지만 시스템 성숙도 부족, 고객 기대치 초과까지 미룬다". positioning.md 에 "pricing disclosure deferred until system maturity ≥ customer expectation threshold (CEO 결정 2026-05-29)" 박음. M2 첫 paid customer 협의 진입 시 가격대 공개 게이트 — CEO 가 평가.
  - **Q2 첫 vertical 시그널 (CEO 합의)** — "첫 paid customer 의 산업 = 첫 vertical" 이미 charter §2 게이트로 박혀 있음 (charter §2 row `첫 vertical 선택 = CEO+CTO+CMO`). 재확인만, 추가 변경 없음.
  - **Q3 OSS/상용 분리선 (M2 후 결정, Recommended)** — charter v1.3 의 public 전환 게이트 (§3 #3 조건부 룰) 와 자연 정렬. positioning.md 에 "OSS line decision deferred to post-M2 customer talks" 박음.
  - **Q4 M3 landing 책임자 (CMO + CDO 협업, Recommended)** — charter §2 decision matrix 에 `landing/portal 비주얼 = CDO` + `sales enablement = CMO (CDO 비주얼 협업)` 이미 매핑. 추가 row 없이 positioning.md 에 "M3 vertical landing = CMO copy + CDO visual" 박음.
- **Cross-agent catches**: 4 답변 중 Q1 (가격) 이 "system maturity threshold" 라는 측정 불가능한 게이트를 도입함 — Growth-5+ 시점에 "maturity = M1 14 preset PASS + acme-erp end-to-end demo" 같은 측정 정의 필요. M1 마무리 Growth 에 박을 후보.
- **Escalations**: 없음 (CEO 가 직접 답함)
- **Cost of my decisions**: LLM ~3 turns Opus 4.7. Infra 0. 향후: maturity threshold 측정 정의가 M1 마무리 게이트 하나 추가.

### Growth-5f (2026-05-29) — colbymchenry/codegraph 설치 (2-step gate + tenant 분리 요구)

- **Role here**: VP (외부 시스템 도입 결정) + Integrator (자산 정착 위치 + tenant 분리 설계 open loop)
- **Decisions made**:
  - **(a) Upstream colbymchenry/codegraph 채택 (NOT JasonMMo fork)** — fork 는 0 stars + 변경점 불명, upstream 은 v0.9.7 active maintainer. CEO 직접 지정.
  - **(b) 2-step gate adoption** — install 즉시 (이번 Growth) + measurement 는 M1 첫 adapter Growth 마무리에. 4-measurement: (1) 질문 답변율 (예: "어느 인격이 wire.entity.update 결정 owner?") (2) 7축 환류 자동화 (catalog/preset 누락 탐지) (3) 고객 가치 (lock-in 회피 — `.codegraph/` rebuildable from source) (4) 유지 비용 (인덱싱 turns·시간). 통과 못하면 `codegraph uninit` 으로 reversible 종료.
  - **(c) 누적 데이터 정책 — project 자산 + 고객별 분리 가능** — CEO 직접 박음. `.codegraph/` 는 우리 자산 (지식 누적), 단 고객사 self-host 시 그 고객의 `.codegraph/` 는 그 고객 데이터. 즉 tenant scope = per-repo (codegraph 의 기본 동작과 일치). 별도 export/sanitize API 필요 여부는 M2 첫 고객 협의 시 재평가.
  - **(d) 정착 위치 — axis 등록은 보류** — 7축 (skill/ddl/middle/frontend/backend/creater/customer/expert-agent) 중 어디에도 안 들어감. codegraph 는 "축을 운용하는 메타 도구" 이지 축 자체가 아님. M1 마무리 measurement 후 채택 확정 시 docs/architecture/ 에 별도 문서.
  - **(e) install 형태** — local (project-scoped `.mcp.json` + `.claude/settings.json`) NOT global. 이유: 다른 repo 와 격리, charter 의 reversibility 원칙 부합.
- **Cross-agent catches**: 없음 (인프라 결정, 인격 산출물 영향 없음)
- **Escalations**: 없음 (CEO 가 "CTO 권고안으로 진행" 직접 위임)
- **Cost of my decisions**:
  - LLM: install·결정 ~5 turns Opus 4.7. measurement Growth 별도.
  - Infra: codegraph npm global 1 binary (~44 KB 패키지 + deps 0 + sqlite native), `.codegraph/` DB local 만 (gitignore), MCP stdio 1 server. 외부 호출 0 (local-first).
  - 향후: M1 첫 adapter Growth 에 측정 0.5 day. 채택 시 tenant 분리 메커니즘 설계 +1 day. 거부 시 `codegraph uninit` ~10 min.

### Growth-6 (2026-05-29) — 14 generic skill seed + _seed-format.md spec

- **역할**: Architect (포맷 설계) + Integrator (engineer 위임·커밋 체인 검증)
- **산출물**: `presets/skills/generic/_seed-format.md` + 14 `*.seed.md` (hr/finance/logistics/inventory/sales/crm/procurement/production/quality/project/asset/document/approval/reporting)
- **Seed 포맷 결정**: YAML frontmatter (domain/label/version/entities/wire_keys) + 5-section MD (Purpose/Core Entities/Domain Operations/Business Rules/Integration Points). Karpathy 원칙: minimal, machine-parseable, wire-aware, compound-friendly.
- **Engineer 위임**: Sonnet 4.6 subagent 1회 — 14 파일 생성 + 14 커밋 (파일당). 품질 검증: hr.seed.md spot-check → 4 entities, 4 business rules, 3 domain ops, 2 integration points. 포맷 100% 준수.
- **Guard result**: G-8 53→70 entries (seed 파일 반영). G-9 7→8 slim entries, 64→73/200 lines. 전체 9 가드 PASS.
- **Cross-agent catch**: engineer.md Growth-6 엔트리 위임 대상.
- **Open loops resolved**: M1 Priority 1 완료. M2 acme-erp demo prerequisite 충족.

### Growth-7 (2026-05-29) — 첫 backend adapter 통합 + G-1 활성 + contract 정합 결정 4건

- **역할**: Architect (adapter 설계 제약·contract 결정) + Integrator (engineer·qa 위임·검증 체인 마무리)
- **산출물 (CTO 직접)**: `error/codes.yaml` (11 코드) · wire-v1.yaml paging flat-underscore 직렬화 컨벤션 · `middle/contract/README.md` + `presets/skills/INDEX.md` (G-5 manifest) · G-5 glob `**/*.seed.md` 강화
- **결정 4건**: (1) error envelope = object `{code,message,details}` (2) paging HTTP 직렬화 = nested→flat underscore (`paging.mode`→`paging_mode`; QA 가 dot-notation drift 적발) (3) gradle-wrapper.jar **추적** — engineer 의 ignore 결정 뒤집음 (self-host "dev 환경 없이 빌드" 가치) (4) G-1 검출 정책 = code→http_status 재선언 FLAG, 문자열 참조 ALLOW
- **위임**: engineer (adapter 19커밋 + 버그수정 + G-1 구현) / qa (compliance 첫 실전 가동)
- **Cross-agent catch**: G-5 가 middle 자산 2개 도달로 **FAIL** 발화 → manifest 로 해소. 동시에 skill axis glob 이 `generic/` 하위 14 seed 를 못 보던 **갭** 발견 → 강화 (가드 약화 아닌 강화, feedback: guards-must-work). QA **BLOCK 2건**이 paging 진짜 버그 적발 → engineer 환류 → 23/23.
- **Guard 상태**: 9 가드 0 FAIL. G-1 SPEC→PASS, G-4·G-5 카탈로그 동기화. §2/§4 갱신.
- **Open loops resolved**: M1 Priority 2 절반 (backend). G-1 활성화 open loop 해소.

### Growth-8 (2026-06-01) — 첫 frontend adapter 통합 + frontend 계약 박기 + CDO 첫 가동 통합

- **역할**: Architect (frontend-adapter 계약 설계) + Integrator (CDO·engineer·qa 3-인격 체인 마무리·border-input 판정)
- **산출물 (CTO 직접)**: `docs/architecture/frontend-adapter-contract.md` — backend 의 응답-서버 compliance 와 다른 **요청-발신자** 계약. F-1 (flat-underscore 직렬화) / F-2 (paging 2모드) / F-3 (error envelope code 분기·message_ko) / F-4 (idempotent delete) 4 준수점 + frontend 판 compliance 게이트 (FRONTEND_BASE_URL+BACKEND_BASE_URL) 정의. react/vue/nexacro 미래 adapter 의 단일 기준.
- **결정 4건**: (1) frontend adapter 정체 = thin self-host proxy server (htmx 템플릿 + wire reverse-proxy), backend 무관 (2) `color.border-input` 독립 semantic 토큰 = gray.400 (3.05:1, WCAG 1.4.11 통과) — CDO escalation 판정, CEO 페르소나만 문서화된 예외 (3) `tokens.css` gitignore — `build_tokens.py` 가 JSON 단일 진실에서 재생성하는 파생 산출물 (gradle-wrapper.jar 와 대비: 후자는 repo 소스에서 비-파생이라 추적) (4) commit trailer 4.7→4.8 동기화 (실제 co-author 모델 반영, mixed history 는 정직한 전환 기록)
- **위임**: CDO (토큰 raw/semantic/persona×3 + 컴포넌트 표준 3 + a11y, 첫 실전 가동) / engineer (adapter 22 파일 + CSS 생성기 + contract_loader) / qa (frontend compliance 게이트, 2번째 가동)
- **Cross-agent catch**: CDO 가 input border 1.52:1 (WCAG 1.4.11 미달) 적발 → CTO 가 border-input 독립 토큰으로 해소 (가드 약화 아님 — 토큰 분리로 ops/it 컴플라이언스 + CEO 의도적 예외 양립). QA first-pass PASS (Growth-7 의 BLOCK→fix 와 달리 결함 0) — engineer 가 contract 문서를 정확히 구현한 결과.
- **Guard 상태**: 9 가드 0 FAIL. G-1 이 2 adapter (backend+frontend) 스캔, frontend contract_loader.py 가 재선언 0 으로 PASS.
- **Open loops resolved**: M1 Priority 2 완료 (frontend). CDO 첫 가동·codegraph measurement 시점 도달.

### Growth-9 (2026-06-01) — codegraph 2-step gate measurement → 조건부 ADOPT

- **역할**: VP (외부 도구 채택 판정) + Architect (scope 경계 박기)
- **산출물 (CTO 직접)**: `docs/architecture/codegraph-adoption.md` — 4-measurement 실측 + 판정.
- **실측**: 32 files/511 nodes/855 edges, reindex 780ms. **언어 = python/java/yaml/kotlin/properties 만 — markdown·json 인덱스 0** (skill seed·learn-logs·design tokens 불가시). canonical 질문 2종 실측: 코드구조형 GOOD / 인격-결정-owner형 (Growth-5f 원래 동기) **FAIL** (답이 markdown ledger 거주).
- **판정 (조건부 ADOPT)**: (1) 코드 네비게이션 도구로만 채택 — adapter 작업 심볼탐색·call path·impact (2) **거버넌스/결정-ownership 용도 DESCOPE** — 그건 diagnose.py 가드 + per-agent ledger 단일 진실 (3) axis 미등록 (메타도구, Growth-5f lean 확정) (4) 정착 = docs/architecture (5) 운영룰 = 큰 변경·세션재개 후 `codegraph sync` (stale 리스크 차단) (6) tenant 분리 = per-repo gitignore 재생성으로 이미 충족 (7) reversibility = `codegraph uninit` 보존.
- **Cross-agent catch**: M-2 (7축 환류 자동화) 에서 codegraph 가 diagnose.py 보다 약함 확인 — 가드가 전 파일타입 grep 으로 이미 우위. 도구 중복 회피 결정.
- **Open loops resolved**: Growth-5f 2-step gate 2번째 step 종결. codegraph 거취 확정.

### Growth-10 (2026-06-01) — ddl 축 채움 + G-10 정의 + QA L2 첫 가동 통합

- **역할**: Architect (catalog format spec + G-10 가드 정의) + Integrator (engineer·qa BLOCK→fix→PASS 체인 마무리)
- **산출물 (CTO 직접)**: `presets/ddl/_catalog-format.md` — neutral 8-type closed set, catalog.yaml 엔트리 형식 (columns/fk/on_delete/constraints/indexes), dialect yaml 형식, multi-tenant 경계 (M5 보류), wire 정합, G-10 3-check 정의.
- **결정**: (1) neutral 8-type 만 (uuid/string/text/integer/decimal/boolean/date/timestamp/enum), enum→VARCHAR+CHECK 전방언 이식 (2) dialect 분리 — postgres·hsqldb full, mysql·oracle 타입맵 stub (open-closed) (3) **tenant_id 컬럼 M5 게이트까지 미박음** (premature multi-tenancy 회피) (4) `presets/ddl/build/` gitignore — render.py 가 catalog 에서 재생성하는 파생물 (tokens.css 선례 일관) (5) adapter 검증 wiring 은 후속 Growth (catalog→InMemoryStore) (6) patch_schema.py 보존 — QA 의 regression-가드 권고 수용 (CQO test hygiene 권한)
- **G-10 정의**: seed entity ⊆ catalog / 모든 fk.entity 실재 / 모든 type closed-set. CTO 가 정의, engineer 가 본문, QA 가 통과기준 — 3-인격 분리 원칙 적용.
- **Cross-agent catch**: QA L2 첫 가동의 BLOCK 이 render.py 3 결함을 적발했으나, QA 가 patched-schema 47/47 로 **catalog 와 renderer 를 분리 진단** — Integrator 로서 이 격리가 정확함을 확인하고 fix 를 renderer 에만 라우팅 (catalog 무수정). Growth-7 패턴 (QA BLOCK→engineer fix→QA PASS) 의 2번째 실증, 이번엔 L2 layer.
- **Escalation 수신**: engineer 가 `finance_journal_entry.period_id` FK 부재 (accounting_period 미존재) 보고 → application-layer 검증으로 충분, 57번째 entity 는 period-close DB 가드 필요 시 후속 Growth 후보로 deferred.
- **Open loops resolved**: ddl 축 첫 채움 (M2 prereq 1개 충족). G-10 신설로 가드 10개.

### Growth-11 (2026-06-01) — 2nd backend (fastapi) 통합 + 공유 suite 단일화 + adapter-agnostic 실증

- **역할**: Architect (fastapi 픽 + backend 축 manifest + suite 단일화 설계) + Integrator (engineer·qa 체인 + G-5 해소)
- **결정**: (1) **fastapi 픽** (CEO "react 또는 fastapi" 위임 → CTO 선택) — backend swap 이 "한 contract 가 Java↔Python 구동" 차별화를 직접 실증하고, black-box compliance suite 의 **첫 재사용**으로 suite 의 adapter-agnostic 설계를 검증하며, axis-7 domain-expert 와 Python 결합이 자연. react(2nd frontend)는 M1 잔여로 후순위. (2) **G-5 해소** — fastapi 가 backend 축을 2-asset 으로 만들어 manifest 트리거 → `backend/adapters/INDEX.md` 작성 (Growth-7 middle/contract/README.md 와 동형, feedback_guards_must_work). (3) **compliance suite 단일화** — QA 가 `tests/adapters/_shared/` 로 옮겼으나 springboot 에 identical copy 잔존 → CTO 가 import shim 으로 진짜 단일 진실 지시 (테스트 코드도 single-source dogma 적용; "3rd adapter 시 정리" deferral 거부).
- **산출물 (CTO 직접)**: `backend/adapters/INDEX.md` — backend 축 manifest (등록 adapter 표 + 공통 8 wire key 계약 + 공유 suite 재사용 절차 + 새 adapter 추가 절차).
- **Cross-agent catch / Integrator**: engineer 의 G-5 FAIL 보고를 manifest 로, QA 의 중복 copy 를 shim 으로 — 두 인격의 부산물을 single-source 로 수렴. **adapter-agnostic 주장 검증 완료**: 동일 23-test suite 가 Spring Boot(Growth-7)·FastAPI(Growth-11) 양쪽 assertion 변경 0 으로 green. CLAUDE.md §4 pluggable backend 가 테스트 layer 에서 증명됨.
- **Escalations**: 없음 (CEO "1→2→3" 위임 범위 내, fastapi 픽은 VP 권한).
- **Open loops resolved**: M1 backend 축 2번째 + 공유 suite 검증. 남은: react adapter, adapter 검증 wiring (catalog→store).

### Growth-12 (2026-06-01) — 검증 계약 + 양 adapter wiring + 가드 회귀 진단·라우팅

- **역할**: Architect (validation 계약 설계) + Integrator (engineer·qa 체인 + 3-가드 회귀 진단)
- **산출물 (CTO 직접)**: `docs/architecture/validation-contract.md` — 단일진실(catalog 런타임 읽기), backward-compat entity_type 해소(catalog∈→enforce, ∉→schema-less 통과 = 기존 23-test 무파손 핵심), 체크표(required/type/enum/length→VALIDATION_ERROR 422, unique→CONFLICT 409), 서버컬럼 제외, PATCH 부분검증, FK 후속, DIM-5 게이트.
- **결정**: VALIDATION_ERROR vs CONFLICT 분리 (codes.yaml 준수 — unique 는 409) / 서버생성 컬럼 검증 제외 / lenient entity_type (additive, not breaking) / FK 참조검증은 Growth-12 제외 (in-memory cross-type 조회 별도 설계).
- **Cross-agent catch (2단)**: (1) **DIM-5 31/31 양 adapter PASS, adapter-agnostic HELD** — 한 catalog 가 Java·Python 검증을 동일 구동. (2) PASS 직후 **가드 3개 회귀를 CTO 가 진단·격리**: G-1 = fastapi 가 422/409 를 코드명 옆에 하드코딩 (springboot 는 loader 경유라 clean) → 진짜 패리티 위반, loader 경유 수정 라우팅. G-6+G-8 = gradle `build/` 생성물 스캔 오탐 (catalog build-copy 주석의 'tenant_id', 컴파일 `.class` 의 `$`) → G-1 과 동일 제외셋으로 스코프 정정. **둘 다 약화 아님**: G-1 은 실버그 수정, G-6/G-8 은 소스 아닌 생성물 제외 (소스 검출 능력 유지). feedback_guards_must_work 의 정밀 적용 — "진짜 issue(G-1) 는 고치고, 오탐(G-6/8) 은 스코프로 정정".
- **Integrator 판단**: 가드 body 의 build-제외는 CTO 가 정의(intent)·engineer 가 구현(body) — 페르소나 경계 유지. QA 통과기준(DIM-5)은 행동 보존(같은 422/409 값) 확인으로 재가동 불요.
- **Escalations**: 없음.
- **Open loops resolved**: catalog→adapter 검증 link (Growth-10/11 의 명시적 후속). 남은: FK 참조 무결성, react adapter.

### Growth-13 (2026-06-01) — self-improve 인덱스 (ledger-index): think-grid 평가 + 아이디어 흡수·인프라 비채택

- **역할**: Architect (think-grid 평가 + ledger-index 설계 계약) + Integrator (engineer 판단 승인 + 환류).
- **계기**: CEO 제기 — "지식이 learn-log 에 누적될수록 context 무거워지고 cross-agent 교차정보 관리 곤란. think-grid README 검토하고 개선안 세우자."
- **평가 (think-grid `D:\AI\workspace\think-grid`)**: 핵심 가치 = 심볼에 앵커된 학습 + 백링크 검색. 단 (1) **이미 80% 보유** — `docs/learn-logs/` 6 인격 원장 + auto-memory `[[]]` + codegraph. (2) **미스핏**: sync-graph.js 는 codegraph→.md mirror = 방금 token-savior→codegraph 로 없앤 "코드그래프 2개" 재발 / Obsidian Graph View 는 인간 전용(에이전트 context 절감 아님) / codegraph 는 .md 미인덱스 / 신규 node+sqlite3 = charter §5 비용·고객 self-host 무게. (3) `.context/` 는 dormant skeleton (0-byte agent 파일, README 예시 이름, untracked).
- **결정**: think-grid 의 *아이디어*만 흡수, *인프라* 전부 비채택. 신규 자산 1개 = `scripts/ledger-index.py` (역인덱스, codegraph DB 는 검증 소스로만 read). 빠진 20% = "심볼-앵커 교차-인격 역인덱스" 만 채움. `_index.json` gitignore (재생성 캐시 — 초안 §4 commit 제안을 CTO 가 번복: generated_from_commit=HEAD 가 커밋마다 stale).
- **산출물 (CTO 직접)**: `docs/architecture/ledger-index.md` — 설계 계약 (입력·앵커추출·codegraph 교차검증·출력 스키마·CLI·제약·think-grid 비채택 결정표).
- **Integrator 판단**: engineer 가 `--symbol` 을 file-anchor basename 까지 확장 (CatalogValidator 가 Files-touched 경로에만 존재) → **승인** (검색 의도 부합, guards-must-work). codegraph unverified 61 도 drop 없이 보존, stale 탐지(`--check`)는 **G-11 가드 후보**로 남김 — 지금 게이트 아님 (가드는 진짜 issue 0 일 때만 박음, feedback_guards_must_work).
- **Escalations**: 없음 (CEO Option A 위임 선택).
- **Open loops resolved**: self-improve context-weight (CEO 제기). 남은: `--check`→G-11 승격 여부, `/contribute-back` 인덱스 재빌드 hook, (선택) Obsidian `--md` 시각화.

### Growth-14 (2026-06-01) — expert-agent end-to-end demo: creater 축 첫 채움 + 화면 초안 실증

- **역할**: Architect (7축 결합 설계 + 옵션 4-각도 공격검증) + Integrator (phase 게이트 + 페르소나 위임) + axis-7 큐레이션 실행자 (live agent 호출).
- **계기**: HANDOFF 후보 #1 — 6축(skill/ddl/middle/frontend/backend/customer)은 자산화됐으나 **creater(orchestrator) 축이 비어** end-to-end 증명 불가. M2 "당일 화면 초안" 인수조건의 핵심 (CMO 경고: 이 자동화 없이는 M2 못 지킴).
- **조사 발견 2건 (설계 전)**: (1) `profiles/acme-erp.yaml` 이 catalog 비호환 — domains `customer`/`order`, entities `customer/contact/address/order/...` 가 catalog 14 도메인(hr/finance/.../sales/crm)에 거의 부재. 근본원인 = `domain-expert-generic.md` 의 14-baseline 표가 **catalog 와 다른 추상 목록**이라 agent 가 phantom entity 로 큐레이션. (2) frontend create 폼이 generic key/value (catalog 56 entity 풍부한 컬럼 정의 미사용) — README "Known Gaps: DDL-axis integration" 미해소. 이 둘이 정확히 M2 를 막던 것.
- **옵션 공격검증**: A(wiring-only, generic 폼) — 노력 낮으나 비전문가에 가치 미증명(CMO 거부). B(field-aware, catalog→manifest→typed 폼) ★ — 차별화 그 자체. C(LLM 인터뷰를 결정적 경로에) — 비결정적, 가드/테스트 불가. **전제 붕괴 공격**: "catalog 컬럼만으로 의미있는 폼이 되나" → FK/시스템 컬럼 그대로 노출 시 깨짐 → **변형**: 컬럼 분류(id/created/updated 숨김, enum→select, fk→id-text+갭명시, scalar→타입) 추가로 성립. → B 채택.
- **핵심 결정**: (1) manifest = catalog 파생 **derived artifact** (`out/<slug>/`, gitignore) — **wire contract 불변** (프로토콜은 entity-agnostic 유지가 옳음; 고객 entity 를 stable 층에 넣으면 결합). frontend 는 manifest 를 **읽기만** (단일-진실 G-1 계열). (2) demo profile 은 catalog-grounded 신규(`shop-demo`), 깨진 acme-erp 는 미수정·CEO 결정 보류. (3) agent baseline 표를 catalog 14 에 1:1 동기화 + "catalog 에서 큐레이션" 원칙 — phantom 근본원인 제거. (4) G-11(creater single-source) 은 구현이 이미 깨끗할 때 박음(guards-must-work).
- **3-phase + 게이트**: P1(orchestrator+manifest, QA PASS — 25 test, 결정성 byte-identical, validation fails-closed rc=1) → P2(frontend typed 폼, 69 test green, fallback 보존) → P3(agent catalog-aware + G-11 + live demo).
- **Integrator/live 실행**: 신규 needs("중소제조 인사+설비")로 domain-expert-generic 직접 호출 → agent 가 hr/approval/asset 11 entity 큐레이션(`smallmfg-demo.yaml`) → `scaffold.py` rc=0 + manifest/DDL 산출 = **7축 end-to-end 실증**. agent 가 `attendance`(catalog 미구현)를 스스로 잡아 escalation 보류 — catalog-aware 작동 확인.
- **G-11 vs Growth-13 후보 충돌 해소**: Growth-13 이 `--check`→G-11 후보로 적어뒀으나 미구현이었음. creater single-source 가 먼저 구현돼 **G-11 확정**, ledger-index `--check` 승격은 **G-12 후보 재배치** (번호는 구현 시점 확정 — 예약 아님).
- **Escalations (CEO 향)**: acme-erp 비호환 — 삭제 vs catalog 실키로 수정. demo 는 shop-demo/smallmfg-demo 로 대체했으므로 비차단이나 첫 sample profile 이 깨진 상태로 남는 건 정직하지 않음 → CEO 결정 요청.
- **Open loops resolved**: creater 축 공백(7축 중 마지막 빈 축) / DDL-axis frontend 통합(README known gap) / agent-catalog baseline 불일치. 남은: acme-erp CEO 결정 / FK 참조무결성(G-12 후보, `customer_id` 실증) / react adapter / `--serve`.

### Growth-15 (2026-06-01) — FK 참조 무결성: catalog hygiene + G-12 + runtime 양 backend

- **역할**: Architect (3-part 설계 + dangling/polymorphic 분류 기준) + Integrator (phase 게이트 + agent 중단 재개 + QA caveat 수용).
- **계기**: Growth-14 가 `sales-order.customer_id` 가 catalog fk 블록 없어 text 분류됨을 실증 → handoff 후보 #2. CEO 가 "#2→#1 순서" 지시.
- **조사**: catalog 74 fk 선언 + `*_id`-no-fk 10개. 핵심 발견 — 단순 "모든 _id 에 fk" 가드는 **polymorphic 컬럼(reference_id+reference_type, subject_id+subject_type, principal_id, counterparty_id, current_version_id 순환회피)에서 false-positive**. 그래서 비자명.
- **3-part 설계**: A(catalog hygiene 주석 — fk-exempt 마커로 의도 표시 + customer_id→contact fk) → B(G-12 마커 기반 가드) → C(runtime FK 검증, 양 backend, DIM-6 — §5 deferred 해소).
- **핵심 결정**: (1) dangling 10개 분류 — polymorphic/circular 7 = `fk-exempt:` 마커, genuine-fixable 1(customer_id→contact, contact 실재·의미 정합), genuine-missing-entity 2(machine_id/period_id = entity 미존재 → `fk-exempt: external ref backlog`, **catalog 성장은 domain-expert 영역이라 비포함**). (2) G-12 = 마커 기반(fk OR fk-exempt) → polymorphic 안전. (3) runtime FK = `fk:` 선언 컬럼만 enforce(exempt skip 자동), nullable/absent skip, VALIDATION_ERROR 재사용(신규 error code 0, codes.yaml http_status). (4) G-12 확정 → ledger-index `--check` 는 G-13 후보로 (번호는 구현 시점).
- **공격검증**: 전제붕괴(polymorphic 오분류) → fk-exempt 마커 화이트리스트로 방어. 롤백 — A 주석+1fk, C additive(DIM-1~5 무회귀), 전부 revert 가능.
- **Integrator/재개**: Part C agent 가 16 tool-use 후 조사 중 silent 중단(커밋 0) → SendMessage 로 동일 컨텍스트 재개 → 완료. customer_id fk 추가가 manifest fk-text + DDL FK + 검증 ripple 로 파이프라인 일관성 증명.
- **Escalations / caveat 수용 (QA)**: **Java live DIM-6 미실행** (이 환경 JDK/Gradle 부재). QA 가 양 validator 5조건 로직 패리티를 적대적 read 로 동일 확인 → **PASS-WITH-CAVEAT** 수용. Java live 37 green 확인은 M1 sign-off 전 필수 게이트로 carry (qa.md regression checkpoint).
- **Cross-agent catch**: Engineer 가 CTO 목록 밖 `report-output.triggered_by_id` 발견·분류 + `inspection-plan`(내 오기 inspection-result) 교정 → integrator 승인. QA 가 DIM-5 fake department_id 회귀를 정당 수정으로 판정.
- **Open loops resolved**: FK 참조 무결성(Growth-12 §5 deferred), catalog dangling hygiene(Growth-14 발견). 남은: Java DIM-6 live / machine·accounting-period entity(domain-expert) / G-13 후보.

### Growth-16 (2026-06-02) — 2nd frontend adapter (react): frontend pluggability 실증

- **역할**: Architect (stack 결정) + Integrator (background 빌드 위임 + QA caveat 즉시 클로즈) + 게이트.
- **계기**: handoff 후보 #1 (CEO "2→1" 지시). backend 측 pluggability 는 2 adapter 로 증명됐으나 frontend 는 vanilla-htmx 1개 — "contract 만 stable, F 교체" 의 frontend 측 미실증.
- **stack 결정 (VP 위임, 재확인 없이 확정)**: Vite+React18+TS. **contract 소비 = 빌드타임 codegen** (wire-v1.yaml+codes.yaml → generated TS module, SPA 는 generated 만 import) — 브라우저가 YAML 못 읽는 문제 해결 + 재구현 아닌 소비(G-1). **토큰 = CSS custom property** (frontend-adapter-contract §7 이 남긴 "CSS custom property vs CSS-in-JS" fork 를 전자로 해소 — 공유 design/tokens 파이프라인 일관, vanilla-htmx 와 동일 --* 소비). Vite dev proxy → BACKEND_BASE_URL (self-host 은 reverse-proxy). manifest typed-form 런타임 fetch + generic fallback (Growth-14 패리티).
- **환경 사전 점검**: Java(Growth-15)가 JDK 부재로 live 미실행됐던 교훈 → react 위임 전 `node --version` 확인(v24 가용) → L1+L3+L4(fastapi) 전부 검증 가능 판정 후 진행. caveat 0 으로 완결(Java 와 대비).
- **위임 방식**: 큰 빌드라 background engineer 1-shot + "중간 커밋 체크포인트" 지시(Part C silent-stop 교훈). 결과 20 커밋 per-file, L1 27→30 / L3 build / L4 35(fastapi) green.
- **QA caveat 즉시 클로즈**: QA 가 F-2 offset-last-page 테스트 hollow(순수 산술) 적발(PASS-WITH-CAVEAT). CEO 퇴근 후 자율 마무리 중이었으나 "known-hollow 테스트를 새 adapter 에 남기지 않는다" 원칙으로 즉시 engineer 위임 → `hasMorePages` 순수 헬퍼 추출(ListScreen+test 공유=single-source) 30 test green. push 전 클로즈.
- **Integrator 판단**: G-1 스코프 — SPA router path(`/login`, `/entities/:type`)는 frontend 내비게이션, wire endpoint 아님 → G-1 대상 외(QA 와 합치). frontend INDEX.md 는 G-5 가 frontend 축 2 adapter 도달로 요구 → 추가.
- **Escalations**: 없음. react L4 는 fastapi 상대만 — springboot 상대 react L4 는 Growth-15 의 Java 환경 게이트와 동일 묶음(별도 신규 부채 아님).
- **Open loops resolved**: frontend 측 pluggability(vanilla-htmx 단일) → 4-corner(2×2) 완성. frontend-adapter-contract §7 토큰 fork. 남은: vue/nexacro(M2 후), react persona 분기, maturity threshold.

### Growth-17 (2026-06-02) — GTM 피벗 integrator: demo-video sign-off + ops-pack vaporware 적발

- **역할**: Integrator — CMO demo-video 산출물 honest-marketing 감사 + 3-doc 동기화. 코드 0.
- **계기**: M1 기술 성숙(6/6) 후 CEO GTM 피벗 확정 → demo 영상이 M2 게이트의 GTM 절반. `/clear` 로 중단됐던 CMO 위임 재개.
- **Scene 4 sign-off (positive)**: 2026-06-02 Java 게이트 closure(react↔springboot L4 36 PASS)로 **4-corner 전부 live-verified** 확인 → CMO 가 보수적으로 단 "react 로드맵 헤지" 제거, 실제 react/springboot 스왑 촬영 승인. honest-marketing 은 과소진술도 교정(검증된 능력은 당당히).
- **Scene 5 적발 (negative, G 정신)**: ops-pack(docker-compose+Vault+Keycloak SSO)이 **repo 전무**(compose/vault/keycloak 파일 0, hero profile `vault_agent:false`/`sso_keycloak:false`)인데 positioning.md 가 이를 **IT-담당자 M1 인수 기준**으로 명시 → vaporware 하드 제약 위반 + M1 maturity 주장과 페르소나 인수 불일치. default 로 못 정하는 CEO 사안 → AskUserQuestion 으로 판정 요청.
- **결정 통합 (CEO 2026-06-02)**: ① ops-pack M2 이관 (T-1~T-6 에 불포함 → M1 maturity 유지). ② Scene 5 cut(~3:00). → demo-video-scenario.md(OQ6 resolved, run-time/VO/checklist 동기화) + positioning.md(§positioning statement "실측 구현" false 정정 + §5 인수 triple M1/M2 재배치) + revenue-roadmap.md(M1/M2 인수 동기화) 3-doc per-file 커밋.
- **Integrator 판단**: positioning §5 의 6 인수 triple ↔ revenue-roadmap gating 1:1 매핑 유지하며 ops-pack 만 M1→M2 평행이동. M1 인수는 live-verified 기준(4-corner 풀테스트+로컬 scaffold)으로 재정의 — "검증 가능한 것만 인수 기준" 원칙.
- **Open loops**: demo 실촬영 CEO 결정 대기(CTA/voice/publish/샘플) / ops-pack 구축(M2 deliverable) / lead 5건

### Growth-18 (2026-06-11) — PM 인격 신설 integrator + LLM Wiki 방법론 리서치

- **역할**: 설계 + 리서치. CEO 직접 제안 ("도메인 자율 성장과 별개로, 고객 질의로 needs 를 발굴·인도하는 절차 필요") 을 7번째 인격으로 구조화. 코드 0.
- **설계 결정**: ① 역할 정의 (`pm-agent.md`) 와 실행 절차 (`pm-delivery-loop` skill) 분리 — *누가/무엇을* vs *어떻게/어떤 순서로*. ② loop 8단계, **step 7 contribute-back 이 종료 게이트** (CLAUDE.md §7 체크리스트와 1:1 — 지식 환류 없는 인도 금지). ③ PM↔domain-expert 경계: PM 은 needs·우선순위·인수, expert 는 catalog 매핑·도메인 언어. ④ acceptance criteria 는 QA 검증 가능성 감수 필수 + honest-promise (Growth-17 Scene 5 교훈을 고객 약속 규칙으로 승격). charter v1.4 (매트릭스 PM 열 + delivery sign-off 합의 행).
- **LLM Wiki 리서치 (CEO 질문 2건 — 지식 축적 방법론 + context 비대화)**: GitHub live 조사 (WeKnora 16k★, deepwiki-open 17k★, nashsu/llm_wiki 11k★, mem0 58k★ 등 18 repo) + Karpathy llm-wiki gist 원전 정독. 판정: **도구 비채택, 방법론 채택** — 서버형·embedding형은 Growth-13 "아이디어 채택, 인프라 비채택" 원칙과 충돌. 우리는 이미 절반 보유 (seed.md=Karpathy 형식, learn-log=log.md, ledger-index=검색 CLI). 갭은 `knowledge/wiki/` + `index.md` + read-side progressive-disclosure 규약. 채택안: `docs/architecture/llm-wiki-adoption.md` — **CEO 결정 대기**.
- **모델 전환 기록**: CEO 가 세션 중 /model fable 전환 → 커밋 trailer Claude Fable 5 로 (Growth-8 의 "trailer 는 실제 co-author 모델 반영" 전례, CLAUDE.md §9 갱신).
- **Open loops**: LLM Wiki 채택 CEO 판정 → 승인 시 Phase 1~3 (knowledge/wiki 골격 → ledger-index 확장 → PM loop wiring) / PM 첫 실전 loop.

### Growth-19 (2026-06-11) — LLM Wiki 채택 실행 (knowledge/wiki 골격 + qmd + graph 위임)

- **역할**: 채택 결정 실행 — Growth-18 채택안을 CEO 가 "진행하자" 로 승인 (인프라 차용 포함 §6 추천 직후).
- **Phase 1 (직접)**: `knowledge/wiki/` 골격 — README.md (페이지 규약·신뢰도 라벨 4종·3-op·anti-pattern) + index.md (카탈로그 진입점) + sources/entities/concepts/syntheses + `knowledge/raw/`. **log.md 신설 안 함** — learn-log 가 단일 진실 (중복 금지).
- **Phase 2 (직접)**: qmd 2.5.3 npm 전역 설치 + collection 3개 (wiki/docs/presets, 파일 2/24/42) + BM25 smoke PASS (질의 "delivery loop acceptance criteria" → pm.md 89%). **Windows 함정 1건**: PATH 앞순위 `.bun\bin\qmd.exe` 고아 shim (bun 전역 목록에 qmd 없음, "/bin/sh not found" 오류) → 고아 2파일 제거로 해소, npm shim (Roaming\npm) 정상. `qmd embed` (시맨틱) 는 GGUF 모델 다운로드라 선택 후속 — BM25 만으로 현 규모 충분.
- **Phase 3 (위임)**: engineer 에 build_graph.py 스펙 위임 — CDN 0 self-contained HTML (사내망 G-6 정신), stdlib only, dangling wikilink 는 에러 아닌 회색 노드 (작성 예정 신호), out/ derived gitignore. PM loop step 7 에 wiki ingest 명문화 + CLAUDE.md §11 read-side 규약 1줄 (index→drill-down, 통읽기 금지).
- **Open loops**: qmd embed 선택 실행 / qmd MCP·plugin 연결 여부 / 첫 실전 ingest (M2 첫 고객 loop #1).

### Growth-20 (2026-06-11) — §6 슬림 회전 정책 수립 + 첫 아카이빙 실행

- **계기**: Growth-19 마무리 시 G-9 가 198/200 — 다음 엔트리가 cap 초과 확정. CEO "G-9 아카이빙도 처리해줘".
- **경계 결정**: Growth-4~12 (13 슬림 엔트리, 2026-05-29~06-01) 이동 / Growth-13~19 유지 — 13 이후가 현재 활성 문맥 (ledger-index·creater 채움·4-corner·GTM·PM·wiki, open loop 상호참조 다수). founding 1~3 은 divider 앞 full 포맷이라 G-9 비카운트 + 헌장 맥락이므로 main 잔류.
- **메커니즘**: PowerShell 라인 분할 (181~336 → archive body), **내용 수정 0** — 아카이브 무결성 원칙 (이동 ≠ 재작성). §6 에 포인터 1줄 + 회전 정책 명문 (cap 접근 시 동일 절차). 결과 198→70 non-blank, 가드 12 PASS.
- **파생 갭 적발**: ledger-index 가 고정 목록이라 pm.md (Growth-18 이후) 와 growth-archive.md 가 **silent 누락** — guards-must-work 정신으로 즉시 engineer 위임 (glob 전환, 향후 인격 추가 시 자동 포함).
- **Open loops**: 없음.

### Growth-21 (2026-06-11) — 전 인격 loop skill 화 + knowledge-sync hook 설계

- **계기**: CEO 지시 2건 — ① 지식 축적·수정 시 연관 skill 반영 hook ② 각 agent 의 role·실행 절차 skill 화 + 지식 저장소 활용.
- **skill 설계 (직접)**: 5 loop (`engineer-loop`/`qa-loop`/`marketing-loop`/`design-loop`/`domain-expert-loop`) — PM 패턴 동형: role 정의서 = 누가/무엇을, skill = 어떻게/순서. 각 loop 에 **지식 저장소 프로토콜 2-step** (시작: `qmd search`+`ledger-index --symbol` 선행 검색 / 종료: wiki 환류 + index.md 1줄 + 신뢰도 라벨). 규약 단일 진실은 `knowledge/wiki/README.md` — skill 은 role-특화 포인트만 (DRY, 5중 복제 회피). 각 agent 정의서 blockquote 에 skill 포인터 1줄 연결.
- **hook 설계 (위임)**: hook 은 LLM 이 아니므로 "skill 자동 수정" 은 불가/위험 — 대신 PostToolUse(Write|Edit) 에서 지식 경로 (knowledge/·presets/·profiles/) 변경 감지 → **additionalContext 로 연관 skill 점검 지시 주입** (경로→skill 매핑 테이블). 작업을 깨지 않게 예외 시 exit 0.
- **loop 내 교훈 인용**: 각 anti-pattern 절은 실제 Growth 교훈으로 anchoring (G-1 재구현 금지, Growth-14 phantom 키, Growth-16 hollow 테스트, Growth-17 vaporware) — 추상 규칙보다 사례 기반.
- **Open loops**: hook 첫 실가동 검증 / CTO integrator skill 화 보류 (main session 은 CLAUDE.md 가 이미 절차 문서).

### Growth-22 (2026-06-11) — 지식 연계 integrator 점검 (CEO 지시)

- **점검 관점**: "agent 가 저장소를 활용하고, 저장소 발전이 skill 과 유기 연계되는가" — 절차 (skill) ↔ 권한 (tools) ↔ 신선도 (인덱스) ↔ 문서 (커버리지) 4축 대조.
- **갭 1 (치명)**: pm/marketing/design/domain-expert 의 tools 에 Bash 부재 — loop skill 의 시작-검색 step (`qmd search`, `ledger-index --symbol`) 이 **실행 불가능한 절차**였음. engineer/qa 만 실행 가능. → 4 정의서 tools 에 Bash 추가. 교훈: 절차를 skill 화할 때 실행 주체의 tool 권한과 대조하는 것이 점검 항목 (이번에 누락했던 것).
- **갭 2**: qmd 는 collection add 시점 인덱스 — 지식 추가 후 `qmd update` 없으면 시작-검색이 stale 인덱스에서 "사례 없음" 거짓 판정. → hook 체크리스트 ⑤ 추가 (engineer, 6792efd). `qmd update` 동작·다중 `-c` 문법 실검증 (skill 예시 유효 확인).
- **갭 3**: main `learn-log.md` 는 repo 루트라 qmd collection (wiki/docs/presets) 밖 — 검색 도구별 커버리지가 비문서. → wiki README 에 커버리지 지도 표 (main 원장 = ledger-index 담당 명시).
- **hook 첫 실가동 (Growth-21 open loop 해소)**: 본 점검 중 README Edit 에 PostToolUse hook 이 실제 발화, ⑤ 포함 컨텍스트 주입 확인 — 체크리스트를 그대로 따라 qmd update 실행까지 완료 (자기 검증 원칙).
- **Open loops**: 없음.

## §3 — Open Loops (이 인격 책임)

- ~~codegraph 2-step gate measurement (Growth-5f)~~ ✅ Growth-9 종결 — 조건부 ADOPT (코드 네비게이션 한정, 거버넌스 DESCOPE), `docs/architecture/codegraph-adoption.md`
- **Cross-agent Growth 의 main 행 포맷 (Growth-5c 박음)**: `### Growth-N (...) — <제목>` 본문 `**인격**: <주도> (+ <보조>)`. 본 Growth-5c/5d/5e 가 첫 적용 — Open loop 해소.
- **engineer-agent / qa-agent 첫 가동**: Engineer Growth-5d 에서 첫 가동 완료. QA 첫 가동은 M1 adapter compliance test 작성 시점.
- **첫 분기 synthesis**: 2026-Q3 마지막 주 (Growth-1~ 누적 통합) — 템플릿 실전 검증
- **public 전환 게이트**: M2 첫 고객 협의 종료 후 (Growth-5e Q3 답변과 동일 게이트) — 그 즉시 charter §3 #3 사전 확인 룰 의식
- ~~**System maturity threshold 측정 정의**~~ ✅ **해소 (2026-06-02)**: `revenue-roadmap.md#M1-Maturity-Threshold` 에 정량 박음 — Technical Maturity T-1~T-6(현재 6/6 MET) + GTM(demo·lead, CEO/CMO). T-7(비용측정)은 런타임 LLM 호출 생기는 M2/M3 로 이관(M1 무 LLM 런타임). 자동화 `maturity-check.py` 는 CEO 승인 시 후속.
- **OpenAPI 3.1 migration (M1 후반)**: 첫 adapter 작업 완료 후 schema 갭 학습 → migration
- **schema v2 (`secrets:` top-level)**: customer profile 5+ block 도달 시 재검토
