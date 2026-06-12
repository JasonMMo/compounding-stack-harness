---
name: research-loop
description: "시장조사·UX리서치·기술조사·경쟁사분석·라이브러리평가 등 모든 리서치 작업에 반드시 이 스킬을 사용한다. deep-research 실행 전후, 웹 검색·URL 분석·문서 수집이 필요할 때, 조사 결과를 knowledge/wiki에 저장해야 할 때 트리거된다. 이 스킬 없이 리서치를 진행하면 raw 결과가 대화 컨텍스트를 잠식해 구현 세션이 토큰 부족으로 실패한다."
---

# Research Loop

> **핵심 원칙**: raw 결과는 대화 밖(인덱스). 쿼리로만 접근. 세션 종료 전 wiki 환류 필수.
> 상세 도구 사용법 → `references/context-mode-guide.md`

## 사전 조건 — 세션 분리

```
[리서치 세션]  → wiki 환류 → /clear 또는 새 세션
[구현 세션]   → wiki 읽기(소량)만 → 구현
```

리서치 raw 결과가 구현 컨텍스트에 쌓이면 남은 토큰으로 구현 불가.

## Loop Steps

| # | 단계 | 도구 | Exit 기준 |
|---|---|---|---|
| 1 | **질문 정의** | 대화 | 3~5개 구체적 질문. 모호하면 CEO에게 범위 확인 먼저 |
| 2 | **사전 wiki 확인** | `/research:query` | 중복 리서치 방지 — 이미 있으면 보완만 |
| 3 | **수집** ★컨텍스트 밖 | `/research:fetch <url>` | raw 결과 인덱스에만 저장, 대화 유입 0 |
| 4 | **분석** ★컨텍스트 밖 | `/research:query <questions>` | 배치 쿼리로 필요한 섹션만 반환 |
| 5 | **검증** | `ctx_execute` | 불확실 클레임 제거, 계산/파싱은 샌드박스 |
| 6 | **wiki 환류** ★필수 | `/research:wiki-save` | git 커밋 완료 |
| 7 | **세션 종료** | `/clear` | 구현 세션은 wiki만 참조해서 시작 |

## wiki 환류 규약

```markdown
---
slug: <kebab-case>
type: SYNTHESIZED | EXTRACTED | INFERRED
updated: YYYY-MM-DD
sources: <출처>
related: <연관 파일>
---
```

카테고리별 저장 위치:

| 카테고리 | 경로 |
|---|---|
| 시장/경쟁사 | `knowledge/wiki/market/` |
| UX/Design | `knowledge/wiki/design/` |
| 기술/라이브러리 | `knowledge/wiki/tech/` |
| 도메인/산업 | `knowledge/wiki/concepts/` |

`out/analysis/`에 초안을 저장했어도 반드시 wiki로 이전 (`out/`은 gitignored).

## Anti-patterns

- 구현 세션에서 deep-research 실행
- `out/analysis/`에만 저장하고 wiki 미환류 (Growth-40 교훈)
- `ctx_search` 대신 `Read`로 인덱스 직접 읽기
- 질문 정의 없이 무작정 검색

## 출력 규약

wiki 경로 + 핵심 발견 3줄 + 다음 세션 권고 작업만 반환한다.
