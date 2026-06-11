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
[Hostinger VPS · 싱가포르]  ── Coolify (self-hosted PaaS)
   ├─ project: acme-corp   → docker stack (frontend+backend+db)
   ├─ project: beta-inc    → docker stack
   └─ ...                   (고객별 격리, 단일 VPS 다중 프로젝트)
   │  Let's Encrypt TLS 자동 (와일드카드 또는 per-subdomain)
```

- **PaaS**: Coolify (오픈소스, self-host). git push → 자동 배포, 프로젝트 격리, TLS 자동, preview 환경 내장.
- **VPS**: **Hostinger KVM 2** (2vCPU/8GB/100GB NVMe, \$8.99/월 24개월 선결제). CEO 확정 (Growth-35 — KVM1 대비 +\$3/월로 RAM 2배라 다수 고객 Docker 스택 여유).
- **OS**: Hostinger "**Coolify**" 애플리케이션 템플릿(있으면, Ubuntu LTS+Coolify 사전설치) → 없으면 **Ubuntu 24.04 LTS** 클린 후 수동 설치. Debian/CentOS 비추천 (Coolify 문서·커뮤니티가 Ubuntu LTS 집중).
  - **리전 = 싱가포르** (Hostinger 한국 DC 없음 — 인도/인니/싱가포르/말聞이시아 중 한국 최근접 ~70-90ms). preview 는 영업 데모라 지연 무관, production 은 고객 self-host 라 무관.
  - **Coolify 원클릭 OS 템플릿** 보유 → 수동 `install.sh` 생략 가능 (셋업 30분+ 단축).
  - 대안 검토 (기각): Vultr 서울 = 진짜 한국 DC·무약정이나 8GB 동급이 ~\$48/월 (5배). 한국 affiliate 리스트(Ultahost 등) = 커미션 정렬·실 Seoul DC 불명확.
  - 쿠폰: HostAdvice VPS 74%+15% (affiliate 링크, 24개월 선결제 조건). 갱신가 상승 주의.
- **DNS**: `n9n.co.kr` 은 **Cloudflare** 관리 (NS clyde/mira.ns.cloudflare.com). 와일드카드 `*` A 레코드 → VPS IP 추가, **반드시 DNS-only (grey cloud)**. 고객마다 `<slug>.n9n.co.kr` 자동 매칭.
  - ⚠ **grey-cloud 필수**: orange(프록시)면 Cloudflare 가 :80 을 가로채 Coolify traefik 의 Let's Encrypt HTTP-01 챌린지가 실패한다. grey 면 트래픽이 VPS 로 직결돼 per-subdomain LE 정상. (Cloudflare 무료 플랜은 와일드카드 프록시 미지원 → 어차피 grey 강제.)
  - 대안: Cloudflare API 토큰으로 DNS-01 와일드카드 단일 인증서도 가능하나, 기본은 grey + per-subdomain HTTP-01 로 단순화.
  - apex `n9n.co.kr` 는 기존 설정 유지 (랜딩/포트폴리오 별도). preview 엔 `*` 와일드카드만 필요.
- **비용 프레이밍**: 건당 500만원 대비 월 \$6 는 무의미. **신뢰도 > 비용 절감** — 여기서 아끼지 않는다 (단 CEO 선택은 초기 KVM 1 절약, 수요 확인 후 업글).

### Preview 부트스트랩 런북 (1회)

> ⚠ 미provisioning. 다음 DevOps 세션 첫 임무. 실행 전 CISO 하드닝 기준 정렬.

1. Hostinger KVM 2 발급 (싱가포르 리전, OS = **Coolify 애플리케이션 템플릿** 또는 Ubuntu 24.04 LTS). SSH 키 인증만, 비밀번호 로그인 비활성.
2. 방화벽: 22(SSH, 내 IP 화이트리스트 권장)/80/443 만 개방.
3. Coolify: 원클릭 템플릿이면 설치 완료 상태. 수동이면 `curl -fsSL https://coolify.io/install.sh | bash` (설치 전 스크립트 검토, CISO).
4. DNS (Cloudflare): `*` A 레코드 → VPS IP, **DNS-only(grey cloud)**. (orange 면 LE HTTP-01 실패.)
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

### Coolify API 배포 레시피 (검증됨, Growth-35 2026-06-11)

토큰은 볼트(`infra/secrets/`)에서 `tr`로 값만 읽어 **SSH 암호 채널로 localhost:8000**에만 쓴다 (평문 HTTP 인터넷 미경유). 토큰 스코프는 **write+deploy** 필수 (read-only 면 POST 가 `Unauthenticated`).

```
T=$(sed -E 's/^COOLIFY_API_TOKEN=//' infra/secrets/preview-vps.env | tr -d ' \t\r\n')   # 값 비출력, ${#T}만 확인
ssh -i ~/.ssh/n9n_preview_ed25519 root@<ip> "COOLIFY_API_TOKEN='$T' bash -s" <<'EOF'
H="Authorization: Bearer $COOLIFY_API_TOKEN"; B="http://localhost:8000/api/v1"
# 1) 프로젝트            → {"uuid": project_uuid}
curl -s -X POST -H "$H" -H 'Content-Type: application/json' -d '{"name":"<slug>"}' "$B/projects"
# 2) 환경 uuid 조회      → environments[].uuid (자동생성 "production")
curl -s -H "$H" "$B/projects/<project_uuid>"
# 3) docker 이미지 앱 + 도메인 + 즉시배포  → {"uuid": app_uuid}
curl -s -X POST -H "$H" -H 'Content-Type: application/json' -d '{
  "project_uuid":"<p>","server_uuid":"<s>","environment_name":"production",
  "docker_registry_image_name":"<img>","docker_registry_image_tag":"latest",
  "ports_exposes":"80","domains":"https://<slug>.n9n.co.kr","instant_deploy":true
}' "$B/applications/dockerimage"
# 4) 정리: DELETE /applications/<app_uuid> (비동기 큐) → 완료 후 DELETE /projects/<project_uuid>
EOF
```

- 증명: `traefik/whoami` → `cicd-smoke.n9n.co.kr` 외부 HTTPS 200 + LE 정식 인증서(90일) ~45s. 삭제 후 도메인 503, 잔여 0.
- 서버 uuid `n12vdydjpwp81hu5i15n1gsb` (localhost). 와일드카드 `*.n9n.co.kr` grey-cloud 가 `<slug>` 서브도메인 DNS 를 자동 커버 → 앱별 DNS 추가 불필요.
- v1 다음: `scaffold.py` 산출 이미지를 `<img>` 자리에 → 한 명령으로 고객 preview 생성.

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
| Hostinger KVM 2 (Coolify preview, 싱가포르) | \$8.99/월 (24개월) | 2vCPU/8GB — 단일 VPS 다중 고객 프로젝트 격리 |
| 도메인 n9n.co.kr | 보유 | 갱신비 연 단위 |
| 와일드카드 TLS | \$0 | Let's Encrypt |
| 터널 (cloudflared, 데모 폴백) | \$0 | Cloudflare 무료 |

고객 수 증가 시 preview 동시 가동분만 선형 — Coolify 단일 VPS 격리로 상수화가 hedge. production 은 고객 인프라라 우리 비용 0.
