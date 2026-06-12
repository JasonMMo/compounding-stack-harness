# HANDOFF — 2026-06-12 (Growth-46: research-loop skill 정비 + commands 3개 신설)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.
> **다음 작업 = 실 고객 발굴 (M2 게이트) — 인프라·디자인·UI·파이프라인·KRDS 전 구간 완료. 막는 건 영업뿐.**

## ▶▶▶ 복귀 직후 상태 (확인용)

- **Git**: clean, master 동기화 (HEAD = tab-form.html 커밋 c3a9a12).
- **팀**: 9-인격 (DevOps 합류). `Agent(subagent_type="devops-agent"|"engineer-agent"|"security-agent", ...)` 직접 spawn 가능.
- **★ preview VPS LIVE**: Hostinger KVM 2 `187.77.140.157` (싱가포르, $8.99/월 24mo). SSH `ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157` (키 인증만). Coolify 4.1.2 healthy (server uuid `n12vdydjpwp81hu5i15n1gsb`). `*.n9n.co.kr` 자동 HTTPS·**Coolify API CI/CD end-to-end 검증 완료**. **8000/8080/6001/6002 클라우드 방화벽 차단(allow 22/80/443) — CISO 잔여 0.** 대시보드는 SSH `-L 8000:localhost:8000` 터널.
- **Coolify API 토큰**: `infra/secrets/preview-vps.env` (raw 값, gitignored, write+deploy 스코프). `sed -E 's/^COOLIFY_API_TOKEN=//' | tr -d ' \t\r\n'` 로 읽고 `${#TOKEN}` 길이만 확인 — **내용 절대 비출력**(`cat`/`cut`/`xxd`/`source` 금지).
- **codegraph MCP** ✔ — `mcp__codegraph__*`. 의존 작업 전 `codegraph sync` 권장.
- **context-mode** 활성 — 큰 출력은 `ctx_execute`/`ctx_execute_file`, mutation·git·navigation 만 Bash.
- **WebFetch/WebSearch deny** — `.claude/settings.json` 에 deny 설정됨. KRDS GitHub 분석은 codegraph 또는 로컬 클론 후 분석.
- **가드**: 13개, 0 real FAIL (G-2/G-3 SPEC). 실행 시 `PYTHONIOENCODING=utf-8` 권장.

## ▣ Growth-46 (이번 세션) — research-loop skill 정비 + commands 3개

- **skill-creator 적용**: research-loop SKILL.md description pushy 강화, references/ 분리 구조 완성.
  - 반론 메모: workflow 스킬에 full eval 루프는 비효율 — 정성 평가로 충분. 다음부터 사전 반론 제기.
- **commands 신설** (모두 `.claude/commands/research/`):
  - `research:fetch` — `ctx_fetch_and_index` 래퍼, raw 결과 대화 차단
  - `research:query` — `ctx_search` 배치 래퍼, 해석 후 요약만 반환
  - `research:wiki-save` — wiki 환류 강제 (프론트매터+index+커밋 일관성) ← 프로젝트 레벨 (global 배치 반론 제기 후 수정)
- **references 추가**: `.claude/skills/research-loop/references/context-mode-guide.md` — ctx 도구 선택 계층
- **커밋**: 0320f2e(SKILL) → b487399(guide) → 460f8af(fetch) → 8f7476f(query) → 7968bf5(wiki-save), 5건

## ▣ Growth-45 (이번 세션) — 리서치 자산 wiki 환류

- **문제**: deep-research 결과(`out/analysis/design/korean-ui-research.md`)가 gitignored `out/`에만 있어 자산 미누적.
- **조치**: `knowledge/wiki/design/korean-ui-patterns.md` 신규 생성 (SYNTHESIZED) — KRDS 74개 컴포넌트·3대 패턴·대기업 디자인 시스템·harness 통합 현황 전부 수록.
- **wiki index**: `Design` 섹션 추가. `build_graph.py` 재생성 (nodes=6, edges=10).
- **커밋**: 7ec9637(wiki 페이지) → 5e91131(index), 2건.

## ▣ Growth-44 (직전 세션) — base.html KRDS CDN 분기 완성

- **Dockerfile**: `ENV UI_THEME=$UI_THEME` 추가 — build ARG → runtime env 전파.
- **server.py**: `UI_THEME = os.environ.get("UI_THEME", "saas")` + context processor `ui_theme` 주입 → 모든 Jinja2 템플릿에서 `{{ ui_theme }}` 참조 가능.
- **base.html**: `{% if ui_theme == 'public-sector' %}` 분기 — KRDS CDN(krds.min.css + krds.min.js defer) / `{% else %}` Open Props + Pico + tokens.css.
- **커밋**: 72bd8d9(Dockerfile ENV) → 9559eca(server) → e341305(base.html), 3건.
- **전 구간 완성**: profile `stack.ui_theme: public-sector` → compose `UI_THEME: public-sector` → Dockerfile build → tokens.css(Pico 스킵) → runtime ENV → base.html KRDS CDN 로드.

## ▣ Growth-43 (직전 세션) — preview_package.py public-sector 파이프라인

- **Dockerfile**: `ARG UI_THEME=saas` + `RUN python build_tokens.py --ui-theme $UI_THEME` — build time에 테마 결정.
- **preview_package.py**: `_get_ui_theme(slug)` 헬퍼 (profile `stack.ui_theme` 읽기, 기본 `saas`). `write_coolify_compose()` / `write_compose()` 에 `ui_theme` 파라미터 추가. 양쪽 compose 템플릿 frontend `build.args: UI_THEME: {ui_theme}` 주입.
- **기존 compose 재생성**: lawfirm-demo / shop-demo / edu-program — 모두 `UI_THEME: saas` 추가됨. 하위호환 유지.
- **검증**: `python preview_package.py --profile lawfirm-demo --coolify` → `UI_THEME: saas` 주입 확인.
- **public-sector 고객 적용 방법**: profile 에 `stack.ui_theme: public-sector` 추가 → `preview_package.py --profile <slug> --coolify` → compose 에 `UI_THEME: public-sector` 자동 → Dockerfile build 시 Pico override 스킵 + KRDS CDN 주석 포함 tokens.css 생성.
- **커밋**: e71b3e0(Dockerfile) → c47d243(preview_package) → e6fd9d5→00baa2d→d18bf60(compose 3건), 5건.

## ▣ Growth-42 (직전 세션) — KRDS 분석 + 정적/동적 public-sector 분기

- **KRDS 클론**: `D:\AI\workspace\krds-uiux` (분석 전용). 74개 컴포넌트. CDN jsDelivr 2파일.
- **핵심**: KRDS table = semantic (Fixed Header 없음) → `dense-table.html` 유지. tab/side_nav = `krds.min.js` 자동.
- **정적 스니펫**: `design/templates/krds-tab.html` / `krds-table.html` / `krds-side-nav.html`.
- **동적**: `token_css_generator.generate(ui_theme=...)`, `build_tokens.py --ui-theme`.

## ▣ Growth-41 (직전 세션) — design/templates 구조 구축 + profile ui_theme

- **profile schema**: `profiles/_README.md` — `stack.ui_theme` 키 추가.
- **design/templates/dense-table.html**: Fixed Header+Column+Hover Action+페이지네이션. vanilla CSS only.
- **design/templates/tab-form.html**: 탭 기반 폼 + 2열 form-grid. eGovFrame 호환.

## ▣ Growth-40 (직전 세션) — 한국 업무용 UI 디자인 리서치

- **리서치 완료**: deep-research 2회 (B2B SaaS/공공 SI + 대기업 디자인 시스템). 결과: `out/analysis/design/korean-ui-research.md`
- **핵심 발견**: ① KRDS(행정안전부, 2025년 의무화) — 빌드 없는 CDN, 공공 SI 고객 영업 포인트 ② 한국 SI 3대 패턴: Dense Table / 좌측 트리메뉴(구현 완료) / 탭 기반 화면 ③ 대기업 공통: semantic 토큰 계약 + variant 체계
- **설정 추가**: `.claude/settings.json` — WebFetch/WebSearch deny (API 자동 사용 차단)

## ▣ 이전 세션 요약 (Growth-35~39) — 참조용

- **G-39**: 아코디언 사이드바 + Hostinger 라이트테마 + 테이블 스타일 (edu-program.n9n.co.kr PASS)
- **G-38**: 영업 루프 풀사이클 리허설 — intake→preview 전 구간 실데이터 검증, edu-program live, 건1 scope-confirm 안내문 발송 대기
- **G-37**: 웹 intake 인터페이스 (intake.n9n.co.kr live), CISO 게이트 첫 완주
- **G-36**: 디자인 Phase 0+1 (Pretendard+Pico+Open Props), 504 인시던트 근본 해결
- **G-35**: DevOps 9번째 인격 신설, Hostinger KVM2 + Coolify + CI/CD end-to-end 검증

## 다음 후보

1. **★ 실 고객 발굴 (M2 게이트)** — 숨고/크몽 첫 의뢰. 인프라·디자인·UI·파이프라인 전 구간 준비 완료. 막는 건 영업뿐.
2. **자동화 잔여 (낮은 우선순위)**: webhook 보류 / SECRET_KEY rotate / G-14 stale-anchor.
4. **KRDS 클론 정리**: `D:\AI\workspace\krds-uiux` 분석 완료 → 필요 시 삭제 가능.

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Sonnet 4.6` (현 모델) / master push CTO 자동 (private repo). `--no-verify`/`--no-gpg-sign` 금지.
- **시크릿 절대 chat·커밋 금지** — 볼트 `infra/secrets/*`(gitignored).
- Windows `NUL` 파일 주의: `> /dev/null` 오용 시 `NUL` 파일 생성.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ / WSL postgres ✓ / codegraph 0.9.9 ✓ / codex CLI 0.118.0 ✓.
