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
| preview VPS — 8000 노출 차단 | 2026-06-11 | harden (3차) | **검증 PASS** — 클라우드 방화벽 allow-list, 8000/8080/6001/6002 외부 차단 실측, 22/80/443 유지. CISO 잔여 0 | $0 |
| 로컬 (preview 패키징) | 2026-06-11 | package (scaffold 결선) | **검증 PASS** — profile→2-container compose, lawfirm-demo /login·/health 200, manifest 14 entities. Coolify 배포는 Phase 2 | $0 |

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
