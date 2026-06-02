# HANDOFF — 2026-06-02 (Growth-16 종료 후)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.

## 이번 세션에 끝낸 것 — Growth-14·15·16 (전부 master 푸시 완료)

세션 시작점은 Growth-13(ledger-index) 종료 직후. CEO 가 후보 #1(expert-agent demo) → 이후 "#2→#1" 지시.

**Growth-14 — expert-agent end-to-end demo (creater 축 첫 채움)**
- `scripts/workflow/scaffold.py`+`manifest.py`: profile→catalog 검증→DDL+screen-manifest. frontend typed-form(manifest 구동, 없으면 generic fallback). **G-11**(creater single-source). agent baseline 표 catalog 1:1 동기화. live: domain-expert agent 가 needs→11 entity 큐레이션→scaffold rc=0 = 7축 실증. acme-erp 비호환은 CEO 결정으로 catalog 실키 수정.

**Growth-15 — FK 참조 무결성**
- catalog FK hygiene(10 dangling 분류: polymorphic 7·backlog 2·customer_id→contact fk) + **G-12** 가드. runtime FK 검증 양 backend + DIM-6. ⚠️ **fastapi live 37 green / Java live 미실행(JDK 부재)**.

**Growth-16 — 2nd frontend adapter (react)**
- `frontend/adapters/react/`: Vite+React18+TS. contract 빌드타임 codegen(G-1 클린), CSS custom property 토큰, 6 screen, F-1~F-4, manifest typed-form. **L1 30 / L3 build / L4 35(fastapi) green**. `frontend/adapters/INDEX.md`(G-5). QA F-2 hollow test caveat → hasMorePages 헬퍼로 클로즈.

## 현재 상태

- **Milestone**: M1 거의 완성. **pluggable F/B 4-corner 완성** (backend springboot+fastapi × frontend vanilla-htmx+react). 7축 전부 활성.
- **Guards**: 12개 (G-1~G-12), 실 FAIL 0 (G-2/G-3 만 SPEC). `python scripts/diagnose.py`.
- **Tests**: workflow L1 25 + vanilla-htmx 23 + manifest 21 + react 30 ... fastapi DIM-1~6 live 37. `out/` gitignore.
- **Git**: clean, master 동기화 (HEAD `e1ed6e9`).

## 2026-06-02 추가 종결 — #1 Java 게이트 + #2 maturity threshold (CEO "1→2" 지시)

- **#1 Java-env 게이트 CLOSED**: 이 머신에 **JDK 21 + gradlew wrapper 존재**(이전 sub-agent 의 "JDK 없음"은 system `gradle` 만 찾은 false-negative). QA 실행 — springboot gradlew test 30(CatalogValidatorTest 22 incl FK 7) + **DIM-1~6 live 37 PASS** + react↔springboot L4 36 PASS(2 skip=Vite preview SPA, M2 전 활성). Growth-15·16 carry 종결. 발견: system JDK21 ↔ Gradle daemon JDK17(무해, Spring Boot 3.2.5 는 17+).
- **#2 maturity threshold 정량화**: `revenue-roadmap.md#M1-Maturity-Threshold`. pricing 공개 = Technical(T-1~T-6, **현재 6/6 MET**) AND GTM(demo·lead, CEO/CMO). T-7 비용측정은 M2/M3 이관. **→ M1 기술 성숙 달성.**

## ▶ 즉시 다음 액션 (CEO 확정: GTM 피벗)

**CMO(marketing-agent) 에 demo 영상 시나리오 + 제작 방법 위임** — 이번 세션에서 위임 직전 `/clear` 로 중단됨. fresh 세션에서 바로 재개:
- 산출물: `docs/marketing/demo-video-scenario.md` (시나리오/스크립트 + 웹리서치 기반 제작 방법 + asset 체크리스트 + 배포 훅).
- 그라운딩: `docs/marketing/positioning.md`(기존 CMO 자산) + M2 페르소나 인수(업무담당자 needs→agent 큐레이션→**당일 typed 화면 초안**) + live 흐름 `smallmfg-demo`(중소제조 인사+설비, 11 entity) / `shop-demo`. 3 차별화(axis-7 expert-agent / pluggable F/B 4-corner / cost-aware self-host).
- **honest marketing**: 검증된 능력만 — 4-corner·screen-manifest typed form·expert-agent end-to-end 전부 live 검증됨(2026-06-02). vaporware 금지.
- 제작 방법: SaaS/dev-tool demo 영상 best practice 웹리서치 → 화면녹화·보이스오버(human vs AI TTS)·편집·자막(한/영)·호스팅·비용추정, 명확한 권고 1개.

## 다음 후보 (우선순위)

1. **GTM (CEO/CMO 소관)** — ↑ demo 영상(위 즉시 액션) + qualified lead 5건 → pricing 공개. 기술 측은 준비 완료.
2. **catalog 성장 (domain-expert)** — `machine`(production), `accounting-period`(finance) entity 신설 → operation.machine_id / journal-entry.period_id fk-exempt backlog 해소.
3. **maturity-check.py 자동화** (T-1~T-6 1-shot PASS/FAIL 리포트, CEO 승인 시 engineer) / Vite preview SPA 테스트 2건 활성(M2 전) / vue·nexacro adapter(M2 후) / react persona ceo·it / ledger-index `--check`→G-13 / OpenAPI 3.1 / `--serve`.

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Opus 4.8` / master push CTO 자동 (private repo).
- Growth 마무리마다 `python scripts/ledger-index.py` 재빌드.
- **환경 가용**: Node v24 ✓ / Python ✓ (fastapi live 가능) / **JDK·Gradle ✗** (springboot live 불가 — 위 #1 게이트의 원인).
- 장시간 background engineer 위임 시 "중간 커밋 체크포인트" 지시 (Part C silent-stop 교훈).
