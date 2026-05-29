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

## §3 — Open Loops (이 인격 책임)

- **Cross-agent Growth 의 main 행 포맷**: 인격이 2개 이상 닿은 Growth 의 main §6 1줄 표기 컨벤션 (예: `Growth-N — CMO+CTO`) — 첫 cross-agent Growth 도착 시 결정
- **engineer-agent / qa-agent 첫 가동**: M1 진입 시 첫 spawn — 실전 협업 패턴 검증
- **첫 분기 synthesis**: 2026-Q3 마지막 주 (Growth-1~ 누적 통합) — 템플릿 실전 검증
- **public 전환 게이트**: CMO 회수 #3 (OSS/상용 분리선) 결정 후 visibility 전환 + 그 즉시 charter §3 #3 사전 확인 룰 의식 (push 룰 변경 X)
