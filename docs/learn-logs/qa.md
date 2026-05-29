# learn-log — QA (CQO)

> Quality gate. 가드 통과 기준·4계층 풀테스트·agent 산출물 감사 인격의 ledger.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 인격 헌장: [`.claude/agents/qa-agent.md`](../../.claude/agents/qa-agent.md).

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Audit target: <감사 대상 — 가드 / 풀테스트 / agent 산출물>
- Pass criteria defined / refined: <통과 기준 결정 사항>
- False PASS / False FAIL risks: <발견·평가한 위험>
- Regression cases: <PASS→FAIL 전환 사례>
- Blocks issued: <머지 차단 카운트>
- Cost: <turns / 추정 $>
```

## §2 — Growth History

(이 인격은 Growth-4 에서 신설됨. 첫 실전 가동은 M1 진입 시 — 4계층 풀테스트 통과 기준 문서화.)

## §3 — Open Loops (이 인격 책임)

- 현행 가드 8개 (G-1~G-8) 의 거짓 PASS / 거짓 FAIL 위험 평가 — 첫 가동 시
- M1 진입 게이트 통과 기준 문서화 — L1~L4 각각의 PASS 정의
- regression 이력 섹션 초기화 (이 파일 §4 로 분리 예정)
