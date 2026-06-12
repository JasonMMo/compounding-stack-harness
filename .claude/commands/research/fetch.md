---
name: research:fetch
description: URL을 context-mode 인덱스에 저장한다 — 대화 컨텍스트 유입 없이 raw 페이지를 인덱싱. research-loop Step 3(수집) 단계에서 사용.
argument-hint: <url> [label]
allowed-tools:
  - mcp__plugin_context-mode_context-mode__ctx_fetch_and_index
  - mcp__plugin_context-mode_context-mode__ctx_search
  - mcp__plugin_context-mode_context-mode__ctx_stats
---

<objective>
URL 하나를 ctx_fetch_and_index로 인덱스에 저장하고, 저장 확인 후 간단한 요약만 대화에 반환한다.
raw 페이지 내용은 절대 대화에 출력하지 않는다 — 인덱스에서 ctx_search로만 접근.
</objective>

<process>

1. **URL 및 레이블 파싱**
   - `$ARGUMENTS`에서 URL(첫 번째 토큰)과 선택적 레이블(나머지)을 추출
   - 레이블이 없으면 URL 도메인에서 자동 생성 (예: `github.com/krds` → `krds-github`)

2. **인덱싱 실행**
   ```
   ctx_fetch_and_index(url=<URL>, label=<레이블>)
   ```
   - 실패 시: 에러 메시지만 출력하고 중단

3. **저장 확인 (선택)**
   - 인덱싱 성공 후 저장된 청크 수 확인용 쿼리 1회:
   ```
   ctx_search(queries=["<레이블>"], max_results=2)
   ```

4. **대화 반환 — 3줄 이내**
   ```
   인덱싱 완료: <레이블>
   청크: <N>개
   다음: /research:query <질문> 으로 내용 조회
   ```

</process>

<notes>
- ctx_fetch_and_index 결과(raw HTML/텍스트)를 절대 대화에 출력하지 않는다
- 여러 URL을 연속 처리할 때는 /research:fetch를 반복 호출한다
- 인덱싱 후 ctx_stats로 전체 인덱스 상태 확인 가능
</notes>
