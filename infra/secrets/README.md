# Secret Vault — `infra/secrets/`

> 소유: `devops-agent` (DevOps, Growth-35). **이 디렉터리의 `.env`·키 파일은 전부 gitignored.** README 와 `*.example` 만 추적된다.

평문 자격증명/토큰/SSH 키는 **여기에만**. 레지스트리(`infra/registry/*.yaml`)엔 `secret_ref`(볼트 키 이름)만 둔다. 시크릿은 **chat·커밋·로그에 절대 노출 금지**.

## 규약

- 자원 1개 = `.env` 1개: `infra/secrets/<resource>.env` (예: `preview-vps.env`).
- 템플릿: 같은 이름 `.example` (값 없는 형태, 추적됨).
- 값 채우기는 **운영자가 본인 에디터/터미널로 직접** (Claude 세션을 거치지 않게 — 토큰이 transcript 에 남지 않도록).
- **불투명 토큰/키는 "값만 담은 전용 파일"로 둔다** (`KEY=value` 금지 — `=` 유무·접두어 포맷 추측이 노출 사고를 부름, Growth-35 2회). 예: `infra/secrets/coolify_api_token` 에 토큰 한 줄만.
- 사용 시 Claude 는 **값을 절대 출력하지 않는다**: `TOKEN=$(tr -d ' \t\r\n' < infra/secrets/coolify_api_token)` 로 읽고 **`${#TOKEN}` 길이만** 확인. `source`·`cut`·`xxd`·`cat` 등 내용을 찍을 수 있는 진단 금지.
- 읽기 실패(빈 값) 시 **포맷 추측 진단을 돌리지 말고** CEO 에게 파일 확인을 요청한다 (진단이 곧 노출).
- 로테이션: 토큰 재발급 시 파일만 교체. 유출 의심 시 즉시 Coolify/Hostinger 에서 revoke 후 재발급 (CISO 에스컬레이션).

## 현재 볼트 항목

| 파일 | 내용 | 비고 |
|---|---|---|
| `coolify_api_token` | Coolify API 토큰 **값만** (한 줄, 접두어·따옴표 없이) | Coolify 4.x. `tr` 로 읽음 |
| (SSH 키) | `~/.ssh/n9n_preview_ed25519` | repo 밖 operator-local |
