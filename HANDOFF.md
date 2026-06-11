# HANDOFF — 2026-06-11 (Windows restart 직전 — docker 설치 완료, compose 실가동 검증이 첫 액션)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.

## ▶▶▶ restart 사유와 복귀 직후 상태

CEO 가 **Docker Desktop 을 설치**하고 Windows 를 재시작함. 재시작으로 사라지는 것:

- **8000 포트의 FastAPI** (background bash 로 띄워둔 것) — 죽음. 필요 시 재기동 (아래 §복귀 절차).
- **WSL postgres** — WSL 배포판 자동 기동 여부에 따라 다름. `python scripts/preflight.py` 가 5432 응답을 알려줌.

재시작 후에도 살아 있는 것:

- **`.env`** (repo root, gitignored) — `DATABASE_URL` 이미 기입됨. 자격증명 재입력 불필요. 형식은 `.env.example` 참조.
- **lawfirm_db 데이터** — WSL postgres 의 디스크에 영속 (1 부서·3 직원·5 판례·3 사건 + GIN 인덱스).
- 코드·문서 전부 — git clean, master 동기화 (HEAD `1ebcff2`).

## ▶▶ 복귀 직후 첫 액션 — docker compose 실가동 검증 (Growth-28 open loop)

Growth-28 에서 `docker-compose.yml` 을 작성했으나 **당시 docker 미설치라 YAML 검증까지만** 수행 (learn-log §Growth-28 "한계" 참조). 이제 docker 가 생겼으니 실가동 1회 검증으로 loop 를 닫는다:

1. `docker --version` / `docker compose version` — 설치 확인.
2. **포트 충돌 판단**: `python scripts/preflight.py` 로 5432 상태 확인.
   - WSL postgres 가 이미 5432 를 점유 중이면 → `.env` 에 `POSTGRES_HOST_PORT=5433` 추가 후 compose 기동, 검증용 `DATABASE_URL` 은 `localhost:5433` 으로.
   - 5432 가 비어 있으면 그대로 기동.
3. `docker compose up -d` → healthcheck green 확인 (`docker compose ps`).
4. compose postgres 의 기본 자격증명은 `.env.example` 의 `POSTGRES_*` 주석 참조 (`.env` 에 미설정 시 user/pass/db = claude/claude/lawfirm_db — **WSL postgres 비밀번호와 다름** 주의).
5. compose DB 에 `python scripts/demo/setup_lawfirm.py` (DATABASE_URL 을 compose 쪽으로 맞춰서) → preflight ALL PASS → L4 검색 1종 스모크 (`손해배상` 2건 기대).
6. PASS 시 learn-log Growth-28 의 "compose 실가동 검증" open loop 닫고 1줄 추가 기록.

검증 후 정리: `docker compose down` (WSL postgres 가 메인이면 compose 는 내려둠. `-v` 붙이면 데이터까지 삭제).

## 이번 세션 (06-11) 에 끝낸 것 — Growth-25 ~ 28 (전부 master 푸시 완료)

- **Growth-25** — legal vertical A안 full-stack (tsvector 판례 검색 + UI + tests). PM loop 첫 시나리오 (30인 법무법인).
- **Growth-26** — **L4 live 5/5 PASS** (손해배상·자백·위약금·case_type 필터·empty). 그 과정에서 **DDL 위상정렬 버그** 발견·픽스: scaffold.py 가 entity 별 `render.py --entity` 를 루프 호출 → 각 subprocess 가 단일 entity 만 보게 되어 cross-entity FK 순서 무력화. 픽스 = `render.py --entities` (복수, comma 구분) 신설 + scaffold `emit_ddl` 단일 호출로 교체. test_scaffold 25/25.
- **Growth-27** — **L4 무개입화 1차**: `.env`/`.env.example` 패턴 + `scripts/preflight.py` (패키지·env·DB·포트·uvicorn 5영역 사전점검, 16체크) + fastapi `main.py`·`setup_lawfirm.py` dotenv 자동 로딩. 배경: Growth-26 에서 CEO 개입 5회 (postgres 설치, 자격증명 2회, DB명, export 구문) — 재발 방지.
- **Growth-28** — **L4 무개입화 마무리**: `docker-compose.yml` (postgres:16-alpine, .env 주입, healthcheck) + preflight 실패 메시지에 복구 명령 내장. ⚠️ 실가동 미검증 (위 첫 액션).

## 현재 상태

- **Milestone**: M3 진행 중 — legal vertical L4 완전 통과 (acceptance criteria 달성). M2 self-host 온보딩 자산 (env/preflight/compose) 확충.
- **Verification Matrix**: L4 live **PASS** (2026-06-11). L1~L3 은 NOT_SETUP (매트릭스상; 개별 테스트는 green).
- **Git**: clean, master 동기화 (HEAD `1ebcff2`).
- **PM loop (lawfirm-demo)**: Step 4 Verify 완료. Step 5 Deliver (데모 패키지) 대기.

## 복귀 절차 (L4 환경 재현 — 이제 무개입 경로)

```
python scripts/preflight.py --profile lawfirm-demo   # 사전점검: 실패 메시지가 곧 복구 명령
# (5432 미응답이면: WSL postgres 기동 또는 docker compose up -d)
python scripts/demo/setup_lawfirm.py                  # 멱등 — 이미 적재돼 있으면 skip 출력
uvicorn main:app --app-dir backend/adapters/fastapi --port 8000   # .env 자동 로딩
# 스모크: GET /api/legal/precedents/search?q=손해배상 → 2건
```

## 다음 후보 (우선순위)

1. **compose 실가동 검증** — ↑ 복귀 직후 첫 액션 (Growth-28 loop 닫기).
2. **PM loop Step 5 (Deliver)** — lawfirm-demo 데모 패키지 (화면 데모 + 사용법 + acceptance criteria 표) 고객 전달 형태로 조립. CEO 지시 대기.
3. **CEO 인터뷰 미답 2문항** — A2 (예산·LLM budget) / A5 (보안·외부망·self-host). lawfirm-demo 시나리오 진행에 필요. **CEO 답변 필요.**
4. **RAG 2단계** (pgvector semantic search) — CTO 설계 → engineer 구현. 착수 지시 필요. 확정 후 `legal-rag-pattern` wiki 작성 (INFERRED→EXTRACTED).

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Fable 5` / master push CTO 자동 (private repo).
- **자격증명은 절대 커밋 금지** — `.env` (gitignored) 에만. 이 파일에도 적지 않음.
- **Bash env var 는 `export`** (CMD `set` 아님) — 다만 dotenv 자동 로딩 후로는 수동 export 자체가 불필요.
- FastAPI 장기 기동은 **Bash `run_in_background`** 사용 (PowerShell Start-Job 은 Running 표시 후 silent 종료 — 06-11 재확인).
- ctx_execute 샌드박스는 localhost 접근 불가 — L4 HTTP 테스트는 PowerShell `Invoke-RestMethod`.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 + gradlew ✓ / **Docker ✓ (06-11 설치, 미검증)** / WSL postgres ✓.
