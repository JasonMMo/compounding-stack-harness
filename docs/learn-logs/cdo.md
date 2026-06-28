# learn-log — CDO

> Design voice. UI 시스템·디자인 토큰·페르소나 인터랙션 인격의 ledger.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 인격 헌장: [`.claude/agents/design-agent.md`](../../.claude/agents/design-agent.md).

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Deliverable: <tokens.md / persona interaction map / landing visual 등>
- Persona served: <CEO / 업무담당자 / IT-담당자 중>
- Accessibility checks: <WCAG / contrast / keyboard nav 등>
- Cross-agent dependency: <CMO 카피 / CTO contract 정합성>
- Cost: <turns / 추정 $>
```

## §2 — Growth History

### Growth-5c (2026-05-29) — docs/design/tokens.md 초안 작성 (M0 founding deliverable)
- Deliverable: `docs/design/tokens.md` — 3 페르소나별 디자인 토큰 전체 스펙 (raw palette, 16+ semantic keys, persona overrides x3, a11y floor, adapter portability contract)
- Persona served: CEO / 업무담당자 / IT-담당자 모두 — 각 페르소나 density·typography·motion override 포함
- Accessibility checks: WCAG AA 4.5:1 contrast 모든 semantic color pair 검증 (§5 contrast table); KWCAG 2.1 10개 항목 매핑 (§4.2); focus state 3px ring spec (§4.3); prefers-reduced-motion token collapse (§2.5)
- Cross-agent dependency: CMO — brand accent 색 결정 (M1 gate, raw.blue 교체 시 semantic layer 무변경 전략 적용). CTO — dark mode 정책 / i18n label 소유권 / token versioning adapter compliance test 포함 여부 (§9 open questions 4개 escalate). CTO 답변 (Growth-5c, 2026-05-29): Q1 보류·Q2 adapter·Q3 YES·Q4 breakpoint.tablet 추가 — tokens.md §11 박힘.
- Cost: 1 turn (no subagent invocations, no WebFetch). 추정 $0.05~$0.10 (Sonnet 4.6, input heavy)

### Growth-65 (2026-06-15) — visual-asset 축(P2) + vision-QA 루브릭(P4)

- Deliverable:
  - `presets/themes/_theme-format.md` (신규 — 테마 스펙 포맷 규약)
  - `presets/themes/_INDEX.md` (신규 — 테마 인덱스)
  - `presets/themes/_motion/presets.yaml` (신규 — 모션 프리셋 8종: fade-simple / fade-up / stagger-children / hover-lift / parallax-lite / reveal-on-scroll / slide-in-left / scale-in; reduced-motion fallback = fade-simple 불변; autoplay 금지)
  - 프로덕션 테마 2종:
    - `aurora` — 대담 그라데이션, SaaS / 핀테크 / B2B 타겟. design/tokens semantic.json 상속(override-only).
    - `studio` — 미니멀 에디토리얼, 에이전시·컨설팅 타겟. 동일 상속 패턴.
  - 섹션 variant 23종 × 2테마 = 46 매핑 누락 0.
  - `design/vision-qa-rubric.yaml` (신규 — 8기준: visual_hierarchy / whitespace / typography / color / layout / responsive / brand / conversion)
- Persona served: 업무담당자 (홈페이지 의뢰 고객) + CEO (인도 전 게이트)
- Accessibility checks: a11y AA 자가검증 (실측 대비비). 섹션 variant 전원 AA 통과 기준 포함.
- Cross-agent dependency:
  - Engineer: theme.yaml → `build-tokens.mjs` 소비 (override-only 패턴 필수 준수).
  - QA: `vision-qa-rubric.yaml` 공동 권위 — 판정 기준 PASS = 모든 기준 ≥3 & 평균 ≥3.5 / BLOCK = 어느 하나 ≤2. CDO+QA 공동 게이트.
  - PM: ms_tone → theme 매핑 (aurora/studio) — intake answer 가 CDO 테마 결정에 1:1 연결.
- Cost: engineer subagent 위임 (이 인격 design spec 산출 + 검증).

### Growth-66 (2026-06-15) — dogfood GTM 랜딩 비주얼 검토 + favicon 슬롯 정책

- Deliverable:
  - `public/favicon.svg` (landing-astro adapter 신규 — "compounding stack" 3-bar 마크, indigo #4F46E5, 테마 중립 기본값)
  - 자사 GTM 랜딩 desktop+mobile full-page 비주얼 리뷰 (dogfood: theme=aurora, hero/features/faq 섹션)
  - **favicon per-theme 슬롯 정책 확립**: 테마가 `public/favicon.svg` 를 자체 파일로 override 하면 per-brand 파비콘 적용 가능. 이를 future per-theme asset slot 으로 문서화.
- Persona served: CEO (인도 전 비주얼 게이트), 업무담당자 (랜딩 페이지 방문 고객)
- Accessibility checks:
  - `prefers-reduced-motion` a11y 결함 수정 확인 (motion island 초기화 시 early-return → reduced-motion 사용자 콘텐츠 즉시 표시)
  - stagger-children 컨테이너 영구 숨김 수정 (Features·Logos 섹션 opacity:0 → 전 방문자 노출 복구)
- Cross-agent dependency:
  - Engineer: landing-astro adapter `public/` 디렉터리 신설 + motion 버그 수정 (Growth-66).
  - QA: full-page screenshot + reduced_motion="reduce" Playwright 캡처 — vision-QA 7/7 PASS 확인.
- Visual verdict (dogfood, desktop+mobile):
  - **판정 B급 professional** — 강한 타입 계층, aurora 그라데이션 hero, CTA 대비 양호, responsive 단열 모바일.
  - **후속 개선 후보** (future Growth):
    - (a) feature 카드 아이콘: `icon` 필드명(brain/layers/gauge)이 Features.astro 아이콘셋 미매핑 → 모든 카드가 동일 lightning 글리프 표시. 아이콘셋 매핑 작업 필요.
    - (b) split-left hero: hero media asset 없을 때 오른쪽 열 공백 → placeholder 이미지 또는 레이아웃 fallback 정책 결정 필요.
- Cost: CDO 비주얼 리뷰(이 인격) + engineer subagent 구현 위임 (Growth-66 동일 세션).

### Growth-68 (2026-06-15) — glowy-waves hero variant 비주얼 채택 (21st.dev → 8축)

- **결정**: 외부 폴리시 컴포넌트(21st.dev) 도입은 "한 장에 붙이기"가 아니라 **테마/섹션 8축에 재사용 variant 로 등록**해야 복리. hero 의 첫 프리미엄 variant 로 glowy-waves 채택(canvas glow + framer-motion).
- **토큰화 원칙**: 외부 컴포넌트의 자체 팔레트(딥 인디고 글로우)는 variant 시그니처로 허용하되, text/CTA/accent 는 우리 `--color-*` 토큰에 매핑 → 테마가 틴트 가능. shadcn 의존 제거(토큰 anchor 버튼).
- **시각 판정**: desktop+mobile 풀페이지 검토 — hero **B급→프리미엄** 도약. 그래디언트 헤드라인("Zero dev team." 보라), pills 3개·stats 3개 M1 메시지 정렬, 하단 features/FAQ/CTA/footer/contact 전부 정상 렌더, 모바일 반응형 단열.
- **후속**: (a) 동일 lightning 글리프 아이콘셋 매핑 미결(Growth-66 잔여 유지) (b) 3D Marquee·Feature Carousel 차기 variant 후보 (c) `headline_accent` 슬롯화로 그래디언트 split 안정화.
- Cost: CDO 비주얼 게이트(이 인격) + engineer 구현 위임 (동일 세션).

### Growth-70 (2026-06-15) — marquee-3d + carousel variant 콘텐츠 큐레이션

- **marquee-3d proof 월**: 3D 이미지 마키는 로고 티커가 아닌 사각 타일 그리드 → 콘텐츠를 파트너 로고(자산 無) 대신 **우리 12개 라이브 생성 데모 스크린샷**으로 결정 = thesis 정렬된 정직한 proof("이게 harness가 뽑은 실물"). 헤딩 "Real systems this harness generated" + 한글 서브헤드. 딥 인디고 배경이 glowy hero에서 연속.
- **carousel**: 탭형 feature 쇼케이스로 기존 three-col 대비 인터랙티브·시각 강화. 3 차별점(AI domain experts/swap stack/cost measured)에 proof 스샷 매핑.
- **시각 판정**: hero→proof월→카루셀→FAQ→CTA 흐름 B+/A- 도달. 8축(theme/section)에 hero·logos·features 각 1 프리미엄 variant 축적 = 복리 실증.
- **후속(open)**: (a) carousel feature 이미지가 /login 화면이라 "domain expert" 의미 약함 → 도메인 충실 스샷/목업으로 교체 (b) carousel 탭 표시 순서 정렬 (c) feature 아이콘셋 매핑(기존 잔여) (d) 차기 variant: pricing·testimonial.
- Cost: CDO 큐레이션(이 인격) + engineer 2회 위임.

### Growth-71 (2026-06-15) — impeccable craft 엔진 채택

- **결정**: 디자인 품질을 매 작업 노동이 아니라 도구로 — vendored `impeccable` SKILL 을 CDO 1차 craft 엔진으로 채택(design-agent.md "Craft 엔진" 절 명문화). register Brand/Product 가 우리 deliverable_kind 와 동형이라 마찰 적음.
- **craft 법규 흡수 대상**: impeccable anti-slop(보라/시안 그래디언트+글로우+다크네온, cream/sand AI 디폴트, 동일카드 reflex, 자간 ≤-0.04em)·motion 규칙(reveal=already-visible 위에서만, headless blank 금지) → vision-QA 루브릭 체크로 편입(후속).
- **reconcile**: impeccable 이 우리 glowy-waves hero(보라 그래디언트+글로우)를 slop 으로 판정 → 도구 가치 증명 겸 첫 실전 = `/impeccable critique gtm-landing` 권장. 결과에 따라 hero 그래디언트 톤다운 검토.
- **후속(open)**: 6 커맨드(layout/colorize/typeset/bolder/delight/polish) 검토 완료 — gtm-landing 에 layout(동일카드 격파)+polish 패스 후보. vision-QA 안티패턴 편입 미시행.
- Cost: CDO 검토(이 인격).

### Growth-72 (2026-06-15) — typeface 결정: Bricolage Grotesque + Epilogue (de-slop)

- **결정**: gtm-landing 폰트를 reflex-reject 4종(Plus Jakarta/Inter/DM Sans/DM Serif)에서 **Bricolage Grotesque(display)+Epilogue(body)** 로 교체. contrast-axis(구성적 그로테스크 + 기하-휴머니스트), 둘 다 off-reflex·MIT·self-host. "실물 craft" 브랜드에 캐릭터 부여, editorial/Stripe-minimal 포화 레인 회피. aurora theme.yaml 토큰 갱신 → 전 consumer 상속.
- **hero accent**: 그래디언트 텍스트(Absolute Ban) → 솔리드 바이올렛 #C4B5FD(aurora glow 톤 유지하며 ban 해소).
- **후속(open)**: hero glow 톤다운(/quieter, 유저 승인됨) → 다음. carousel /login 이미지 교체(/polish). em-dash(/clarify). critique 재실행해 27→상승 확인 권장.
- Cost: CDO 폰트 결정(이 인격) + engineer 위임.

### Growth-73 (2026-06-15) — critique 백로그 청산 (27→30 Good)

- **quieter 판정**: indigo glow 절제 채택(반사 완화), 단색 아이덴티티 유지 — 보조 accent(/colorize)는 현 단계 불요(restraint 의도).
- **polish 이미지 큐레이션**: carousel feature 이미지를 bare login(lawfirm/shop) → 콘텐츠 풍부 공개 캡처(edu-program/gtm-landing/construction)로. 도메인 충실 목업은 후속 자산 작업(auth-gated 한계).
- **결과**: detector CLEAN, Design Health 27→30(Good 진입). critique→fix→re-critique 트렌드가 craft 복리 루프를 수치로 입증.
- **후속(open)**: carousel 전용 도메인 목업(P2), indigo 보조 accent(/colorize, 선택), 연락폼 실엔드포인트(실고객).
- Cost: CDO 큐레이션(이 인격) + engineer 위임.

### Growth-74 (2026-06-15) — /colorize: warm 보조 accent 채택

- **팔레트 결정**: indigo 단색 → indigo(주) + **terracotta #AB5527**(보조). 보색·비-네온·AA. 전략 = Committed-leaning Restrained, 보조색 ≲15% 도징. navy+gold/cyan+purple 슬롭 회피.
- **적용 철학**: 차별화 1포인트("0 bits" = data leaves network 0)에 색 집중 → 단색 절제 유지하며 시선 유도. carousel 인디케이터·FAQ open-state 는 보조 wayfinding.
- **토큰화**: `accent-warm` semantic 토큰 → 전 landing 재사용(복리). 헤드라인 accent(violet)는 불변 — 2색 위계 명확.
- Cost: CDO 색 전략(이 인격) + engineer 적용.

### Growth-75 (2026-06-15) — harvest 테마 craft (맥주 런칭, 2번째 테마)

- **테마 컨셉**: gtm의 차가운 indigo-glow와 **정반대 질감** = 따뜻한 크래프트-맥주. 팔레트 = 로스팅 맥아 앰버-카퍼 drench(#9C5118 등) + 신선한 홉그린 + 상쾌한 포말 쿨 하이라이트(OKLCH). impeccable "cream/sand AI 디폴트" 회피 — 따뜻함을 timid near-white 아닌 committed 앰버로 표현.
- **타이포**: Big Shoulders Display(컨덴스드 "맥주 라벨" 디스플레이) + Hanken Grotesk(휴머니스트 본문). 둘 다 off-reflex, gtm의 Bricolage/Epilogue와 구분되는 별도 브랜드 정체성.
- **질감**: 그레인 SVG 노이즈 + CSS 탄산 버블(canvas 아님) = 유기적·촉각적. 3 pillar(roasted malt/fresh hops/crisp finish)가 CEO가 요청한 3 감각 직역.
- **검증**: 풀페이지 시각 게이트 3회(토큰 클로버·셰브론·blank 적발 후 수정). theme 축이 전 고객 재사용 자산으로 복리됨을 2번째 증명.
- Cost: CDO 테마 디자인(design-agent) + engineer 픽스 위임.

### Growth-76 (2026-06-15) — atelier 테마 + A2 아키타입 구성 craft (Studio North)

- **문제 재정의**: gtm(aurora)·hopwell(harvest)이 테마만 다르고 **페이지 구조가 동일** → 의뢰인 눈엔 같은 템플릿. CDO 결론: 진짜 다양성은 **섹션 variant × 페이지 아키타입 × 테마**의 곱. theme 축 단독으로는 부족.
- **atelier 테마**: 3번째 테마. ink-pressed editorial — 잉크블랙 hero(#141418) + warm-paper(#F5F2EC) + 단일 copper accent(#9A5B32, hover/CTA만). aurora(indigo)·harvest(amber)와 또 다른 정체성. 폰트 Raleway(art-deco display) + Karla(humanist body) — 둘 다 off-reflex, 기존 테마 폰트와 비중복. cream/sand AI 디폴트 회피(warm-paper는 chroma 낮은 의도적 종이, near-white 타이밍 아님).
- **A2 구성**: headline-only hero(이미지 0, 타입 주도) → masonry 갤러리("selected work") → 창업자 split 스토리(POV+pull_quote) → single-col 리스트 → 단일 대형 후기 → 다크 CTA → 미니멀 푸터. SaaS hero-metric·카드그리드 클리셰 회피. 잉크/페이퍼 14.2:1 등 전 페어 AA.
- **검증**: 풀페이지 시각 게이트 — CTA 빈 플레이스홀더 흰박스 적발→실콘텐츠 스샷 교체. detector CLEAN, no-JS h1 opacity 1.
- Cost: CDO 디자인(design-agent 백그라운드 1회, ~126K tok) / envelope.

### Growth-77 (2026-06-16) — kiln 테마 + A4 아키타입 parallax-scroll craft (TERRA ceramics)

- **Deliverable**:
  - 4번째 테마 `presets/themes/kiln/` — 점토 테라코타(clay #C9A078, OKLCH L0.78/C0.07·cream-trap 회피) + 목회재 중성(ash) + 가마-엠버 accent(#B5501A). 폰트: Cormorant Garamond(display) + Source Serif 4(body) — off-reflex serif+serif 대비 축, editorial-craft 지향. texture-clay/ash/ember 3 토큰(CSS gradient+grain, 사진 0). AA 10 pair 검증. aurora(indigo-glow)·harvest(amber-craft)·atelier(ink-paper)와 4번째 완전 고유 정체성.
  - 첫 **SCROLL-CINEMATIC variant** `gallery/parallax-scroll` — 21st.dev "Text Parallax Content" 적응. framer-motion `useScroll` 기반 sticky full-viewport "챕터" 패널이 스크롤에 따라 scale+overlay, 각 챕터의 heading/subheading은 parallax offset으로 독립 이동. 챕터 아래 editorial body+CTA 블록. 라이브러리 8축 중 처음으로 **scroll-driven 모션**(gtm·hopwell·studio-north은 intersect 기반 static-scroll). 시간 축에서 CEO "같은 패턴, 다른 색" 비판에 정면 응답.
  - `texture:clay|ash|ember` 센티넬 — parallax-scroll `src` 가 sentinel이면 테마 material-texture 필드 렌더(CSS gradient+grain). 실 고객은 실사 `src` 경로 입력, 데모는 사진 0으로 운영(A2 CTA blank-box 계열 결함 구조적 회피).

### Growth-130b (2026-06-28) — design-cloud cowork loop cycle-1 ⑦: --font-size-display 토큰 환류

- **Deliverable**: 본채 `design/tokens/{raw,semantic}.json` 에 디스플레이 타이포 토큰 신설 — `--font-size-display: 44px` / `--font-line-display: 52px` (raw `type.scale.display` + semantic `size-display`/`line-display`). 별채 hero(`components/hero/styles.css` + `.ds-pkg/src/components.css`) headline 을 `--font-size-3xl`(24px)→`--font-size-display` 스왑.
- **루프 검증**: cowork loop ⑥→② 다운로드(`DesignSync` read) → ⑦ 토큰 환류 경로의 첫 end-to-end 완주. cycle-1 브리프가 의도한 "토큰 갭 probe"(semantic 스케일이 24px에서 끝나 hero headline 부족)가 클라우드 워크벤치 오버레이로 발현 → 본채 단일진실에 토큰 신설로 해소(raw 자체확대 금지 원칙 유지).
- **Craft 인사이트 (핵심)**: baton 핸드오프엔 "40px 확정"으로 적혔으나, **cloud-pull 다운로드 실측 결과 오버레이 실제값은 44px**(`__om-edit-overrides` `font-size:44px !important`). 추정값으로 토큰을 박지 말고 **아티팩트를 먼저 내려받아 실측**해야 한다 — 핸드오프 노트와 실제 디자인이 갈릴 수 있다. founder 확인하 44px 확정. 다음 sync 시 워크벤치 오버레이는 토큰이 대체하므로 제거 가능.
- **Persona served**: 전 페르소나(랜딩 hero = marketing-site deliverable 공통 셸). landing-astro 가 본채 design/tokens 직접 소비처라 `--font-size-display` 자동 전파(legal-pro 는 독립 테마 경로라 무영향).
- **Accessibility**: 44px/52px line-height ≈ 1.18 비율(디스플레이 타이포 적정). 색/대비 무변경(text-1 on surface-1 17.28:1 유지).
- **Cross-agent dependency**: CTO — export_system 누출 게이트(24패턴) + preflight_sibling conformance PASS, 양 repo 파일당 커밋·push. design-cloud-bridge v2 경계(본채 클라우드 비연결: read-only 다운로드만, 업로드 노출 0) 준수.
- **Cost**: 본채 2커밋 + 별채 7커밋(9dbdfbc·6a80140 / 4b115e8..47ff5bb). subagent 0, API 추가 0.

### Growth-130c (2026-06-28) — cowork loop 자동화 A/B + 마커 가드 결함 환류 (CTO 검토)

- **Deliverable**: 별채 design_work_0625 가 cowork loop 자동화 4스크립트 추가, CTO 검토·파일당 커밋·push(`47ff5bb..b170306`). **A** `scripts/sync-preflight.mjs`(build-tokens→render 마커검증→본채 preflight_sibling.py 한 방, SYNC-READY 판정) + `scripts/hooks/{post-commit,install.mjs}`(커밋후 비차단 informer). **B** `scripts/design/pull-diff.mjs`(cloud→local 워크벤치 `__om-edit-overrides` 오버레이 감지, font-size→토큰 환류 힌트, 2단계: --fetch-list→에이전트 get_file 덤프→--remote diff).
- **경계 검증 (CTO 게이트)**: 두 스크립트 모두 §0 황금률 준수 — A는 본채 게이트 *호출만*(클라우드 미접촉, 업로드는 사람 게이트), B는 순수 node 라 원격 직접 read 불가→에이전트 fetch 강제(무인 클라우드 접근 불가가 설계로 보장). denylist 게이트를 cloud-exposed 별채가 아닌 본채에 두고 외부 호출하는 판단 정확(금지패턴 목록 노출 방지). preflight_sibling CLEAN(신규 4파일 포함, denylist 0/conformance 0) + sync-preflight 직접 실행 SYNC-READY 확증.
- **확정 결함 1건 (design_work_0625 lane — CTO 미수정, 신호만)**: sync-preflight 의 미해결-마커 가드가 **exit code 아닌 stderr 문자열 매칭에 전적 의존**. `render-showcase.mjs` 는 마커 잔존 시에도 exit 0(`process.exit` 는 components-dir 부재 1곳뿐) → 구조적 가드 L62 가 못 잡고 fragile grep `/미해결 마커|\[WARN\]/` 만 남음. 누락(문구 변경 시 마커가 클라우드로)·오탐(무관 `[WARN]` 에 hard-FAIL) 양방향 취약. **근본 수정 권장**: render-showcase 가 마커 발견 시 `process.exit(2)` → L62 구조적 캐치, grep 은 보조 강등.
- **Craft 인사이트**: 핸드오프 자동화 게이트는 "통과/실패" 신호의 **출처가 구조적(exit code)인지 문자열 파싱인지** 구분해야 한다 — 후자는 산출물 문구 드리프트에 silently 깨진다. 다운로드-먼저(130b)와 동일 교훈: 추정·문자열이 아니라 결정적 신호에 게이트를 묶는다.
- **음성 테스트 검증 (N1/N2, CTO, 클라우드 미접촉)**: 게이트가 "초록불 고무도장"이 아님을 차단 경로로 증명. **N1**(미해결 마커 주입) — render-showcase 단독 exit **0**(결함 재현 확정), sync-preflight는 stderr grep으로 exit **1** 차단(현 방어선이 문구 하나에 매달림을 실측). **N2**(denylist `attorney`+인프라 URL 주입) — preflight_sibling 게이트 ABORT exit **1**, LEAK 4건; 보너스로 **셸뿐 아니라 gitignored 렌더 산출물(`reference/rendered/`)까지 트리 전체 스캔**(누출이 셸 밖으로 새도 차단, defense-in-depth 확인). 양 테스트 주입분 `git checkout`+재렌더로 원복, 커밋 0. N3(graceful-degrade exit 2)는 별채 T1 검증 시 끼워 돌리기로 스킵.
- **Cross-agent dependency**: design_work_0625 — 4스크립트 작성. CTO — 소스 검토·경계 검증·게이트 재실행·**N1/N2 음성 테스트**·파일당 커밋·push·결함 판정. 후속은 `.handoff/baton.md` **cycle-2 브리프**로 핸드오프(STATE=BRIEF-POSTED): **T1** render-showcase `process.exit(2)`(마커 전용)+sync-preflight L62 `status===2` 분기(문구 의존성 제거), **T2** 재빌드 번들 재업로드 후 pull-diff cycle-2로 Hero override-free CLEAN 확인 → ⑦ round-trip 닫힘 증명.
- **Cost**: 별채 4커밋, subagent 0, API 추가 0.

<!-- 아래는 Growth-77 terra-ceramics 단편(헤더 유실) — 별도 정리 대상 -->
  - item_slots 보강: `gallery/parallax-scroll`(heading/subheading/body/cta_label/cta_href), `story/timeline-year`(year/milestone/detail). 신규 섹션 type `lead/minimal-field`(`entity.create`(entity_type=lead) 재사용, G-1 — 신규 wire key 0). 카탈로그 11→13 type.
- **Persona served**: 업무담당자 (공예·로컬 홈페이지 의뢰 고객), CEO (인도 전 게이트)
- **Accessibility checks**: AA 10 pair 검증(clay/ash/ember 조합 전부). no-JS 콘텐츠 5/5 PASS(framer-motion SSR baked opacity 함정 회피 — Growth-69 계열). mobile body.scrollWidth−clientWidth=0px, hero "Made of earth, fire, and time." 390w Cormorant 줄바꿈 정상.
- **Visual verdict**: desktop+mobile+no-JS 풀페이지 PASS — kiln 토큰(#C9A078), 3 chapter heading, hero, lead 전부 라이브 콘텐츠 그랩 확인(terra-ceramics.n9n.co.kr).
- **Cross-agent dependency**: Engineer — GalleryParallaxScroll.tsx(rules-of-hooks 수정·SSR opacity 수정), Lead.astro, Story timeline-year 구현. DevOps — terra-ceramics 배포 + COOLIFY_API_BASE 오픈루프 종결.
- **Cost**: CDO 디자인(design-agent) + engineer 구현 위임.

### Growth-78 (2026-06-16) — meridian 테마 + A6 B2B-services 비주얼 게이트 (MERIDIAN)

- **Decision**: 5번째 테마 **meridian** — B2B 매니지드IT/보안 자문 레지스터. 색 전략 = **Committed(단일 시그널)**: 쿨스톤 화이트 surface #F7F8F4(OKLCH C0.008 H100 — cream/sand 디폴트 회피, 돌 캐스트)에 **딥 포레스트그린 #1A5C3A**(OKLCH H155 = green, navy/indigo 반사 회피) 단 하나. glow·gold·gradient 0. 신뢰는 구조·정밀·여백으로 전달. 폰트 = Syne(geometric-angular display, 엔지니어드 권위) + DM Sans(humanist body) — 대비축 페어링, 이전 5 테마와 전부 distinct.
- **Accessibility checks**: a11y 8 pair 전부 AA~AAA(body 17:1, primary on surface 12.3:1, hero dark 17.8:1, team monogram white-on-forest 12.3:1 AAA). text-3 tertiary 4.6:1 AA minimum.
- **Visual verdict (CTO/CDO 게이트)**: desktop+mobile+no-JS 풀페이지 PASS. hero(near-black)→quote-band(forest-green) 연속 다크밴드지만 hue shift 로 의도적 분리 확인. process 넘버럴(합법적 시퀀스), team monogram(MR/PN/TL forest 원), forest-green CTA 밴드 — A6 가 SaaS/F&B/agency 와 구조적으로 다른 회사로 읽힘. 약점=features 텍스트 스택 sparse(이미지 0)이나 B2B 절제로 수용. forest 토큰(#1A5C3A) 라이브 확인.
- **Cross-agent dependency**: Engineer — Process.astro·Team.astro(monogram)·Logos quote-band·라우팅·Syne/DM Sans 폰트. DevOps — meridian 배포 + 포털 재배포. CTO — profile B2B 카피 직접 작성.
- **Cost**: design 토큰 CTO 직접(design-agent 미spawn) + engineer 구현 위임.

### Growth-84 (2026-06-16) — prism 테마(9번째) + hero/bento-grid + A7 API Platform archetype

- **Deliverable**: `out/bento-hero/cdo-spec.md` — (1) prism theme.yaml 전체 토큰(deep-azure #1B4FA8, OKLCH H≈228 미점유 hue, white canvas, IBM Plex Sans+DM Sans+DM Mono, `accent-glow: 0.00` 글로우 완전차단), (2) hero/bento-grid 변형 스펙(GlassmorphismTrust 21st.dev 레퍼런스의 **구조**(text-7col/stat+marquee-bento-5col)만 차용·dark-neon 팔레트·백드롭글로우·스톡이미지 전량 제거·흰 캔버스+은은한 surface-2 카드로 중화), (3) props/item_slots/catalog 항목 제안, (4) A7 API Platform archetype 신설(8 sections, light hero, process 섹션 없음, stats ticker surface-2 배경), (5) Prism 전 섹션 카피 전문, (6) impeccable 4-reflex-reject 자가검사 1줄씩.
- **Hue 선정 근거**: H≈220-240 대역 전 9테마 미점유 확인(기존 hue 시계 재검토). aurora(H≈280)와 52도 간격, neon-cyan(H≈200) 금지구역 이탈. primary(#1B4FA8) on white = 7.6:1 AAA — 전 토큰 쌍 AAA 목표 충족.
- **Growth-69 준수**: bento 카드 콘텐츠 전량 SSR baked; `backdrop-filter: blur` 은 progressive enhancement만. 마키 정적 fallback 구현(`prefers-reduced-motion` 가드).
- **CTO 비주얼 검증 FIX-FIRST 2건**: ticker-band 라이트밴드 대비 부족(surface-2 배경 시 토큰 미적용) + footer 빈컬럼 — 엔지니어가 컴포넌트 일반화(조건부 bg 토큰 주입 + 컬럼 필 guard)로 해결.
- **Persona served**: IT-담당자 / ops (API platform 타겟 buyer)
- **Accessibility checks**: text-1 (#141C28) on white 17.7:1 AAA; primary (#1B4FA8) on white 7.6:1 AAA; bento 카드 내부 (surface-2) 16.4:1 AAA; text-3 4.6:1 AA(캡션 전용). focus ring = primary, non-text 7.6:1 >> 3:1.
- **Cross-agent dependency**: Engineer — IBM Plex Sans + DM Sans + DM Mono fontsource 패키지 추가, HeroBentoGrid.astro 구현, catalog.yaml bento-grid variant 추가, landing-pattern-matrix §2·§3 갱신. QA — 비주얼 게이트 + no-JS 검증.
- **Cost**: CDO 디자인 패스 1 turn (design-agent, out/ 파일 산출).

### Growth-130d (2026-06-28) — (가) 슬라이스 브릭2: landing-astro IO-reveal → motion 팔레트 배선

- **Deliverable**: Growth-87 IO-reveal 3티어(`:root` baseline / `[data-motion="subtle"]` / `[data-motion="rich"]`)의 duration/ease/stagger 를 브릭1 design motion 팔레트 `var(--motion-*-*)` 참조로 교체. landing-astro `tokens.gen.css`(생성기 build-tokens.mjs 가 semantic.json flatten)에 motion primitive 11종(duration fast/base/slow/intro, ease standard/emphasized/exit/spring, stagger tight/base/loose) 자동 유입 — 생성기 무수정. 살아있는 reveal 시스템이 design 토큰을 실제 소비 = 토큰 시스템 end-to-end 증명.
- **CTO 매핑 결정(팔레트 동결, 어댑터 소비자만 변경)**: baseline=slow/emphasized/stagger-base(80 정확일치), subtle=base/emphasized/stagger-tight, rich=slow/emphasized/stagger-loose. `--motion-distance`(공간값)는 팔레트 밖 → 현행 유지(baseline −24/subtle −16/rich −40).
- **CTO 판단 — rich duration 팔레트 갭**: 구 rich=640ms였으나 팔레트에 rich 전용 슬롯 부재 → slow(480)를 baseline과 공유. rich 차별화는 distance(−40, baseline 1.67×) + stagger(140, 1.75×)로 지각상 충족 → 수용. `duration-xslow`(640+) 슬롯은 후속 브릭에서 CDO 필요 시 팔레트 추가(미결).
- **범위 한정**: 레거시 `.motion-fade-*`(`--animation-*`)·`.hover-lift`(`--transition-*`) 클래스는 이번 제외(후속 브릭).
- **검증(CTO 독립)**: build:tokens rc0 · test:tokens 8/8(브릭2 가드 2건 신설) · astro build rc0(2p/5.26s) · prefers-reduced-motion 3블록 생존(fade-simple 강등 유지) · G-69 default-visible 무손상 · global.css 3블록 팔레트 var 참조 직접 확인 · tokens.gen.css 11종/구 transition 0.
- **커밋(파일당)**: `81b98a1` global.css, `fd9546f` tokens.test.mjs. tokens.gen.css=gitignored 빌드산출물(미커밋, 빌드 재생성). 푸시 `747910d..fd9546f`. preflight leakage CLEAN.
- **Cross-agent**: design-agent 실행(매핑 표 CTO 제공). Engineer — 후속 브릭(레거시 클래스 토큰화 + 신규 intro/page-transition 프리셋)에서 합류.

### Growth-130e (2026-06-28) — (가) 브릭3b/3a/3c: 페이지 전환 프리셋 + 모션 어휘 단일화 완결

- **3b 신규 capability — 페이지 전환 프리셋**(engineer): landing-astro에 Astro `<ViewTransitions/>`(4.16.18 API) 탑재, `isMotionOn`(motion!=off) 게이트 → off는 라우터 미탑재=표준 풀내비(G-69). `::view-transition-old/new(root)` cross-fade+rise가 `--motion-duration-base`(280, 스냅)·`--motion-ease-emphasized` 소비. reduced-motion=animation:none. `intro`(900) 토큰은 일회성 인트로-오버레이용 보존. README 모션 섹션에 프리셋 등록(섹션 아닌 사이트-레벨 → catalog.yaml 무변경, motion 다이얼로 전 고객 자동 적용). 커밋 `e951904`(BaseLayout)/`a5694ab`(global.css)/`618bd06`(README).
- **3a 어휘 단일화**(design): 레거시 `.motion-fade-simple/up`·`.motion-scale-in`·`.motion-stagger-child`·`.hover-lift` 의 하드코딩 fallback(200/500/450/300ms+raw bezier) → 팔레트 토큰 fallback으로 교체(1차 island var 보존, fallback만). reduced-motion 강등 타겟도 토큰화. IO-reveal 3티어(브릭2) 무변경. 커밋 `07c8b29`(global.css 1파일, 8/8행).
- **3c 팔레트 갭 해소**(design): 브릭2 박제한 rich duration 갭 → `motion.duration.xslow`(640) 1슬롯 additive 추가(raw.json/semantic.json), landing rich `--motion-duration` slow→xslow 재배선. 3 생성기(landing/react/vanilla) 전부 xslow emit 확인. 기존 4값(150/280/480/900) 불변. 커밋 `143e48b`(raw)/`aab8d37`(semantic)/`7be1bd1`(landing global rich).
- **CTO 통합검증·정정 1건**: 3c 브리프에서 내가 react TRACKED 토큰출력을 `src/styles/semantic.css`로 지정했으나 **실재하지 않는 경로**(`check-ignore`가 비존재 비-ignore 경로를 TRACKED로 오판). 실제 react 토큰출력은 전부 gitignore(`src/tokens/tokens.gen.css`) → react drift 0, 커밋할 tracked 산출물 없음이 정답. design-agent가 임의 커밋 않고 플래그→CTO 소스 확인(`git ls-files`/`git grep`)으로 확정. [subagent-cross-service-verify] 적용.
- **검증(전 브릭 CTO 독립)**: build:tokens/test:tokens(8/8)/astro build 전부 PASS, reduced-motion·G-69 무손상, 커밋 파일당·푸시(`4904a89..7be1bd1`)·preflight CLEAN.
- **결과**: (가) 슬라이스 = 팔레트(브릭1)→IO-reveal 배선(브릭2)→페이지전환 프리셋(3b)→레거시 흡수(3a)→팔레트 갭해소(3c). landing-astro 모션이 design 토큰 단일 소스로 완결. 후속(미결): 일회성 인트로-오버레이(`intro` 토큰 소비), 타 어댑터 motion 토큰 확산.

### Growth-130f (2026-06-28) — (가) 후속: 일회성 인트로 스플래시 오버레이 (intro 토큰 첫 소비)

- **신규 컴포넌트**(engineer): `IntroOverlay.astro` — 브릭2~3c에서 보존해둔 `--motion-duration-intro`(900) 토큰의 **첫 소비처**. 의뢰인 "인트로 페이지" 요구의 나머지 절반.
- **G-69 inverted-default 패턴**(CTO 설계 결정): 오버레이 기본 CSS = 완전 숨김(opacity:0/visibility:hidden/pointer-events:none). JS가 첫 로드에만 `.is-active`(노출)→`.is-exiting`(토큰 구동 퇴장) 부여. 기존 IO-reveal은 "기본 가시→JS가 숨김"인데, 풀스크린 오버레이는 역으로 "기본 숨김→JS가 노출"이어야 JS-off에서 콘텐츠 미가림. degrade 4경로: JS-off(.is-active 미부여)/motion=off(BaseLayout 게이트 마크업 미출력)/reduced-motion(스크립트 early-return + CSS display:none)/세션 재생됨(sessionStorage `landing-intro-played`).
- **CTO 2차 환류 — safety timeout**: 1차 산출물은 collapse를 `animationend`에만 의존. 코드베이스 타 모션 island(IO-reveal 800/1200ms fallback) 규율 대비 누락 → 멈춤 시 풀스크린 오버레이가 콘텐츠 영구 가림=최악 모드. `done` 가드 공유 collapse() + `setTimeout(intro+400ms)` 추가 재위임, animationend/timeout 중 선발화 승리. VT: `astro:page-load` 바인딩(내비마다 재확인, 키 존재 시 즉시 return).
- **토큰 소비**: 퇴장 `@keyframes intro-overlay-exit`+워드마크 `intro-mark-scale`(1→1.04) 모두 `--motion-duration-intro`+`--motion-ease-emphasized`(하드코딩 0). 팔레트 FROZEN 무변경(`git status design/tokens` CLEAN 확인).
- **검증(CTO 독립)**: astro build SUCCESS, 4 degrade 경로 코드 추적 확인, BaseLayout 마운트=body 첫 자식·게이트, preflight CLEAN. 커밋 파일당 4건 `3e4531c`(component)/`2ff626b`(global.css)/`42242d1`(BaseLayout)/`df5d7c6`(README), 푸시 `d72a52d..df5d7c6`.
- **결과**: (가) 슬라이스 motion 토큰 5값(150/280/480/640/900) 전부 소비처 확보 — intro까지 살아있는 토큰이 됨. 후속(미결): 타 어댑터(react/vanilla) motion 토큰 확산.

### Growth-130g (2026-06-28) — (가) 후속: motion 토큰 타 어댑터 확산 (react·vanilla-htmx)

- **확산 = 양자화 마이그레이션**(CTO 결정): 두 어댑터는 motion 토큰을 emit 하나 소비 안 함(정찰 확인). 임의 레거시 duration 마다 토큰을 늘리는 건 토큰 시스템의 본질(제약 스케일)을 파괴 → ad-hoc 값을 기존 5-tier 로 **양자화**. 팔레트 FROZEN 무변경.
- **react**(engineer): app.css 하드코딩 `0.15s` 2건 → `--motion-duration-fast`+`--motion-ease-standard`. 부수효과: 기존 하드코딩이 reduced-motion override(→0.01ms)를 우회하던 접근성 버그 해소. 커밋 `277405e`.
- **react codegen 근본버그 적발·수정**(CTO→engineer): 빌드 검증 중 react 어댑터가 **master 에서 전면 빌드불가** 발견 — `codegen.mjs` 가 wire 키의 `.`만 `_`로 치환하고 `-`는 방치, `project.search-similar`→`project_search-similar:` bare key→TS 구문오류(prebuild 자동재생성이라 상시 깨짐). 근본수정: `key.replace(/[^A-Za-z0-9]/g,'_')`(G-7 flat-underscore 일치). contract YAML 하이픈 보존, 어댑터가 식별자 정규화. 생성물 gitignored. 커밋 `ab196cc`. **[subagent-cross-service-verify]: 에이전트 "pre-existing build fail" 주장을 CTO 가 직접 빌드 재현·근본원인 소스확인 후 채택(경로도 에이전트 추정 src/wire→실제 src/contract 정정).**
- **vanilla-htmx**(design): app.css 21 transition 양자화 — 100/120/150/180/200/220ms → fast/base, ease/cubic-bezier → standard/emphasized. 200ms site별 판정(micro→fast, 레이아웃→base). **CTO 정정 1건**: 사이드바 슬라이드(L459) 감속-진입 곡선을 design 이 ease-exit(가속)로 오매핑 → ease-emphasized 로 정정(의미 역전 방지). tokens.css reduced-motion override 로 전 transition 자동 강등 확인. 커밋 `1cdaf2a`.
- **검증·인도**: react 풀빌드 SUCCESS(codegen 수정이 motion 변경까지 동시 검증), preflight CLEAN, 파일당 3커밋 푸시 `a17ff39..1cdaf2a`.
- **결과**: 3 어댑터(landing/react/vanilla) 전부 motion 토큰 소비처 확보 — palette 단일 소스가 전 프런트로 확산. 후속(미결): HTMX swap/settle 전환 프리셋(vanilla net-new capability, landing 3b 격 — 정찰이 "최고 레버리지"로 지목).

## §3 — Open Loops (이 인격 책임)

- [x] `docs/design/tokens.md` 초안 — Growth-5c 완료
- [ ] landing/portal 비주얼 가이드 (M1 demo 전)
- [ ] persona interaction map — CMO 의 3 pitch 와 1:1 정렬
- [x] dark mode 보류 결정 (CTO Growth-5c, M2 게이트)
- [x] CTO 4 open questions (§9) 답변 수령 (Growth-5c)
- [ ] brand accent 색 확정 대기 (CEO + CMO — M1 gate)
- [ ] engineer agent 에 토큰 JSON 파일 생성 위임 (M1 착수 시)
