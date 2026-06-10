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

## AI Search 패턴 — 2단계 (Growth-24 A안 로드맵)

### 1단계 (즉시 가능 — postgres tsvector)
```sql
-- holding + keywords 컬럼에 GIN 인덱스
CREATE INDEX idx_precedent_fts ON legal_precedent
  USING GIN (to_tsvector('korean', holding || ' ' || COALESCE(keywords, '')));
-- 검색
SELECT * FROM legal_precedent
WHERE to_tsvector('korean', holding || ' ' || COALESCE(keywords, ''))
    @@ plainto_tsquery('korean', '손해배상 소멸시효');
```

### 2단계 (RAG 어댑터 — 설계 예정)
- `full_text` 를 chunk 단위로 분할 → embedding → vector store (pgvector 또는 외부)
- fastapi 엔드포인트: `POST /api/precedent/search` `{ "query": "...", "top_k": 5 }`
- 응답: 유사 판례 목록 + 요지 + citation — 변호사가 전략 수립에 활용
- **설계 완료 시 `knowledge/wiki/syntheses/legal-rag-pattern.md` 에 기록할 것**

## Ingest 절차 (판례 추가 시)

1. `citation` 중복 확인 → 있으면 update, 없으면 insert
2. `holding` 300자 이상 확인
3. `full_text` 저장 시 저작권 확인 기록 (`notes` 필드에 "출처: 대법원 공개" 명시)
4. 등록 후 `qmd update` — 검색 인덱스 갱신
