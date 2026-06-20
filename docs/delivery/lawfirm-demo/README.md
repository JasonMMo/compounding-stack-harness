# 인도 패키지 — 법무법인 데모 (lawfirm-demo)

## 인도 개요

이 패키지는 30인 법무법인을 대상으로 한 AI 판례 검색 시스템 데모의 인도 자산입니다. 변호사가 키워드로 관련 판례를 검색하면 시스템이 PostgreSQL full-text search (tsvector/GIN 인덱스) 를 사용해 판례를 묶어 제시합니다. 재판 전략 수립은 변호사가 담당하며, 시스템은 관련 판례 제시(augment 모드)만 수행합니다.

> **버전 주의**: 이 인도 패키지는 `lawfirm-demo` 프로파일 기반 **tsvector FTS 단독** 경로다. 이후 구현된 라이브 RAG 서비스(`legal-rag.n9n.co.kr`, Growth-93/97)는 **FTS∥ANN→RRF 하이브리드 + 로컬 e5-base 임베딩 + chunk_id 인용**으로 한 단계 진화했다. 통합 제품(사건관리+RAG) 방향은 `docs/projects/legal/` 참조.

---

## 패키지 구성

| 파일 | 설명 |
|---|---|
| `README.md` | 이 문서 — 셋업 가이드·사용법·지원 경로 |
| `acceptance-criteria.md` | 인수 기준 대조표 (L4 live 5종 PASS 증빙) |
| `demo-scenario.md` | 변호사 페르소나 화면 데모 시나리오 |

---

## 보안 주의사항

> **경고** 운영 배포 전 DB 및 앱 기본 자격증명(claude/claude, demo/demo)을 반드시 변경하십시오.

> **경고** API 포트(8000/8081)를 사내망 외부로 노출하지 마십시오. 현재 판례 검색 API는 인증이 없으며 사내망 격리를 전제로 합니다.

상세 운영 보안 체크리스트: [`security-checklist.md`](security-checklist.md)

---

## 5분 셋업 가이드

아래 절차는 2026-06-11 기준 무개입 재현 검증 완료된 경로입니다. 검증되지 않은 단계는 추가하지 않습니다.

### 사전 확인

```
python scripts/preflight.py --profile lawfirm-demo
```

출력된 실패 메시지가 곧 복구 명령입니다. 메시지를 따라 조치 후 다음 단계로 진행합니다.

### 1단계 — DB 기동 (5432 미응답 시)

```
docker compose up -d
```

postgres:16-alpine 컨테이너가 기동됩니다. 기본 자격증명: 사용자 `claude`, 비밀번호 `claude`, DB `lawfirm_db`.

### 2단계 — 데모 데이터 적재

```
python scripts/demo/setup_lawfirm.py
```

docker compose DB 를 사용하는 경우 환경변수를 명시합니다.

bash:

```
DATABASE_URL=postgresql://claude:claude@localhost:5432/lawfirm_db python scripts/demo/setup_lawfirm.py
```

PowerShell:

```
$env:DATABASE_URL='postgresql://claude:claude@localhost:5432/lawfirm_db'; python scripts/demo/setup_lawfirm.py
```

스크립트는 멱등 실행됩니다 (중복 실행 무해). 적재 내용: 부서 1, 직원 3, 판례 5, 사건 3.

### 3단계 — 백엔드 서버 기동

```
uvicorn main:app --app-dir backend/adapters/fastapi --port 8000
```

`.env` 파일이 자동 로딩됩니다. 서버가 정상 기동되면 `http://localhost:8000` 에서 API가 응답합니다.

### 4단계 — 스모크 테스트

```
GET http://localhost:8000/api/legal/precedents/search?q=손해배상
```

응답 예시:

```json
{
  "items": [
    { "citation": "대법원 2020다12345", "court": "대법원", "decided_date": "2020-05-21", "case_type": "civil", ... },
    { "citation": "서울고등법원 2019나56789", "court": "서울고등법원", "decided_date": "2019-11-30", "case_type": "civil", ... }
  ],
  "total": 2
}
```

`total` 이 2 이면 정상입니다.

---

## 검색 화면 사용법

화면: `frontend/adapters/vanilla-htmx/templates/legal_precedent_search.html`

| 기능 | 조작 방법 | 동작 |
|---|---|---|
| 키워드 검색 | 검색어 입력 후 "검색" 버튼 클릭 | holding + keywords 필드 full-text 검색, 최대 10건 반환 |
| 사건 유형 필터 | 드롭다운에서 유형 선택 후 검색 | 민사 / 형사 / 행정 / 가사 / 상사 중 하나로 결과 제한 |
| 빈 결과 처리 | 검색어와 일치하는 판례 없음 | "검색 결과가 없습니다." 문구 표시 |
| 결과 카드 | 검색 결과 목록 | 판례 인용 / 사건 유형 배지 / 법원 / 선고일 / 요지 300자 / 키워드 표시 |

검색어 예시: `손해배상`, `자백`, `위약금`

---

## 지원 문의 경로

- 셋업 오류: `python scripts/preflight.py --profile lawfirm-demo` 출력 메시지 첨부
- 기능 문의: `acceptance-criteria.md` 의 인수 기준 대조표 확인 후 해당 항목 번호와 함께 문의
- 담당: 고객사 담당자 또는 프로젝트 PM
