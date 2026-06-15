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

## §3 — Open Loops (이 인격 책임)

- [x] `docs/design/tokens.md` 초안 — Growth-5c 완료
- [ ] landing/portal 비주얼 가이드 (M1 demo 전)
- [ ] persona interaction map — CMO 의 3 pitch 와 1:1 정렬
- [x] dark mode 보류 결정 (CTO Growth-5c, M2 게이트)
- [x] CTO 4 open questions (§9) 답변 수령 (Growth-5c)
- [ ] brand accent 색 확정 대기 (CEO + CMO — M1 gate)
- [ ] engineer agent 에 토큰 JSON 파일 생성 위임 (M1 착수 시)
