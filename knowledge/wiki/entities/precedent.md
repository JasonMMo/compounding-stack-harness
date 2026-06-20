---
slug: precedent
confidence: EXTRACTED
updated: 2026-06-11
source: lawfirm-demo (Growth-24 PM loop #1)
---

# precedent (판례)

> catalog entity: `precedent` (domain: `legal`). seed: `presets/skills/legal/precedent-registry.seed.md`.

## 정의

법원이 선고한 판결의 요지·전문을 저장·검색하는 지식 저장소 단위. `citation` 이 unique key. `[EXTRACTED]` — 업무담당자가 "판례정보를 입력하고 일일이 사람이 검색한다"고 직접 언급.

## 핵심 필드

| 필드 | 의미 | 비고 |
|---|---|---|
| `citation` | 판례 인용 표기 | unique, 예: "대법원 2020. 3. 12. 선고 2019다12345 판결" |
| `court` | 법원명 | 대법원/고등법원/지방법원 등 |
| `decided_date` | 선고일 | 미래 날짜 불가 |
| `case_type` | 사건 유형 | legal-case 와 동일 enum |
| `holding` | 판시 요지 | NOT NULL, 검색 핵심, 300자 이상 권장 |
| `full_text` | 판결문 전문 | nullable, 공개 판례만 저장 |
| `keywords` | 키워드 | comma-separated |

## 저작권 주의 `[UNVERIFIED]`

판결문 전문(`full_text`) 저장 전 공개 여부 확인 필수. 대법원 종합법률정보(glaw.scourt.go.kr) 공개 판례는 저장 가능 — 단, 상업적 재배포 조건 재확인 필요.

## AI 검색 패턴 (A안) — ✅ 구현·라이브 (Growth-93/97)

> 1·2단계 모두 구현됨. 실제는 `legal-rag` 서비스의 단일 하이브리드(FTS∥ANN→RRF)로 통합. 상세 [[legal-rag-pattern]] · [[legal-ai-search-strategy]].

### 1단계 — FTS ✅
`holding` + `keywords` → 생성 컬럼 `fts_vector`(GIN) → `plainto_tsquery('simple', …)` 키워드 검색 (한국어는 `pg_bigm` 보강).

### 2단계 — RAG (벡터 ANN) ✅
`full_text` → `legal_document_chunk` 청크 → 로컬 `multilingual-e5-base` 임베딩 → `pgvector` HNSW. 메인 검색은 청크 레벨, 인용은 `chunk_id` 기준. [[legal-rag-pattern]] 작성 완료.

## 관련 엔티티

- [[legal-case]] — 사건-판례 연결 (application layer M:N)
- [[legal-ai-search-strategy]] — 검색 아키텍처 개요
