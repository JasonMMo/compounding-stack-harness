# HANDOFF — 2026-06-11 (Growth-29 완료 — compose 실가동 검증 PASS, 다음은 PM Deliver 또는 CEO 인터뷰)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.

## 현재 상태

- **Growth-29 완료** — Growth-28 open loop (compose 실가동 검증) 닫힘:
  - docker 29.5.3 / compose v5.1.4 설치 확인. `down -v` fresh volume → `up -d` healthy → setup → preflight ALL PASS → L4 스모크 (`손해배상` 2건) **전 과정 무개입 PASS**.
  - 그 과정에서 **subset FK 누출 버그** 발견·픽스: render.py 가 subset 밖 entity (`hr_position`·`crm_contact`) FK 를 inline REFERENCES 로 방출 → fresh DB 에서 CREATE TABLE 연쇄 실패. WSL DB 의 잔존 테이블이 은폐했던 버그. 픽스 + 회귀 테스트 (`TestSubsetFkOmission`) — test_scaffold 27/27.
  - cp949 픽스: preflight.py / setup_lawfirm.py 가 PowerShell 기본 콘솔에서 UnicodeEncodeError 로 죽던 것 → UTF-8 reconfigure.
- **Milestone**: M3 진행 중 (legal vertical L4 PASS). M2 self-host 온보딩 경로 fresh-환경 입증 완료.
- **PM loop (lawfirm-demo)**: Step 4 Verify 완료. Step 5 Deliver 대기.
- **compose 는 내려둠** (`docker compose down`, 볼륨 유지 — lawfirm_db 시드 데이터 잔존). WSL postgres 도 정지 상태일 수 있음 — 어느 쪽이든 `python scripts/preflight.py` 가 알려주고, 실패 메시지가 곧 복구 명령.

## L4 환경 재현 (무개입 경로 — fresh 환경 검증 완료)

```
python scripts/preflight.py --profile lawfirm-demo   # 실패 메시지가 곧 복구 명령
# (5432 미응답이면: docker compose up -d)
python scripts/demo/setup_lawfirm.py                  # 멱등; compose DB 면 DATABASE_URL=postgresql://claude:claude@localhost:5432/lawfirm_db
uvicorn main:app --app-dir backend/adapters/fastapi --port 8000   # .env 자동 로딩
# 스모크: GET /api/legal/precedents/search?q=손해배상 → 2건
```

주의: repo root `.env` 의 `DATABASE_URL` 은 WSL postgres 자격증명. compose DB 를 쓸 때는 위처럼 env var 로 override (claude/claude/lawfirm_db — `.env.example` 의 `POSTGRES_*` 주석 참조).

## 다음 후보 (우선순위)

1. **PM loop Step 5 (Deliver)** — lawfirm-demo 데모 패키지 (화면 데모 + 사용법 + acceptance criteria 표) 고객 전달 형태로 조립. CEO 지시 대기.
2. **CEO 인터뷰 미답 2문항** — A2 (예산·LLM budget) / A5 (보안·외부망·self-host). lawfirm-demo 시나리오 진행에 필요. **CEO 답변 필요.**
3. **RAG 2단계** (pgvector semantic search) — CTO 설계 → engineer 구현. 착수 지시 필요. 확정 후 `legal-rag-pattern` wiki 작성 (INFERRED→EXTRACTED).

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Fable 5` / master push CTO 자동 (private repo).
- **자격증명은 절대 커밋 금지** — `.env` (gitignored) 에만.
- FastAPI 장기 기동은 **Bash `run_in_background`** (PowerShell Start-Job 은 silent 종료 — 06-11 재확인).
- ctx_execute 샌드박스는 localhost 접근 불가 — L4 HTTP 테스트는 PowerShell `Invoke-RestMethod`.
- **uncommitted 주의**: `presets/skills/INDEX.md` + `presets/skills/generic/*.seed.md` 수정분이 세션 시작 전부터 working tree 에 있음 (이번 작업과 무관) — 출처 확인 후 커밋/폐기 판단 필요.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 + gradlew ✓ / **Docker ✓ (06-11 설치·실가동 검증 완료)** / WSL postgres ✓.
