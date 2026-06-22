# D2 — 유저플로우 : 법무법인 통합 업무관리 (lawfirm-demo)

> 문서 번호: D2
> owner: PM · CDO
> 상태: DRAFT v0.1 (2026-06-23)
> 연관 anchor: `docs/projects/lawfirm-demo/`
> 상위 입력: D1 기능명세서 (`docs/projects/lawfirm-demo/D1-functional-spec.md`)
> 참고: 이 문서의 사례 데이터는 모두 **가상(가명) 데이터**임. 실존 인물·법인·사건과 무관.

---

## 0. 읽기 전 주의

- 모든 화면 라우트는 실제 `frontend/adapters/vanilla-htmx/server.py` 에 구현된 것만 기재한다. 미구현 화면은 `[[ ]]` 로 표기하고 "데모 범위 외"로 명시한다.
- killer-app(legal-pro) 은 lawfirm-demo 와 **물리적으로 별개 앱·별개 DB·별개 로그인**이다. SSO 없음. 진입 링크 클릭 후 legal-pro 화면에서 별도 인증이 필요하다.
- 이 문서의 플로우는 서버사이드 렌더링(vanilla-htmx) + FastAPI 백엔드 구조를 기반으로 한다.

---

## 1. 페르소나 요약

| 페르소나 | 역할 | 주 진입 화면 | 핵심 목표 |
|---|---|---|---|
| CEO (대표 변호사·파트너) | 경영·감독 | 홈 → 사건·결재 목록 | 전사 사건 현황·결재 라인 파악 |
| 업무담당자 (어소시에이트·사무장) | 실무 입력·조회 | 홈 → 사건·당사자·문서·결재 | 사건 등록, 당사자·문서 첨부, 결재 상신, killer-app 점프 |
| IT 담당자 | 운영·보안 | 홈 → 문서 접근규칙·직원·부서 | 접근권한 설정, 직원 등록, 헬스 확인 |

---

## 2. 공통 진입 플로우 — 로그인 → 홈

모든 페르소나의 공통 시작점이다.

```
[브라우저 접속] → GET /
       │
       ├─ 미인증 ──→ GET /login  [로그인 화면]
       │                  │
       │            POST /login {username, password}
       │                  │
       │            ┌─────┴──────────────────┐
       │            │ 인증 실패               │ 인증 성공
       │            │ 401 + 한국어 오류 표시  │ 세션 토큰 발급
       │            │ (화면 재렌더)           │
       │            └─────────────────────────┘
       │                        │
       └─ 인증 중 ──────────────→ GET /home  [홈 화면]
                                     │
                           도메인 카드 4종 표시:
                           [법무] [인사] [문서관리] [전자결재]
                           + 상단 배너: "AI 판례검색" (killer-app 링크)
```

**시드 데이터 예시**: `demo/demo` 로그인 후 홈 화면에 "법무법인 데모" 브랜드명 + 4개 도메인 카드 + 상단 "AI 판례검색" 배너 표시. 배너는 `KILLER_APP_URL` 환경변수가 설정된 경우에만 노출.

---

## 3. 시나리오 1 — 업무담당자: 새 사건 등록 → 당사자 추가 → 문서 첨부

**페르소나**: 어소시에이트 이수진 (EMP002, 소송부)
**목표**: 신규 수임 사건을 시스템에 등록하고, 당사자·문서를 연결한다.
**시드 기준**: CASE-2024-005 "업무상 횡령 고소 대응 사건" 의 등록 흐름을 모사.

```
[홈 화면 /home]
       │
       클릭: [법무] 도메인 카드
       │
       GET /entities/legal-case  [사건 목록]
       │  - 기존 사건 10건 표시 (CASE-2024-001 ~ CASE-2025-003)
       │  - 페이지당 20건, 오프셋 페이징
       │
       클릭: [새 사건 등록] 버튼
       │
       GET /entities/legal-case/new  [사건 등록 폼]
       │  - 필드: 사건번호, 제목, 사건유형, 상태, 접수일, 법원, 다음기일, 담당변호사ID, 요약
       │
       입력 후 [저장]
       │
       POST /entities/legal-case/new
       │  body: {entity_type: "legal-case", data: {case_number: "CASE-2024-005",
       │          title: "업무상 횡령 고소 대응 사건", case_type: "criminal",
       │          status: "active", filed_date: "2024-04-22", ...}}
       │
       ┌─────────────────────────────┐
       │ 성공 → 302 redirect         │
       └─────────────────────────────┘
              │
              GET /entities/legal-case/<new_id>  [사건 상세]
              │  - 등록된 사건 정보 표시

              ─── 당사자 추가 ───

              사이드바 클릭: [당사자] → GET /entities/legal-case-party
              │  (현재 당사자 목록, case_id 필터 미지원 — 전체 목록)
              │
              클릭: [새 당사자 등록] 버튼
              │
              GET /entities/legal-case-party/new  [당사자 등록 폼]
              │  - 필드: 사건ID, 역할, 이름, 비고
              │
              입력: {case_id: "<new_id>", role: "plaintiff",
                     name: "주식회사 미래테크", notes: "피해 법인 고소인"}
              │
              POST /entities/legal-case-party/new
              │
              → 성공 → GET /entities/legal-case-party/<party_id>
              │
              반복: 피고 "유창호"(전 재무이사), 감정인 "공인회계사 나인규" 추가

              ─── 사건문서 첨부 ───

              사이드바 클릭: [사건문서] → GET /entities/legal-case-document
              │
              클릭: [새 문서 등록] 버튼
              │
              GET /entities/legal-case-document/new  [사건문서 등록 폼]
              │  - 필드: 사건ID, 문서유형, 제목, 제출일, 저장경로, 비고
              │
              입력: {case_id: "<new_id>", document_type: "evidence",
                     title: "회계감정 보고서", filed_at: "2024-07-15",
                     storage_key: "cases/c5/evidence_001.pdf",
                     notes: "갑 제3호증"}
              │
              POST /entities/legal-case-document/new
              │
              → 성공 → GET /entities/legal-case-document/<doc_id>
              │  - ingest_status: "pending" (색인 대기 상태로 초기화)
```

**완료 상태**: 사건·당사자 3명·사건문서 1건이 시스템에 등록됨.

---

## 4. 시나리오 2 — 변호사: 사건 검토 중 killer-app 으로 점프해 판례 검색

**페르소나**: 파트너 변호사 김대호 (EMP001, 소송부)
**목표**: CASE-2024-007 "부동산 이중매매 소유권 이전 청구" 사건 검토 중 관련 판례가 필요해 AI 판례검색으로 이동한다.
**크로스앱 경계**: lawfirm-demo → legal-pro 는 별도 탭으로 이동. **SSO 없음, 별도 로그인 필요.**

```
[사건 목록 /entities/legal-case]
       │
       클릭: CASE-2024-007 "부동산 이중매매 소유권 이전 청구"
       │
       GET /entities/legal-case/<C7_id>  [사건 상세]
       │  - 상태: trial, 법원: 인천지방법원, 담당: 최준혁
       │  - 요약: "제1매수인 권리 보전 위한 소유권 이전 청구. 부동산 감정가 6억원."
       │  - 다음 기일: 2026-07-25
       │

       ─── 판례 필요 → killer-app 진입 ───

       상단 배너 클릭: "AI 판례검색"  (또는 사이드바 링크)
       │
       ┌──────────────────────────────────────────────────────────────────┐
       │ target=_blank → 새 탭 열림                                       │
       │ URL: legal-rag.n9n.co.kr/pro                                     │
       │                                                                  │
       │ *** 크로스앱 핸드오프 ***                                         │
       │ lawfirm-demo 와 legal-pro 는 물리적으로 별개 앱·별개 DB 임.      │
       │ 이 시점부터 lawfirm-demo 세션은 전달되지 않음.                    │
       │ legal-pro 화면에서 변호사 계정으로 별도 로그인 필요.              │
       └──────────────────────────────────────────────────────────────────┘
              │
              [legal-pro 로그인 화면]  ← 변호사 bcrypt 인증 (별도 계정)
              │
              로그인 성공 → legal-pro 판례검색 화면
              │
              검색어 입력: "이중매매 반사회적 법률행위 소유권"
              │
              POST /search (legal-rag API)
              │  - 하이브리드 검색 (FTS + ANN + RRF)
              │  - 관련 판례 청크 반환
              │
              결과: 대법원 2020다77892 판시요지 확인
              │  "부동산 이중매매에서 제2매수인이 제1매매 사실을 알면서
              │   매매계약을 체결하였다면 반사회적 법률행위로서 무효이고..."
              │
              [원문 보기] 드로어 클릭 → 판결 전문 확인

       ─── 원래 탭으로 복귀 ───

       lawfirm-demo 사건 상세 탭으로 복귀 (세션 유지)
       │
       확인한 판례를 준비서면 작성에 활용 (시스템 외부 작업)
```

**정직 표기**: killer-app 진입 후 legal-pro 에서 별도 로그인이 필요하다. lawfirm-demo 와 legal-pro 간 자동 인증(SSO) 은 현재 구현되지 않았으며, 인도 범위 외다.

---

## 5. 시나리오 3 — 결재요청 상신 → 다단계 승인 → 결정

**페르소나**: 강민서(EMP007, 기업자문팀) 가 상신, 김대호(EMP001) 와 대표가 승인.
**목표**: AQ5 "SaaS 계약서 의뢰인 외부 발송 승인" 결재 흐름 시연.
**시드 기준**: 1단계(담당파트너 승인, 강민서→완료) + 2단계(대표변호사 최종승인, 미응답) 진행 중 상태.

```
─── 상신 단계 ───

[홈 화면] → 클릭: [전자결재] 도메인 카드
       │
       GET /entities/approval-request  [결재요청 목록]
       │  - 7건 표시: approved 4, rejected 1, in-progress 1, pending 1
       │
       클릭: [새 결재요청] 버튼
       │
       GET /entities/approval-request/new  [결재요청 등록 폼]
       │  - 필드: 제목, 유형(leave/expense/contract/dispatch/purchase), 신청 대상 ID, 만료일
       │
       입력: {title: "SaaS 계약서 의뢰인 외부 발송 승인",
              subject_type: "dispatch",
              subject_id: "<case_document_id>",  ← C6 사건문서
              requester_id: "<E7_id>",
              expires_at: "2026-07-31"}
       │
       POST /entities/approval-request/new
       │
       → 성공 → GET /entities/approval-request/<AQ5_id>  [결재요청 상세]
       │  - 상태: pending

       ─── 결재단계 설정 ───

       GET /entities/approval-step/new  [결재단계 등록]
       │
       입력: {request_id: "<AQ5_id>", sequence: 1,
              name: "담당파트너 승인", requires_all: true}
       POST /entities/approval-step/new → 성공
       │
       입력: {request_id: "<AQ5_id>", sequence: 2,
              name: "대표변호사 최종승인", requires_all: true}
       POST /entities/approval-step/new → 성공

       ─── 결재자 지정 ───

       GET /entities/approval-approver/new  [결재자 등록]
       입력: {step_id: "<step1_id>", employee_id: "<E7_id>"}  ← 강민서
       POST → 성공
       입력: {step_id: "<step2_id>", employee_id: "<EMP1_id>"}  ← 김대호
       POST → 성공

       ─── 1단계 승인 ───

       GET /entities/approval-decision/new
       입력: {step_id: "<step1_id>",
              approver_id: "<approver1_id>",
              decision: "approved",
              comment: "1차 승인."}
       POST /entities/approval-decision/new → 성공
       │
       GET /entities/approval-step/<step1_id>/edit  [단계 상태 수정]
       입력: {status: "approved"}
       POST → 성공
       │
       GET /entities/approval-request/<AQ5_id>/edit  [요청 상태 수정]
       입력: {status: "in-progress"}
       POST → 성공

       ─── 2단계 (대기 중) ───

       GET /entities/approval-request  [목록 재조회]
       │  - AQ5 상태: in-progress (1단계 완료, 2단계 대기)
       │  - 현재 시드 상태: 김대호(대표) 응답 대기 (responded_at = NULL)
       │

       ─── (향후) 2단계 최종 승인 ───

       [[ 결재자가 브라우저에서 직접 결정을 입력하는 전용 화면은 현재 구현되지 않음.
          현재 demo 에서는 관리자가 approval-decision/new 에서 대리 입력하는 방식.
          전용 결재 처리 화면은 Q-1 확정 후 구현 범위를 결정. ]]

       최종 승인 시: approval-decision 등록 + approval-step 상태→approved + approval-request 상태→approved
```

**시드 데이터 비교**:
- AQ1 "이수진 연차" (1단계만, 김대호 승인, 코멘트: "승인합니다.") — 단일 단계 흐름
- AQ4 "한소율 연차" (1단계에서 임도현이 반려, 코멘트: "재판 일정 충돌로 반려.") — 반려 흐름
- AQ6 "복합기 구매 340만원" (3단계 결재, pending 상태) — 3단계 미진행 흐름

---

## 6. 시나리오 4 — IT 담당자: 문서 접근규칙 설정

**페르소나**: 배지수 (EMP012, 지원팀 관리자)
**목표**: 신규 문서 "법인 인사규정" 에 대해 부서별 접근권한을 설정한다.
**시드 기준**: DOC10 "법인 인사규정" + 기존 접근규칙 패턴(법인 정관 → 지원팀 read, 개인정보처리방침 → 지원팀 admin).

```
[홈 화면] → 클릭: [문서관리] 도메인 카드
       │
       GET /entities/document-document  [문서 목록]
       │  - 10건 표시: 법인 정관(v2.0, published), 개인정보처리방침(v2.0),
       │    법률자문 표준 위임계약서(v2.0), 직원 복무 규정(v2.0), ...
       │
       클릭: "법인 인사규정" (DOC10)
       │
       GET /entities/document-document/<DOC10_id>  [문서 상세]
       │  - 카테고리: 인사서류(CAT-HR), 소유자: 배지수, 상태: published
       │  - 현행 버전: v1.0 (인사규정_v1.pdf, 200KB)

       ─── 접근규칙 확인 ───

       사이드바 클릭: [접근규칙] → GET /entities/document-access-rule  [접근규칙 목록]
       │  - 8건 표시:
       │    DOC1 법인정관 → 지원팀 read (무기한)
       │    DOC2 개인정보처리방침 → 지원팀 admin (무기한)
       │    DOC5 복무규정 → 지원팀 admin (무기한)
       │    DOC6 출장비 정산 지침 → 지원팀 read (무기한)
       │    DOC7 2025년 예산안 → EMP001 김대호 read (만료: 2027-01-01)
       │    DOC8 소장 작성 표준 서식 → 소송부(LAW001) read (무기한)
       │    DOC9 준비서면 작성 가이드 → EMP002 이수진 edit (무기한)
       │

       ─── 신규 접근규칙 등록 ───

       클릭: [새 접근규칙] 버튼
       │
       GET /entities/document-access-rule/new  [접근규칙 등록 폼]
       │  - 필드: 문서ID, 주체 유형(department/employee), 주체ID, 권한(read/edit/admin), 만료일
       │
       입력 예시 1 — 지원팀 전체 edit 권한:
       {document_id: "<DOC10_id>",
        principal_type: "department",
        principal_id: "<DEPT5_id>",  ← 지원팀
        permission: "edit",
        expires_at: null}
       POST /entities/document-access-rule/new → 성공
       │
       입력 예시 2 — 기업자문팀 read 권한 (한시적):
       {document_id: "<DOC10_id>",
        principal_type: "department",
        principal_id: "<DEPT3_id>",  ← 기업자문팀
        permission: "read",
        expires_at: "2027-01-01T00:00:00+00:00"}
       POST /entities/document-access-rule/new → 성공

       ─── 버전 이력 확인 ───

       사이드바 클릭: [버전] → GET /entities/document-version  [버전 목록]
       │  - 14건 표시: DOC1 v1.0(비공개)→v2.0(공개), DOC2 v1.0→v2.0, ...
       │
       클릭: DOC10 "법인 인사규정 v1.0"
       │
       GET /entities/document-version/<VID14_id>  [버전 상세]
       │  - 파일명: 인사규정_v1.pdf, 200KB, is_published: true
       │
       [[ 파일 실제 다운로드/미리보기 기능은 데모 범위 외.
          storage_key 경로 정보만 표시. ]]
```

**접근규칙 패턴 정리**:
- 부서 단위 bulk 권한: `principal_type=department` + 부서 ID → 해당 부서 전원 적용
- 개인 한시 권한: `principal_type=employee` + 직원 ID + `expires_at` → 한시적 열람
- 권한 레벨: `read` < `edit` < `admin` (admin = 규칙 변경 포함)

---

## 7. 예외·에러 플로우

| 상황 | 트리거 | 화면 처리 | 관련 ID |
|---|---|---|---|
| 인증 실패 (로그인) | 잘못된 사용자명/비밀번호 | 로그인 화면 재렌더 + 한국어 오류 메시지 | A-01 |
| 미인증 접근 | 세션 토큰 없이 보호 라우트 접근 | 로그인 화면으로 302 리디렉션 | A-03 |
| 세션 만료 (인증 중) | 세션 만료 후 API 호출 | 로그인 화면으로 302 리디렉션 | A-03 |
| 존재하지 않는 엔티티 (404) | `/entities/<type>/<id>` 접근 | `error.html` — "해당 항목을 찾을 수 없습니다." | 공통 |
| 삭제 2단계 확인 | `GET /entities/<type>/<id>/delete` | `delete_confirm.html` — "정말 삭제하시겠습니까?" | 공통 |
| 삭제 성공 | `POST /entities/<type>/<id>/delete` | `delete_success.html` — 삭제 완료 메시지 | 공통 |
| 이미 삭제된 항목 재접근 | DELETE 후 GET | `delete_success.html` — already_deleted=True (F-4 멱등성) | 공통 |
| 필수 필드 누락 (등록) | 빈 필드로 POST | 등록 폼 재렌더 + 한국어 오류 메시지 | 공통 |
| 백엔드 연결 불가 | BACKEND_BASE_URL 응답 없음 | `error.html` — "서버에 연결할 수 없습니다. (UNAVAILABLE)" | 공통 |
| killer-app 진입 후 별도 로그인 | 배너 클릭 → legal-pro | legal-pro 로그인 화면 (lawfirm-demo 세션 무관) | F-03 |

---

## 8. 화면 전환 맵 (라우트 기준)

실제 `server.py` 에 구현된 라우트만 기재한다.

```
/                     → (인증 여부에 따라) /login 또는 /home
/login    GET         → 로그인 폼 화면
/login    POST        → 인증 처리 → /home 또는 오류 재렌더
/logout   POST        → 세션 폐기 → /login
/home     GET         → 홈 화면 (도메인 카드 + killer-app 배너)

/entities/<type>              GET  → 목록 화면 (list.html 또는 layout 변형)
/entities/<type>/new          GET  → 등록 폼 (create.html)
/entities/<type>/new          POST → 등록 처리 → /<type>/<new_id> 또는 오류
/entities/<type>/<id>         GET  → 상세/수정 폼 (detail.html)
/entities/<type>/<id>/edit    POST → 수정 처리 → /<type>/<id> 또는 오류
/entities/<type>/<id>/delete  GET  → 삭제 확인 화면 (delete_confirm.html)
/entities/<type>/<id>/delete  POST → 삭제 처리 → delete_success.html
/entities/<type>/<id>/panel   GET  → 상세 패널 파셜 (htmx, master-detail 레이아웃용)

/legal/search  GET  → 법무 판례 키워드 검색 화면 (legal_precedent_search.html)
/health        GET  → 헬스체크 화면 (인증 없음)

[killer-app 링크: target=_blank → legal-rag.n9n.co.kr/pro]
  ↑ lawfirm-demo 세션 전달 없음. legal-pro 별도 로그인 필요. ↑
```

**엔티티 슬러그 목록** (현재 4도메인 14엔티티):
`legal-case`, `legal-precedent`, `legal-case-party`, `legal-case-document`,
`hr-employee`, `hr-department`,
`document-document`, `document-version`, `document-category`, `document-access-rule`,
`approval-request`, `approval-step`, `approval-approver`, `approval-decision`

---

## 9. killer-app 크로스앱 핸드오프 플로우 (정직 표기)

```
lawfirm-demo (세션 인증, demo/demo)
       │
       상단 배너 또는 사이드바: "AI 판례검색" 클릭
       │
       ▼
       [새 탭 오픈] target=_blank
       URL: ${KILLER_APP_URL} (환경변수 = legal-rag.n9n.co.kr/pro)
       │
       ┌────────────────────────────────────────────────────────┐
       │ 경계: 이 시점부터 별개 앱                               │
       │ - 별개 서버 (legal-rag.n9n.co.kr)                      │
       │ - 별개 PostgreSQL DB                                    │
       │ - 별개 인증 (변호사 이메일+비밀번호, bcrypt)            │
       │ - SSO 없음 — lawfirm-demo 세션 토큰 무효               │
       └────────────────────────────────────────────────────────┘
       │
       legal-pro 로그인 화면
       │
       변호사 계정으로 로그인
       │
       legal-pro 판례검색·원문보기 화면
       │
       (검색 후 원래 lawfirm-demo 탭으로 수동 복귀)
```

**왜 SSO 가 없는가**: lawfirm-demo 와 legal-pro 는 현재 물리적으로 별개의 배포·DB·인증 시스템이다. 통합 인증(SSO) 는 현재 인도 범위 외이며, 향후 요구사항으로 escalation 가능 (CTO → CEO 확인 필요).

---

## 10. 화면 인벤토리 (D3 입력)

| # | 화면 이름 | 라우트 | 상태 변형 | 연결 기능 ID |
|---|---|---|---|---|
| S-01 | 로그인 | `GET/POST /login` | 기본 / 오류(인증실패) / 오류(서버불가) | A-01 |
| S-02 | 홈 | `GET /home` | 도메인 카드 / killer-app 배너(있음/없음) | A-04, F-01 |
| S-03 | 엔티티 목록 | `GET /entities/<type>` | 기본 / 페이징 / 검색 / 오류 | B-01 등 |
| S-04 | 엔티티 상세/수정 | `GET /entities/<type>/<id>` | 조회 / 수정 모드 / 수정 오류 | B-02 등 |
| S-05 | 엔티티 등록 | `GET/POST /entities/<type>/new` | 빈 폼 / 제출 오류(필드 강조) | B-03 등 |
| S-06 | 삭제 확인 | `GET /entities/<type>/<id>/delete` | 확인 전 / 이미 삭제됨 | 공통 |
| S-07 | 삭제 성공 | `POST /entities/<type>/<id>/delete` | 완료 / already_deleted | 공통 |
| S-08 | 에러 | `error.html` | 재시도 가능 / 불가 / 인증 오류 | 공통 |
| S-09 | 법무 판례 검색 | `GET /legal/search` | 검색 전 / 검색 결과 / 0건 | B-09 |
| S-10 | 헬스체크 | `GET /health` | ok / 오류 | N-09 |
| [[S-11]] | 결재자 승인/반려 전용 화면 | 미구현 | — | Q-1 확정 후 구현 여부 결정 |

> `[[ ]]` 는 현재 server.py 에 없는 화면. 구현 여부는 Q-1 CEO·업무담당자 확인 후 결정.

---

## 11. 스크린 레이아웃 패턴

server.py 는 환경변수로 레이아웃 패턴을 엔티티별로 설정한다.

| 패턴 | 환경변수 | 템플릿 | 설명 |
|---|---|---|---|
| 기본 목록 | (기본) | `list.html` | 단순 표 + 상세 링크 |
| 마스터-디테일 | `MASTER_DETAIL_ENTITIES` | `list-master-detail.html` | 좌: 목록, 우: 상세 패널 (htmx 파셜) |
| 상단-하단 | `TOP_BOTTOM_ENTITIES` | `list-top-bottom.html` | 위: 목록, 아래: 상세 패널 |
| 모달 | `MODAL_ENTITIES` | `list-modal.html` | 목록에서 모달로 상세 표시 |

lawfirm-demo 에서 적합한 레이아웃 배정 (CDO 확정 전 제안):
- `legal-case`, `document-document`, `approval-request` → 마스터-디테일 (상세 내용이 많음)
- `legal-case-party`, `legal-case-document`, `approval-step` → 상단-하단 (부모 엔티티와 함께 보기)
- `document-category`, `hr-department` → 기본 목록 (단순 항목)

---

## 부록 A — 기능 ID ↔ 플로우 단계 추적성

| 기능 ID | 기능명 | 등장 시나리오 | 플로우 단계 |
|---|---|---|---|
| A-01 | 세션 로그인 | 전 페르소나 | 공통 진입 → POST /login |
| A-03 | 인증 게이트 | 전 페르소나 | 미인증 접근 → /login 리디렉션 |
| A-04 | 홈 화면 | 전 페르소나 | 로그인 성공 → /home |
| B-01~B-04 | 사건 CRUD | 시나리오 1, 2 | /entities/legal-case 일련 |
| B-05~B-08 | 판례 CRUD | (목록 조회) | /entities/legal-precedent 일련 |
| B-09 | 판례 키워드 검색 | (법무 검색 화면) | /legal/search |
| B-10~B-13 | 당사자 CRUD | 시나리오 1 | /entities/legal-case-party 일련 |
| B-14~B-17 | 사건문서 CRUD | 시나리오 1 | /entities/legal-case-document 일련 |
| C-01~C-04 | 직원 CRUD | (IT 운영) | /entities/hr-employee 일련 |
| C-05~C-08 | 부서 CRUD | (IT 운영) | /entities/hr-department 일련 |
| D-01~D-04 | 문서 CRUD | 시나리오 4 | /entities/document-document 일련 |
| D-05~D-08 | 버전 CRUD | 시나리오 4 | /entities/document-version 일련 |
| D-09~D-12 | 카테고리 CRUD | 시나리오 4 | /entities/document-category 일련 |
| D-13~D-16 | 접근규칙 CRUD | 시나리오 4 | /entities/document-access-rule 일련 |
| E-01~E-04 | 결재요청 CRUD | 시나리오 3 | /entities/approval-request 일련 |
| E-05~E-08 | 결재단계 CRUD | 시나리오 3 | /entities/approval-step 일련 |
| E-09~E-12 | 결재자 CRUD | 시나리오 3 | /entities/approval-approver 일련 |
| E-13~E-16 | 결재결정 CRUD | 시나리오 3 | /entities/approval-decision 일련 |
| F-01~F-03 | killer-app 연동 | 시나리오 2 | 배너·사이드바 → target=_blank |
