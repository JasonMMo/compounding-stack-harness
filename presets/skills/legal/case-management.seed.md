# case-management (사건 관리)

## Authority
- 권위 참조: 한국 민사소송법·형사소송법 공통 사건 관리 패턴 (Growth-24 legal vertical)
- catalog 위치: `legal` 도메인, entity `legal-case` + `case-party` + `case-document`

## Entities

- **legal-case**: 사건의 생애 관리 단위. `case_number` (사건번호) 가 unique key. `assigned_attorney_id` → `employee.id` (담당 변호사). `client_contact_id` → `crm.contact.id` (의뢰인). `next_hearing_date` 필드는 일정 알림 트리거.
- **case-party**: 사건 당사자 목록. 한 사건에 원고(plaintiff)/피고(defendant)/증인(witness)/상대방 변호인(opposing-counsel)/전문가 증인(expert-witness) 복수 존재. `contact_id` 연결로 crm 과 교차.
- **case-document**: 소장·준비서면·증거·법원명령·계약서·서신 등 사건 첨부 문서. `storage_key` 는 `document_version.storage_key` 참조 (cross-domain, FK 생략).

## Relationships

- `legal-case` 1:N `case-party`: 한 사건에 여러 당사자
- `legal-case` 1:N `case-document`: 한 사건에 여러 문서
- `legal-case` N:1 `employee` (assigned_attorney): 담당 변호사 배정
- `legal-case` N:1 `crm.contact` (client): 의뢰인 (없을 수도 있음 — nullable)

## Constraints

- `case_number` unique — 같은 사건번호 중복 불가
- `status` 상태 흐름: `intake → active → trial → appeal → closed|withdrawn` — terminal state 에서 재활성화 불가 (application layer)
- `closed`/`withdrawn` 전환 시 `case-document` append-only 유지 (법적 감사 추적)
- `next_hearing_date` 은 `filed_date` 이후여야 함 (application layer)

## Examples

- 민사 손해배상 사건: case_type=civil, intake→active(소장접수)→trial(기일지정)→closed(화해)
- 형사 변호: case_type=criminal, active 중 복수 case-party (피의자·검사·증인)
- 행정 취소소송: case_type=administrative, appeal 단계 존재 가능성 높음

## AI Search 연결 (Growth-24 A안)

- `legal-case.summary` 필드: postgres tsvector 인덱스 → 키워드 기반 사건 검색 (즉시 가능)
- `precedent` 연결은 별도 seed (`precedent-registry.seed.md`) 참조
- RAG 벡터 임베딩: 어댑터 레이어 구현 예정 — 이 seed 의 scope 외
