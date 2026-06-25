---
title: deep-research — claude.ai/design 분리·통합 (2026-06)
type: source
created: 2026-06-26
updated: 2026-06-26
sources: []
---

# deep-research 리포트 — claude.ai/design ↔ repo 분리·통합 아키텍처

deep-research 하니스 (fan-out 웹서치 → 페칭 → 3-vote adversarial 검증 → 합성), 2026-06-25/26 실행.
원본 초안: `out/deep-research-design-cloud.json` (gitignored — 소멸 위험, 본 페이지가 환류 진입점).

- **질문**: claude.ai/design(Claude Design, `/design-sync`)을 self-host 복리 monorepo 와 분리·통합하고
  고객 복제본을 전달하는 아키텍처.
- **결과**: 8 findings (6 high / 1 medium 합성), caveats 5종. 합성·인용은 [[claude-design-cloud-boundary]].
- **검증**: 주장당 3-vote, 2/3 refute 시 kill. 일부 verify 에이전트는 1M-context 크레딧 부재로 실패(영향 경미).

## 1차 출처 (fetched live)

- anthropic.com/pricing · /legal/privacy
- support.claude.com BAA: articles 8114513, 15455031
- support.anthropic.com privacy-legal
- designtokens.org · tr.designtokens.org/format
- styledictionary.com (+ /info/architecture, /info/dtcg) · github.com/style-dictionary
- storybook.js.org/docs/sharing/package-composition
- github.com/vercel/platforms
