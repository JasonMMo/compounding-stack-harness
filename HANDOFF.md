# HANDOFF — 2026-06-11 (codegraph 수리 완료 + context 다이어트 2차 — MCP/플러그인 정리 일단락)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.

## ▶▶▶ 복귀 직후 상태 (확인용)

context 다이어트(1차+2차)가 끝났고, 효과는 **새 세션부터** 완전 적용된다 (플러그인·MCP 는 세션 시작 시 1회 로드). `/context` 치면 이전보다 가벼울 것.
- **codegraph MCP 툴**: 연결은 복구됨(✔). in-session 툴 활성화는 **다음 세션부터**. 코드 검색에 `mcp__codegraph__*` 7종 사용 가능 (의존 작업 전 `codegraph sync` 로 그래프 최신화 권장 — stale 리스크 차단).
- **claude-mem 비활성화 효과**: 세션 시작 S### observation 덤프 + 매 Read observation 힌트가 **다음 세션부터 사라짐**. DB(`~/.claude-mem/claude-mem.db` 22.8MB)는 보존, 키 true 로 되돌리기 가능.
- **`security-agent` (CISO)**: spawn 목록에 직접 잡힘 — `Agent(subagent_type="security-agent", ...)` 직접 호출 가능.

## ▶▶ codegraph 수리 — 완료 (✔ Connected)

원인: `@colbymchenry/codegraph` npm global 바이너리가 사라져 `codegraph serve --mcp` 가 못 뜸 (`.mcp.json` 프로젝트 스코프 등록은 정상). 인덱스도 미생성 상태였음.
조치: `npm i -g @colbymchenry/codegraph` 재설치(0.9.9) → `codegraph init .` 로 인덱싱(98파일·1,461노드·2,546엣지·881ms) → `claude mcp list` ✔ Connected 확인.
운영 룰(계승): 큰 변경·세션 재개 후 codegraph 의존 전 `codegraph sync` (또는 `index`). `.codegraph/` 는 gitignore (재생성 가능 로컬 캐시).

## context 다이어트 2차 (이번 세션) — master 푸시 완료

- **mcp-openai 제거** (user scope, `~/.claude.json`): codex CLI 0.118.0 + openai-codex 플러그인 작동 확인 → 중복 OpenAI MCP 제거. 되돌리려면 `claude mcp add`.
- **claude-mem 비활성화** (`.claude/settings.json` `enabledPlugins` `claude-mem@thedotmack: false`, 커밋 `a543f7a`): repo 일급 자산(learn-log/role ledger/wiki/ledger-index/context-mode timeline)과 중복 + context 비용원. DB 보존, 키 true 로 복구.

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
- **Git**: clean, master 동기화 (HEAD `a543f7a` = context 다이어트 2차 — claude-mem 비활성화 커밋).
- **PM loop (lawfirm-demo)**: Step 5 Deliver 완료, **CEO 승인 대기** (delivery sign-off = CEO+PM, 보안·기능 게이트 통과 보고됨). 승인 시 Step 6 Feedback.

## 다음 후보 (우선순위)

1. **PM loop lawfirm CEO 승인** → 승인 시 고객 전달 + Step 6 Feedback. (기능 L4 5/5 + 보안 CISO PASS 양 게이트 통과 보고됨 — 승인만 남음)
2. **subagent 결과 파일화** — 큰 분석은 결과를 파일로 쓰고 경로만 반환 (지난 세션 보안리뷰 64k 가 메인에 들어온 게 변동비 주범). 작업 방식 변경, CEO 결정 대기.
3. **남은 MCP/플러그인 정리 결정** (CEO 판단 대기): Google Drive(미인증), gemini-cli(연결됨·codex/zai 와 역할 겹침?), zai-mcp-server(이미지분석·이 프로젝트 무관). ← mcp-openai·claude-mem 은 이번에 정리됨.
4. **RAG 2단계** (pgvector) / **legal 검색 토큰 인증** (M2, 보안 체크리스트 #4) / **시크릿 커밋 금지 정적 가드** (G-N 후보).

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Fable 5` / master push CTO 자동 (private repo).
- **자격증명 절대 커밋 금지** — `.env` (gitignored).
- 새 agent 정의는 세션 시작 시 로드 — security-agent 는 이번 세션부터 직접 spawn 가능.
- Windows `NUL` 파일 주의: `> /dev/null` 대신 잘못 쓰면 `NUL` 추적 파일 생성됨 → `cmd /c 'del /f /q \\.\<abs path>\NUL'` 로 제거.
- ctx_execute 샌드박스는 bash for-loop·python3 명령에서 깨질 수 있음 (NODE preload 충돌) — python 분석은 `language: python` 직접 사용.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ (실가동 검증됨) / WSL postgres ✓ / codegraph ✓ (0.9.9 재설치·인덱싱·MCP 연결 복구) / codex CLI 0.118.0 ✓.
