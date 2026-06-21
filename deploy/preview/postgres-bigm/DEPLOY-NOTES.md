# postgres-bigm — 배포 메모 (DevOps)

## 이미지 정체

`legal-rag-postgres-bigm:pg16` — pgvector/pgvector:pg16 기반 + pg_bigm 1.2 소스빌드 추가.  
`CREATE EXTENSION pg_bigm` 가 가능한 상태. 실제 `CREATE EXTENSION` 호출은 DBA 마이그레이션(`01_extensions.sql` DO 블록)이 담당.

## Coolify 에서 적용 방법

1. Coolify UI → legal-rag 서비스 → **Redeploy** (force rebuild 체크)
2. Coolify 는 `docker_compose_location` 의 `db.build.context` 를 인식해 `./postgres-bigm/Dockerfile` 을 빌드한다.
3. 빌드 후 기존 `legal-rag-pgdata` 볼륨은 **그대로 마운트됨** (pg16→pg16, 데이터 호환, 볼륨명 변경 없음).
4. 컨테이너 기동 후 `legal-rag.apply-schema.sh` 재실행 — `01_extensions.sql` DO 블록이 pg_bigm을 자동 활성화함.

## 빌드 시간 / 캐시 전략

| 상황 | 예상 빌드 시간 |
|---|---|
| 최초 빌드 (apt + wget + make) | 3~6분 (VPS CPU 성능 의존) |
| pg_bigm ARG 미변경 재빌드 | Docker layer cache hit → 수초 |
| pg_bigm 버전 핀 변경 시 | 전체 RUN 레이어 재실행 (3~6분) |

Coolify 는 Redeploy 시 기본적으로 캐시를 재사용한다. 강제 클린 빌드는 Coolify "Force Rebuild" 토글.

## 데이터 볼륨 보존 확인

- 볼륨명: `legal-rag-pgdata` (compose.yml `volumes` 섹션 고정, 변경 금지)
- 이미지 교체 전후 pg 메이저 버전 동일 (16→16) → pgdata 디렉터리 구조 호환
- Coolify managed volume 이므로 Redeploy 로는 볼륨 삭제되지 않음
- 단, Coolify "Delete Service" 는 볼륨 삭제 포함 — **절대 실행 금지**

## Coolify build context 주의사항

- `legal-rag.compose.yml` 의 `db.build.context: ./postgres-bigm` 는 **compose 파일 위치 기준 상대경로**.
- Coolify 는 `docker_compose_location: /deploy/preview/legal-rag.compose.yml` 로 등록되어 있으므로  
  실제 build context = `<clone-root>/deploy/preview/postgres-bigm/` — 올바른 경로.
- embed/app 서비스의 build context (`.` = repo root) 와 혼동 주의.

## 리스크

1. **최초 빌드 실패 가능성**: pg_bigm 소스 URL 또는 SHA256 checksum 불일치 시 빌드 실패.  
   `Dockerfile` ARG `PGBIGM_SHA256` 가 실제 tarball 과 불일치하면 `sha256sum --check` 에서 즉시 실패.  
   이 경우 Coolify 빌드 로그에서 확인 후 CTO 에 보고.
2. **apt mirror 네트워크 지연**: VPS 위치(KR)에서 Debian 패키지 다운로드가 느릴 수 있음. 재시도로 해소.
3. **pg_bigm PGXS 경로**: `postgresql-server-dev-16` 패키지가 pg_config 를 올바른 경로에 설치해야 `USE_PGXS=1` 가 작동.  
   pgvector/pgvector:pg16 (Debian 기반) 에서 이미 검증된 패턴 — 동일 베이스이므로 동작 예상.
