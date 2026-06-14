---
name: pm-delivery-loop
description: Run the PM delivery loop for a customer engagement — needs discovery interview, requirement specification (profile + acceptance criteria), build coordination, verification gate, delivery packaging, feedback triage, and knowledge contribute-back. Use when starting or advancing any customer-facing delivery work.
---

# PM Delivery Loop

> 실행 주체: `pm-agent` (`.claude/agents/pm-agent.md`). 이 skill 은 절차의 단일 진실 — 역할 정의서는 *누가/무엇을*, 이 문서는 *어떻게/어떤 순서로* 를 담는다.

고객 요청 1건 = loop 1회전. 8단계, 마지막 단계 (contribute-back) 가 **종료 게이트** — 이 단계 없이 loop 를 닫지 않는다.

## Loop Steps

| # | 단계 | 동작 | Exit 기준 |
|---|---|---|---|
| 0 | **Intake** | 요청을 1줄로 정리하고 기존 자산 검색: `python scripts/ledger-index.py --symbol <키워드>`, `profiles/`, `presets/skills/`, `knowledge/generic/verified-profiles/` | 신규 needs / 기존 자산 확장 판정 완료 |
| 1 | **Discover** | 페르소나별 인터뷰 (CEO / 업무담당자 / IT-담당자, 각 5~10 질문). 솔루션이 아니라 문제를 묻는다: 현재 어떻게 우회하는가, 빈도는, 안 풀리면 무슨 비용인가 | needs note 가 "누가 / 무엇을 / 왜" 로 기술됨 |
| 2 | **Specify** | domain-expert 와 협업해 `profiles/<slug>.yaml` 초안 (catalog 존재 키만) + acceptance criteria 작성. criteria 는 측정 가능해야 하며 QA 감수를 받는다 | profile 초안 + criteria 가 CEO (또는 고객 측) 확인됨 |
| 3 | **Build** | `python scripts/workflow/scaffold.py --profile <slug>` 실행. 갭 (catalog 미존재 entity, adapter 기능 부족) 은 CTO 경유 engineer / domain-expert 에 위임 — PM 직접 구현 금지 | scaffold 산출 완료 + 갭은 백로그 등록 |
| 4 | **Verify** | `python scripts/diagnose.py` + 해당 stack 의 4계층 풀테스트 subset + acceptance criteria 대조표 작성. QA 게이트 통과 필수 | 전 criteria PASS 또는 BLOCK 해소 + Needs-Fit PASS |
| **4b** | **Needs-Fit** | CODEX: needs-note vs manifest/AC coverage matrix → PASS/PASS-WITH-CAVEAT/BLOCK | Needs-Fit PASS (`docs/delivery/<slug>/needs-fit-review.md`) |
| 5 | **Deliver** | 인도 패키지 구성 (화면 초안 / 데모 / 사용 문서). CEO 승인 후 전달 — 외부 전달 책임은 CEO (charter §2) | 고객 수령 확인 |
| 6 | **Feedback** | 피드백 수집 → triage: **수용** (→ step 1 재진입) / **backlog** (사유와 함께 기록) / **거절** (사유 회신). 가격·계약 영향 건은 CEO 이관 | 전 피드백 분류 완료, 수용분은 새 회전 계획 수립 |
| 7 | **Contribute-back** ★종료 게이트 | 지식 환류: **wiki ingest** (`knowledge/wiki/` 페이지 갱신 + index.md 1줄, 규약: `knowledge/wiki/README.md`), seed/preset 갱신, FAQ 누적 (`presets/skills/<industry>/faq.md`), verified-profile 사례 (PII 제거), `learn-log.md §6` 1줄 + `docs/learn-logs/pm.md` 상세 | CLAUDE.md §7 체크리스트 5항목 전부 답변됨 |

## 단계별 산출물 위치

- needs note / 인터뷰 기록 / 대조표: `docs/learn-logs/pm.md` 해당 Growth 절 (또는 첨부 경로 명시)
- profile: `profiles/<slug>.yaml` (스키마: `profiles/_README.md`)
- scaffold 산출: `out/` (gitignore — 인도 패키지로만 복사)
- 환류 자산: `presets/`, `knowledge/generic/verified-profiles/`
- **반환 규약**: 위 산출물은 파일에 쓰고 main 으로는 **요약 + 경로 + 결정/BLOCK 항목만** 반환 (envelope §4). 규약: [`subagent-output-protocol.md`](../../../docs/architecture/subagent-output-protocol.md)

## Auto-Pass Rule for Qualifying Intake Leads

intake_sync.py 가 `qualify` 상태 리드를 처리할 때 Steps 2~4 를 자동으로 실행한다 (draft 승급·scaffold·deploy·ui_check·needs-fit). 이 자동 경로의 산출물은 **내부 preview** 로 간주하며 Step 5 (Deliver, CEO 외부 전달 게이트) 대상이 아니다.

- Steps 5·6·7 은 자동화 대상이 아님 — CEO 게이트 (Step 5) 와 PM triage (Step 6·7) 는 항상 사람 판단.
- CEO override: `--force-slug` 플래그 또는 `processed.jsonl` 수동 편집으로 자동 경로를 우회하거나 재실행할 수 있다.
- `qualify` 미충족 리드 (gap_only / defer / prefer_call) 는 자동 경로 진입 불가 → pm-inbox triage.

## Needs-Fit Audit Gate (Step 4b)

Step 4 Verify 와 Step 5 Deliver 사이에 삽입되는 감사 게이트. 상시 페르소나(인격)가 아니라 **on-demand codex 실행 함수** 다.

- **입력**: `needs-note.md` + `acceptance-criteria.md` + `out/<slug>/screen-manifest.json` + `profiles/<slug>.yaml`
- **방법**: needs 항목(누가/무엇을/왜) 추출 → manifest 엔티티·AC·flow 와 coverage matrix → COVERED/PARTIAL/GAP → 집계 PASS(GAP 0) / PASS-WITH-CAVEAT(PARTIAL 만) / BLOCK(GAP 존재)
- **출력**: `docs/delivery/<slug>/needs-fit-review.md` (PII strip 필수) + main 에는 envelope(§4)만
- **호출**: `Agent(subagent_type='codex:codex-rescue', prompt=<template>)`. 템플릿: `.claude/skills/pm-delivery-loop/needs-fit-prompt-template.md`. 래퍼: `scripts/workflow/needs_fit_audit.py` (선택)
- **BLOCK 처리**: GAP=엔티티·adapter 부재 → CTO 백로그 / AC 누락 → PM 이 criteria 보강. Step 5 외부 인도는 charter §2 상 CEO 단독 불변.
- 규약: [`subagent-output-protocol.md`](../../../docs/architecture/subagent-output-protocol.md)

## Anti-patterns (위반 시 QA 경계 감사 대상)

- 인터뷰 없이 profile 작성 (needs 추측 금지 — domain-expert 의 "추측 금지" 원칙과 동일)
- 측정 불가 acceptance criteria ("직관적이다", "빠르다" — 수치/명령 재현 없는 기준 금지)
- live-verified 되지 않은 능력을 인수 기준으로 약속 (Growth-17 vaporware 교훈)
- PM 의 직접 코드 작성 / contract 변경
- step 7 생략 후 loop 종료 ("다음에 정리하자" = 원칙 위반 신호)

## Loop 중단 (Escalation 시)

charter §6 에스컬레이션 사유 발생 시 loop 를 해당 step 에서 **freeze** 하고 CEO 판정 후 재개. freeze 상태와 사유는 `docs/learn-logs/pm.md` 에 기록.
