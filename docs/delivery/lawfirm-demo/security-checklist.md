# self-host 보안 체크리스트 — 법무법인 데모

이 체크리스트는 인도받은 시스템을 운영 환경에 안전하게 배포하기 위한 확인 항목입니다. 인도 후 첫 운영 기동 전, 각 항목을 순서대로 확인하고 완료 여부를 표시하십시오.

---

| # | 항목 | 조치 방법 | 완료 기준 |
|---|---|---|---|
| 1 | DB 기본 자격증명 변경 | `.env` 에서 POSTGRES_USER/POSTGRES_PASSWORD 를 claude/claude 이외 값으로 설정, DATABASE_URL 동기화 | `docker compose up -d` 재기동 후 새 자격증명으로만 접속 |
| 2 | 앱 데모 계정 비밀번호 변경 | `backend/adapters/fastapi/routers/auth.py` 의 _DEMO_USERS 를 환경변수/외부설정으로 교체 (M2 작업) | demo/demo 로그인 불가 |
| 3 | 포트 사내망 격리 | 방화벽/Docker 네트워크로 8000·8081 을 사내망 IP 대역으로만 제한 | 외부 IP 에서 검색 API 응답 없음 |
| 4 | API 인증 활성화 | 판례 검색 엔드포인트에 토큰 인증 적용 (M2 roadmap). 현재 미적용 — 사내망 격리로 보완 | Authorization 없이 401 |
| 5 | .env Git 미추적 확인 | `git ls-files .env` 출력 없음 확인 | 출력 없음 |
| 6 | 에러 응답 정보 누출 차단 | (C2 로 이미 적용됨 — 인도 코드에 반영) | 500 응답 body 에 DB 내부 정보 없음 |
| 7 | 서버 바인딩 제한 | 운영 시 `--host 127.0.0.1` 또는 reverse proxy(nginx) 앞단 배치 | 외부 인터페이스 직접 접근 불가 |
