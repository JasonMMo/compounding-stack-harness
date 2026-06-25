# staging/design-sync — claude.ai/design 동기화 작업 영역

> Design-Cloud Bridge 의 **transient 작업 영역**. `/design-sync` 로 cloud 에서 내려온
> 컴포넌트가 여기 착지하고, `scripts/design/normalize.py` 가 읽어 토큰/variant 후보를 추출한다.
> 설계: [`docs/architecture/design-cloud-bridge.md`](../../docs/architecture/design-cloud-bridge.md) §3.

## 규약

- 컴포넌트 1건 = `staging/design-sync/<component-slug>/` (HTML/CSS).
- **이 디렉터리의 내용물은 gitignore** (이 README 만 추적) — 동기화 산출은 transient,
  production 진실은 정규화 후 `design/tokens/` · `presets/themes/` · `presets/site-sections/` 에.
- 컴포넌트 HTML 을 `frontend/adapters/*/` 로 **직접 복사 금지** — 반드시 정규화 게이트 경유
  (G-정규화게이트 가드가 차단, WP-2).

## 흐름

```
/design-sync ──▶ staging/design-sync/<slug>/  ──normalize.py──▶ 정규화 리포트(CDO 검수)
                                                                    │
                                              theme.yaml override + catalog variants
```

## 사용

```bash
python scripts/design/normalize.py staging/design-sync/<slug>
```
