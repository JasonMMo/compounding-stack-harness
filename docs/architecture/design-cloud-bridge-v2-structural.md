# Design Layer ↔ claude.ai/design 안전 코웍 — 구조적 분리 아키텍처 (v2)

> CTO 컨설팅 리포트 (Growth-130 후속, 2026-06-27). "외부 컨설팅 의뢰" 관점의 자기진단.
> v1 설계([`design-cloud-bridge.md`](design-cloud-bridge.md))를 **부정하지 않고 승격**한다 —
> v1 의 *절차적* 누출 게이트를 *구조적* 도메인-프리로 끌어올려, UI 레이어 작업을
> claude.ai/design 에 마찰 없이 위임 가능하게 만드는 것이 목표.
> 근거: 두-레포 cross-mapping (wire-contract / screen-manifest / sibling shell / bridge tooling)
> + Growth-130 누출 사고 사후분석.

---

## 0. Executive Summary

**진단.** 현 브리지는 누출 방지를 **절차(procedure)** — 스크럽 + denylist 스캔 + 매 반복 PII 검토 —
에 의존한다. 절차에 의존할 수밖에 없는 진짜 이유는, 디자인 sibling 레포의 컴포넌트가
**도메인 텍스트를 마크업에 inline 하드코딩**하고 있어 "구조적으로 도메인-프리"가 아니기
때문이다. 이 단일 결함이 두 증상의 공통 근본 원인이다:

1. **마찰** — pricing 섹션 하나 손보는 데 4개의 수동 게이트/왕복 (업로드 전 PII 확인 → 수동
   download/배치 → normalize 판단 → CI 가드). 매 *반복마다* 반복된다.
2. **누출** — denylist(`FORBIDDEN_PATTERNS`)가 미래 도메인 용어를 열거할 수 없어, 익명 셸에
   잔존한 `판례/대법원/손해배상`을 못 잡고 cloud 업로드 (`79206fa` 사고).

**역설.** 우리는 **이미 정답을 갖고 있다.** business-system 경로는 같은 문제를 이미 풀었다:

| 레이어 | 프레젠테이션 텍스트가 사는 곳 | 도메인-프리? |
|---|---|---|
| `middle/contract/wire-v1.yaml` | **없음** (라벨/display 필드 0개, 순수 데이터 스키마) | ✅ 구조적 |
| `screen-manifest.json` | 빌드타임에 profile+catalog → manifest 주입 | ✅ 빌드 경계 |
| `frontend/adapters/vanilla-htmx` `create.html:43` | `{{ field.label }}` — manifest 읽기만, 하드코딩 0 | ✅ 구조적 |
| **`harness-design-system/components/*/index.html`** | **마크업에 inline 하드코딩** (`"위약금 산정 기준 (예시)"` 등) | ❌ **퇴행** |

디자인 sibling 레포만 검증된 내부 패턴(manifest 주입)을 안 따르고 inline 하드코딩으로
퇴행했다. **처방은 새 발명이 아니라, 우리가 이미 증명한 분리 패턴을 디자인 레이어에 확장하는 것.**

**처방.** 디자인 컴포넌트를 **props/slot 구동 셸 + 합성 fixtures**로 리팩터해, 도메인 텍스트가
**구조적으로 들어갈 수 없게** 만든다. 그 결과:

- 누출 방지가 **절차 → 구조**로 이동한다. denylist 는 1차 게이트 → **2차 안전망**으로 강등.
- 1차 게이트가 **denylist → allowlist(conformance)**로 바뀐다. "셸의 모든 텍스트 노드는 slot
  placeholder 이거나 합성 corpus 출처여야 한다." allowlist 는 *미래 용어 열거 불가능성* 문제가
  **원천적으로 없다** — 판례 사고의 재발 클래스를 구조로 차단.
- 경계를 **토큰 JSON only → 컴포넌트 구조(마크업+CSS)까지** 안전하게 확대 가능. 셸이
  도메인-프리라 누출할 게 없으므로, cloud craft 산출물(레이아웃·인터랙션)을 자유롭게 받는다.
  이것이 v1 의 "axis-8 밋밋함"(고정 variants) 까지 함께 푼다.

---

## 1. 진단 — 왜 현재는 위임이 어려운가

### 1.1 마찰: 채널이 없어서 안전하지만, 채널이 없어서 느리다

claude.ai/design 은 BAA 제외·학습 기본 서비스다. v1 은 cloud↔repo 사이에 **자동 양방향 채널을
일절 두지 않는** 결정(authoring-only 물리격리)으로 안전을 확보했다. 대가는 마찰이다 — 매
반복마다 사람이 (a) 업로드 전 무명성 확인, (b) 수동 download → `staging/design-sync/` 배치,
(c) `normalize.py` 토큰/variant 판단, (d) CI 가드 통과를 거친다. **누출 방지가 per-iteration
비용**이라 디자인 *사고*가 아니라 *왕복*이 시간을 먹는다.

### 1.2 누출: denylist 의 구조적 한계

`FORBIDDEN_PATTERNS`(현 24종)는 **denylist**다. denylist 는 "알려진 나쁜 것"만 막는다. 새
도메인(의료/제조/금융)을 태울 때마다 그 도메인의 용어를 *미리* 열거해야 하는데, 이는 원리적으로
불가능하다(개방형 집합). Growth-130 누출이 정확히 이 실패 모드였다 — 15패턴 preflight 가
`판례/대법원/precedent` 를 포함 안 해 통과시켰다. 패턴을 24종으로 늘렸지만 **다음 도메인에서
같은 클래스의 사고가 재발할 구조는 그대로**다.

### 1.3 경계가 좁아서 디자인 작업이 새어나간다

v1 경계는 "넘어오는 건 DTCG 토큰 JSON 뿐". 그런데 디자인 *반복*은 색·간격(토큰)만이 아니라
**컴포넌트 구조·레이아웃·인터랙션**을 만지는 일이다. 토큰만 경계로 허용하면, 정작 craft 의
본질(레이아웃)은 경계 밖이라 **컴포넌트 HTML 안에서 도메인과 함께 섞여** 왕복한다. 좁은 경계가
오히려 inline 하드코딩을 강제하고, 그것이 1.2 의 누출 표면이 된다.

---

## 2. 근본 원인 — UI 티어 내부 분리 원칙 위반

3-tier 의 핵심은 **표현(presentation)과 콘텐츠(content)의 분리**다. business-system 경로는 이를
지킨다(§0 표). 디자인 sibling 만 위반한다: 컴포넌트 = 표현 + 콘텐츠가 한 파일에 융합. 따라서

> 누출 방지를 *절차*에 의존할 수밖에 없는 이유 = 컴포넌트가 *구조적으로* 콘텐츠를 품고 있어서.

분리가 구조로 보장되면, 누출 방지도 절차가 아니라 구조가 된다. **근본 원인 하나를 고치면 마찰과
누출이 동시에 풀린다.**

---

## 3. 목표 아키텍처 — UI 티어를 프랙탈하게 3-sublayer 로

전체 시스템이 3-tier(F / Middle / B)이듯, **UI 티어 내부도 동형으로 3겹**으로 가른다:

```
┌─ Shell layer (CLOUD-SAFE) ─────────── claude.ai/design 위임 대상 ─────────┐
│  순수 컴포넌트: 마크업 + 토큰(var) + 위젯로직 + slot 선언                  │
│  보이는 텍스트 = 전부 합성 fixtures(lorem/중립 corpus) 또는 {{slot}}       │
│  도메인 어휘 0 — 구조적으로 들어갈 수 없음                                 │
└────────────────────────────┬──────────────────────────────────────────────┘
                             │  prop/slot schema  (= 디자인의 wire-contract)
┌─ Binding layer (PRIVATE) ──┴──── main 레포, 절대 cloud 미도달 ─────────────┐
│  screen-manifest 메커니즘 재사용: profile+catalog → 실 라벨/데이터 주입     │
│  Shell 의 slot 에 빌드타임에 도메인 콘텐츠를 채움                          │
└────────────────────────────┬──────────────────────────────────────────────┘
                             │  wire-v1.yaml  (이미 도메인-프리)
┌─ Data layer (PRIVATE) ─────┴──── backend + contract ──────────────────────┐
│  순수 데이터 스키마. 라벨 없음. (이미 §0 표대로 구조적 도메인-프리)        │
└────────────────────────────────────────────────────────────────────────────┘
```

**Shell ↔ Binding 계약 = prop/slot schema.** 이것이 F/B 의 wire-contract 와 정확히 같은 역할을
디자인 레이어에서 한다 — Shell 은 "나는 `title`, `excerpt`, `score`, `source_kind` slot 이
필요하다"를 *선언*하고, Binding(manifest)이 빌드타임에 *실값*을 채운다. **cloud 는 slot 선언과
합성 fixtures 만 본다. 실값은 main 레포 빌드에서만 결합된다.**

핵심: 이건 이미 `create.html` 의 `{{ field.label }}` 이 하는 일이다. 그 패턴을 **선언적 컴포넌트
계약**으로 격상해 디자인 sibling 에 적용할 뿐.

---

## 4. 패러다임 전환 — 누출 방지: denylist → 구조 + allowlist

| | v1 (현재) | v2 (목표) |
|---|---|---|
| 1차 게이트 | denylist 스캔 (`FORBIDDEN_PATTERNS`) | **conformance(allowlist)**: 셸 텍스트 노드 = slot \| 합성 corpus |
| 실패 모드 | 미래 용어 열거 불가 → 누출 통과 | 없음 (개방형 집합 문제가 구조적으로 소거됨) |
| denylist 역할 | 1차 (유일) | **2차 안전망** (defense-in-depth, 그대로 유지) |
| 누출 방지 비용 | per-iteration (매 sync) | **one-time** (셸 conformance, design-time) |
| 새 도메인 추가 | 패턴 N종 추가 필요 | **무변경** (셸은 도메인 불문) |

**Conformance gate (신규 G-21 후보):** 셸 컴포넌트의 모든 텍스트 노드를 AST/템플릿 파싱해,
(a) `{{slot}}` placeholder 이거나 (b) `fixtures/synthetic.json` corpus 에 존재하는 문자열이 아니면
**BLOCK**. 하드코딩된 임의 문자열 = 위반. 이로써 "익명이라 믿었는데 도메인이 잔존" 사고가
구조적으로 불가능해진다 (셸에는 합성 corpus 외 문자열이 존재할 수 없음).

---

## 5. 마찰 감소 — Before / After

| 단계 | v1 | v2 |
|---|---|---|
| 업로드 전 무명성 확인 | 매 반복 사람 판단 | **one-time 셸 conformance** (셸이 영구 도메인-프리) |
| download → staging 배치 | 매 반복 수동 | 유지 (cloud API 부재는 외부 제약) — 단 스크럽 불필요 |
| 스크럽 (도메인 텍스트 제거) | **매 반복 필수** | **소거** (셸에 도메인 텍스트가 애초에 없음) |
| normalize 토큰/variant 판단 | 매 반복 | 유지 — 단 경계 확대로 컴포넌트 구조도 수용 |
| 경계 | 토큰 JSON only | + 컴포넌트 마크업/CSS (셸이 안전하므로) |

순효과: **누출 방지를 위한 per-iteration 노동이 0 에 수렴**. 남는 왕복은 cloud 가 로컬 파일
쓰기를 못 하는 외부 제약(수동 download) 하나뿐이고, 이건 우리가 못 고치는 부분.

---

## 6. 마이그레이션 경로 (work packages)

> v1 산출물(export_system / preflight / dtcg_schema / build_replica / G-16~20)은 **전부 유지**.
> v2 는 그 위에 구조 분리를 얹는다. 파괴적 변경 없음.

- **WP-A — prop/slot schema 정의.** 디자인의 wire-contract. 각 셸이 받는 slot 을 선언적 JSON 으로
  (`harness-design-system/components/<c>/contract.json`). DTCG 와 별 스키마, 또는 DTCG 확장 — §7 결정.
- **WP-B — 5 셸 리팩터.** `index.html` 의 inline 도메인 텍스트 → `{{slot}}` + `fixtures/synthetic.json`
  (중립 lorem corpus). engineer + CDO. 이때 기존 스크럽본은 폐기하고 합성 corpus 로 재생성.
- **WP-C — conformance gate G-21.** `scripts/diagnose.py` 에 셸 텍스트-노드 allowlist 스캔 추가.
  §2 카탈로그 행 + §4 카운터 21→22. preflight 에도 연동(sync 직전 재실행).
- **WP-D — 경계 확대.** `normalize.py` 가 토큰뿐 아니라 컴포넌트 구조(마크업/CSS 변경)도 수용해
  catalog variant 로 분해. v1 "axis-8 밋밋함"의 실질 해법.
- **WP-E — denylist 재배치.** `FORBIDDEN_PATTERNS` 를 1차→2차 안전망으로 문서화(코드 변경 없음,
  역할 재정의). conformance 가 통과한 뒤 한 번 더 거르는 defense-in-depth.

권장 순서: A → B → C (여기까지가 누출/마찰 동시 해결의 최소셋) → D → E.

---

## 7. founder 결정 게이트 (열린 질문)

1. **합성 corpus 출처/언어.** lorem ipsum(라틴) vs 한국어 중립 더미("샘플 제목 1") vs 추상
   placeholder("{title}"). 디자인 충실도 ↔ 누출 안전 trade-off. **권장: 한국어 중립 더미** (실
   레이아웃 폭/줄바꿈을 보면서 craft 가능하되 도메인 0).
2. **prop schema 표현.** 별도 `contract.json` vs DTCG 확장. **권장: 별도** (DTCG 는 토큰 표준이지
   컴포넌트 계약 표준 아님 — C5 뉘앙스).
3. **경계 확대 범위.** 마크업까지만 vs CSS 까지 (WP-D). **권장: 마크업+scoped CSS** (Tailwind 혼용
   여부는 별도 CDO 컨벤션 판정 — v1 미결 항목 승계).
4. **착수 범위.** A~C 최소셋만(누출 재발 차단 + 마찰 제거)부터 vs A~E 일괄.

---

## 8. 한 줄 결론

> 누출 방지를 **막는 일**(denylist 스크럽)에서 **불가능하게 만드는 일**(구조적 도메인-프리)로
> 옮긴다. 그 방법은 새 발명이 아니라, business-system 이 이미 증명한 manifest-주입 분리를 디자인
> 레이어에 확장하는 것. 부수효과로 매-반복 마찰이 사라지고 경계가 넓어져 axis-8 craft 가 풀린다.
