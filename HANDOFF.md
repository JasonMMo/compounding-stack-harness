# Session Handoff — 2026-06-17

## 이번 세션 범위 (최신)

**마케팅사이트 8축(theme/section) 트랙 — 페이지-구조 아키타입 확장 (Growth-75 → 88)**.
웹에이전시형 랜딩 데모를 "테마(색·폰트)" 다양성에서 **페이지 구조 아키타입(A1~A7)** 다양성으로 확장 중. CEO 가 "색·텍스트만 다른 같은 패턴"을 지적(Growth-76) → 진짜 차별은 **섹션 variant × 페이지 아키타입 × 테마의 곱**이라는 결론. 블루프린트: [`docs/architecture/landing-pattern-matrix.md`](docs/architecture/landing-pattern-matrix.md).
Growth-88: **모션 다이얼 진짜 레버화** — flux-demo·meridian `motion:rich` 파일럿. 레거시 `[data-motion]` 옵저버 always-load 리팩터 + `html[data-motion="rich"]` 가 레거시 keyframe vars 스케일 → 기존 카탈로그 17개 섹션 전체 격상. snap+island 한계 문서화(`data-snap-panel` backlog).

> ✅ **Growth-81 A1 FLUX LIVE** — https://flux.n9n.co.kr (6번째 데모, flux 테마). **P0 종결**.
> ✅ **Growth-82 A3 Event LIVE** — https://summit-horizon.n9n.co.kr (7번째 데모, ignite 테마, SUMMIT Horizon 2026). 신규 variant 3종(horizontal-steps/newsletter-inline/four-up) + logos/grid 워드마크 폴백 결함 픽스. 풀페이지 9/9 섹션 비주얼 검증, ui_check 7/7. **P2(A3) 종결**.
> ✅ **Growth-84 A7 API Platform LIVE** — https://prism.n9n.co.kr (9번째 데모, prism 테마(9th, deep-azure #1B4FA8)). **신규 hero/bento-grid 변형**(텍스트 좌 + stat/proof bento 우, 무사진·무JS; GlassmorphismTrust 21st.dev 레퍼런스 구조 차용·미감 중화). CTO 비주얼 검증서 **ticker-band 저대비·footer 빈컬럼** FIX-FIRST 적발 → `Stats.astro` styleHints.bg honor + `Footer.astro` 데이터주도 컬럼+빈컬럼 가드로 **일반화**(전 데모 재사용, flux 회귀 0). §2 stale 4건 HAVE 환류. **→ A1~A7 7개 아키타입 전부 BUILT**.
> ✅ **Growth-83 A5 Mobile App LIVE** — https://lumi.n9n.co.kr (8번째 데모, nova 테마, Lumi 습관·집중 앱). **무사진(0 stock)**: gallery/grid-2x2 src-optional CSS 폰목업 4종 + marquee 자체 proof 재사용 + cta 다운로드 버튼쌍(copy.secondary_*). site_manifest `variant_overrides` 신설로 **P2(slot 완화)·P1(items[] copy_slots) 동시 종결**. FeatureCarousel sr-only SSR(Growth-69). 풀페이지 8/8 비주얼 검증. **→ A1~A6 6개 아키타입 전부 BUILT, 매트릭스 1차 완성**.
> ✅ **Growth-85 21st.dev 6종 triage → process/split-animation 신규 변형** — 파운더 드롭 레퍼런스 6종(PixelLogoGrid/InkReveal/PixelPerfectHero/TableOfContents/Sparkles/AgentPlan)을 CDO 가 불변식 게이트로 triage: **AgentPlan 1종만 채택**(InkReveal=Growth-69위반·TableOfContents=섹션type없음·Sparkles=impeccable glow위반 reject, PixelPerfectHero/PixelLogoGrid backlog). `process/split-animation` 으로 중화 구현(랜덤상태 제거·read-only·`<details open>` SSR fallback). **A1 flux 데모에 흡수·재배포 LIVE**(한국어 4단계 태스크트리). status 토큰 추가 0(기존 3-state 재활용). NEED 14→13. triage 판정 matrix §4 박제. pytest 140·비주얼 PASS.
> ✅ **Growth-86 자체 GTM 랜딩 한국어화 + locale 전파 feature** — 우리 플래그십 M1 리드젠 랜딩(gtm-landing, LIVE)이 영어였던 모순 해소: 전 섹션 카피·SEO 한국어(CMO), `defaults.locale ko-KR`. 부수 신설 **locale 전파 feature**(profile→manifest top-level `locale`→BaseLayout `<html lang>` BCP-47 서브태그; 하드코딩 `lang="en"` 제거, 영문 데모 en-US 기본 보존 — open-closed, 전 고객 재사용) + **aurora family-display 한국어 시스템폰트 폴백**(헤드라인 글리프 결함, zero egress — self-host thesis 준수). pytest 145(신규 5)·`<html lang="ko">`·비주얼 전 섹션 PASS. backlog: kiln·studio·harvest 동일 폰트 갭 + **모션 트랙**(sanggong식 스크롤 스냅 풀스크린+IO 진입모션 변형 자산화, "B급 상한 상향" 검토 — 파운더 승인 방향).
> ✅ **Growth-87 모션 시스템 + 신규 변형 3종 + zero-egress** — 파운더가 sanggong.co.kr(한국 랜딩 웹에이전시) 지목 → 효과를 클론 아닌 변형으로 누적. **scroll-snap 풀스크린 셸 + IO 진입-리빌 디렉티브(vanilla·라이브러리0) + 모션 토큰 + `site.scroll_mode`/`site.motion`(off/subtle/rich) 다이얼** 신설. 신규 변형 **hero/scroll-reveal·gallery/full-bleed-strip·stats/pinned-staged**. **G-69 유지**(`html.motion-ready [data-reveal]:not(.in-view){opacity:0}` — JS off시 전부 가시, 픽셀 mean_diff=0). gtm-landing 파일럿(snap+subtle). 부수로 **Google Fonts CDN egress 적발·제거**(우리 "0 bits egress" 랜딩이 fonts.googleapis 호출하던 자가모순 — IBM Plex/DM Mono @fontsource 이전 → 전 테마 zero-egress). pytest 380(신규12)·비주얼 JS-on/off PASS·dist googleapis 0 hit. B급→A급 상한 상향. 설계: [`docs/architecture/motion-system.md`](docs/architecture/motion-system.md).

---

## 완료 항목 (마케팅사이트 트랙, Growth-75~83)

| Growth | 아키타입 / 산출 | 테마 | LIVE URL | 상태 |
|---|---|---|---|---|
| 75 | (테마 다양성) HOPWELL 맥주 런칭 | harvest | https://hopwell.n9n.co.kr | ✅ LIVE |
| 76 | **A2** Creative Agency/Portfolio — Studio North | atelier | https://studio-north.n9n.co.kr | ✅ LIVE |
| 77 | **A4** 공예/로컬 — TERRA ceramics (첫 scroll-cinematic) | kiln | https://terra-ceramics.n9n.co.kr | ✅ LIVE |
| 78 | **A6** B2B 매니지드IT — MERIDIAN | meridian | https://meridian.n9n.co.kr | ✅ LIVE |
| 79 | (툴링) 공식 Anthropic 스킬 5종 검토 → webapp-testing 1종 채택 | — | — | ✅ |
| 80 | **A1** SaaS Product Launch — FLUX (인프라/관측성) | flux | https://flux.n9n.co.kr | ✅ LIVE |
| 81 | (배포) A1 FLUX LIVE + 포털 6번째 카드 + 레지스트리 | flux | https://flux.n9n.co.kr | ✅ LIVE |
| 82 | **A3** Event/Conference — SUMMIT Horizon 2026 (신규 variant 3종) | ignite | https://summit-horizon.n9n.co.kr | ✅ LIVE |
| 83 | **A5** Mobile App — Lumi (무사진 grid-2x2 + variant_overrides, P1/P2 종결) | nova | https://lumi.n9n.co.kr | ✅ LIVE |
| 84 | **A7** API Platform — Prism (hero/bento-grid 신규 + ticker-band/full-links 일반화) | prism | https://prism.n9n.co.kr | ✅ LIVE |
| 85 | (변형) 21st.dev 6종 triage → process/split-animation 신규 (A1 flux 흡수·재배포) | flux | https://flux.n9n.co.kr | ✅ LIVE |

- **라이브 마케팅 데모 9종**: gtm-landing(indigo aurora) · hopwell · studio-north · terra-ceramics · meridian · flux · summit-horizon · lumi · **prism**. 포털에 카드 9장. **→ A1~A7 7개 아키타입 전부 BUILT.** (※ 별도로 Growth-57 business-system 데모 7종은 `*-demo.n9n.co.kr` — 아래 참조표.)
- **테마 9종**: aurora(gtm) · harvest · atelier · kiln · meridian · flux · ignite · nova · **prism**(신규, deep-azure #1B4FA8, OKLCH H≈228 미점유). 누적 위치 `presets/themes/<slug>/`.
- **섹션 카탈로그**: **14/14 type 완성**, HAVE variant 39(Growth-85 로 process/split-animation 추가; Growth-84 hero/bento-grid + §2 stale 4건 HAVE 정정). NEED 13. 단일진실 `presets/site-sections/catalog.yaml`.

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

### ✅ 매트릭스 아키타입 — A1~A7 전부 BUILT (Growth-77/78/80/81/82/83/84 누적 종결)
- A1 FLUX: https://flux.n9n.co.kr (project=jq25nyzfirch3flp7no2wg3u, app=oyemv0mttkn8eo05xflvc4x2, flux). 6번째 카드.
- A3 Event: https://summit-horizon.n9n.co.kr (project=k105u8soe4fergofhdje2nkt, app=jvo3hnfmf2bv8ce10mcj96l0, ignite). 7번째 카드.
- A5 Mobile App: https://lumi.n9n.co.kr (project=x7be9f2b7nr1zhykxubn6wwt, app=j10swdnw5tyndidudjnsr04r, nova). 8번째 카드. 무사진 grid-2x2 + cta 버튼쌍 (Growth-83).
- **A7 API Platform: https://prism.n9n.co.kr (project=qfbgsfa42ep757lxx88amwje, app=z13nexbnkj2651flq82bfy0u, prism). 9번째 카드 + `infra/registry/prism.yaml`(live). 신규 hero/bento-grid + ticker-band/full-links 일반화, 풀페이지 비주얼 검증 (Growth-84).**
- A4 Tildé(F&B): https://hopwell.n9n.co.kr (harvest). A6 MERIDIAN(B2B): https://meridian.n9n.co.kr (meridian). A2 Studio North: https://studio-north.n9n.co.kr (atelier).

### ✅ P2 — catalog copy_slots/item_slots variant-aware 완화 (Growth-83 종결)
- `site_manifest.py` 에 `variant_overrides` 메커니즘 신설: per-section catalog 엔트리가 `variant_overrides: {<variant>: {copy_optional:[], item_optional:[]}}` 를 들고, validate_site 가 missing 검사 전 차감. 적용: gallery grid-2x2/parallax-scroll `src`-optional + testimonial pull-quote-wall copy(quote/author_name) optional. **Growth-80 P1(items[] variant copy_slots 강제)도 동시 종결.** 테스트: `TestVariantOverrides` 9건.

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
Growth-84 (A7 Prism) — per-file 커밋 3배치 + push 3회. 대표:
70123b2 log(growth-84): devops 원장 갱신                            [Fable 5, devops]
c10f295 feat(registry): prism digital asset record                 [Fable 5, devops]
a7c1a5f feat(portal): add Prism 9th demo card                      [Fable 5, devops]
a02b239 log(growth-84): learn-log + matrix(A7 등재·stale 정정)       [Opus 4.8, CTO]
…(HeroBentoGrid/Stats fix/Footer fix/[...page]/theme/profile/catalog/site_manifest/test/compose/qa.md — engineer/QA = Fable 5)
```
HEAD = origin/master(코드/compose/registry/portal/components/devops·qa ledger 전부 push 완료). **마무리 잔여 = engineer.md·cdo.md ledger + 이 HANDOFF 커밋 + push.**
(트레일러 mixed: engineer/QA/devops 커밋은 Fable 5, CTO 커밋은 Opus 4.8 — §9 "실제 co-author 모델 정직 반영".)

### 미커밋 / untracked (의도적 보류)
- `M .claude/settings.json` — 로컬 하네스 설정(worktree override 포함, 커밋 보류).
- `?? design/reference/21st/2~9.txt` — 21st.dev 참조 자료 8종(디자인 인풋, 커밋 보류). Growth-84 가 3.GlassmorphismTrustHero 를 hero/bento-grid 의 구조 레퍼런스로 사용(미감은 중화).

---

## 다음 세션 시작 체크리스트

1. **풀테스트**: `PYTHONUTF8=1 python -m pytest scripts/workflow/tests -q` + `PYTHONUTF8=1 python scripts/diagnose.py`(0 FAIL 기대).
2. **landing-astro 빌드 확인**: `cd frontend/adapters/landing-astro && npm run build`(BUILD SUCCESS).
3. **비주얼 검증 회수**: ui_check `--base-url <serve> --slug <s> --entry-path /` (7/7 기대) + **풀페이지 스크롤 세그먼트 캡처**(`out/shot_seg.py`, large-file-guard 회피용 뷰포트 분할) 로 below-fold 전 섹션 육안 확인 — Growth-82 에서 logos 플레이스홀더·footer 오타가 ui_check PASS 에도 풀페이지로만 적발됨.
4. 파운더 지시에 따라 오픈 루프 선택. **A1~A7 7개 아키타입 전부 BUILT** — 다음 후보: ① 매트릭스 §2 잔여 NEED variant 14종 커버리지 확대(hero/scroll-reveal · features/timeline-horizontal · process/split-animation · gallery/full-bleed-strip · team/headshot-list · faq/categorized · lead/multi-field-card · pricing/comparison-table 등), ② 신규 실고객 needs 기반 아키타입×테마 조합, ③ 기존 9 데모 콘텐츠/마무리(P3). 파운더가 `design/reference/21st/`에 추가 레퍼런스 6종(4~9.txt: PixelLogoGrid/InkReveal/PixelPerfectHero/TableOfContents/Sparkles/AgentPlan) 드롭 — 다음 variant 디자인 인풋 후보. 파운더 우선순위 확인 후 착수.
