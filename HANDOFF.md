# HANDOFF — 2026-06-11 (Growth-34: output protocol dogfood 측정 + G-13 가드)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.

## ▶▶▶ 복귀 직후 상태 (확인용)

- **Git**: clean, master 동기화 (HEAD `6d316d1` = Growth-34 cto-ledger).
- **codegraph MCP** ✔ 연결됨 — `mcp__codegraph__*` 8종 사용 가능. 의존 작업 전 `codegraph sync` 권장 (stale 차단).
- **claude-mem 비활성화** — 세션 시작 덤프/Read 힌트 없음. DB 보존, 키 true 로 복구.
- **security-agent (CISO)** 직접 spawn 가능 — `Agent(subagent_type="security-agent", ...)`.
- **context-mode** 활성 — 큰 출력은 `ctx_execute`/`ctx_execute_file`, mutation·git·navigation 만 Bash.
- **가드**: 13개 (G-13 신설), 0 real FAIL (G-2/G-3 SPEC). 실행 시 `PYTHONIOENCODING=utf-8` 권장 (cp949 stdout 의 `└` 인코딩 에러로 rc=1 오탐 방지 — 가드 FAIL 아님).

## ▶▶ 이번 세션에 끝낸 것 — master 푸시 완료

**Growth-34 — Output Protocol dogfood 측정 + G-13 가드 + 인프라 보안 회귀 점검**. Growth-33 규약이 *측정* 없이 주장만 있던 것을, 같은 실패 모드(security-agent)로 재가동해 증명.
- **dogfood 측정**: 보안리뷰 본문 193줄/8KB → `out/analysis/security-infra-review-2026-06-11.md`(gitignored), subagent 내부 58.6k 토큰 격리, **main 반환 = envelope ~10줄**. Growth-32 ~64k 유입 대비 변동비 차단 증명.
- **G-13 신설**: `g13_subagent_output_protocol_wired` — 7 loop SKILL 의 protocol 링크 정적 검사. envelope 크기는 런타임 속성 → wiring 드리프트만 가드. `--check` 후보 G-14 로 재배치.
- **부수 보안**: CAV-1 demo password (M1 stub) / CAV-2 codegraph 1인 메인테이너 (`.npmrc` 버전 핀 권장). 둘 다 informational.
- **§6 회전**: Growth-34 엔트리가 §6 200행 cap 초과 → Growth-13~15 를 `growth-archive.md` 로 회전 (Growth-20 정책). §6 179행.

## 현재 상태

- **Milestone**: M3 진행 — legal vertical. lawfirm-demo 는 **가상 시나리오로 시스템 작동 검증 완료** (실 고객 아님 — PM/CISO/기능 게이트 전 과정 dogfood). M2 self-host 온보딩 자산 완비.
- **Verification Matrix**: L2 PASS, L4 PASS, 보안리뷰 PASS. L1·L3 NOT_SETUP (개별 green). 가드 13개 green.

## 다음 후보 (우선순위)

1. **engineer: `.npmrc` codegraph 버전 핀** (`@colbymchenry/codegraph@0.9.9`) — CISO CAV-2 후속, 공급망 hedge. 작은 작업.
2. **G-14 (`--check` stale-anchor)** — ledger-index stale 앵커 탐지 가드 구현 (오래 밀린 후보).
3. **남은 MCP/플러그인 정리 결정** (CEO 판단): Google Drive(미인증), gemini-cli, zai-mcp-server(이미지·무관).
4. **RAG 2단계** (pgvector) / **legal 검색 토큰 인증** (M2, 보안 체크리스트 #4) / **시크릿 커밋 금지 정적 가드** (G-N 후보).
5. **실 고객 발굴** (M2 게이트) — 지금까지는 가상 시나리오 검증, 매출은 실 고객 라이선스에서 시작.

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Opus 4.8` (트레일러 = 실제 co-author 모델, §9) / master push CTO 자동 (private repo).
- **자격증명 절대 커밋 금지** — `.env` (gitignored).
- 새 agent 정의는 세션 시작 시 로드 — security-agent 직접 spawn 가능.
- Windows `NUL` 파일 주의: `> /dev/null` 오용 시 `NUL` 추적 파일 생성 → `cmd /c 'del /f /q \\.\<abs path>\NUL'`.
- ctx_execute 샌드박스는 bash for-loop·python3 에서 깨질 수 있음 — python 분석은 `language: python` 직접.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ / WSL postgres ✓ / codegraph 0.9.9 ✓ / codex CLI 0.118.0 ✓.
