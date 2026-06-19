# Legal RAG — Coolify Preview 배포 실행 체크리스트

> 단일 진실: DevOps 인격이 유지. 변경 시 커밋 + `docs/learn-logs/devops.md` 갱신.
> 대상 URL: https://legal-rag.n9n.co.kr
> Compose 파일: `deploy/preview/legal-rag.compose.yml`
> 레지스트리: `infra/registry/legal-rag.yaml`
> 설치 전체 절차(DB 롤·하드닝·RLS 검증): `docs/runbooks/legal-rag-install.md` 참조 — 중복 기술 없음.
> 인프라 토폴로지: yesnic 도메인 → Cloudflare DNS → Hostinger VPS 187.77.140.157 → Coolify → Traefik

---

## 이미 완료된 항목 (재작업 금지)

Growth-92/93 에서 완성된 아티팩트. Founder 가 재빌드하거나 수정하지 않는다.

| 완료 항목 | 위치 |
|---|---|
| 4-컨테이너 Compose (db·tei·embed·app) | `deploy/preview/legal-rag.compose.yml` |
| embed-adapter Dockerfile + shim 코드 | `services/legal-rag/embed-adapter/` |
| app Dockerfile | `services/legal-rag/Dockerfile` |
| DDL 01~08 + seed 4종 | `presets/ddl/augments/legal/` |
| 49개 서비스 테스트 | `services/legal-rag/tests/` |
| 디지털 자산 레지스트리 초안 | `infra/registry/legal-rag.yaml` |

---

## 차단 요인 (배포 전 필수 — 아래 순서대로)

| ID | 항목 | 담당 | 상태 |
|---|---|---|---|
| **B3** | pg_bigm: preview 는 `pgvector/pgvector:pg16` 그대로 사용 결정 완료 (pg_bigm 없음 — Korean FTS 품질 저하는 데모 수용 범위) | founder 결정 필요 | OPEN |
| **B4** | VPS 인바운드 디렉터리 사전 생성 (§1-A) | [FOUNDER] | OPEN |
| **B5** | Coolify 환경변수 패널 시크릿 6종 입력 (§1-B) | [FOUNDER] | OPEN |
| **B6** | Cloudflare DNS 레코드 추가 (§1-C) | [FOUNDER] | OPEN |
| **B7** | DDL + seed 적용 — deploy 후 `db` 컨테이너 대상 (§1-D) | [FOUNDER] | OPEN |

> B1(Dockerfile)·B2(embed-adapter) 는 engineer 가 완료. 목록에서 제거.
> B3 는 "pg_bigm 없음=demo 품질" 을 founder 가 수용한다고 표시하면 닫힌다.

---

## §0 4-컨테이너 토폴로지 (참조)

```
[Traefik TLS] → app:8000 (FastAPI)
                    ↓ LEGAL_RAG_EMBED_URL=http://embed:8080
               embed:8080 (FastAPI shim — embed-adapter)
                    ↓ TEI_BASE_URL=http://tei:80
               tei:80  (HuggingFace TEI, CPU, intfloat/multilingual-e5-base)
               db:5432 (pgvector/pgvector:pg16)
```

- `db`, `tei`, `embed` 는 외부 포트 없음 — Coolify uuid-net 내부 전용.
- `app` → Traefik 라우팅 → TLS (Let's Encrypt).
- `LEGAL_RAG_EMBED_URL` 은 shim(`embed:8080`)을 가리킨다. `tei:80` 직접 지정 절대 금지.

---

## §1 배포 전 준비 [FOUNDER]

### A. VPS 인바운드 디렉터리 생성

bind-mount 소스(`/data/legal-rag/ingest`)가 deploy 전에 VPS 에 없으면 Docker 가 빈 디렉터리를 root 소유로 만들어 컨테이너 쓰기 권한이 깨진다. 반드시 먼저 생성한다.

```bash
ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157 \
  'mkdir -p /data/legal-rag/ingest && ls -la /data/legal-rag/'
```

**SUCCESS**: 출력에 `ingest` 디렉터리가 나타남.
**FAIL**: SSH 연결 실패 → key 경로 확인 (`ls ~/.ssh/n9n_preview_ed25519`), VPS IP 핑 확인.

### B. 시크릿 생성 및 Coolify 환경변수 패널 입력

**Step 1 — 로컬에서 값 생성 (붙여넣기용)**:

```bash
# JWT_SECRET: HS256 서명 키 (64-char hex = 32 byte)
openssl rand -hex 32
# 출력 예: 8f3a...  ← 이 값을 LEGAL_RAG_JWT_SECRET 에 사용

# SERVICE_TOKEN: /ingest X-Service-Token (32-char hex)
openssl rand -hex 16
# 출력 예: c2d1...  ← 이 값을 LEGAL_RAG_SERVICE_TOKEN 에 사용

# DB 패스워드 (app_service 롤용)
openssl rand -base64 24
# 출력 예: Xk9f...  ← POSTGRES_PASSWORD 와 DSN 의 <pw> 에 동일하게 사용
```

생성한 값은 `infra/secrets/` 아래 gitignored 파일에 즉시 보관:

```
infra/secrets/legal-rag-jwt-secret.txt
infra/secrets/legal-rag-service-token.txt
infra/secrets/legal-rag-db-password.txt   ← DSN 에 포함되는 값과 동일
```

**Step 2 — Coolify UI 입력**: Coolify 앱 생성 완료 후, 앱 > Environment Variables 패널에서 아래 전체를 설정한다. Deploy 전에 완료해야 한다.

**필수 환경변수 (6종 — 이 6개가 없으면 app 컨테이너가 기동 거부)**:

| Coolify 환경변수 이름 | 값 형식 | 출처 |
|---|---|---|
| `LEGAL_RAG_POSTGRES_USER` | `app_service` | 고정값 (compose db 서비스와 동일해야 함) |
| `LEGAL_RAG_POSTGRES_PASSWORD` | `<openssl rand -base64 24 출력>` | Step 1 생성값 |
| `LEGAL_RAG_DB_DSN` | `postgresql://app_service:<pw>@db:5432/legaldb` | `db` = compose 서비스 이름, `<pw>` = POSTGRES_PASSWORD 와 동일 |
| `LEGAL_RAG_JWT_SECRET` | `<openssl rand -hex 32 출력>` | Step 1 생성값 |
| `LEGAL_RAG_SERVICE_TOKEN` | `<openssl rand -hex 16 출력>` | Step 1 생성값 |
| `LEGAL_RAG_INGEST_ROOT` | `/data/legal-docs` | 고정값 (compose bind-mount target) |

> **DSN 주의**: compose 내부에서 db 컨테이너 이름이 `db` 이므로 host 는 반드시 `db` (127.0.0.1 금지). 형식은 `postgresql://app_service:<pw>@db:5432/legaldb` 표준형식 강제 — libpq key=value 형식 사용 시 로그 마스킹 비동작.

**선택 환경변수 (기본값 있음 — 초기 배포 시 생략 가능)**:

| 이름 | 기본값 | 변경 시 주의 |
|---|---|---|
| `LEGAL_RAG_EMBED_MODEL_VERSION` | `intfloat/multilingual-e5-base` | 아래 prefix 잠금 주의 참조 |
| `LEGAL_RAG_CHUNK_TOKENS` | `500` | |
| `LEGAL_RAG_CHUNK_OVERLAP` | `50` | |
| `LEGAL_RAG_RRF_K` | `60` | |
| `LEGAL_RAG_TOP_K` | `10` | |
| `LEGAL_RAG_FTS_LIMIT` | `100` | |
| `LEGAL_RAG_ANN_LIMIT` | `100` | |
| `LEGAL_RAG_POOL_MIN` | `2` | |
| `LEGAL_RAG_POOL_MAX` | `10` | |
| `LEGAL_RAG_ENV` | compose 에서 `prod` 고정 | 변경 불가 (prod = /docs 비활성화) |

> **LEGAL_RAG_EMBED_URL 은 입력하지 않는다.** compose 파일에서 `http://embed:8080` 으로 하드코딩됨. Coolify UI 에서 이 변수를 추가하면 compose 값이 덮어씌워지므로 위험.

### C. Cloudflare DNS 레코드 확인 및 추가

먼저 와일드카드 레코드 존재 여부를 확인한다.

**확인**: Cloudflare 대시보드 > n9n.co.kr 존 > DNS > `*.n9n.co.kr` A 레코드가 `187.77.140.157` 를 가리키고 있으면 추가 불필요.

**없으면 추가**:

```
Type: A
Name: legal-rag
Content: 187.77.140.157
TTL: Auto
Proxy status: DNS only (주황 클라우드 OFF)
```

> Proxy 를 ON(오렌지 클라우드) 으로 설정하면 Cloudflare 가 443 을 프록시하여 Coolify/Traefik 의 Let's Encrypt TLS 와 충돌한다. 반드시 DNS only.

**SUCCESS**: `nslookup legal-rag.n9n.co.kr` 가 `187.77.140.157` 반환 (TTL 전파 1~5분 대기 가능).

### D. 임베딩 prefix 잠금 확인 (인제스트 전 필수)

- [ ] **[FOUNDER] 체크**: `EMBED_QUERY_PREFIX` / `EMBED_PASSAGE_PREFIX` 를 변경하지 않음.
  - compose 기본값: `query: ` / `passage: ` (embed-adapter 환경변수 기본값).
  - 실 문서를 한 건이라도 ingest 한 후에 prefix 를 변경하면 기존 벡터와 쿼리 벡터 간 공간 불일치 → 검색 품질 붕괴. 전체 re-embed 필요.
  - 변경이 필요하면 **QA 사인오프 전에** 결정하고 DDL + seed 적용 전에 설정한다.
  - 현재 상태: QA 사인오프 보류 중 — prefix 변경 금지.

---

## §2 TEI 첫 부팅 주의 [FOUNDER]

**첫 deploy 시 `tei` 컨테이너가 `intfloat/multilingual-e5-base` (~1.1 GB)를 HuggingFace Hub 에서 다운로드한다.** 모델 다운로드 완료 전까지 `tei` healthcheck 가 통과하지 않는다.

의존 체인:
```
tei healthy → embed starts → embed healthy → app starts
```

따라서 **첫 deploy 는 최대 10~15분 소요될 수 있다.** Coolify 빌드 폴 타임아웃(기본 5분)이 있으면 배포가 실패로 보일 수 있으나 컨테이너는 백그라운드에서 계속 기동된다.

**첫 deploy 후 tei 로그 모니터링 방법**:

```bash
# SSH 접속 후
ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157

# tei 컨테이너 이름 확인 (Coolify 가 UUID prefix 붙임)
docker ps --format "table {{.Names}}\t{{.Status}}" | grep tei

# 로그 tail
docker logs -f <tei-container-name>
# 기대 메시지: "Ready to serve requests" 가 나오면 모델 로드 완료
```

**이후 재배포**: 모델은 `tei-data` 볼륨에 캐시된다. Coolify 가 볼륨을 삭제하지 않는 한 (~1.1 GB 재다운로드 없음) 재배포는 수초 내 ready.

> Coolify UI 에서 앱 삭제 후 재생성(재프로비저닝) 시 `tei-data` 볼륨이 삭제될 수 있다. 삭제된 경우 다음 deploy 에서 재다운로드.

---

## §3 dry-run 검증 [FOUNDER]

```bash
# SSH 터널 활성 확인
curl -s --max-time 3 http://localhost:8000/api/v1/healthcheck
# 기대: 어떤 응답이든 돌아오면 터널 살아있음 (404 도 정상)

# 터널이 없으면 열기
ssh -i ~/.ssh/n9n_preview_ed25519 -fN \
  -o ServerAliveInterval=30 \
  -L 8000:localhost:8000 \
  root@187.77.140.157

# dry-run (API 변경 없음 — 스크립트가 할 일만 출력)
PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py \
  --slug legal-rag \
  --skip-scp \
  --entry-path /health \
  --dry-run
```

dry-run 출력에서 확인:
- `compose_location: /deploy/preview/legal-rag.compose.yml` (슬래시 시작 필수)
- `domain_service: app`
- 환경변수 값이 `***` 로 마스킹됨 (평문 노출 없음)

**FAIL 시**: 레지스트리 `infra/registry/legal-rag.yaml` 의 `compose_file` / `domain_service` 필드 확인.

---

## §4 실 배포 [FOUNDER]

B3~B6 확인, dry-run PASS, §1-A~C 완료 후 실행.

```bash
PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py \
  --slug legal-rag \
  --skip-scp \
  --entry-path /health
```

스크립트 자동 처리 목록:
1. 미푸시 커밋 자동 push (Coolify 는 GitHub 에서 pull — push 없이는 구버전 빌드됨)
2. SSH 터널 확인
3. Coolify 프로젝트/앱 생성 또는 재사용 (idempotent)
4. domain PATCH: `legal-rag.n9n.co.kr → app 서비스`
5. 배포 트리거 + 빌드 폴 (5분 타임아웃)
6. `/health` HTTP 200 + TLS CN 검증
7. `infra/registry/legal-rag.yaml` 에 `coolify_project`, `coolify_app`, `status: live`, `deployed_at` 기록

> 첫 deploy 시 §2 의 이유로 스크립트 빌드 폴이 타임아웃될 수 있다. 타임아웃 실패여도 §2 절차로 tei 로그를 직접 확인한다.

---

## §5 Coolify UI 배포 후 확인 [FOUNDER]

deploy_to_coolify.py 가 처리하지 않는 항목:

1. Coolify UI > 앱 > Environment Variables 패널에서 §1-B 필수 6종 입력 여부 재확인.
2. 환경변수 입력/수정 후 **Redeploy** 버튼 클릭 (env 반영 배포).
3. Coolify UI > 앱 > Logs > Runtime 탭 — `tei` 컨테이너 `Ready to serve requests` 확인 (§2 참조).
4. `embed` 컨테이너 `healthy` 상태 확인 (tei ready 이후 10~15초).
5. `app` 컨테이너 `healthy` 상태 확인 (embed ready 이후 20초).

---

## §6 DDL + Seed 적용 (live db 컨테이너 대상) [FOUNDER]

DDL/seed 전체 SQL 순서·내용은 `docs/runbooks/legal-rag-install.md §4` 참조. 여기서는 preview compose 환경에서의 실행 방법만 기술한다.

**사전 조건**: §4 deploy 완료, `db` 컨테이너 healthy.

```bash
# SSH 접속
ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157

# db 컨테이너 이름 확인
docker ps --format "table {{.Names}}\t{{.Status}}" | grep "\-db\-"

# repo 경로 (Coolify 클론 경로 — 실제 경로를 아래로 대체)
REPO=/var/lib/docker/volumes/<coolify-project-uuid>/_data
# 또는 Coolify 가 클론하는 경로를 UI > Settings > Source 에서 확인

# DSN (환경변수 값과 동일하게 입력)
export DSN="postgresql://app_service:<pw>@localhost:5432/legaldb"

# db 컨테이너에서 직접 psql 실행 (augment 01~08, 순서 엄수)
DB=<db-container-name>

docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/01_extensions.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/02_legal_case_augment.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/03_precedent_augment.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/04_case_document_augment.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/05_case_party_rls.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/06_legal_document_chunk.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/07_rag_query_log.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/08_legal_attorney.sql

# Seed (FK 의존 순서 엄수)
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/seed/seed_attorneys.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/seed/seed_precedents.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/seed/seed_cases.sql
docker exec -i $DB psql -U app_service -d legaldb \
  < $REPO/presets/ddl/augments/legal/seed/seed_case_documents.sql
```

**적용 확인**:

```bash
docker exec -i $DB psql -U app_service -d legaldb -c "
SELECT
  (SELECT COUNT(*) FROM legal_attorney)       AS attorneys,
  (SELECT COUNT(*) FROM legal_case)           AS cases,
  (SELECT COUNT(*) FROM legal_precedent)      AS precedents,
  (SELECT COUNT(*) FROM legal_case_document)  AS documents;
"
# SUCCESS: attorneys=3, cases=12, precedents=22, documents=15
```

> 01_extensions.sql 은 슈퍼유저 또는 CREATEROLE 권한이 필요하다. `app_service` 로 권한 오류가 나면 `postgres` 슈퍼유저로 실행:
> `docker exec -i $DB psql -U postgres -d legaldb < .../01_extensions.sql`

---

## §7 라이브 검증 [FOUNDER]

DNS 전파(§1-C) 완료 후 실행.

```bash
SLUG=legal-rag
BASE="https://${SLUG}.n9n.co.kr"

# 1. Health (200 + {"status":"ok"})
curl -s --max-time 15 "$BASE/health"
# SUCCESS: {"status":"ok"}
# FAIL: connection refused → DNS 미전파(대기) 또는 app 미기동(§5 Logs 확인)

# 2. TLS 인증서 확인
echo | openssl s_client -connect ${SLUG}.n9n.co.kr:443 \
  -servername ${SLUG}.n9n.co.kr 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
# SUCCESS: CN=legal-rag.n9n.co.kr, issuer=Let's Encrypt, 만료일 90일 후

# 3. 로그인 e2e (install runbook §8 데모 자격증명)
TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"lee.junho@example-lawfirm.kr","password":"demo1234!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "TOKEN: ${TOKEN:0:20}..."
# SUCCESS: TOKEN 이 빈 문자열이 아님 (첫 20자 출력)
# FAIL: KeyError access_token → seed 미적용(§6) 또는 JWT_SECRET 미설정(§1-B)

# 4. 검색 e2e (seed + ingest 후)
curl -s -X POST "$BASE/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "계속적 공급계약 해지 기회손실", "top_k": 3}' \
  | python3 -m json.tool
# SUCCESS: chunks 배열, 각 항목에 citation metadata 포함, answer_text 없음 (Lite 티어)
# FAIL: 빈 배열 → demo docs ingest 필요 (install runbook §4-4 참조)

# 5. rate-limit 검증 (6번째 요청부터 429)
for i in $(seq 1 8); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"bad@test.com","password":"bad"}')
  echo "Request $i: $STATUS"
done
# SUCCESS: 1~5 = 401 또는 422, 6~8 = 429

# 6. 통합 pytest (VPS 직접 Postgres 접근)
cd services/legal-rag
LEGAL_RAG_DB_DSN_POSTGRES="postgresql://app_service:<pw>@187.77.140.157:5432/legaldb" \
  pytest tests/ -m postgres -v
# SUCCESS: 모든 테스트 PASSED (49개 포함)
```

---

## §8 배포 완료 후 레지스트리 갱신 [FOUNDER]

deploy_to_coolify.py 가 자동으로 채우지 않는 항목을 수동 보완:

```yaml
# infra/registry/legal-rag.yaml 에서 아래 필드 채우기
preview:
  coolify_project: "<uuid>"          # deploy 스크립트가 자동 기입
  coolify_app: "<uuid>"             # deploy 스크립트가 자동 기입
  status: live                      # deploy 스크립트가 자동 기입
  deployed_at: "2026-XX-XX"         # deploy 스크립트가 자동 기입
  tls: "Let's Encrypt, CN=legal-rag.n9n.co.kr, exp <날짜>"  # §7 step 2 결과로 수동 기입
  build_commit: "<git sha>"         # git log --oneline -1 출력으로 수동 기입
```

갱신 후 커밋 (파일당 별도 커밋 — CLAUDE.md §9):

```bash
git add infra/registry/legal-rag.yaml
git commit -m "$(cat <<'EOF'
chore(registry): mark legal-rag preview live

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
EOF
)"
git push origin master
```

---

## §9 롤백 / 중단 절차

배포 중 단계에서 복구 불가 오류 발생 시:

```bash
# Coolify UI: 앱 > Stop 클릭 (컨테이너 정지)
# 또는 SSH 에서 직접:
ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157

# 컨테이너 목록 확인
docker ps | grep legal-rag

# 전체 중지 (Coolify 관리 컨테이너이므로 Coolify UI Stop 권장)
docker stop <app-container> <embed-container> <tei-container> <db-container>
```

**볼륨 처리 주의**:
- `legal-rag-pgdata` 볼륨: DDL/seed 가 적용된 경우 삭제 금지. 재배포 시 그대로 재사용.
- `tei-data` 볼륨: 삭제하면 다음 deploy 에서 ~1.1 GB 재다운로드 (§2 참조). 삭제 불필요.
- 볼륨 삭제가 필요한 경우(스키마 완전 초기화): `docker volume rm <project-prefix>_legal-rag-pgdata` — 이 경우 DDL+seed 를 §6 에서 전부 재적용해야 함.

**DNS 취소**: Cloudflare 에서 `legal-rag A` 레코드 삭제. 와일드카드 레코드는 건드리지 않는다.
