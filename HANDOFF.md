# HANDOFF — 2026-06-11 (Growth-35: DevOps 인격 신설 + 배포 토폴로지 v1)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.

## ▶▶▶ 복귀 직후 상태 (확인용)

- **Git**: clean, master 동기화 (HEAD `af78448` = Growth-35 learn-log).
- **팀**: 9-인격 (DevOps 합류). `Agent(subagent_type="devops-agent", ...)` 직접 spawn 가능.
- **codegraph MCP** ✔ 연결됨 — `mcp__codegraph__*` 8종 사용 가능. 의존 작업 전 `codegraph sync` 권장 (stale 차단).
- **claude-mem 비활성화** — 세션 시작 덤프/Read 힌트 없음. DB 보존, 키 true 로 복구.
- **security-agent (CISO)** 직접 spawn 가능 — `Agent(subagent_type="security-agent", ...)`.
- **context-mode** 활성 — 큰 출력은 `ctx_execute`/`ctx_execute_file`, mutation·git·navigation 만 Bash.
- **가드**: 13개, 0 real FAIL (G-2/G-3 SPEC). G-13 은 이제 8개 loop SKILL 스캔 (devops-loop 포함). 실행 시 `PYTHONIOENCODING=utf-8` 권장 (cp949 stdout 의 `└` 인코딩 에러로 rc=1 오탐 방지 — 가드 FAIL 아님).

## ▶▶ 이번 세션에 끝낸 것 — master 푸시 완료

**Growth-35 — DevOps 인격 신설 (9번째) + 배포 토폴로지 v1**. CEO 가 이 harness 로 숨고/크몽 **건당 500만원 1인 비대면 창업** → 인프라·디지털 자산·CI/CD 담당 인격 신설.
- **핵심 통찰**: **preview 티어 ≠ production 티어**. self-host(M2)가 가치 제안 → 최종물은 고객 인프라. n9n.co.kr/VPS 는 **설득용 preview 전용**.
- **배포 결정**: 고객-facing preview 는 노트북 터널 ✗ (다운 리스크) → **Coolify on Seoul VPS** ($6~12/월) + `*.n9n.co.kr` 와일드카드. 터널은 화면공유 데모 폴백만. 메신저 = 숨고/크몽 채팅 → 카톡채널 (커스텀 ✗).
- **신설 자산**: `devops-agent.md` + `devops-loop/SKILL.md`(출력 규약 wiring) + `docs/architecture/deployment-topology.md` + `infra/registry/`(시크릿 볼트 gitignored) + charter v1.6 + CLAUDE.md §1/INDEX 동기화. 12 파일 개별 커밋.

## 현재 상태

- **Milestone**: M2/M3 — legal vertical + 비대면 창업 인프라 토대. lawfirm-demo 는 **가상 시나리오 검증 완료** (실 고객 아님). preview/production 2-티어 토폴로지 확정 (인프라 미provisioning).
- **Verification Matrix**: L2 PASS, L4 PASS, 보안리뷰 PASS. L1·L3 NOT_SETUP (개별 green). 가드 13개 green.

## 다음 후보 (우선순위)

1. **DevOps: preview 티어 provisioning** — Seoul VPS 발급 + Coolify 설치 + `*.n9n.co.kr` 와일드카드 DNS (`deployment-topology.md` §2 런북). CEO 액션 필요 (VPS 구매·DNS). 첫 인프라 비용 §5 환류.
2. **DevOps: CI/CD v1** — `scaffold.py` → docker build → Coolify preview push 파이프라인 + 레지스트리 첫 엔트리.
3. **engineer: `.npmrc` codegraph 버전 핀** (`@colbymchenry/codegraph@0.9.9`) — CISO CAV-2 후속, 공급망 hedge.
4. **G-14 (`--check` stale-anchor)** — ledger-index stale 앵커 탐지 가드 (오래 밀린 후보).
5. **실 고객 발굴** (M2 게이트) — 숨고/크몽 첫 의뢰. 매출은 실 고객에서 시작.

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Opus 4.8` (트레일러 = 실제 co-author 모델, §9) / master push CTO 자동 (private repo).
- **자격증명 절대 커밋 금지** — `.env` (gitignored).
- 새 agent 정의는 세션 시작 시 로드 — security-agent 직접 spawn 가능.
- Windows `NUL` 파일 주의: `> /dev/null` 오용 시 `NUL` 추적 파일 생성 → `cmd /c 'del /f /q \\.\<abs path>\NUL'`.
- ctx_execute 샌드박스는 bash for-loop·python3 에서 깨질 수 있음 — python 분석은 `language: python` 직접.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ / WSL postgres ✓ / codegraph 0.9.9 ✓ / codex CLI 0.118.0 ✓.
