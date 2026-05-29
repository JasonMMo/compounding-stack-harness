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
- **gating → M2**: 14 도메인 풀테스트 4계층 그린 + 첫 demo 영상 + lead 5건

---

### M2 — First Paid Customer

- **목표**: 1 회사가 self-host license 결제
- **deliverable**:
  - 첫 customer profile 작성 완료 (해당 회사 산업 무관)
  - 그 회사 도메인 N개 scaffold + 실제 사내 운영 1주 이상
  - ops pack (docker-compose + Vault + SSO) 그 회사 환경 적용
  - 결제 영수증 발행
- **revenue trigger**: **첫 self-host license 매출 발생** (예: \$10K)
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
- **gating**: 종착점 (v3.0 은 별도 결정)

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
