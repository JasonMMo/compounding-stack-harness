---
slug: legal-ai-search-strategy
confidence: EXTRACTED
updated: 2026-06-20
source: Growth-24 CTO 설계 (A안 채택) → Growth-93/97 구현·라이브 (legal-rag 서비스)
---

# legal-ai-search-strategy (법무 AI 검색 전략)

> Growth-24 에서 확정된 A안 augment 패턴. B안(전략 자동 생성) 은 scope 제외.
>
> **구현 상태 (Growth-93/97, 2026-06-20)**: A안의 1·2단계가 **모두 구현·라이브**됨
> (`legal-rag.n9n.co.kr`). 단, 원래 구상(lawfirm-demo 위 2개 엔드포인트)과 달리
> **별도 `legal-rag` FastAPI 서비스의 단일 하이브리드 파이프라인**(FTS∥ANN→RRF)으로
> 실현. 코드: `services/legal-rag/retrieve.py`. 상세: [[legal-rag-pattern]].

## A안 vs B안 결정

| | A안 (채택) | B안 (제외) |
|---|---|---|
| 내용 | AI가 관련 판례 묶어 제시, 변호사가 전략 수립 | AI가 재판 전략 문서 자동 생성 |
| 구현 난이도 | tsvector(즉시) + RAG(2단계) | 법률 할루시네이션 리스크, 전문가 검증 레이어 필요 |
| M3 범위 | O | X — 별도 제품 수준 |
| honest-promise | 가능 | 현재 불가 (Growth-17 교훈 적용) |

## 2단계 구현 로드맵 → **구현 완료 (단일 하이브리드 파이프라인으로 통합)**

> 아래 1·2단계는 Growth-24 당시 *순차 로드맵* 구상. 실제 구현(Growth-93/97)은
> 두 단계를 **하나의 하이브리드 검색**(FTS ∥ ANN → RRF 병합)으로 합쳐
> `legal-rag` 서비스에 구현. `retrieve.py` Stage 1(FTS) / Stage 2(ANN) / Stage 3(RRF).

### 1단계 — postgres FTS ✅ 구현
- 대상: `legal_document_chunk.chunk_text` (원래 구상은 `precedent.holding`/`keywords`)
- 쿼리: `plainto_tsquery('simple', q)` + `to_tsvector('simple', chunk_text)` (GIN 인덱스, `ts_rank_cd` 정렬)
- 제약 메모: 형태소 분석기(`pg_bigm`/`pgroonga`)는 `simple` config 로 현재 우회 — 한국어 형태소 정밀도 향상은 후속 과제

### 2단계 — RAG (벡터 ANN) ✅ 구현·라이브
- 입력: `legal_document_chunk` (~500 토큰 청크)
- 임베딩: **로컬 `multilingual-e5-base` (768-dim, 비대칭 query/passage prefix)** — 클라우드 API 금지(규제업종, API비0). openai `text-embedding-3-small` 후보는 폐기
- 벡터 스토어: `pgvector` HNSW, cosine `embedding <=> query_vec` — 별도 infra 불필요 ✅
- 엔드포인트: `POST /search` (`services/legal-rag/api.py`) — 원래 구상 `/api/precedents/semantic-search` 와 다름
- 응답: RRF(k=60) top-K 청크 + **chunk_id 1:1 인용**(환각 차단) + RLS 행단위/청크단위 격리. holding 요약 생성은 미포함(검색+인용까지만 — [[legal-rag-pattern]] §6)

## 비용 추정 — **실제: $0/월 (로컬 모델 채택)**

실제 채택은 **로컬 `multilingual-e5-base` (Growth-93)** 이라 임베딩 API 비용은 **0** 이다.
규제업종 데이터 외부전송 금지가 1차 사유, 비용 0 은 부수 효과.

아래 표는 *클라우드 임베딩을 썼다면* 의 가상 비교치 `[INFERRED]` (폐기된 경로):

| 항목 | 단가 | 월 사용량 (추정) | 월 비용 |
|---|---|---|---|
| 판례 임베딩 (1회성) | $0.02/1M tokens | 1,000 판례 × 2,000 tokens = 2M | ~$0.04 |
| 검색 쿼리 임베딩 | $0.02/1M tokens | 50회/일 × 200 tokens × 30일 = 0.3M | ~$0.006 |
| **합계** | | | **< $1/월** |

로컬 채택이 위 비용마저 0 으로 만들었고, 동시에 데이터주권을 확보했다.

## 관련

- [[precedent]] — 검색 대상 entity
- [[legal-case]] — 검색 결과를 사건 전략에 연결
