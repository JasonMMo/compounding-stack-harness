# deploy/preview/hanbang-rag.md
# 한방 급여기준 RAG 데모 — 배포 런북 (preview 티어)

> 소유: DevOps (Growth-136). 현재 라이브: **수동 docker compose** (CTO 실행, founder 인가).
> URL: https://hanbang-rag.n9n.co.kr/app/ — 로그인 후 검색.

## 1. 토폴로지 (legal-rag 자원 재사용)

legal-rag 와 달리 **app-only**. 한방 corpus(`hanbang_rag_*`, 781청크)는 legal-rag 의
postgres(`legaldb`)에 적재돼 있고, embed 모델(intfloat/multilingual-e5-base, 768d)도 동일.
따라서 hanbang app 은 legal-rag 의 docker network(`gwpba3e8j8upf9v0swf96wkt`)에
**external network** 로 합류해 `db:5432`·`embed:8080` 을 서비스명으로 resolve 한다.

- 중복 0 (db/embed 신규 컨테이너 없음), legal-rag 배포와 비결합(별도 재배포).
- coolify-proxy(Traefik v3.6)가 이 네트워크에 연결돼 있어 라벨만으로 자동 라우팅.
- DNS: `*.n9n.co.kr` wildcard → 187.77.140.157 (서브도메인 추가 불필요).

## 2. 코드 구성 (커밋 완료)

| 파일 | 내용 |
|---|---|
| `services/hanbang-rag/web/` | vanilla SPA (index.html·app.js 778줄·styles/). legal `/app` 슬림화: 사건 기능 전부 제거, 로그인+검색+고시원문드로어. |
| `services/hanbang-rag/api.py` | `/app` StaticFiles 마운트 추가(조건부). |
| `services/hanbang-rag/Dockerfile` | CMD `uvicorn api:app`. web/ 는 `COPY services/hanbang-rag/ .` 에 포함. |
| `deploy/preview/hanbang-rag.compose.yml` | app-only, external net, Traefik 라벨(+/auth/login ratelimit). |

## 3. 환경변수 (.env / Coolify 패널 — 시크릿 미커밋)

```
HANBANG_RAG_DB_DSN=postgresql://app_service:<PW>@db:5432/legaldb
HANBANG_RAG_JWT_SECRET=<openssl rand -hex 32>
HANBANG_RAG_SERVICE_TOKEN=<openssl rand -hex 32>
HANBANG_RAG_INGEST_ROOT=/data/hanbang-docs
HANBANG_RAG_EMBED_MODEL_VERSION=multilingual-e5-base
```
> DSN user 는 `app_service` (BYPASSRLS). api.py 로그인이 `hanbang_rag_user` 를 읽는데
> `app_user` 는 거기 grant 가 없기 때문. 공개 고시 corpus 라 행 격리 불요 → 허용.
> EMBED_URL 은 compose 에 `http://embed:8080` 하드(내부 서비스명, 외부 노출 0).

## 4. 수동 배포 절차 (현재 라이브 방식)

```bash
# 1) 소스 전송 (repo → VPS, 캐시 제외)
ssh root@187.77.140.157 'rm -rf /root/hanbang-deploy && mkdir -p /root/hanbang-deploy/services'
tar --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.pyc' \
    -czf - -C services hanbang-rag | ssh root@187.77.140.157 'tar -xzf - -C /root/hanbang-deploy/services'
scp deploy/preview/hanbang-rag.compose.yml root@187.77.140.157:/root/hanbang-deploy/

# 2) .env 작성 (시크릿 — 출력 금지), ingest 디렉터리
ssh root@187.77.140.157 'mkdir -p /data/hanbang-rag/ingest && chmod 0777 /data/hanbang-rag/ingest'
# /root/hanbang-deploy/.env 에 §3 5키 작성, chmod 600

# 3) 빌드·기동
ssh root@187.77.140.157 'cd /root/hanbang-deploy && docker compose -f hanbang-rag.compose.yml up -d --build'
```

## 5. 검증 (수용 기준)

`python3 deploy/preview/hanbang-rag.verify-search.py` (VPS 호스트에서 공개 URL 타격):
- `[LOGIN] HTTP 200 role=admin token=OK`
- 5시나리오 각 `total_results>0` + 인용 `notice_number` 표시
- `[DOC] HTTP 200 ... full_text_len>0` (고시 원문 드로어)

데모계정: `demo@hanbang-rag.local` / `hanbang2026`.

## 6. Coolify 정식 등록 (founder 선택 — 권장)

수동 컨테이너는 git auto-redeploy 가 없다. 정식화하려면:
- Coolify → New Resource → Docker Compose, repo `master`,
  compose location `/deploy/preview/hanbang-rag.compose.yml`.
- env 패널에 §3 5키 입력. external network 블록은 Coolify 가 존중함.
- 등록 후 수동 컨테이너(`hanbang-deploy-app-1`) 중지·제거(라우터 충돌 방지).

## 7. 잔여/주의

- ✅ **표·서식 청크 정제 완료 (Growth-137, 2026-06-30)** — `ingest_hanbang_notices.py`
  의 `clean_admrul_text()` 가 별표 박스드로잉 테두리(─━│┃┼)·용지규격을 제거(셀 텍스트
  보존). 재인제스트 결과 **청크 781→125**, 박스문자 chunk·full_text 모두 0, 5시나리오
  라이브 PASS·발췌문 청결. 재인제스트 절차: §8 참조.
- 한국어 simple-FTS 부분문자열 미스(첩약 등) — pg_bigm 바이그램은 legal-rag 와 공유 이미지라
  동일 개선 트랙. ([[legal-rag-korean-lexical-pass]])
- 프로덕션 전: STORAGE 바디제한(Traefik)·app_service→app_user 분리 검토.

## 8. corpus 재인제스트 (정제 로더 변경 시)

corpus 정제 로직(`scripts/corpus/ingest_hanbang_notices.py`)을 바꾼 뒤 라이브 반영:

```bash
# 1) 갱신 로더를 VPS 인제스트 디렉터리에 동기화
scp -i ~/.ssh/n9n_preview_ed25519 scripts/corpus/ingest_hanbang_notices.py \
    root@187.77.140.157:/root/hanbang-poc/ingest/

# 2) gwpba3e8 네트워크 one-off 컨테이너로 재인제스트 (DSN 은 실행중 app env 에서
#    읽어 변수로만 전달 — stdout 노출 0). app 이미지에 psycopg+httpx 포함.
ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157 '
  DSN=$(docker inspect hanbang-deploy-app-1 --format "{{range .Config.Env}}{{println .}}{{end}}" \
        | grep "^HANBANG_RAG_DB_DSN=" | cut -d= -f2-)
  docker run --rm --network gwpba3e8j8upf9v0swf96wkt \
    -v /root/hanbang-poc/ingest:/app \
    -v /root/hanbang-poc/out/corpus/hanbang:/corpus:ro \
    -e DSN="$DSN" -e EMBED=http://embed:8080 -e CORPUS=/corpus \
    -e MODEL=multilingual-e5-base -e PYTHONIOENCODING=utf-8 \
    -w /app hanbang-rag-app:latest python ingest_hanbang_notices.py'
```

ingest.py 의 ON CONFLICT upsert + orphan 삭제(`chunk_index >= len(chunks)`)가 정합성을
보장하므로 청크 수가 줄어도 고아 청크 없음. 앱 재시작 불요(쿼리시 DB 직독). 검증: §5.
