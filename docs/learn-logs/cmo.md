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

## §3 — Open Loops (이 인격 책임)

- 위 4 질문 회수 (CEO 결정 대기)
- M1 이전 한 줄 포지셔닝 최종 확정 (CEO 승인 게이트)
- 첫 블로그 글 5개 outline (M1 이후)
- 경쟁사 분석 1장 (predibase / vercel / retool / supabase / internal tool builders 중)
