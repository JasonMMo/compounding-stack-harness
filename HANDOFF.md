# HANDOFF — 2026-06-11 (context 다이어트 후 /clear 직전 — 복귀 직후 codegraph 수리가 첫 액션)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.

## ▶▶▶ 왜 /clear 했나 + 복귀 직후 상태

context 가 너무 빨리 차서 CEO 가 정리 후 재진입. 이번 세션에서 **고정비 다이어트** 를 했고, 그 효과는 **새 세션부터** 적용된다 (플러그인·MCP 는 세션 시작 시 1회 로드). 즉 지금 막 들어온 이 세션이 다이어트의 첫 수혜 세션이다.

**재시작으로 바뀐 것 (확인용)**: `/context` 치면 이전보다 가벼울 것. 새로 등록된 것: **`security-agent` (CISO)** 가 이제 spawn 목록에 직접 잡힌다 (지난 세션엔 general-purpose 로 우회했음 — 이번엔 `Agent(subagent_type="security-agent", ...)` 직접 호출 가능).

## ▶▶ 복귀 직후 첫 액션 — codegraph 수리

`claude mcp list` 에서 **codegraph 가 연결 실패** (`codegraph serve --mcp` 가 안 뜸). 이 프로젝트가 쓰려고 `.claude/settings.json` permissions 에 codegraph 7종 allow 해둠 (codegraph_search/context/callers/callees/impact/node/status). 코드 검색에 유용하니 살린다.

진단 순서:
1. `claude mcp list` — codegraph 상태 재확인 (✘ Failed to connect 면 진행).
2. `codegraph` 바이너리 존재·PATH 확인 (`where codegraph` / `Get-Command codegraph`). 없으면 설치 필요 (codegraph 가 무엇인지부터 — npm? cargo? 사용자 확인).
3. `codegraph serve --mcp` 수동 실행해 에러 메시지 확인 (인덱스 미생성? 포트? 바이너리 누락?).
4. 흔한 원인: 코드베이스 인덱스 미생성 (`codegraph index` 류 선행 필요) 또는 바이너리 미설치.
5. 고친 뒤 `claude mcp list` 로 ✔ Connected 확인.

## 이번 세션 (06-11 오후) 에 끝낸 것 — 전부 master 푸시 완료

- **Growth-29** — docker compose 실가동 검증 PASS + render.py **subset FK 누출 버그** 픽스 (fresh DB 가 잡음, WSL DB 가 은폐했던 것). cp949 UTF-8 픽스. test_scaffold 27/27.
- **Growth-30** — L2 게이트 재가동: `L2HsqldbSmokeTest.java` 의 seed FK 어긋남 (`cust-001`→`con-001`) 픽스 → **48/48 PASS**. Verification Matrix L2 NOT_SETUP→PASS.
- **Growth-31** — PM loop Step 5 Deliver: `docs/delivery/lawfirm-demo/` 인도 패키지 (README·acceptance AC-1~5·demo-scenario) 조립. profile status draft→active.
- **Growth-32** — **CISO (8번째 인격) 신설** + lawfirm 인도물 첫 보안 리뷰 **PASS** (A5 외부유출 0, SQLi/XSS/시크릿 0, CAVEAT 3건 engineer 해소). `security-agent.md`+`security-loop` skill, charter v1.5, CLAUDE.md §1, `security-checklist.md`. CEO 인터뷰 A5(보안 on-premise)·A6(예산 500만원 초기구축비) profile 반영.
- **context 다이어트** (Growth 미부여 — 인프라 작업):
  - 플러그인 9종 이 프로젝트만 비활성화 (`.claude/settings.json` `enabledPlugins` false): nexacro×2, frontend-design, ui-ux-pro-max, context-engineering, glm-plan-usage, document-skills, claude-hud, superpowers. **되돌리려면 해당 키 true** 또는 행 삭제.
  - MCP 2종 글로벌 제거: `token-savior-recall` (token-optimizer 중복), `gemini` (gemini-cli 중복·연결실패). 되돌리려면 `claude mcp add`.
  - knowledge-sync 훅 메시지 1줄로 단축.

## 현재 상태

- **Milestone**: M3 진행 — legal vertical 인도 직전 (기능 L4 5/5 + 보안 CISO PASS 양 게이트 통과). M2 self-host 온보딩 자산 (env/preflight/compose/security-checklist) 완비.
- **Verification Matrix**: L2 PASS, L4 PASS, 보안리뷰 PASS. L1·L3 NOT_SETUP (개별 테스트는 green).
- **Git**: clean, master 동기화 (HEAD = context 다이어트 커밋).
- **PM loop (lawfirm-demo)**: Step 5 Deliver 완료, **CEO 승인 대기** (delivery sign-off = CEO+PM, 보안·기능 게이트 통과 보고됨). 승인 시 Step 6 Feedback.

## 다음 후보 (우선순위)

1. **codegraph 수리** — ↑ 복귀 직후 첫 액션.
2. **남은 MCP/플러그인 정리 결정** (CEO 판단 대기): Google Drive(미인증), mcp-openai(codex 중복?), zai-mcp-server(이미지분석·이 프로젝트 무관), claude-mem(매 Read observation 노이즈 ↔ 메모리 검색 기능 트레이드오프).
3. **subagent 결과 파일화** — 큰 분석은 결과를 파일로 쓰고 경로만 반환 (이번 세션 보안리뷰 64k 가 메인에 들어온 게 변동비 주범). 작업 방식 변경, CEO 결정 대기.
4. **PM loop lawfirm CEO 승인** → 승인 시 고객 전달 + Step 6 Feedback.
5. **RAG 2단계** (pgvector) / **legal 검색 토큰 인증** (M2, 보안 체크리스트 #4) / **시크릿 커밋 금지 정적 가드** (G-N 후보).

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Fable 5` / master push CTO 자동 (private repo).
- **자격증명 절대 커밋 금지** — `.env` (gitignored).
- 새 agent 정의는 세션 시작 시 로드 — security-agent 는 이번 세션부터 직접 spawn 가능.
- Windows `NUL` 파일 주의: `> /dev/null` 대신 잘못 쓰면 `NUL` 추적 파일 생성됨 → `cmd /c 'del /f /q \\.\<abs path>\NUL'` 로 제거.
- ctx_execute 샌드박스는 bash for-loop·python3 명령에서 깨질 수 있음 (NODE preload 충돌) — python 분석은 `language: python` 직접 사용.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ (실가동 검증됨) / WSL postgres ✓ / codegraph ✗ (수리 대상).
