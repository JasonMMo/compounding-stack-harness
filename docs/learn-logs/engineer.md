# learn-log — Engineer

> Implementation hand. CTO 가 결정한 설계를 코드로 옮기는 인격의 ledger.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 인격 헌장: [`.claude/agents/engineer-agent.md`](../../.claude/agents/engineer-agent.md).

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Files touched: <경로 list>
- Implementation choices: <변수명·구조·error handling 등 인격 단독 결정>
- Tests added: <4계층 중 어느 layer>
- Catches surfaced: <CTO/QA 에 던진 escalation 신호>
- Cost: <turns / 추정 $>
```

## §2 — Growth History

(이 인격은 Growth-4 에서 신설됨. 첫 실전 가동은 M1 진입 시 — `middle/contract/` 첫 wire 키 schema 작성.)

## §3 — Open Loops (이 인격 책임)

- M1 진입 시 첫 spawn — `middle/contract/` 첫 wire 키 schema 파일 작성 (CTO 가 결정한 키 목록 기반)
- `scripts/diagnose.py` G-1/G-2 SPEC → 활성 전환 시 함수 본문 보강
