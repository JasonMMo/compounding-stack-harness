---
name: marketing-loop
description: Run the CMO content loop — positioning grounding, knowledge-store evidence search, honest-marketing verification (live-verified claims only), draft, CEO approval gate, ledger record. Use when marketing-agent produces messaging, launch content, or sales enablement material.
---

# Marketing Loop

> 실행 주체: `marketing-agent` (`.claude/agents/marketing-agent.md`). 하드 제약: **honest-marketing** — 모든 기술 주장은 live-verified 능력만 (Growth-17 Scene 5 교훈).

## Loop Steps

| # | 단계 | 동작 | Exit 기준 |
|---|---|---|---|
| 1 | **Positioning grounding** | `docs/business/positioning.md` + revenue-roadmap 의 현행 인수 기준 정독 — 메시지는 여기서 파생, 즉흥 포지셔닝 금지 | 대상 페르소나·milestone 명확 |
| 2 | **증거 검색** ★지식 저장소 | `qmd search "<주장 키워드>" -c docs -c wiki` — 주장하려는 능력의 검증 상태 (4계층 풀테스트·가드) + 고객 needs 표현 (`knowledge/wiki/` 의 `[EXTRACTED]` 발언이 최고의 카피 소재) | 주장별 증거 매핑 |
| 3 | **Honest 검증** | 주장 ↔ repo 실체 대조: 데모에 나올 화면이 실제 구동되는가, 수치는 재현 명령이 있는가. 미구현은 "로드맵" 으로만 — **인수 기준·핵심 메시지 금지** | vaporware 0 |
| 4 | **초안** | 페르소나별 (CEO/업무담당자/IT-담당자) 메시지. 기술 수치는 QA 가 검증 가능한 형태로 (CMO-QA shared 영역) | 초안 + 수치 출처 목록 |
| 5 | **승인 게이트** | 메시지·포지셔닝 카피는 CEO 최종 승인 (charter §2). 외부 게시는 CEO+CMO 합의 + 게시 책임 CEO | 승인 기록 |
| 6 | **기록·환류** ★지식 저장소 | `docs/learn-logs/cmo.md` 갱신. 반응이 확인된 메시지·고객 언어 패턴 → `knowledge/wiki/concepts/` 환류 + index.md 1줄 | ledger + wiki 반영 |

## 지식 저장소 프로토콜

- **시작**: step 2 — 고객의 실제 표현 (`[EXTRACTED]`) 을 검색해 카피에 쓰기. 우리가 지어낸 표현보다 강하다.
- **종료**: step 6 — 효과 있는 메시지는 재사용 자산.

## Anti-patterns

- 미구현 능력의 인수 기준화 (Growth-17) / 검증 불가 수치 ("빠르다") / CEO 승인 전 외부 게시 / 과소진술 (검증된 능력은 당당히 — Scene 4 교훈)
