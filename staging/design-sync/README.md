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

## 역방향 (cloud → repo) pull 절차

claude.ai/design 이 `harness-design-system` sibling 레포에서 컴포넌트를 craft 한 후
main 레포로 역반입하는 경로:

```
claude.ai/design
  ─ DTCG export (tokens.json 또는 컴포넌트 HTML/CSS)
    ─ harness-design-system 에 커밋
      ─ 수동으로 staging/design-sync/<slug>/ 로 복사
        ─ python scripts/design/normalize.py staging/design-sync/<slug>
          ─ CDO 검수 후 design/tokens/ 또는 presets/ 에 반영
```

**staging 은 양방향 착지점**:

| 방향 | 경로 |
|---|---|
| main → cloud (순방향) | `export_system.py` → `harness-design-system/tokens/` |
| cloud → main (역방향) | cloud DTCG export → `staging/design-sync/<slug>/` → `normalize.py` |

역방향에서 컴포넌트 HTML 을 main 레포 adapter 에 **직접 복사 금지**.
반드시 `normalize.py` 게이트를 통과한 뒤 CDO 승인 후 반영한다.

### 순방향 (토큰 export) 실행

```bash
# main 레포 루트에서
python scripts/design/export_system.py [--target ../harness-design-system]

# sibling 레포에서 CSS 재빌드
cd ../harness-design-system && node build-tokens.mjs
```
