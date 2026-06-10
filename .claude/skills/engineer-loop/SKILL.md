---
name: engineer-loop
description: Run the Engineer execution loop for any implementation delegation — spec intake, prior-art search in the knowledge store, minimal-impact implementation, guard verification, ledger record, per-file commits. Use when engineer-agent receives a CTO delegation or any code/script/test work starts.
---

# Engineer Loop

> 실행 주체: `engineer-agent` (`.claude/agents/engineer-agent.md` — *누가/무엇을*). 이 문서는 *어떻게/어떤 순서로*.

## Loop Steps

| # | 단계 | 동작 | Exit 기준 |
|---|---|---|---|
| 1 | **Spec intake** | CTO 위임 스펙 정독. 모호하면 구현 전에 질문 (추측 구현 금지) | 산출물·검증 기준·커밋 단위가 명확 |
| 2 | **Prior-art 검색** ★지식 저장소 | `qmd search "<주제>" -c docs` + `python scripts/ledger-index.py --symbol <심볼>` — 같은 패턴을 푼 Growth·기존 adapter/template 확인. 재발명 금지 | 기존 자산 재사용 여부 판정 |
| 3 | **환경 사전 점검** | 필요 런타임 확인 (`node --version`, JDK 등) — Growth-15 Java 부재 교훈: 검증 불가 환경이면 위임 전에 보고 | 검증 가능 판정 |
| 4 | **구현** | 최소 변경 (Simplicity First). contract/middle 은 읽기만 — 변경 필요 발견 시 CTO 에스컬레이션 | 스펙 충족 |
| 5 | **검증** | `PYTHONIOENCODING=utf-8 python scripts/diagnose.py` 전체 + 관련 테스트 (L1~L4 해당 subset). 가드 FAIL 은 해소 또는 명시 보고 — silence 금지 | 가드 전 PASS + 테스트 green |
| 6 | **기록·커밋** | `docs/learn-logs/engineer.md` Growth 절 + 파일당 1커밋 (HEREDOC, Fable 5 trailer). **push 는 CTO** | 커밋 해시 보고 |
| 7 | **환류** ★지식 저장소 | 재사용 가능 패턴 발견 시 `knowledge/wiki/concepts/` 페이지 초안 (라벨 `[EXTRACTED]`/`[INFERRED]`, index.md 1줄) 또는 CTO 에 등록 제안 | CLAUDE.md §7 체크 |

## 지식 저장소 프로토콜 (규약: `knowledge/wiki/README.md`)

- **시작**: step 2 — wiki/원장 검색이 구현보다 먼저. 통읽기 금지 (index→drill-down).
- **종료**: step 7 — "한 번만 쓸 코드인데" 가 떠오르면 catalog/template/wiki 등록부터.

## Anti-patterns

- 스펙 모호한 채 추측 구현 / contract 재구현 (G-1) / 가드 FAIL silence / `git add -A` / push / known-hollow 테스트 잔류 (Growth-16 교훈)
