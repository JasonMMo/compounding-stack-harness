# Frontend Adapter Contract

> CTO 결정 (Growth-8). swappable-layers.md §6 의 compliance 게이트는 **backend** adapter (wire 응답을 *내는* HTTP 서버) 기준이다. Frontend adapter 는 반대 방향 — wire 요청을 **내는** UI 다. 이 문서가 모든 frontend adapter (vanilla-htmx / react / vue / nexacro) 의 단일 계약이다.

## 1. Frontend adapter 의 정체

```
Browser ──(HTML + 프레임워크 UI)──> [Frontend adapter] ──(wire HTTP)──> [Backend adapter]
                                         self-host thin server              (any backend)
```

Frontend adapter 는:
1. 사용자에게 generic CRUD UI 를 렌더한다 (14 baseline 도메인 공통 — entity_type 파라미터화).
2. 그 UI 의 상호작용을 **wire-protocol 요청**으로 직렬화해 `BACKEND_BASE_URL` 로 보낸다.
3. wire 응답 (성공 payload + error envelope) 을 자기 프레임워크 어법으로 렌더한다.

**backend 무관**: frontend adapter 는 어떤 backend adapter 와도 동작해야 한다. backend 종류를 알지 못한다 — wire contract 만 안다.

## 2. 불변 원칙 (G-1 / swappable §4 계승)

Frontend adapter 는 `middle/contract/*` 를 **읽기만** 한다. 재구현 금지:

- 엔드포인트 경로·요청 필드·error code 집합을 adapter 안에 **하드코딩하지 않는다** — `wire-v1.yaml` / `codes.yaml` 에서 읽는다 (backend 의 `ContractLoader` 와 동형).
- error code → 사용자 메시지 매핑을 adapter 가 재선언하지 않는다 — `codes.yaml` 의 `message` / `message_ko` 를 읽는다.

## 3. 요청 직렬화 — 4 필수 준수점

| # | 준수점 | 규약 |
|---|---|---|
| **F-1** | **flat-underscore 쿼리** | HTTP query 로 실리는 중첩 필드는 underscore 평탄화 (`paging.mode`→`paging_mode`, `sort.field`→`sort_field`). wire-v1.yaml 헤더 코멘트 (Growth-7) 가 단일 진실. JSON body transport 는 중첩 객체 그대로 가능. |
| **F-2** | **paging 2모드** | offset (`paging_mode=offset&paging_page=&paging_size=`) + cursor (`paging_mode=cursor&paging_cursor=`) 둘 다 발신 가능. cursor 응답의 `next_cursor` 를 다음 요청에 반영. |
| **F-3** | **error envelope 렌더** | wire 응답의 `error.code` 로 분기 (message 텍스트로 분기 금지). `code` → `codes.yaml` 의 `message_ko` (한국어 baseline) 를 사용자에게 표시. `retriable: true` 코드는 재시도 UI (예: RATE_LIMITED → 백오프 안내) 제공 가능. |
| **F-4** | **idempotent 의미 보존** | `entity.delete` 2회 호출 둘 다 success 로 렌더 (404→success 표준). 사용자에게 "이미 삭제됨" 을 오류로 표시하지 않는다. |

## 4. Compliance 게이트 (frontend 판)

새 frontend adapter 머지 조건. backend 의 black-box HTTP suite 와 다른 차원:

1. **F-1 직렬화 검증**: adapter 가 보낸 실제 HTTP 요청을 캡처해 paging/sort 가 flat-underscore 인지 단언. (캡처 방법: thin server 의 outbound 요청 로깅, 또는 mock backend 가 받은 쿼리 검사.)
2. **F-3 envelope 렌더 검증**: backend 가 각 error code 를 반환했을 때 adapter UI 가 해당 `message_ko` 를 표시하고 `code` 로 올바르게 분기하는지.
3. **F-2 paging 검증**: offset 마지막 페이지 + cursor 양쪽 UI 흐름.
4. **L1+L3+L4**: L1 (있으면 단위테스트), L3 (build/번들), L4 live (frontend + backend 둘 다 기동 → 실제 화면 렌더). L2 (JDBC) 는 frontend 비해당.

테스트 위치: `tests/adapters/<frontend-kind>/`. backend 의 `ADAPTER_BASE_URL` 파라미터화 패턴 계승 — `FRONTEND_BASE_URL` + `BACKEND_BASE_URL` 2개로 live 검증.

## 5. 디자인 토큰 소비 (CDO 계약)

Frontend adapter 의 비주얼은 `design/tokens/` 단일 진실에서 온다:

- `raw.json` → semantic 참조 (`{color.accent.600}`) 해소 → CSS custom property 생성 (`--color-primary: …`).
- `semantic.json` 만 컴포넌트가 사용 (raw hex 직접 박기 금지 — CDO 원칙 #1).
- 페르소나 override 는 `[data-persona="ceo|ops|it"]` 스코프 블록. merge 순서 raw → semantic → persona.
- 토큰 → CSS 생성기는 **adapter 의 build 단계** 책임 (engineer). 토큰 JSON 은 CDO 가 소유, 생성 로직은 adapter 가 소유 — 재선언이 아니라 *소비*.

생성 규약 상세: [`design/tokens/README.md`](../../design/tokens/README.md).

## 6. 최소 화면 세트 (M1)

vanilla-htmx 첫 adapter 가 데모해야 하는 화면 (entity_type 파라미터화로 14 도메인 공통):

- **list** — 페이징 테이블 (offset 기본), 필터, 정렬.
- **detail / edit** — 단건 read + update 폼.
- **create** — 신규 폼.
- **delete** — 확인 후 idempotent 삭제.
- **login** — auth.login → token 보관.
- **(선택) health** — status.health 표시.

페르소나 분기 (CDO): 같은 entity 도 CEO=요약 카드 / ops=입력 폼 / it=raw 테이블. M1 vanilla-htmx 는 ops 페르소나 (입력 폼) 를 기본으로 구현, 나머지는 `data-persona` 스위치로 후속.

## 7. Open

- F-1 직렬화 자동 캡처 방식 (outbound 로깅 vs mock backend) — QA 가 frontend compliance suite 작성 시 확정.
- react/vue adapter 의 토큰 소비 (CSS custom property vs CSS-in-JS) — 해당 adapter Growth 시점.
- nexacro adapter — M2 이후 (한국 SI 진입 시점, 이전 repo 자산 포팅).
