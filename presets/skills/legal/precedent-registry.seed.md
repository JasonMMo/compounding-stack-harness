# precedent-registry (판례 등록소)

## Authority
- 권위 참조: 대법원 종합법률정보(glaw.scourt.go.kr) 판례 메타 구조 (Growth-24 legal vertical)
- catalog 위치: `legal` 도메인, entity `precedent`

## Entities

- **precedent**: 판례 1건. `citation` 이 unique key (예: "대법원 2020. 3. 12. 선고 2019다12345 판결"). `holding` (요지) 은 NOT NULL — 검색의 핵심. `full_text` (전문) 은 nullable — 분량이 크고 저작권 확인 필요. `keywords` 는 comma-separated (application layer 파싱).

## Relationships

- `precedent` 은 독립 entity — `legal-case` 와 M:N 가능하나 junction table 은 Growth-24 scope 외 (application layer 에서 참조 번호로 연결).
- 판례 → 사건 유형 (`case_type`) 공유: civil/criminal/administrative/family/commercial — `legal-case.case_type` 과 동일 enum.

## Constraints

- `citation` unique — 같은 판례 중복 등록 불가
- `full_text` 저장 시 **공개 판례만 허용** — 대법원 공개 원칙 확인 후 저장 (저작권 주의 사항, G-4 계열)
- `decided_date` 은 미래 날짜 불가 (application layer)
- `holding` 은 300자 이상 권장 — 검색 품질에 직결 (application layer 경고)

## Examples

- 민사 판례: citation="대법원 2019. 7. 11. 선고 2018다221111 판결", case_type=civil, keywords="손해배상,계약위반,소멸시효"
- 형사 판례: citation="대법원 2021. 5. 27. 선고 2020도1234 판결", case_type=criminal
- 행정 판례: citation="대법원 2022. 11. 24. 선고 2022두3456 판결", case_type=administrative

## AI Search 패턴 — 2단계 (Growth-24 A안 로드맵) → **구현·라이브 (Growth-93/97)**

> 1·2단계 모두 구현 완료. 실제는 `legal-rag` 서비스의 단일 하이브리드 파이프라인
> (FTS ∥ ANN → RRF k=60)으로 통합. 코드 `services/legal-rag/retrieve.py`,
> DDL `presets/ddl/augments/legal/03_precedent_augment.sql` · `06_legal_document_chunk.sql`.
> 아키텍처 상세: [[legal-rag-pattern]]. 검색 전략 상세: [[legal-ai-search-strategy]].
>
> **검색 단위 주의**: 메인 하이브리드 검색 경로는 **`legal_document_chunk` 청크 레벨**에서
> 돈다 (`retrieve.py` 가 `chunk_text` FTS + chunk `embedding` ANN 을 RRF 병합).
> 아래 1단계에 보이는 `legal_precedent.fts_vector`/`holding_embedding` 은 판례 레벨
> 보조 검색면으로 존재하지만, 실제 답변 검색은 청크 단위로 수행되고 인용도 `chunk_id` 기준이다.

### 1단계 (postgres FTS) — ✅ 구현
실제 구현은 `'korean'` config 대신 **`'simple'` + 선택적 `pg_bigm`**(extension 없으면
`plainto_tsquery` 로 graceful degrade — `01_extensions.sql`), inline 표현식 인덱스 대신
**생성 컬럼 `fts_vector`** 사용:
```sql
-- 03_precedent_augment.sql: 미리 계산된 생성 tsvector 컬럼 + GIN
ALTER TABLE legal_precedent
  ADD COLUMN fts_vector tsvector
  GENERATED ALWAYS AS (to_tsvector('simple', holding || ' ' || COALESCE(keywords, ''))) STORED;
CREATE INDEX idx_legal_precedent_fts ON legal_precedent USING GIN (fts_vector);
-- 한국어 부분일치 보강(있을 때): GIN (holding gin_bigm_ops)
-- 검색
SELECT * FROM legal_precedent
WHERE fts_vector @@ plainto_tsquery('simple', '손해배상 소멸시효');
```

### 2단계 (RAG 벡터 ANN) — ✅ 구현·라이브
- `full_text` 를 `legal_document_chunk` (~500 토큰)으로 분할 → 임베딩 → `pgvector` HNSW (별도 infra 불필요)
- 임베딩: **로컬 `multilingual-e5-base` (768-dim, 비대칭 query/passage prefix)** — 클라우드 API 금지(규제업종, API비0)
- 엔드포인트: `POST /search` (`services/legal-rag/api.py`) — 원래 구상 `/api/precedent/search` 와 다름
- 응답: RRF top-K 청크 + **chunk_id 1:1 인용**(환각 차단) + RLS 행/청크 격리. 요지 *생성* 은 미포함(검색+인용까지만)
- ~~설계 완료 시 legal-rag-pattern 에 기록할 것~~ → 완료([[legal-rag-pattern]] 작성됨)

## Ingest 절차 (판례 추가 시)

1. `citation` 중복 확인 → 있으면 update, 없으면 insert
2. `holding` 300자 이상 확인
3. `full_text` 저장 시 저작권 확인 기록 (`notes` 필드에 "출처: 대법원 공개" 명시)
4. 등록 후 `qmd update` — 검색 인덱스 갱신
