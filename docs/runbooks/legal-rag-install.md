# Legal RAG — Self-Host Install Runbook

> 단일 진실: DevOps 인격이 유지. 변경 시 커밋 + `docs/learn-logs/devops.md` 갱신.
> 토폴로지: yesnic 도메인 → Cloudflare DNS → Hostinger VPS 187.77.140.157 → Coolify → Traefik
> 인프라 비용 영향: 추가 VPS/SaaS 없음. 기존 Coolify 단일 VPS 에 컨테이너 추가. 기존 $8.99/월 고정분 배분.

법무법인 사내망에 Legal RAG MVP(Lite 티어 — 검색+인용, LLM 생성 없음)를 self-host 설치하는 완전 재현 절차.

**핵심 가치 보장**: 데이터 외부 유출 0, 월 API 비 0.

**실 Coolify 배포는 founder 실행 게이트**: 이 런북은 절차를 완비하되, VPS/Coolify 접근이 필요한 단계는 `[FOUNDER GATE]` 로 표시한다. DevOps 인격이 임의로 배포를 시도하지 않는다.

---

## 목차

1. [사전 요건](#1-사전-요건)
2. [Postgres + pgvector + pg_bigm 설치](#2-postgres--pgvector--pg_bigm-설치)
3. [DB 롤 생성 및 DSN 준비](#3-db-롤-생성-및-dsn-준비)
4. [DDL + Seed 적용 순서](#4-ddl--seed-적용-순서)
5. [임베딩 사이드카 기동](#5-임베딩-사이드카-기동)
6. [서비스 환경변수 및 기동 (Coolify / Compose)](#6-서비스-환경변수-및-기동)
7. [운영 하드닝 체크리스트](#7-운영-하드닝-체크리스트)
8. [데모 자격증명](#8-데모-자격증명)
9. [라이브 검증 절차](#9-라이브-검증-절차)
10. [트러블슈팅](#10-트러블슈팅)

---

## 1. 사전 요건

| 항목 | 요건 | 비고 |
|---|---|---|
| OS | Ubuntu 22.04 LTS 이상 | 사내 서버 또는 VM |
| Postgres | 15 이상 | pgvector, pg_bigm 확장 필요 |
| Python | 3.11 이상 | 가상환경 권장 |
| Docker | 24 이상 | Coolify 배포 경로 사용 시 |
| 디스크 | 10 GB 이상 여유 | 청크+벡터 데이터 성장 고려 |
| 네트워크 | 사내망 폐쇄 | 임베딩 사이드카는 외부 인터넷 미사용 |

**founder 접근 방법 (Coolify preview 경로)**:
- VPS 접근: Hostinger 브라우저 터널 (Control Panel → Browser Terminal). SSH 공개키 인증은 현재 불가 — `~/.ssh` 키 기반 접근을 시도하지 않는다.
- VPS IP: `187.77.140.157`
- API 토큰: `infra/secrets/preview-vps.env` (gitignored 볼트)

---

## 2. Postgres + pgvector + pg_bigm 설치

고객사 사내망 서버에서 수행한다.

```bash
# Ubuntu apt
sudo apt-get update
sudo apt-get install -y postgresql-15 postgresql-15-pgvector

# pg_bigm (PPA 없으면 소스 빌드)
sudo apt-get install -y postgresql-server-dev-15 build-essential
wget https://github.com/pgbigm/pg_bigm/releases/download/v1.2-20200228/pg_bigm-1.2-20200228.tar.gz
tar xf pg_bigm-1.2-20200228.tar.gz
cd pg_bigm-1.2-20200228 && make USE_PGXS=1 && sudo make USE_PGXS=1 install
```

psql 접속 후 설치 확인:

```sql
SELECT name, default_version FROM pg_available_extensions
WHERE name IN ('vector', 'pg_bigm');
-- vector 와 pg_bigm 두 행이 나와야 정상
```

---

## 3. DB 롤 생성 및 DSN 준비

**DSN 형식 강제 (하드닝 #1)**: 로그 마스킹이 동작하려면 반드시 `postgresql://user:pw@host:port/db` 표준형식을 사용한다. libpq key=value 형식 사용 시 마스킹 regex 가 동작하지 않는다.

```bash
# postgres 슈퍼유저로 접속
sudo -u postgres psql

-- DB 생성
CREATE DATABASE legaldb;
\c legaldb

-- 롤 생성
-- app_service: BYPASSRLS (ingest + 로그인 검증 전용)
CREATE ROLE app_service LOGIN PASSWORD '<strong-password-here>';
ALTER ROLE app_service BYPASSRLS;

-- app_user: RLS 적용 (변호사 세션 연결 — 현재 미사용, 향후 Pro 티어용)
CREATE ROLE app_user LOGIN PASSWORD '<strong-password-here>';

-- app_service 에게 legaldb 접근 권한
GRANT CONNECT ON DATABASE legaldb TO app_service;
GRANT CONNECT ON DATABASE legaldb TO app_user;
```

DSN 예시 (이 형식을 볼트에 저장):

```
postgresql://app_service:<strong-password>@127.0.0.1:5432/legaldb
```

---

## 4. DDL + Seed 적용 순서

`DSN` 환경변수에 위 표준형식 DSN 을 설정한 뒤 repo 루트에서 실행한다.

### 4-1. Baseline DDL 렌더링 (최초 1회)

Baseline DDL 은 커밋된 파일이 아니라 `render.py` 가 `catalog.yaml` 에서 실시간 생성한다. 4개 legal 엔티티만 스코핑하므로 HR FK 오염(`hr_employee` 등)이 발생하지 않는다.

```bash
# repo root 에서 실행. PyYAML 이 없으면 아래 docker one-liner 를 사용한다.
python presets/ddl/render.py --dialect postgres \
  --entities legal-case,precedent,case-party,case-document \
  | psql "$DSN"

# PyYAML 없이 throwaway 컨테이너로 렌더링 + 즉시 적용:
docker run --rm -v "$(pwd)":/w -w /w python:3.11-slim \
  sh -c 'pip install -q pyyaml && python presets/ddl/render.py --dialect postgres \
  --entities legal-case,precedent,case-party,case-document' \
  | psql "$DSN"
```

> **Coolify / docker exec 경로**: 아래 §4-bis 의 `legal-rag.apply-schema.sh` 를 사용하면 렌더링부터 seed 까지 자동으로 처리된다. 이 단계를 수동으로 실행할 필요가 없다.

### 4-2. RAG Augment DDL (01 ~ 09, 순서 엄수)

```bash
export DSN="postgresql://app_service:<pw>@127.0.0.1:5432/legaldb"

psql "$DSN" -f presets/ddl/augments/legal/01_extensions.sql       # vector, pg_bigm, 롤 정의
psql "$DSN" -f presets/ddl/augments/legal/02_legal_case_augment.sql
psql "$DSN" -f presets/ddl/augments/legal/03_precedent_augment.sql
psql "$DSN" -f presets/ddl/augments/legal/04_case_document_augment.sql
psql "$DSN" -f presets/ddl/augments/legal/05_case_party_rls.sql
psql "$DSN" -f presets/ddl/augments/legal/06_legal_document_chunk.sql
psql "$DSN" -f presets/ddl/augments/legal/07_rag_query_log.sql
psql "$DSN" -f presets/ddl/augments/legal/08_legal_attorney.sql   # legal_attorney 테이블
psql "$DSN" -f presets/ddl/augments/legal/09_grants.sql           # app_user SELECT/INSERT 권한 (RLS 발효 전제)
```

**주의**: 01 이 롤 생성을 포함한다. 슈퍼유저 또는 CREATEROLE 권한이 있는 계정으로 실행해야 한다.

### 4-3. Seed 데이터 (순서 엄수 — FK 의존성)

```bash
psql "$DSN" -f presets/ddl/augments/legal/seed/seed_attorneys.sql      # 반드시 첫 번째 (FK 피참조)
psql "$DSN" -f presets/ddl/augments/legal/seed/seed_precedents.sql
psql "$DSN" -f presets/ddl/augments/legal/seed/seed_cases.sql          # legal_attorney FK 의존
psql "$DSN" -f presets/ddl/augments/legal/seed/seed_case_documents.sql
```

### 4-bis. Coolify preview 적용 (docker exec 경로) [FOUNDER GATE]

> **Coolify / VPS 에 직접 배포된 컨테이너에 적용할 때는 이 경로를 사용한다.** 위 §4-1 ~ §4-3 은 on-prem (고객사 서버) 참조용이다. Preview 환경에서는 `psql "$DSN"` 을 호스트에서 직접 실행할 수 없으므로 `docker exec` 를 경유한다.

원샷 스크립트 (`deploy/preview/legal-rag.apply-schema.sh`) 가 아래 단계를 모두 자동화한다:
1. db 컨테이너 자동 탐색 (project UUID `gwpba3e8j8upf9v0swf96wkt` prefix 기준, hash suffix 는 재배포마다 변경되므로 절대 하드코딩 금지)
2. `POSTGRES_USER` 자동 탐색 (`docker exec printenv`)
3. base DDL 렌더링 (throwaway python:3.11-slim 컨테이너 사용 — 호스트 PyYAML 불필요)
4. 01~09 augment + 4개 seed 를 지정 순서로 적용 (`-v ON_ERROR_STOP=1` 로 오류 즉시 중단)
5. 카운트 검증 + PASS/FAIL 출력

```bash
# VPS 호스트 Hostinger 브라우저 터널에서 실행 (repo 루트에 클론되어 있어야 함)
cd /path/to/compounding-stack-harness   # repo 루트
bash deploy/preview/legal-rag.apply-schema.sh

# db 컨테이너 이름을 수동 지정할 경우 (자동 탐색 실패 시):
bash deploy/preview/legal-rag.apply-schema.sh db-gwpba3e8j8upf9v0swf96wkt-<hash>
```

예상 출력 (PASS 시):
```
[1/9] Repo root: /path/to/repo
[2/9] DB container (auto-discovered): db-gwpba3e8j8upf9v0swf96wkt-115816635412
[3/9] POSTGRES_USER: <user>
[4/9] Rendering base DDL via throwaway python container ...
...
  PASS  attorneys: 3
  PASS  cases: 12
  PASS  precedents: 22
  PASS  parties: 29
  PASS  documents: 15
  PASS  pg_bigm: correctly ABSENT (preview auto-degraded to plainto_tsquery)
  PASS  vector extension: present
  PASS  legal_case RLS: relrowsecurity=t, relforcerowsecurity=t
==========================================
  ALL CHECKS PASSED. Schema + seed ready.
==========================================
```

스크립트는 멱등(idempotent)하다 — 부분 실패 후 수정하고 재실행해도 안전하다.

### 4-4. Demo docs ingest (청크 + 벡터 생성)

임베딩 사이드카(§5)가 기동된 후 실행:

```bash
# 서비스 기동 상태에서 ingest API 호출
# X-Service-Token 은 LEGAL_RAG_SERVICE_TOKEN 볼트 값 사용
curl -X POST http://localhost:8000/ingest \
  -H "X-Service-Token: <service-token>" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/data/demo_docs/complaint_hanbit_vs_miraesolution.txt", "source_id": "<doc-uuid-000001>", "source_type": "case_document"}'

curl -X POST http://localhost:8000/ingest \
  -H "X-Service-Token: <service-token>" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/data/demo_docs/brief_alphatech_copyright.txt", "source_id": "<doc-uuid-000015>", "source_type": "case_document"}'

curl -X POST http://localhost:8000/ingest \
  -H "X-Service-Token: <service-token>" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/data/demo_docs/contract_software_supply.txt", "source_id": "<doc-uuid-000002>", "source_type": "case_document"}'
```

`<doc-uuid-*>` 는 `seed_case_documents.sql` 의 실제 UUID 값으로 대체한다.

적용 확인:

```sql
-- 확장 설치 확인
SELECT extname FROM pg_extension WHERE extname IN ('vector','pg_bigm');

-- 롤 확인
SELECT rolname, rolbypassrls FROM pg_roles WHERE rolname IN ('app_service','app_user');

-- 변호사 3명 확인 (비밀번호 해시만, 평문 아님)
SELECT id, email, role, is_active FROM legal_attorney;

-- 사건 12건 확인
SELECT COUNT(*) FROM legal_case;  -- 기대: 12
```

---

## 5. 임베딩 사이드카 기동

**외부 노출 금지 (하드닝 #2)**: `LEGAL_RAG_EMBED_URL` 은 반드시 localhost 또는 사내망 주소여야 한다. 인터넷 라우팅 주소 사용 시 법률 문서가 외부 서버로 전송된다.

**Growth-94 피벗**: TEI (HuggingFace text-embeddings-inference cpu-1.5) 는 제거되었다. TEI 의 Rust `hf-hub` 다운로더가 VPS 환경에서 `'relative URL without a base'` 오류로 실패(확인됨)하였기 때문이다. 현재 embed 사이드카는 **단일 컨테이너** (`services/legal-rag/embed-adapter/`) 로, `sentence-transformers` (intfloat/multilingual-e5-base, 768-dim) 를 이미지 빌드 시점에 내장(`COPY model/`)한다. 런타임에서는 `HF_HUB_OFFLINE=1` 로 설정되어 외부 다운로드를 차단한다.

**on-prem 단독 설치용 수동 기동 참조** (Coolify preview 는 `deploy/preview/legal-rag.compose.yml` 이 자동 기동):

```bash
# embed-adapter (모델 내장 단일 컨테이너) — 내부 전용
docker run -d \
  --name legal-embed-sidecar \
  -e HF_HUB_OFFLINE=1 \
  -e EMBED_MODEL_NAME="intfloat/multilingual-e5-base" \
  <embed-adapter-image-tag>   # Coolify 빌드 이미지 태그 또는 로컬 빌드

# 헬스체크
curl http://localhost:8080/health
# 기대: 200 OK {"status":"ok"}
```

> **참고**: 첫 이미지 빌드 시 모델 (~1.1 GB) 이 이미지에 포함된다. 빌드는 느리지만 런타임 다운로드가 없어 사내망 폐쇄 환경에서 안정적이다.

> **프리픽스 LOCK (Growth-93, QA PASS)**: adapter 는 e5 비대칭 프리픽스를 적용한다 — `/embed`(검색)=`query: `, `/embed/batch`(인제스트)=`passage: `. **첫 인제스트 후 `EMBED_QUERY_PREFIX`/`EMBED_PASSAGE_PREFIX` 변경 금지** (전 코퍼스 재임베딩 강제). caller-split 불변식은 가드 G-87 로 강제.

### 사이드카 contract (서비스가 기대하는 API)

```
POST /embed          {"text": "<string>"}
                  → {"embedding": [<float x 768>], "model": "<version>"}

POST /embed/batch    {"texts": ["<string>", ...]}
                  → {"embeddings": [[<float x 768>], ...], "model": "<version>"}

GET  /health      → 200 OK
```

---

## 6. 서비스 환경변수 및 기동

### 6-1. 시크릿 준비 (Coolify 볼트 — 하드닝 #6)

모든 시크릿은 Coolify UI 환경변수 패널에 주입한다. 평문 `.env` 파일을 서버에 두지 않는다.

Coolify 에서 설정할 환경변수 (필수):

| Variable | 예시 | 설명 |
|---|---|---|
| `LEGAL_RAG_DB_DSN` | `postgresql://app_service:pw@127.0.0.1:5432/legaldb` | 표준형식 필수 (하드닝 #1) |
| `LEGAL_RAG_EMBED_URL` | `http://127.0.0.1:8080` | 사내망/localhost 전용 (하드닝 #2) |
| `LEGAL_RAG_INGEST_ROOT` | `/data/legal-docs` | path-traversal 가드 루트 |
| `LEGAL_RAG_JWT_SECRET` | `<64-char random hex>` | HS256 서명 시크릿 |
| `LEGAL_RAG_SERVICE_TOKEN` | `<32-char random hex>` | /ingest X-Service-Token |

시크릿 생성 명령 (로컬 실행 후 Coolify UI 에 붙여넣기):

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"  # SERVICE_TOKEN
python3 -c "import secrets; print(secrets.token_hex(64))"  # JWT_SECRET (32-byte = 64 hex)
```

Coolify 에서 설정할 환경변수 (선택, 기본값 있음):

| Variable | 기본값 | 설명 |
|---|---|---|
| `LEGAL_RAG_EMBED_MODEL_VERSION` | `intfloat/multilingual-e5-base` | 모델 버전 기록용 (Growth-93: embeddinggemma 폐기) |
| `LEGAL_RAG_CHUNK_TOKENS` | `500` | 청크 목표 토큰 수 |
| `LEGAL_RAG_CHUNK_OVERLAP` | `50` | 청크 오버랩 토큰 |
| `LEGAL_RAG_RRF_K` | `60` | RRF 상수 k |
| `LEGAL_RAG_TOP_K` | `10` | 검색 반환 청크 수 |
| `LEGAL_RAG_FTS_LIMIT` | `100` | FTS 후보 한도 |
| `LEGAL_RAG_ANN_LIMIT` | `100` | ANN 후보 한도 |
| `LEGAL_RAG_POOL_MIN` | `2` | DB pool 최소 연결 |
| `LEGAL_RAG_POOL_MAX` | `10` | DB pool 최대 연결 |
| `LEGAL_RAG_ENV` | `dev` | **프로덕션은 반드시 `prod` 로 설정** — `prod` 시 docs/openapi 비활성화 |

**운영 관점**: `LEGAL_RAG_ENV=prod` 로 설정하면 FastAPI auto-docs(`/docs`, `/redoc`) 및 OpenAPI JSON 엔드포인트가 비활성화된다. `GET /health` 는 인증 없이 `{"status":"ok"}` 200 만 반환하는 **shallow liveness** 로, DB·사이드카 등 내부 상태를 일절 노출하지 않는다(인프라 정찰 차단). DB pool·사이드카 reachability 상세 점검은 `GET /health/detail` 로 분리되었고 **X-Service-Token 인증**이 걸린다 (코드는 engineer 가 처리, 이 런북은 운영 설정 관점만 기술).

### 6-2. Coolify 배포 [FOUNDER GATE]

`preview-deploy.md` 의 Step 2~4 를 `legal-rag` slug 로 따른다.

Compose 파일 위치: `deploy/preview/legal-rag.compose.yml` (engineer/DevOps 가 작성 예정).

```bash
# SSH 포워딩 활성 후
PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py \
  --slug legal-rag --dry-run

# 확인 후 실제 배포
PYTHONIOENCODING=utf-8 python scripts/workflow/deploy_to_coolify.py \
  --slug legal-rag
```

### 6-3. 직접 uvicorn 기동 (개발/테스트 환경)

```bash
cd services/legal-rag
pip install -r requirements.txt

export LEGAL_RAG_DB_DSN="postgresql://app_service:<pw>@127.0.0.1:5432/legaldb"
export LEGAL_RAG_EMBED_URL="http://127.0.0.1:8080"
export LEGAL_RAG_INGEST_ROOT="/data/legal-docs"
export LEGAL_RAG_JWT_SECRET="<64-char-hex>"
export LEGAL_RAG_SERVICE_TOKEN="<32-char-hex>"
export LEGAL_RAG_ENV="prod"

uvicorn api:app --host 127.0.0.1 --port 8000
```

**함정**: `--host 0.0.0.0` 은 사내망 다른 호스트에서 직접 접근을 허용한다. Traefik 을 앞에 두는 경우 `127.0.0.1` 바인딩 권장. Traefik 없이 직접 노출이 필요한 경우 방화벽으로 접근 IP 를 제한한다.

---

## 7. 운영 하드닝 체크리스트

아래 7항목을 설치 완료 전 모두 확인한다.

### #1 DSN 표준형식 강제

- [ ] `LEGAL_RAG_DB_DSN` 값이 `postgresql://user:pw@host:port/db` 형식인지 확인
- [ ] libpq key=value 형식(`host=... dbname=...`) 사용 시 로그 마스킹 비동작 → 표준형식으로 교체

### #2 EMBED_URL localhost/사내망 전용

- [ ] `LEGAL_RAG_EMBED_URL` 이 `http://127.0.0.1:...` 또는 사내망 IP 임을 확인
- [ ] `http://api.openai.com`, `https://cohere.ai` 등 외부 주소 절대 사용 금지 (법률 문서 외부 전송)
- [ ] 사이드카가 외부 인터페이스에 바인딩되어 있지 않은지 `ss -tlnp | grep 8080` 으로 확인

### #3 query_text 평문저장 완화 (Lite 티어)

`legal_rag_query_log.query_text` 가 현재 평문 저장된다.

- [ ] Postgres `pg_hba.conf` 에서 `app_service` 연결을 loopback only 로 제한:
  ```
  # pg_hba.conf 추가 (기존 host 라인보다 먼저)
  local  legaldb  app_service  md5
  host   legaldb  app_service  127.0.0.1/32  scram-sha-256
  # 원격 host 라인에서 app_service 제외
  ```
- [ ] 설정 반영: `sudo systemctl reload postgresql`
- [ ] 외부 IP 에서 app_service 로 직접 연결이 거부되는지 확인
- [ ] 향후 Pro 티어 전환 시: query_text AES-256 암호화 (engineer 작업으로 연기)

### #4 ingest_root 볼륨 nosymfollow 마운트

- [ ] `/data/legal-docs` 를 nosymfollow 옵션으로 마운트:
  ```bash
  # /etc/fstab 또는 docker compose 볼륨 설정
  mount -o bind,nosymfollow /data/legal-docs /data/legal-docs
  ```
- [ ] Docker Compose 경우:
  ```yaml
  volumes:
    - type: bind
      source: /data/legal-docs
      target: /data/legal-docs
      bind:
        propagation: private
  # nosymfollow 는 호스트 마운트 옵션으로 설정 (compose 직접 미지원)
  ```
- [ ] 심볼릭 링크로 root 탈출 불가 확인: `ln -s /etc/passwd /data/legal-docs/test.txt` 후 ingest 시 거부되는지 테스트 (후 삭제)

### #5 Postgres 볼륨 LUKS 암호화 + Traefik TLS 종단

- [ ] `/var/lib/postgresql/` 디렉터리가 LUKS 암호화 볼륨 위에 있는지 확인:
  ```bash
  lsblk -o NAME,TYPE,MOUNTPOINT,FSTYPE
  # pg data 볼륨이 crypt 타입이어야 함
  ```
- [ ] LUKS 볼륨 미적용 시 고객사 IT 담당자와 협의하여 사내 암호화 정책 확인
- [ ] Traefik TLS 종단 확인 (Coolify 배포 경로):
  ```bash
  echo | openssl s_client -connect <service-fqdn>:443 -servername <service-fqdn> \
    2>/dev/null | openssl x509 -noout -issuer -dates
  # issuer 에 Let's Encrypt 또는 사내 CA 표시 확인
  ```
- [ ] HTTP(80) → HTTPS(443) 리디렉션 확인:
  ```bash
  curl -v -o /dev/null http://<service-fqdn>/health 2>&1 | grep "< HTTP"
  # 기대: 301 또는 308 Moved Permanently
  ```

### #6 시크릿 Coolify 볼트 관리

- [ ] `LEGAL_RAG_DB_DSN`, `LEGAL_RAG_JWT_SECRET`, `LEGAL_RAG_SERVICE_TOKEN` 이 Coolify 환경변수 패널에 입력되어 있음
- [ ] 서버 파일시스템에 `.env` 평문 파일이 없음: `find /data /opt -name "*.env" -o -name ".env"` 로 확인
- [ ] `infra/registry/legal-rag.yaml` 의 `secret_ref` 가 볼트 키 이름만 참조하고 평문이 없음
- [ ] Git history 에 시크릿이 없음: `git log --all -S "LEGAL_RAG_JWT_SECRET" -- '*.env'` (0건이어야 함)

### #7 rate-limit on /auth/login (Traefik 미들웨어)

앱 코드 변경 없이 Traefik 미들웨어로 `/auth/login` 에 IP 기준 rate-limit 을 적용한다. 약 5 req/min.

**Coolify 배포 경로 (Docker label)**:

```yaml
# deploy/preview/legal-rag.compose.yml 의 서비스 labels 섹션에 추가
labels:
  # 기존 Traefik 라벨 유지 + 아래 추가
  - "traefik.http.middlewares.legal-rag-ratelimit.ratelimit.average=5"
  - "traefik.http.middlewares.legal-rag-ratelimit.ratelimit.burst=10"
  - "traefik.http.middlewares.legal-rag-ratelimit.ratelimit.period=1m"
  - "traefik.http.middlewares.legal-rag-ratelimit.ratelimit.sourcecriterion.ipstrategy.depth=1"
  - "traefik.http.routers.legal-rag-login.rule=PathPrefix(`/auth/login`)"
  - "traefik.http.routers.legal-rag-login.entrypoints=https"
  - "traefik.http.routers.legal-rag-login.tls=true"
  - "traefik.http.routers.legal-rag-login.service=legal-rag"
  - "traefik.http.routers.legal-rag-login.priority=100"
  - "traefik.http.routers.legal-rag-login.middlewares=legal-rag-ratelimit"
```

> **주의 (CISO 게이트-8 LOW)**: `legal-rag-login` 라우터는 반드시 `entrypoints`·`tls`·`service`(기존 `legal-rag` 서비스명)·`priority`(기본 catch-all 라우터보다 높게)를 명시해야 한다. 누락 시 라우터가 어느 서비스에도 연결되지 않는 dead router 가 되어 rate-limit 이 적용되지 않는다. 배포 후 `traefik` 대시보드 또는 `curl` 429 검증(아래)으로 활성화를 반드시 확인한다.

**Traefik 정적 설정 경로 (traefik.yml)**:

```yaml
# 또는 traefik dynamic config (legal-rag.yml)
http:
  middlewares:
    legal-rag-ratelimit:
      rateLimit:
        average: 5
        burst: 10
        period: "1m"
        sourceCriterion:
          ipStrategy:
            depth: 1
  routers:
    legal-rag-login:
      rule: "PathPrefix(`/auth/login`)"
      middlewares:
        - legal-rag-ratelimit
```

검증:

```bash
# 6회 연속 요청 시 6번째부터 429 Too Many Requests 확인
for i in $(seq 1 8); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST https://<service-fqdn>/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"bad@test.com","password":"bad"}')
  echo "Request $i: $STATUS"
done
# 기대: 1~5 = 401/422, 6~8 = 429
```

---

## 8. 데모 자격증명

**이 자격증명은 이 런북에만 기록한다.** seed SQL 에는 bcrypt 해시만 저장되어 있으며 평문 비밀번호는 없다.

**데모 비밀번호**: `demo1234!` (전원 동일 — 데모 환경 전용)

| 이름 | 이메일 | 역할 | 담당 사건 |
|---|---|---|---|
| 이준호 | lee.junho@example-lawfirm.kr | partner | c001~c006 (assigned) + 전체 (partner_id) |
| 박서연 | park.seoyeon@example-lawfirm.kr | attorney | c007~c012 (assigned) |
| 김정훈 | jh.kim@example-lawfirm.kr | partner | 파트너 (감독 역할) |

**RLS 시연**: 이준호(partner)로 로그인 시 전체 사건 조회 가능. 박서연으로 로그인 시 c007~c012 만 조회되며 c001~c006 문서는 0건 반환.

**프로덕션 전환 전 필수**: 데모 비밀번호를 새 비밀번호(bcrypt $2b$ cost 12 해시)로 교체한다.

```sql
-- 프로덕션 전환 시 각 변호사별 비밀번호 교체
UPDATE legal_attorney SET password_hash = '<new-bcrypt-hash>'
WHERE email = 'lee.junho@example-lawfirm.kr';
```

---

## 9. 라이브 검증 절차

**주의**: L2/L4/RLS 통합테스트는 실 Postgres + pgvector + 사이드카가 필요하다. **실 인프라 접근이 있는 founder 가 실행하는 게이트**다.

### L2 — Postgres 스키마 Smoke

```bash
export DSN="postgresql://app_service:<pw>@127.0.0.1:5432/legaldb"

psql "$DSN" -c "
SELECT
  (SELECT COUNT(*) FROM legal_attorney)       AS attorneys,
  (SELECT COUNT(*) FROM legal_case)           AS cases,
  (SELECT COUNT(*) FROM legal_precedent)      AS precedents,
  (SELECT COUNT(*) FROM legal_case_party)     AS parties,
  (SELECT COUNT(*) FROM legal_case_document)  AS documents;
"
# 기대: attorneys=3, cases=12, precedents=22, parties=29, documents=15
```

### L4 — 서비스 e2e (uvicorn 기동 후)

```bash
BASE="http://localhost:8000"

# 1. 로그인 (이준호)
TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"lee.junho@example-lawfirm.kr","password":"demo1234!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "TOKEN: ${TOKEN:0:20}..."   # 첫 20자만 출력 (보안)

# 2. 검색
curl -s -X POST "$BASE/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "계속적 공급계약 해지 기회손실", "top_k": 3}' \
  | python3 -m json.tool

# 기대: ranked chunks + citation metadata (answer_text 없음)
```

### RLS 격리 통합테스트 [FOUNDER GATE]

실 Postgres + pgvector + 사이드카 기동 환경 필요.

```bash
cd services/legal-rag

# 단위 테스트 (DB/사이드카 불필요)
LEGAL_RAG_INGEST_ROOT=/tmp LEGAL_RAG_JWT_SECRET=test LEGAL_RAG_SERVICE_TOKEN=test \
  pytest tests/ -q

# 통합 테스트 (실 Postgres + pgvector 필요)
LEGAL_RAG_DB_DSN_POSTGRES="postgresql://app_service:<pw>@127.0.0.1:5432/legaldb" \
  pytest tests/ -m postgres -v
```

통합 테스트 핵심 검증 (이준호 토큰으로 박서연 사건 0건 확인):

```
PASSED tests/test_rls_isolation.py::test_cross_attorney_isolation
  - 이준호 JWT → /search → c007~c012 문서 = 0건
  - 박서연 JWT → /search → c001~c006 문서 = 0건
```

### Coolify 배포 검증 [FOUNDER GATE]

```bash
# TLS + HTTP 200 확인
curl -s -o /dev/null -w "HTTP %{http_code}" --max-time 15 \
  "https://<slug>.n9n.co.kr/health"
# 기대: HTTP 200

# TLS 인증서 확인
echo | openssl s_client -connect <slug>.n9n.co.kr:443 \
  -servername <slug>.n9n.co.kr 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

---

## 10. 트러블슈팅

### 503 sidecar_unavailable

```
{"detail": "sidecar_unavailable: ..."}
```

원인: `LEGAL_RAG_EMBED_URL` 사이드카가 응답하지 않음.

```bash
curl http://127.0.0.1:8080/health
# 실패 시 사이드카 재기동
docker restart legal-embed-sidecar
```

### RuntimeError: Required environment variable 'LEGAL_RAG_JWT_SECRET' is not set

원인: Coolify 환경변수 누락. UI 에서 해당 변수 확인 후 재배포.

### psql: FATAL: password authentication failed for user "app_service"

원인: `pg_hba.conf` 또는 DSN 비밀번호 불일치. 표준형식 DSN 사용 여부 확인.

```bash
# DSN 형식 확인
echo $LEGAL_RAG_DB_DSN
# postgresql://app_service:...@127.0.0.1:5432/legaldb  ← 정상
# host=127.0.0.1 dbname=legaldb user=app_service ...    ← 마스킹 불가, 표준형식으로 변경
```

### pgvector 확장 없음 오류

```sql
ERROR:  type "vector" does not exist
```

원인: `01_extensions.sql` 미적용 또는 pgvector 미설치.

```bash
sudo apt-get install -y postgresql-15-pgvector
psql "$DSN" -f presets/ddl/augments/legal/01_extensions.sql
```

### /auth/login 429 Too Many Requests (정상 동작 확인용)

Traefik rate-limit 미들웨어 정상 동작. 1분 대기 후 재시도. 브루트포스 차단 의도.

### RLS 로 인한 0건 반환 (예상치 못한 경우)

변호사 UUID가 `app.current_user_id` 로 올바르게 설정되었는지 확인:

```sql
-- 현재 세션 변수 확인
SELECT current_setting('app.current_user_id', true);
-- 올바른 UUID 가 나와야 함

-- 없으면 빈 문자열 → 모든 RLS 정책 불통과 → 0건 (fail-safe 동작, 정상)
```

토큰의 `sub` 클레임이 `legal_attorney.id` 와 일치하는지 jwt.io 에서 디코딩 확인 (서명 검증 필요 없는 페이로드 확인용).
