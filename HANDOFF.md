# HANDOFF — 2026-06-12 (Growth-42: KRDS 컴포넌트 분석 + 정적/동적 public-sector 분기)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.
> **다음 작업 = preview_package.py public-sector 분기 (Dockerfile CDN 주입) OR 실 고객 발굴 (M2 게이트)**

## ▶▶▶ 복귀 직후 상태 (확인용)

- **Git**: clean, master 동기화 (HEAD = tab-form.html 커밋 c3a9a12).
- **팀**: 9-인격 (DevOps 합류). `Agent(subagent_type="devops-agent"|"engineer-agent"|"security-agent", ...)` 직접 spawn 가능.
- **★ preview VPS LIVE**: Hostinger KVM 2 `187.77.140.157` (싱가포르, $8.99/월 24mo). SSH `ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157` (키 인증만). Coolify 4.1.2 healthy (server uuid `n12vdydjpwp81hu5i15n1gsb`). `*.n9n.co.kr` 자동 HTTPS·**Coolify API CI/CD end-to-end 검증 완료**. **8000/8080/6001/6002 클라우드 방화벽 차단(allow 22/80/443) — CISO 잔여 0.** 대시보드는 SSH `-L 8000:localhost:8000` 터널.
- **Coolify API 토큰**: `infra/secrets/preview-vps.env` (raw 값, gitignored, write+deploy 스코프). `sed -E 's/^COOLIFY_API_TOKEN=//' | tr -d ' \t\r\n'` 로 읽고 `${#TOKEN}` 길이만 확인 — **내용 절대 비출력**(`cat`/`cut`/`xxd`/`source` 금지).
- **codegraph MCP** ✔ — `mcp__codegraph__*`. 의존 작업 전 `codegraph sync` 권장.
- **context-mode** 활성 — 큰 출력은 `ctx_execute`/`ctx_execute_file`, mutation·git·navigation 만 Bash.
- **WebFetch/WebSearch deny** — `.claude/settings.json` 에 deny 설정됨. KRDS GitHub 분석은 codegraph 또는 로컬 클론 후 분석.
- **가드**: 13개, 0 real FAIL (G-2/G-3 SPEC). 실행 시 `PYTHONIOENCODING=utf-8` 권장.

## ▣ Growth-42 (이번 세션) — KRDS 분석 + 정적/동적 public-sector 분기 완성

- **KRDS 클론 분석**: `D:\AI\workspace\krds-uiux` (shallow clone, 분석 전용). 74개 컴포넌트 확인. CDN 2파일 (`krds.min.css` 579KB / `krds.min.js` 183KB). jsDelivr 한 줄.
- **핵심 발견**: KRDS table = semantic (Fixed Header 없음) → 우리 `dense-table.html` 별도 유지 필요. tab/side_navigation = `krds.min.js` 자동 동작.
- **정적 스니펫 3개**: `design/templates/krds-tab.html` / `krds-table.html` / `krds-side-nav.html` — KRDS 원본 마크업 + CDN 주석 + saas vs public-sector 비교 가이드.
- **동적 분기**: `token_css_generator.generate(ui_theme="saas"|"public-sector")` — `public-sector` 시 Pico override 106줄 스킵 + KRDS CDN 주석 삽입. `build_tokens.py --ui-theme` CLI arg.
  - 검증: `saas` 366줄·365 props / `public-sector` 260줄·237 props ✓
- **커밋**: 1ed1a21→c3df9a3→c3a9a12(G-41) → 9c0d303→c44424c→8a0ff66→b23ee25→8c1ab94(G-42), 8건 pushed.

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

1. **★ preview_package.py public-sector 분기** — profile `stack.ui_theme` 읽어 Dockerfile의 `RUN python build_tokens.py` 에 `--ui-theme public-sector` 자동 주입 + base.html 에 KRDS CDN `<link>`/`<script>` 삽입. 파이프라인 마지막 조각.
2. **★ 실 고객 발굴 (M2 게이트)** — 숨고/크몽 첫 의뢰. 인프라·디자인·UI 준비 완료.
3. **자동화 잔여 (낮은 우선순위)**: webhook 보류 / SECRET_KEY rotate / G-14 stale-anchor.
4. **KRDS 클론 정리**: `D:\AI\workspace\krds-uiux` 분석 완료 → 필요 시 삭제 가능.

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Sonnet 4.6` (현 모델) / master push CTO 자동 (private repo). `--no-verify`/`--no-gpg-sign` 금지.
- **시크릿 절대 chat·커밋 금지** — 볼트 `infra/secrets/*`(gitignored).
- Windows `NUL` 파일 주의: `> /dev/null` 오용 시 `NUL` 파일 생성.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ / WSL postgres ✓ / codegraph 0.9.9 ✓ / codex CLI 0.118.0 ✓.
