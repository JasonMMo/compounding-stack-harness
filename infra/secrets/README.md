# Secret Vault — `infra/secrets/`

> 소유: `devops-agent` (DevOps, Growth-35). **이 디렉터리의 `.env`·키 파일은 전부 gitignored.** README 와 `*.example` 만 추적된다.

평문 자격증명/토큰/SSH 키는 **여기에만**. 레지스트리(`infra/registry/*.yaml`)엔 `secret_ref`(볼트 키 이름)만 둔다. 시크릿은 **chat·커밋·로그에 절대 노출 금지**.

## 규약

- 자원 1개 = `.env` 1개: `infra/secrets/<resource>.env` (예: `preview-vps.env`).
- 템플릿: 같은 이름 `.example` (값 없는 형태, 추적됨).
- 값 채우기는 **운영자가 본인 에디터/터미널로 직접** (Claude 세션을 거치지 않게 — 토큰이 transcript 에 남지 않도록).
- 사용 시 Claude 는 `set -a; . infra/secrets/<file>.env; set +a` 로 **출력 없이 env 주입**, 값을 echo 하지 않는다.
- 로테이션: 토큰 재발급 시 파일만 교체. 유출 의심 시 즉시 Coolify/Hostinger 에서 revoke 후 재발급 (CISO 에스컬레이션).

## 현재 볼트 항목

| 파일 | 내용 | 비고 |
|---|---|---|
| `preview-vps.env` | `COOLIFY_API_TOKEN` (+ 선택 `VPS_ROOT_PW`) | Hostinger KVM 2 / Coolify 4.x |
| (SSH 키) | `~/.ssh/n9n_preview_ed25519` | repo 밖 operator-local |
