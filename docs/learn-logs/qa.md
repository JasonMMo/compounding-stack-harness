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

### Growth-5a (2026-05-29) — G-9 통과 기준 위임 검토 (QA agent 미가동, CTO 임시 권한)

- **Audit target**: G-9 가드 (main learn-log §6 슬림 cap)
- **Pass criteria defined / refined** (CTO 가 QA 부재 동안 임시로 박음, QA 첫 가동 시 재검토):
  - 본문 비-blank ≤ 10행 / `### Growth-N` 엔트리
  - 슬림 §6 (divider 이후) 전체 비-blank ≤ 200행
  - 코드 펜스 (```...```) 내부는 카운트 제외 — spec template 이 자기 가드에 안 걸려야 함
- **False PASS / False FAIL risks (CTO 가 미리 노트)**:
  - 거짓 PASS: 한 줄에 긴 prose 가 박히면 줄 수는 통과해도 가독성 손실 — 향후 길이 cap 추가 검토
  - 거짓 FAIL: 코드 펜스 외 인용 블록 (`>`) 은 활성으로 카운트됨, 의도된 행동
- **Regression cases**: 없음 (신설)
- **Blocks issued**: 0 (감사 인격 미가동)
- **Cost**: 0 turns (CTO 가 위임 권한으로 박음)
- **Note**: 본 엔트리는 *위임 결정 기록* 으로, QA agent 가 M1 진입 시 첫 가동되면 본 통과 기준을 인수·재평가한다.

## §3 — Open Loops (이 인격 책임)

- 현행 가드 9개 (G-1~G-9) 의 거짓 PASS / 거짓 FAIL 위험 평가 — 첫 가동 시
- G-9 통과 기준 인수·재평가 (CTO 임시 박음 → QA 정식 검토)
- M1 진입 게이트 통과 기준 문서화 — L1~L4 각각의 PASS 정의
- regression 이력 섹션 초기화 (이 파일 §4 로 분리 예정)
