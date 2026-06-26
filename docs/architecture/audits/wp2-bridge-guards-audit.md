# WP-2 Design-Cloud Bridge CI Guard Audit (G-16~G-20)

**감사일**: 2026-06-27
**대상 커밋**: 5a41bf5 (master HEAD)
**감사자**: CQO (qa-agent)
**비고**: 원본 audit 파일은 gitignored `out/` 에 존재했으며 소멸됨. 본 문서는 현재 master 코드를 직접 실행/검증해 재생성한 동등 감사본.

---

## Dimension 1 — 각 가드 존재·실행

**검증 방법**: `python scripts/diagnose.py --list` 출력 확인 + GUARDS registry 직접 판독 (diagnose.py:1824~1846)

| Guard | --list 등록 | GUARDS registry | 함수명 | 함수 위치 |
|---|---|---|---|---|
| G-16 | PASS | `g16_design_upload_scope` | diagnose.py:1582 | 확인 |
| G-17 | PASS | `g17_cloud_coupling_leak` | diagnose.py:1628 | 확인 |
| G-18 | PASS | `g18_cross_tenant_leak` | diagnose.py:1667 | 확인 |
| G-19 | PASS | `g19_dtcg_schema` | diagnose.py:1724 | 확인 |
| G-20 | PASS | `g20_normalization_gate` | diagnose.py:1784 | 확인 |

**rc**: 0 (--list 실행). 총 등록 가드 21개 (G-87 포함).

---

## Dimension 2 — PASS/SPEC 상태 정합

**검증 방법**: `python scripts/diagnose.py G-16,G-17,G-18,G-19,G-20` 직접 실행 + 코드 로직 대조

| Guard | 실행 상태 | 코드 SPEC 조건 | 정합 |
|---|---|---|---|
| G-16 | **SPEC** | staging/design-sync/ 미존재 또는 README 외 파일 없음 (diagnose.py:1595~1610) | 일치 — 디렉터리 존재하나 README만 있음 |
| G-17 | **PASS** | delivery 루트 1개 이상 존재 시 scan (diagnose.py:1643~1664) | 일치 — 3 root 존재, 34 파일 스캔, 위반 0 |
| G-18 | **SPEC** | out/replicas/ 미존재 (diagnose.py:1684~1689) | 일치 — WP-3 이전이므로 SPEC 정상 |
| G-19 | **SPEC** | *.tokens.json 없음 (diagnose.py:1758~1763) | 일치 — 아직 토큰 override 없음 |
| G-20 | **PASS** | production roots 존재 시 scan (diagnose.py:1797~1817) | 일치 — 15506 파일 스캔, provenance marker 0 |

이전 메모(G-17/G-20 PASS, 나머지 SPEC)와 현재 실행 결과 **완전 일치**.

---

## Dimension 3 — 카탈로그/카운터 정합

**검증 방법**: learn-log.md §2 + §4 직접 검색

**§2 카탈로그**: G-16~G-20 5행 존재 확인.

| Guard | §2 row | 함수 포인터 | 상태 기술 |
|---|---|---|---|
| G-16 | 존재 | `scripts/diagnose.py::g16_design_upload_scope` | SPEC (sync 전) |
| G-17 | 존재 | `scripts/diagnose.py::g17_cloud_coupling_leak` | PASS (clean repo 0위반) |
| G-18 | 존재 | `scripts/diagnose.py::g18_cross_tenant_leak` | SPEC (WP-3 전) |
| G-19 | 존재 | `scripts/diagnose.py::g19_dtcg_schema` | SPEC (tokens.json 없음) |
| G-20 | 존재 | `scripts/diagnose.py::g20_normalization_gate` | PASS (marker 0) |

**§4 카운터**:
- Growth-130 WP-1+WP-2 행: 카운터 **21** — "G-16~G-20 (5종 추가)" 명시
- 직전 Growth-93 행: 카운터 **16** (G-87 추가 후)
- 16 → 21 (+5) 전환 **정합** (16 + G-16~G-20 5개 = 21)

발견사항: learn-log §4에 G-87 추가 시점(Growth-93, 카운터 16)이 G-1~G-15(15개) + G-87 = 16인데, G-87이 87번이면서 16번째 가드임을 카운터가 수량 기반으로 관리하고 있음. 이는 의도된 설계(guard_id != 순번)로 QA 결함 아님.

---

## Dimension 4 — 누출 가드 실효성 (거짓 PASS 위험)

### G-17 cloud-coupling leak

스캔 대상: `out/replicas/`, `frontend/adapters/landing-astro/src`, `presets/themes`, `presets/site-sections` (diagnose.py:1552~1556).
금지 토큰: `claude.ai/design`, `claude.ai`, `DesignSync`, `/design-sync` (diagnose.py:1542~1544).
탐지 방식: 대소문자 무시 (`.lower()` 비교, diagnose.py:1655~1658).

**거짓 PASS 위험 평가**:
1. **문서/주석 제외**: `.md`/`.yaml` 제외 — `_CODE_SUFFIXES`만 스캔 (diagnose.py:1562). 정당한 아키텍처 문서의 `claude.ai` 언급은 오탐하지 않음.
2. **스캔 커버리지**: `out/replicas/`가 없을 때는 3 delivery root만 스캔. WP-3 replica 도입 후에는 자동 포함됨 (present = [r for r in roots if r.exists()]).
3. **토큰 누락 위험**: `claude-design` 등 변형 토큰은 현재 리스트에 없음. 그러나 설계 문서(docs/architecture/design-cloud-bridge.md)상 경계는 DTCG JSON 파일이며, 클라우드 도메인명 직접 삽입은 개발자 실수 시나리오 — 커버리지 충분.

**판정**: 거짓 PASS 위험 **낮음**. `.claude.ai`나 하이픈 변형은 미탐 가능성 있으나 realistic attack surface 아님.

### G-18 cross-tenant leak

slug 수집: `profiles/*.yaml` stem + `infra/registry/cases/*.yaml` stem + 번들 이름 (diagnose.py:1696~1702).
탐지: 단어 경계 regex `(?<![A-Za-z0-9_-]){slug}(?![A-Za-z0-9_-])` — 부분문자열 오탐 방지 (diagnose.py:1710).
최소 slug 길이 3자 이상만 검사 (diagnose.py:1707) — 2자 이하 slug 미탐 위험 있으나, 현재 프로파일 slug 체계상 2자 이하 slug는 없음 (G-8 ASCII slug 정책).

**판정**: 거짓 PASS 위험 **낮음**. SPEC 상태이므로 현재 실행 영향 없음; 활성화 후 단어 경계 로직은 표준적.

---

## Dimension 5 — 회귀 안전성 (clean repo 오탐 0 확인)

| Guard | clean repo 결과 | 오탐 여부 |
|---|---|---|
| G-16 | SPEC (내용물 없음) | 없음 |
| G-17 | PASS (34파일 스캔, 0 위반) | 없음 |
| G-18 | SPEC (out/replicas/ 없음) | 없음 |
| G-19 | SPEC (*.tokens.json 없음) | 없음 |
| G-20 | PASS (15506파일 스캔, 0 위반) | 없음 |

전체 rc=0. clean repo에서 FAIL을 내는 가드 없음.

---

## 발견사항

**D-1 (정보, BLOCK 아님)**: G-16의 PII 패턴에서 하이픈 없는 13자리 주민번호 형식(`\d{13}`)이 epoch-ms 타임스탬프와 충돌을 이유로 의도적 제외됨 (diagnose.py:1535~1536). 이 판단은 코드 주석에 명시되어 있으며 "(후속 재검토)" 표기. 현재로선 거짓양성 억제 우선이 타당하나, RRN 탐지 범위 제한을 QA 후속 모니터링 항목으로 등록.

**D-2 (정보, BLOCK 아님)**: G-17 스캔 시 `out/replicas/`가 없으면 해당 root skip하고 PASS 반환 (delivery 34파일 스캔). WP-3 replica 도입 후 G-17이 replica 번들도 추가 스캔하는 것이 설계 의도인데, `_BRIDGE_REPLICA_ROOT`가 `roots` tuple에 포함되어 있어 자동으로 스캔됨 — 문제 없음.

---

## 최종 판정

**MERGE-OK**

G-16~G-20 5개 가드가 모두 diagnose.py에 실재하고, GUARDS registry에 등록되어 있으며, --list/--json/직접 실행 모두 rc=0. 상태(SPEC/PASS)가 코드 로직 및 learn-log §2 기술과 일치. §4 카운터 16→21 전환 정합. 거짓 PASS 위험 낮음 (clean repo 오탐 0, 누출 탐지 로직 표준적). D-1 RRN 패턴 제한은 코드 내 명시된 의도적 트레이드오프로 BLOCK 사유 아님.

---

_본 문서는 원본 audit (gitignored out/ 소멸)의 재생성본. 현재 master 5a41bf5 기준 실행 증거 기반._
