# Context-Mode 도구 사용 가이드

> SKILL.md Step 3~5 실행 시 참조. ctx_fetch_and_index → ctx_search → ctx_execute 흐름.

## 도구 선택 계층

| 의도 | 도구 | 비고 |
|---|---|---|
| URL 수집 | `ctx_fetch_and_index` | `/research:fetch` 래퍼 사용 |
| 인덱스 검색 | `ctx_search(queries=[...])` | `/research:query` 래퍼 사용 |
| 데이터 가공 | `ctx_execute(language, code)` | 필터/집계/파싱만 — 파일 쓰기 불가 |
| 파일 분석 | `ctx_execute_file(path, ...)` | Read 대신 사용 (결과만 대화 유입) |
| 병렬 수집 | `ctx_batch_execute(commands, queries)` | 여러 URL/명령 + 검색 한 번에 |

## ctx_fetch_and_index

```python
ctx_fetch_and_index(url="https://...", label="krds-github")
```

- 네트워크 접근, jsDelivr/GitHub/공식 문서 모두 가능
- `label`이 FTS5 청크 타이틀 → 검색 품질에 직결, 의미있게 작성
- raw 결과 절대 대화 출력 금지

## ctx_search

```python
ctx_search(
    queries=["KRDS 탭 컴포넌트 클래스명", "Fixed Header 구현"],
    max_results=3,          # 질문당 최대 청크 수
    source="session-events" # 세션 메모리만 검색 시
)
```

- 여러 질문 배열로 한 번에 → 라운드트립 1회
- 결과: 각 질문별 ranked 청크 목록
- **반환값 해석 후 요약만 대화 출력** — raw 청크 붙여넣기 금지

## ctx_execute (분석용)

```python
ctx_execute(language="python", code="""
import json
# 인덱스 데이터를 분석하는 코드
# console.log() / print() 한 것만 대화 반환
""")
```

- 파일 쓰기 불가 (sandbox) — 파일 생성은 Write 도구 사용
- 계산/파싱/필터링에만 사용

## ctx_batch_execute

```python
ctx_batch_execute(
    commands=[
        {"label": "krds-tab", "command": "curl https://..."},
        {"label": "krds-table", "command": "curl https://..."}
    ],
    queries=["탭 컴포넌트 JS API"]  # 수집 + 검색 한 번에
)
```

## Anti-patterns

| 금지 | 대체 |
|---|---|
| `Read` → 대용량 파일 | `ctx_execute_file` |
| `WebFetch` 직접 호출 | `ctx_fetch_and_index` |
| `ctx_search` 결과 raw 출력 | 해석 후 요약만 |
| 구현 세션에서 ctx_fetch 실행 | 리서치 세션에서 미리 인덱싱 |
