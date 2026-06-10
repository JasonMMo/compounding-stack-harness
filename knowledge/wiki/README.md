# knowledge/wiki — LLM Wiki (Karpathy 패턴)

> 도메인·고객 횡단 지식이 누적되는 회사 wiki. **LLM 이 쓰고 유지하며, 인간은 소스 큐레이션과 질문을 담당**한다 (Karpathy llm-wiki 패턴). 채택 결정: [`docs/architecture/llm-wiki-adoption.md`](../../docs/architecture/llm-wiki-adoption.md) (Growth-19, CEO 승인 2026-06-11).

## 구조 (llm-wiki-agent 규약 차용)

```
knowledge/wiki/
├── index.md          # 카탈로그 — 페이지당 1줄. 모든 ingest 가 갱신 (LLM 내비게이션 진입점)
├── sources/          # 소스 요약 페이지 — 고객 인터뷰·요청·외부 문서 1건당 1페이지 (PII 제거)
├── entities/         # 실체 페이지 — 고객사·제품·인물(역할만)·시스템
├── concepts/         # 개념 페이지 — 도메인 패턴·업무 규칙·반복 needs
└── syntheses/        # 합성 페이지 — 질의 답변·비교·분석 결과의 환류 (chat history 에 증발 금지)
```

- **log 는 신설하지 않는다** — `learn-log.md` 가 append-only 시간순 기록을 이미 담당 (단일 진실).
- **raw 원문**은 `knowledge/raw/<customer-slug>/` 에 불변 보관 (LLM 은 읽기만).
- 시각화: `python scripts/wiki/build_graph.py` → `out/wiki-graph.html` (derived, gitignore).

## 페이지 규약

모든 페이지는 YAML frontmatter + `[[wikilink]]` 상호참조:

```markdown
---
title: <페이지 제목>
type: source | entity | concept | synthesis
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [<소스 페이지 slug>, ...]   # 이 페이지 주장의 근거
---

본문. 관련 페이지는 [[slug]] 로 링크.
주장마다 신뢰도 라벨: **[EXTRACTED]** / **[INFERRED]** / **[AMBIGUOUS]** / **[UNVERIFIED]**
```

### 신뢰도 라벨 (sdyckjq llm-wiki-skill 차용)

| 라벨 | 의미 | 예 |
|---|---|---|
| `[EXTRACTED]` | 소스가 명시적으로 말함 | 고객: "월 마감은 영업일 3일 내" |
| `[INFERRED]` | 소스들로부터 우리가 추론 | 마감 압박 → 자동화 수요 높을 것 |
| `[AMBIGUOUS]` | 소스 간 상충 — 양쪽 병기 | A 인터뷰 ≠ B 인터뷰 |
| `[UNVERIFIED]` | 출처 불명 — 후속 확인 필요 | 업계 통념 수준 |

PM 의 honest-promise 원칙과 직결: **고객 약속의 근거는 `[EXTRACTED]` 만 인정**.

## 3 Operations

| Op | 트리거 | 동작 |
|---|---|---|
| **Ingest** | PM loop step 7 (contribute-back), 또는 수동 | 소스 읽기 → `sources/` 요약 페이지 → 관련 entity/concept 페이지 갱신 → **index.md 1줄 추가** |
| **Query** | 과거 지식 필요 시 | **index.md 먼저** (또는 `qmd search`) → 해당 페이지만 drill-down. 전체 디렉터리 통읽기 금지 |
| **Lint** | 분기 synthesis (synthesis-template) 에 통합 | 모순·고아 페이지·stale 주장·`[UNVERIFIED]` 잔존 점검 |

## 검색 (qmd)

```
qmd search "<자연어 질의>" -c wiki        # BM25 (기본)
qmd embed && qmd query "<질의>" -c wiki   # 시맨틱 (GGUF 모델 다운로드 후, 선택)
```

collection 구성은 `docs/architecture/llm-wiki-adoption.md` §6.5 참조. qmd 불가 환경 fallback: `python scripts/ledger-index.py --symbol <키워드>` + index.md 수동 스캔.

## Anti-patterns

- index.md 갱신 없는 페이지 추가 (고아 페이지 양산)
- 신뢰도 라벨 없는 고객 관련 주장
- synthesis 를 chat 에만 남기고 환류 생략 ("좋은 답은 wiki 에 파일링한다")
- 페이지 비대화 — 한 페이지가 100행 초과 시 분할 + 링크 (G-9 정신)
