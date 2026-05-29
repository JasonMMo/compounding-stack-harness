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

## §3 — Open Loops (이 인격 책임)

- **Cross-agent Growth 의 main 행 포맷 (Growth-5c 박음)**: `### Growth-N (...) — <제목>` 본문 `**인격**: <주도> (+ <보조>)`. 본 Growth-5c/5d/5e 가 첫 적용 — Open loop 해소.
- **engineer-agent / qa-agent 첫 가동**: Engineer Growth-5d 에서 첫 가동 완료. QA 첫 가동은 M1 adapter compliance test 작성 시점.
- **첫 분기 synthesis**: 2026-Q3 마지막 주 (Growth-1~ 누적 통합) — 템플릿 실전 검증
- **public 전환 게이트**: M2 첫 고객 협의 종료 후 (Growth-5e Q3 답변과 동일 게이트) — 그 즉시 charter §3 #3 사전 확인 룰 의식
- **System maturity threshold 측정 정의**: Growth-5e Q1 답변이 의존 — M1 마무리 Growth 에 "M1 14 preset PASS + acme-erp demo PASS = maturity = pricing 공개 게이트" 식 박을 후보
- **OpenAPI 3.1 migration (M1 후반)**: 첫 adapter 작업 완료 후 schema 갭 학습 → migration
- **schema v2 (`secrets:` top-level)**: customer profile 5+ block 도달 시 재검토
