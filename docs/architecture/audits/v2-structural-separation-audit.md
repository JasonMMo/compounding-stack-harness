# Design-Cloud Bridge v2 구조적 분리 감사

**감사일**: 2026-06-27
**대상 커밋 (main)**: 3a8fe84 (master HEAD)
**대상 레포**: `compounding-stack-harness` (main) + `harness-design-system` (sibling)
**감사자**: CQO (qa-agent)
**설계 근거**: `docs/architecture/design-cloud-bridge-v2-structural.md`, `components/CONTRACT.md`

---

## 최종 Verdict

**BLOCK**

사유: 항목 4 — `preflight_sibling.py` 가 exit 1 (false positive지만 게이트 FAIL). `.design-sync/` 가 `_SKIP_DIRS` 에서 누락.

---

## 7항목 PASS/FAIL 요약

| # | 항목 | 판정 | 핵심 근거 |
|---|---|---|---|
| 1 | G-21 게이트 정확성 + 적대적 확인 | **PASS** | `python scripts/diagnose.py G-21` → PASS. 도메인 어휘 전 항목 BLOCK, chrome/마커/allowlist 항목 오탐 0 |
| 2 | 셸 리팩터 완전성 — 도메인 잔재 0 | **PASS** | `components/*/index.html` 전 5개 파일 + styles.css + contract.json 도메인 어휘 0. `reference/` 와 `.design-sync/` 는 별개(하단 주석 참조) |
| 3 | corpus 중립성 (`fixtures/synthetic.json`) | **PASS** | 법무/의료/금융 어휘 0 (rule 메타주석 내 언급은 콘텐츠 아님). 한국어 중립 더미 구성 확인 |
| 4 | preflight 양 게이트 (exit 0) | **FAIL** | `python scripts/design/preflight_sibling.py` exit 1. `.design-sync/NOTES.md` 32~33줄이 FORBIDDEN_PATTERNS `legal`/`\bprecedent\b`/`판례` 를 본문에 *언급* (scrub 절차 기술 메타 문서). `_SKIP_DIRS` 에 `.design-sync` 누락이 원인 |
| 5 | WP-D normalize 구조추출 | **PASS** | `normalize.py ../harness-design-system/components/chip` → 슬롯 12개, BEM variant 6개 정상 추출, 주석 노이즈 없음 |
| 6 | 렌더 무결성 (`render-showcase.mjs`) | **PASS** | 5컴포넌트 렌더 완료, 미해결 마커 WARN 0 |
| 7 | denylist 2차망 보존 + learn-log | **PASS** | `export_system.py` FORBIDDEN_PATTERNS 24종 intact, 역할 재정의 주석("1차→2차 안전망") 존재. `learn-log.md §2` G-21 행 존재(line 60), `§4 카운터 22` 행 존재(line 95) |

---

## 발견된 결함

### DEFECT-1 (BLOCK 사유): preflight_sibling.py — `.design-sync` skip 누락

**위치**: `scripts/design/preflight_sibling.py` `_SKIP_DIRS`

**현상**: `preflight_sibling.py` 실행 시 exit 1.
```
[LEAK] .design-sync\NOTES.md:32  ← 패턴 'legal'
[LEAK] .design-sync\NOTES.md:32  ← 패턴 '\bprecedent\b'
[LEAK] .design-sync\NOTES.md:33  ← 패턴 'legal'
[LEAK] .design-sync\NOTES.md:33  ← 패턴 '판례'
```

**원인 분석**: `.design-sync/NOTES.md` §0 anonymization 섹션(line 32~33)이 이전 scrub 작업을 *기술*하는 메타 문서("source-precedent→source-reference 로 스크럽했다", "계약 해지/위약금/판례 를 중립 placeholder 로 교체했다"). 해당 파일은 claude.ai/design 으로 내보내는 산출물이 아니며, cloud 연결 경로 밖의 dev 노트다. 그러나 `_SKIP_DIRS` 가 `.ds-sync`(빌드 인프라) 만 포함하고 `.design-sync`(설계 노트·캐시) 를 누락해 스캔 대상에 포함된다.

**False positive 여부**: YES — `.design-sync/NOTES.md` 는 cloud export 경로 밖(dev-only). 그러나 게이트가 false positive 를 내는 것은 설계 결함이다. 가드 침묵 금지 원칙상 false FAIL 도 수정 대상.

**수정 방향**: `_SKIP_DIRS` 에 `".design-sync"` 추가. 단, `.design-sync/.cache/` 같은 하위 디렉터리는 이미 gitignore 대상이므로 부모 디렉터리 전체 skip 이 안전하다. 대안으로, `NOTES.md` 에서 실제 도메인 용어를 backtick 코드블록 안에만 두는 방식도 가능하나, skip 디렉터리 추가가 더 구조적.

**수정 범위**: `scripts/design/preflight_sibling.py` 1줄.

---

### 관찰 사항 (BLOCK 아님, 추후 검토 권장)

**OBS-1**: `reference/showcase.html` (sibling) 에 도메인 어휘 다수 존재 (`계약 해지`, `위약금`, `임대차`, `불법행위`, `과실`, `주식회사 가나다` 등 22줄). 이 파일은 `.gitignore` 대상이 아니며 정적으로 커밋된 파일이다. G-21 스캔 범위 (`components/*/index.html`) 에는 포함되지 않고, preflight `.design-sync` skip 수정 후에도 `reference/` 는 스캔 대상으로 남는다. `reference/showcase.html` 이 cloud 업로드 경로에 포함되지 않음을 설계 문서에 명시하거나, `_SKIP_DIRS` 에 `"reference"` 를 추가하는 것을 권장.

**OBS-2**: `drawer/index.html` 의 `aria-label="닫기"` 와 `원문 보기 (drawer 열기)` 는 `_structural-allowlist.txt` 에 정확히 포함되어 있어 G-21 통과하나, allowlist 에 없는 새 버튼 텍스트가 추가될 때 BLOCK 됨을 주의. 현재 닫힌 집합이 12개로 관리 가능한 수준.

---

## 재현 명령

```bash
# 항목 1 — G-21 게이트
PYTHONIOENCODING=utf-8 python scripts/diagnose.py G-21

# 항목 4 — preflight (현재 FAIL)
cd D:\AI\workspace\compounding-stack-harness && PYTHONIOENCODING=utf-8 python scripts/design/preflight_sibling.py

# 항목 5 — normalize
cd D:\AI\workspace\compounding-stack-harness && PYTHONIOENCODING=utf-8 python scripts/design/normalize.py ../harness-design-system/components/chip

# 항목 6 — render-showcase
cd D:\AI\workspace\harness-design-system && node scripts/render-showcase.mjs
```

---

## 수정 전 MERGE 불가

DEFECT-1 해소 후 재감사 필요:
1. `scripts/design/preflight_sibling.py` `_SKIP_DIRS` 에 `".design-sync"` 추가
2. `python scripts/design/preflight_sibling.py` exit 0 확인
3. OBS-1 (`reference/showcase.html` 처리 방침) 명시 또는 skip 추가

---

## CTO 검증 부록 (2026-06-27, [[subagent-cross-service-verify]] 적용)

QA 1차 보고의 판정을 CTO 독립 소스검증으로 정정한다. **QA가 두 건의 누출 심각도를 과소평가했고, DEFECT-1 의 수정안은 누출을 *숨기는* 오판이었다.**

### 정정 1 — DEFECT-1 은 false positive 가 아니라 TRUE POSITIVE
- QA 제안: `preflight _SKIP_DIRS` 에 `.design-sync` 추가(스캔 제외).
- 검증: `git ls-files` 로 `.design-sync/NOTES.md` 가 **tracked** 확인 → cloud 연결=GitHub 레포 전체 노출이므로 이 파일은 cloud-노출. NOTES.md §0 가 스크럽 이력 prose 로 금지어(`legal`/`precedent`/`판례`/`계약 해지/위약금`)를 **재나열**(self-leak 안티패턴 재발).
- 올바른 수정: skip 이 아니라 **prose 카테고리화**(`2e68e04`). 금지어를 명명하지 않고 "vertical-specific terms genericized" 로 기술.

### 정정 2 — OBS-1(showcase.html) 은 권장이 아니라 BLOCK 급 누출
- `reference/showcase.html`(tracked, cloud-노출)이 구 legal 컴포넌트 마크업을 **inline 복제**(계약 해지/위약금/임대차/주식회사 가나다 23줄). denylist 에 그 용어가 없어 preflight 통과 = **denylist 맹점의 실증**(v2 thesis 그대로).
- 수정: 콘텐츠-프리 iframe 갤러리로 교체(`ad41ded`), G-21 을 `reference/*.html` 까지 확대해 이 사각 영구 차단(`bb7b0f1`).

### 교훈
- 서브에이전트의 "false positive" 자기판정은 **노출 모델(tracked=cloud-노출)을 먼저 확인**하고 신뢰. 가드 FAIL 을 끄기 전에 그 FAIL 이 진짜 누출을 가리키는지 검증.
- denylist 가 통과시킨 것 ≠ 안전. allowlist conformance(G-21)를 cloud-노출 HTML **전수**로 확대하는 것이 근본 해법.

### 최종 상태 (CTO 재검증)
- G-21 PASS (components 5 + showcase, chrome allowlist 19종).
- preflight 양 게이트 CLEAN, exit 0.
- sibling **전체 tracked 트리** broad 도메인 스윕(denylist 맹점 용어 포함) = **0 잔재**.
- **최종 Verdict: MERGE-OK** (DEFECT-1·OBS-1 해소 후).
