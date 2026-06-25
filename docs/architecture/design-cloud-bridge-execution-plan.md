# Design-Cloud Bridge — 실행 계획 (수정·배포·테스트 절차)

> CTO 결정 (Growth-130 후속, 2026-06-26). 아키텍처 본문: [`design-cloud-bridge.md`](design-cloud-bridge.md).
> 본 문서는 **그 아키텍처를 어떻게 구현·배포·검증하는가**의 실행 계획.
> 역할 분담 확정: **claude-design = cloud craft 전용(git 밖)**, **repo-side 가드/CLI = main(CTO) 세션**.

## 1. 토폴로지 — 누가 어디서 작업하나

```
┌──────────────── claude-design 세션 (CLOUD, git 밖) ────────────────┐
│  claude.ai/design 워크벤치에서 컴포넌트 craft (배포 없이 즉시 렌더)  │
│  산출물은 git 에 직접 안 들어옴 → /design-sync 로 staging 에 내려줌  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ /design-sync (1 컴포넌트씩)
                                ▼  ▶ DTCG 토큰 JSON + 컴포넌트 staging ◀
┌──────────── main(CTO) 세션 (REPO-side, worktree 격리) ──────────────┐
│  git worktree:  D:/AI/workspace/harness-cloud-bridge                 │
│  branch:        design/cloud-bridge                                  │
│  · 정규화 스크립트 / CI 가드 5종 / 복제본 빌드 CLI 구현              │
│  · 파일당 커밋 → Phase QA PASS 시에만 master 로 머지                 │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ merge (fast-forward, QA gate 후)
                                ▼
                    master  ──push──▶  Coolify 자동 빌드 (라이브)
```

- **master 보호**: 구현은 `design/cloud-bridge` branch 에만. 머지 전까지 master = 라이브 데모 영향 0 ([[push-before-deploy]]).
- **문서 예외**: 아키텍처/계획 문서(`docs/architecture/*`)는 deploy 무영향 → master 직접 (discoverability). **코드는 branch.**
- **worktree 주의**: cwd ≠ main repo root → 상대경로 훅 취약 ([[subagent-cwd-hook-fragility]]). 신규 파일 Write 는 안전, 기존 파일 수정은 직접 diff 검증. `.venv`/`node_modules`/`.codegraph`/`.serena` 는 worktree 에서 재구축(gitignore).

## 2. 작업 분해 (WP) — CTO repo-side, claude-design 비의존 우선

| WP | 내용 | claude-design 의존 | 산출물 |
|---|---|---|---|
| **WP-1** | 경계·스캐폴딩 — `staging/` 컨벤션, DTCG 토큰 스키마, 정규화 스크립트 스켈레톤 | ✗ | `scripts/design/normalize.py`(skeleton), 토큰 스키마, staging README |
| **WP-2** | **CI 가드 5종** + 테스트 (안전망 우선) | ✗ | `scripts/diagnose.py` 가드 + §2 카탈로그 + 단위테스트 |
| **WP-3** | 복제본 빌드 CLI — Style Dictionary v5+ 평가/정렬, 고객 정적번들 | ✗ | `scripts/design/build_replica.py` + 테스트 |
| **WP-4** | 파일럿 통합 — craft 1건 → 정규화 → variant → 라이브 측정 | ✓ (craft 도착 필요) | catalog variant + landing-astro 컴포넌트 + 측정 리포트 |

**착수 순서**: WP-1 → WP-2 → WP-3 (전부 unblocked) → WP-4 (claude-design craft 도착 시). 가드(WP-2)를 앞세워 안전망부터 구축.

## 3. 영역별 기능·특징·제약

| 영역 | 기능 | 특징 | 제약 |
|---|---|---|---|
| **Cloud craft** (claude-design) | 컴포넌트 시각 craft, 배포없는 즉시 렌더 | 밋밋함 해소 엔진, 빠른 반복 | **PII·기밀 업로드 금지**(BAA제외·학습기본). 무명 컴포넌트만. 1컴포넌트씩 |
| **Sync** (`/design-sync`) | cloud→`staging/` 다운, finalize_plan 경로잠금 | 점진(통째교체 금지) | 대량 마이그레이션 부적합. staging 은 gitignore |
| **정규화 게이트** (`normalize.py`) | 컴포넌트→토큰override+variant 분해 | **비협상** — CDO 검수 | 미통과 직접붙임 = axis-8 붕괴. 컴포넌트 HTML production 직커밋 금지 |
| **토큰 경계** (DTCG JSON) | cloud↔repo 단일 교환 포맷 | raw→semantic→theme.yaml 계층이 곧 경계 | DTCG v2025.10(W3C CG, Rec 아님). "표준준수" 광고 금지 |
| **CI 가드 5종** (`diagnose.py`) | 업로드스코프·결합누출·교차테넌트·DTCG스키마·정규화 검사 | 머지·인도 BLOCK 권한 | §2 카탈로그+§4 counter 갱신 필수 |
| **복제본 빌드** (`build_replica.py`) | 고객 theme+profile→정적 번들 | 빌드타임 **물리격리**(런타임 라우팅 반대) | Style Dictionary **v5+ 핀**. 번들에 cloud ref·타테넌트 slug·PII = 0 |
| **배포** (Coolify) | master push→자동 빌드 | bridge 툴링 대부분 non-runtime | landing-astro 빌드 영향 산출물만 배포 주의 |
| **테스트** (4계층) | L1 가드+단위 / L3 build / L4 live | QA agent 게이트 | 의도된 violation 외 0 error |

## 4. 수정 → 배포 → 테스트 사이클

```
[worktree: design/cloud-bridge]
  수정 ─▶ 파일당 커밋(§9, Fable 5 trailer) ─▶ WP별 테스트
                                                  │
                                          ┌───────┴────────┐
                                       FAIL              PASS
                                          │                │
                                       수정 반복      QA agent 게이트
                                                           │
                                                    master fast-forward 머지
                                                           │
                                                    master push ─▶ Coolify
                                                           │
                                                    L4 live 검증(해당 시)
```

### 수정 절차
1. main(CTO) 세션이 worktree(`harness-cloud-bridge`, `design/cloud-bridge`)에서 작업.
2. 파일당 별도 커밋 (CLAUDE.md §9), `Co-Authored-By: Claude Fable 5`.
3. 코드는 branch, 문서(`docs/architecture/*`)는 master.

### 배포 절차
1. WP 완료 + 테스트 PASS + QA agent 게이트 통과 → master 로 fast-forward 머지.
2. master push → Coolify 자동 빌드. **머지 전 master·라이브 데모 영향 0.**
3. 복제본/landing-astro 산출물 변경 시에만 라이브 빌드 영향 → L4 확인.

### 테스트 절차
- **L1**: 새 가드별 단위테스트 + `python scripts/diagnose.py` (전체 가드 무회귀).
- **정규화**: 샘플 synced 컴포넌트 → 기대 토큰/variant 추출 일치.
- **복제본 누출**: 빌드 산출물에 `claude.ai`/cloud ref **0**, 타 고객 slug **0**, raw PII **0** (= 누출 가드를 테스트로).
- **L3 build**: `npm run build` (landing-astro) BUILD SUCCESS.
- **L4 live**: 복제본 정적 번들 HTTP 응답 확인 (WP-4 / 복제본 변경 시).

## 5. WP별 Exit Criteria

| WP | 완료 기준 |
|---|---|
| WP-1 | staging 컨벤션 문서화 + normalize.py 스켈레톤이 샘플 입력 파싱(no-op OK) + DTCG 스키마 존재 |
| WP-2 | 가드 5종 구현 + 각 단위테스트 PASS + `diagnose.py` green + §2 카탈로그 등록 |
| WP-3 | build_replica.py 가 샘플 고객 theme 로 정적 번들 생성 + 누출 가드 3종 PASS |
| WP-4 | craft 1건이 variant+토큰으로 정규화·라이브 반영, 시간절감/품질 측정 리포트 → design-loop SKILL 박제 |

## 6. 잔여 게이트 (founder/외부)
- **legal 고객**: Claude Design BAA beta 졸업 재검증 전 PII 절대 금지 (C2).
- **Style Dictionary v5+** 도입은 `build_tokens.py` 정렬 vs 대체 평가 후 (WP-3).
