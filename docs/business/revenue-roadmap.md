# Revenue Roadmap

> 매출 모델·milestone·gating 조건이 한 곳에. 모든 Growth 엔트리는 어느 milestone 에 기여하는지 명시 (learn-log §6 의무 필드).

## Revenue Model — 4 stream

| 스트림 | 단위 | 가격 가이드 (TBD) | 비고 |
|---|---|---|---|
| **Self-host license** | 회사당 연간 | 초기 \$10K~\$30K | 1 회사 = 1 license = N 도메인 무제한 |
| **Expert-agent subscription** | agent 1개당 월 | 초기 \$200~\$500 | per-vertical agent — 의료/제조/물류/금융 등 |
| **Marketplace revenue share** | preset PR 머지당 | 30% revenue share to contributor | M4 이후 |
| **SaaS hosting** | 테넌트당 월 | TBD | M5 (Growth-73 4-조건 충족 후) |

## Milestone Ladder

각 milestone 은 다음 4 필드를 가진다:
- **목표**: 정성적 도착 지점
- **deliverable**: 합의 가능한 산출물
- **revenue trigger**: 매출이 발생하기 시작하는 조건
- **gating**: 다음 milestone 진입 조건

---

### M0 — Founding (2026-05-29 ~ 2026-06-30 예정)

- **목표**: 헌장·아키텍처·비즈니스 로드맵 정렬
- **deliverable**: 이 문서들 (CLAUDE.md, AGENTS.md, README.md, 4 docs/ 문서, learn-log §0~§6 골격)
- **revenue trigger**: 없음
- **페르소나 인수**: CEO 와 IT-담당자 역할을 겸하는 창업 팀이 헌장·아키텍처·비용 모니터링 문서를 읽고 7축 구조와 revenue gate 를 30분 안에 설명할 수 있다.
- **gating → M1**: 7축 모두 owner 디렉터리 존재 + L1 풀테스트 골격 작동 + 첫 commit log 가 per-file 규칙 준수

---

### M1 — Generic Harness Baseline

- **목표**: 산업 무관 14 공통 도메인 (고객/계약/주문/청구/회계/재고/직원/근태/문서/일정/공지/권한/감사로그/파일) 으로 풀스택 1 set 가 동작
- **deliverable**:
  - `presets/skills/generic/*.seed.md` × 14
  - `presets/ddl/catalog.yaml` (14 도메인 × 4 dialect)
  - `middle/contract/` v1
  - **Frontend adapter 2개**: vanilla-htmx + react
  - **Backend adapter 2개**: springboot-jakarta + fastapi
  - `domain-expert-generic` agent 가 profile 작성 도움 demo
- **revenue trigger**: 없음 (그러나 sales lead 수집 시작)
- **페르소나 인수**: IT-담당자 가 4-corner (springboot·fastapi × vanilla-htmx·react) 의 4계층 풀테스트·compliance test 가 전부 PASS 함을 확인하고, 14 도메인 중 1개를 로컬에서 scaffold → typed 화면이 사내망 내부에서 외부 클라우드 호출 없이 동작함을 30분 안에 검증한다. (ops pack 실배포는 M2 로 이관 — CEO 결정 2026-06-02. ops pack 미구현이 M1 maturity 를 막지 않음: T-1~T-6 기술 기준에 ops pack 불포함.)
- **gating → M2**: 14 도메인 풀테스트 4계층 그린 + 첫 demo 영상 + lead 5건 → 정량 기준은 [M1 Maturity Threshold](#m1-maturity-threshold--pricing-공개-정량-게이트) (Technical 6/6 + GTM)

---

### M2 — First Paid Customer

- **목표**: 1 회사가 self-host license 결제
- **deliverable**:
  - 첫 customer profile 작성 완료 (해당 회사 산업 무관)
  - 그 회사 도메인 N개 scaffold + 실제 사내 운영 1주 이상
  - ops pack (docker-compose + Vault + SSO) 그 회사 환경 적용
  - 결제 영수증 발행
- **revenue trigger**: **첫 self-host license 매출 발생** (예: \$10K)
- **페르소나 인수**: 업무담당자 가 domain-expert agent 와 인터뷰 세션 1회 (최대 2시간) 를 완료하고, 자기 회사 핵심 도메인 1개의 CRUD 화면 초안을 당일 수령하여 실제 업무 데이터를 입력해 본다. 또한 IT-담당자 가 ops pack (docker-compose + Vault + SSO) 을 사내 Linux 서버에 배포하고 SSO 로그인·감사로그 적재까지 2시간 안에 검증한다 (M1 에서 이관).
- **gating → M3**: 첫 고객 사례 공개 가능 + 그 회사 산업이 무엇인지 데이터로 확정

---

### M3 — Expert-Agent First Vertical

- **목표**: M2 첫 고객의 산업을 vertical 로 박고, `domain-expert-<산업>` agent 가독립 매출
- **deliverable**:
  - `.claude/agents/domain-expert-<산업>.md`
  - `presets/skills/<산업>/*.seed.md` × 30~50
  - `presets/ddl/<산업>.yaml` (산업 특화 entity)
  - 산업별 컨벤션 (예: 의료 ICD-10, 금융 회계계정과목) 가드
  - **expert-agent SaaS landing page** (해당 산업 한정)
- **revenue trigger**: **첫 per-agent SaaS 구독 발생** (예: \$300/월 × 2개사)
- **페르소나 인수**: 특정 산업의 업무담당자 가 해당 산업 전용 domain-expert agent 와 인터뷰 후, 산업 특화 필드 (예: 의료 ICD-10 코드, 금융 계정과목) 가 포함된 화면 초안을 1주일 안에 수령하고 "기존 업무 방식과 맞다"고 확인한다.
- **gating → M4**: 2 vertical 동시 매출 발생 + customer 누적 5개사 + L1~L4 풀테스트 자동화

---

### M4 — 3 Vertical + Marketplace Alpha

- **목표**: 3 산업 동시 운영 + 외부 contributor 가 preset PR 보내는 흐름 작동
- **deliverable**:
  - 3 vertical agent (`.claude/agents/domain-expert-<a>.md`, `<b>.md`, `<c>.md`)
  - GitHub Issue 템플릿: "당신 산업의 14 preset PR 받습니다"
  - PR 리뷰 자동화 (4계층 풀테스트 + diagnose guards + 산업 컨벤션 가드)
  - 30% revenue share 정책 + Stripe Connect (혹은 동등) 구현
- **revenue trigger**: **첫 marketplace 외부 contributor PR 머지 + 그 contributor 에게 첫 share 송금**
- **페르소나 인수**: 외부 contributor (IT-담당자 또는 도메인 전문가) 가 새 industry preset PR 을 제출하고, 4계층 자동 테스트 + 산업 컨벤션 가드를 통과하여 머지 승인을 3일 안에 받는다.
- **gating → M5**: 외부 contributor 누적 10명 + customer 누적 20개사 + Growth-73 4-조건 점검

---

### M5 — Multi-Tenant SaaS (v2.0)

- **목표**: 자체 호스팅 SaaS 모드 진입 (Growth-73 4-조건 ALL-AND 충족 시에만)
- **deliverable**:
  - 멀티테넌트 isolation 검증
  - 데이터 격리 감사 통과
  - SOC2 / ISO 27001 트랙 진입
  - SaaS pricing tier 공개
- **revenue trigger**: **첫 SaaS 테넌트 결제**
- **페르소나 인수**: CEO 가 SaaS 플랜 landing page 에서 trial 신청 후, IT-담당자 개입 없이 테넌트 프로비저닝이 완료되고 업무담당자 가 첫 로그인해서 도메인 선택 화면을 보는 전 과정이 1시간 안에 끝난다.
- **gating**: 종착점 (v3.0 은 별도 결정)

## M1 Maturity Threshold — pricing 공개 정량 게이트

> Growth-5e Q1 의존 해소 (2026-06-02, CTO). "M1 이 팔 만큼 성숙했는가"를 정성 판단이 아니라 **측정 가능한 체크리스트**로 박는다. M1→M2 gating(§M1) 의 **기술 성숙도** 절반을 정량화한다 — 나머지 절반(demo 영상 + lead 5건)은 GTM 으로 CEO/CMO 소유.

### 두 축 분리 (둘 다 충족해야 pricing 공개)

- **Technical Maturity** (CTO 소유, 자동 측정 가능) — 아래 T-1~T-6.
- **GTM Readiness** (CEO/CMO 소유) — demo 영상 1건 + qualified lead 5건 + pricing tier 내부 합의.
- **pricing 공개 = Technical ALL-PASS AND GTM ALL-MET.** 하나라도 미충족 시 가격 비공개 (charter §3 #3 정신).

### Technical Maturity 체크리스트

| ID | 기준 | 측정 방법 | 현재 (2026-06-02) |
|---|---|---|---|
| **T-1** | 7축 전부 ≥1 자산 + manifest 노출 | 각 축 디렉터리/INDEX 존재 (G-5) | ✅ PASS |
| **T-2** | 14 도메인 catalog 무결성 (seed⊆catalog, dangling FK 0, type closed-set, FK hygiene) | G-10 + G-12 PASS | ✅ PASS |
| **T-3** | 전 가드 0 real FAIL | `scripts/diagnose.py` (G-2/G-3 SPEC 허용) | ✅ 12/12 |
| **T-4** | pluggable F/B 4-corner (≥2 backend × ≥2 frontend) compliance | adapter INDEX + adapter-agnostic suite | ✅ springboot·fastapi × vanilla-htmx·react |
| **T-5** | 4계층 풀테스트 그린 — 양 backend DIM-1~6 + 양 frontend F-1~F-4 live | L1~L4 live run | ✅ springboot 37 · fastapi 37 · react 36 · vanilla-htmx 37 (Java-env 2026-06-02 종결) |
| **T-6** | expert-agent end-to-end (needs→profile→scaffold rc=0→typed 화면) | scaffold rc=0 + screen-manifest | ✅ smallmfg-demo (Growth-14) |

**현재 Technical Maturity = 6/6 MET → M1 기술 성숙 달성.**

### T-7 (비용 측정) — M1 N/A, M2/M3 로 이관

per-request LLM/infra 비용 측정(charter §5)은 **M1 런타임에 측정할 대상이 없다** — M1 harness 는 순수 로컬(scaffold·adapter·render 무 LLM), expert-agent 추론은 Claude Code 외부에서 발생. 제품이 자체 LLM/infra 호출을 하는 시점(배포형 expert-agent = M3, 호스팅 = M5)에 **T-7 = "deployed 경로 per-request cost log 작동"** 으로 활성. M1 maturity 미달 사유 아님.

### 자동화 (후속 — CEO 승인 시 engineer 위임)

`scripts/maturity-check.py` (또는 make 타겟): T-1~T-6 을 한 번에 평가해 PASS/FAIL maturity 리포트 1장 출력 (diagnose + 4-corner live suite 오케스트레이션). 현재는 수동 평가(위 표). 자동화하면 매 Growth 마무리에 maturity 회귀를 잡는다.

> **결론 (2026-06-02)**: M1 은 기술적으로 pricing 공개 준비 완료. 남은 게이트 = GTM (demo 영상 + lead 5건) — CEO/CMO 소관.

## Growth Entry Format (learn-log §6 의무)

```markdown
### Growth-N (YYYY-MM-DD) — <title>
- Axis touched: <축들>
- Milestone: M? (예: M1, M2)
- Revenue contribution: <어떻게 매출에 기여 또는 "infra only">
- Cost impact: <이 변경이 LLM/infra 비용에 미치는 영향, 없으면 "none">
- ...
```

매월 마지막날 CTO 가 milestone 진행률 1줄 리포트를 learn-log §6 끝에 추가.

## 결정 메모

- **첫 vertical 결정 방식**: M2 첫 고객의 산업으로 자동 결정. **사전 vertical 선택 금지** — 도메인 전문가 없는 추측은 비싸다.
- **무료 trial 정책**: M2 까지 3개사 무료 사용 허용 (case study 권리 양도 받음). M3 부터 paid only.
- **OSS / 상용 분리선**: middle contract + adapter compliance test = OSS (Apache 2.0). orchestrator + expert-agent definitions + customer profile tooling = commercial.

## marketing-site Deliverable 위치 (Growth-65)

- **고객층**: 웹에이전시형 신규 고객 — 시각·UX 가 업무시스템보다 중요한 SMB. 품질 바 B(professional SMB). 부티크 아트디렉션(A)은 비채택(사람 craft·복리 불가).
- **M1 GTM dogfood**: 우리 자신의 랜딩을 첫 테마(`aurora`)로 빌드 → 데모 + 리드 인프라로 활용. M1 gating 조건(T-1~T-6) 과는 별개 — 7축 안의 visual-asset 축(8번째 축) 검증.
- **M2/M3 상품화**: marketing-site SKU 추가 — 라이선스(제작 일회성) / 제작 매출 라인. self-host license 에 marketing-site 빌드 패키지가 옵션으로 포함.

## Intake 파이프라인 매출 신호 (Growth-62)

자율 intake 파이프라인이 두 가지 매출 신호를 생성한다:

- **gap-registry → Growth**: `docs/intake-inbox/gap-registry.jsonl` 에 누적되는 미충족 gap_category 가 count≥3 에 도달하면 PROMOTE 플래그 → CTO 주간 스캔 → 해당 축(7축 중) Growth-N 생성 → engineer 구현 → 향후 리드 가점. 미충족 리드가 **제품 확장 백로그의 우선순위 입력**이 된다 (복리 축적).
- **stalled-lead → cost-report**: `pipeline_monitor.py` 가 SLA 초과 stall 케이스를 감지하면 `docs/intake-inbox/alerts.md` 에 기록. stall된 qualify 리드는 **예상 매출 손실 신호** — 매월 cost-report (`cost-reports/<YYYY-MM>.md`) 에 환류하여 DevOps/PM 이 병목 개선 우선순위를 잡는다.
