# PM Ledger — 인격별 상세 기록

> 7번째 인격 (Growth-18 신설). main `learn-log.md §6` 은 1줄 rollup, 이 파일이 PM 이 닿은 Growth 의 상세. 역할 정의: `.claude/agents/pm-agent.md`, 절차: `.claude/skills/pm-delivery-loop/SKILL.md`.

## §1 — Growth 상세

### Growth-23 (2026-06-11) — 인터뷰 질문 시트 초안 + profile 역분석

- **역분석 발견**: shop-demo (이커머스 2도메인 crm+sales) 와 smallmfg-demo (제조 4도메인 hr+hr-leave+approval+asset) 비교 → needs 는 도메인 선택 수 (2~4개) 로 표현된다. smallmfg escalation notes 가 "지금 안 푸는 needs" 를 명시한 점 — 인터뷰에서 미래 needs 포착 질문을 설계하는 근거.
- **기준선 확정**: stack 선택 (fastapi/vanilla-htmx/postgres) 은 IT-담당자 인터뷰 결과, auth.method 와 locale 은 조직 규모·복잡도 proxy, billing.llm_budget 은 CEO 예산 인터뷰 결과가 채운다.
- **산출물**: `docs/business/interview-sheet.md` — 3 페르소나 × 6 질문 = 총 18 주질문, 각 질문에 "이 답이 채우는 칸" 명시. 답변→profile 변환 절차 1단락 포함.
- **open loops 해소**: 인터뷰 질문 시트 초안 완료, 기존 profile 2건 역분석 완료.

### Growth-18 (2026-06-11) — PM 인격 신설 (founding)

- **계기**: CEO 직접 제안 — "지금까지는 특정 도메인을 자율적으로 발전시켰다 (공급 측). 고객 질의로 needs 를 발굴하고 구현·인도하는 절차 (수요 측) 가 별도로 필요하다."
- **신설 내용**: 역할 정의서 (`pm-agent.md`) + 실행 절차 skill (`pm-delivery-loop`) + charter v1.4 (권한 매트릭스 PM 열) + 이 ledger.
- **설계 결정 (CTO)**: ① domain-expert 와의 경계 — PM 은 *무엇이 필요한가* (needs·우선순위·인수), expert 는 *그것이 도메인적으로 무엇인가* (catalog 매핑·도메인 언어). ② loop 종료 게이트 = contribute-back (CLAUDE.md §7 과 1:1). ③ acceptance criteria 는 QA 감수 필수 — "측정 가능성 우선" 원칙을 고객 인수에도 적용. ④ honest-promise — Growth-17 Scene 5 vaporware 교훈을 고객 약속 규칙으로 승격.
- **첫 실전**: M2 첫 고객 후보 발생 시 loop #1 회전. 그 전 준비물: 3-페르소나 인터뷰 질문 시트 초안 (Initial Task 5).

## §2 — Loop 회전 기록

| # | 고객 | 시작 | 단계 | 상태 |
|---|---|---|---|---|
| 1 | 30인 법무법인 (lawfirm-demo) | 2026-06-11 | Step 5 Deliver | 인도 패키지 조립 완료 (`docs/delivery/lawfirm-demo/`) + CISO 보안 게이트 PASS (CAVEAT 3건 해소, Growth-32). CEO 승인 대기 — 외부 전달 책임은 CEO (charter §2) |

### CEO 인터뷰 답변 기록 (lawfirm-demo, 2026-06-11)

미답이던 2문항이 CEO 답변으로 채워짐 (인터뷰 시트 A5·A6):

- **A6 (예산)**: 초기 구축비 **500만원 (일회성)** — self-host 설치·구축·라이선스. profile `billing.setup_cost_krw: 5000000`. 월 LLM 운영 예산은 초기비와 분리, AI 검색 빈도 측정 후 별도 확정 (`llm_budget_usd_per_month: TBD` 유지).
- **A5 (보안·데이터)**: **소송 데이터 외부 유출 절대 금지, self-host 필수.** "우리가 제공하는 결과물에 보안 결함이 없도록 전달" — 인도물에 대한 명시적 보안 품질 요구. profile `security` 섹션 신설 (data_residency: on-premise, self_host: required). 이 요구가 **CISO 인격 신설 (Growth-32)** 의 직접 계기. CISO 첫 리뷰에서 A5(외부 유출 0) 충족 확인.

## §3 — Open Loops (이 인격 책임)

- ~~**인터뷰 질문 시트 초안** (3 페르소나 × 5~7 질문)~~ → **완료** (Growth-23, `docs/business/interview-sheet.md`)
- ~~**기존 profile 2건 역분석** (shop-demo, smallmfg-demo)~~ → **완료** (Growth-23, §1 기록)
- **FAQ 누적 위치 신설** (`presets/skills/<industry>/faq.md`) — 첫 고객 질문 발생 시
