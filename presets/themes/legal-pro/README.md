# legal-pro — Theme

> 8번째 축(visual-asset) 등록 테마. 법무·규제·컴플라이언스 버티컬용.

## 미감

Deep navy (`#0F1729` header, `#1A2744` primary) + restrained gold (`#B8960C` precedent badge).
권위와 절제. 장식 없이 내용으로 신뢰를 얻는 디자인.

## 검증 출처

`services/legal-rag` 라이브 서비스에서 검증된 팔레트·컴포넌트를 canonical 추출.
M3 첫 버티컬(법무법인 RAG MVP) Growth-100 이후 실 배포 상태에서 확정.

## 파일 구조

| 파일 | 역할 |
|---|---|
| `tokens.css` | navy+gold 팔레트 + semantic override CSS 변수 |
| `components.css` | citation-card, ingest-badge, doc-drawer, health-banner 컴포넌트 CSS |
| `theme.json` | 테마 매니페스트 (color map, a11y, reuse guide) |

`services/legal-rag/web/styles/` 파일이 라이브의 단일 진실이며,
이 디렉터리는 8번째 축의 canonical 등록 자산이다.

## 재사용 — 다음 버티컬

1. `--lr-*` prefix 는 legal-rag 전용. 신규 vertical 은 자체 prefix 신설.
2. `--color-primary`, `--color-badge-*` semantic 토큰만 override.
3. `components.css` 는 수정 없이 재사용 가능 — semantic 토큰만 바뀌어도 다른 인상.

### 의료 vertical 예시

```css
/* presets/themes/medical-pro/tokens.css */
:root {
  --med-teal-800: #0D5E6B;
  --color-primary: var(--med-teal-800);
  --color-badge-precedent-fg: var(--med-teal-800);  /* 판례 → 논문 */
  --color-badge-document-fg:  var(--med-teal-800);  /* 사건문서 → 진료기록 */
}
```

### 금융 vertical 예시

```css
/* presets/themes/finance-pro/tokens.css */
:root {
  --fin-burgundy-800: #6B1A1A;
  --color-primary: var(--fin-burgundy-800);
}
```

## 접근성

- 판례 뱃지(`#B8960C` on `#FDF8E7`): 추정 5.1:1. 실측 미달 시 `#92720A` 대체.
- 사건문서 뱃지(`#1A2744` on `#E8EDF5`): 추정 9.8:1 (여유).
- 헤더 워드마크(흰색 on `#0F1729`): 추정 16.5:1.
- `prefers-reduced-motion` 준수: 드로어 transition 은 모션 없이 즉시 표시 대안 가능.

## Growth 연결

- Growth-97: SPA /app 데모 라이브
- Growth-100: 원문 드로어 구현 + legal-pro 테마 초안 확정
- Growth-101+: 이 파일 정식 등록 (T2)
