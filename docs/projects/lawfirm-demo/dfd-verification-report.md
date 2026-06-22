---
document: DFD-VERIFICATION-REPORT
title: D5 DFD verification report -- lawfirm-demo
auditor: CQO
date: 2026-06-23
status: BLOCK (BLK-D5-8)
---

# D5 DFD 검증 보고서 -- lawfirm-demo

## 개요

D5 DFD 34개 VP + 8개 BLOCK 조건을 시드 데이터 + DDL 정적 분석으로 검증.
외부 네트워크/라이브DB 호출 없음. 검증 스크립트: `scripts/demo/dfd_verify.py`.

**스크립트 실행 결과**: PASS=35 FAIL=0 N-A=9 TOTAL=44
(VP-P8-07은 스크립트 단순 CASCADE 존재 체크 PASS였으나 DDL 정밀 분석 FAIL 확정)

## VP 판정표

### P1 인증 (5개 - 모두 N-A)

| VP-ID | 판정 | 비고 |
|---|---|---|
| VP-P1-01 | N-A | 잘못된 password -> 401 -- HTTP runtime |
| VP-P1-02 | N-A | 세션 없이 보호 라우트 -> 302 -- HTTP runtime |
| VP-P1-03 | N-A | 만료 세션 -> 302 -- HTTP runtime |
| VP-P1-04 | N-A | logout 후 재접근 -> 302 -- HTTP runtime |
| VP-P1-05 | N-A | 로그인 성공 홈 화면 4카드 -- HTTP runtime |

### P2 사건 관리 (6개 - 모두 PASS)

| VP-ID | 판정 | 근거 |
|---|---|---|
| VP-P2-01 | PASS | 10개 사건 assigned_attorney_id 전부 hr_employee 내, dangling 0 |
| VP-P2-02 | PASS | case_type: civil/criminal/administrative/family/commercial 값만 사용 |
| VP-P2-03 | PASS | status: intake/active/trial/appeal/closed/withdrawn 값만 사용 |
| VP-P2-04 | PASS | 10개 case_number 모두 고유 |
| VP-P2-05 | PASS | DDL: legal_case_party.case_id ON DELETE CASCADE 확인 |
| VP-P2-06 | PASS | DDL: legal_case_document.case_id ON DELETE CASCADE 확인 |

### P3 판례 (3개)

| VP-ID | 판정 | 근거 |
|---|---|---|
| VP-P3-01 | PASS | 12개 citation 모두 고유 |
| VP-P3-02 | PASS | P6(대법원 2022므5678) keywords/holding에 이혼 포함 확인 |
| VP-P3-03 | N-A | 0건 결과 렌더 -- HTTP runtime |

### P4 당사자 (3개 - 모두 PASS)

| VP-ID | 판정 | 근거 |
|---|---|---|
| VP-P4-01 | PASS | 28개 당사자 case_id 전부 ALL_CASE 내, dangling 0 |
| VP-P4-02 | PASS | role: plaintiff/defendant/witness/opposing-counsel/expert-witness 값만 사용 |
| VP-P4-03 | PASS | C7 피고 2명(_pid(17) 양재호, _pid(18) 구은서) 확인 -- UNIQUE 없음 정상 |

### P5 사건문서 (4개)

| VP-ID | 판정 | 근거 |
|---|---|---|
| VP-P5-01 | PASS | 22개 사건문서 case_id 전부 ALL_CASE 내, dangling 0 |
| VP-P5-02 | PASS | 4건 pending 존재, enum 전체 유효(pending/processing/done/error) |
| VP-P5-03 | PASS | document_type 허용값 7종 내 값만 사용 |
| VP-P5-04 | N-A | ingest_status 역전 허용 여부 -- 앱 레이어 runtime |

### P6 인사 (5개 - 모두 PASS)

| VP-ID | 판정 | 근거 |
|---|---|---|
| VP-P6-01 | PASS | 11개 신규 직원 department_id 전부 ALL_DEPT 내 |
| VP-P6-02 | PASS | DDL: assigned_attorney_id ON DELETE RESTRICT 확인 |
| VP-P6-03 | PASS | DDL: owner_id ON DELETE RESTRICT 확인 |
| VP-P6-04 | PASS | status: active/on-leave/terminated 값만 사용 (E14 on-leave 정상) |
| VP-P6-05 | PASS | EMP001-EMP014 14개 employee_number 모두 고유 |

### P7 문서관리 (8개 - 모두 PASS)

| VP-ID | 판정 | 근거 |
|---|---|---|
| VP-P7-01 | PASS | 10개 문서 category_id 전부 6개 카테고리 내 |
| VP-P7-02 | PASS | 10개 문서 owner_id 전부 ALL_EMP 내 |
| VP-P7-03 | PASS | 14개 버전 (doc_id, version_number) 중복 없음 |
| VP-P7-04 | PASS | 8개 접근규칙 (doc_id, type, principal_id) 중복 없음 |
| VP-P7-05 | PASS | permission: read/edit/admin 값만 사용 |
| VP-P7-06 | PASS | DDL: document_access_rule.document_id ON DELETE CASCADE |
| VP-P7-07 | PASS | DDL: document_version.document_id ON DELETE CASCADE |
| VP-P7-08 | PASS | department 6건(ALL_DEPT), employee 2건(ALL_EMP) 다형 주체 모두 유효 |

### P8 전자결재 (10개)

| VP-ID | 판정 | 근거 |
|---|---|---|
| VP-P8-01 | PASS | 7개 요청 requester_id 전부 ALL_EMP 내 |
| VP-P8-02 | PASS | approval_request.status 허용값 6종 내 값만 사용 |
| VP-P8-03 | PASS | 13개 step (request_id, sequence) 중복 없음 |
| VP-P8-04 | PASS | 14개 approver (step_id, employee_id) 중복 없음 |
| VP-P8-05 | PASS | 10개 decision 전부 approved/rejected |
| VP-P8-06 | PASS | 10개 decision (step_id, approver_id) 중복 없음 |
| VP-P8-07 | **FAIL** | approval_decision.step_id RESTRICT로 approval_request 삭제 CASCADE 차단 |
| VP-P8-08 | N-A | 상태전이 pending->in-progress -- 앱 레이어 runtime |
| VP-P8-09 | N-A | 상태전이 in-progress->approved -- 앱 레이어 runtime |
| VP-P8-10 | PASS | AQ5 req=in-progress s1=approved s2=active responded_at=None |

## 발견 결함

### DEFECT-1 (VP-P8-07 / BLK-D5-8): approval_decision CASCADE 누락

**파일**: `out/lawfirm-demo/ddl/postgres.sql` -- approval_decision CREATE TABLE

**현행 DDL (문제)**:
```sql
FOREIGN KEY ("step_id") REFERENCES "approval_step" ("id") ON DELETE RESTRICT,
```

**CASCADE 체인 분석**:
```
approval_request --(CASCADE)--> approval_step      OK
approval_step    --(CASCADE)--> approval_approver   OK
approval_step    --(RESTRICT)-> approval_decision   BLOCK!
```

결재 결정이 존재하는 approval_step 삭제 시 FK RESTRICT 위반.
approval_request 삭제 전체가 실패한다.
BLK-D5-8 기대: step -> approver -> 연쇄 삭제 -- 실제: decision 있는 step에서 차단.

**수정 방향** (`out/lawfirm-demo/ddl/postgres.sql`):
```sql
-- Before:
FOREIGN KEY ("step_id") REFERENCES "approval_step" ("id") ON DELETE RESTRICT,
-- After:
FOREIGN KEY ("step_id") REFERENCES "approval_step" ("id") ON DELETE CASCADE,
```
approval_decision.approver_id RESTRICT는 유지 (approver 단독 삭제 방지 목적).

## BLK 조건 충족 여부

| 조건 ID | BLOCK 기준 | 상태 |
|---|---|---|
| BLK-D5-1 | VP-P1-01~02 FAIL | N-A (런타임 미검증) |
| BLK-D5-2 | VP-P2-01 FAIL | CLEAR (PASS) |
| BLK-D5-3 | VP-P2-05~06 CASCADE FAIL | CLEAR (PASS) |
| BLK-D5-4 | VP-P5-02 ingest pending FAIL | CLEAR (PASS) |
| BLK-D5-5 | VP-P6-02 RESTRICT FAIL | CLEAR (PASS) |
| BLK-D5-6 | VP-P7-04 UNIQUE FAIL | CLEAR (PASS) |
| BLK-D5-7 | VP-P8-06 UNIQUE FAIL | CLEAR (PASS) |
| BLK-D5-8 | VP-P8-07 CASCADE FAIL | **BLOCK** (DDL 결함) |

## 추가 FK 무결성 탐색

| 검증 항목 | 결과 |
|---|---|
| approval_decision.approver_id -> APPROVAL_APPROVERS | OK |
| approval_decision.step_id -> APPROVAL_STEPS | OK |
| approval_approver.step_id -> APPROVAL_STEPS | OK |
| approval_approver.employee_id -> ALL_EMP | OK |
| document_version.uploaded_by -> ALL_EMP | OK |
| current_version_id backfill -> ALL_VER (10건) | OK |

current_version_id: DDL에 FK 제약 없음 (UUID 컬럼만). 앱 레이어 책임. backfill 전부 유효.

## N-A 항목 (founder 라이브 검증 목록)

| VP-ID | 확인 내용 |
|---|---|
| VP-P1-01 | POST /login wrong password -> 401 Korean error message |
| VP-P1-02 | GET /home without session cookie -> 302 /login |
| VP-P1-03 | GET /home expired session -> 302 /login |
| VP-P1-04 | POST /logout then old cookie -> 302 /login |
| VP-P1-05 | Login -> 4 domain cards + killer-app banner (KILLER_APP_URL 설정시) |
| VP-P3-03 | GET /legal/search?q=존재하지않는키워드 -> 0건 HTML (에러 아님) |
| VP-P5-04 | ingest_status done->pending UPDATE 허용 여부 앱 확인 |
| VP-P8-08 | 1단계 승인 후 request.status = in-progress 확인 |
| VP-P8-09 | 마지막 단계 승인 후 request.status = approved 확인 |

## 프로세스 매핑 완전성

D5 부록 A 기준: A(P1), B-1(P2), B-2(P3), B-3(P4), B-4(P5), C(P6), D(P7), E(P8), F(크로스앱 경계)
D1 모듈 A~F 전부 DFD 프로세스에 커버됨. D2 시나리오 1~4 모두 해당 DFD에 대응. 완전성 PASS.

## 종합 판정

**BLOCK -- BLK-D5-8 위반**

DEFECT-1 수정 후 재검증 필요.
수정 위치: `out/lawfirm-demo/ddl/postgres.sql` approval_decision.step_id FK RESTRICT -> CASCADE.
정적 검증 범위 내 나머지 25개 VP: 전부 PASS.
9개 N-A: founder 라이브 검증 이관.

---
*검증 스크립트*: `scripts/demo/dfd_verify.py`
*스크립트 집계*: PASS=35 FAIL=0 N-A=9 TOTAL=44
*DDL 정밀 분석 최종*: PASS=25 FAIL=1(VP-P8-07) N-A=9 TOTAL=35
