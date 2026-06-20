# legal-rag-mvp — DDL augments (postgres-specific)

> **축**: axis-2 (ddl) 의 **dialect-specific overlay**. `presets/ddl/catalog.yaml` 은 dialect-neutral 단일 진실 — 여기 SQL 은 catalog 가 표현 못 하는 postgres 전용 기능(pgvector / tsvector / pg_bigm / RLS / HNSW)을 얹는다. `render.py` 는 이 디렉터리를 렌더하지 **않는다**; self-host Postgres 에 순서대로 직접 적용한다.

## 왜 augment 인가

catalog 의 neutral 타입 어휘에 `vector(768)` · `tsvector` · RLS 정책 · 부분 HNSW 인덱스가 없다. catalog 를 오염시키지 않고(타 dialect 어댑터 보호) postgres 전용 기능을 분리 관리하기 위해 overlay 로 둔다. legal 버티컬 **전 법무법인 고객 재사용** = 복리 자산(M3 첫 버티컬).

## 적용 순서

| # | 파일 | 내용 |
|---|---|---|
| 01 | `01_extensions.sql` | `vector`·`pg_bigm` 확장, `set_updated_at()` 트리거 함수, `app_service`/`app_user` 롤 (DB당 1회) |
| 02 | `02_legal_case_augment.sql` | legal_case: partner_id, fts_vector(GIN/pg_bigm), RLS(담당변호사+파트너) |
| 03 | `03_precedent_augment.sql` | legal_precedent: fts_vector, firm-wide RLS(전 app_user 읽기) |
| 04 | `04_case_document_augment.sql` | legal_case_document: content_text/ingest_status, fts_vector, case-scoped RLS |
| 05 | `05_case_party_rls.sql` | legal_case_party: case-scoped RLS (PII 격리) |
| 06 | `06_legal_document_chunk.sql` | **NEW** RAG 청크 테이블 — pgvector(768) embedding, HNSW(cosine), 인용 앵커=chunk.id |
| 07 | `07_rag_query_log.sql` | **NEW** 질의 감사 로그 (append-only, attorney 본인 질의만 RLS) |

ERD: `erd_legal_rag.md`.

## 핵심 계약 (engineer 가 반드시 지킴)

- **세션 변수**: app_user 커넥션은 매 트랜잭션 `SET LOCAL app.current_user_id = '<attorney_uuid>'`. 누락 시 RLS 가 0행 반환(fail-safe).
- **롤 모델**: 백엔드 서비스 = `app_service`(BYPASSRLS 또는 SET SESSION AUTHORIZATION), 개별 변호사 = `app_user`(RLS 적용).
- **인용 무결성**: RAG 답변은 `legal_document_chunk.id` 만 출처로 인용 → `source_id`(precedent|case_document)로 역해소. chunk.id 외 참조 금지 = 환각 불가.
- **검색 파이프라인**: `plainto_tsquery` FTS 1단계 → `embedding <=> $query_vec` ANN 2단계 → RRF(Reciprocal Rank Fusion) 병합.
- **임베딩**: multilingual-e5-base 로컬 사이드카(768-dim), 클라우드 API 0. `model_version` 기록 → 모델 교체 시 재임베드 추적.

## 출처

DBA 산출 (Growth-48). 초안 위치 `out/legal-rag-mvp/schema/` (gitignored) → 본 디렉터리로 환류. 도메인 명세는 `out/legal-rag-mvp/domain-needs-spec.md` → wiki 환류 예정.
