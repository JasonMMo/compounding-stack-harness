---
name: qa-loop
description: Run the QA audit loop — pass-criteria check, adversarial verification, regression lookup in the knowledge store, PASS/FAIL/PASS-WITH-CAVEAT verdict, ledger record. Use when qa-agent audits any agent output, guard policy, fulltest gate, or merge/release verification.
---

# QA Loop

> 실행 주체: `qa-agent` (`.claude/agents/qa-agent.md`). 판정 권위: 거짓 PASS > 거짓 FAIL 우선순위.

## Loop Steps

| # | 단계 | 동작 | Exit 기준 |
|---|---|---|---|
| 1 | **기준 확인** | 감사 대상의 통과 기준이 *명령으로 재현 가능*한지 먼저 — 측정 불가 기준이면 감사 전에 반려 | 기준이 재현 가능 |
| 2 | **이력 검색** ★지식 저장소 | `python scripts/ledger-index.py --symbol <대상>` + `qmd search "<대상> regression" -c docs` — 같은 위치의 과거 PASS→FAIL, 기존 caveat 확인 | regression 여부 판정 |
| 3 | **적대 검증** | 산출물을 *반박하려고* 시도: 하드코딩 grep, hollow 테스트 (assertion 이 대상을 실제로 통과하는가), 경계값. 주장 수치는 재실행으로 재현 | 반박 시도 소진 |
| 4 | **경계 감사** | 산출물이 작성 인격의 헌장 범위 안인가 (engineer 가 contract 변경? CMO 가 가격?) — 위반 시 CTO 보고 | 경계 위반 0 또는 보고됨 |
| 5 | **판정** | PASS / FAIL / PASS-WITH-CAVEAT. CAVEAT 은 해소 조건을 명령형으로 명시 (예: "JDK 환경에서 37 green 확인 후 클로즈") | 판정 + 근거 명령 기록 |
| 6 | **기록** | `docs/learn-logs/qa.md` 갱신. regression 이면 §regression 절 + learn-log 추적 | ledger 반영 |
| 7 | **환류** ★지식 저장소 | 반복 발견 패턴 (예: hollow 테스트 유형) 은 `knowledge/wiki/concepts/` 페이지 또는 가드 후보로 CTO 제안 | 3회 반복 → 가드 제안 의무 |

## 지식 저장소 프로토콜

- **시작**: step 2 — 과거 판정·caveat 검색 없이 감사 시작 금지 (동일 caveat 재발견 낭비 방지).
- **종료**: step 7 — 판정 자체가 지식: 비자명한 판정 근거는 wiki syntheses 로.

## 출력 규약

감사 근거·재현 명령·반박 시도 상세는 `docs/learn-logs/qa.md` (누적) 또는 인도물 단위면 `docs/delivery/<slug>/qa-report.md` 에 쓰고, main 으로는 **판정 + 경로 + FAIL/CAVEAT 항목만** 반환한다 (envelope §4). 규약: [`subagent-output-protocol.md`](../../../docs/architecture/subagent-output-protocol.md).

## Vision-QA Gate (marketing-site 인도 전 필수)

marketing-site deliverable 의 triage_status 를 delivered 로 전환하기 전에:

1. `python scripts/workflow/ui_check.py --slug <slug> --base-url <url> --full-vision`
   실행 → `docs/intake-inbox/ui-checks/<slug>-vision-request.json` 생성 (LLM 0, 결정론).
2. CDO/QA 가 request 의 각 스크린샷을 zai-mcp `analyze_image` 로 열고
   `design/vision-qa-rubric.yaml` 8 기준을 채점 (1~5 점).
3. 판정 규칙 (`design/vision-qa-rubric.yaml::judgment`):
   **PASS** = 모든 기준 ≥3 AND 평균 ≥3.5 / **BLOCK** = 어느 기준 ≤2 / **WARN** = 그 외.
4. 결과를 `docs/intake-inbox/ui-checks/<slug>-vision-verdict.json`(`{"slug","verdict","scores",...}`)
   에 쓴다. verdict PASS 가 아니면 인도 BLOCK (G-15).

## Anti-patterns

- "직관적으로 안전해 보임" 판정 / 가드 약화 제안 수용 / CAVEAT 의 해소 조건 누락 / 산출 인격에게 판정 위임
