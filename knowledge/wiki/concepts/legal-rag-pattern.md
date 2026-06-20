---
title: Legal RAG Pattern — 규제업종 하이브리드 검색 아키텍처
slug: legal-rag-pattern
type: concept
created: 2026-06-18
updated: 2026-06-18
sources: [legal-rag-mvp-ddl-augments-readme, legal-rag-mvp-domain-needs-spec]
---

재사용 아키텍처 패턴. 법무 버티컬(M3)에서 도출, 의료·금융 등 규제업종 공통 적용 가능. 관련: [[legal-ai-search-strategy]] [[legal-mvp-spec]] [[smb-ai-market-2026h1]]

## 1. augment 패턴 — neutral catalog + dialect overlay 분리

`presets/ddl/catalog.yaml` 은 dialect-neutral 단일 진실(vector/tsvector 타입 표현 불가). **[EXTRACTED]**

Postgres 전용 기능(pgvector·tsvector·RLS·HNSW)은 `presets/ddl/augments/<vertical>/` 에 overlay SQL로 분리. `render.py` 는 이 디렉터리를 렌더하지 않는다 — self-host Postgres에 순서대로 직접 적용. **[EXTRACTED]**

이 분리로 타 dialect 어댑터(MySQL·Oracle·HSQLDB)가 오염되지 않으며, 버티컬 augment 파일은 법무 전 고객이 재사용 = 복리 자산.

## 2. 하이브리드 검색 파이프라인 (FTS + ANN → RRF)

```
쿼리
  └─ 1단계: plainto_tsquery (tsvector GIN/pg_bigm) — 키워드 매칭
  └─ 2단계: embedding <=> $query_vec (pgvector HNSW, cosine) — 시맨틱 ANN
  └─ RRF 병합: score = Σ 1/(k + rank_i), k=60
  └─ 결과: 상위 N 청크 (chunk.id 리스트)
```

**[EXTRACTED]** (augments README 핵심 계약 §검색 파이프라인)

- FTS 단독: 동의어·맥락 미처리. ANN 단독: 키워드 정밀도 낮음. RRF 병합이 두 약점 상쇄. **[INFERRED]**
- `k=60` — Reciprocal Rank Fusion 표준 상수. 변경 시 재실험 권고.

## 3. 인용 무결성 — 환각 구조적 차단

```
legal_document_chunk.id  (PK, UUID)
  ├─ source_type: 'precedent' | 'case_document'
  └─ source_id: FK → legal_precedent.id | legal_case_document.id
```

RAG 답변은 `chunk.id` 만 인용 → `source_id`로 역해소. **LLM이 판례 텍스트를 재생성하는 경로가 DDL 수준에서 존재하지 않는다.** **[EXTRACTED]**

- chunk.id PK 1:1 바인딩 = 생성된(hallucinated) citation 불가
- "검색 결과 없음"이면 UI는 "DB에 없음. 외부 검색 권고" 메시지 출력 (생성 금지)
- 모든 답변에 출처(citation or case-document.id + 파일명) 표시 필수 — 출처 없는 답변 UI 불허

## 4. RLS 세션 계약 — 롤 모델

| 롤 | 권한 | 용도 |
|---|---|---|
| `app_service` | BYPASSRLS 또는 SET SESSION AUTHORIZATION | 백엔드 서비스 커넥션 (ingest, 관리) |
| `app_user` | RLS 적용 | 개별 변호사 커넥션 (검색·조회) |

매 트랜잭션 시작 시: `SET LOCAL app.current_user_id = '<attorney_uuid>'` **[EXTRACTED]**

누락 시 RLS가 0행 반환(fail-safe). 백엔드 bypass 금지 — 엔지니어 계약. **[EXTRACTED]**

접근 범위:
- `legal_case` / `case_document` / `case_party` — 담당 변호사 + 파트너 (case-scoped RLS)
- `legal_precedent` — firm-wide (전 `app_user` 읽기)
- `rag_query_log` — attorney 본인 질의만 (append-only)

## 5. 로컬 임베딩 사이드카 — self-host 쐐기

임베딩 모델: `intfloat/multilingual-e5-base` 768-dim (한+영, 비대칭 query/passage prefix), 로컬 sentence-transformers 사이드카 배포 (모델 weight 이미지 baked, 런타임 오프라인). **클라우드 API 호출 0.** (Growth-93: 후보였던 embeddinggemma 는 공개 이미지 부재로 폐기) **[EXTRACTED]**

- 의료·법무 등 규제업종에서 외부 API 전송은 개인정보보호법·비밀유지 의무 위반 소지 (PIPA §23, §28-8, 변호사법 §26). **[INFERRED]**
- `model_version` 필드 기록 → 모델 교체 시 재임베드 추적 가능
- 오프라인 사무소 환경(네트워크 없는 지방 법무법인) 대응

## 6. "검색+인용까지만, 생성 없음" — 규제업종 적합성

LLM summarization MVP 제외 이유: **[EXTRACTED]**
1. 법률 환경에서 없는 판례 생성 = 변호사법 위반·징계 사유 소지
2. holding 원문 표시로 변호사가 직접 판단 — augment 모드 (전략 생성 ≠ 이 시스템)
3. 면책 고지 필수: "이 시스템은 검색 도구입니다. 법률 판단은 변호사가 수행합니다."

Growth-17 honest-promise 교훈: RAG 검색은 구현됐으나 AI 전략 *자동생성*(B안)은 미구현 — 미구현 기능 약속 금지. **[INFERRED]**

## 7. 의료·금융 버티컬 일반화

이 패턴의 4요소(neutral catalog + dialect overlay / FTS+ANN+RRF / chunk.id 인용 무결성 / 로컬 임베딩 사이드카)는 버티컬에 무관하다. 의료는 EMR 청크·진료기록 RLS, 금융은 계약서·공시 청크·부서 RLS로 `augments/<vertical>/` 디렉터리만 교체하면 동일 파이프라인 재사용 가능. 규제 근거(의료법·금융실명법)가 다를 뿐 "외부 전송 0 + 인용 무결성"의 셀링포인트는 동일. **[INFERRED]**
