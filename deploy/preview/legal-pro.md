# deploy/preview/legal-pro.md
# legal-pro React SPA — L4 배포 절차 (preview 티어)

> 소유: DevOps (Growth-35). 라이브 트리거는 **founder 실행**.
> 서빙 전략: 전략 A — legal-rag FastAPI /pro StaticFiles 마운트 (동일 오리진, CORS 0).

## 1. 전략 요약

legal-pro React SPA(`frontend/adapters/legal-pro/`)를 legal-rag 백엔드(FastAPI, `legal-rag.n9n.co.kr`)와 **동일 오리진**으로 서빙한다.

- URL: `https://legal-rag.n9n.co.kr/pro` (로그인 랜딩)
- Vite `base=/pro/`, React Router `basename="/pro"` 설정됨
- API 호출(`/auth`, `/search`, `/cases`, `/documents`, `/health`)은 동일 오리진 → CORS 헤더 불필요
- 기존 vanilla SPA(`/app`)는 그대로 유지됨 — 충돌 없음

## 2. 코드 변경 요약 (커밋 완료 전제)

| 파일 | 변경 내용 |
|---|---|
| `frontend/adapters/legal-pro/vite.config.ts` | `base: '/pro/'` 추가 |
| `frontend/adapters/legal-pro/src/main.tsx` | `BrowserRouter basename="/pro"` 추가 |
| `services/legal-rag/Dockerfile` | multi-stage: Node 20 stage에서 prebuild 의존 서브트리 COPY → `npm run build` → dist/ 를 runtime stage `web/pro/`로 COPY |
| `services/legal-rag/api.py` | `/pro` StaticFiles 마운트 추가 (마지막 줄, `/app` 패턴 동일) |

> FastAPI API 핸들러(검색/사건/RLS 로직)는 변경하지 않았다.

## 3. Dockerfile Stage 1 구조 (REPO_ROOT 해석)

```
WORKDIR /src
COPY middle/contract/ ./middle/contract/            # codegen.mjs 의존
COPY presets/themes/legal-pro/ ./presets/themes/legal-pro/   # build-tokens.mjs 의존
COPY services/legal-rag/web/styles/ ./services/legal-rag/web/styles/  # build-tokens.mjs 의존
COPY frontend/adapters/legal-pro/package*.json ./frontend/adapters/legal-pro/
WORKDIR /src/frontend/adapters/legal-pro
RUN npm ci
COPY frontend/adapters/legal-pro/ ./
RUN npm run build   # prebuild: codegen → build-tokens → tsc+vite → dist/
```

REPO_ROOT 손계산: `__dirname=/src/frontend/adapters/legal-pro/scripts`, `resolve('../../../..') = /src` → COPY 경로와 정확히 일치.

## 4. 빌드 의존 사항 (Coolify 자동 처리)

- Coolify 가 `legal-rag.compose.yml`의 `app` 서비스를 Redeploy하면 `services/legal-rag/Dockerfile`의 multi-stage 빌드가 수행된다.
- Stage 1(Node 20): `npm ci` → `npm run build` — 빌드 시간 약 60~120초 추가 예상 (최초, 이후 레이어 캐시).
- Stage 2(Python 3.11): 기존과 동일, `web/pro/` COPY 추가.

## 5. founder 실행 배포 절차

### 전제 조건 확인
- [ ] 이 PR/커밋이 `master` 브랜치에 push되어 있어야 함 (CTO 실행)
- [ ] Coolify의 `legal-rag` 서비스가 git repo `master` 를 트래킹하고 있음

### 단계별 절차

1. **git push 확인** (CTO가 먼저 실행)
   - 이 문서와 함께 커밋된 5개 파일이 `master`에 있는지 GitHub에서 확인.

2. **Coolify 로그인**
   - URL: VPS 관리 IP 또는 Coolify 설치 포트 (기존 접속 방법 동일)

3. **legal-rag 서비스 Redeploy**
   - Coolify UI 좌측 메뉴 → Projects → legal-rag 프로젝트 → `app` 서비스 선택
   - 우상단 **"Redeploy"** 버튼 클릭
   - 빌드 로그 창에서 정상 순서 확인:
     ```
     [stage-1/frontend-builder] COPY middle/contract/ ...
     [stage-1/frontend-builder] COPY presets/themes/legal-pro/ ...
     [stage-1/frontend-builder] COPY services/legal-rag/web/styles/ ...
     [stage-1/frontend-builder] npm ci --prefer-offline
     [stage-1/frontend-builder] npm run build
       > prebuild: codegen.mjs  (contract.gen.ts 생성)
       > prebuild: build-tokens.mjs  (tokens.gen.css 생성)
       > tsc + vite build → dist/
     [stage-2] pip install ...
     Successfully deployed
     ```

4. **빌드 실패 시 로그 확인 포인트**
   - `codegen.mjs` 실패: `/src/middle/contract/error/codes.yaml` 미발견 → Stage 1 COPY 라인 확인
   - `build-tokens.mjs` 실패: `/src/services/legal-rag/web/styles/tokens.css` 또는 `/src/presets/themes/legal-pro/tokens.css` 미발견 → Stage 1 COPY 확인
   - `tsc` 실패: contract.gen.ts 미생성 → codegen 단계 로그 확인
   - `COPY --from=frontend-builder /src/frontend/adapters/legal-pro/dist ./web/pro` 실패: dist/ 미생성 → npm build 로그 재확인

## 6. 배포 후 검증

### 접속 URL
- 메인: `https://legal-rag.n9n.co.kr/pro`
- 로그인 후 사건 현황: `https://legal-rag.n9n.co.kr/pro/cases`
- 기존 vanilla SPA (회귀): `https://legal-rag.n9n.co.kr/app`

### 스모크 체크 항목 (순서대로)

1. `GET https://legal-rag.n9n.co.kr/pro` → HTTP 200, React HTML 반환 (브라우저 또는 curl)
2. 브라우저에서 `/pro` 열기 → 로그인 화면 렌더링 확인 (법무 판례 검색 헤더)
3. 데모 계정(박민준 또는 이지현)으로 로그인 → `/pro/cases` 리다이렉트 + 사건 목록 표시
4. 판례 검색 탭 클릭 → `/pro/search` 화면 정상
5. 직접 URL 입력 `https://legal-rag.n9n.co.kr/pro/cases/...` (새로고침) → 200, React Router SPA 처리 (html=True fallback 동작 확인)
6. `GET https://legal-rag.n9n.co.kr/app` → 기존 vanilla SPA 정상 (회귀 없음)
7. `GET https://legal-rag.n9n.co.kr/health` → `{"status":"ok"}` (API 정상)

### 실패 시 롤백
- `/pro` StaticFiles 조건부 마운트: `web/pro/` 디렉터리 부재 시 마운트 자체를 건너뜀 (`os.path.isdir` 가드) → 기존 `/app`·API는 정상 유지.
- Node 빌드 실패 시 이전 커밋으로 Redeploy하면 multi-stage 제거됨 (Stage 2만 남아 기존 동작 복원).

## 7. 리스크 / 주의사항

| 항목 | 내용 |
|---|---|
| 빌드 시간 증가 | Node 20 stage 최초 빌드 +60~120s. 이후 레이어 캐시(npm ci) 로 단축 |
| prebuild REPO_ROOT 의존 | codegen.mjs·build-tokens.mjs 가 `resolve('../../../..')` 로 repo-root 를 계산. Stage 1 WORKDIR=/src, 어댑터는 `/src/frontend/adapters/legal-pro/`에 위치하므로 REPO_ROOT=/src 로 정확히 해석됨. .dockerignore 에 middle/·presets/·services/legal-rag/web/ 배제 항목 없음(확인 완료). |
| 이미지 크기 증가 | multi-stage 덕에 Node/npm 은 runtime 이미지에 포함 안 됨 — 문제 없음 |
| React Router SPA fallback | FastAPI StaticFiles `html=True` 가 `/pro/<path>` 직접 접근 시 index.html 반환. FastAPI API 라우트(`/auth`, `/search` 등)는 StaticFiles 보다 먼저 등록되어 있어 충돌 없음 |
| 로컬 개발 base 변경 | `base: '/pro/'` 설정으로 `npm run dev` 시 `http://localhost:5174/pro` 로 접속해야 함 |

## 8. 디지털 자산 레지스트리 갱신 (배포 완료 후)

`infra/registry/` 에 아래 항목 추가:
- 서브도메인: `legal-rag.n9n.co.kr/pro` (경로 기반 — 서브도메인 추가 없음)
- 서비스: legal-pro React SPA, legal-rag 동일 Coolify 서비스에 포함
- 상태: preview (고객 데모용)

## 9. G-2 C3 문서업로드 배포 추가요건 (Growth-108)

C3(`POST /cases/{id}/documents` 비동기 ingest)는 업로드 파일을 디스크에 영구 저장한다.
아래 3건은 **founder/DevOps 가 Coolify 에서 설정**해야 업로드가 동작·존속한다.

> **전제**: 9-1 ~ 9-3 이 모두 충족되어야 §9-4 스모크(항목 8~11)가 통과한다.
> 라이브 첫 테스트(2026-06-22)에서 3건 모두 설정 갭으로 드러남 — 코드는 정상이었고 전부 배포환경 문제였다.

### 9-1. 환경변수 + compose passthrough (필수)

두 단계가 **모두** 필요하다. 한쪽만 해도 컨테이너 미주입 → 500.

1. **Coolify 환경변수 패널** — `LEGAL_RAG_STORAGE_ROOT` 값 입력 (예: `/data/legal-docs/case-uploads`).
   구 예시 `/data/legal-storage` 는 영구볼륨 밖이라 Redeploy 시 소멸 위험이므로 사용 금지.
2. **compose 매핑 확인** — `legal-rag.compose.yml` 의 `app` 서비스 `environment:` 블록에
   `LEGAL_RAG_STORAGE_ROOT: ${LEGAL_RAG_STORAGE_ROOT}` 가 있어야 컨테이너로 주입된다
   (커밋 e5d7dd9 에서 반영 완료).
3. **적용 확인** — Redeploy 후 **app 컨테이너** 터미널(Coolify → app 서비스 → Terminal)에서:
   ```
   printenv LEGAL_RAG_STORAGE_ROOT
   ```
   값이 출력되어야 한다. 빈 출력이면 패널 값 저장 또는 compose 매핑을 다시 확인.

미설정 시 증상: 업로드 엔드포인트 500 ("문서 저장소가 설정되지 않았습니다", api.py:1271-1273).

### 9-2. 영구 볼륨 + 호스트 디렉터리 쓰기권한 (필수)

두 단계가 **모두** 필요하다.

#### 9-2-a. Coolify persistent volume (bind-mount)
- `LEGAL_RAG_STORAGE_ROOT` 가 가리키는 경로를 영구 bind-mount 로 마운트.
  미마운트 시 Redeploy/재시작마다 업로드 파일 소멸(컨테이너 레이어 휘발). 비동기 ingest 가
  파일을 읽기 전 재배포되면 status=error.
- `legal-rag.compose.yml` 의 `app` 서비스에 volume 매핑 추가 후 Coolify 동기화.

#### 9-2-b. 호스트 디렉터리 쓰기권한 (bind-mount 사용 시 필수)
- app 컨테이너는 non-root `appuser`(Dockerfile:67)로 실행된다. 호스트 디렉터리가 root
  소유인 상태로 bind-mount 되면 `appuser` 가 파일을 쓰지 못해 500("파일 저장에 실패했습니다", api.py:1338-1355 except).
- **호스트(VPS)에서 디렉터리 사전 생성 + 권한 설정** (SSH 또는 Coolify db Terminal 아님 — VPS shell):
  ```bash
  # preview 티어 (단일테넌트): chmod 0777 허용
  mkdir -p /data/legal-rag/ingest/case-uploads
  chmod 0777 /data/legal-rag/ingest/case-uploads

  # 프로덕션: appuser UID 확인 후 chown (보안 우선)
  # docker exec <app-container> id appuser   → uid=XXXX
  # chown XXXX /data/legal-rag/ingest/case-uploads && chmod 0750 .../case-uploads
  ```
- 호스트 디렉터리 권한 변경은 **Redeploy 없이 즉시·존속**한다 (bind-mount 특성).
- 확인: Coolify app Terminal → `ls -la /data/legal-docs/case-uploads/` 권한 확인.

### 9-3. 라이브 DB grant 적용 (필수)

`presets/ddl/augments/legal/09_grants.sql` 의 INSERT/UPDATE grant 가 라이브 postgres 에
**미반영 상태일 수 있다** — Coolify Redeploy 는 DDL 을 재실행하지 않는다 (DDL-in-repo ≠ live-DB).

**증상**: 사건 생성 403(api.py:828 42501 catch), 당사자 추가 404(api.py:1038), 당사자 수정 500
(update_party 는 42501 catch 없음).

**grant 적용 확인** — Coolify db 서비스 Terminal 에서:
```sql
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'app_user'
  AND table_name IN ('cases','case_parties','case_documents');
```
`cases`/`case_parties`/`case_documents` 각각 INSERT·UPDATE 6행이 모두 있어야 한다.
누락 시 아래 절차로 재적용.

**grant 재적용 절차** (SSH 키 불가 시 Coolify db 서비스 Terminal 사용):
- Coolify → db 서비스 → Terminal → `psql -U "$POSTGRES_USER" -d legaldb`
- 웹터미널에서 heredoc(`<<EOF`)은 깨지므로 **한 줄씩** 실행:
  ```sql
  GRANT INSERT, UPDATE ON TABLE cases TO app_user;
  GRANT INSERT, UPDATE ON TABLE case_parties TO app_user;
  GRANT INSERT, UPDATE ON TABLE case_documents TO app_user;
  ```
- 멱등(이미 적용된 grant 재실행은 무해). 재적용 후 앱 재시작 불필요.
- 09_grants.sql 전체를 일괄 실행할 경우: `psql -U "$POSTGRES_USER" -d legaldb -f /path/to/09_grants.sql` (파일이 컨테이너 내 마운트된 경우).

### 9-4. 업스트림 바디 크기 제한 (CISO CAVEAT-A — 권고)
- 앱은 `content = await file.read()` 후 20MiB 검사 → 업스트림 limit 부재 시 거대 업로드가
  메모리에 먼저 적재되어 OOM 위험. **Traefik/nginx 에서 `client_max_body_size`(nginx) 또는
  Traefik `maxRequestBodyBytes` 를 22m(≈23068672)** 로 설정해 앱 도달 전 차단 권고.
  단일테넌트 preview 티어에서는 BLOCK 아님(CISO PASS), 프로덕션 인도 전 적용.

### 9-5. C3 스모크 추가 항목 (§6 체크리스트 이후)

> 9-1(환경변수+compose) · 9-2(볼륨+권한) · 9-3(grant) 가 모두 완료되어야 아래 항목이 통과한다.

8. `/pro/cases/<id>` → 문서 업로드 패널에서 .pdf/.txt 첨부 → 201, 뱃지 "대기중"(pending)
9. 5~60초 후 폴링으로 뱃지 "색인완료"(done) 전환 확인 (비동기 ingest 동작)
10. `.exe` 첨부 시도 → 400 거부 (확장자 allowlist)
11. Redeploy 후 업로드 파일 잔존 확인 (9-2 영구볼륨 검증)
