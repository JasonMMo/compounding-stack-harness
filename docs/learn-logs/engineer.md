# learn-log — Engineer

> Implementation hand. CTO 가 결정한 설계를 코드로 옮기는 인격의 ledger.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 인격 헌장: [`.claude/agents/engineer-agent.md`](../../.claude/agents/engineer-agent.md).

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Files touched: <경로 list>
- Implementation choices: <변수명·구조·error handling 등 인격 단독 결정>
- Tests added: <4계층 중 어느 layer>
- Catches surfaced: <CTO/QA 에 던진 escalation 신호>
- Cost: <turns / 추정 $>
```

## §2 — Growth History


> **회전**: Growth-5d ~ Growth-70 → [`archive/engineer-01.md`](archive/engineer-01.md) (2026-07-05, Growth-144. 규약: `README.md`)

### Growth-71 (2026-06-15) — impeccable 디자인 SKILL vendoring + 네트워크 감사

- **작업**: `pbakaus/impeccable` shallow-clone → `.claude/skills/impeccable/` 코어만 복사(93파일 ~2.1MB, SHA fff712c v3.6.0). LICENSE + NOTICE.vendored.md 동봉. 13개 AI툴 중복·site/tests/cli 제외.
- **감사(핵심)**: telemetry/posthog/OpenAI API 없음, 전 파일 ASCII(G-8). 단 `scripts/context.mjs:161` 이 `fetch(impeccable.style/api/version)` 으로 **매 세션 업데이트 폴링(NETWORK)** → no-network 위반. live-mode·detector fetch 는 localhost 한정(무해). 중화: `.impeccable/config.json {updateCheck:false}`(context.mjs 가 config/env 둘 다 인식, 커밋되어 영구).
- **교훈**: 서드파티 vendoring 절차 = ① 코어만 추출(중복 패키징 제외) ② LICENSE+NOTICE+SHA 핀 ③ **fetch/http/api/telemetry/openai/spawn grep 감사** ④ 네트워크 옵트아웃을 커밋(env 아닌 config 파일로 영구) ⑤ ASCII(G-8) 확인. 대용량 browser JS(live-browser 432KB 등)는 size 무관 커밋(읽기만 100KB 가드 대상).
- **Cost**: engineer subagent 1회(39K tok) / envelope.

### Growth-72 (2026-06-15) — typeset de-slop (gtm-landing)

- **작업**: impeccable `/typeset` 실행. ① hero `bg-clip-text` 그래디언트 제거 → 솔리드 `#C4B5FD` accent + weight. ② 폰트 4종(plus-jakarta/inter/dm-serif-display/dm-sans, 전부 reflex-reject) 제거 → `@fontsource-variable/bricolage-grotesque` + `@fontsource-variable/epilogue`(MIT, self-host, Korean fallback). global.css 9 import→2, aurora theme.yaml font 토큰 갱신.
- **검증**: build SUCCESS, detector gradient-text **제거**(em-dash 잔존, 별도 패스), 라이브 computed font=Bricolage/Epilogue 확인, no-JS h1 opacity 1.
- **교훈**: @fontsource 기본 폰트가 impeccable reflex-reject 와 다수 겹침 — 신규 어댑터 폰트 선택 시 reflex 목록 대조 필요. theme.yaml font 토큰이 단일진실이라 1곳 수정으로 전 consumer 반영.
- **Cost**: engineer subagent 1회(52K tok) / envelope.

### Growth-73 (2026-06-15) — critique 백로그 3패스(quieter+clarify+polish)

- **quieter**: HeroGlowyWaves 웨이브 opacity 0.45→0.22 등 ~절반, 진폭 70→50px, shadowBlur 35→14, radial blob 520→380px/alpha 0.35→0.15. canvas/폰트/accent 불변.
- **clarify**: gtm-landing.yaml body 카피 em-dash 9→0(콜론/괄호/마침표). detector CLEAN.
- **polish**: carousel feature image → non-login richer(edu-program/gtm-landing/construction). 한계: auth-gated 라 dashboard 캡처 불가, 공개 캡처 중 richest.
- **검증**: 단일 빌드 SUCCESS, detector `[]` CLEAN, no-JS h1 opacity 1. 무충돌 다건은 1빌드·1배포 배치가 효율.
- **Cost**: engineer subagent 1회(56K tok) / envelope.

### Growth-74 (2026-06-15) — /colorize accent-warm 토큰 + 3곳 적용

- `accent-warm`(#AB5527) 토큰을 aurora theme.yaml 에 추가 → build-tokens.mjs 가 `--color-accent-warm` 방출(.gen.css/.gen.js 재생성, gitignored). 적용: HeroGlowyWaves 스탯값 조건부 색, FeatureCarousel 활성 dot, Faq.astro `group-open:`. 하드코딩 hex 없이 var() 참조.
- **검증**: build SUCCESS, detector CLEAN, contrast AA(5.17/3.09:1), 라이브 "0 bits"=rgb(171,85,39).
- **caveat**: 스탯 강조가 "0 으로 시작" 휴리스틱 — gtm-landing 엔 정확하나 재사용성 위해 manifest `highlight:true` 플래그가 더 견고(open loop).
- **Cost**: engineer subagent 1회(86K tok) / envelope.

### Growth-75 (2026-06-15) — 어댑터 멀티테마 픽스 + harvest 섹션

- **theme-aware 빌드(핵심)**: `npm run build`가 `build-tokens.mjs aurora` 하드코딩 → harvest 프로파일도 aurora 토큰으로 빌드돼 carousel/FAQ가 indigo. 신규 `scripts/build-tokens-auto.mjs`(PUBLIC_SITE_MANIFEST 의 `.theme` 읽어 build-tokens 호출, fallback aurora)로 교체. Dockerfile 무변경(이미 PUBLIC_SITE_MANIFEST 설정). 전 미래 테마의 전제조건.
- **harvest 섹션/픽스**: `HeroBrewBubbles.astro`(grain SVG noise + CSS 탄산 버블, no canvas, no-JS 가시), carousel 색 토큰화(harvest amber/aurora indigo 양립)+크래프트 아이콘(wheat/leaf/droplets)+레이아웃, FAQ 셰브론 명시 20px, BaseLayout 모션 reveal 견고화(threshold 0+rootMargin 200px+800ms fallback).
- **교훈**: build green·detector CLEAN ≠ 비주얼 정상 — 풀페이지 스샷이 토큰 클로버·거대 셰브론·below-fold blank 3차 적발. 멀티테마는 빌드 파이프라인의 테마 가정을 의심.
- **Cost**: engineer subagent 3회(67+67+103K tok) / envelope.

### Growth-76 (2026-06-15) — 신규 섹션 type 2종(gallery·story) + hero variant + 라우팅

- **신규 섹션 type**: `gallery`(item_slots src/alt+caption/href, variants masonry-3col/full-bleed-strip/grid-2x2) + `story`(copy_slots headline+body/pull_quote/..., variants founder-split/timeline-year) → `presets/site-sections/catalog.yaml`(8→10 type, additive). hero.variants에 `headline-only` 추가.
- **컴포넌트**: `HeroHeadlineOnly.astro`(no-JS opacity 1), `Gallery.astro`(masonry-3col + copper hover overlay, gallery-overlay 토큰 + 비-atelier CSS fallback), `Story.astro`(founder-split, 다단락 body \n\n 분리). `[...page].astro`에 import+라우팅 추가(open-closed, 기존 무변경).
- **스레딩**: `manifest.ts`의 `Section.items`가 이미 `Array<Record<string,unknown>>`이라 gallery items 무변경 통과. `site_manifest.py` items 경로 재사용 → Python 무변경. 테스트 `test_eight_section_types` equality→subset(additive). 42/42 PASS.
- **교훈**: ① 카탈로그 확장은 equality 검사를 subset로 바꿔 additive 보장. ② 신규 섹션이 기존 items 스레딩을 재사용하면 Python/contract 무변경(open-closed 설계의 배당). ③ theme-specific 토큰(gallery-overlay)은 CSS fallback으로 비-해당 테마 호환.
- **Cost**: engineer/CDO 통합 백그라운드 agent 1회(~126K tok) / envelope.

### Growth-77 (2026-06-16) — GalleryParallaxScroll + Lead + timeline-year + hooks/SSR 버그 2종 수정

- Files touched:
  - `frontend/adapters/landing-astro/src/sections/GalleryParallaxScroll.tsx` (신규 — React island, framer-motion useScroll, sticky chapters, `texture:` sentinel)
  - `frontend/adapters/landing-astro/src/sections/Lead.astro` (신규 — minimal-field email input, `entity.create` 재사용)
  - `frontend/adapters/landing-astro/src/pages/[...page].astro` (수정 — gallery/parallax-scroll·lead/minimal-field·story/timeline-year 라우팅 추가)
  - `frontend/adapters/landing-astro/src/sections/Story.astro` (수정 — timeline-year variant: year/milestone/detail item_slots 스레딩)
  - `presets/site-sections/catalog.yaml` (수정 — gallery/parallax-scroll variant 추가·story/timeline-year item_slots·lead/minimal-field 신규 type, 11→13 type)
  - `presets/themes/kiln/` (신규 테마 디렉터리 — theme.yaml + texture token CSS)
  - `profiles/terra-ceramics.yaml` (신규 — A4 customer profile)
  - `deploy/preview/terra-ceramics.compose.yml` (신규)
  - `infra/registry/terra-ceramics.yaml` (신규 — coolify project=itw5euifm5shu8vt84axxz8p, app=q9hq2xlr3cjzh47smq7z0xe8)

- Implementation choices:
  - **GalleryParallaxScroll.tsx**: `useScroll({target: containerRef})` 로 스크롤 진행도 추적. 각 챕터: `useTransform(scrollYProgress, [start, end], values)` 로 scale + overlay opacity 독립 계산. heading/subheading은 parallax offset track (시차). chapters 배열 길이가 동적이어도 고정 순서로 훅 호출(rules-of-hooks 준수를 위해 챕터당 훅 배열 선언 방식 채택).
  - **rules-of-hooks 버그 수정**: 최초 구현에서 `reducedMotion` 조건부로 `useTransform` 호출 → React hooks-must-not-be-conditional 위반. 수정: `useTransform` 는 unconditional 선언, 반환값 사용 시 `reducedMotion` 분기로 value-branch. 훅 순서 불변 보장.
  - **Growth-69 SSR opacity 버그 수정**: framer-motion이 `initial={{opacity:0}}`를 SSR HTML에 baked → `initial={false}` + JS 없는 환경에서 opacity:1 보장하는 conditional style application. 5/5 no-JS 콘텐츠 체크 PASS.
  - **texture: sentinel**: `src` 값이 `texture:clay|ash|ember` 이면 실 이미지 `<img>` 대신 CSS gradient+grain div 렌더(테마 material-texture field). 실 고객은 `src: /path/to/photo.jpg` 입력, 데모는 sentinel로 사진 0 운영.
  - **Lead.astro**: `entity.create`(entity_type=lead) 재사용 — wire key 신규 추가 없음(G-1, open-closed). email single field, `PUBLIC_DEMO_MODE` 분기로 demo stub.
  - **story/timeline-year**: `Story.astro` 에 variant 분기 추가. items[]{year, milestone, detail} → vertical timeline 렌더. founder-split variant 무변경(additive).
  - **catalog additive**: `test_eight_section_types` equality→subset 패턴 유지. Python/contract 무변경 — items 스레딩 재사용.

- Tests added:
  - **L1 pytest**: 71 PASS (0 regression). site_manifest·adapter 기존 케이스 전부 green.
  - **L3**: `npm run build` BUILD SUCCESS.
  - **no-JS**: 5/5 콘텐츠 체크 PASS (opacity:1 SSR 확인).
  - **impeccable detector**: CLEAN.
  - **visual**: desktop+mobile+no-JS 풀페이지 PASS (mobile scrollWidth−clientWidth=0px, 3 chapter headings, hero, lead 콘텐츠 확인).

- Catches surfaced:
  - rules-of-hooks 위반 — conditional `useTransform` 초기 구현 → unconditional + value-branch 로 자체 수정(CTO 에스컬레이션 없음).
  - Growth-69 SSR 함정 재발 — GalleryParallaxScroll initial opacity:0 SSR bake → `initial={false}` 로 수정. 동일 계열 2번째 발견.

- Cost: engineer subagent 다회 / envelope 반환.

### Growth-78 (2026-06-16) — Process + Team + Logos quote-band (A6 B2B 섹션 3종, 전부 Astro-native)

- Files touched:
  - `frontend/adapters/landing-astro/src/sections/Process.astro` (신규 — process/numbered-stack: bold display 넘버럴 left-rail + title/description, ghost 카드, thin divider, 위치 기반 넘버링·step_label override)
  - `frontend/adapters/landing-astro/src/sections/Team.astro` (신규 — team/headshot-grid: 반응형 avatar 그리드, **monogram-initials 폴백** — photo 없으면 forest-green 원에 이니셜 흰 글씨, 사진 0)
  - `frontend/adapters/landing-astro/src/sections/Logos.astro` (수정 — quote-band variant: 다크 밴드 단일 고객 인용+author 어트리뷰션, copy.quote/author_name/author_title/company, 기존 horizontal-scroll·grid 분기 무변경)
  - `frontend/adapters/landing-astro/src/pages/[...page].astro` (수정 — process·team section type 라우팅 추가; logos quote-band 는 기존 Logos 경로 재사용)
  - `frontend/adapters/landing-astro/package.json`·`package-lock.json`·`src/styles/global.css` (수정 — @fontsource-variable/syne + dm-sans 추가·import)
- Implementation choices:
  - **전부 Astro-native(React 아일랜드 0)**: quote-band/numbered-stack/headshot-grid 모두 정적 렌더, JS 는 IntersectionObserver entrance 모션만. Growth-77 parallax 와 대조 — A6 는 scroll-cinematic 불필요, 무JS 완전 렌더가 B2B 신뢰 레지스터에 더 적합.
  - **monogram 폴백**: `item.photo` 부재 시 이니셜(이름 첫 두 단어 첫 글자) forest-green 원 흰 글씨 — 조작된 stock face 0, asset-free 패턴(parallax texture: sentinel 과 동일 철학).
  - **numbered-stack 넘버링 합법성**: process 는 진짜 순차(impeccable — 순서가 정보를 담는 경우 넘버 허용). eyebrow-reflex 아님.
- Tests/verify: npm install(syne+dm-sans 2 pkg), scaffold → out/meridian/site-manifest.json(process·team·quote-band·contact.enabled), theme-aware build SUCCESS(tokens.gen.css --color-primary #1A5C3A — aurora purple 아님), impeccable detector CLEAN([]), desktop+mobile+no-JS 풀페이지 PASS(Growth-69 — motion-hidden 은 런타임 JS 만 추가, SSR HTML 미포함).
- Catches surfaced: Playwright `fullPage:true` 가 뷰포트 스크롤 안 해 IntersectionObserver 미발화 → 중간 섹션 blank 캡처. screenshot 스크립트에 scroll_and_wait() 추가로 해소(컴포넌트 결함 아님).
- Cost: engineer subagent 1회 / envelope 반환.

### Growth-84 (2026-06-16) — A7 API Platform: hero/bento-grid + prism 테마 + FIX-A/B 2종

- Files touched:
  - `frontend/adapters/landing-astro/src/sections/HeroBentoGrid.astro` (신규 — hero/bento-grid 변형: 7/5 grid desktop / single-col mobile, stat 카드(monogram badge·대형 mono stat·progress bar·mini-stats 3-col·status tag pills) + marquee 카드(정적 DOM 전체 회사명 + CSS keyframe @prefers-reduced-motion 가드), 전부 semantic token var(--color-*), opacity:0 없음)
  - `frontend/adapters/landing-astro/src/pages/[...page].astro` (수정 — HeroBentoGrid import + `variant==='bento-grid'` 분기, Footer items passthrough 추가)
  - `frontend/adapters/landing-astro/src/styles/global.css` (수정 — IBM Plex Sans + DM Sans + DM Mono Google Fonts `@import url()` 추가; npm 패키지 무추가)
  - `frontend/adapters/landing-astro/src/sections/Stats.astro` (수정 — FIX-A: ticker-band `tickerIsLight` 분기 — `styleHints.bg` surface-*/light → 라이트 밴드(surface-2 배경·primary 숫자·text-2 라벨); 그 외 → 기존 다크 밴드(hero-bg-from·primary-border·surface-3) — flux 회귀 0)
  - `frontend/adapters/landing-astro/src/sections/Footer.astro` (수정 — FIX-B: full-links `items?: FooterColumn[]` prop 추가, 데이터 주도 컬럼 렌더; 빈 컬럼 가드(`links.length > 0` 필터); items 없으면 하드코딩 fallback(contactHref 없으면 Support 컬럼 자동 제거 — 기존 empty-col 버그 동시 수정))
  - `presets/themes/prism/theme.yaml` (신규 — 9번째 테마; deep-azure #1B4FA8, IBM Plex Sans + DM Sans + DM Mono, bento-card-bg/border/status 전용 토큰, nova 형식 100% 일치)
  - `presets/themes/prism/README.md` (신규 — nova 디렉터리 컨벤션 동형)
  - `presets/site-sections/catalog.yaml` (수정 — hero.variants에 bento-grid 추가, hero item_slots + variant_overrides 신설; footer item_slots + variant_overrides(minimal/newsletter make items optional))
  - `scripts/workflow/site_manifest.py` (수정 — bento_items + cta_secondary passthrough 추가)
  - `profiles/prism-demo.yaml` (신규 — A7 9-섹션 구성, CDO spec §5 카피 전문, footer 3-컬럼 실데이터)
  - `deploy/preview/prism.compose.yml` (신규 — lumi.compose.yml 미러, PROFILE_SLUG=prism-demo)
  - `scripts/workflow/tests/test_site_manifest.py` (수정 — TestHeroBentoGrid 12케이스 추가; 115→127 passed)
- Implementation choices:
  - **Google Fonts `@import url()` (no npm pkg)**: CDO spec 이 fontsource 를 언급했으나 CTO 지시(lockfile churn 회피) + 기존 global.css 패턴 우선. 차이점을 spec 이탈이 아닌 허용 범위 내 선택으로 처리.
  - **marquee 정적 DOM 전략**: 회사명 2-copy(`aria-hidden` 두 번째 복사) 를 SSR DOM 에 전부 출력 후 `@media (prefers-reduced-motion: no-preference)` 로만 CSS scroll 활성. JS 없이 모든 이름 가시 — Growth-69 완전 준수.
  - **`tickerIsLight` Set 분기**: `new Set(['surface-1','surface-2','surface-3','light'])` — 신규 라이트 키가 생겨도 Set 확장만 하면 됨. `bg: dark` 미설정 → 다크 디폴트로 flux 하드코딩 그대로 유지.
  - **Footer `profileColumns` 필터**: `items.filter(col => col.links?.length > 0)` — 헤더만 있는 컬럼 선렌더 금지. profileColumns 없으면 defaultColumns(contactHref 조건부 Support) 로 fallback — 기존 고객 profiles 무변경.
- Tests/verify: scaffold → out/prism-demo/site-manifest.json CLEAN (위반 0). Astro build `[build-tokens-auto] resolved theme "prism"` 로그 확인. dist/index.html SSR 콘텐츠 21/21 PASS (headline·stat·marquee 6개 회사명·CTA pair·9섹션 copy 전부). FIX-A 15/15 PASS (prism light bg + flux dark 회귀 없음). test_site_manifest 127 passed.
- Catches surfaced: 없음(FIX-A/B 는 CTO 비주얼 검증에서 발견해 engineer 가 해소 — 아키텍처 결함 아닌 다크-전용 공유 컴포넌트 첫 라이트 테마 노출 유형).
- 교훈: 라이트 테마가 다크-전용 하드코딩 공유 컴포넌트를 처음 밟으면 색 하드코딩을 styleHints honor 로 일반화(Cta.astro FIX-선례 동형). 한 컴포넌트를 고치면 이후 모든 테마가 혜택을 받는 compounding 구조.
- Cost: engineer subagent 1회(FIX-A/B 포함) / envelope 반환.

### Growth-85 (2026-06-16) — process/split-animation: CDO 중화 구현 (21st.dev AgentPlan 레퍼런스)

- Files touched:
  - `presets/site-sections/catalog.yaml` (수정 — process.item_slots.optional에 status/subtasks/tools 추가; split-animation variant_overrides 신설; SSR fallback·접근성·토큰 규약 주석 포함)
  - `frontend/adapters/landing-astro/src/sections/ProcessSplitAnimation.astro` (신규 — 2-column split layout: 1fr 2fr grid desktop / single-col mobile; `<details open>` SSR fallback Growth-69 준수; 3-state status icon(check-circle/circle-dot/circle) + aria-label 접근성; Astro scoped `<style>` 블록; 기존 테마 토큰 전용 — 새 토큰 추가 없음; 마케팅 read-only: Math.random/toggleTaskStatus 제거)
  - `frontend/adapters/landing-astro/src/pages/[...page].astro` (수정 — ProcessSplitAnimation import + `variant==='split-animation'` 분기; 기존 Process 분기 보존)
  - `profiles/flux-demo.yaml` (수정 — process/numbered-stack → split-animation 교체; 4단계 태스크 트리 한국어 copy; 소스 연결(completed)→SLO 정의(active)→비용 계측(upcoming)→배포 게이트(upcoming); tools[] 다수 포함)
  - `scripts/workflow/tests/test_site_manifest.py` (수정 — TestProcessSplitAnimation 클래스 신설 8케이스: catalog 등록·validation·status enum·subtasks passthrough·flux-demo 프로필 검증; 127→140 passed)
- Implementation choices:
  - **Astro scoped `<style>` (not inline JSX `<style>{...}`)**: Features.astro의 `<style>{...}` 패턴이 Fragment `<>` 안에서만 동작하고 section 안 중간에선 PostCSS가 백틱을 파싱 실패함을 빌드 오류로 확인 → Astro 컴포넌트 레벨 `<style>` 블록으로 전환. scoped CSS가 더 clean.
  - **3-state로 축소**: 원본 5-state(completed/in-progress/need-help/failed/pending) → 마케팅 read-only에 과하다는 CDO 스펙 지침 준수 → completed/active/upcoming 3종만.
  - **토큰 추가 없음**: success/warning/danger 토큰 신발명 대신 기존 text-2(completed muted), primary(active accent), text-3(upcoming tertiary) 재활용. 색은 보조, 아이콘 shape가 1차 구분.
  - **`<details open>` SSR fallback**: JS 없이 subtask 트리 전부 펼쳐진 상태 정적 렌더. JS가 있으면 네이티브 `<details>` toggle이 자동으로 닫기/열기 PE로 동작 — 별도 script 불필요.
  - **site_manifest.py passthrough 무변경**: `[dict(it) for it in items_val]`의 shallow copy가 subtasks(nested list)를 읽기 전용 JSON 직렬화에서 올바르게 통과시킴. 변경 불필요.
- Tests/verify: scaffold → out/flux-demo/site-manifest.json CLEAN(위반 0). Astro build `[build] Complete!` 1 page built in 6.61s. pytest 140 passed(기존 127 + 신규 13).
- Catches surfaced: 없음.
- 교훈: Astro에서 JSX 표현식 중간의 `<style>{...}` 패턴은 Fragment 안에서만 허용. 컴포넌트 레벨 `<style>` 블록이 scoped CSS + 타입 안전 + PostCSS 호환으로 더 권장.
- Cost: engineer subagent 1회 / envelope 반환.

## §3 — Open Loops (이 인격 책임)

- ~~react frontend adapter (Growth-16)~~ ✅ 완료 (L1/L3/L4 fastapi green)
- **Java DIM-6 live 미실행** — JDK/Gradle 환경서 `pytest tests/adapters/springboot-jakarta/` 37 green 확인 (M1 sign-off 전 필수, QA caveat)
- ~~FK 참조 무결성 (Growth-15 A+B+C)~~ ✅ 완료 (fastapi live 검증, java 코드 패리티)
- ~~creater axis: scaffold.py/manifest.py + frontend typed-form + G-11 (Growth-14)~~ ✅ 완료
- ~~M1 진입 시 첫 spawn — `middle/contract/` 첫 wire 키 schema 파일 작성~~ ✅ Growth-5d 완료
- ~~`scripts/diagnose.py` G-1 SPEC → PASS 전환~~ ✅ Growth-7 완료 (code→status 재선언 검출)
- adapter `paging.mode` fallback 제거 — flat-underscore 단일 표준 정착 시 (Growth-8 후보)
- ~~frontend vanilla-htmx adapter 구현 (Growth-8) + CDO tokens.md → tokens JSON 생성~~ ✅ Growth-8 완료
- ~~DDL axis: catalog.yaml 56 entities + dialects + render.py + G-10~~ ✅ Growth-10 완료
- `scripts/diagnose.py` G-2 SPEC → 활성 전환 시 함수 본문 보강 (profile path extractor)
- CTO escalation 4건 응답 대기 (Growth-5d Decision Log 참조)
- L2 HSQLDB schema+seed smoke harness 활성화 — QA 주도 (command: `python presets/ddl/render.py --dialect hsqldb > presets/ddl/build/hsqldb-schema.sql`)
- ~~wire `entity.create`/`entity.update` → catalog 검증 wiring~~ ✅ Growth-12 완료 (both adapters)
- ~~fastapi backend adapter (Growth-11)~~ ✅ 완료
- fastapi adapter: cursor paging 구현 — Growth-N (BAD_REQUEST 현재 동작, springboot 동일)
- DIM-5 validation tests 추가 — QA 주도 (`tests/adapters/_shared/test_compliance.py` 에 DIM-5 class 추가, validation-contract.md §6 시나리오 7개)
