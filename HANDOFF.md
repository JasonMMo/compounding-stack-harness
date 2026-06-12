# HANDOFF — 2026-06-12 (Growth-41: design/templates 구조 구축 + profile ui_theme)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.
> **다음 작업 = KRDS GitHub 직접 분석 → KRDS 기반 public-sector 테마 적용 검토, 실 고객 발굴 (M2 게이트)**

## ▶▶▶ 복귀 직후 상태 (확인용)

- **Git**: clean, master 동기화 (HEAD = tab-form.html 커밋 c3a9a12).
- **팀**: 9-인격 (DevOps 합류). `Agent(subagent_type="devops-agent"|"engineer-agent"|"security-agent", ...)` 직접 spawn 가능.
- **★ preview VPS LIVE**: Hostinger KVM 2 `187.77.140.157` (싱가포르, $8.99/월 24mo). SSH `ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157` (키 인증만). Coolify 4.1.2 healthy (server uuid `n12vdydjpwp81hu5i15n1gsb`). `*.n9n.co.kr` 자동 HTTPS·**Coolify API CI/CD end-to-end 검증 완료**. **8000/8080/6001/6002 클라우드 방화벽 차단(allow 22/80/443) — CISO 잔여 0.** 대시보드는 SSH `-L 8000:localhost:8000` 터널.
- **Coolify API 토큰**: `infra/secrets/preview-vps.env` (raw 값, gitignored, write+deploy 스코프). `sed -E 's/^COOLIFY_API_TOKEN=//' | tr -d ' \t\r\n'` 로 읽고 `${#TOKEN}` 길이만 확인 — **내용 절대 비출력**(`cat`/`cut`/`xxd`/`source` 금지).
- **codegraph MCP** ✔ — `mcp__codegraph__*`. 의존 작업 전 `codegraph sync` 권장.
- **context-mode** 활성 — 큰 출력은 `ctx_execute`/`ctx_execute_file`, mutation·git·navigation 만 Bash.
- **WebFetch/WebSearch deny** — `.claude/settings.json` 에 deny 설정됨. KRDS GitHub 분석은 codegraph 또는 로컬 클론 후 분석.
- **가드**: 13개, 0 real FAIL (G-2/G-3 SPEC). 실행 시 `PYTHONIOENCODING=utf-8` 권장.

## ▣ Growth-41 (이번 세션) — design/templates 구조 구축 + profile ui_theme

- **profile schema**: `profiles/_README.md` — `stack.ui_theme` 키 추가. `saas`(기본, Pico+tokens) / `public-sector`(KRDS CDN) 분기 체계 확립.
- **design/templates/dense-table.html**: Fixed Header(sticky top) + Fixed Column(sticky left) + Hover Action(opacity 0→1) + 페이지네이션 바. vanilla CSS only, JS 의존 0. 한국 SI/공공 Dense Table 패턴 구현.
- **design/templates/tab-form.html**: 수평 탭 헤더 + 탭별 폼 패널 + 2열 form-grid. eGovFrame 표준 레이아웃 호환. 탭 전환 JS 12줄.
- **커밋**: 1ed1a21(profile) → c3df9a3(dense-table) → c3a9a12(tab-form), 3건 pushed.

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

1. **★ KRDS GitHub 직접 분석** — `git clone https://github.com/KRDS-uiux/krds-uiux` 로컬 클론 후 컴포넌트 목록 확인 (table/tree-menu/tab 포함 여부). WebFetch deny 우회: Bash git clone 사용.
2. **★ public-sector 테마 적용** — KRDS 컴포넌트 확인 후 `design/templates/krds-table.html` + `design/templates/krds-tab.html` 제작. `stack.ui_theme: public-sector` 프로파일에서 CDN 자동 주입.
3. **★ 실 고객 발굴 (M2 게이트)** — 숨고/크몽 첫 의뢰. 인프라·데모·UI 준비 완료.
4. **자동화 잔여 (낮은 우선순위)**: webhook 보류 / SECRET_KEY rotate / G-14 stale-anchor.

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Sonnet 4.6` (현 모델) / master push CTO 자동 (private repo). `--no-verify`/`--no-gpg-sign` 금지.
- **시크릿 절대 chat·커밋 금지** — 볼트 `infra/secrets/*`(gitignored).
- Windows `NUL` 파일 주의: `> /dev/null` 오용 시 `NUL` 파일 생성.
- 환경: Node v24 ✓ / Python 3.14 ✓ / JDK 21 ✓ / Docker ✓ / WSL postgres ✓ / codegraph 0.9.9 ✓ / codex CLI 0.118.0 ✓.
