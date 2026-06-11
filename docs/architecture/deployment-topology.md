# Deployment Topology — preview 티어 vs production 티어

> 단일 진실. 소유: `devops-agent` (DevOps, 9번째 인격, Growth-35). 변경은 CTO 아키텍처 결정 + DevOps 실행.
> 맥락: 1인 비대면 창업 (숨고/크몽 건당 500만원). 고객 접점 3종 (메신저·preview·설치) 의 인프라 설계.

## 1. 핵심 통찰 — 2-티어 분리

우리 가치 제안은 **고객 사내망 self-host** (M2 라이선스 매출). 그러므로 최종 결과물은 **고객 인프라**에 산다. n9n.co.kr / VPS 는 **고객 설득용 preview/staging 전용**이지 최종 호스팅이 아니다.

| 티어 | 위치 | 목적 | 수명 | 소유 |
|---|---|---|---|---|
| **Preview** | 내 VPS (`<slug>.n9n.co.kr`) | 고객이 아무 때나 결과 확인 (비대면 설득) | 계약~인도 | 우리 (DevOps) |
| **Production** | 고객 사내망 (self-host) | 실제 운영 — 인도물 | 영구 | 고객 (DevOps 설치 지원) |

> 이 분리가 모든 배포 선택을 가른다. preview 는 *마케팅 자산*, production 은 *인도물*.

## 2. Preview 티어 — Coolify on VPS (결정)

### 왜 로컬 Docker + 터널이 아닌가

로컬 Docker + 터널 (cloudflared/frp) 을 **고객-facing preview 로 쓰면 안 된다** — 노트북이 꺼지면 preview 가 죽는다. 비대면 신뢰도에 치명적 (고객이 링크 눌렀는데 죽어있음 = 계약 손실).

→ 터널은 **작업 중 화면공유 데모** (내가 보는 앞에서 시연) 폴백으로만 사용.

### 결정 스택

```
[고객 브라우저]
   │  https://acme-corp.n9n.co.kr
   ▼
[Seoul VPS]  ── Coolify (self-hosted PaaS)
   ├─ project: acme-corp   → docker stack (frontend+backend+db)
   ├─ project: beta-inc    → docker stack
   └─ ...                   (고객별 격리, 단일 VPS 다중 프로젝트)
   │  Let's Encrypt TLS 자동 (와일드카드 또는 per-subdomain)
```

- **PaaS**: Coolify (오픈소스, self-host). git push → 자동 배포, 프로젝트 격리, TLS 자동, preview 환경 내장.
- **VPS**: Seoul 리전 (Vultr / AWS Lightsail / 카페24, ~\$6~12/월, ≥2vCPU/4GB). Coolify 권장 사양 충족.
  - Oracle Cloud Free ARM (Seoul) 도 가능하나 사업용은 account reclaim 리스크로 비추천.
- **DNS**: `n9n.co.kr` 와일드카드 `*.n9n.co.kr` A 레코드 → VPS IP. 고객마다 `<slug>.n9n.co.kr` 한 줄로 발급.
- **비용 프레이밍**: 건당 500만원 대비 월 \$6~12 는 무의미. **신뢰도 > 비용 절감** — 여기서 아끼지 않는다.

### Preview 부트스트랩 런북 (1회)

> ⚠ 미provisioning. 다음 DevOps 세션 첫 임무. 실행 전 CISO 하드닝 기준 정렬.

1. Seoul VPS 발급 (≥2vCPU/4GB, Ubuntu LTS). SSH 키 인증만, 비밀번호 로그인 비활성.
2. 방화벽: 22(SSH, 내 IP 화이트리스트 권장)/80/443 만 개방.
3. Coolify 설치 (`curl -fsSL https://coolify.io/install.sh | bash` — 설치 전 스크립트 검토, CISO).
4. DNS: 가비아/도메인 등록기관에서 `*.n9n.co.kr` + `n9n.co.kr` A 레코드 → VPS IP.
5. Coolify 에서 와일드카드 TLS (Let's Encrypt DNS-01) 또는 per-project TLS 구성.
6. 헬스체크 + 레지스트리 (`infra/registry/`) 에 VPS·도메인 자산 기록.

## 3. Production 티어 — 고객 self-host (인도)

최종 인도물은 고객 사내망에 self-host. 인도 경로:

| 방식 | 조건 | 절차 |
|---|---|---|
| **원격 설치** (기본) | 고객이 SSH/AnyDesk 허용 | 패키지 전송 → docker compose up → 부트스트랩 → 인수 확인 |
| **1회 방문 설치** | 사내망 완전 격리 (법무법인류) | USB/사내 반입 → 온사이트 docker compose up → 인수 |

- 인도 전제: PM 인도 승인 + **CISO 보안 게이트 PASS** (self-host 보안 체크리스트) + QA 4계층 PASS.
- 패키징: `scaffold.py` 산출물 + adapter + docker-compose + self-host 보안 체크리스트 (기본 자격증명 변경 강제).

## 4. CI/CD 파이프라인 (v1 스케치)

```
profile(<slug>.yaml)
   │  python scripts/workflow/scaffold.py --profile <slug>
   ▼
DDL + screen-manifest + adapter 산출
   │  docker build (frontend adapter + backend adapter + middle)
   ▼
[preview] Coolify push → <slug>.n9n.co.kr   (고객 확인)
   │  고객 승인 후
   ▼
[production] 패키지 릴리스 → 원격/방문 설치 (고객 self-host)
```

- preview 배포는 git push 트리거 (Coolify webhook). production 패키징은 명시적 릴리스 (인도 승인 후).
- L4 live 풀테스트와 정렬 — preview URL 이 곧 L4 검증 대상.

## 5. GTM 접점 (3종)

| # | 접점 | 수단 | 비고 |
|---|---|---|---|
| 1 | **메신저** | 숨고/크몽 플랫폼 채팅 (초기) → 카카오톡 채널 (진행) | 플랫폼 규정상 초반은 on-platform. 커스텀 메신저 ✗ (과설계) |
| 2 | **Preview 사이트** | `<slug>.n9n.co.kr` (Coolify) + `n9n.co.kr` 랜딩/포트폴리오 | §2 |
| 3 | **설치** | 원격 (SSH/AnyDesk) / 1회 방문 | §3 |

## 6. 디지털 자산 레지스트리

모든 자산 (도메인·서브도메인·VPS·인증서·시크릿 참조·설치 기록) 은 [`infra/registry/`](../../infra/registry/) 에 추적. **시크릿 평문은 절대 커밋 금지** — 레지스트리엔 볼트 키 참조만, 평문은 gitignored 볼트 (`infra/secrets/`). CISO 시크릿 스캔과 정렬.

## 7. 비용 (charter §5 환류)

| 항목 | 비용 | 비고 |
|---|---|---|
| Seoul VPS (Coolify preview) | \$6~12/월 | 단일 VPS 다중 고객 프로젝트 격리 |
| 도메인 n9n.co.kr | 보유 | 갱신비 연 단위 |
| 와일드카드 TLS | \$0 | Let's Encrypt |
| 터널 (cloudflared, 데모 폴백) | \$0 | Cloudflare 무료 |

고객 수 증가 시 preview 동시 가동분만 선형 — Coolify 단일 VPS 격리로 상수화가 hedge. production 은 고객 인프라라 우리 비용 0.
