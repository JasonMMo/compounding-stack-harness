# Session Handoff — 2026-06-13 (updated)

## Session 범위

Growth-49 ~ Growth-54 완료. Capacitor axis-4 scaffold + 5개 업종 데모 배포 + 데모 포털 구축 + 6개 데모 seed data 내장 배포 + **manufacturing-demo 7번째 업종 추가**.

---

## 완료 항목

### Growth-49 — Capacitor adapter scaffold
- `frontend/adapters/capacitor/capacitor.config.ts` — remote server mode (`server.url: https://edu-program.n9n.co.kr`)
- `frontend/adapters/capacitor/package.json` — @capacitor/cli ^8.4.0, typescript ^6.0.3
- `frontend/adapters/capacitor/.gitignore`
- **로컬 작업 미완**: `npm install && npm run add:android && npm run add:ios` 는 로컬에서 직접 실행 필요

### Growth-50 — 5개 업종 데모 profile 생성
- `profiles/logistics-demo.yaml`
- `profiles/distribution-demo.yaml`
- `profiles/construction-demo.yaml`
- `profiles/itservice-demo.yaml`
- `profiles/trading-demo.yaml`

### Growth-51 — 5개 데모 + 포털 Coolify 배포
- `deploy/preview/{slug}.compose.yml` 5개 생성
- `deploy/preview/demo-portal.compose.yml` 생성
- `demo-portal/Dockerfile` + `demo-portal/index.html` 생성
- `scripts/workflow/deploy_demo_portal.py` 생성
- Windows cp949 인코딩 버그 픽스: `deploy_to_coolify.py`, `scaffold.py`에 `sys.stdout.reconfigure(encoding="utf-8")` 추가

### Growth-52 — 도메인 라우팅 충돌 해결 + edu-demo 카드 추가
- `demo.n9n.co.kr` -> edu-program 으로 포워딩되던 문제 해결
  - edu-program(uuid: `tp0608w5b013sypb4euwplld`) 도메인을 `edu-program.n9n.co.kr` 단독으로 복구
- `demo-portal/index.html` 6번째 카드(교육기관) 추가
- 포털 재배포 완료

---

## 라이브 상태 (모두 HTTP 200 확인)

| URL | 용도 |
|---|---|
| https://demo.n9n.co.kr | 데모 포털 (7개 업종 카드) |
| https://logistics-demo.n9n.co.kr/login | 물류·운송 |
| https://distribution-demo.n9n.co.kr/login | 도매·유통 |
| https://construction-demo.n9n.co.kr/login | 건설·시공 |
| https://itservice-demo.n9n.co.kr/login | IT서비스 |
| https://trading-demo.n9n.co.kr/login | 무역·수출입 |
| https://edu-program.n9n.co.kr/login | 교육기관 (6번째 카드) |
| https://manufacturing-demo.n9n.co.kr/login | 제조업 (7번째 카드) |

로그인: `admin` / `demo1234`

---

## Coolify 앱 UUID 맵

| slug | uuid |
|---|---|
| edu-program | `tp0608w5b013sypb4euwplld` |
| demo-portal (active) | `s6872cr0asfp02sc0vgw8wi2` |
| demo-portal (stale dup) | ~~`gwdizi7tws4yabv25xnbph0w`~~ (Growth-55에서 삭제) |
| logistics-demo | `hmb6jp67w6stmhsdi6e4h73o` |
| distribution-demo | `gufoc3trwh2umw53k93bjdyp` |
| construction-demo | `l3dyahzqjssm4l15tjpc75cj` |
| itservice-demo | `iguqvhla1cnhhjm14f3xgi2h` |
| trading-demo | `ybawqjqryxst5ofwnekaxpak` |
| manufacturing-demo | `ufbllprbzrg8pktn9yfhsybq` |
| server | `n12vdydjpwp81hu5i15n1gsb` |

---

## 인프라 핵심 사실 (다음 세션 필독)

- **FastAPI 백엔드**: `InMemoryEntityStore` 사용 — PostgreSQL 없음. 데모 앱 시작 시 빈 화면이 정상.
  씨드 데이터가 필요하면 `SEED_FILE` 환경변수로 JSON 경로 지정.
- **Compose build context**: Coolify는 repo root 기준 — `COPY demo-portal/index.html` (not `COPY index.html`)
- **Coolify race condition**: 앱 생성 후 `docker_compose_raw` 로드까지 10~15초. domain PATCH 전 polling 필요.
- **Coolify 배포 엔드포인트**: `GET /applications/{uuid}/start` (POST /deploy 아님)
- **domain PATCH**: `{"docker_compose_domains": [...], "force_domain_override": True}` — raw list, json.dumps 금지
- **토큰 보안**: `TOKEN=$(tr -d ' \t\r\n' < infra/secrets/coolify_api_token)` 길이만 확인. 값 출력 절대 금지.
- **SSH key**: `~/.ssh/n9n_preview_ed25519` (repo 외부 operator-local)

---

## 완료 추가

### Growth-54 — manufacturing-demo 7번째 업종 추가 (2026-06-13)
- `profiles/manufacturing-demo.yaml` — production·quality·inventory·procurement·hr 5 도메인
- `presets/ddl/catalog.yaml` — production-plan·production-result·ncr 3개 엔티티 신규 추가
- `seed-data/manufacturing-demo.json` — 97 레코드 (work-order·BOM·defect·ncr 등)
- `deploy/preview/manufacturing-demo.compose.yml` + Coolify 배포
- `demo-portal/index.html` — 7번째 카드 추가, "7가지 업종" 업데이트
- **트러블슈팅**: deploy_to_coolify.py 실행 전 파일 커밋·푸시 필수 (미커밋 시 compose_raw null)

### Growth-55 — Coolify stale app 정리 (2026-06-13)
- `gwdizi7tws4yabv25xnbph0w` (demo-portal 중복) DELETE — HTTP 200
- project `xngfun8b14dchdujcwl3898c` (빈 project) DELETE — HTTP 200
- active app `s6872cr0asfp02sc0vgw8wi2` 생존 확인

### Growth-53 — 6개 데모 seed data 내장 (2026-06-13)
- `seed-data/logistics-demo.json` + 5개 추가 — 업종별 한국 현실 데이터 (carrier/shipment/vendor/employee 등)
- `backend/adapters/fastapi/Dockerfile` — `COPY seed-data/ /app/seed-data/` 추가
- 6개 compose — `SEED_FILE: /app/seed-data/{slug}.json` 환경변수 추가
- edu-program compose: 기존 bind-mount 방식 제거 → repo 내장 방식으로 전환
- 전 슬러그 재배포 완료 — HTTP 200 확인

---

## 오픈 루프 (우선순위 순)

### ~~P1 — demo-portal 중복 project 정리~~ ✅ Growth-55 완료
- stale app(`gwdizi7tws4yabv25xnbph0w`) + 빈 project(`xngfun8b14dchdujcwl3898c`) API로 삭제

### ~~P2 — manufacturing-demo 추가~~ ✅ Growth-54 완료

### P2 — Capacitor 로컬 플랫폼 setup
- `frontend/adapters/capacitor/` 에서 직접 실행: `npm install && npm run add:android && npm run add:ios`

### P3 — Supabase backend adapter 구현
- 현재 `backend/adapters/supabase/README.md` 스캐폴드만 존재
- M3 이후 SaaS 모드 전제조건

---

## 최신 git (master)

```
17f18da  feat(portal): manufacturing-demo 7번째 카드 추가 + 섹션 "7가지" 업데이트
```

모든 변경사항 push 완료.

---

## 다음 세션 시작 체크리스트

1. `https://demo.n9n.co.kr` 접속 확인 (7개 카드 표시)
2. `https://manufacturing-demo.n9n.co.kr/login` — 데이터 표시 확인
3. 오픈 루프 P1 (Coolify stale app 정리) 또는 P3 (Supabase adapter) 중 선택
4. SSH 터널 확인: `ssh -L 8000:localhost:8000 n9n_preview` 후 `curl http://localhost:8000/api/v1/version`
