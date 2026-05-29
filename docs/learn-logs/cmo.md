# learn-log — CMO

> Market-facing voice. 메시지·런칭·콘텐츠 인격의 ledger.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 인격 헌장: [`.claude/agents/marketing-agent.md`](../../.claude/agents/marketing-agent.md).

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Deliverable: <positioning.md / pitch / blog outline / content calendar 등>
- Persona served: <CEO / 업무담당자 / IT-담당자 중>
- Tech claims (need CTO check): <검증 필요한 기술 수치>
- Open questions to CEO: <회수 대기 결정>
- Cost: <turns / 추정 $>
```

## §2 — Growth History

### Growth-3 (2026-05-29) — CMO 첫 배치 (positioning.md)

- **Deliverable**: [`docs/marketing/positioning.md`](../marketing/positioning.md) — 1줄 약속 + 3 페르소나 카드 + 3대 차별화 페르소나별 번역 + M0~M5 페르소나-시간 triple
- **Persona served**: 3개 모두 (CEO / 업무담당자 / IT-담당자)
- **Tech claims (need CTO check)**:
  - M1 IT-담당자 2시간 배포 — ops pack (docker-compose + Vault + SSO) 실측 필요
  - M2 업무담당자 당일 화면 초안 — M1 의 generic preset + middle contract 파이프라인 의존, M1 deliverable 우선순위에 반영 요청
  - M5 CEO 1시간 trial → 도메인 선택 화면 — multi-tenant isolation 검증 후 측정
- **Open questions to CEO** (회수 대기):
  1. self-host license 가격대 확정 (현재 \$10K~\$30K 가이드)
  2. 첫 vertical 시그널 캡처 방식 (M2 첫 고객 산업 기록 자동화)
  3. OSS / 상용 분리선 합의 시점 (현재: middle contract + adapter compliance test 가 OSS 예정)
  4. M3 vertical landing page 책임자 (CMO 단독 vs CDO 협업)
- **Cost**: 1 subagent invocation (Sonnet 4.6), 약 \$0.3 추정

### Growth-5e (2026-05-29) — CEO 회수 질문 4건 답변 통합 (Growth-3 open loop 해소)

- Persona served: 모든 페르소나 (메시지·게이트 정렬)
- Delivered: positioning.md 에 CEO 4 답변 박힘 — Q1 가격대 deferral (maturity threshold), Q2 첫 vertical = 첫 paid customer 산업, Q3 OSS 분리선 = M2 후, Q4 M3 landing = CMO+CDO
- Cross-agent dependency: Q1 의 "maturity threshold" 는 측정 정의 필요 (CTO 가 M1 마무리 Growth 에 박을 후보), Q4 는 CDO 협업 (charter §2 매핑 활용)
- Cost: ~3 turns, 본 통합 작업만 (질문 응답은 CEO 가 직접)
- Open loops: M2 가격 공개 게이트 (CEO 가 maturity 평가), M3 landing 작업 시 CDO sync

## §3 — Open Loops (이 인격 책임)

- [x] Growth-3 open Q1 (가격대) — 해소됨 (Growth-5e): CEO 결정, maturity threshold 게이트로 공개 보류
- [x] Growth-3 open Q2 (첫 vertical 시그널) — 해소됨 (Growth-5e): 첫 paid customer 산업 = 첫 vertical, 사전 선택 없음
- [x] Growth-3 open Q3 (OSS/상용 분리선) — 해소됨 (Growth-5e): M2 첫 고객 협의 종료 후 결정
- [x] Growth-3 open Q4 (M3 landing 책임자) — 해소됨 (Growth-5e): CMO copy + CDO visual 협업 (charter §2 매핑)
- M1 이전 한 줄 포지셔닝 최종 확정 (CEO 승인 게이트)
- 첫 블로그 글 5개 outline (M1 이후)
- 경쟁사 분석 1장 (predibase / vercel / retool / supabase / internal tool builders 중)
- M2 가격 공개 게이트 (CEO 가 maturity threshold 평가)
- M3 landing 작업 시 CDO sync
