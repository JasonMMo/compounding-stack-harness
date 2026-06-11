# DevOps Ledger — 인격별 상세 기록

> 실행 주체: `devops-agent` (`.claude/agents/devops-agent.md`). main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 이 파일은 DevOps 가 닿은 Growth 의 인프라·배포·설치·비용 상세 (대상·조치·재현 명령) 를 담는다. main §6 은 1줄 rollup + 이 ledger pointer.

토폴로지 단일 진실: [`../architecture/deployment-topology.md`](../architecture/deployment-topology.md). 절차: [`../../.claude/skills/devops-loop/SKILL.md`](../../.claude/skills/devops-loop/SKILL.md).

## §1 — Growth 상세

### Growth-35 (2026-06-11) — DevOps 인격 신설 (founding) + 배포 토폴로지 v1

- **계기**: CEO 직접 요구 — 이 harness 를 바탕으로 **1인 비대면 창업** (숨고/크몽 건당 500만원). 고객 접점 3종 (메신저·preview 사이트·원격/방문 설치) + 인프라·디지털 자산·CI/CD 담당 인격 필요. n9n.co.kr 도메인 보유.
- **결정 (CEO 위임 → CTO 설계)**: 인프라/배포/CD 를 engineer·CISO 에 통합하지 않고 전담 9번째 인격으로 분리. 근거 — ① engineer 는 artifact *생성*, DevOps 는 *출하·호스팅·추적* (다른 축) ② CISO 는 보안 *판정*, DevOps 는 하드닝 *실행* ③ 1인이 N 고객 자산을 추적해야 하므로 레지스트리 단일 책임자 필요 ④ charter "직무별 인격" 철학.
- **핵심 아키텍처 통찰 (CTO)**: **preview 티어 ≠ production 티어**. 우리 가치 제안은 고객 사내망 self-host (M2) → 최종 인도물은 고객 인프라. n9n.co.kr/VPS 는 **고객 설득용 preview/staging 전용**. 이 분리가 배포 선택을 가른다.
- **배포 결정**: 로컬 Docker+터널을 고객-facing preview 로 쓰지 않는다 (노트북 의존 = 비대면 신뢰도 치명). **Coolify on Seoul VPS** (\$6~12/월) + `*.n9n.co.kr` 와일드카드 DNS → 고객별 `<slug>.n9n.co.kr`. 터널(cloudflared)은 작업 중 화면공유 데모 폴백으로만.
- **GTM 접점**: 숨고/크몽 플랫폼 채팅(초기) → 카카오톡 채널(진행) → n9n.co.kr 랜딩/포트폴리오. 커스텀 메신저 ✗ (과설계).
- **신설 자산**: `.claude/agents/devops-agent.md` + `.claude/skills/devops-loop/SKILL.md` (출력 규약 wiring, G-13) + `docs/architecture/deployment-topology.md` (토폴로지 단일 진실) + `infra/registry/` (디지털 자산 레지스트리 스캐폴드) + charter v1.6 (9-인격) + CLAUDE.md §1 동기화 + INDEX.md 행.
- **권한**: preview 티어 운영·디지털 자산 레지스트리·CI/CD·시크릿 볼트 운영·설치 런북·인프라 비용 추적 (단독, CTO 아키텍처 제약 내). 인도 설치는 PM 승인 + CISO 보안 게이트 후.
- **첫 임무 (다음 세션)**: ① preview VPS provisioning (Seoul) + Coolify 설치 + `*.n9n.co.kr` 와일드카드 DNS ② CI/CD v1 (`scaffold.py` → docker build → Coolify push) ③ 레지스트리 첫 엔트리.

## §2 — Loop 회전 기록 (배포·설치)

> 각 행: 대상 환경 | 일자 | 동작 (provision/deploy/install) | 결과 | 비용 델타

| 대상 | 일자 | 동작 | 결과 | 비용 델타 |
|---|---|---|---|---|
| (인격 신설 — 첫 배포는 다음 세션 preview VPS provisioning 부터) | 2026-06-11 | founding | 토폴로지 v1 확정 | preview 티어 \$6~12/월 (예정, 미provisioning) |
