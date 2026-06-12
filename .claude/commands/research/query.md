---
name: research:query
description: 인덱스에 대한 배치 검색 — 여러 질문을 한 번에 실행하고 핵심 섹션만 대화에 반환. research-loop Step 2(사전 wiki 확인)·Step 4(분석) 단계에서 사용.
argument-hint: "<question1> | <question2> | <question3>"
allowed-tools:
  - mcp__plugin_context-mode_context-mode__ctx_search
  - mcp__plugin_context-mode_context-mode__ctx_batch_execute
---

<objective>
파이프(`|`)로 구분된 여러 질문을 ctx_search 배치로 실행하고,
각 질문에 대한 핵심 섹션만 요약해 대화에 반환한다.
raw 청크 텍스트 전체를 출력하지 않는다 — 해석된 답변만 반환.
</objective>

<process>

1. **질문 파싱**
   - `$ARGUMENTS`를 `|`로 분리 → 질문 배열 생성
   - 구분자가 없으면 단일 질문으로 처리

2. **배치 검색 실행**
   ```
   ctx_search(queries=[<q1>, <q2>, ...], max_results=3)
   ```
   - source 필터 필요 시: `source="session-events"` (세션 메모리) 또는 기본값(전체)

3. **결과 해석 및 반환**
   각 질문에 대해:
   - 관련 청크 발견 → 핵심 답변 2~3문장으로 요약
   - 청크 없음 → "인덱스에 없음 — /research:fetch <url>로 수집 필요"

4. **출력 형식**
   ```
   ## Q: <질문1>
   <2~3문장 요약>
   출처: <레이블 또는 파일명>

   ## Q: <질문2>
   ...
   ```

</process>

<notes>
- ctx_search 결과(raw 청크)를 그대로 붙여넣지 않는다 — 반드시 해석해서 요약
- knowledge/wiki 사전 확인 용도: `$ARGUMENTS`에 "이미 wiki에 있는가?" 질문 추가 가능
- 세션 메모리 검색: source="session-events" 추가
- 검색 결과가 없으면 /research:fetch로 수집 후 재시도 안내
</notes>
