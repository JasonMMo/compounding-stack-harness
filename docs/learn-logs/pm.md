# PM Ledger — 인격별 상세 기록

> 7번째 인격 (Growth-18 신설). main `learn-log.md §6` 은 1줄 rollup, 이 파일이 PM 이 닿은 Growth 의 상세. 역할 정의: `.claude/agents/pm-agent.md`, 절차: `.claude/skills/pm-delivery-loop/SKILL.md`.

## §1 — Growth 상세

### Growth-18 (2026-06-11) — PM 인격 신설 (founding)

- **계기**: CEO 직접 제안 — "지금까지는 특정 도메인을 자율적으로 발전시켰다 (공급 측). 고객 질의로 needs 를 발굴하고 구현·인도하는 절차 (수요 측) 가 별도로 필요하다."
- **신설 내용**: 역할 정의서 (`pm-agent.md`) + 실행 절차 skill (`pm-delivery-loop`) + charter v1.4 (권한 매트릭스 PM 열) + 이 ledger.
- **설계 결정 (CTO)**: ① domain-expert 와의 경계 — PM 은 *무엇이 필요한가* (needs·우선순위·인수), expert 는 *그것이 도메인적으로 무엇인가* (catalog 매핑·도메인 언어). ② loop 종료 게이트 = contribute-back (CLAUDE.md §7 과 1:1). ③ acceptance criteria 는 QA 감수 필수 — "측정 가능성 우선" 원칙을 고객 인수에도 적용. ④ honest-promise — Growth-17 Scene 5 vaporware 교훈을 고객 약속 규칙으로 승격.
- **첫 실전**: M2 첫 고객 후보 발생 시 loop #1 회전. 그 전 준비물: 3-페르소나 인터뷰 질문 시트 초안 (Initial Task 5).

## §2 — Loop 회전 기록

| # | 고객 | 시작 | 단계 | 상태 |
|---|---|---|---|---|
| — | (없음 — M2 첫 고객 대기) | | | |

## §3 — Open Loops (이 인격 책임)

- **인터뷰 질문 시트 초안** (3 페르소나 × 5~7 질문) — M2 첫 접촉 전 준비
- **기존 profile 2건 역분석** (shop-demo, smallmfg-demo) — 인터뷰 기준선
- **FAQ 누적 위치 신설** (`presets/skills/<industry>/faq.md`) — 첫 고객 질문 발생 시
