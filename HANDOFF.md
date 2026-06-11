# HANDOFF — 2026-06-11 (Growth-33: subagent output protocol 확립 — 결과 파일화 규약)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.

## ▶▶▶ 복귀 직후 상태 (확인용)

- **Git**: clean, master 동기화 (HEAD `5462564` = Growth-33 learn-log).
- **codegraph MCP** ✔ 연결됨 — `mcp__codegraph__*` 7종 사용 가능. 의존 작업 전 `codegraph sync` 권장 (stale 차단).
- **claude-mem 비활성화** — 세션 시작 덤프/Read 힌트 없음. DB 보존, 키 true 로 복구.
- **security-agent (CISO)** 직접 spawn 가능 — `Agent(subagent_type="security-agent", ...)`.
- **context-mode** 활성 — 큰 출력은 `ctx_execute`/`ctx_execute_file`, mutation·git·navigation 만 Bash.

## ▶▶ 이번 세션에 끝낸 것 — master 푸시 완료

**Growth-33 — Subagent Output Protocol (결과 파일화)**. Growth-32 보안리뷰 ~64k 토큰 main 유입이 변동비 주범 → subagent→main **반환 경계** 규약 확립.
- 신규 단일 진실: `docs/architecture/subagent-output-protocol.md` (임계 ~30줄/2KB / 위치 3종: `docs/learn-logs/<role>.md`·`docs/delivery/<slug>/<role>-review.md`·`out/analysis/`(gitignored) / envelope 4항: 판정→경로→결정·BLOCK→비용).
- 7 loop SKILL 에 `## 출력 규약` 1줄 환류 (8-인격 기본 적용). CLAUDE.md §11 포인터 (ad-hoc agent 는 CTO spawn prompt 명시).
- 10 커밋 (파일당 별도). context-mode(내부 분석 비용) 와 다른 축 = 반환 비용.

## 현재 상태

- **Milestone**: M3 진행 — legal vertical 인도 직전 (기능 L4 5/5 + 보안 CISO PASS 양 게이트 통과). M2 self-host 온보딩 자산 완비.
- **Verification Matrix**: L2 PASS, L4 PASS, 보안리뷰 PASS. L1·L3 NOT_SETUP (개별 green).
- **PM loop (lawfirm-demo)**: Step 5 Deliver 완료, **CEO 승인 대기** (양 게이트 통과 보고됨, 승인만 남음). 승인 시 Step 6 Feedback.

## 다음 후보 (우선순위)

1. **PM loop lawfirm CEO 승인** → 승인 시 고객 전달 + Step 6 Feedback. (인도 패키지: `docs/delivery/lawfirm-demo/`)
2. **Growth-33 dogfood 측정** — 다음 보안/QA 리뷰가 실제로 envelope 만 반환하는지 확인 (효과 증명). 임계 초과 자동 감지 가드 후보.
3. **남은 MCP/플러그인 정리 결정** (CEO 판단): Google Drive(미인증), gemini-cli, zai-mcp-server(이미지·무관).
4. **RAG 2단계** (pgvector) / **legal 검색 토큰 인증** (M2, 보안 체크리스트 #4) / **시크릿 커밋 금지 정적 가드** (G-N 후보).

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Opus 4.8` (트레일러 = 실제 co-author 모델, §9) / master push CTO 자동 (private repo).
- **자격증명 절대 커밋 금지** — `.env` (gitignored).
- 새 agent 정의는 세션 시작 시 로드 — security-agent 직접 spawn 가능.
- Windows `NUL` 파일 주의: `> /dev/null` 오용 시 `NUL` 추적 파일 생성 → `cmd /c 'del /f /q \\.\<abs path>\NUL'`.
- ctx_execute 샌드박스는 bash for-loop·python3 에서 깨질 수 있음 — python 분석은 `language: python` 직접.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ / WSL postgres ✓ / codegraph 0.9.9 ✓ / codex CLI 0.118.0 ✓.
