# Legal RAG MVP — Seed Data

법무법인 한강(가명) 데모 시드 데이터. RAG MVP 환각0·인용무결성 시연용.

## 파일 구성

```
seed/
  seed_precedents.sql          판례 22건 (legal_precedent)
  seed_cases.sql               사건 12건 (legal_case) + 당사자 29건 (legal_case_party)
  seed_case_documents.sql      사건 서류 15건 (legal_case_document, content_text 포함)
  demo_docs/
    complaint_hanbit_vs_miraesolution.txt   소장 — 공급계약 해지 손해배상
    brief_alphatech_copyright.txt           준비서면 — 소프트웨어 저작권 침해
    contract_software_supply.txt            계약서 — 소프트웨어 유지보수 공급계약
  README.md                    이 파일
```

## 적용 순서

아래 순서를 반드시 지킨다. FK 의존성 때문에 역순 적용 시 오류가 발생한다.

```
# 0. Growth-24 baseline DDL (legal_case, legal_precedent, legal_case_party, legal_case_document)
#    이미 적용된 경우 건너뜀.

# 1. RAG augment DDL (01~07) — augments/legal/ 디렉터리
psql $DSN -f presets/ddl/augments/legal/01_extensions.sql
psql $DSN -f presets/ddl/augments/legal/02_legal_case_augment.sql
psql $DSN -f presets/ddl/augments/legal/03_precedent_augment.sql
psql $DSN -f presets/ddl/augments/legal/04_case_document_augment.sql
psql $DSN -f presets/ddl/augments/legal/05_case_party_rls.sql
psql $DSN -f presets/ddl/augments/legal/06_legal_document_chunk.sql
psql $DSN -f presets/ddl/augments/legal/07_rag_query_log.sql

# 2. 시드 데이터
psql $DSN -f presets/ddl/augments/legal/seed/seed_precedents.sql
psql $DSN -f presets/ddl/augments/legal/seed/seed_cases.sql
psql $DSN -f presets/ddl/augments/legal/seed/seed_case_documents.sql

# 3. demo_docs ingest (txt 파일 → legal_document_chunk)
#    engineer가 구현하는 ingest 파이프라인의 진입점:
#    seed/demo_docs/*.txt → content 추출 → chunk 분할 → embedding → legal_document_chunk INSERT
#    상세: docs/architecture/rag-ingest-pipeline.md (예정)
```

### 전제 조건

- PostgreSQL 15+, pgvector, pg_bigm 확장 설치 완료
- `app_user`, `app_service` 롤 생성 완료 (RLS 정책 의존)
- `employee` 테이블에 담당 변호사 2명 UUID가 존재하거나,
  `seed_cases.sql` 내 DO 블록이 자동 삽입 (스키마 일치 필요)

---

## 데이터 규모 요약

| 테이블 | 건수 |
|---|---|
| legal_precedent | 22건 |
| legal_case | 12건 |
| legal_case_party | 29건 |
| legal_case_document | 15건 |
| demo_docs (txt) | 3건 |

**RLS 시연용 변호사 2명**

| UUID | 이름(가명) | 역할 | 담당 사건 |
|---|---|---|---|
| `a1000000-0000-0000-0000-000000000001` | 이준호 | 파트너 (partner_id 전체) | c001~c006 (assigned) + 전체 (partner) |
| `a1000000-0000-0000-0000-000000000002` | 박서연 | 어소시에이트 | c007~c012 (assigned) |

파트너 이준호는 `partner_id`로 전 사건을 조회할 수 있고,
박서연은 `assigned_attorney_id`로 자신 담당 사건(c007~c012)만 조회 가능.
→ `SET app.current_user_id = '<uuid>'` 로 RLS 전환 시연.

---

## 데모 검색 시나리오 3개

### 시나리오 A — 판례 키워드 검색 (tsvector FTS)

**질의**: "계속적 공급계약 해지 기회손실"

**기대 매칭 판례**:
- `대법원 2022. 7. 28. 선고 2021다54321 판결` (UUID: `…000002`)
  holding: "계속적 공급계약에서 중도 해지 시 기회손실 포함 손해배상"

**기대 매칭 문서**:
- `doc…000001` — 소장 (한빛테크 vs 미래솔루션): content_text에 "기회손실 170,000,000원" 포함
- `doc…000003` — 준비서면 제1호: "계속적 계약 관계 신뢰보호 원칙" 포함

**인용 결과 형식**:
```
[판례] 대법원 2022. 7. 28. 선고 2021다54321 판결
  → 계속적 공급계약 해지 예고 의무 위반 시 기회손실 포함 배상 책임.
[문서] 사건 2024가합10001 소장 §4-(3)
  → 원고 기회손실 170,000,000원 산정 근거.
```

**검증 포인트**: 두 결과가 모두 실제 DB 레코드(chunk.source_id)에 연결되어
존재하지 않는 판례를 생성하지 않음(환각 0).

---

### 시나리오 B — 저작권 침해 실질적 유사성 (FTS + 향후 벡터 검색)

**질의**: "소프트웨어 소스코드 의거성 실질적 유사성 저작권 침해"

**기대 매칭 판례**:
- `대법원 2023. 1. 26. 선고 2022다55678 판결` (UUID: `…000013`)
  holding: "소프트웨어 소스코드 표현 형식 비교, 아이디어-표현 이분법"

**기대 매칭 문서**:
- `doc…000014` — 소장 (알파테크 vs 베타솔루션): "의거성", "실질적 유사성" 포함
- `doc…000015` — 준비서면 제1호: 상세 비교표(유사 라인 4,200개) 포함
- `demo_docs/brief_alphatech_copyright.txt`: ingest 완료 시 청크로 분할

**인용 결과 형식**:
```
[판례] 대법원 2023. 1. 26. 선고 2022다55678 판결
  → 소스코드 실질적 유사성: 구조·순서·알고리즘 표현 비교 기준.
[문서] 사건 2024가합20012 준비서면 §3-3
  → 유사 라인 4,200 / 6,100 (약 68%), 버그 코드 동일 위치 확인.
```

**검증 포인트**: 아이디어-표현 이분법을 정확히 적용한 판례만 인용,
관련 없는 특허 판례(시나리오 무관)는 결과에서 제외됨.

---

### 시나리오 C — RLS 격리 시연 (변호사별 사건 접근 제어)

**질의**: 박서연(UUID: `…000002`)으로 로그인 후 "배임 형사 사건 경영판단"

**기대 동작**:
```sql
SET app.current_user_id = 'a1000000-0000-0000-0000-000000000002';
-- 박서연은 c004(업무상 배임) 사건에 할당되지 않음
-- → legal_case, legal_case_document, legal_case_party 에서 c004 행 반환 없음
```

**기대 결과**:
- `legal_precedent` 조회: `대법원 2021. 8. 19. 선고 2021도3344 판결` 반환
  (판례는 firm-wide — 모든 변호사 접근 가능)
- `legal_case_document` c004 관련 문서: **0건** (RLS 차단)
- 이준호(UUID: `…000001`)로 전환 시 c004 문서 정상 반환

**검증 포인트**: RAG 답변이 판례 인용은 가능하나 c004 사건 서류 내용은
박서연 세션에서 인용 불가 → 데이터 격리 무결성 입증.

---

## ingest 파이프라인 진입점 (engineer 참조)

1. **최우선 ingest 대상**: `demo_docs/*.txt` 3건
   - 파일 경로 → `legal_case_document.storage_key` 매핑은 `seed_case_documents.sql` 참조
   - `complaint_hanbit_vs_miraesolution.txt` → `doc…000001`
   - `brief_alphatech_copyright.txt` → `doc…000015`
   - `contract_software_supply.txt` → `doc…000002`

2. **ingest 흐름**:
   ```
   txt 파일 읽기
     → 약 500 토큰 단위 청크 분할
     → nomic-embed-text (dim=768) 임베딩
     → legal_document_chunk INSERT
         (source_type='case_document', source_id=<doc_uuid>, case_id=<case_uuid>)
     → legal_case_document.ingest_status = 'done' 업데이트
   ```

3. **판례 embedding**: `seed_precedents.sql` 22건의 `holding` 필드
   → `legal_precedent.holding_embedding` 컬럼 (현재 NULL)
   → ingest 사이드카가 채움

4. **FTS 즉시 테스트** (embedding 없이도 가능):
   ```sql
   SELECT citation, holding
   FROM legal_precedent
   WHERE fts_vector @@ plainto_tsquery('simple', '계속적 공급계약 해지 기회손실');
   ```

---

## 가명 처리 원칙 (PIPA 준수)

- 모든 인명은 홍길동·김민수·이준호 등 가명이며 실존 인물과 무관
- 모든 법인명은 가명이며 실존 법인과 무관
- 주민등록번호·사업자등록번호 형식의 식별자는 어떤 파일에도 없음
- 가상 주소는 실제처럼 보이지 않도록 "가상 주소" 명시
- 판례 사건번호는 형식만 현실적인 가상 번호 (실제 판례 전문 복제 없음)
- wiki 환류 시 이 seed 데이터의 PII(가명 포함)는 기재하지 않고
  패턴·구조만 기록 (domain-expert-legal Operating Principles 준수)
