# CQO 감사 — WP-3 고객 복제본 빌더 (build_replica.py)

**감사일**: 2026-06-27
**대상 커밋**: 5a41bf5 (master HEAD)
**감사자**: CQO (QA agent)
**비고**: 원본 audit 파일은 gitignored `out/` 에 작성돼 소멸. 현행 master 코드·테스트를 직접 실행하여 동등 감사를 재생성한 문서임.

---

## Dimension 1 — 빌더 존재·구조

**판정: PASS**

`scripts/design/build_replica.py` 실재 확인 (11.9K). 4단계 파이프라인이 독립 함수로 구현됨:

| 단계 | 함수 | 위치 |
|---|---|---|
| scaffold | `run_scaffold(slug, out_root)` | build_replica.py:79 |
| astro build | `run_astro_build(adapter_dir, manifest)` | build_replica.py:95 |
| isolate | `isolate_bundle(source_dist, slug, replica_root)` | build_replica.py:119 |
| leak gate | `verify_no_leak(replica_root, slug, ...)` | build_replica.py:132 |

오케스트레이터 `build_replica(slug, ...)` (L175)가 4단계를 순서 보장하여 호출. CLI `main()` (L223)은 argparse로 노출.

`--skip-astro-build` 플래그(L199)로 node_modules 없는 환경에서도 격리·누출게이트만 재실행 가능 — CI 환경 분리 설계 의도 확인.

---

## Dimension 2 — 누출 3종 게이트 실효성

**판정: PASS (한계 1건 명시 기록)**

`verify_no_leak` (build_replica.py:132)는 `diagnose.py`의 단일 진실 가드를 재사용(재구현 금지 원칙 준수):

### G-17 클라우드 결합 (build_replica.py:152)
- `diagnose.g17_cloud_coupling_leak(scan_roots=(bundle,))` 호출
- 탐지 토큰: `"claude.ai/design"`, `"claude.ai"`, `"DesignSync"`, `"/design-sync"` (diagnose.py:1542~1544)
- 대소문자 변형 탐지: 전체 텍스트 `.lower()` 후 토큰 lower와 비교 (diagnose.py:1657)
- 스캔 대상: `_CODE_SUFFIXES` — `.md`/`.yaml` 제외로 문서 내 정당한 언급과 구분
- **false-PASS 위험**: 바이너리 에셋(.png/.woff2) 내 텍스트 토큰은 탐지 불가. build_replica.py:142에 한계로 명시.

### G-18 교차 테넌트 slug (build_replica.py:157)
- `diagnose.g18_cross_tenant_leak(replica_root=replica_root, ...)` 호출
- known slug = profiles/*.yaml stem + infra/registry/cases/*.yaml stem + 현존 번들 디렉터리명 합집합 (diagnose.py:1698~1712)
- 토큰 경계 매칭: `(?<![A-Za-z0-9_-]){slug}(?![A-Za-z0-9_-])` 패턴으로 부분문자열 오탐 방지 (diagnose.py:1710)
- **false-PASS 위험 (QA 판정)**: 단일 번들만 빌드된 상태에서는 foreign slug set이 비어 G-18이 사실상 비활성(거짓음성). build_replica.py:140~144에 명시적 한계로 기록. M2+ 복수 고객 빌드 시 재검토 대상. 이 한계는 침묵이 아닌 **explicit 문서화**로 처리됨 — QA 기준: acceptable.

### PII / 시크릿 경로 참조 (build_replica.py:163)
- `diagnose._PII_PATTERNS` (이메일·RRN·API키 등) + `diagnose._FORBIDDEN_PATH_REFS` (apps/intake/data 등 내부 경로)
- 대상 파일: `_TEXTY_SUFFIXES` (코드 + .yaml + .md + .txt)
- 이 번들(`replica_root/slug`)만 스캔 — 타 번들 혼입 방지

---

## Dimension 3 — open-closed 준수

**판정: PASS**

새 고객/테마 추가가 `build_replica.py` 코드 변경 없이 가능한 경로 확인:

1. **프로파일 주입**: `load_profile(slug)` (L58)은 `profiles/<slug>.yaml` 읽기만. 신규 고객은 yaml 추가로 완결.
2. **테마 주입**: 프로파일의 `site.theme` 키 → `scaffold.py` 경유 → `landing-astro` 어댑터의 `build-tokens.mjs`가 `presets/themes/<slug>/theme.yaml` 소비. `build_replica.py`는 테마 이름을 코드에 박지 않음.
3. **adapter 주입**: `--adapter-dir` CLI 인자로 override 가능 (L229). 기본값 `frontend/adapters/landing-astro`.
4. **deliverable_kind 가드**: `_deliverable_kind(profile) != "marketing-site"` 시 명시적 `ReplicaError` (L192~195) — 침묵 대신 명시적 실패. business-system 프로파일 보호.

`hopwell.yaml`(profiles/ 실재 확인): `stack.deliverable_kind=marketing-site`, `site.theme=harvest` — 기존 harvest 테마(`presets/themes/harvest/theme.yaml` 실재 확인)를 별도 코드 변경 없이 소비하는 구조 확인.

---

## Dimension 4 — 테스트 정합

**판정: PASS — 30 passed, 메모와 일치**

```
python -m pytest tests/design/test_build_replica.py \
                 tests/design/test_bridge_guards.py \
                 tests/design/test_bridge_skeleton.py -v
결과: 30 passed (rc=0)
```

| 파일 | 커버 대상 | 주요 케이스 |
|---|---|---|
| test_build_replica.py | isolate_bundle, verify_no_leak | G-17/G-18/PII 각 PASS·FAIL·경계 케이스 |
| test_bridge_guards.py | G-16~G-20 diagnose 가드 | SPEC/PASS/FAIL 세 경로 각 1종 이상 |
| test_bridge_skeleton.py | normalize.extract_candidates, dtcg_schema | 색·폰트·간격 추출, 키 화이트리스트 검증 |

`test_build_replica.py`는 외부 단계(scaffold/npm) 없이 픽스처 dist로 격리 복제·누출 게이트만 결정적으로 검증 — CI 결정론 확보. 실제 astro 빌드는 production Dockerfile 경로로 분리.

`test_bridge_guards.py:TestG18CrossTenant::test_pass_own_slug_only` — 각 테넌트 번들에 자기 slug만 있을 때 PASS, 타 slug 포함 시 FAIL 명확히 검증됨.

---

## Dimension 5 — 실증 재현성 (hopwell/harvest 109파일·누출0)

**판정: PARTIAL — 코드/픽스처로 뒷받침, dry-run은 node_modules 부재로 미실행**

learn-log.md:90 WP-3 행 기록:
> "G-18 SPEC→PASS 활성 (hopwell/harvest 실증 109파일 번들, 누출 0)"

정적 근거:
- `profiles/hopwell.yaml` 실재 (deliverable_kind=marketing-site, theme=harvest)
- `presets/themes/harvest/theme.yaml` 실재 (10.8K)
- G-18 SPEC→PASS 전환은 WP-2 시점(G-18=SPEC, replica root 부재)에서 WP-3 빌드 실행 후 활성화됨을 learn-log.md:89→90 행 전환 기록으로 추적 가능

109파일 수치: `out/replicas/` 는 `.gitignore` 대상이므로 현행 master에 산출물 없음. 수치는 당시 실행 결과이며 코드 기반 건식 재현 불가. 단 `build_replica.py:209`의 `file_count = sum(1 for _ in bundle.rglob("*") if _.is_file())` 로직이 정확하고, landing-astro Astro SSG 빌드 산출물 규모(100+ 파일)는 테마 복잡도와 일치. **QA 판단: 수치 자체는 검증 불가하나 코드 로직·픽스처 구조는 신뢰 가능.**

---

## 발견사항 (Findings)

| 번호 | 구분 | 내용 | 위험도 | 처리 |
|---|---|---|---|---|
| F-1 | 한계 | G-18은 단일 번들 환경에서 거짓음성 — foreign slug set 비어 비활성 | LOW | build_replica.py:140 명시적 문서화, M2+ 재검토 예약. 침묵 아님 — acceptable |
| F-2 | 한계 | 바이너리 에셋(.png/.woff2) 내 텍스트 토큰 탐지 불가 | LOW | build_replica.py:142 명시. 정적 SSG 번들에서 바이너리 내 cloud 토큰 삽입 경로 비현실적 |
| F-3 | 정보 | G-18 SPEC→PASS 전환 근거가 gitignored 산출물에만 존재 | INFO | learn-log.md:90 기록으로 추적 가능. 재현 시 `--skip-astro-build` + dist 픽스처로 재현 가능 |

신규 BLOCK 사항 없음.

---

## 최종 판정

**MERGE-OK**

4단계 파이프라인 구현 확인, 누출 3종 게이트 diagnose 단일 진실 재사용, open-closed 구조 확인, 테스트 30 passed (메모와 일치), hopwell/harvest 실증 정적 근거 충분. F-1/F-2 한계는 코드 내 명시적 문서화로 처리됨 — 침묵 아닌 explicit 한계 선언은 QA 기준 acceptable.
