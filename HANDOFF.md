# Session Handoff — 2026-06-16

## 이번 세션 범위 (최신)

**마케팅사이트 8축(theme/section) 트랙 — 페이지-구조 아키타입 확장 (Growth-75 → 80)**.
웹에이전시형 랜딩 데모를 "테마(색·폰트)" 다양성에서 **페이지 구조 아키타입(A1~A6)** 다양성으로 확장 중. CEO 가 "색·텍스트만 다른 같은 패턴"을 지적(Growth-76) → 진짜 차별은 **섹션 variant × 페이지 아키타입 × 테마의 곱**이라는 결론. 블루프린트: [`docs/architecture/landing-pattern-matrix.md`](docs/architecture/landing-pattern-matrix.md).

> ✅ **Growth-80 빌드·검증 완료** + **Growth-81 LIVE 배포 완료**. A1 FLUX(인프라 SaaS) — flux 테마 + 신규 섹션 3종, 로컬 ui_check **7/7 PASS**.
> ✅ **FLUX LIVE** — https://flux.n9n.co.kr (HTTPS 200, 서빙 마크업 stats/bento/pull-quote 검증). 6번째 마케팅 데모 카드 + 레지스트리 등록 완료. **P0 종결**.

---

## 완료 항목 (마케팅사이트 트랙, Growth-75~80)

| Growth | 아키타입 / 산출 | 테마 | LIVE URL | 상태 |
|---|---|---|---|---|
| 75 | (테마 다양성) HOPWELL 맥주 런칭 | harvest | https://hopwell.n9n.co.kr | ✅ LIVE |
| 76 | **A2** Creative Agency/Portfolio — Studio North | atelier | https://studio-north.n9n.co.kr | ✅ LIVE |
| 77 | **A4** 공예/로컬 — TERRA ceramics (첫 scroll-cinematic) | kiln | https://terra-ceramics.n9n.co.kr | ✅ LIVE |
| 78 | **A6** B2B 매니지드IT — MERIDIAN | meridian | https://meridian.n9n.co.kr | ✅ LIVE |
| 79 | (툴링) 공식 Anthropic 스킬 5종 검토 → webapp-testing 1종 채택 | — | — | ✅ |
| 80 | **A1** SaaS Product Launch — FLUX (인프라/관측성) | flux | https://flux.n9n.co.kr | ✅ LIVE |
| 81 | (배포) A1 FLUX LIVE + 포털 6번째 카드 + 레지스트리 | flux | https://flux.n9n.co.kr | ✅ LIVE |

- **라이브 마케팅 데모 6종**: gtm-landing(indigo aurora) · hopwell · studio-north · terra-ceramics · meridian · **flux**. 포털에 카드 6장. (※ 별도로 Growth-57 business-system 데모 7종은 `*-demo.n9n.co.kr` — 아래 참조표.)
- **테마 6종**: aurora(gtm) · harvest · atelier · kiln · meridian · **flux**(신규). 누적 위치 `presets/themes/<slug>/`.
- **섹션 카탈로그**: Growth-80 으로 **14/14 type 완성**(stats type 추가), HAVE variant 30. 단일진실 `presets/site-sections/catalog.yaml`.

### Growth-80 (A1 FLUX) 세부 — 다음 세션 직접 관련
- **flux 테마**: amber-gold `#8B5E10` 단일 액센트(OKLCH H72 미점유) + charcoal flat hero, Space Grotesk + Inter. aurora violet/Bricolage 와 hue·폰트·레지스터 3축 분리. 네온/터미널그린 반사 회피.
- **신규 섹션**: `stats`(ticker-band, 카드 박싱 없는 인라인 통계 밴드) + `features/bento-mosaic`(불규칙 grid, hero카드 2행span) + `testimonial/pull-quote-wall`(풀블리드 비대칭 인용).
- **profile**: `profiles/flux-demo.yaml` (deliverable_kind=marketing-site).
- **함정/교훈**(재발 주의):
  - ① **인라인 grid-template 은 `@media` 로 못 덮음** → 모바일 오버플로우(453>390px). sentinel 클래스 + scoped `@media` 로 이전해 해결. Tailwind 반응형 prefix 도 인라인 style 무력.
  - ② `logos/horizontal-scroll` **텍스트 워드마크 폴백** 신설(stock 자산 0 규율, meridian monogram 계승). `site_manifest.py` 의 **companies[] emit 누락 버그** 수정(images[] 동형 passthrough) — 커밋 `bea804e`.

---

## 핵심 불변 (다음 세션 필독)

### 마케팅사이트 트랙
- **deliverable_kind = `marketing-site`**: entity/DDL 축 bypass, theme·site-sections(8축) 만 탄다. site-manifest → 테마 → landing-astro 파이프라인. 설계 [`docs/architecture/site-manifest.md`](docs/architecture/site-manifest.md).
- **theme-aware 빌드**: `build-tokens-auto.mjs` 가 manifest 의 theme 키를 자동으로 읽음(Growth-75 에서 aurora 하드코딩 픽스). 새 테마는 Docker 무변경으로 추가.
- **비주얼 검증 불가결**: **build green·detector CLEAN ≠ 비주얼 정상**. Growth-75/76/77 전부 풀페이지 스크린샷이 결함 적발(aurora 색 누수, 빈 플레이스홀더 이미지, below-fold 모션 blank). 배포 전 desktop+mobile+no-JS 풀페이지 스샷 필수.
- **stock 자산 0 규율**: 사진 미사용. 텍스트 워드마크(logos) / monogram-initials(team) / `texture:clay|ash|ember` 센티넬(gallery) 로 운영.
- **모션 reveal SSR 트랩**(Growth-69 계열, 반복): below-fold/headless 에서 blank → threshold 0 + rootMargin 200px + 800ms fallback, no-JS 시 opacity 1.
- **검증 도구**: impeccable detector(antipattern) + `ui_check.py` + Growth-79 채택 `webapp-testing`(Playwright `with_server.py`, 빌드→serve→E2E 일괄).

### 배포 레시피 (Coolify, Growth-75~78 누적)
- `deploy_static_site.py --domain` 은 **https:// 스킴 필수**(없으면 422 Invalid URL).
- `docker_compose_domains` PATCH 포맷: `[{"name":svc,"domain":url}]` 배열.
- Coolify race: 앱 생성 후 `docker_compose_raw` 로드 10~15초, domain PATCH 전 polling.
- 배포 엔드포인트: `GET /applications/{uuid}/start`.
- **배포 전 git push 필수** — 미커밋 시 compose_raw null([[push-before-deploy]] 메모리).
- 토큰: `TOKEN=$(tr -d ' \t\r\n' < infra/secrets/coolify_api_token)` 값 출력 금지. SSH key: `~/.ssh/n9n_preview_ed25519`.
- `COOLIFY_API_BASE` env 사용(Growth-77 오픈루프 종결).
- **SSH 터널 좀비소켓**: 8000 점유/커널 누수 시 다른 로컬 포트(8010)로 재수립 후 직접 API 호출, deploy 스크립트 API_BASE 임시 패치 후 `git checkout` 복구(커밋 오염 방지).

### 공통
- **Windows 인코딩**: `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 로 실행(cp949 em-dash crash 회피).
- **백그라운드 에이전트 cwd 고정 주의**(Growth-76): 세션 cwd 가 landing-astro 에 고정되면 상대경로 훅 깨짐 → 루트로 Set-Location 복구.
- **워크트리 가드**(이번 세션): bg 세션 격리 훅이 깨져 있어 `.claude/settings.json` 에 `"worktree":{"bgIsolation":"none"}` 추가로 in-place 편집 허용함. 훅 복구 시 재검토.

---

## 오픈 루프 (우선순위 순)

### ✅ P0 — FLUX LIVE 배포 (Growth-81 종결)
- A1 FLUX 라이브: https://flux.n9n.co.kr (Coolify project=jq25nyzfirch3flp7no2wg3u, app=oyemv0mttkn8eo05xflvc4x2). 포털 6번째 카드 + `infra/registry/flux.yaml` 등록 완료. 풀테스트 329 PASS(스테일 테스트 1건 동반 수정).

### P1 — catalog copy_slots variant-aware 완화 (Growth-80 발견)
- `pull-quote-wall` 등 items[] 기반 variant 가 catalog testimonial `copy_slots.required(quote/author_name)` 를 강제당해 profile 에 중복 기입 발생. copy_slots 를 **variant-aware optional** 로 완화 검토.

### P2 — 매트릭스 잔여 아키타입
- **A3(Event)** · **A5(Mobile App)** 아키타입 미산출. 잔여 variant(매트릭스 참조). 블루프린트 `docs/architecture/landing-pattern-matrix.md`.

### P3 — 콘텐츠/마무리 (실고객 전 보류)
- carousel 전용 목업(business-system 데모 auth-gated 라 dashboard 캡처 불가).
- 연락폼 demo-stub → 실엔드포인트(실고객 시).
- 스탯 강조를 manifest `highlight:true` 플래그로(현재 "0 으로 시작" 휴리스틱 대체, Growth-74).

### (이전 트랙, 종결됨 — 참조용)
- 파이프라인 모니터(Growth-62~64): 외부 모니터 LIVE `pipeline.n9n.co.kr`(CF Access, 부팅자동), Supabase L4 10/10 PASS, Capacitor 8 정렬 — 모두 완료. 상세는 메모리 [[todo-external-pipeline-monitor]] + `docs/runbooks/external-pipeline-monitor.md`.

---

## business-system 데모 (Growth-57, 참조용 — 마케팅 트랙과 별개)

| URL | 업종 | slug | Coolify UUID |
|---|---|---|---|
| demo.n9n.co.kr | 데모 포털 | demo-portal | `s6872cr0asfp02sc0vgw8wi2` |
| logistics-demo.n9n.co.kr | 물류·운송 | logistics | `hmb6jp67w6stmhsdi6e4h73o` |
| distribution-demo.n9n.co.kr | 도매·유통 | distribution | `gufoc3trwh2umw53k93bjdyp` |
| construction-demo.n9n.co.kr | 건설·시공 | construction | `l3dyahzqjssm4l15tjpc75cj` |
| itservice-demo.n9n.co.kr | IT서비스 | itservice | `iguqvhla1cnhhjm14f3xgi2h` |
| trading-demo.n9n.co.kr | 무역·수출입 | trading | `ybawqjqryxst5ofwnekaxpak` |
| manufacturing-demo.n9n.co.kr | 제조업 | manufacturing | `ufbllprbzrg8pktn9yfhsybq` |
| edu-program.n9n.co.kr | 교육기관 | edu-program | `tp0608w5b013sypb4euwplld` |

로그인 `demo`/`demo`. 백엔드 `InMemoryEntityStore`(PostgreSQL 없음, `SEED_FILE` env). server uuid `n12vdydjpwp81hu5i15n1gsb`.

---

## 최신 git (master)

```
<this-commit> log(growth-81): A1 FLUX LIVE 배포 종결 (devops/learn-log/HANDOFF)  ← HEAD
35863bd feat(portal): add FLUX (A1 SaaS) demo card — 6th marketing demo
4b19b1b chore(registry): flux digital-asset record — A1 marketing demo LIVE
28026ce build(preview): flux.compose.yml — A1 FLUX marketing-site deploy unit
55777ce test(site-manifest): A1 stats type -> 14 section types (was stale 13)
2836594 log(growth-80): A1 FLUX 인프라SaaS 빌드 + flux 테마 + 섹션3종, ui_check 7/7 PASS
```
HEAD = origin/master(push 완료). flux.compose/registry/portal/test 커밋은 push 됨, ledger 커밋이 이번 마무리.

### 미커밋 / untracked (의도적 보류)
- `M .claude/settings.json` — 로컬 하네스 설정(worktree override 포함, 커밋 보류).
- `?? design/reference/21st/2.ModernAnimatedHeroSection.txt` `?? 3.GlassmorphismTrustHero.txt` — 21st.dev 참조 자료(디자인 인풋, 커밋 보류).

---

## 다음 세션 시작 체크리스트

1. **풀테스트**: `PYTHONUTF8=1 python -m pytest scripts/workflow/tests -q` + `PYTHONUTF8=1 python scripts/diagnose.py`(0 FAIL 기대).
2. **landing-astro 빌드 확인**: `cd frontend/adapters/landing-astro && npm run build`(BUILD SUCCESS).
3. **FLUX 로컬 확인**: ui_check 또는 webapp-testing 으로 flux-demo manifest 렌더 점검(7/7 PASS 기대).
4. 파운더 지시에 따라 오픈 루프 선택 — 기본 다음 수: **P0(FLUX LIVE 배포)** → P1/P2.
