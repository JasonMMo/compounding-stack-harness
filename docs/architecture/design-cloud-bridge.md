# Design-Cloud Bridge — claude.ai/design ↔ repo 분리·통합 아키텍처

> CTO 결정 (Growth-130, 2026-06-26). 근거: deep-research 검증 리포트 (8 findings, adversarial 3-vote).
> 원본 초안 `out/deep-research-design-cloud.json` (gitignored). 지식 환류:
> [[claude-design-cloud-boundary]] (`knowledge/wiki/syntheses/`).

## 0. 문제

디자인 조정에 반복작업·시간이 과다하고, axis-8 산출물이 "밋밋"하다. 원인은 구조적이다 —
시각적 다양성이 (a) 토큰 재색칠 + (b) site-sections 카탈로그의 고정 `variants` 집합에서만
나오고, 새 레이아웃은 어댑터 컴포넌트를 손으로 짜야 한다. 게다가 실제 시간 싱크는 디자인
*사고*가 아니라 `편집 → push → Coolify redeploy → headless 검증` 배포-왕복이다 ([[htmx-demo-verify-skill]]).

claude.ai/design (Claude Design, `/design-sync`)은 **배포 없이 브라우저에서 렌더된 컴포넌트를
즉시 보며 craft** 하는 점에서 이 둘을 친다. 그러나 클라우드 결합·데이터 누출 리스크가 있어
**경계 설계가 선결**이다. 본 문서가 그 경계와 통합·복제본 전달을 규정한다.

## 1. 연구로 확정된 제약 (외부 사실)

신뢰도 라벨은 deep-research 검증 투표 결과. 출처는 §7.

| # | 제약 | 신뢰도 | 함의 |
|---|---|---|---|
| C1 | Claude Design 은 유료 티어(Pro/Team/Enterprise) 기능, Free 미포함 | high | 내부 워크벤치로만 쓰는 전제 — 고객은 접근 안 함 |
| C2 | Claude Design 은 **BAA 적용 제외**(beta 태그). Enterprise 라도 HIPAA/규제데이터 보장 밖 | high | **의뢰인 PII·변호사-의뢰인 비밀 자료는 절대 업로드 금지.** beta 졸업 시 재검증 |
| C3 | 기본 프라이버시 정책(eff. 2026-07-08)은 Input/Output **학습 사용 허용**(opt-out 가능, 단 ①안전검토 플래그 ②사용자 신고 2건은 opt-out 무시) | high | 비-Enterprise 계정 업로드물은 학습 포함 위험. Enterprise 는 별도 고객계약 적용 |
| C4 | 서드파티 커넥터/외부 API 로 데이터 전달 시 해당 정책 적용 + 정부요청 대응 정책 존재 | high | 클라우드 업로드 컴포넌트는 법적 disclosure 대상 가능 |
| C5 | DTCG JSON 포맷 first stable **2025.10**. W3C **Community Group** deliverable(완전한 W3C Recommendation 아님), 벤더중립 interop, 스펙만 발행(툴 아님), alias/2-layer 지원 | high | 토큰 경계 표준으로 채택. 고객에 "W3C 표준 준수"로 광고 금지(뉘앙스) |
| C6 | Style Dictionary v4+ 권장 빌드엔진(first-class DTCG, Node+브라우저, 단일소스→CSS/Sass/Android/iOS, `include`/`source` override). v5(v5.5.0, 2026-06-21)에 DTCG v2025.10 — **v5+ 핀** | high | 우리 `build_tokens.py` 의 정렬 대상 또는 대체 후보 |
| C7 | Storybook Package Composition — 디자인시스템을 자체 버전 npm 패키지 + 자체 호스팅 Storybook(`storybook.url`)으로, 소비 repo 가 소스 inline 없이 참조 | high | 분리-발행 파이프라인 패턴. 단 원격 호스팅 Storybook 필요 |
| C8 | vercel/platforms 멀티테넌트는 **런타임** 미들웨어 라우팅(Redis per-tenant)=런타임 논리격리. self-host 프라이버시 우선엔 **반대 패턴**: 빌드타임 정적 per-customer 빌드=물리격리가 우월 | high | landing-astro SSG = 이미 빌드타임 정적 → 복제본 전략의 정합 근거 |

**핵심 결론**: C2+C3+C4 가 **분리 경계를 강제**한다 — PII·기밀은 클라우드 워크벤치에 도달해선 안 되고,
넘어오는 유일한 산출물은 **정규화된 DTCG 토큰 JSON** 이어야 하며, 클라우드 결합은 production·인도물에
**일절 잔존하지 않아야** 한다.

## 2. (A) 분리 경계 — 무엇이 클라우드, 무엇이 repo

```
┌─────────────────────── CLOUD (claude.ai/design) ────────────────────────┐
│  authoring-only surface. 내부(CTO/CDO)만 접근. 고객 접근 0.               │
│  · 컴포넌트 HTML 을 배포 없이 즉시 렌더하며 craft (밋밋함 해소 엔진)       │
│  · 업로드 금지: 의뢰인 PII / 변호사-의뢰인 자료 / 고객 실데이터 (C2~C4)   │
│  · 올라가는 것: 무명(無名) 디자인 컴포넌트·팔레트 실험만                  │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │  경계를 넘는 유일 산출물 =
                               │  ▶ DTCG 토큰 JSON (raw/semantic override) ◀
                               │  (컴포넌트 HTML 은 production 코드에 유입 금지;
                               │   craft 결정을 "토큰+variant 명세"로만 추출)
                               ▼
┌─────────────────────────── REPO (compounding-stack-harness) ─────────────┐
│  axis-8 복리 저장소 (single source of truth)                              │
│  · design/tokens/{raw,semantic}.json  ← DTCG 경계 (C5)                    │
│  · presets/themes/<slug>/theme.yaml   ← override-only                     │
│  · presets/site-sections/catalog.yaml ← variants 명세                     │
│  · frontend/adapters/landing-astro/   ← SSG 소비자 (빌드타임 정적, C8)    │
└───────────────────────────────────────────────────────────────────────────┘
```

**불변 규칙**:
1. 경계를 넘는 것은 **토큰 JSON + variant 명세뿐**. 클라우드의 컴포넌트 HTML 을 그대로
   production 에 붙이지 않는다 (정규화 게이트 B 통과 필수).
2. 클라우드는 **authoring-only**. 빌드·배포·인도물 어디에도 claude.ai API 참조·URL 이 남지 않는다.
3. 우리 기존 토큰 계층(raw→semantic→theme.yaml→persona)은 이미 DTCG 의 2-layer/alias 모델과
   정합(C5) → **이 계층이 곧 경계**. 새 표준을 만들지 않는다 (복리).

## 3. (B) 통합 + 정규화 게이트

```
claude-design craft  ──/design-sync (1 컴포넌트씩)──▶  staging/ (gitignored)
                                                          │
                          ┌── 정규화 스크립트 (CDO/design-agent + impeccable) ──┐
                          │  컴포넌트에서 색/간격/타이포 결정을 추출 →          │
                          │   · design/tokens/*.json 또는 theme.yaml override   │
                          │   · presets/site-sections/catalog.yaml 의 variants  │
                          │  레이아웃은 landing-astro 컴포넌트 + variant 키로    │
                          └──────────────────────┬───────────────────────────────┘
                                                 ▼
                          CI lint 게이트 (D) ─ PASS ─▶ commit (파일당, §9)
```

- `/design-sync` 는 "한 컴포넌트씩, 통째 교체 금지" 설계 → **variant 단위 점진 통합**에 정합.
  대량 마이그레이션엔 부적합 (anti-pattern, §6).
- 정규화 게이트가 **비협상 조건**. 이걸 건너뛰고 클라우드 산출을 페이지에 직접 붙이면 one-off
  덤프 = axis-8 복리 붕괴. CDO 가 catalog variant + 토큰으로 분해해야 머지.
- 산출물 착지 매핑:

| claude-design 산출 | repo 착지 |
|---|---|
| 새 hero/feature/pricing 레이아웃 변형 | `presets/site-sections/catalog.yaml` `variants:` + landing-astro 컴포넌트 |
| 색·타이포 팔레트 | `design/tokens/*.json` + 새 `theme.yaml`(override만) |
| 컴포넌트 craft(그림자·모션·간격) | semantic.json / theme-specific 토큰 |

## 4. (C) 고객 복제본 빌드 — 빌드타임 물리격리

연구 C8: 런타임 라우팅(vercel/platforms, Redis per-tenant)의 **반대**로 간다.
self-host·프라이버시 우선이므로 **빌드 시점에 고객별 정적 번들을 물리적으로 생성**한다.

```
공유 base 토큰 (include)  +  고객 theme.yaml (source, override)
        │                            │
        └──────────► Style Dictionary v5+ (C6) ─▶ 고객 전용 CSS
                                                      │
              고객 profile/site-manifest ─▶ landing-astro SSG ─▶ 정적 번들
                                                      │
        ┌─────────────────────────────────────────────┘
        ▼  인도물 = 그 고객의 브랜딩/데이터만. 타 테넌트 0. 클라우드 결합 0.
```

- `include`(공유 base) / `source`(고객 override) override 패턴(C6)이 복제본 생성의 빌드 프리미티브.
- landing-astro 가 이미 빌드타임 SSG(C8 정합) → **구조변경 없이** 같은 파이프라인에 고객 profile +
  theme.yaml 만 주입하면 복제본. "구조변경 0" 요구 충족.
- 인도 번들엔 **claude.ai 참조·타 테넌트 slug·raw PII 가 0** 이어야 한다 → 게이트 D 가 강제.

## 5. (D) CI/QA 게이트 + 프라이버시 가드 (G-N 후보)

`scripts/diagnose.py` 에 추가할 가드 후보 (번호는 §2 카탈로그 확정 시 부여):

| 가드(후보) | 검사 | 차단 사유 |
|---|---|---|
| **업로드 스코프 가드** | `/design-sync` finalize_plan 대상에 PII/기밀 태그·고객 slug·실데이터 경로가 포함되면 BLOCK | C2~C4 — 클라우드 학습/disclosure 노출 |
| **클라우드 결합 누출 가드** | 빌드 출력·인도 번들에 `claude.ai`/design API URL·클라우드 자산 참조 grep → 발견 시 BLOCK | A§2 규칙 2 — 인도물 결합 잔존 |
| **교차 테넌트 누출 가드** | 복제본 번들에 타 고객 slug/식별자 grep → 발견 시 BLOCK | C 물리격리 — 데이터 누출 0 |
| **DTCG 토큰 스키마 가드** | 경계를 넘는 토큰 JSON 이 DTCG v2025.10 스키마 통과(C5) + semantic 키 화이트리스트 | B — 정규화 게이트 무결성 |
| **정규화 게이트 가드** | staging/ 컴포넌트 HTML 이 production 경로(frontend/adapters/*/)에 직접 커밋되면 경고 | B — one-off 덤프 방지(복리) |

> 위 5종은 **§2 가드 카탈로그 + §4 counter 갱신**과 함께 별도 Growth 에서 구현 (이번은 설계 박제).

## 6. 리스크·안티패턴 (연구 §5) + 완화

| 안티패턴 | 완화 |
|---|---|
| 벤더 락인 (클라우드 툴에 디자인 자산 종속) | 경계 = DTCG 토큰 JSON(C5). 클라우드는 authoring-only, repo 가 single source |
| 클라우드↔repo drift | 토큰 JSON 단일 경계 + 정규화 게이트. 컴포넌트 HTML 양방향 동기화 금지 |
| 실수 데이터 게시 | 업로드 스코프 가드(D) + 운영 규칙 "무명 컴포넌트만 업로드" |
| one-component-at-a-time 병목 | variant 단위 점진 통합에 한정. 대량 작업은 repo 내 직접(클라우드 우회) |

## 7. 출처 (deep-research, fetched 2026-06-25/26)

- claude.ai/design 티어·BAA·프라이버시: anthropic.com/pricing · /legal/privacy · support.claude.com BAA articles (8114513, 15455031) · support.anthropic.com privacy-legal
- DTCG: designtokens.org · tr.designtokens.org/format
- Style Dictionary: styledictionary.com (+ /info/architecture, /info/dtcg) · github.com/style-dictionary
- 분리-발행: storybook.js.org/docs/sharing/package-composition
- 멀티테넌트 대조: github.com/vercel/platforms

## 8. 채택 단계 (phasing)

1. **Phase 0 (본 문서)** — 경계·게이트 설계 박제. ✅
2. **Phase 1 파일럿** — 밋밋한 표면 1개(권장: landing-astro 테마 1종)로 craft→sync→정규화→라이브
   한 사이클 측정. 시간절감·품질상승 정량화 → design-loop SKILL 에 절차 박제.
3. **Phase 2** — 게이트 D 5종을 `scripts/diagnose.py` 가드로 구현 + §2 카탈로그 등록.
4. **Phase 3** — Style Dictionary v5+ 채택 평가(`build_tokens.py` 정렬 vs 대체) + 복제본 빌드 CLI.
5. **게이트**: 고객(특히 legal) 인도물에 게이트 D 전부 PASS 전까지 클라우드 워크벤치는
   **무명 디자인 자산 전용**. BAA beta 졸업(C2) 재검증 전까지 PII 절대 금지.
