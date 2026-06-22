# D1 — 기능명세서 : 법무법인 통합 업무관리 (lawfirm-demo)

> 문서 번호: D1
> owner: PM
> 상태: DRAFT v0.1 (2026-06-23)
> 연관 anchor: `docs/projects/lawfirm-demo/`
> 다운스트림: D2(유저플로우)
> 참고: 이 문서의 시드 데이터는 모두 **가상(가명) 데이터**임. 실존 인물·법인·사건과 무관.

---

## 1. 제품 개요 & 범위

### 1.1 제품 정의

**lawfirm-demo** 는 법무법인 규모 30명의 **통합 업무관리 시스템**이다. 사건관리·인사·문서관리·전자결재의 4개 도메인을 단일 웹 인터페이스로 운영하며, 사내망 self-host 방식으로 소송 데이터 외부 유출을 구조적으로 차단한다.

- **인도 형태**: self-host (사내 서버 Docker 기반 설치)
- **URL**: `lawfirm-demo.n9n.co.kr` (세션 로그인, demo/demo)
- **스택**: vanilla-htmx 프런트 + FastAPI 백엔드 + PostgreSQL
- **killer-app 연동**: AI 판례검색(legal-pro, `legal-rag.n9n.co.kr/pro`) 을 상단 배너·사이드바에서 크로스링크 제공. **물리적으로 별개 앱·별개 DB·별개 로그인** (SSO 없음, 진입점만 제공).

### 1.2 범위 — In Scope

| 도메인 | 포함 기능 |
|---|---|
| **법무 (legal)** | 사건 CRUD, 판례 조회, 당사자 관리, 사건문서 관리 |
| **인사 (hr)** | 직원 목록/상세/등록, 부서 관리 |
| **문서관리 (document)** | 문서 목록/상세/등록/삭제, 버전 이력, 카테고리 관리, 접근규칙 |
| **전자결재 (approval)** | 결재요청 목록/상세/등록, 결재단계 관리, 결재자 지정, 결재결정 기록 |
| **공통** | 세션 로그인/로그아웃, 홈 화면 도메인 카드, 에러 화면, killer-app 진입 링크 |

### 1.3 범위 — Out of Scope

| 제외 항목 | 이유 |
|---|---|
| AI 판례 RAG 검색 (생성형) | legal-pro 앱 영역. lawfirm-demo 는 진입 링크만 제공 |
| SSO 통합 (lawfirm-demo ↔ legal-pro) | 물리적 별개 앱. 별도 로그인 필요 — 정직 표기 |
| 외부 클라우드 API 호출 (임베딩·LLM) | 소송 데이터 외부 유출 금지 (보안 정책 A5) |
| 재판 전략 자동 생성 | legal-pro Pro 티어 로드맵. 현 인도 범위 외 |
| 멀티테넌트 SaaS 모드 | M5 게이트 조건 미충족. self-host 단독 |
| 모바일 전용 앱 | 브라우저 반응형 웹 제공 — 네이티브 앱 별도 |

---

## 2. 페르소나별 가치

### 2.1 CEO (대표 변호사·파트너)

**목표**: 전사 사건 현황 파악, 데이터 유출 제로 확인, 직원 생산성 향상 투자 타당성 판단.

| 요건 | 설명 |
|---|---|
| 사건 현황 일람 | 10개 사건의 상태(active/trial/closed/appeal/intake)·담당 변호사·다음 기일 파악 |
| 데이터 외부 전송 없음 증빙 | 소송 데이터가 사내망 밖으로 나가지 않음을 설치 런북으로 확인 |
| 결재 라인 투명성 | 다단계 결재(팀장→파트너→대표) 흐름과 현재 단계 상태를 한 화면에서 파악 |
| 인도물 패키지 | 기능명세서(이 문서) + D2 유저플로우를 영업 자료로 활용 가능 |

### 2.2 업무담당자 (어소시에이트 변호사·사무장)

**목표**: 사건별 당사자·문서 관리, 결재 상신, AI 판례검색으로 실무 생산성 향상.

| 요건 | 설명 |
|---|---|
| 사건 등록·수정 | CASE-2024-004 "이혼 및 재산분할 청구 사건" 처럼 사건번호·법원·기일·담당 변호사를 시스템에 입력 |
| 당사자 관리 | 원고·피고·증인·상대방대리인 역할 구분, 사건별 다중 당사자 등록 |
| 사건문서 첨부 | 소장·준비서면·증거·계약서 등 문서 유형별 파일 등록, 색인 상태 확인 |
| 결재 상신 | 연차신청·출장비·계약체결 등 유형별 결재요청을 단계 지정 후 상신 |
| killer-app 진입 | 사건 검토 중 AI 판례검색이 필요하면 상단 배너에서 클릭 → legal-pro 별도 탭 |

### 2.3 IT 담당자

**목표**: 사내망 설치·운영, 시크릿 관리, 접근 권한 설정.

| 요건 | 설명 |
|---|---|
| Self-host 완전 설치 | Docker 기반. 외부 클라우드 의존 없음. 사내망 단독 운영 |
| 세션 인증 관리 | demo/demo 세션 로그인. 30명 규모. SSO 불필요 |
| 문서 접근규칙 설정 | 부서/직원 단위로 read/edit/admin 권한을 문서별 설정 |
| 보안 환경변수 관리 | `SECRET_KEY` 등 시크릿을 환경변수로 주입 (평문 파일 미보관) |
| 헬스체크 | `GET /health` 로 서비스 상태 확인 |

---

## 3. 기능 목록

> 각 기능에 실제 시드 데이터 예시를 인용한다. 모든 인명·법인명은 가상 데이터임.

### 모듈 A — 인증·세션

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| A-01 | 세션 로그인 | 사용자명+비밀번호 제출 → 세션 토큰 발급. 인증 실패 시 401 + 한국어 오류 메시지 | `GET/POST /login` | 전 페르소나 |
| A-02 | 로그아웃 | 세션 토큰 폐기, 백엔드 logout 호출 후 로그인 화면 이동 | `POST /logout` | 전 페르소나 |
| A-03 | 인증 게이트 | 미인증 상태에서 보호 라우트 접근 시 로그인 화면으로 리디렉션 | 미들웨어 | 시스템 |
| A-04 | 홈 화면 | 로그인 후 도메인 카드(법무/인사/문서/결재) + killer-app 진입 배너 표시 | `GET /home` | 전 페르소나 |

**시드 데이터 예시**: `demo/demo` 계정으로 로그인하면 "법무법인 데모" 홈 화면이 렌더링되고, 상단 배너에 "AI 판례검색" 크로스링크가 표시된다.

### 모듈 B — 법무 도메인 (legal)

#### B-1. 사건 관리 (legal-case)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| B-01 | 사건 목록 조회 | 사건 목록 표시. 오프셋 페이징, 정렬, 검색 지원 | `GET /entities/legal-case` | 업무담당자·CEO |
| B-02 | 사건 상세 조회/수정 | 사건번호·제목·유형·상태·법원·기일·담당 변호사·요약 조회 및 PATCH 수정 | `GET /entities/legal-case/<id>` `POST /entities/legal-case/<id>/edit` | 업무담당자 |
| B-03 | 사건 등록 | 신규 사건 등록 폼. 사건번호·제목·유형·접수일 필수 | `GET/POST /entities/legal-case/new` | 업무담당자 |
| B-04 | 사건 삭제 확인 | 2단계 확인 후 삭제. 법적 보관 요건이 있으면 논리 삭제 권고 | `GET/POST /entities/legal-case/<id>/delete` | 업무담당자 |

**시드 데이터 예시**:
- CASE-2024-004 "이혼 및 재산분할 청구 사건" (가사, trial, 서울가정법원, 담당: 임도현, 다음 기일 2026-07-10)
- CASE-2025-002 "하도급 단가 인하 손해배상" (민사, closed, 부산지방법원 — 항소심 원고 일부 승소 확정)

#### B-2. 판례 관리 (legal-precedent)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| B-05 | 판례 목록 조회 | 판례 목록. 인용번호·법원·선고일·사건유형·판시요지 표시 | `GET /entities/legal-precedent` | 업무담당자 |
| B-06 | 판례 상세 조회/수정 | 판시요지·키워드·full_text 조회 및 수정 | `GET /entities/legal-precedent/<id>` `POST /entities/legal-precedent/<id>/edit` | 업무담당자 |
| B-07 | 판례 등록 | 인용번호·법원·선고일·사건유형·판시요지 입력 | `GET/POST /entities/legal-precedent/new` | 업무담당자 |
| B-08 | 판례 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/legal-precedent/<id>/delete` | 업무담당자 |
| B-09 | 키워드 전문 검색 (법무 화면) | `/legal/search` — 키워드 기반 판례 검색 화면 (htmx → 백엔드 full-text search). killer-app 과 다른 간이 검색. | `GET /legal/search` | 업무담당자 |

**시드 데이터 예시**:
- 대법원 2022므5678 "이혼 소송에서 유책 배우자의 청구는 원칙적으로 허용되지 않으나, 혼인 관계가 객관적으로 완전히 파탄된 경우 예외적으로 허용될 수 있다." (가사, 키워드: 이혼 유책배우자 혼인파탄)
- 대법원 2023도8821 업무상 횡령 불법영득의사 판례 (형사, 2023-04-27)

#### B-3. 당사자 관리 (legal-case-party)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| B-10 | 당사자 목록 조회 | 사건별 당사자 목록. 역할(원고/피고/증인/상대방대리인/감정인) 표시 | `GET /entities/legal-case-party` | 업무담당자 |
| B-11 | 당사자 상세 조회/수정 | 이름·역할·사건 연결·비고 조회 및 수정 | `GET /entities/legal-case-party/<id>` `POST /entities/legal-case-party/<id>/edit` | 업무담당자 |
| B-12 | 당사자 등록 | 사건ID·역할·이름 입력으로 신규 당사자 추가 | `GET/POST /entities/legal-case-party/new` | 업무담당자 |
| B-13 | 당사자 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/legal-case-party/<id>/delete` | 업무담당자 |

**시드 데이터 예시**:
- C5(업무상 횡령): 원고 "주식회사 미래테크"(피해 법인), 피고 "유창호"(전 재무이사), 감정인 "공인회계사 나인규"(회계감정인)
- C7(이중매매): 원고 "송민준"(제1매수인), 피고 "양재호"(매도인), 피고 "구은서"(제2매수인) — 같은 사건에 피고가 2명

#### B-4. 사건문서 관리 (legal-case-document)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| B-14 | 사건문서 목록 조회 | 사건문서 목록. 문서 유형·제목·제출일·색인 상태(done/pending/error) 표시 | `GET /entities/legal-case-document` | 업무담당자·IT담당자 |
| B-15 | 사건문서 상세 조회/수정 | 문서 유형·제목·제출일·저장 경로·색인 상태 조회 및 수정 | `GET /entities/legal-case-document/<id>` `POST /entities/legal-case-document/<id>/edit` | 업무담당자 |
| B-16 | 사건문서 등록 | 사건ID·문서유형·제목·파일 경로 입력으로 신규 문서 등록 | `GET/POST /entities/legal-case-document/new` | 업무담당자 |
| B-17 | 사건문서 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/legal-case-document/<id>/delete` | 업무담당자 |

**시드 데이터 예시**:
- C1(ABC 손해배상): "손해배상 청구 소장" (complaint, done), "원고 준비서면 제1호" (brief, done), "공급계약서 사본" (evidence, pending — 색인 대기)
- C3(행정처분 취소): "처분 통지서 사본" (court-order, error — 색인 실패)

### 모듈 C — 인사 도메인 (hr)

#### C-1. 직원 관리 (hr-employee)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| C-01 | 직원 목록 조회 | 직원 목록. 사번·이름·부서·입사일·상태 표시. 페이징·검색 지원 | `GET /entities/hr-employee` | CEO·IT담당자 |
| C-02 | 직원 상세 조회/수정 | 사번·이름·부서·직급·입사일·상태 조회 및 수정 | `GET /entities/hr-employee/<id>` `POST /entities/hr-employee/<id>/edit` | CEO |
| C-03 | 직원 등록 | 사번·이름·부서·입사일 입력으로 신규 등록 | `GET/POST /entities/hr-employee/new` | IT담당자 |
| C-04 | 직원 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/hr-employee/<id>/delete` | IT담당자 |

**시드 데이터 예시**:
- EMP001 김대호 (소송부, 파트너변호사, 입사 2010년대)
- EMP004 최준혁 (송무2팀, 2013-06-01 입사)
- EMP014 권현우 (지원팀, on-leave 상태)

#### C-2. 부서 관리 (hr-department)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| C-05 | 부서 목록 조회 | 부서 목록. 부서코드·이름·관리자 표시 | `GET /entities/hr-department` | CEO·IT담당자 |
| C-06 | 부서 상세 조회/수정 | 부서코드·이름·상위부서·관리자 조회 및 수정 | `GET /entities/hr-department/<id>` `POST /entities/hr-department/<id>/edit` | IT담당자 |
| C-07 | 부서 등록 | 부서코드·이름 입력 | `GET/POST /entities/hr-department/new` | IT담당자 |
| C-08 | 부서 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/hr-department/<id>/delete` | IT담당자 |

**시드 데이터 예시**: 소송부(LAW001, 관리자: EMP001 김대호), 송무2팀(LAW002, 관리자: 최준혁), 기업자문팀(LAW003, 관리자: 강민서), 가사·형사팀(LAW004, 관리자: 임도현), 지원팀(SUP001, 관리자: 배지수) 총 5개 부서.

### 모듈 D — 문서관리 도메인 (document)

#### D-1. 문서 관리 (document-document)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| D-01 | 문서 목록 조회 | 문서 목록. 제목·카테고리·소유자·상태(published/draft/archived) 표시 | `GET /entities/document-document` | 전 페르소나 |
| D-02 | 문서 상세 조회/수정 | 제목·카테고리·소유자·상태·현행 버전·보관기한 조회 및 수정 | `GET /entities/document-document/<id>` `POST /entities/document-document/<id>/edit` | 업무담당자 |
| D-03 | 문서 등록 | 제목·카테고리·소유자·상태 입력 | `GET/POST /entities/document-document/new` | 업무담당자 |
| D-04 | 문서 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/document-document/<id>/delete` | 업무담당자 |

**시드 데이터 예시**:
- "법인 정관" (내부규정, 소유자: 배지수, published, 현행버전 v2.0, 보관기한 2035-01-01)
- "2025년 예산안" (회계서류, 소유자: 문채린, archived — 이력 보관)
- "준비서면 작성 가이드" (서식·템플릿, 소유자: 김대호, draft — 미완성)

#### D-2. 문서 버전 관리 (document-version)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| D-05 | 버전 목록 조회 | 문서별 버전 이력. 버전번호·업로더·파일명·공개 여부 표시 | `GET /entities/document-version` | 업무담당자 |
| D-06 | 버전 상세 조회/수정 | 버전번호·파일 크기·MIME·체크섬·공개 여부 조회 및 수정 | `GET /entities/document-version/<id>` `POST /entities/document-version/<id>/edit` | 업무담당자 |
| D-07 | 버전 등록 | 문서ID·버전번호·파일 정보 입력으로 신규 버전 추가 | `GET/POST /entities/document-version/new` | 업무담당자 |
| D-08 | 버전 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/document-version/<id>/delete` | 업무담당자 |

**시드 데이터 예시**:
- 법인 정관: v1.0(비공개, 204KB, 배지수 업로드) → v2.0(공개, 210KB, 배지수 업로드). 현행 버전은 v2.0.
- 법률자문 표준 위임계약서: v1.0 → v2.0 (강민서 업로드, docx 형식)

#### D-3. 카테고리 관리 (document-category)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| D-09 | 카테고리 목록 조회 | 카테고리 목록. 코드·이름·기본 보관기간 표시 | `GET /entities/document-category` | IT담당자 |
| D-10 | 카테고리 상세 조회/수정 | 코드·이름·상위 카테고리·보관기간 조회 및 수정 | `GET /entities/document-category/<id>` `POST /entities/document-category/<id>/edit` | IT담당자 |
| D-11 | 카테고리 등록 | 코드·이름·보관기간 입력 | `GET/POST /entities/document-category/new` | IT담당자 |
| D-12 | 카테고리 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/document-category/<id>/delete` | IT담당자 |

**시드 데이터 예시**: 소송서류(CAT-LAWSUIT, 10년), 계약서(CAT-CONTRACT, 10년), 내부규정(CAT-INTERNAL, 5년), 인사서류(CAT-HR, 10년), 회계서류(CAT-FINANCE, 7년), 서식·템플릿(CAT-TEMPLATE, 1년).

#### D-4. 접근규칙 관리 (document-access-rule)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| D-13 | 접근규칙 목록 조회 | 문서별 부서/직원 단위 접근규칙. 권한(read/edit/admin)·만료일 표시 | `GET /entities/document-access-rule` | IT담당자 |
| D-14 | 접근규칙 상세 조회/수정 | 문서ID·주체 유형(부서/직원)·주체ID·권한·만료일 조회 및 수정 | `GET /entities/document-access-rule/<id>` `POST /entities/document-access-rule/<id>/edit` | IT담당자 |
| D-15 | 접근규칙 등록 | 문서·주체·권한·만료일 지정으로 신규 규칙 생성 | `GET/POST /entities/document-access-rule/new` | IT담당자 |
| D-16 | 접근규칙 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/document-access-rule/<id>/delete` | IT담당자 |

**시드 데이터 예시**:
- "법인 정관" → 지원팀(부서) read 권한 (무기한)
- "2025년 예산안" → EMP001 김대호(직원) read 권한 (만료: 2027-01-01 — 한시적 열람)
- "개인정보처리방침" → 지원팀(부서) admin 권한

### 모듈 E — 전자결재 도메인 (approval)

#### E-1. 결재요청 관리 (approval-request)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| E-01 | 결재요청 목록 조회 | 결재요청 목록. 제목·유형·신청자·상태(pending/in-progress/approved/rejected) 표시 | `GET /entities/approval-request` | 전 페르소나 |
| E-02 | 결재요청 상세 조회/수정 | 제목·유형·신청자·현재 상태·만료일 조회 및 수정 | `GET /entities/approval-request/<id>` `POST /entities/approval-request/<id>/edit` | 업무담당자 |
| E-03 | 결재요청 등록 | 제목·유형·신청 대상·만료일 입력으로 결재 상신 | `GET/POST /entities/approval-request/new` | 업무담당자 |
| E-04 | 결재요청 삭제 | 2단계 확인 후 삭제 (pending 상태만 취소 권장) | `GET/POST /entities/approval-request/<id>/delete` | 업무담당자 |

**시드 데이터 예시**:
- AQ1 "연차휴가 신청 (2024-08-05~06)" — 이수진 신청, approved
- AQ4 "연차휴가 신청 (2024-09-02~06)" — 한소율 신청, rejected (팀장 반려: "재판 일정 충돌로 반려. 일정 조정 후 재신청 바람.")
- AQ5 "SaaS 계약서 의뢰인 외부 발송 승인" — 강민서 신청, in-progress (1단계 승인 완료, 대표변호사 최종 승인 대기 중)
- AQ6 "사무용 복합기 구매 결의 (340만원)" — 배지수 신청, pending (3단계 결재 중 아직 1단계 미통보)

#### E-2. 결재단계 관리 (approval-step)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| E-05 | 결재단계 목록 조회 | 결재요청별 단계 목록. 순서·단계명·상태·전원동의 여부 표시 | `GET /entities/approval-step` | 업무담당자 |
| E-06 | 결재단계 상세 조회/수정 | 단계명·순서·상태 조회 및 수정 | `GET /entities/approval-step/<id>` `POST /entities/approval-step/<id>/edit` | 업무담당자 |
| E-07 | 결재단계 등록 | 결재요청ID·순서·단계명 지정으로 신규 단계 추가 | `GET/POST /entities/approval-step/new` | 업무담당자 |
| E-08 | 결재단계 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/approval-step/<id>/delete` | 업무담당자 |

**시드 데이터 예시**:
- AQ3(IT 서비스 계약 체결): 1단계 "담당파트너 승인"(approved) → 2단계 "대표변호사 최종승인"(approved) — 2단계 완료 승인
- AQ6(복합기 구매): 1단계 "지원팀장 승인"(pending) → 2단계 "재무 확인"(pending) → 3단계 "대표 결재"(pending) — 3단계 대기

#### E-3. 결재자 관리 (approval-approver)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| E-09 | 결재자 목록 조회 | 단계별 결재자 목록. 직원·통보일·응답일 표시 | `GET /entities/approval-approver` | 업무담당자 |
| E-10 | 결재자 상세 조회/수정 | 단계ID·직원ID·통보일·응답일 조회 및 수정 | `GET /entities/approval-approver/<id>` `POST /entities/approval-approver/<id>/edit` | 업무담당자 |
| E-11 | 결재자 등록 | 단계ID·직원ID 지정으로 결재자 추가 | `GET/POST /entities/approval-approver/new` | 업무담당자 |
| E-12 | 결재자 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/approval-approver/<id>/delete` | 업무담당자 |

**시드 데이터 예시**: AQ5 "SaaS 계약서 외부 발송 승인"의 1단계 결재자 강민서(2026-06-21 응답 완료), 2단계 결재자 김대호(2026-06-21 통보, 아직 미응답).

#### E-4. 결재결정 관리 (approval-decision)

| ID | 기능명 | 설명 | 라우트 | 페르소나 |
|---|---|---|---|---|
| E-13 | 결재결정 목록 조회 | 결재 결정 기록 목록. 결정(approved/rejected)·코멘트·결정일 표시 | `GET /entities/approval-decision` | 전 페르소나 |
| E-14 | 결재결정 상세 조회/수정 | 단계·결재자·결정·코멘트 조회 및 수정 | `GET /entities/approval-decision/<id>` `POST /entities/approval-decision/<id>/edit` | CEO |
| E-15 | 결재결정 등록 | 단계ID·결재자ID·결정·코멘트 입력 | `GET/POST /entities/approval-decision/new` | CEO |
| E-16 | 결재결정 삭제 | 2단계 확인 후 삭제 | `GET/POST /entities/approval-decision/<id>/delete` | CEO |

**시드 데이터 예시**:
- AQ1 이수진 연차 → EMP001 김대호: "승인합니다." (2024-07-25)
- AQ4 한소율 연차 → 임도현(팀장): "재판 일정 충돌로 반려. 일정 조정 후 재신청 바람." (2024-08-20, rejected)
- AQ7 ABC 손해배상 위임계약 → 최준혁(2단계): "최종 승인." (2024-01-14)

### 모듈 F — killer-app 연동 (AI 판례검색)

| ID | 기능명 | 설명 | 진입점 | 경계 |
|---|---|---|---|---|
| F-01 | killer-app 배너 | 로그인 후 전 화면 상단 배너에 "AI 판례검색" 링크 표시 (`KILLER_APP_URL` 환경변수로 활성화) | 상단 배너 (모든 인증 화면) | `target=_blank` — 새 탭 |
| F-02 | 사이드바 killer-app 링크 | 사이드바 내비게이션에 killer-app 바로가기 | 사이드바 | `target=_blank` — 새 탭 |
| F-03 | 별도 로그인 안내 | killer-app 은 lawfirm-demo 와 **물리적으로 별개 앱·별개 DB·별개 로그인**. SSO 없음. 진입 후 legal-pro 화면에서 별도 인증 필요. | killer-app 진입 시 화면 안내 | 정직 표기 |

**시드 데이터 예시**: lawfirm-demo 에서 CASE-2024-005 "업무상 횡령 고소 대응 사건" 검토 중 관련 판례가 필요하면 상단 배너 "AI 판례검색" 클릭 → `legal-rag.n9n.co.kr/pro` 새 탭 → 변호사 별도 로그인 → "횡령 불법영득의사" 검색.

---

## 4. 비기능 요건 (NFR)

### 4.1 보안·데이터 격리

| NFR-ID | 요건 | 기준 |
|---|---|---|
| N-01 | 소송 데이터 외부 유출 0 | 모든 처리가 사내 서버 내부에서 실행. 외부 클라우드 API 호출 없음 (보안 정책 A5) |
| N-02 | 세션 인증 | 30명 규모. 세션 쿠키 기반 인증. `SECRET_KEY` 환경변수 필수 |
| N-03 | 미인증 접근 차단 | 모든 보호 라우트는 세션 토큰 없으면 `/login` 리디렉션 |
| N-04 | HTTPS 종단 | Traefik 리버스 프록시 TLS. HTTP → HTTPS 리디렉션 |
| N-05 | 시크릿 환경변수 주입 | `SECRET_KEY` 등 시크릿을 Coolify 볼트 또는 동등 시스템으로 주입. 평문 `.env` 서버 보관 금지 |

### 4.2 Self-Host 운영

| NFR-ID | 요건 | 기준 |
|---|---|---|
| N-06 | 완전 self-host | Docker 기반. 외부 네트워크 의존 없는 사내망 단독 운영 |
| N-07 | DB 요건 | PostgreSQL (tsvector full-text search 지원) |
| N-08 | 멱등 설치 | DDL + seed 재실행 안전 (IF NOT EXISTS, ON CONFLICT DO NOTHING) |
| N-09 | 헬스체크 | `GET /health` 로 서비스 상태 확인 (인증 없음) |

### 4.3 사용성

| NFR-ID | 요건 | 기준 |
|---|---|---|
| N-10 | 브라우저만으로 사용 | 코드 지식 없이 브라우저에서 전 기능 접근 (vanilla-htmx, 서버사이드 렌더링) |
| N-11 | 에러 한국어 표시 | 모든 오류 메시지를 한국어로 표시 (codes.yaml message_ko) |
| N-12 | 삭제 2단계 확인 | 모든 삭제 작업은 확인 화면 거침 (실수 방지) |
| N-13 | 오프셋 페이징 | 목록 화면 기본 20건씩 오프셋 페이징. 정렬·검색 지원 |

---

## 5. 추적성 매트릭스 — 기능 ↔ 라우트 ↔ 엔티티

| 모듈 | 기능 ID 범위 | 엔티티 | 주요 라우트 패턴 |
|---|---|---|---|
| A (인증) | A-01~A-04 | 세션 | `/login`, `/logout`, `/home` |
| B-1 (사건) | B-01~B-04 | legal-case | `/entities/legal-case[/<id>[/edit\|/delete]]`, `/entities/legal-case/new` |
| B-2 (판례) | B-05~B-09 | legal-precedent | `/entities/legal-precedent[/<id>[/edit\|/delete]]`, `/legal/search` |
| B-3 (당사자) | B-10~B-13 | legal-case-party | `/entities/legal-case-party[/<id>[/edit\|/delete]]` |
| B-4 (사건문서) | B-14~B-17 | legal-case-document | `/entities/legal-case-document[/<id>[/edit\|/delete]]` |
| C-1 (직원) | C-01~C-04 | hr-employee | `/entities/hr-employee[/<id>[/edit\|/delete]]` |
| C-2 (부서) | C-05~C-08 | hr-department | `/entities/hr-department[/<id>[/edit\|/delete]]` |
| D-1 (문서) | D-01~D-04 | document-document | `/entities/document-document[/<id>[/edit\|/delete]]` |
| D-2 (버전) | D-05~D-08 | document-version | `/entities/document-version[/<id>[/edit\|/delete]]` |
| D-3 (카테고리) | D-09~D-12 | document-category | `/entities/document-category[/<id>[/edit\|/delete]]` |
| D-4 (접근규칙) | D-13~D-16 | document-access-rule | `/entities/document-access-rule[/<id>[/edit\|/delete]]` |
| E-1 (결재요청) | E-01~E-04 | approval-request | `/entities/approval-request[/<id>[/edit\|/delete]]` |
| E-2 (결재단계) | E-05~E-08 | approval-step | `/entities/approval-step[/<id>[/edit\|/delete]]` |
| E-3 (결재자) | E-09~E-12 | approval-approver | `/entities/approval-approver[/<id>[/edit\|/delete]]` |
| E-4 (결재결정) | E-13~E-16 | approval-decision | `/entities/approval-decision[/<id>[/edit\|/delete]]` |
| F (killer-app) | F-01~F-03 | — (크로스링크) | 배너·사이드바 → `KILLER_APP_URL` (target=_blank) |

---

## 6. 핵심 가정·결정 기록

| 항목 | 결정 | 근거 |
|---|---|---|
| 단일 통합 데모 | 4개 도메인을 한 시스템으로 | 법무법인 업무 전반을 단일 UI로 시연 |
| killer-app 별도 앱 | SSO 없이 진입 링크만 제공 | 물리적 별개 배포. 정직 표기 원칙 |
| 세션 인증 | 30명 규모, SSO 불필요 | profile auth.method=session |
| 소송 데이터 self-host 필수 | 외부 유출 0 | 보안 정책 A5 (고객 요건) |
| CRUD 전 화면 제공 | 목록/상세/등록/삭제 4종 | 실제 server.py 라우트 구현 기준 |
| 2단계 삭제 확인 | `delete_confirm.html` + `delete_success.html` | 접근성 가이드라인 — 파괴적 작업 확인 필수 |
| 판례 간이검색 별도 | `/legal/search` 화면 존재 | server.py `legal_search()` 라우트 실존. killer-app 의 RAG 검색과 다른 단순 키워드 검색 |

---

## 7. 열린 질문

| # | 질문 | owner | 우선순위 |
|---|---|---|---|
| Q-1 | 결재 워크플로우에서 결재자가 브라우저로 직접 결정(승인/반려)을 입력하는 화면이 필요한가, 아니면 관리자가 결재결정을 대리 입력하는 방식으로 충분한가? | PM → 업무담당자 | 높음 |
| Q-2 | 사건문서 색인 상태(pending→done) 폴링 UI 가 필요한가? (legal-pro 처럼 실시간 상태 갱신) | PM → IT담당자 | 중간 |
| Q-3 | 접근규칙은 현재 데이터 레코드(principal_type/principal_id/permission)만 관리하며, 실제 파일 접근 제어 로직은 백엔드에서 별도 구현 필요. 이번 인도 범위인가? | PM → CTO | 중간 |
| Q-4 | 문서 버전 등록 시 실제 파일 업로드(multipart)가 필요한가, 아니면 파일 경로(storage_key) 입력만으로 충분한가? | PM → 업무담당자 | 중간 |

---

## 부록 A — 엔티티 목록 (4도메인 16엔티티)

| 도메인 | 엔티티 | 테이블 | 시드 건수 |
|---|---|---|---|
| legal | 사건 | legal_case | 10 |
| legal | 판례 | legal_precedent | 12 |
| legal | 당사자 | legal_case_party | 28 |
| legal | 사건문서 | legal_case_document | 22 |
| hr | 직원 | hr_employee | 14 |
| hr | 부서 | hr_department | 5 |
| document | 문서 | document_document | 10 |
| document | 버전 | document_version | 14 |
| document | 카테고리 | document_category | 6 |
| document | 접근규칙 | document_access_rule | 8 |
| approval | 결재요청 | approval_request | 7 |
| approval | 결재단계 | approval_step | 13 |
| approval | 결재자 | approval_approver | 14 |
| approval | 결재결정 | approval_decision | 10 |

> 시드 데이터 출처: `scripts/demo/seed_lawfirm_full.py` (가상 데이터, 가명 처리)
