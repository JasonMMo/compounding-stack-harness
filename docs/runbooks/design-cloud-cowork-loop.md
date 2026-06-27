# Design × Cloud Co-work Loop Runbook

> 단일 진실: CTO 인격이 유지 (경계·게이트 choke point 책임). 변경 시 커밋 + `learn-log.md §6` rollup.
> 설계 근거: [`docs/architecture/design-cloud-bridge-v2-structural.md`](../architecture/design-cloud-bridge-v2-structural.md) (구조분리 v2).
> 적용 대상: 별채 `harness-design-system` ↔ 본채 `compounding-stack-harness` ↔ `claude.ai/design` 3자 협업.

별채 디자인 작업을 클라우드(claude.ai/design)에 위임하면서 **데이터 누출 0** 으로 주고받는 반복 절차.
한 번의 협업 사이클 = ①~⑦. design-sync 는 ④ 게이트 뒤에만 오는 **업로드(로컬→클라우드)** 동작이다.

## 경계 (절대 불변)

| | 레포 | 클라우드 연결 | 담는 것 |
|---|---|---|---|
| **본채** | `compounding-stack-harness` | ❌ 절대 금지 | profiles·legal seed·DSN·실 고객 데이터 |
| **별채** | `harness-design-system` (sibling) | ✅ 여기만 | 슬롯 템플릿 + 중립 더미(`fixtures/synthetic.json`) + 토큰 (구조적 도메인-프리) |

> 클라우드 연결 = **GitHub 레포 전체 노출** (git-tracked 전부, `/design-sync` 한 컴포넌트만 아님).
> 그래서 별채엔 도메인 텍스트가 *구조적으로* 존재할 수 없게 만들어 둠 (셸=슬롯만).

## 두 세션의 역할 분담

| 액터 | cwd | 담당 단계 | 못 하는 것 |
|---|---|---|---|
| **design_work_0625** (별채 로컬 CLI) | 별채 | ② 슬롯 작성·synthetic.json·allowlist, ③ 로컬 렌더 | ④ 게이트 (스크립트가 본채에만 있음) → "푸시 안전" 판정 불가 |
| **CTO** (본채 메인 세션, 이 세션) | 본채 | ① 토큰 export, ④ preflight 게이트, ⑤ 별채 push, ⑦ 본채 환류 | — |
| **claude.ai/design** (클라우드 웹툴) | 클라우드 | ⑥ 비주얼 디자인 (founder) | 게이트 미통과분은 받지 않음 |

> design_work_0625(로컬 CLI) ≠ claude.ai/design(클라우드 웹). 전자가 슬롯작업, 후자가 비주얼 디자인. design-sync 가 둘 사이 다리.

## 협업 루프 (한 사이클)

### ① 본채 → 별채: 토큰 export *(토큰이 바뀐 경우만)*
```bash
# 본채 루트
python scripts/design/export_system.py --target ../harness-design-system
```
컴포넌트 구조만 손볼 거면 skip.

### ② 별채에서 셸 작성/수정 — **슬롯만** *(design_work_0625)*
- `components/<name>/index.html` 의 모든 가시 텍스트 = `{{slot}}` 마커.
- 더미 값은 `fixtures/synthetic.json` 에만 (중립 한국어).
- a11y 라벨·버튼 chrome 리터럴은 `components/_structural-allowlist.txt` 에 1줄 추가 후 사용.
- **도메인 콘텐츠(제목·본문·질의·실데이터)는 셸에 리터럴 금지 → 무조건 슬롯.**
- ⚠ **design-sync 는 여기서 하지 않는다.** ②는 순수 로컬 편집. sync(업로드)는 ④ 게이트 뒤(⑤ 직후).

### ③ 로컬 렌더 확인 *(design_work_0625)*
```bash
# 별채
node scripts/render-showcase.mjs   # reference/rendered/<c>.html + showcase.html 갤러리
```
끝나면 baton 에 `READY-FOR-GATE` 기록. **푸시·sync 하지 않음** (CTO 게이트 대기).

### ④ 누출 게이트 — **필수, push/sync 전 무조건** *(CTO)*
```bash
# 본채 루트
python scripts/design/preflight_sibling.py
```
- **1차 G-21 conformance (allowlist)**: 셸 텍스트노드가 `{{마커}}` 또는 allowlist 정확일치인지. 한 줄이라도 도메인어 잔존 = **BLOCK**.
- **2차 denylist**: 알려진 고위험 식별자 보강 스캔.
- 출력 `CLEAN — /design-sync 연결 안전` 이어야만 진행. FAIL = baton 에 `GATE-FAIL — <위반 줄>` 기록, ②로 반려.

### ⑤ 별채 커밋 → push *(CTO — 단일 choke point)*
- 게이트 PASS 후에만. 파일당 별도 커밋, Fable 5 trailer, `--no-verify` 금지.
- push 해야 GitHub=클라우드에 반영. baton 에 `GATE-PASS — sync 안전` 기록.

### ⑥ claude.ai/design 에서 디자인 *(founder)*
- 게이트 green 상태에서 **design-sync 1회** (로컬 별채 → 클라우드 업로드). = 미결인 `34c4c9d7` 삭제→클린 재sync 동작과 동일.
- 클라우드가 별채를 sync → 드래그 가능한 React 래퍼 + 토큰/클래스로 비주얼 디자인.
- 결과 구조 변경분을 별채로 내려 ②부터 반복.

### ⑦ 별채 → 본채 환류 *(CTO — 디자인 확정 후)*
- 확정 토큰/패턴을 본채 `design/tokens/` 단일진실에 반영.
- 셸 구조를 본채 어댑터(screen-manifest 주입형, `{{ field.label }}`)에 매핑 — 실 라벨은 build-time manifest 가 주입. 클라우드엔 라벨이 없고 본채에서만 결합.

## Baton 핸드오프

별채 안 **gitignored**(=클라우드 비노출) 파일로 양쪽이 번갈아 기록:
```
harness-design-system/.handoff/baton.md
```
| 상태 | 쓰는 주체 | 의미 |
|---|---|---|
| `READY-FOR-GATE` | design_work_0625 | ②③ 끝, 게이트 요청 (푸시 안 함) |
| `GATE-PASS` | CTO | 게이트 통과·push 완료, sync 안전 |
| `GATE-FAIL` | CTO | 위반 줄 명시, ②로 반려 |

founder 가 한쪽 세션에 "baton 확인" 한 마디로 각 턴 트리거.

## 황금률

1. **본채는 클라우드에 연결하지 않는다.** 클론 한 번 = profiles·legal·DSN 노출.
2. **셸엔 슬롯만, 더미는 synthetic.json, chrome 는 allowlist.** 셋 다 안 맞는 텍스트 = push 금지 신호.
3. **push/sync 전 항상 `preflight_sibling.py` green.** 게이트 FAIL 을 끄지 말 것 — FAIL 은 실누출을 가리킨다 (tracked=cloud 노출모델 먼저 확인). design-sync 는 게이트 *뒤*에만.
