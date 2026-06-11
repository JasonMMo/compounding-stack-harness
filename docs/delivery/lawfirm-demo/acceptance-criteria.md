# 인수 기준 대조표 — 법무법인 데모 (lawfirm-demo)

> 인수 기준은 인도 전 확정되었으며, 이 문서는 확정 기준의 검증 결과 증빙입니다.
> 검증일: 2026-06-11 / 환경: Docker Compose PostgreSQL 16 (fresh 기동) / 검증 방식: L4 live 무개입 재현

---

## 인수 기준 대조표

| # | 기준 | 검증 명령 | 결과 | 증빙 (검색어 / 기대값) |
|---|---|---|---|---|
| AC-1 | `q=손해배상` 검색 시 `total` 이 2 이상이며 `citation` 필드가 반환된다 | `GET /api/legal/precedents/search?q=손해배상` | PASS (2026-06-11) | 반환 2건: `대법원 2020다12345`, `서울고등법원 2019나56789` |
| AC-2 | `q=자백` 검색 시 응답 `items` 배열이 1건 이상 반환된다 | `GET /api/legal/precedents/search?q=자백` | PASS (2026-06-11) | 1건 이상 반환 확인 |
| AC-3 | `q=위약금` 검색 시 응답 `items` 배열이 1건 이상 반환된다 | `GET /api/legal/precedents/search?q=위약금` | PASS (2026-06-11) | 1건 이상 반환 확인 |
| AC-4 | `case_type=civil` 필터 적용 시 응답 `items` 의 모든 항목의 `case_type` 값이 `civil` 이다 | `GET /api/legal/precedents/search?q=손해배상&case_type=civil` | PASS (2026-06-11) | 반환 항목 전체 `case_type: civil` 확인 |
| AC-5 | 데이터에 존재하지 않는 검색어 입력 시 `total` 이 0 이고 `items` 가 빈 배열이다 | `GET /api/legal/precedents/search?q=존재하지않는검색어XYZ` | PASS (2026-06-11) | `{"items": [], "total": 0}` 반환 확인 |

---

## 검증 환경 요약

| 항목 | 값 |
|---|---|
| 검증일 | 2026-06-11 |
| DB | PostgreSQL 16 (Docker Compose, postgres:16-alpine) |
| 검색 방식 | tsvector full-text search, 'simple' 사전, GIN 인덱스 |
| 백엔드 | FastAPI (`backend/adapters/fastapi`) |
| 데모 데이터 | `scripts/demo/setup_lawfirm.py` (판례 5건, 사건 3건) |
| 재현 경로 | `scripts/preflight.py` → `docker compose up -d` → `setup_lawfirm.py` → `uvicorn` |

---

## 범위 외 기능 (인수 기준 아님)

아래 기능은 이번 인도 범위에 포함되지 않습니다. 인수 기준으로 사용할 수 없습니다.

- 의미 기반(semantic/RAG) 검색
- 재판 전략 자동 생성
- 판례 전문 열람
- 사용자 인증·권한 관리
