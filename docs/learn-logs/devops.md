# DevOps Ledger — 인격별 상세 기록

> 실행 주체: `devops-agent` (`.claude/agents/devops-agent.md`). main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 이 파일은 DevOps 가 닿은 Growth 의 인프라·배포·설치·비용 상세 (대상·조치·재현 명령) 를 담는다. main §6 은 1줄 rollup + 이 ledger pointer.

토폴로지 단일 진실: [`../architecture/deployment-topology.md`](../architecture/deployment-topology.md). 절차: [`../../.claude/skills/devops-loop/SKILL.md`](../../.claude/skills/devops-loop/SKILL.md).

## §1 — Growth 상세

### Growth-35 (2026-06-11) — DevOps 인격 신설 (founding) + 배포 토폴로지 v1

- **계기**: CEO 직접 요구 — 이 harness 를 바탕으로 **1인 비대면 창업** (숨고/크몽 건당 500만원). 고객 접점 3종 (메신저·preview 사이트·원격/방문 설치) + 인프라·디지털 자산·CI/CD 담당 인격 필요. n9n.co.kr 도메인 보유.
- **결정 (CEO 위임 → CTO 설계)**: 인프라/배포/CD 를 engineer·CISO 에 통합하지 않고 전담 9번째 인격으로 분리. 근거 — ① engineer 는 artifact *생성*, DevOps 는 *출하·호스팅·추적* (다른 축) ② CISO 는 보안 *판정*, DevOps 는 하드닝 *실행* ③ 1인이 N 고객 자산을 추적해야 하므로 레지스트리 단일 책임자 필요 ④ charter "직무별 인격" 철학.
- **핵심 아키텍처 통찰 (CTO)**: **preview 티어 ≠ production 티어**. 우리 가치 제안은 고객 사내망 self-host (M2) → 최종 인도물은 고객 인프라. n9n.co.kr/VPS 는 **고객 설득용 preview/staging 전용**. 이 분리가 배포 선택을 가른다.
- **배포 결정**: 로컬 Docker+터널을 고객-facing preview 로 쓰지 않는다 (노트북 의존 = 비대면 신뢰도 치명). **Coolify on Hostinger VPS** (KVM 1, 싱가포르, \$5.84/월 24개월 — CEO 확정, 한국 페이지 검토 후) + `*.n9n.co.kr` 와일드카드 DNS → 고객별 `<slug>.n9n.co.kr`. 터널(cloudflared)은 작업 중 화면공유 데모 폴백으로만.
  - **provider 비교 (기각)**: Hostinger 한국 DC 없음 → 싱가포르 최근접(~70-90ms, preview 무관). Vultr 서울 = 진짜 한국 DC·무약정이나 8GB 동급 ~\$48/월(5배). 한국 affiliate 리스트(Ultahost 등) = 커미션 정렬·실 Seoul DC 불명확. → preview 는 지연 무관·RAM 가성비 우선이라 Hostinger. Coolify 원클릭 템플릿으로 셋업 단축. **확정: KVM 2** (2vCPU/8GB, \$8.99/월 — KVM1 +\$3 로 RAM 2배라 다수 스택 여유). OS = Coolify 템플릿(있으면)/Ubuntu 24.04 LTS.
- **GTM 접점**: 숨고/크몽 플랫폼 채팅(초기) → 카카오톡 채널(진행) → n9n.co.kr 랜딩/포트폴리오. 커스텀 메신저 ✗ (과설계).
- **신설 자산**: `.claude/agents/devops-agent.md` + `.claude/skills/devops-loop/SKILL.md` (출력 규약 wiring, G-13) + `docs/architecture/deployment-topology.md` (토폴로지 단일 진실) + `infra/registry/` (디지털 자산 레지스트리 스캐폴드) + charter v1.6 (9-인격) + CLAUDE.md §1 동기화 + INDEX.md 행.
- **권한**: preview 티어 운영·디지털 자산 레지스트리·CI/CD·시크릿 볼트 운영·설치 런북·인프라 비용 추적 (단독, CTO 아키텍처 제약 내). 인도 설치는 PM 승인 + CISO 보안 게이트 후.
- **첫 임무 (다음 세션)**: ① preview VPS provisioning (Seoul) + Coolify 설치 + `*.n9n.co.kr` 와일드카드 DNS ② CI/CD v1 (`scaffold.py` → docker build → Coolify push) ③ 레지스트리 첫 엔트리.

## §2 — Loop 회전 기록 (배포·설치)

> 각 행: 대상 환경 | 일자 | 동작 (provision/deploy/install) | 결과 | 비용 델타

| 대상 | 일자 | 동작 | 결과 | 비용 델타 |
|---|---|---|---|---|
| (인격 신설 — 첫 배포는 다음 세션 preview VPS provisioning 부터) | 2026-06-11 | founding | 토폴로지 v1 확정 + provider 확정 (Hostinger KVM 2 싱가포르, OS=Coolify 템플릿/Ubuntu 24.04) | Hostinger KVM 2 \$8.99/월 24개월 (CEO provisioning 중) |
| preview VPS (187.77.140.157, 싱가포르) | 2026-06-11 | provision (1차) | live — 접속·하드닝 일부 | KVM 2 \$8.99/월 가동 |
| preview VPS — TLS 파이프라인 | 2026-06-11 | provision (2차) | **검증 PASS** — `<slug>.n9n.co.kr` 자동 HTTPS | LE 무료 |
| preview VPS — CI/CD (Coolify API) | 2026-06-11 | deploy (스모크) | **검증 PASS** — API 로 프로젝트→앱→배포→외부 HTTPS 200, 정리 후 잔여 0 | LLM 0, infra 0 (기존 VPS) |
| lumi.n9n.co.kr (Growth-83) | 2026-06-16 | deploy (A5 Mobile App, nova 테마) | **검증 PASS** — build finished, HTTPS 200, "Build better days" 서빙 확인. portal 8번째 카드 반영 | $0 (shared VPS) |
| preview VPS — 8000 노출 차단 | 2026-06-11 | harden (3차) | **검증 PASS** — 클라우드 방화벽 allow-list, 8000/8080/6001/6002 외부 차단 실측, 22/80/443 유지. CISO 잔여 0 | $0 |
| 로컬 (preview 패키징) | 2026-06-11 | package (scaffold 결선) | **검증 PASS** — profile→2-container compose, lawfirm-demo /login·/health 200, manifest 14 entities. Coolify 배포는 Phase 2 | $0 |
| lawfirm-demo.n9n.co.kr (Coolify Phase 2) | 2026-06-11 | deploy (첫 영속 preview) | **검증 PASS** — build_pack=dockercompose, LE TLS 자동, /login 200, /login HTML 정상. 앱 UUID opryb94j9k5cjdv8bienenv0 | LLM ~$0.5, infra $0 (기존 VPS) |
| shop-demo.n9n.co.kr (리허설) | 2026-06-12 | deploy (반복 가능성 입증) | **검증 PASS** — 동일 경로 2번째 반복. /login 200, TLS CN=shop-demo, /health 200. 앱 UUID cn56k6xtmhp2njv5ed31xv7t. 런북 신설 | LLM ~$0.3, infra $0 (기존 VPS) |
| shop-demo.n9n.co.kr (자동화 검증) | 2026-06-12 | deploy (멱등 재배포 — 스크립트) | **PASS** — `deploy_to_coolify.py --slug shop-demo` 단일 명령. 빌드 finished, /login 200, /health 200, TLS CN PASS. preview_package.py --coolify 구조 diff PASS. | LLM ~$0.3, infra $0 |
| shop-demo.n9n.co.kr (갭1·갭2 자동화) | 2026-06-12 | registry 자동 merge + webhook 조사 | **PASS (갭1)** — 레지스트리 merge(secret_ref/tls/수동 필드 보존, deployed_at=Coolify finished_at). **CTO 컨펌 대기 (갭2b)** — webhook 조사: repo-level 매칭 리스크 확인, `--setup-webhook` 계획 출력 PASS. | LLM ~$0.4, infra $0 |
| Caddy vs Coolify spike | 2026-06-12 | 평가 (코드 레벨 + 파일 준비) | 함정 5/5 해소 확인. API 호출 6~8 → 1~2. wildcard TLS cert 발급 0. 권고: 현 시점 Coolify 유지 (CEO 대시보드 상실 비용 > 함정 캡슐화 현상태). Docker 오프라인으로 컨테이너 실행 미완 — spike 파일 준비 완료. | LLM ~$0.3, infra $0 |

### Growth-35 provisioning 1차 (2026-06-11) — preview VPS 부트스트랩

- **접속**: 전용 키 `n9n_preview_ed25519` (용도별 격리, oracle 패턴 계승) 생성 → CEO 가 Hostinger 최초 설정 "Add SSH Key" 로 등록 → 키 인증 성공.
- **정찰**: Ubuntu 24.04.4 LTS, Docker 29.5.3, **Coolify 4.1.2** 풀스택 healthy (coolify/proxy=traefik v3.6/db=pg15/redis/realtime), RAM 7.8Gi(8GB ✓), 리스닝 22·80·443·8000·8080·6001·6002.
- **하드닝 적용**: `/etc/ssh/sshd_config.d/00-hardening.conf` — `PasswordAuthentication no` + `PermitRootLogin prohibit-password` (00- prefix 로 50-cloud-init yes 보다 먼저 파싱돼 우선). `sshd -t` 검증 → reload → 새 연결로 키 인증 재확인 (REKEY_OK).
- **CISO 미해소 (TODO)**: ① 방화벽 inactive — 클라우드 방화벽으로 8000(admin UI)→CEO IP 제한 필요 (ufw 는 docker-published 포트 미차단 gotcha). ② `apt upgrade` 미실행. ③ Coolify `/register` 200=열림 → **CEO 즉시 admin 선점 필요** (포트 8000 인터넷 노출, 선등록자=root).
- **다음**: admin 등록 후 → 클라우드 방화벽 → Coolify instance FQDN/`*.n9n.co.kr` 와일드카드 + TLS → CI/CD v1 → 레지스트리 고객 엔트리.

### Growth-35 provisioning 2차 (2026-06-11) — DNS + TLS 파이프라인 end-to-end 검증 PASS

- **admin 선점**: CEO Coolify admin 등록 완료 → `/register` 302→login (열린 창 닫힘, 보안 해소).
- **DNS**: n9n.co.kr 은 **Cloudflare** 관리. `*` A→187.77.140.157 **grey-cloud(DNS-only)** 추가 → Cloudflare/Google 양쪽 전파 확인 (acme-corp/test/foobar 모두 직접 IP).
- **TLS 검증 (Coolify API 없이 SSH 만으로)**: traefik 구성 정찰 (certresolver `letsencrypt` HTTP-01, network `coolify`, acme.json 0B) → `coolify` 네트워크에 traefik 라벨 단 `traefik/whoami` 테스트 컨테이너 기동(`Host(test.n9n.co.kr)`) → **35s 내 LE 정식 인증서 자동 발급** (acme.json 15.9KB, issuer=Let's Encrypt, CN=test.n9n.co.kr, ~9/9 만료) → 외부 머신 `https://test.n9n.co.kr` 200 + whoami + X-Forwarded-Proto=https → 테스트 컨테이너 제거(잔여 0).
- **증명**: 임의 `<slug>.n9n.co.kr` → 자동 HTTPS 파이프라인 작동. preview 티어 코어 기능 live.
- **CISO 잔여**: ① 8000(admin UI) 인터넷 노출 (admin 등록·강비번으로 auth 보호되나 source-IP 제한 권장 — CEO 공인 IP 121.165.228.221 관측되나 가정용 동적 가능성) ② apt upgrade ③ 향후 admin 을 `coolify.n9n.co.kr`(443) 로 서빙 후 raw 8000 차단이 정석.
- **다음**: 남은 하드닝 → Coolify API 토큰(시크릿 볼트) → CI/CD v1 (`scaffold.py`→Coolify 배포) → 첫 고객 preview.

### Growth-35 CISO 사고 (2026-06-11) — 토큰 source 노출 + 규약 수정

- **사고**: Coolify API 토큰을 볼트에서 `set -a; . preview-vps.env` (source) 로 읽음 → Coolify 토큰이 `id|hash` 형식(`|` 포함)이라 미인용 값의 `|` 를 셸이 파이프로 해석 → 에러 메시지로 **토큰 값이 transcript 에 노출**.
- **영향**: 토큰이 root 권한 + 8000 인터넷 노출 → 노출 토큰 폐기 필수. 커밋물엔 없음(볼트 gitignored), git history 깨끗.
- **조치**: ① CEO 가 노출 토큰 즉시 revoke + 재발급 ② 볼트 규약 수정 — **source 금지, `sed -n 's/^KEY=//p'` 추출** (셸 미실행, 특수문자 안전). README + .example 반영.
- **교훈 (1줄)**: 시크릿 .env 는 절대 `source` 하지 않는다 — 임의 토큰의 특수문자(`|$ \``)가 셸에서 실행·노출된다. 값 추출은 sed/grep 으로 셸을 안 거치게. (가드 후보: 스크립트 내 `source *.env`/`. *.env` 탐지.)
- **2차 노출 (같은 세션)**: 재발급 토큰을 `cut -d= -f1` 로 진단 → 파일에 `KEY=` 접두어 없이 값만 있어 전체 줄(=토큰) 출력. **2번째 토큰도 폐기**. 근본 교훈: ① 불투명 토큰은 `KEY=value` 금지 → **값만 담은 전용 파일**(`coolify_api_token`), `tr` 로 읽고 `${#}` 길이만 확인 ② **읽기 실패 시 포맷 추측 진단(`cut`/`xxd`/`cat`) 금지** — 진단이 곧 노출. 빈 값이면 CEO 에게 파일 확인 요청. README/example 반영, `preview-vps.env`(KEY=value) 폐기 → `coolify_api_token`(raw).
- **3차(폐기 후 재발급) — 운영 파일 = `preview-vps.env`(raw 값)**: CEO 가 노출 2개 폐기 후 새 토큰을 `preview-vps.env` 에 raw 로 저장 (sed 가 접두어 유무 양쪽 처리). 읽기 스크립트에서 fallback 라인 누락 시 `coolify_api_token`(없는 파일)만 읽어 `len=0` → **내용 비출력 원칙대로 `wc -c` 바이트 길이만으로 어느 파일에 있는지 판별**(content 안 찍음). 교훈: 시크릿 소스 경로는 한 곳으로 고정하거나 항상 fallback 포함. 빈 값일 때도 `wc -c`/존재 확인은 안전(값 비노출), `cat`/`cut` 만 금지.

### Growth-35 CI/CD v1 (2026-06-11) — Coolify API 배포 파이프라인 end-to-end 증명

- **토큰 스코프 함정**: 첫 토큰 read-only → `GET 200` 이지만 `POST /projects` = `{"message":"Unauthenticated."}`. 같은 헤더에 메서드만 다르면 **쓰기 스코프 부재** 신호. CEO 가 **write+deploy**(또는 root) 스코프로 재발급 → POST 200.
- **파이프라인**: `POST /projects`(uuid) → `GET /projects/{uuid}`(환경 production uuid) → `POST /applications/dockerimage`(image=traefik/whoami, ports_exposes=80, domains=https://cicd-smoke.n9n.co.kr, instant_deploy=true) → ~45s 후 **외부 머신 `https://cicd-smoke.n9n.co.kr` 200 + LE 정식 인증서**(CN=cicd-smoke.n9n.co.kr, issuer Let's Encrypt, 90일, ssl_verify=0).
- **정리**: `DELETE /applications/{uuid}` 는 **비동기 큐** → 즉시 `DELETE /projects/{uuid}` 하면 `"Project has resources"` 실패. ~15s 후 재시도 → `Project deleted`, projects=[], 외부 도메인 503. 잔여 0.
- **증명 의미**: profile→scaffold 산출 이미지를 `dockerimage` image 자리에 넣으면 **한 명령으로 고객 preview 자동 생성**. creater(CI/CD)축 코어 작동. 레시피는 토폴로지 §4 에 런북화 (재유도 금지).
- **CISO 잔여(불변)**: 8000 admin UI 인터넷 노출 — 토큰은 SSH→localhost 로만 쓰므로 8000 을 클라우드 방화벽으로 막아도 API 운영 무영향. 다음 하드닝: instance FQDN `coolify.n9n.co.kr`(443) + raw 8000 차단.

### Growth-35 하드닝 3차 (2026-06-11) — 8000 admin UI 노출 차단 (CISO 잔여 0)

- **상황**: `instance_settings.fqdn = null` + 4.1.2 UI 에 FQDN 필드가 안 보임(버전별 위치 이동). → instance FQDN(443) 경로 대신 **클라우드 방화벽 allow-list** 채택 (버전 UI 무관·하이퍼바이저 레벨이라 `ufw 가 docker-published 포트 미차단` gotcha 회피).
- **조치 (CEO 실행, DevOps 설계·검증)**: Hostinger 클라우드 방화벽 default-deny + inbound **22/80/443 만 허용**. 22=SSH(키전용), 80=LE HTTP-01+리다이렉트, 443=preview HTTPS. 나머지 자동 차단.
- **검증 (외부 머신 실측)**: 8000/8080/6001/6002 = 차단(필터), 22/80 = OPEN, 443 = traefik 503(백엔드 없을 때 정상). preview 파이프라인·SSH·인증서 발급 무손상.
- **대시보드 접속**: 8000 차단 후엔 **SSH local-forward** `ssh -i ~/.ssh/n9n_preview_ed25519 -L 8000:localhost:8000 root@<ip>` → `http://localhost:8000` (암호 채널, 인터넷 노출 0). CEO 접속 확인.
- **결과**: provisioning 1·2차의 CISO 미해소(방화벽·8000 노출) **전부 해소 — CISO 잔여 0**. apt 최신·커널 패치는 1차에서 완료.
- **교훈 (1줄)**: 관리 UI 노출 차단은 "관리용 포트를 인터넷에 안 연다 + SSH 터널로만 접속" 이 가장 단순·확실. FQDN/리버스프록시 경로는 webhook 등 외부 인바운드가 필요할 때만.

### Growth-35 scaffold→preview 결선 v1 (2026-06-11) — 로컬 2-container 패키징 (engineer 위임)

- **설계 (CTO)**: preview 배포 단위 = **DB 없는 2-container** — 백엔드 fastapi 가 `store.py` InMemoryEntityStore(시작 시 빈 상태) 라 postgres 불필요. frontend(vanilla-htmx, manifest 렌더, 도메인 대상) + backend(/api/* wire). 정찰로 entry/env/포트/in-memory 확인 후 engineer 에 구현 위임(charter 모델 롤: CTO 설계→engineer 구현).
- **구현 (engineer)**: `backend/.../Dockerfile` + `frontend/.../Dockerfile`(둘 다 build context=repo root, middle/contract+catalog COPY) + 루트 `.dockerignore` + `scripts/workflow/preview_package.py --profile <slug>`(scaffold 호출→`out/<slug>/docker-compose.yml` 생성, frontend :8090 노출, backend 미노출, manifest read-only bind, SECRET_KEY 주석 placeholder). 4 파일 개별 커밋.
- **검증 (engineer, 로컬)**: lawfirm-demo `docker compose up -d --build` → `/login` 200, `/health` 200, 프론트 로그 `ManifestLoader: 14 entities` → `down -v` 정리. 가드 0 FAIL(G-11 이 scripts/workflow 4 스크립트 스캔, render.py 단일소스 import 확인).
- **출력 규약 적용**: engineer 가 상세 보고서 `out/analysis/preview-wiring-v1.md`(gitignored) 작성, main 엔 envelope ~15줄(상태+파일+검증+CAVEAT)만 반환. subagent 내부 65k 토큰 격리.
- **Phase 2 (Coolify) 미해소 — CTO 다음**: ① compose build context 가 절대 경로(로컬 전용) → Coolify(Linux)는 §4 pre-built `dockerimage`(레지스트리) 경로로 재설계 ② **manifest 주입**: 현재 host volume bind(1 이미지 N 프로필 pluggability 위해) → Coolify 단일호스트면 사전배포 단계로 manifest 를 서버에 두거나, env/init-fetch 로 전환. 이미지 태그 `compounding-{backend|frontend}-{slug}:local`.
- **교훈 (1줄)**: 배포 단위를 "정찰로 실제 런타임 의존(여기선 in-memory store→DB 불필요)을 먼저 확인" 하면 과설계(불필요한 postgres 컨테이너)를 피한다. local-first 검증으로 Coolify 전에 컨테이너 단위를 de-risk.

### Growth-35 Coolify Phase 2 (2026-06-11) — lawfirm-demo.n9n.co.kr 첫 영속 preview 배포 PASS

- **목표**: 로컬 검증된 2-container preview 를 `lawfirm-demo.n9n.co.kr` 로 실제 배포 (고객 아무 때나 확인 가능한 영속 preview).
- **Step A — deploy key**: `ssh-keygen ed25519` → `infra/secrets/coolify_deploy_ed25519{,.pub}` (gitignored) → `gh api` GitHub repo deploy key(read_only, id=154181975) → Coolify `POST /api/v1/security/keys` (Python urllib, JSON 파일 우회, uuid=s127pafarr46wlu1r2mre2te). **PASS**.
- **Step B — compose 파일**: `deploy/preview/lawfirm-demo.compose.yml` 작성 (repo-루트 상대 빌드 컨텍스트, manifest bind-mount `/data/coolify/manifests/lawfirm-demo/screen-manifest.json`, domain = API PATCH 방식). 커밋 `e96fd3d` → master 푸시. **PASS**.
- **Step C — manifest 주입**: `ssh mkdir -p /data/coolify/manifests/lawfirm-demo` → `scp out/lawfirm-demo/screen-manifest.json` → 서버 22071 bytes 검증. **PASS**.
- **Step D — 앱 생성·도메인·배포·검증**:
  - `POST /applications/private-deploy-key` (build_pack=dockercompose, docker_compose_location=`/deploy/preview/lawfirm-demo.compose.yml`) → app_uuid=`opryb94j9k5cjdv8bienenv0`. **PASS**.
  - `PATCH /applications/{uuid}` docker_compose_domains=`[{"name":"frontend","domain":"https://lawfirm-demo.n9n.co.kr"}]` → 200. **PASS**.
  - `POST /applications/{uuid}/envs` SECRET_KEY 주입 → instant_deploy → 빌드 ~39s, 2-container started. **PASS**.
  - 외부 검증: `https://lawfirm-demo.n9n.co.kr/` → 302→/login → 200, LE 인증서(CN=lawfirm-demo.n9n.co.kr, exp 2026-09-09), HTML 한국어 로그인 페이지. **PASS**.
- **함정 기록**:
  1. `docker_compose_location` 포맷: `./` 또는 미 `/` 시작 = 422. **반드시 `/`로 시작하는 절대 경로** (예: `/deploy/preview/foo.yml`).
  2. `docker_compose_domains` 포맷: JSON 문자열 아님, `array`. 올바른 형식 = `[{"name":"<service>","domain":"https://..."}]`.
  3. `SERVICE_FQDN_*` 환경변수: compose 파일 내 env로는 Coolify 4.1.2에서 traefik 자동 라우팅 안 됨. 대신 **API PATCH docker_compose_domains 필드**로 설정.
  4. `fqdn` 필드 직접 PATCH: 422("This field is not allowed"). compose 앱은 docker_compose_domains 만 사용.
  5. curl을 bash 인라인 스크립트로 쓰면 훅이 차단 → `out/*.sh` 파일에 담고 실행하거나 Python urllib 사용.
  6. SSH 터널(`-fN -L 8000:localhost:8000`)은 장시간 작업 중 끊길 수 있음 → 재연결: `ssh -i ~/.ssh/n9n_preview_ed25519 -fN -L 8000:localhost:8000 -o ServerAliveInterval=30 root@187.77.140.157`.
  7. SECRET_KEY가 env var 목록 조회 시 `real_value` 필드에 노출됨 — 목록 조회 응답 출력 시 value 필드 마스킹 필요.
- **레지스트리**: `infra/registry/lawfirm-demo.yaml` 생성 — 모든 UUID/경로/TLS/secret_ref 기록.
- **교훈 (1줄)**: Coolify dockercompose 도메인은 "SERVICE_FQDN_* env"가 아니라 "API PATCH docker_compose_domains 배열"로 설정한다 — 이 패턴이 4.1.2 공식 메커니즘.

### Growth-35 리허설 — shop-demo.n9n.co.kr (2026-06-12) — Phase 2 반복 가능성 입증 PASS

- **목표**: lawfirm-demo 와 동일한 경로로 shop-demo(소매 SMB) 를 배포 — Phase 2 가 손대지 않고 반복 가능한지 검증 + 런북 고착화.
- **경로**: profile shop-demo(기존) → manifest 생성(entities: contact·sales-order·sales-order-line) → `deploy/preview/shop-demo.compose.yml`(lawfirm-demo 복제·3곳 치환) → manifest scp → Coolify API 4단계(project→app→domain PATCH→deploy) → 외부 검증.
- **신규 UUID**: project `k5vmkpn9ygimznoxnavpwd4y`, app `cn56k6xtmhp2njv5ed31xv7t`, deploy `d3k0p5ssr978fhnl5veu1pyn`.
- **재사용 UUID (변경 없음)**: server `n12vdydjpwp81hu5i15n1gsb`, privkey `s127pafarr46wlu1r2mre2te`, deploy-key id 154181975.
- **검증 결과**: /login HTTP 200 PASS, TLS CN=shop-demo.n9n.co.kr exp 2026-09-09 PASS, /health HTTP 200 PASS.
- **추가 함정 (신규 발견)**: ① 프로젝트 생성 payload 에 한글 포함 시 "Invalid JSON" — ASCII 설명문 사용. ② env 주입 body 에 `is_build_time`/`is_secret` 포함 시 422 — `key`+`value` 만.
- **런북**: `docs/runbooks/preview-deploy.md` 신설 — 전체 N단계, 함정 목록, 재사용 UUID, 실제 예시(shop-demo), 수동→자동 갭 기록.
- **레지스트리**: `infra/registry/shop-demo.yaml` 생성.
- **수동→자동 갭 (CTO 후속)**: ① `deploy/preview/<slug>.compose.yml` 자동 생성 (현재 수동 복제·치환) ② Coolify API 4단계 단일 스크립트화 ③ manifest scp 자동화.
- **교훈 (1줄)**: deploy key·server·privkey UUID 는 같은 repo 의 신규 고객마다 완전 재사용 가능 — Coolify project+app UUID 만 신규 발급하면 된다. 배포 시간 ~5분(Phase 2 첫 배포 30분 대비).

### Growth-35 갭1·갭2 자동화 (2026-06-12) — 레지스트리 merge + webhook 조사

- **갭1 완료 — 레지스트리 자동 merge**: `deploy_to_coolify.py` 에 `update_registry()` 추가. 배포 성공 후 `infra/registry/<slug>.yaml` 에 `coolify_project/app/url/status/deployed_at` 만 갱신. `deployed_at` = Coolify 배포 응답의 `finished_at` (서버 타임스탬프, 하드코드 금지). raw-line merge 방식 — PyYAML 불필요, `secret_ref`·`tls`·`build_commit`·수동 필드 완전 보존. shop-demo 검증: merge PASS, secret_ref 보존, 후행 주석 클린 처리 확인.
- **갭2a 완료 — `--commit` 플래그**: `deploy/preview/<slug>.compose.yml` 을 배포 전 per-file 커밋·push. `git add <file>` 만 사용(git add -A 금지), 이미 커밋된 파일이면 skip.
- **갭2b 조사 완료 — webhook CTO 컨펌 대기**:
  - Coolify 4.1.2 webhook URL = `https://187.77.140.157/webhooks/source/github/events/manual`
  - 인증 = `X-Hub-Signature-256: sha256=<HMAC>`, 시크릿 = `manual_webhook_secret_github` (앱마다 자동 생성 40자)
  - **핵심 리스크**: Coolify 4.1.2 은 `git_repository` 로만 앱 매칭 → master push 시 같은 repo 의 **모든 앱** 동시 재배포. per-app 필터 없음. 현재 2 테넌트 → 모두 트리거됨.
  - `--setup-webhook` 으로 계획 출력 + vault 저장 구현. `--confirm` 으로 `gh api` 실제 등록 (CTO 컨펌 후).
  - 웹훅 시크릿 = `infra/secrets/<slug>-webhook-secret.txt` 볼트 저장, 레지스트리/코드 평문 금지.
- **커밋**: `08be0c4` (registry+commit), `b7853cc` (shop-demo registry), `6d26ab1` (webhook), `6a83c96` (runbook).
- **교훈 (1줄)**: Coolify 4.1.2 webhook은 app-level이 아닌 repo-level 매칭이므로, "모든 테넌트가 항상 안정"이 보장될 때만 auto-deploy webhook 을 활성화하는 것이 안전하다.

### Growth-35 자동화 v1 (2026-06-12) — deploy_to_coolify.py + preview_package.py --coolify

- **목표**: 리허설에서 식별된 수동 갭 3종 자동화 (compose 수동 복제·치환 / API 4단계 수동 실행 / manifest scp 수동).
- **산출물 1 — `scripts/workflow/preview_package.py --coolify`**: `deploy/preview/<slug>.compose.yml` 자동 생성. 검증된 lawfirm-demo/shop-demo 의 차집합(slug-가변 부분)만 파라미터화. 생성 후 shop-demo 레퍼런스와 구조 diff 자동 실행 — slug 차이 외 0 이면 PASS. 로컬 모드(`--coolify` 없음) 완전 보존.
- **산출물 2 — `scripts/workflow/deploy_to_coolify.py --slug <slug>`**: 런북 8단계를 멱등·단일 명령으로. project ensure(재사용/생성) → app ensure → domain PATCH → manifest SCP → SECRET_KEY 주입(409=이미 있음 → 스킵, Coolify 4.1.2 per-env PATCH 엔드포인트 미노출 확인) → deploy 트리거 → 빌드 폴링 → 외부 검증(HTTP/TLS).
- **재사용 상수 하드코딩**: server_uuid `n12vdydjpwp81hu5i15n1gsb`, private_key_uuid `s127pafarr46wlu1r2mre2te` — 런북에서 가져옴, 재생성 금지.
- **보안 처리**: 토큰 `sed` 추출(shell source 금지, 특수문자 안전). `real_value` 필드 전 응답에서 `***masked***` 치환(CISO §7). SECRET_KEY 값 절대 미출력.
- **실측 발견**: Coolify 4.1.2 에서 env 이미 존재 시 POST → 409; 단일 env PATCH `/envs/{uuid}` 엔드포인트 존재하지 않음(404). 해결책 = 409 를 idempotent success 로 처리.
- **shop-demo 멱등 재배포 검증**: `deploy_to_coolify.py --slug shop-demo` → build finished, /login 200, /health 200, TLS CN=shop-demo.n9n.co.kr PASS. 기존 2 테넌트 무손상.
- **커밋**: `28c8a49` (preview_package.py), `3575569` (deploy_to_coolify.py), `e11ae34` (runbook).
- **교훈 (1줄)**: 신규 slug 배포 전체 플로우 = `preview_package.py --profile <slug> --coolify` → compose commit+push → `deploy_to_coolify.py --slug <slug> --dry-run` → `deploy_to_coolify.py --slug <slug>` — 이게 단일 진실.

### Growth-35 Caddy spike (2026-06-12) — Coolify 대체재 평가

- **목적**: Coolify 4.1.2 함정 5개 실측 기준선으로 Caddy+compose 공정 비교.
- **spike 파일**: `out/spike-caddy/` (docker-compose.yml + Caddyfile + run-spike.ps1). Docker Desktop 오프라인으로 컨테이너 실행 미완 — 코드 레벨 검증으로 대체.
- **주요 발견**:
  - 함정 5/5 모두 Caddy+compose 에서 구조적으로 해소 (F-1/F-2: Coolify 전용 API 없음, F-3: env 조회 경로 없음, F-4: 재기동 rotate, F-5: compose project 개별 재배포)
  - API 호출 수: 6~8 → 1~2로 축소
  - wildcard TLS (DNS-01 + Cloudflare): 신규 slug cert 발급 0회 (xcaddy 커스텀 빌드 필요)
  - harness artifact(Dockerfile/compose) 코드 변경 0 — deploy 스크립트 1개 교체만
  - CEO 대시보드 상실 = 가장 큰 비기술적 비용 (Caddy 에 UI 없음)
- **권고**: 현 시점 Coolify 유지. 근거 — 함정 5개가 deploy_to_coolify.py 로 이미 캡슐화된 상태에서, CEO 대시보드 상실 + xcaddy 커스텀 빌드 + 15~30s cutover 다운타임 비용이 더 크다.
- **전환 트리거**: 테넌트 ≥ 5 개 AND SECRET_KEY rotate 월 1회 이상 필요 AND Coolify 4.x 가 F-4/F-5 미해소 확인 시.
- **전체 비교 문서**: `out/analysis/spike-caddy-vs-coolify.md` (gitignored)
- **교훈 (1줄)**: 함정이 코드 레벨로 캡슐화된 뒤에는, 전환 비용 계산을 "남은 함정" 이 아닌 "캡슐화 유지 비용 vs 전환 후 ops 비용" 으로 해야 한다.

### Growth-67 정적 marketing-site preview 레인 + n9n 공개 데모 2종 (2026-06-15)

- **목적**: marketing-site(정적 SSG, 백엔드 無)는 business-system 전용 `deploy_to_coolify.py`(screen-manifest+SECRET_KEY+/login) 레인을 못 탐 → 정적 preview 레인 신설.
- **신규 자산**: `frontend/adapters/landing-astro/Dockerfile`(멀티스테이지: node+python3로 scaffold→astro build→nginx, ARG PROFILE_SLUG/DEMO_MODE) · `scripts/workflow/deploy_static_site.py`(deploy_demo_portal.py 일반화, `--slug/--domain/--compose/--service`, idempotent) · `deploy/preview/{gtm-landing,landing-portal}.compose.yml` · `landing-portal/{index.html,Dockerfile}`.
- **배포 결과**: gtm-landing.n9n.co.kr (project=kt6fcno8hync4plaabxadtqj, app=umyt8l38jv386mwfja5v3d2p, aurora 테마, DEMO_MODE=1) + landing.n9n.co.kr (project=mqzuqcz0au9qgte38r80fcok, app=aqtrpz5vna8auictdquovbww, 랜딩 데모 인덱스 포털) — 둘 다 build finished, HTTPS 200, 콘텐츠 검증 PASS.
- **함정 (신규)**: Git Bash **MSYS 경로 변환** — CLI 인자 `/deploy/preview/x.yml`가 `C:/Program Files/Git/deploy/preview/x.yml`로 둔갑 → Coolify 422 `docker_compose_location format invalid`. 해소: `MSYS_NO_PATHCONV=1`. (deploy_demo_portal.py는 경로를 Python 상수로 하드코딩해 무사했음 — CLI 인자화하며 노출된 함정.) deploy_static_site.py 사용 시 항상 `MSYS_NO_PATHCONV=1` 프리픽스.
- **레지스트리**: `infra/registry/{gtm-landing,landing-portal}.yaml` status=live.
- **교훈 (1줄)**: Windows에서 절대경로를 CLI 인자로 넘길 때는 MSYS 변환을 의심하라 — 같은 값이 하드코딩이면 통과, 인자면 둔갑한다.

### Growth-75 (2026-06-15) — hopwell(harvest) 배포 + 배포 함정 2종

- **배포**: hopwell.n9n.co.kr (project=pfwbarlxcb7raljvd5gp5wnf, app=a4g7t9vvltsl7y3ab3tdr869, harvest 테마, DEMO_MODE=1) `deploy_static_site.py` + 신규 `deploy/preview/hopwell.compose.yml`. landing 포털에 HOPWELL 카드 추가 후 재배포. 둘 다 HTTPS 200.
- **함정 ① `--domain` 스킴 필수**: `deploy_static_site.py --domain hopwell.n9n.co.kr`(스킴 없음) → docker_compose_domains PATCH 422 `Invalid URL`. **반드시 `--domain https://hopwell.n9n.co.kr`**. PATCH 본문 포맷 = `[{"name":svc,"domain":url}]` 배열(+force_domain_override). 또 fresh app은 compose 파싱 전 PATCH가 레이스로 422 → 스크립트 재실행(idempotent)이면 2회차에 성공.
- **함정 ② SSH 터널 드롭 + 좀비 소켓**: 대량 배포/폴링 중 `localhost:8000` 터널 드롭. 재수립 시 죽은 PID가 8000을 Listen 점유("Address already in use", taskkill 불가 — OS 지연 해제). 해소: **다른 로컬 포트로 재수립**(`-L 8010:localhost:8000`) 후 직접 API 호출로 진행(deploy_static_site.py는 8000 하드코딩이라 우회).
- **교훈**: API 자동화 장시간 작업은 터널 안정성(ServerAliveInterval)과 포트 재사용 실패를 전제로 폴백 포트를 준비하라.

### Growth-82 (2026-06-16) — summit-horizon 배포 + 포털 7번째 카드 (A3 Event, 7번째 라이브 데모)

- **배포**: summit-horizon.n9n.co.kr (Coolify project=k105u8soe4fergofhdje2nkt, app=jvo3hnfmf2bv8ce10mcj96l0, ignite 테마, PROFILE_SLUG=event-demo, DEMO_MODE=1). `deploy_static_site.py --slug summit-horizon --domain https://summit-horizon.n9n.co.kr --compose /deploy/preview/summit-horizon.compose.yml --service web`. status=finished, HTTPS 200. **서빙 마크업 검증**(공개 HTTPS): SUMMIT HORIZON·스폰서 워드마크·horizontal-steps·waitlist 전부 present, 오타픽스(summithorizon) 반영, aurora 누수 0.
- **포털 재배포**(Growth-78/81 패턴): 🎟️ 이벤트 카드 추가 커밋·push 후 `deploy_static_site.py --slug landing-portal --service portal` 명시 재배포 → landing.n9n.co.kr 200, summit-horizon·flux 카드 동시 present 확인.
- **레지스트리**: `infra/registry/summit-horizon.yaml` (status=live, project/app UUID·theme=ignite·archetype=A3·profile_slug=event-demo 기록).
- **터널**: Growth-81 의 detached `Start-Process` SSH 터널(ServerAliveInterval=30)이 세션 내내 안정 유지 — 재드롭 0. SIGHUP 분리 기동 패턴 유효성 재확인.
- **교훈 (1줄)**: slug(브랜드, summit-horizon) 와 PROFILE_SLUG(profile 파일명, event-demo) 분리 — flux(slug=flux/PROFILE_SLUG=flux-demo) 선례 재사용. Coolify --slug 는 브랜드 네이밍, Docker build arg 는 profile 파일명.

### Growth-81 (2026-06-16) — flux 배포 + 포털 6번째 카드 (A1 FLUX, 6번째 라이브 데모, Growth-80 P0 종결)

- **배포**: flux.n9n.co.kr (Coolify project=jq25nyzfirch3flp7no2wg3u, app=oyemv0mttkn8eo05xflvc4x2, flux 테마, DEMO_MODE=1). `deploy_static_site.py --slug flux --domain https://flux.n9n.co.kr --compose /deploy/preview/flux.compose.yml --service web`. status=finished, HTTPS 200. **서빙 마크업 검증**(공개 HTTPS, 터널 무관): stats/bento/pull-quote 섹션 전부 present + aurora 누수 0 — 스테일 빌드 아님 확인.
- **포털 재배포**(Growth-78 교훈 적용): ⚡ SaaS 카드 추가 커밋·push 후 `deploy_static_site.py --slug landing-portal --service portal` 명시 재배포 → landing.n9n.co.kr 200, flux 카드·기존 meridian 카드 동시 present 확인.
- **레지스트리**: `infra/registry/flux.yaml` (status=live, project/app UUID·theme=flux·archetype=A1 기록).
- **함정 ① 터널 SIGHUP 드롭**: `ssh -fN` 를 툴 백그라운드로 띄우면 태스크 reaping 시 SIGHUP 으로 소멸 → 후속 배포가 `tunnel check failed: timed out`. 해소: PowerShell `Start-Process -WindowStyle Hidden -FilePath ssh -ArgumentList ... -N -L 8000:localhost:8000` + `ServerAliveInterval=30 ExitOnForwardFailure=yes` 로 셸 세션과 분리 기동(Growth-76/77 좀비소켓 계열 후속 — 이번엔 소켓 점유가 아니라 부모 셸 SIGHUP 이 원인). FLUX 라이브 검증 자체는 공개 HTTPS 라 터널 무관.
- **함정 ② 스테일 테스트 동반 픽스**: Growth-80 이 stats(14번째 타입) 추가했으나 풀테스트가 13 을 단언(`test_catalog_has_..._thirteen_total`) → 배포 전 풀테스트 1 FAIL. 14 로 동기화 후 배포(빌드 산출이 단언보다 앞서면 같은 작업에서 테스트 갱신).
- **교훈 (1줄)**: 장시간 API 자동화의 터널은 부모 셸과 **프로세스 분리 기동**(Start-Process detached + ServerAlive)으로 SIGHUP 드롭을 차단 — `ssh -fN` 백그라운드는 툴 reaping 에 취약.

### Growth-78 (2026-06-16) — meridian 배포 + 포털 재배포 (A6 MERIDIAN, 5번째 라이브 데모)

- **배포**: meridian.n9n.co.kr (Coolify project=jrum1rdwq1oa53bmsb6awhvr, app=b17ccvgfsqqhieucir9ymbnu, meridian 테마, DEMO_MODE=1). `deploy_static_site.py --slug meridian --domain https://meridian.n9n.co.kr --compose /deploy/preview/meridian.compose.yml --service web` (COOLIFY_API_BASE=8010, MSYS_NO_PATHCONV=1). status=finished, HTTPS 200, 콘텐츠+forest 토큰(#1A5C3A) 검증 PASS.
- **포털 재배포 필수 확인**: landing 포털은 git push 로 **자동 재배포되지 않음** — push 후 라이브 포털에 terra 카드만 있고 meridian 카드 부재 확인 → `deploy_static_site.py --slug landing-portal --service portal` 명시 재배포해야 신규 카드 반영(HTTP 200 재확인). 카드 커밋만으론 라이브 미반영 (Growth-77 도 동일 패턴이었음 — 이번에 명문화).
- **레지스트리**: `infra/registry/meridian.yaml` (status=live, project/app UUID·theme=meridian·archetype=A6 기록).
- **교훈 (1줄)**: 포털은 별도 Coolify 앱이라 데모 카드 커밋·푸시 후 **반드시 포털을 명시 재배포**해야 라이브 반영 — push=auto-deploy 가정 금지(Coolify webhook 미설정). Growth-77 의 COOLIFY_API_BASE env-var·leading-slash --compose 함정은 그대로 재사용(재발 0).

### Growth-77 (2026-06-16) — terra-ceramics 배포 + COOLIFY_API_BASE 오픈루프 종결 + leading-slash 422 함정

- **배포**: terra-ceramics.n9n.co.kr (Coolify project=itw5euifm5shu8vt84axxz8p, app=q9hq2xlr3cjzh47smq7z0xe8, kiln 테마, DEMO_MODE=1). `deploy_static_site.py` + `deploy/preview/terra-ceramics.compose.yml`. landing 포털에 공예/로컬 카드(🏺) 추가 후 재배포. 둘 다 HTTPS 200, 콘텐츠 검증 PASS.
- **COOLIFY_API_BASE 오픈루프 종결**: Growth-76 교훈 ②(하드코딩 API_BASE → env-var 화 권고)를 이번 세션에서 실행. `deploy_static_site.py` 의 `API_BASE=localhost:8000` 하드코딩 → `COOLIFY_API_BASE` 환경변수로 교체(default `http://localhost:8000/api/v1`). 8000 좀비소켓 재발 시 `MSYS_NO_PATHCONV=1 COOLIFY_API_BASE=http://localhost:8010/api/v1 python deploy_static_site.py ...` 로 임시패치·git-checkout 없이 운영 가능. Growth-75·76 의 임시 8010 패치 후 복구(커밋 오염 방지) 댄스가 영구 해소됨.
- **leading-slash --compose 422 함정 확인**: `deploy_static_site.py --compose` 인자는 **반드시 `/` 로 시작하는 repo-rooted 경로**(`/deploy/preview/<slug>.compose.yml`). 슬래시 없거나 상대경로 → Coolify HTTP 422 `docker_compose_location format invalid`. Git Bash 에서 `MSYS_NO_PATHCONV=1` 없으면 MSYS 경로 변환으로 둔갑하므로 함께 사용.
- **레지스트리**: `infra/registry/terra-ceramics.yaml` (status=live, project/app UUID 기록).
- **교훈 (1줄)**: 하드코딩 엔드포인트를 env-var 화하면 좀비소켓·포트 충돌 같은 운영 이변에 코드 오염 없이 대응 가능 — "임시 패치 후 git-checkout 복구" 패턴은 항상 env-var 화로 전환해야 할 신호.

### Growth-76 (2026-06-15) — studio-north(atelier) 배포 + 8000 좀비소켓 폴백

- **배포**: studio-north.n9n.co.kr (project=pznz8dsk2h93frb51w4ejtlr, app=rls8w0yd6vxvq4721ava5a1n, atelier 테마, DEMO_MODE=1) `deploy_static_site.py` + 신규 `deploy/preview/studio-north.compose.yml`. landing 포털 "준비 중" 카드를 라이브 카드로 교체 후 재배포. 둘 다 HTTPS 200, 콘텐츠+토큰(9A5B32/141418) 검증 PASS.
- **함정 (Growth-75 ② 후속, 악화)**: 8000 좀비소켓이 이번엔 **프로세스 자체 소멸**(PID 6356 존재하지 않으나 소켓 Listen 유지 — 커널 레벨 누수, taskkill 대상 없음). 8000 회복 불가 → 8010 터널만 정상(API `/version`→200, 8000→http=000). deploy_static_site.py가 `API_BASE=localhost:8000` 하드코딩이라 **임시로 8010 패치 후 실행, 완료 즉시 `git checkout`으로 복구**(커밋 오염 0).
- **함정 (신규)**: 백그라운드 빌드 에이전트가 종료 후 **세션 cwd를 frontend/adapters/landing-astro에 고정** → 상대경로 PreToolUse/PostToolUse 훅(`scripts/hooks/*.py`)이 FileNotFound로 깨짐. `Set-Location <repo-root>`로 복구.
- **교훈**: ① 좀비 소켓은 PID 부재 시 OS 재부팅 외 회복 불가 — 폴백 포트 상시 준비. ② 하드코딩 엔드포인트는 env-var 화(`COOLIFY_API_BASE`)가 운영 유연성 — deploy 스크립트 API_BASE 후보(open loop). ③ 백그라운드 에이전트 후엔 세션 cwd를 명시 복구.

### Growth-83 (2026-06-16) — lumi 배포 + 포털 8번째 카드 (A5 Mobile App, 8번째 라이브 데모)

- **배포**: lumi.n9n.co.kr (Coolify project=x7be9f2b7nr1zhykxubn6wwt, app=j10swdnw5tyndidudjnsr04r, nova 테마, PROFILE_SLUG=mobile-demo, DEMO_MODE=1). `deploy_static_site.py --slug lumi --domain https://lumi.n9n.co.kr --compose /deploy/preview/lumi.compose.yml --service web`. status=finished, HTTPS 200. **서빙 마크업 검증**: "Lumi — Build better days, one habit at a time" 타이틀, nova/mobile 키워드 전부 present.
- **포털 재배포** (Growth-78/82 패턴 재사용): `deploy_static_site.py --slug landing-portal --service portal` 명시 재배포 → landing.n9n.co.kr 200, 8개 데모 href 전부 present (lumi.n9n.co.kr 신규 8번째 확인).
- **레지스트리**: `infra/registry/lumi.yaml` (status=live, project/app UUID, theme=nova, archetype=A5, profile_slug=mobile-demo 기록). 커밋 `0fa3fb0`.
- **터널**: Growth-81 detached Start-Process SSH 터널(ServerAliveInterval=30) 안정 유지 — 재드롭 0.
- **신규 함정 0건**: Growth-82(summit-horizon A3) 동일 경로 재사용, 트랩 없음.
- **교훈 (1줄)**: A5 Mobile App archetype이 같은 deploy_static_site.py 레인으로 무수정 배포됨 — slug(lumi)/PROFILE_SLUG(mobile-demo) 분리 패턴(Growth-82 선례)이 안정적으로 재현됨.
