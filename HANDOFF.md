# HANDOFF — 2026-06-12 (Growth-46: research-loop skill 정비 + commands 3개)

> 다음 세션 인계. 단일 진실은 `learn-log.md` + `docs/learn-logs/<role>.md` — 이 파일은 *지금 어디고 다음은 뭔지*만.
> **다음 작업 = 실 고객 발굴 (M2 게이트) — 인프라·디자인·UI·파이프라인·KRDS 전 구간 완료. 막는 건 영업뿐.**

## ▶▶▶ 복귀 직후 상태 (확인용)

- **Git**: clean, master 동기화 (HEAD = 80d7b93, HANDOFF Growth-46).
- **팀**: 9-인격 (DevOps 합류). `Agent(subagent_type="devops-agent"|"engineer-agent"|"security-agent", ...)` 직접 spawn 가능.
- **★ preview VPS LIVE**: Hostinger KVM 2 `187.77.140.157` (싱가포르, $8.99/월 24mo). SSH `ssh -i ~/.ssh/n9n_preview_ed25519 root@187.77.140.157` (키 인증만). Coolify 4.1.2 healthy. `*.n9n.co.kr` 자동 HTTPS. **Coolify API CI/CD end-to-end 검증 완료**. 8000/8080/6001/6002 클라우드 방화벽 차단(22/80/443만 허용).
- **Coolify API 토큰**: `infra/secrets/preview-vps.env` (gitignored). 내용 절대 비출력.
- **context-mode** 활성 — 큰 출력은 `ctx_execute`/`ctx_execute_file`, mutation·git·navigation 만 Bash.
- **WebFetch/WebSearch deny** — `.claude/settings.json` deny 설정. 외부 리서치는 context-mode 또는 codegraph.
- **가드**: 13개, 0 real FAIL. `PYTHONIOENCODING=utf-8` 권장.

## ▣ Growth-46 (이번 세션) — research-loop skill 정비 + commands

- **skill-creator 적용**: SKILL.md description pushy 강화, references/ 구조 완성.
  - **핵심 교훈**: workflow 스킬에 full eval 루프는 비효율 — 반론 제기 후 스킵.
- **commands 신설** (`.claude/commands/research/`):
  - `research:fetch` — `ctx_fetch_and_index` 래퍼, raw 결과 대화 차단
  - `research:query` — `ctx_search` 배치 래퍼, 해석 후 요약만 반환
  - `research:wiki-save` — wiki 환류 강제, 프론트매터+index+커밋 일관성 (프로젝트 레벨)
- **references 추가**: `research-loop/references/context-mode-guide.md`
- **메모리 갱신**: `feedback_pushback.md` — CTO로서 비효율 제안에 냉철하게 반론 제기
- **커밋**: 0320f2e→b487399→460f8af→8f7476f→7968bf5→80d7b93, 6건

## ▣ Growth-45 — 리서치 자산 wiki 환류

- `knowledge/wiki/design/korean-ui-patterns.md` 신규 생성 (KRDS + 한국 SI 3대 패턴 + harness 통합)
- wiki index Design 섹션 추가. CLAUDE.md §7 환류 정책 추가.

## ▣ Growth-44 — base.html KRDS CDN 분기 완성

- **전 구간 완성**: profile `stack.ui_theme: public-sector` → compose `UI_THEME` → Dockerfile ENV → tokens.css(Pico 스킵) → base.html Jinja2 KRDS CDN.
- Dockerfile `ENV UI_THEME=$UI_THEME` (build ARG → runtime 전파). server.py context_processor. base.html `{% if ui_theme == 'public-sector' %}`.

## ▣ Growth-43 — preview_package.py public-sector 파이프라인

- `_get_ui_theme(slug)` 헬퍼. compose 템플릿 `args: UI_THEME: {ui_theme}`. 기존 compose 재생성(하위호환).

## ▣ Growth-42 — KRDS 분석 + 정적/동적 분기

- KRDS 클론 `D:\AI\workspace\krds-uiux` (74컴포넌트, CDN 2파일).
- `design/templates/`: krds-tab / krds-table / krds-side-nav / dense-table / tab-form.
- `token_css_generator.generate(ui_theme=...)`, `build_tokens.py --ui-theme`.

## ▣ Growth-35~41 — 인프라·디자인 기반 (참조용)

- **G-41**: design/templates 구조, profile ui_theme 키.
- **G-39**: 아코디언 사이드바 + Hostinger CSS (edu-program.n9n.co.kr PASS).
- **G-38**: 영업 루프 풀사이클 리허설 — intake→preview 전 구간 실검증.
- **G-37**: 웹 intake 인터페이스 (intake.n9n.co.kr live), CISO 게이트 첫 완주.
- **G-36**: 디자인 Phase 0+1 (Pretendard+Pico+Open Props), 504 근본 해결.
- **G-35**: DevOps 9번째 인격 신설, Hostinger KVM2 + Coolify + CI/CD end-to-end.

## 다음 후보

1. **★★ 실 고객 발굴 (M2 게이트)** — 숨고/크몽 첫 의뢰. 시스템 전 구간 준비 완료. 막는 건 영업뿐.
2. **UX/Design Pattern deep-research** — `/research:fetch` + `/research:query` 이제 사용 가능. 미답: KWCAG, 인터랙션 패턴, 한국어 UX 관행.
3. **자동화 잔여** (낮은 우선순위): webhook 보류 / SECRET_KEY rotate / G-14 stale-anchor.
4. **KRDS 클론 정리**: `D:\AI\workspace\krds-uiux` 분석 완료 → 필요 시 삭제 가능.

## CTO 행동 규범 (이번 세션 확립)

- **반론 먼저**: 유저 제안이 비효율·기술 불량이면 실행 전 냉철하게 반론 제기 + 대안 제시.
- 유저가 고수하면 따름. 침묵 = 동의 금지.

## 운영 메모

- 파일당 별도 커밋 / `Co-Authored-By: Claude Sonnet 4.6` (현 모델) / master push CTO 자동 (private repo).
- **시크릿 절대 chat·커밋 금지** — 볼트 `infra/secrets/*`(gitignored).
- Windows `NUL` 파일 주의: `> /dev/null` 오용 시 `NUL` 파일 생성.
- 환경: Node v24 / Python 3.14 / JDK 21 / Docker / WSL postgres / codegraph 0.9.9 / codex CLI 0.118.0.
- `design/refrence/hostinger-design.png` — untracked, 디렉토리명 오타. 다음 세션에서 처리 여부 결정.
