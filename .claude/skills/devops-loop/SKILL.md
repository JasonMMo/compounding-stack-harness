---
name: devops-loop
description: Run the DevOps/Platform loop — asset inventory, provision/deploy preview tier, CI/CD pipeline, package & install (remote/onsite), registry update, infra cost reflux. Use when devops-agent provisions infra, ships a preview, runs a pipeline, or installs a deliverable.
---

# DevOps Loop

> 실행 주체: `devops-agent` (`.claude/agents/devops-agent.md`). 단일 진실 토폴로지: [`deployment-topology.md`](../../../docs/architecture/deployment-topology.md). 인도(설치) 실행은 PM 인도 승인 + CISO 보안 게이트 통과 후.

## Loop Steps

| # | 단계 | 동작 | Exit 기준 |
|---|---|---|---|
| 1 | **자산 점검** ★레지스트리 | `infra/registry/` 에서 대상 고객·환경의 현재 자산 (서브도메인·VPS·인증서·시크릿 참조) 을 확인. 없으면 신규 발급 계획 | 대상 자산 상태 1줄씩 식별 |
| 2 | **이력 검색** ★지식 저장소 | `python scripts/ledger-index.py --symbol <대상>` + `qmd search "<대상> deploy" -c docs` — 같은 환경의 과거 배포·설치·장애 이력 확인 | 기존 인프라 이력 판정 |
| 3 | **provision / build** | preview: Coolify 프로젝트 + `<slug>.n9n.co.kr` 발급. 인도물: profile → `scaffold.py` → docker build → 패키징. 시크릿은 볼트 주입 (커밋 ✗) | 빌드/프로비전 성공, 로그 격리 |
| 4 | **배포 / 설치** | preview: Coolify push → TLS 발급 → URL 확인. production: 원격(SSH/AnyDesk) 또는 1회 방문 설치 런북 수행 (self-host) | 대상 URL/환경에서 기대 응답 (L4 live 와 정렬) |
| 5 | **검증·하드닝** | 배포 후 헬스체크 + 최소 노출 확인 (포트·서브도메인·접근). 하드닝 실행분은 CISO 기준 준수, 보안 판정은 CISO 게이트 | health PASS + 노출 최소 확인 |
| 6 | **레지스트리·비용 환류** ★ | `infra/registry/` 에 발급 자산·설치 기록 갱신 (시크릿 참조만). 신규 인프라 비용을 charter §5 + 월 cost-report 에 환류 | 레지스트리 반영 + 비용 1줄 기록 |
| 7 | **기록·환류** ★지식 저장소 | `docs/learn-logs/devops.md` 갱신. 반복 수동 절차 (3회) 는 런북/스크립트/CI 로 상수화 (복리 §3). 가드 가능한 인프라 불변식은 CTO 에 가드 row 제안 | ledger 반영 + 런북/가드 환류 |

## 지식 저장소 프로토콜

- **시작**: step 2 — 과거 배포·장애 이력 검색 없이 provisioning/설치 시작 금지.
- **종료**: step 7 — 비자명한 인프라 패턴·설치 함정은 런북/wiki 로 누적 (고객 수 증가 시 반복 배포를 CI/런북으로 상수화하는 hedge).

## 출력 규약

배포 로그·빌드 출력·설치 트레이스 본문은 `docs/learn-logs/devops.md` (누적) 또는 인도물 단위면 `docs/delivery/<slug>/deploy-log.md` 에 쓰고, main 으로는 **결과 (URL/상태) + 레지스트리 경로 + 비용 델타 + BLOCK/CAVEAT 항목만** 반환한다 (envelope §4). 규약: [`subagent-output-protocol.md`](../../../docs/architecture/subagent-output-protocol.md).

## Anti-patterns

- 고객-facing preview 를 노트북 터널에 의존 (노트북 꺼지면 다운) / 발급 자산을 레지스트리에 기록 안 함 (자산 분실) / 시크릿을 레지스트리·커밋에 평문 저장 (CISO 에스컬레이션) / 수동 클릭으로만 배포 (재현 불가) / 인프라 비용을 §5 에 환류 안 함 / 보안 게이트 (CISO) 전에 인도 설치
