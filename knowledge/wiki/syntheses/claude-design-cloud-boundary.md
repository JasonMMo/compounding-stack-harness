---
title: claude.ai/design ↔ repo 분리·통합 경계 (Design-Cloud Bridge)
type: synthesis
created: 2026-06-26
updated: 2026-06-26
sources: [deep-research-design-cloud-2026-06]
---

# claude.ai/design 을 내부 디자인 워크벤치로 쓸 때의 경계

디자인 craft 를 클라우드 툴(Claude Design, `/design-sync`)에서 빠르게 하되, 우리 복리 자산과
고객 인도물은 클라우드에서 분리한다. 전체 아키텍처는 [`docs/architecture/design-cloud-bridge.md`](../../../docs/architecture/design-cloud-bridge.md).

## 왜 분리가 강제인가 (외부 사실)

- **[EXTRACTED]** Claude Design 은 **BAA 적용 제외**(beta 태그) — Enterprise 라도 HIPAA/규제데이터
  보장 밖. 출처: support.claude.com BAA 문서(8114513, 15455031, modified 2026-06).
- **[EXTRACTED]** 기본 프라이버시 정책(eff. 2026-07-08)은 Input/Output **학습 사용 허용**(opt-out
  가능, 단 ①안전검토 플래그 ②사용자 신고는 opt-out 무시). Enterprise 는 별도 고객계약. 출처: anthropic.com/legal/privacy.
- **[EXTRACTED]** 서드파티 커넥터/외부 API 전달 시 해당 정책 적용 + 정부요청 대응 정책 존재 →
  업로드물 법적 disclosure 대상 가능.
- **[INFERRED]** ∴ 의뢰인 PII·변호사-의뢰인 자료·고객 실데이터는 **클라우드 워크벤치에 절대 도달 금지**.
  넘어오는 유일 산출물 = 정규화된 토큰 JSON.

## 경계 메커니즘 (표준)

- **[EXTRACTED]** DTCG JSON 포맷 first stable **2025.10**, 벤더중립 interop, alias/2-layer 지원.
  단 W3C **Community Group** deliverable(완전한 Recommendation 아님) → "W3C 표준 준수" 광고 금지.
- **[EXTRACTED]** Style Dictionary **v5+**(v5.5.0, 2026-06-21)에 DTCG v2025.10 지원. `include`(공유 base)
  /`source`(고객 override) 패턴 = 복제본 빌드 프리미티브.
- **[EXTRACTED]** Storybook Package Composition = 디자인시스템 분리-발행 패턴(자체 npm 패키지+호스팅 Storybook).
- **[EXTRACTED]** vercel/platforms 멀티테넌트는 **런타임** 라우팅(Redis). self-host 프라이버시 우선엔
  **반대**(빌드타임 정적 per-customer 빌드=물리격리)가 우월. 우리 landing-astro SSG 와 정합.

## 우리 적용 (3 결론)

1. **[INFERRED]** 우리 토큰 계층(raw→semantic→theme.yaml→persona)이 이미 DTCG 2-layer 와 정합 →
   **이 계층이 곧 경계**. 새 표준 신설 0 (복리). cf. [[korean-ui-patterns]] 토큰 소비.
2. **[INFERRED]** 클라우드 = authoring-only(무명 컴포넌트만), repo = single source. 컴포넌트 HTML 은
   **정규화 게이트**(CDO 가 catalog variant + 토큰으로 분해) 통과해야 머지. 미통과 직접붙임 = axis-8 붕괴.
3. **[INFERRED]** 고객 복제본 = 빌드타임 정적 물리격리(landing-astro SSG + 고객 theme.yaml/profile 주입,
   구조변경 0). 인도 번들에 claude.ai 참조·타 테넌트 slug·raw PII 가 **0** 이어야 함 → CI 가드 5종이 강제.

## 미해결 / 재검증 (caveats)

- **[UNVERIFIED]** Claude Design beta 졸업 시 BAA 적용 개선 가능 → **legal 고객 engagement 전 재검증**.
- 프라이버시 정책은 2026-07-08 개정판 — 시점별 차이 주의.
- DTCG 는 Recommendation 아님 / Style Dictionary 는 **v5+ 핀**(v4 는 옛 draft).
