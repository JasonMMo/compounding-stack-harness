---
slug: legal-ai-search-strategy
confidence: INFERRED
updated: 2026-06-11
source: Growth-24 CTO 설계 (lawfirm-demo A안 채택)
---

# legal-ai-search-strategy (법무 AI 검색 전략)

> Growth-24 에서 확정된 A안 augment 패턴. B안(전략 자동 생성) 은 scope 제외.

## A안 vs B안 결정

| | A안 (채택) | B안 (제외) |
|---|---|---|
| 내용 | AI가 관련 판례 묶어 제시, 변호사가 전략 수립 | AI가 재판 전략 문서 자동 생성 |
| 구현 난이도 | tsvector(즉시) + RAG(2단계) | 법률 할루시네이션 리스크, 전문가 검증 레이어 필요 |
| M3 범위 | O | X — 별도 제품 수준 |
| honest-promise | 가능 | 현재 불가 (Growth-17 교훈 적용) |

## 2단계 구현 로드맵

### 1단계 — postgres tsvector (즉시 가능)
- 대상: `precedent.holding` + `precedent.keywords`
- 인덱스: `CREATE INDEX ... USING GIN (to_tsvector('korean', ...))`
- 엔드포인트: `GET /api/precedents/search?q=<keyword>&type=civil`
- 제약: 형태소 분석기 필요 (`pg_bigm` 또는 `pgroonga` — postgres extension)

### 2단계 — RAG (설계 예정, CTO 에스컬레이션)
- 입력: `precedent.full_text` chunk (500 tokens)
- 임베딩: openai `text-embedding-3-small` 또는 로컬 모델 (cost-aware 선택)
- 벡터 스토어: `pgvector` (postgres 확장) — 별도 infra 불필요
- 엔드포인트: `POST /api/precedents/semantic-search`
- 응답: top-K 유사 판례 + holding 요약
- **설계 확정 시 이 페이지 `[INFERRED]` → `[EXTRACTED]` 갱신할 것**

## 비용 추정 `[INFERRED]`

| 항목 | 단가 | 월 사용량 (추정) | 월 비용 |
|---|---|---|---|
| 판례 임베딩 (1회성) | $0.02/1M tokens | 1,000 판례 × 2,000 tokens = 2M | ~$0.04 |
| 검색 쿼리 임베딩 | $0.02/1M tokens | 50회/일 × 200 tokens × 30일 = 0.3M | ~$0.006 |
| **합계** | | | **< $1/월** |

로컬 모델(`nomic-embed-text`) 채택 시 비용 0.

## 관련

- [[precedent]] — 검색 대상 entity
- [[legal-case]] — 검색 결과를 사건 전략에 연결
