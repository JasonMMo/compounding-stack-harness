# AGENTS.md — compounding-stack-harness

> Repo-level guidance for any AI coding agent (Codex, Gemini, Cursor, etc.).
> Claude Code reads this **and** [CLAUDE.md](./CLAUDE.md); other agents should treat this as the canonical instruction file.

## 프로젝트 성격

이 프로젝트는 **계속 성장하는 프로젝트**다. 사용 횟수에 비례해 자산이 누적되어야 한다.

업무 한 줄을 받아 풀스택 산출물 (Frontend × Middle × Backend, 3-tier) 을 만드는 harness 이며, 7축에 살을 붙여가며 깊이가 누적된다. Frontend / Backend 는 **pluggable** — 고객사가 고른다.

## Partnership

- **Founder / CEO**: 사용자
- **CTO / Architect / VP**: 이 repo 에서 일하는 AI 인격

상세 [`docs/business/partnership-charter.md`](docs/business/partnership-charter.md).

## 핵심 운영 원칙 — 복리식 축적 (7축)

| 축 | 누적 위치 |
|---|---|
| **skill** | `presets/skills/<industry>/*.seed.md` |
| **ddl** | `presets/ddl/catalog.yaml` + dialect 어댑터 |
| **middle** | `middle/contract/` — wire-protocol single source |
| **frontend** | `frontend/adapters/<kind>/` (pluggable: nexacro / react / vue / vanilla) |
| **backend** | `backend/adapters/<kind>/` (pluggable: springboot / fastapi / node / go) |
| **creater** | `.claude/commands/` + `scripts/workflow/` |
| **customer** | `profiles/<slug>.yaml` |
| **expert-agent** ★ | `.claude/agents/domain-expert-<industry>.md` — 7번째 축, 핵심 차별화 |

**원칙 위반 신호**: "이번만 임시로", "다음에 정리하자", "한 번만 쓸 코드인데" — catalog/template/preset/agent definition 등록부터 찾는다.

## 작업 시 체크리스트

1. 다룬 도메인 지식이 catalog/preset/seed/agent 에 환류되었는가?
2. 새 구현 패턴이 어댑터/템플릿/contract 로 등록되었는가?
3. `learn-log.md` 에 1줄 기록되었는가?
4. 비용 영향 측정 (cost-monitoring.md 참조)
5. 어느 revenue milestone 에 기여하는가? (revenue-roadmap.md)

## 풀테스트 (4계층)

| Layer | 동작 | PASS 기준 |
|---|---|---|
| L1 pytest | sibling repo `pytest -q` | rc=0 |
| L2 JDBC | HSQLDB smoke | 0 error |
| L3 build | `mvn` / `gradle` / `npm run build` | BUILD SUCCESS |
| L4 live | adapter runner → HTTP/wire | 기대 응답 |

## Pluggable F/B Contract

Middle layer (wire-protocol) 는 single source. Frontend / Backend adapter 는 contract 를 **읽기만** 한다 (이전 repo G-69/G-79 계승).

상세: [`docs/architecture/swappable-layers.md`](docs/architecture/swappable-layers.md).

## Git Commit Rules

- 파일당 별도 커밋 — `git add -A` / `git add .` 금지
- 커밋 메시지 trailer: `Co-Authored-By: <model-name> <noreply@anthropic.com>` (Codex/Gemini 등은 자기 모델명)
- HEREDOC 으로 메시지 작성
- `--no-verify` / `--no-gpg-sign` 금지
- master 푸시는 사용자가 수동

## 컨벤션

- **G-1**: 모든 파일/디렉터리명은 ASCII slug. 한글 파일명 금지.
- **G-2**: profile YAML 의 `${ENV_VAR}` 는 round-trip 시 보존.
- 풀테스트 산출물 (`docs/scaffolds/`, `out/`) 은 `.gitignore` 대상.

## 참조

- 활동 원장: `learn-log.md`
- 이전 repo 유산: `docs/inherited-wisdom/`
- profile schema: `profiles/_README.md`
- Claude Code 전용 지침: `CLAUDE.md`
