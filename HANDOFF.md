# HANDOFF — 2026-06-12 (Growth-35: preview 자동화 결선 + Coolify 유지 결정)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.
> **다음 작업 = 실 고객 발굴 (M2 게이트)** — preview 파이프라인은 한 줄 명령으로 완성됨. 인프라 작업 더 없이 첫 의뢰만 받으면 됨.

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

## ▣ preview 파이프라인 — 한 줄 명령으로 완성 (이번 세션 결선)

**profile slug → 외부 HTTPS preview 가 두 줄.** 새 고객 의뢰 오면 이대로:
```
PYTHONIOENCODING=utf-8 python scripts/workflow/preview_package.py --profile <slug> --coolify   # 서버용 compose 생성
PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py --slug <slug>              # Coolify API 4단계 + manifest scp + 검증 한 방 (레지스트리 auto-merge 포함)
```
- **검증된 레시피** = `private-deploy-key` 엔드포인트 + `build_pack=dockercompose`(git-build) + manifest **persistent-storage RO 마운트**(서버 `/data/coolify/manifests/<slug>/screen-manifest.json` → frontend `/data/manifest/`). 함정·재사용 uuid·단계 전부 런북 `docs/runbooks/preview-deploy.md` 에 박힘.
- **재사용 상수**: server_uuid `n12vdydjpwp81hu5i15n1gsb`, privkey_uuid `s127pafarr46wlu1r2mre2te`(모든 고객 deploy 공용), git deploy key 이미 GitHub 등록(재생성 금지).
- **현재 live**: `lawfirm-demo.n9n.co.kr` + `shop-demo.n9n.co.kr` (둘 다 가상 고객, HTTPS 200 + LE cert). 멀티테넌트 동작 확인.
- **함정 (런북 참조)**: docker_compose_location 절대 `/` 경로 / 도메인은 `docker_compose_domains` PATCH(fqdn 필드 422) / SECRET_KEY 가 `/envs` GET `real_value` 평문 노출(조회 시 마스킹).

**substrate 결정 (이번 세션)**: **Coolify 유지.** Caddy spike 결과 Caddy 가 기술 우위(5/5 함정 제거·wildcard DNS-01 cert 0발급·harness 변경 0)지만, 함정이 `deploy_to_coolify.py` 로 이미 캡슐화돼 현 운영비용≈0 → 전환비용(CEO 대시보드 상실 + `xcaddy` 커스텀 빌드 + 15~30s 다운타임)이 더 큼. **검증·비용산정된 탈출 경로 확보**(spike 파일 `out/spike-caddy/*` + `out/analysis/spike-caddy-vs-coolify.md`). **전환 트리거**: 테넌트≥5 AND SECRET_KEY rotate 월1회↑ 필요 AND Coolify 4.x 함정 미해소 — 셋 다 충족 시 재검토.

**webhook auto-deploy 보류 결정**: Coolify 4.1.2 가 per-app/path 필터 없어 repo-push 시 전 테넌트 동시 재배포 → 영업 데모 안정성 위협. 수동 한 줄 deploy 가 통제·멱등·테넌트 격리. 코드는 `--setup-webhook --confirm` 게이트로 보관(당기지 않음). 재고 조건: per-app 필터 생기거나 테넌트 다수.

## 다음 후보

1. **★ 실 고객 발굴 (M2 게이트)** — 숨고/크몽 첫 의뢰. **인프라는 준비 끝** — 의뢰 받으면 profile 작성 → 위 두 줄 → 외부 데모. 막는 건 영업뿐.
2. **자동화 잔여 (작음, 낮은 우선순위)**: 레지스트리 변경분 per-file 커밋 자동화 / git push→auto-redeploy(webhook 보류 중) / SECRET_KEY rotate(현 Coolify UI 수동).
3. **engineer: `.npmrc` codegraph 버전 핀** / **G-14 (`--check` stale-anchor)** (Growth-34 이월).

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Opus 4.8` (트레일러=실제 co-author, §9) / master push CTO 자동 (private repo). `--no-verify`/`--no-gpg-sign` 금지.
- **시크릿 절대 chat·커밋 금지** — 볼트 `infra/secrets/*`(gitignored), 레지스트리엔 `secret_ref` 만. 시크릿 파일은 `tr`/`sed` 로 값만, 내용 비출력.
- §6 Growth 엔트리는 10줄 캡(G-9) — 길어지면 줄 병합. 상세는 `docs/learn-logs/<role>.md` 로.
- Windows `NUL` 파일 주의: `> /dev/null` 오용 시 `NUL` 추적 파일 생성 → `cmd /c 'del /f /q \\.\<abs path>\NUL'`. python 실행 `PYTHONIOENCODING=utf-8`.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ / WSL postgres ✓ / codegraph 0.9.9 ✓ / codex CLI 0.118.0 ✓.
