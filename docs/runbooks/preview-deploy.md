# Preview Deploy Runbook

> 단일 진실: DevOps 인격이 유지. 변경 시 커밋 + `docs/learn-logs/devops.md` 갱신.
> 검증 완료: lawfirm-demo (2026-06-11), shop-demo (2026-06-12) — 동일 경로 2회 반복 PASS.

새 고객 preview 를 `<slug>.n9n.co.kr` 에 올리는 전체 절차. profile slug 하나로 완전 재현 가능.

## 재사용 고정 자산 (신규 고객마다 재사용, 재생성 금지)

| 자산 | 값 | 위치 |
|---|---|---|
| Preview VPS IP | 187.77.140.157 | `infra/registry/*.yaml` |
| Coolify server_uuid | `n12vdydjpwp81hu5i15n1gsb` | Coolify API |
| Coolify privkey_uuid | `s127pafarr46wlu1r2mre2te` | Coolify > Security > Keys |
| GitHub deploy key id | 154181975 | GitHub repo > Settings > Deploy keys |
| Coolify API endpoint | `http://localhost:8000/api/v1/` | SSH 포워딩 경유 |
| API 토큰 위치 | `infra/secrets/preview-vps.env` | gitignored 볼트 |

## 사전 조건 확인

```bash
# SSH 포워딩 활성 확인
curl -s --max-time 3 http://localhost:8000/api/v1/healthcheck
# 기대: {"message":"Not found.",...}  (404 = API 살아있음)

# 죽어있으면 재활성:
ssh -i ~/.ssh/n9n_preview_ed25519 -fN \
  -o ServerAliveInterval=30 \
  -L 8000:localhost:8000 \
  root@187.77.140.157
```

## Step 1 — Manifest 생성

```bash
PYTHONIOENCODING=utf-8 python scripts/workflow/preview_package.py --profile <slug>
# 산출물: out/<slug>/screen-manifest.json
```

## Step 2 — Coolify Compose 파일 작성

> **자동화**: `preview_package.py --coolify` 가 이 단계를 자동 처리한다.

```bash
PYTHONIOENCODING=utf-8 python scripts/workflow/preview_package.py --profile <slug> --coolify
# 산출물: deploy/preview/<slug>.compose.yml
# 검증: 생성 후 shop-demo 레퍼런스와 구조 diff 자동 출력 (slug 차이 외 0 이어야 PASS)
```

수동 작성이 필요한 경우에만: `deploy/preview/lawfirm-demo.compose.yml` 을 `deploy/preview/<slug>.compose.yml` 로 복제 후 3곳 치환:

1. 주석 헤더의 `profile: lawfirm-demo` → `profile: <slug>`
2. `source:` 경로: `/data/coolify/manifests/lawfirm-demo/` → `/data/coolify/manifests/<slug>/`
3. 헤더 주석의 도메인 예시: `lawfirm-demo.n9n.co.kr` → `<slug>.n9n.co.kr`

**함정**: `docker_compose_location` 은 반드시 `/` 로 시작하는 절대경로 (`/deploy/preview/<slug>.compose.yml`). Coolify API body 의 `docker_compose_location` 필드.

커밋 후 master 푸시:

```bash
git add deploy/preview/<slug>.compose.yml
git commit -m "feat(deploy): add <slug> Coolify preview compose file
...
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
git push origin master
```

## Step 3 — Manifest SCP

```bash
ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157 \
  "mkdir -p /data/coolify/manifests/<slug>"

scp -i ~/.ssh/n9n_preview_ed25519 \
  out/<slug>/screen-manifest.json \
  root@187.77.140.157:/data/coolify/manifests/<slug>/screen-manifest.json

# 확인:
ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157 \
  "ls -la /data/coolify/manifests/<slug>/"
```

## Step 3.5 — (선택) manifest scp 단독 실행

`deploy_to_coolify.py` 가 scp 를 포함하므로 별도 실행 불필요. 수동으로 올려야 할 때만:

```bash
ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157 \
  "mkdir -p /data/coolify/manifests/<slug>"
scp -i ~/.ssh/n9n_preview_ed25519 \
  out/<slug>/screen-manifest.json \
  root@187.77.140.157:/data/coolify/manifests/<slug>/screen-manifest.json
```

## Step 4 — Coolify API 배포

> **자동화**: Steps 4a~4e + manifest scp + SECRET_KEY 주입 + 외부 검증이 한 명령으로.
>
> ```bash
> # dry-run 먼저 (payload 확인, 실제 API 호출 없음):
> PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py --slug <slug> --dry-run
>
> # 실제 배포 (멱등 — 이미 있는 project/app 재사용):
> PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py --slug <slug>
> ```
>
> 멱등 보장: project·app 이 이미 존재하면 재사용(shop-demo 기존 테넌트 안전).
> 기존 slug 재배포 = 동일 명령 재실행.

수동 단계 참조용 (스크립트 내부 동작):

> 규약: curl 인라인 금지 (훅 차단) — `out/*.sh` 또는 `out/*.py` 스크립트 파일로 실행 후 삭제.

### 4a. 프로젝트 생성

```bash
# out/step4a_create_project.sh 작성 후 bash 실행
# payload: {"name":"<slug>","description":"..."}
# POST http://localhost:8000/api/v1/projects
# 응답: {"uuid":"<project_uuid>"}
```

### 4b. Compose 앱 생성

```
POST http://localhost:8000/api/v1/applications/private-deploy-key
body:
{
  "project_uuid": "<project_uuid>",
  "server_uuid": "n12vdydjpwp81hu5i15n1gsb",
  "environment_name": "production",
  "build_pack": "dockercompose",
  "git_repository": "git@github.com:JasonMMo/compounding-stack-harness.git",
  "git_branch": "master",
  "private_key_uuid": "s127pafarr46wlu1r2mre2te",
  "docker_compose_location": "/deploy/preview/<slug>.compose.yml",   <-- 절대경로 필수
  "name": "<slug>",
  "instant_deploy": false
}
응답: {"uuid":"<app_uuid>","domains":"..."}
```

### 4c. 도메인 설정 (PATCH)

**함정**: `fqdn` 직접 PATCH 는 422 오류. 반드시 `docker_compose_domains` 배열 방식 사용.

```
PATCH http://localhost:8000/api/v1/applications/<app_uuid>
body:
{
  "docker_compose_domains": [{"name":"frontend","domain":"https://<slug>.n9n.co.kr"}]
}
응답: {"uuid":"<app_uuid>"}
```

### 4d. 배포 트리거

```
GET http://localhost:8000/api/v1/applications/<app_uuid>/start
응답: {"message":"Deployment request queued.","deployment_uuid":"<deploy_uuid>"}
```

### 4e. 빌드 로그 확인

```
GET http://localhost:8000/api/v1/deployments/<deploy_uuid>
응답.status: "finished" (PASS) | "error" (FAIL → logs 확인)
```

빌드 성공 판정: `status == "finished"`, 마지막 visible 로그 = `"Gracefully shutting down build container"`.

## Step 5 — 외부 검증

```bash
# HTTP 200 확인
curl -s -o /dev/null -w "HTTP %{http_code}" --max-time 15 "https://<slug>.n9n.co.kr/login"
# 기대: HTTP 200

# TLS 인증서 CN 확인
echo | openssl s_client -connect <slug>.n9n.co.kr:443 -servername <slug>.n9n.co.kr \
  2>/dev/null | openssl x509 -noout -subject -issuer -dates
# 기대: subject=CN=<slug>.n9n.co.kr, issuer=Let's Encrypt

# /health 확인
curl -s -o /dev/null -w "HTTP %{http_code}" --max-time 10 "https://<slug>.n9n.co.kr/health"
# 기대: HTTP 200
```

3항목 모두 PASS 시 preview live 확정.

**CISO 보안 주의 (§7)**: `GET /applications/{uuid}/envs` 응답의 `real_value` 필드에 SECRET_KEY 평문 노출됨. `deploy_to_coolify.py` 는 이 필드를 `***masked***` 로 자동 치환하여 절대 출력하지 않는다. 수동 API 호출 시에도 응답 출력 전 `real_value` 필드를 마스킹할 것.

## Step 6 — SECRET_KEY 주입

SECRET_KEY 를 Coolify 앱 환경 변수로 주입 (gitignored 볼트에서 읽어 API POST):

```
# 볼트에 키 생성 (infra/secrets/<slug>-secret-key.txt, gitignored)
python -c "import secrets; open('infra/secrets/<slug>-secret-key.txt','w').write(secrets.token_hex(32))"

# Coolify API 주입
POST http://localhost:8000/api/v1/applications/<app_uuid>/envs
body: {"key":"SECRET_KEY","value":"<value_from_vault>"}
```

**함정**: `is_build_time` / `is_secret` 필드 포함 시 422. body 는 `key`/`value` 만.

## Step 7 — 레지스트리 등록

> **자동화**: `deploy_to_coolify.py` 가 배포 성공 후 자동으로 `infra/registry/<slug>.yaml` 을 갱신한다.
>
> - 갱신 필드: `coolify_project`, `coolify_app`, `url`, `status`, `deployed_at` (Coolify `finished_at` 타임스탬프 사용, 하드코드 금지)
> - **merge 보장**: `secret_ref`, `tls`, `contact`, `production`, `build_commit` 등 수동 작성 필드 절대 클로버 금지
> - 파일 없으면 최소 스켈레톤 자동 생성
> - 갱신 후 커밋은 별도로 (`--skip-registry` 플래그로 skip 가능)

수동 작성이 필요한 경우에만: `infra/registry/<slug>.yaml` 을 `_template.yaml` 기반으로 작성:
- `secret_ref`: `vault/<slug>/secret-key` 참조만 (평문 금지)
- 모든 uuid (coolify_project, coolify_app) 기록
- `tls` 필드: `openssl x509` 출력 기준

레지스트리 커밋:

```bash
git add infra/registry/<slug>.yaml
git commit -m "feat(registry): add <slug> digital asset record
...
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

## Step 8 — Ledger 갱신

`docs/learn-logs/devops.md` 에 1줄 롤업 + 상세 기록.

## 실제 예시 (shop-demo, 2026-06-12)

| Step | 결과 | 비고 |
|---|---|---|
| manifest 생성 | PASS | entities: contact, sales-order, sales-order-line |
| compose 작성+커밋 | PASS | commit e62abac |
| manifest scp | PASS | /data/coolify/manifests/shop-demo/ |
| project 생성 | PASS | uuid: k5vmkpn9ygimznoxnavpwd4y |
| app 생성 | PASS | uuid: cn56k6xtmhp2njv5ed31xv7t |
| 도메인 PATCH | PASS | docker_compose_domains 방식 |
| 배포 트리거 | PASS | deploy uuid: d3k0p5ssr978fhnl5veu1pyn |
| 빌드 로그 | PASS | status: finished, 0 visible errors |
| HTTPS /login | PASS | HTTP 200 |
| TLS CN | PASS | CN=shop-demo.n9n.co.kr, exp 2026-09-09 |
| /health | PASS | HTTP 200 |
| SECRET_KEY 주입 | PASS | env uuid: uow88ywm0w2wskq30ct8lfju |

## 자동화 현황 및 남은 갭 (2026-06-12 갱신)

| 단계 | 자동화 상태 | 명령 |
|---|---|---|
| compose 파일 생성 | **완료** | `preview_package.py --profile <slug> --coolify` |
| compose commit+push | **완료** | `deploy_to_coolify.py --slug <slug> --commit` |
| manifest SCP | **완료** | deploy_to_coolify.py 내장 |
| Coolify API 4단계 | **완료** | deploy_to_coolify.py 내장 |
| 레지스트리 갱신 | **완료** | deploy_to_coolify.py 내장 (merge, secret_ref 보존) |
| GitHub webhook 등록 | **조사 완료 — CTO 컨펌 대기** | `deploy_to_coolify.py --slug shop-demo --setup-webhook` (계획 출력) / `--confirm` (실행, CTO 승인 후) |

### webhook 자동 재배포 컨펌 게이트

- **조사 결과 (2026-06-12)**: Coolify 4.1.2 webhook 엔드포인트 = `https://187.77.140.157/webhooks/source/github/events/manual`, 인증 = GitHub HMAC-SHA256 (`X-Hub-Signature-256`), 시크릿 = 앱의 `manual_webhook_secret_github` (40자 hex, 자동 생성됨)
- **중요 제한**: Coolify 4.1.2 webhook 은 `git_repository` 로 앱을 매칭 — master push 시 **같은 repo 를 가진 모든 앱이 동시 재배포**됨. 현재 lawfirm-demo + shop-demo 2개 테넌트 모두 트리거됨.
- **CTO 컨펌 필요 항목**: ① 2 테넌트 동시 자동 재배포 허용 여부 ② webhook URL 이 VPS IP 직접(443) 사용해도 무방한지 (FQDN 사용 권장 여부) ③ 적용 범위 (shop-demo 먼저 / 전체 동시)
- **컨펌 후 실행**: `PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py --slug shop-demo --setup-webhook --confirm`

## 비용

preview 추가당 인프라 비용 증가 없음 (공유 VPS, 컨테이너 1개 추가). Hostinger KVM2 $8.99/월 고정분 배분.
