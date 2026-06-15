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

## §3 — Open Loops (이 인격 책임)

- [x] `docs/design/tokens.md` 초안 — Growth-5c 완료
- [ ] landing/portal 비주얼 가이드 (M1 demo 전)
- [ ] persona interaction map — CMO 의 3 pitch 와 1:1 정렬
- [x] dark mode 보류 결정 (CTO Growth-5c, M2 게이트)
- [x] CTO 4 open questions (§9) 답변 수령 (Growth-5c)
- [ ] brand accent 색 확정 대기 (CEO + CMO — M1 gate)
- [ ] engineer agent 에 토큰 JSON 파일 생성 위임 (M1 착수 시)
