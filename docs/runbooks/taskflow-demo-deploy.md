# Taskflow-Demo Deploy Runbook

> DevOps 인격 유지. 변경 시 커밋 + `docs/learn-logs/devops.md` 갱신.
> 재사용 인프라: preview VPS 187.77.140.157 / Coolify / Traefik / n9n.co.kr Cloudflare.
>
> **보안 고지**: login `demo`/`demo` 는 스텁(인증 검증 없음). 백엔드는 in-memory store
> — 재시작 시 모든 데이터 소멸. **실 고객 데이터 입력 절대 금지.** 가짜 데모 데이터 전용.

## 아키텍처 요약

```
Cloudflare DNS (taskflow-demo.n9n.co.kr → 187.77.140.157)
  └── Traefik (SSL termination, Let's Encrypt)
        └── Coolify stack: taskflow-demo
              ├── backend   (fastapi, port 8081, in-memory store)
              ├── seeder    (one-shot: scaffold → manifest, seed 51 records)
              └── frontend  (vanilla-htmx Flask, port 5000)
                            shared volume: taskflow_manifest (manifest JSON)
```

**seeder 동작**: backend healthy 대기 → `scaffold.py --profile taskflow-demo` 실행 (manifest 생성) → manifest를 shared volume에 복사 → `seed_loader.py` 51건 POST → exit 0. 매 Coolify redeploy마다 실행 → 데모 데이터 초기화됨 (의도적).

---

## Step 0 — 사전 조건 확인

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

---

## Step 1 — Cloudflare DNS 레코드 추가

Cloudflare 대시보드 > n9n.co.kr 존 > DNS:

| Type | Name | Content | Proxy |
|---|---|---|---|
| A | taskflow-demo | 187.77.140.157 | Proxied (주황 구름) |

이미 `*.n9n.co.kr` 와일드카드 A 레코드가 있으면 이 단계 생략 (레코드 존재 확인만).

---

## Step 2 — SECRET_KEY 볼트 준비

```bash
# gitignored 볼트 경로: infra/secrets/taskflow-demo-secret-key.txt
python -c "import secrets; print(secrets.token_hex(32))"
# 출력 값을 infra/secrets/taskflow-demo-secret-key.txt 에 저장 (git 추적 안 됨)
```

Coolify 환경 변수에 `SECRET_KEY=<위 값>` 을 주입 (Step 4e).

---

## Step 3 — git push (artifacts 포함)

```bash
# 다음 파일들이 커밋·푸시되어 있어야 Coolify 빌드가 성공함
# (CTO가 아래 파일들을 퍼-파일 커밋 후 push)
#   deploy/preview/taskflow-demo.compose.yml
#   scripts/taskflow-seeder/Dockerfile
#   scripts/taskflow-seeder/entrypoint.sh
#   infra/registry/taskflow-demo.yaml

git log --oneline -5   # 위 파일들이 포함된 커밋 확인
git push origin master
```

---

## Step 4 — Coolify 배포 (자동화 스크립트 사용)

### 4a. dry-run 확인

```bash
PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py \
  --slug taskflow-demo --dry-run
# payload 확인 후 이상 없으면 실제 배포 진행
```

### 4b. 실제 배포

```bash
PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py \
  --slug taskflow-demo
# 완료 시 응답에 project_uuid, app_uuid 출력 → infra/registry/taskflow-demo.yaml 에 채워 넣을 것
```

### 4c. 수동 대안 (스크립트 실패 시)

deploy_to_coolify.py 가 없거나 실패할 경우:

1. **프로젝트 생성**: POST `/api/v1/projects` `{"name":"taskflow-demo"}`
2. **앱 생성**: POST `/api/v1/applications/private-deploy-key`
   ```json
   {
     "project_uuid": "<project_uuid>",
     "server_uuid": "n12vdydjpwp81hu5i15n1gsb",
     "environment_name": "production",
     "build_pack": "dockercompose",
     "git_repository": "git@github.com:JasonMMo/compounding-stack-harness.git",
     "git_branch": "master",
     "private_key_uuid": "s127pafarr46wlu1r2mre2te",
     "docker_compose_location": "/deploy/preview/taskflow-demo.compose.yml",
     "name": "taskflow-demo",
     "instant_deploy": false
   }
   ```
3. **도메인 설정**: PATCH `/api/v1/applications/<app_uuid>`
   ```json
   {"docker_compose_domains": [{"name":"frontend","domain":"https://taskflow-demo.n9n.co.kr"}]}
   ```
   > 함정: git fetch race — `docker_compose_raw` 필드가 채워질 때까지 5s 간격 poll 후 PATCH.
4. **환경 변수 주입**: Coolify UI > 앱 > Environment Variables > `SECRET_KEY=<볼트 값>`
5. **배포 트리거**: GET `/api/v1/applications/<app_uuid>/start`

---

## Step 5 — manifest SCP 불필요 (이 demo는 seeder가 처리)

taskflow-demo는 seeder 컨테이너가 배포 시 scaffold.py로 manifest를 생성하고
shared Docker volume에 기록한다. lawfirm-demo의 `/data/coolify/manifests/` 호스트
bind-mount 방식을 **사용하지 않는다** — SCP 단계 없음.

> bind-mount 디렉터리화 함정(lawfirm-demo edu-program 2026-06-12 실측)을 피하기 위해
> 의도적으로 named volume 방식으로 설계함.

---

## Step 6 — 빌드 로그 확인

Coolify UI > 앱 > Deployments > 최신 항목 > Logs

기대 순서:
1. `backend` 빌드 완료 + healthcheck PASS
2. `seeder` 실행: `[seeder] Step 1: generate screen-manifest` → `[seeder] manifest written` → `[seeder] Step 2: seed taskflow-demo demo data` → `[seeder] seed complete — exiting cleanly`
3. `frontend` 빌드 완료 + 기동

`seeder` 가 exit 1 로 종료하면 `frontend` 가 `service_completed_successfully` 조건 미충족으로 뜨지 않는다. 로그에서 `[seeder] ERROR` 키워드를 확인할 것.

---

## Step 7 — 외부 검증 (smoke check)

```bash
# 1. 프론트 응답
curl -s -o /dev/null -w "HTTP %{http_code}" --max-time 15 \
  "https://taskflow-demo.n9n.co.kr/login"
# 기대: HTTP 200

# 2. TLS 인증서
echo | openssl s_client -connect taskflow-demo.n9n.co.kr:443 \
  -servername taskflow-demo.n9n.co.kr 2>/dev/null \
  | openssl x509 -noout -subject -dates
# 기대: CN=taskflow-demo.n9n.co.kr, Let's Encrypt

# 3. 백엔드 health (프론트 컨테이너를 통한 내부 검증은 Coolify 로그로 확인)
#    직접 접근 불가 (포트 미노출). 프론트가 응답하면 backend healthy 판정.

# 4. 로그인 + API 동작 확인
#    브라우저에서 https://taskflow-demo.n9n.co.kr/login
#    ID: demo / PW: demo 로그인
#    보드 화면 진입 후 태스크 목록 표시 확인 (51건 seeded)

# 5. API 직접 확인 (선택)
#    Coolify > 앱 > Terminal > backend 컨테이너:
#    curl http://localhost:8081/api/status/health
#    curl -X POST http://localhost:8081/api/auth/login \
#      -H "Content-Type: application/json" \
#      -d '{"username":"demo","password":"demo"}' | python -m json.tool
#    # 토큰 확인 후:
#    curl -H "Authorization: Bearer <token>" \
#      "http://localhost:8081/api/entities/task" | python -m json.tool
#    # 기대: records 배열 (seeded 태스크 목록)
```

---

## Step 8 — 레지스트리 갱신

배포 완료 후 `infra/registry/taskflow-demo.yaml` 의 null 필드를 채운다:

```yaml
coolify_project: <project_uuid>
coolify_app: <app_uuid>
coolify_env: <environment_uuid>
status: live
deployed_at: "YYYY-MM-DD"
build_commit: <head_sha>
tls: "Let's Encrypt, CN=taskflow-demo.n9n.co.kr, exp YYYY-MM-DD"
```

---

## Redeploy (데모 데이터 초기화)

Coolify UI > 앱 > Redeploy 버튼 (또는 git push → 자동 트리거 설정 시).
seeder가 재실행되어 51건 초기 상태로 리셋된다.

## 주요 결정 사항 (재검토 불필요)

| 결정 | 이유 |
|---|---|
| Manifest를 seeder에서 생성 | out/이 gitignored → 호스트 SCP 없이 재현 가능, bind-mount 디렉터리화 함정 회피 |
| Named volume (taskflow_manifest) | 호스트 bind-mount 의존성 제거 — seeder와 frontend 간 manifest 공유 |
| seeder restart: "no" | 1회 실행 후 종료. frontend는 service_completed_successfully 게이트 |
| in-memory store + 매 redeploy 리셋 | 반복 데모에 항상 깨끗한 상태 제공 — 데이터 영속성 없음 (의도적) |
| 인증 게이트 없음 (demo/demo만) | 가짜 데이터 전용 — 실 고객 데이터 격리 고객사 배포 시 별도 설계 필요 |
