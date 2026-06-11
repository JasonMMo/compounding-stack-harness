# .claude/agents — Agent Manifest

> G-5 (asset-exposure) manifest. 새 agent 추가 시 이 표에 1행 추가.

## Axis-7 expert agents (외부 고객 향 — 도메인 자문)

| Agent | Vertical | Scope |
|---|---|---|
| [domain-expert-generic.md](domain-expert-generic.md) | generic (baseline) | 14 generic 도메인 entity/relationship/preset 셰이핑. vertical agent 부재 시 기본 자문역 |
| [domain-expert-legal.md](domain-expert-legal.md) | legal | 법무법인·법무팀 고객. 사건 관리·판례 검색·한국 법체계 관습. generic 을 supersede (Growth-24) |

## 내부 직무 인격 (Partnership Charter §1)

| Agent | 역할 | 책임 영역 |
|---|---|---|
| [engineer-agent.md](engineer-agent.md) | Engineer | 구현·refactor·adapter·script·테스트 코드 |
| [qa-agent.md](qa-agent.md) | CQO | 가드 통과 기준·4계층 풀테스트 게이트·머지 BLOCK |
| [marketing-agent.md](marketing-agent.md) | CMO | 포지셔닝·메시지·런칭·sales enablement |
| [design-agent.md](design-agent.md) | CDO | 디자인 토큰·UI 시스템·접근성 |
| [pm-agent.md](pm-agent.md) | PM | 고객 needs 발굴·요구사항·delivery loop 품질 |
| [security-agent.md](security-agent.md) | CISO | 인도 전 보안 리뷰 게이트·시크릿/취약점 점검·데이터 유출 추적·self-host 하드닝·보안 인도 BLOCK |
| [devops-agent.md](devops-agent.md) | DevOps | preview 티어 운영·디지털 자산 레지스트리·CI/CD·시크릿 볼트·설치 런북·인프라 비용 추적 |

상세 역할 정의: [`docs/business/partnership-charter.md`](../../docs/business/partnership-charter.md), agent frontmatter 규약: `.claude/rules/agent-definition.md` (user-global).
