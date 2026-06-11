# Digital Asset Registry — `infra/registry/`

> 소유: `devops-agent` (DevOps, Growth-35). 토폴로지: [`../../docs/architecture/deployment-topology.md`](../../docs/architecture/deployment-topology.md).

1인이 N 고객의 디지털 자산을 추적하는 단일 진실. "어느 고객이 어느 서브도메인·VPS·인증서·설치 상태인가" 를 1초 안에 답한다.

## 규약

- 고객 1명 = 파일 1개: `infra/registry/<slug>.yaml` (slug 은 ASCII, G-8 준수).
- 공유 인프라 (VPS·도메인) 는 `infra/registry/_shared.yaml`.
- **시크릿 평문 절대 금지** — `secret_ref` 에 **볼트 키 이름만** 기록. 평문 자격증명/토큰/키는 `infra/secrets/` (gitignored) 에만. CISO 시크릿 스캔과 정렬.
- 템플릿: [`_template.yaml`](_template.yaml).

## 필드

| 필드 | 의미 |
|---|---|
| `slug` | 고객 식별자 (ASCII) |
| `preview.subdomain` | `<slug>.n9n.co.kr` |
| `preview.coolify_project` | Coolify 프로젝트 이름 |
| `preview.status` | provisioning / live / retired |
| `production.install_method` | remote / onsite |
| `production.installed_at` | 설치 일자 (인도 완료 시) |
| `secret_ref` | 볼트 키 이름 (평문 ✗) |
| `cost_note` | 이 고객 귀속 인프라 비용 메모 (§5 환류) |
