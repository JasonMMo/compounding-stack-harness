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

## §3 — Open Loops (이 인격 책임)

- **G-9 후보**: main learn-log §6 의 행당 길이 / 행 수 가드 (trade-off 보강 토론 후 결정)
- **Cross-agent Growth 의 main 행 포맷**: 인격이 2개 이상 닿은 Growth 의 main §6 1줄 표기 컨벤션 (예: `Growth-N — CMO+CTO`)
- **engineer-agent / qa-agent 첫 가동**: M1 진입 시 첫 spawn — 실전 협업 패턴 검증
