# Legal RAG — Coolify Preview 배포 실행 체크리스트

> 단일 진실: DevOps 인격이 유지. 변경 시 커밋 + `docs/learn-logs/devops.md` 갱신.
> 대상 URL: https://legal-rag.n9n.co.kr
> Compose 파일: `deploy/preview/legal-rag.compose.yml`
> 레지스트리: `infra/registry/legal-rag.yaml`
> 설치 전체 절차(DB·하드닝·검증): `docs/runbooks/legal-rag-install.md` 참조 — 중복 기술 없음.

---

## 차단 요인 (배포 전 필수 해결)

아래 항목이 하나라도 미완료이면 배포를 시작하지 않는다.

| ID | 항목 | 담당 | 상태 |
|---|---|---|---|
| **B1** | `services/legal-rag/Dockerfile` 생성 (engineer) | engineer | OPEN |
| **B2** | 임베딩 사이드카 thin adapter 이미지 확정·빌드 (engineer) — 상세는 §0 | engineer | OPEN |
| **B3** | pg_bigm 포함 여부 결정: `pgvector/pgvector:pg16` 그대로 vs `Dockerfile.db` 커스텀 빌드 | founder | OPEN |
| **B4** | VPS 디렉터리 사전 생성 (§1-A) | founder | OPEN |
| **B5** | DDL + seed 적용 — legal-rag-install.md §4 전체 (01~08 augment + seed 4종) | founder | OPEN |
| **B6** | Cloudflare DNS 레코드 추가 (§5) | founder | OPEN |

---

## §0 임베딩 사이드카 결정 (B2 상세)

`embed_client.py` 가 요구하는 contract:

```
POST /embed        {"text": str}           → {"embedding": [float x 768], "model": str}
POST /embed/batch  {"texts": [str, ...]}   → {"embeddings": [[float x 768], ...], "model": str}
GET  /health                               → 200 OK
```

**판정: 현재 공개된 off-the-shelf 이미지 중 이 contract 를 그대로 만족하는 것 없음.**

| 이미지 | /embed 경로 | 응답 키 | 768-dim 모델 | 판정 |
|---|---|---|---|---|
| `ghcr.io/huggingface/text-embeddings-inference` | `/embed` (일치) | `[[float...]]` 배열 직접 반환 (불일치 — `{"embeddings":...}` 래퍼 없음) | `intfloat/multilingual-e5-base` 등 | thin adapter 필요 |
| `ollama/ollama` | `/api/embeddings` (불일치) | `{"embedding":[...]}` (단수, `/embed/batch` 없음) | `nomic-embed-text` 768-dim | thin adapter 필요 |
| `embeddinggemma` | contract 기준 (일치 추정) | 공개 Docker Hub 이미지 없음 | 768-dim 명시 | 이미지 출처 확인 필요 |

**engineer 권장 경로**: TEI(`intfloat/multilingual-e5-base`) 를 백엔드로 하는 thin FastAPI 어댑터 빌드.
- 어댑터 위치: `services/legal-rag/embed-adapter/`
- 어댑터가 TEI `/embed` 를 호출하고 응답을 `{"embedding":...}` / `{"embeddings":...}` 형식으로 변환
- compose 의 `embed` 서비스를 `busybox placeholder` 에서 실제 빌드 블록으로 교체

---

## §1 배포 전 준비 [FOUNDER]

### A. VPS 인바운드 디렉터리 생성

```bash
# SSH 접속 (SSH 포워딩 없이 직접)
ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157 \
  'mkdir -p /data/legal-rag/ingest && ls -la /data/legal-rag/'
```

ingest 볼륨 마운트 소스 경로(`/data/legal-rag/ingest`)는 compose 실행 전 존재해야 한다.
Docker 가 먼저 빈 디렉터리를 생성하면 bind-mount 타입 볼륨이 깨진다.

### B. 시크릿 생성 및 Coolify 볼트 입력

**로컬에서 시크릿 값 생성**:

```bash
# JWT_SECRET (64-char hex)
python3 -c "import secrets; print(secrets.token_hex(64))"

# SERVICE_TOKEN (32-char hex)
python3 -c "import secrets; print(secrets.token_hex(32))"

# DB 패스워드 (app_service 롤용)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

생성한 값을 `infra/secrets/` 아래 gitignored 파일에 저장 (볼트):

```
infra/secrets/legal-rag-jwt-secret.txt       — LEGAL_RAG_JWT_SECRET
infra/secrets/legal-rag-service-token.txt    — LEGAL_RAG_SERVICE_TOKEN
infra/secrets/legal-rag-db-dsn.txt           — LEGAL_RAG_DB_DSN (postgresql://app_service:pw@db:5432/legaldb)
infra/secrets/legal-rag-postgres-password.txt — LEGAL_RAG_POSTGRES_PASSWORD
```

**Coolify UI 환경변수 패널에서 설정** (앱 생성 후, deploy 전):

| 변수 | 값 출처 |
|---|---|
| `LEGAL_RAG_DB_DSN` | `postgresql://app_service:<pw>@db:5432/legaldb` (db 서비스 이름 사용) |
| `LEGAL_RAG_POSTGRES_USER` | `app_service` |
| `LEGAL_RAG_POSTGRES_PASSWORD` | 볼트 값 |
| `LEGAL_RAG_JWT_SECRET` | 볼트 값 |
| `LEGAL_RAG_SERVICE_TOKEN` | 볼트 값 |
| `LEGAL_RAG_INGEST_ROOT` | `/data/legal-docs` (컨테이너 내 mount target) |

선택 변수는 기본값이 있으므로 초기 배포 시 생략 가능.

### C. DDL + Seed 적용

`docs/runbooks/legal-rag-install.md §4` 전체를 따른다.
compose 의 `db` 컨테이너가 기동된 **이후** 적용하거나, 외부 Postgres 서버에 먼저 적용 후 DSN 을 그 서버로 설정한다.

preview 티어는 compose 내 `db` 컨테이너를 사용하므로, 컨테이너 기동 후 `docker exec` 로 적용:

```bash
# VPS SSH 접속 후
# Coolify 가 컨테이너를 시작한 뒤 (deploy 후)
docker exec -i <db-container-id> psql -U app_service -d legaldb \
  < presets/ddl/augments/legal/01_extensions.sql
# ... 02~08, seed 4종 순서대로
```

또는 deploy_to_coolify.py 실행 전 외부 Postgres 를 미리 프로비저닝하고 DSN 을 그쪽으로 지정한다.

---

## §2 dry-run 검증 [FOUNDER]

```bash
# SSH 포워딩 활성 확인
curl -s --max-time 3 http://localhost:8000/api/v1/healthcheck
# 기대: {"message":"Not found.",...}  (404 = 터널 살아있음)

# 죽어있으면 재활성
ssh -i ~/.ssh/n9n_preview_ed25519 -fN \
  -o ServerAliveInterval=30 \
  -L 8000:localhost:8000 \
  root@187.77.140.157

# dry-run (no API 변경)
PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py \
  --slug legal-rag \
  --skip-scp \
  --entry-path /health \
  --dry-run
```

`--skip-scp`: legal-rag 는 screen-manifest 없음 (레지스트리 `manifest_server_path: null`).
`--entry-path /health`: UI 없음, health endpoint 가 라이브 검증 기준.

dry-run 출력에서 확인:
- compose_location: `/deploy/preview/legal-rag.compose.yml` (슬래시 시작 필수)
- domain service name: `app` (레지스트리 `domain_service: app` 반영)
- 모든 시크릿 값이 `***` 로 마스킹되어 있는지

---

## §3 실 배포 [FOUNDER]

B1~B4 블로커 해소, dry-run PASS 후 실행.

```bash
PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py \
  --slug legal-rag \
  --skip-scp \
  --entry-path /health
```

스크립트가 자동으로:
1. 미푸시 커밋 자동 push (Coolify 는 GitHub 에서 pull — 로컬 커밋 push 필수)
2. SSH 터널 확인
3. Coolify 프로젝트/앱 생성 또는 재사용 (idempotent)
4. domain PATCH: `legal-rag.n9n.co.kr → app 서비스`
5. 배포 트리거 + 빌드 폴 (5분 타임아웃)
6. `/health` HTTP 200 + TLS CN 검증
7. `infra/registry/legal-rag.yaml` 에 `coolify_project`, `coolify_app`, `status: live`, `deployed_at` 자동 기록

---

## §4 deploy 후 Coolify UI에서 직접 수행 [FOUNDER]

deploy_to_coolify.py 가 처리하지 않는 항목:

1. Coolify UI > 앱 > Environment Variables 패널에서 §1-B 의 시크릿 6종 입력 확인
2. 환경변수 적용 후 **Redeploy** (env 변경이 적용된 빌드가 아니라면)
3. Coolify UI > 앱 > Logs 에서 빌드/런타임 오류 없음 확인

---

## §5 DNS [FOUNDER]

Cloudflare 대시보드에서:

```
Type: A
Name: legal-rag
Value: 187.77.140.157
TTL: Auto
Proxy: DNS only (orange cloud OFF — Coolify TLS 종단 직접)
```

또는 와일드카드 `*.n9n.co.kr A 187.77.140.157` 이 이미 있으면 서브도메인 레코드 불필요.
현재 와일드카드 존재 여부: `deployment-topology.md` 참조.

---

## §6 라이브 검증 [FOUNDER]

```bash
SLUG=legal-rag

# 1. Shallow health (200이어야 함)
curl -s -o /dev/null -w "HTTP %{http_code}" --max-time 15 \
  "https://${SLUG}.n9n.co.kr/health"

# 2. TLS 인증서 확인
echo | openssl s_client -connect ${SLUG}.n9n.co.kr:443 \
  -servername ${SLUG}.n9n.co.kr 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
# 기대: CN=legal-rag.n9n.co.kr, issuer=Let's Encrypt

# 3. 로그인 e2e (seed 적용 후)
BASE="https://${SLUG}.n9n.co.kr"
TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"lee.junho@example-lawfirm.kr","password":"demo1234!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "TOKEN: ${TOKEN:0:20}..."

# 4. 검색 e2e
curl -s -X POST "$BASE/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "계속적 공급계약 해지 기회손실", "top_k": 3}' \
  | python3 -m json.tool

# 5. rate-limit 검증 (6번째 요청부터 429)
for i in $(seq 1 8); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"bad@test.com","password":"bad"}')
  echo "Request $i: $STATUS"
done
# 기대: 1~5 = 401/422, 6~8 = 429

# 6. 통합 테스트 (실 Postgres + 사이드카 기동 후)
cd services/legal-rag
LEGAL_RAG_DB_DSN_POSTGRES="postgresql://app_service:<pw>@187.77.140.157:5432/legaldb" \
  pytest tests/ -m postgres -v
```

---

## §7 배포 완료 후 레지스트리 확인 [FOUNDER]

deploy_to_coolify.py 가 자동 업데이트하지만, 수동으로 아래 필드를 확인·보완한다:

```yaml
# infra/registry/legal-rag.yaml 에서 확인
preview:
  coolify_project: <uuid 채워졌는지>
  coolify_app: <uuid 채워졌는지>
  status: live
  deployed_at: "<날짜>"
  tls: "Let's Encrypt, CN=legal-rag.n9n.co.kr, exp <날짜>"  # 수동 기입
  build_commit: <git sha>  # 수동 기입
```

레지스트리 업데이트 후 파일당 별도 커밋 (CLAUDE.md §9 규칙):

```bash
git add infra/registry/legal-rag.yaml
git commit -m "chore(registry): mark legal-rag preview live — <날짜>

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git push origin master
```
