---
name: research-loop
description: 토큰 효율적 리서치 세션 — 시장/UX/기술/경쟁사 조사. context-mode 도구로 raw 결과를 대화 밖에 유지하고, 세션 종료 전 knowledge/wiki/ 환류를 강제한다. deep-research 워크플로우 실행 전후 이 절차를 따른다.
---

# Research Loop

> **핵심 원칙**: 리서치 raw 결과는 대화 컨텍스트에 들어오지 않는다. 인덱스에 저장, 쿼리로만 접근, 위키로 환류.

## 사전 조건 — 세션 분리

리서치는 구현 세션과 **반드시 분리**한다.

```
[리서치 세션]  →  wiki 환류  →  /clear 또는 새 세션
[구현 세션]    →  wiki 읽기(소량)만  →  구현
```

이유: deep-research fan-out 결과가 구현 세션 컨텍스트에 쌓이면 남은 토큰으로 구현 불가.

## Loop Steps

| # | 단계 | 도구 | Exit 기준 |
|---|---|---|---|
| 1 | **질문 정의** | 대화 | 리서치 질문 3~5개 구체화. 모호한 질문 → 먼저 CEO 에게 범위 확인 |
| 2 | **사전 wiki 확인** | `qmd search "<키워드>" -c wiki` | 이미 있는 지식 재확인 (중복 리서치 방지) |
| 3 | **수집** ★컨텍스트 밖 | `ctx_fetch_and_index` (웹) / `ctx_batch_execute` (로컬) | raw 결과가 인덱스에만 저장됨 — 대화 유입 0 |
| 4 | **분석** ★컨텍스트 밖 | `ctx_search(queries:[...])` — 한 번에 모든 질문 배치 | 답변 섹션만 대화로 반환 |
| 5 | **검증** | 필요 시 `ctx_execute` 로 계산/파싱 — 결과 요약만 출력 | 불확실 클레임 제거 |
| 6 | **wiki 환류** ★필수 | `knowledge/wiki/<category>/<slug>.md` + `index.md` 1줄 | git 커밋 완료 |
| 7 | **`/clear` 또는 세션 종료** | — | 구현 세션은 wiki 만 참조해서 시작 |

## context-mode 도구 선택

| 상황 | 도구 | 이유 |
|---|---|---|
| 웹 페이지 분석 | `ctx_fetch_and_index(url)` | raw HTML 대화 유입 차단 |
| 여러 명령 동시 실행 | `ctx_batch_execute(commands, queries)` | 수집+쿼리 1 round-trip |
| 인덱스 내용 조회 | `ctx_search(queries:[q1, q2, ...])` | 여러 질문 배치 처리 |
| 계산/파싱/집계 | `ctx_execute(language, code)` | 중간 데이터 샌드박스 처리 |
| **금지** | `Read` (대용량 파일) / `WebFetch` (직접) | 대화 컨텍스트 팽창 |

## wiki 환류 규약

```markdown
---
slug: <kebab-case>
type: SYNTHESIZED | EXTRACTED | INFERRED
updated: YYYY-MM-DD
sources: <출처 목록>
related: <연관 파일>
---
```

- `out/analysis/` 에 초안을 저장했어도 **반드시 wiki 로 이전** (`out/`은 gitignored — 소멸 위험)
- 불확실 내용은 `[INFERRED]` 레이블 필수
- `knowledge/wiki/index.md` 1줄 추가 후 `build_graph.py` 재생성

## 리서치 카테고리별 저장 위치

| 카테고리 | wiki 경로 |
|---|---|
| 시장/경쟁사 | `knowledge/wiki/market/` |
| UX/Design 패턴 | `knowledge/wiki/design/` |
| 기술/라이브러리 | `knowledge/wiki/tech/` |
| 도메인/산업 지식 | `knowledge/wiki/concepts/` |
| 검증된 고객 사례 | `knowledge/generic/verified-profiles/` |

## Anti-patterns

- 구현 세션에서 deep-research 실행 (컨텍스트 소진)
- `out/analysis/` 에만 저장하고 wiki 미환류
- `ctx_search` 대신 `Read` 로 인덱스 결과 직접 읽기
- 질문 정의 없이 무작정 검색 시작
- 한 세션에 리서치 + 구현 혼재

## 출력 규약

리서치 산출물은 `knowledge/wiki/<category>/<slug>.md` 에 쓰고, main 으로는 **wiki 경로 + 핵심 발견 3줄 + 다음 세션 권고 작업** 만 반환한다.
