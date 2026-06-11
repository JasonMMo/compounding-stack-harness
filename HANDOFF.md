# HANDOFF — 2026-06-11 (Growth-35: DevOps 인격 + preview 티어 live + scaffold→preview v1)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.
> **다음 작업 = Coolify Phase 2** (아래 ▣ 섹션부터 바로 시작).

## ▶▶▶ 복귀 직후 상태 (확인용)

- **Git**: clean, master 동기화 (HEAD = scaffold→preview v1 기록 커밋).
- **팀**: 9-인격 (DevOps 합류). `Agent(subagent_type="devops-agent"|"engineer-agent"|"security-agent", ...)` 직접 spawn 가능.
- **★ preview VPS LIVE**: Hostinger KVM 2 `187.77.140.157` (싱가포르, $8.99/월 24mo). SSH `ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157` (키 인증만). Coolify 4.1.2 healthy (server uuid `n12vdydjpwp81hu5i15n1gsb`). `*.n9n.co.kr` 자동 HTTPS·**Coolify API CI/CD end-to-end 검증 완료**. **8000/8080/6001/6002 클라우드 방화벽 차단(allow 22/80/443) — CISO 잔여 0.** 대시보드는 SSH `-L 8000:localhost:8000` 터널.
- **Coolify API 토큰**: `infra/secrets/preview-vps.env` (raw 값, gitignored, write+deploy 스코프). `sed -E 's/^COOLIFY_API_TOKEN=//' | tr -d ' \t\r\n'` 로 읽고 `${#TOKEN}` 길이만 확인 — **내용 절대 비출력**(`cat`/`cut`/`xxd`/`source` 금지, 빈 값이면 `wc -c`·존재확인만 후 CEO에 문의). 사용은 SSH→localhost:8000 으로만.
- **codegraph MCP** ✔ — `mcp__codegraph__*`. 의존 작업 전 `codegraph sync` 권장.
- **context-mode** 활성 — 큰 출력은 `ctx_execute`/`ctx_execute_file`, mutation·git·navigation 만 Bash.
- **가드**: 13개, 0 real FAIL (G-2/G-3 SPEC). 실행 시 `PYTHONIOENCODING=utf-8` 권장.

## ▶▶ 이번 세션(Growth-35)에 끝낸 것 — master 푸시 완료

CEO 가 이 harness 로 숨고/크몽 **건당 500만원 1인 비대면 창업** → DevOps 인격 신설 + preview 인프라 전 구간 구축.
- **DevOps 인격(9번째) 신설**: `devops-agent.md` + `devops-loop/SKILL.md` + charter v1.6 + `infra/registry/`·`infra/secrets/`(볼트 gitignored).
- **핵심 통찰**: **preview 티어 ≠ production 티어**. self-host(M2)=가치 제안 → 최종물은 고객 인프라, n9n.co.kr/VPS 는 설득용 preview 전용.
- **provisioning**: Hostinger KVM2 싱가포르 + Coolify + `*.n9n.co.kr`(Cloudflare grey) + LE 자동 TLS 검증 + SSH 키전용·커널패치.
- **CI/CD v1**: Coolify API(write+deploy) 프로젝트→dockerimage 앱→instant_deploy→외부 HTTPS 200 + LE 인증서 검증 후 정리(잔여 0). 레시피=`deployment-topology.md §4`.
- **하드닝**: 8000 admin UI 등 클라우드 방화벽 차단(allow 22/80/443) 실측 → CISO 잔여 0.
- **scaffold→preview v1 (engineer 위임)**: `preview_package.py`+Dockerfile×2+`.dockerignore` → **DB 없는 2-container compose**(백엔드 in-memory store). lawfirm-demo 로컬 `/login`·`/health` 200, manifest 14ent 검증.
- **보안 사고 2회**(토큰 source·cut 노출) → raw-file 시크릿 규약 hardening (노출 2토큰 CEO 폐기 완료).

## ▣ 다음 작업 — Coolify Phase 2 (로컬 preview → 서버 배포)

**목표**: `preview_package.py` 로 로컬 검증된 2-container preview 를 **`<slug>.n9n.co.kr` 로 실제 배포**. profile 한 줄 → 외부 HTTPS preview.

**왜 로컬 compose 를 그대로 못 올리나**: ① `out/<slug>/docker-compose.yml` 의 build context 가 **절대 Windows 경로**(로컬 전용) ② manifest 가 **host volume bind**(Coolify 서버엔 그 파일 없음).

**검증된 무기**: `deployment-topology.md §4` 의 Coolify API `dockerimage` 레시피 (pre-built 레지스트리 이미지 → 도메인 → instant_deploy → 외부 HTTPS, 이미 PASS). 와일드카드 `*.n9n.co.kr` 가 `<slug>` DNS 자동 커버.

**재설계 결정 사항 (CTO 가 Phase 2 시작 시 확정)**:
1. **이미지 빌드·배급**: adapter 2개를 빌드 → 레지스트리 push. 레지스트리 선택지 — (a) Coolify 내장/서버 로컬 빌드(Coolify 가 git/Dockerfile 에서 빌드) (b) 외부 레지스트리(ghcr/docker hub) push 후 §4 `dockerimage` pull. **(a) 가 §4 dockerimage 와 안 맞을 수 있음 — Coolify "deploy from Dockerfile/compose" 경로 조사 필요** vs (b) 단순.
2. **manifest 주입 (1 이미지 N 프로필 유지)**: host-bind 대신 — (i) 배포 전 서버에 manifest 파일을 scp/생성하고 Coolify persistent storage 로 마운트 (ii) manifest 내용을 env 로 주입(크기 확인) (iii) 컨테이너 init 이 프로필 URL 에서 fetch. **(i) 가 현 아키텍처에 가장 근접**.
3. **backend↔frontend 묶기**: Coolify 에서 2-service 를 한 프로젝트로(compose 배포) vs 2 dockerimage 앱(frontend 만 도메인, backend 내부). 후자가 §4 검증 경로에 가까움.

**Phase 2 첫 스텝 (제안)**:
- (a) Coolify 4.1.2 가 Dockerfile/compose 빌드를 API 로 지원하는지 확인 (`/api/v1/applications/dockerfile` 또는 compose 엔드포인트 조사 — SSH→localhost:8000) → 빌드 경로 확정.
- (b) lawfirm-demo 로 backend 이미지 1개 먼저 서버 배포(내부) → frontend 이미지 + manifest 주입 → `lawfirm-demo.n9n.co.kr` 도메인 → 외부 HTTPS·로그인 화면 확인.
- (c) 성공 시 `infra/registry/lawfirm-demo.yaml` 첫 고객 엔트리 작성(`_template.yaml` 기반).
- 상세 로컬 보고서(참고): `out/analysis/preview-wiring-v1.md` (gitignored, 이 머신).

## 다음 후보 (Phase 2 이후)

1. **첫 고객 preview 리허설** — 가상 고객 1명으로 profile→preview_package→Coolify→`<slug>.n9n.co.kr` HTTPS 전 과정 dogfood + 레지스트리 엔트리.
2. **engineer: `.npmrc` codegraph 버전 핀** / **G-14 (`--check` stale-anchor)** (Growth-34 이월).
3. **실 고객 발굴** (M2 게이트) — 숨고/크몽 첫 의뢰.

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Opus 4.8` (트레일러=실제 co-author, §9) / master push CTO 자동 (private repo). `--no-verify`/`--no-gpg-sign` 금지.
- **시크릿 절대 chat·커밋 금지** — 볼트 `infra/secrets/*`(gitignored), 레지스트리엔 `secret_ref` 만. 시크릿 파일은 `tr`/`sed` 로 값만, 내용 비출력.
- §6 Growth 엔트리는 10줄 캡(G-9) — 길어지면 줄 병합. 상세는 `docs/learn-logs/<role>.md` 로.
- Windows `NUL` 파일 주의: `> /dev/null` 오용 시 `NUL` 추적 파일 생성 → `cmd /c 'del /f /q \\.\<abs path>\NUL'`. python 실행 `PYTHONIOENCODING=utf-8`.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ / WSL postgres ✓ / codegraph 0.9.9 ✓ / codex CLI 0.118.0 ✓.
