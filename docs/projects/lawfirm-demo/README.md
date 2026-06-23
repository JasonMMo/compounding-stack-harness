# lawfirm-demo 인도 패키지 — 법무법인 4도메인 메인 데모

> 작성: PM (Growth-18). 기준일: 2026-06-23. 이 문서는 D1~D5 및 검증보고서를 묶는 인도 인덱스다.

---

## 1. 이 패키지가 인도하는 것

법무법인 업무를 4도메인으로 통합한 **업무관리 데모 시스템**의 기획·설계 문서 전체. 구현팀이 이 문서 묶음만으로 실제 시스템을 재현할 수 있도록 명세·흐름·화면·데이터구조·데이터흐름을 계층적으로 제공한다.

**커버하는 4도메인**: 사건관리 / 문서관리 / 전자결재 / 판례검색

**스택**: vanilla-htmx + FastAPI (메인 데모), React + Vite (killer-app 크로스링크)

**시드 규모(가명 데이터)**: 부서 5 · 직원 14 · 판례 12 · 사건 10 · 당사자 28 · 사건문서 22 · 문서 카테고리 6 · 문서 10 · 문서버전 14 · 접근규칙 8 · 결재요청 7 · 결재단계 13 · 결재자 14 · 결재결정 10

---

## 2. 대상 독자 (3 페르소나)

| 페르소나 | 주요 관심 문서 | 이 패키지에서 얻는 것 |
|---|---|---|
| **CEO** | D1(기능 범위), D2(사용자 여정) | "어떤 업무를 자동화하는가, 도입 후 어떻게 달라지는가" |
| **업무담당자 (파트너 변호사 / 사무장)** | D2(업무 흐름), D3(화면), D5(데이터 흐름) | "내 일상 업무 절차가 시스템에 어떻게 반영되는가" |
| **IT 담당자** | D4(ERD), D5(DFD), dfd-verification-report | "스키마·인터페이스·검증 결과 — 내부 연동 가능 여부 판단" |

---

## 3. 문서 인덱스

| 파일 | 역할 | 한 줄 요약 |
|---|---|---|
| [D1-functional-spec.md](D1-functional-spec.md) | 기능 명세 | 4도메인 기능 목록 · acceptance criteria · 시드 데이터 범위 정의 |
| [D2-user-flow.md](D2-user-flow.md) | 사용자 흐름 | 페르소나별 주요 업무 시나리오 및 화면 전이 흐름도 |
| [D3-wireframe.md](D3-wireframe.md) | 와이어프레임 | 12개 주요 화면 ASCII 레이아웃 (실제 vanilla-htmx 셸 기준) |
| [D4-erd.md](D4-erd.md) | ERD | 4도메인 통합 Entity-Relationship 다이어그램 + 테이블 정의 |
| [D5-dfd.md](D5-dfd.md) | 데이터 흐름도 | Level 0/1/2 DFD, 8 프로세스, 검증 포인트 34건 · BLK 8건 정의 |
| [dfd-verification-report.md](dfd-verification-report.md) | DFD 정적 검증 보고서 | PASS 35 / FAIL 0 / N-A 9. BLK-D5-8 RESOLVED (2026-06-23) |

---

## 4. 메인 데모 ↔ Killer-App 관계

```
[lawfirm-demo]  ──────────────────────────────────────────
  lawfirm-demo.n9n.co.kr                                  |
  vanilla-htmx / FastAPI / PostgreSQL                      |  "AI 판례검색 ↗" 링크
  4도메인 업무관리 (사건/문서/결재/판례)                  |  (상단 배너 + 좌측 메뉴)
                                                           |
  KILLER_APP_URL 환경변수로 연결 주소 주입 ──────────────▶ [legal-pro]
                                                            legal-rag.n9n.co.kr/pro
                                                            React + Vite / 별도 PostgreSQL
                                                            AI 판례 RAG 검색 (변호사 로그인)
```

**정직성 경계**:
- 두 시스템은 **물리적으로 별개** 배포·DB·로그인이다.
- **SSO 아님** — 메인 데모(demo/demo)와 killer-app은 각각 독립 인증을 사용한다.
- 연결은 단방향 링크(KILLER_APP_URL env)이며, 데이터 공유·API 연동은 현재 없다.
- self-host 환경에서 두 앱 모두 사내망 내 별도 컨테이너로 운영한다.

---

## 5. 라이브 접속 정보

| 항목 | 값 |
|---|---|
| 메인 데모 URL | `lawfirm-demo.n9n.co.kr` |
| 기본 자격증명 | demo / demo |
| Killer-app URL | `legal-rag.n9n.co.kr/pro` |

**founder 라이브화 잔여 액션** (founder Redeploy 후 검증):

1. demo-portal: lawfirm-demo 카드 링크·설명 갱신 후 Redeploy
2. lawfirm-demo: 4도메인 통합 시드(가명 데이터 전체) 라이브 DB 적용 후 Redeploy
3. 라이브 적용 후 D1 acceptance criteria 항목 및 dfd-verification-report N-A 9건(인증·런타임) 재검증

---

## 6. 구 인도 패키지와의 관계

`docs/delivery/lawfirm-demo/` 에 기존 인도 패키지가 존재한다. 해당 패키지는 **FTS 단독 구버전**(판례검색만, 부서 1 / 직원 3 / 판례 5 / 사건 3 기준)으로 작성되었으며 지금도 유효한 이력 문서다. **이 4도메인 메인 데모 패키지(본 디렉토리)는 구 패키지를 포함·확장하며**, 4도메인 통합·시드 규모 확대·DFD 정적 검증을 추가로 커버한다. 구 패키지 자체는 삭제하지 않고 그 위치에 유지한다.

참조: [구 인도 패키지 README](../../delivery/lawfirm-demo/README.md)

---

## 7. 보안 전제 및 경고

- **self-host · 사내망 격리 전제**: 이 데모는 인터넷 공개 환경이 아닌 사내망 또는 VPN 격리 환경 운영을 전제로 설계되었다.
- **기본 자격증명 반드시 변경**: demo/demo 는 데모 전용 자격증명이다. 실운영 환경 전환 시 반드시 강력한 자격증명으로 교체하고 환경변수(`.env`)로 분리하라.
- **prod 전 필수 조치(founder 확인 대기)**: CAVEAT-A — Traefik 요청 바디 제한 설정. 현재 미적용 상태. 대용량 문서 업로드 시 취약점 존재.
- 보안 상세는 구 패키지의 [security-checklist.md](../../delivery/lawfirm-demo/security-checklist.md) 참조 (FTS 단독 기준이나 기본 원칙은 동일 적용).
