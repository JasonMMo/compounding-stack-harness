# PM Ledger — 인격별 상세 기록

> 7번째 인격 (Growth-18 신설). main `learn-log.md §6` 은 1줄 rollup, 이 파일이 PM 이 닿은 Growth 의 상세. 역할 정의: `.claude/agents/pm-agent.md`, 절차: `.claude/skills/pm-delivery-loop/SKILL.md`.

## §1 — Growth 상세

### Growth-62 (2026-06-14) — 자율 intake 파이프라인 설계 (Phase 7 문서화)

**8-Phase 계획 요약**:

- **Phase 1** — 적응형 적격 정책 + Gap 성장 레지스트리: `qualification_policy.yaml` 단일 진실 (scoring, qualify_threshold=55, gap_definitions), `qualify.py` (LLM 0, 순수 데이터). gap_category count≥3 → PROMOTE → Growth-N(해당 축) lifecycle. `docs/intake-inbox/gap-registry.jsonl` (PII-free).
- **Phase 1b** — 고객 소통 Audit Trail: VPS `audit.jsonl` (hash-chain, tamper-evident) + repo `infra/registry/cases/<id>.yaml` (PII-free). 이벤트 9종 (SUBMITTED→CLOSED). `audit_export.py` 분쟁 대비.
- **Phase 2** — Q&A 정교화: `show_if` 적응형 후속질문 5종, "통화 요청" 경로(prefer_call 플래그→사람 큐), industry-default 스키마(`presets/industry-defaults.yaml` — demo profile 파생, IT 지식 부족 고객 fallback).
- **Phase 3** — 제출 시 in-process 변환 (VPS): `_post_submit_conversion()` (qualify→triage.json / convert→draft.yaml·needs-note.md / audit append / inbox.jsonl 기록). LLM 0.
- **Phase 4** — Sync 브리지 (`intake_sync.py`, 로컬): SSH rsync → prefer_call(사람 큐) / gap_only·defer(gap-registry) / qualify(scaffold→deploy→ui_check→needs-fit→registry). 멱등(processed.jsonl). `--dry-run --no-ssh --force-slug` 플래그.
- **Phase 5** — Needs-Fit 감사 게이트 (Step 4b): needs-note + AC + manifest → coverage matrix (COVERED/PARTIAL/GAP) → PASS/PASS-WITH-CAVEAT/BLOCK. `codex:codex-rescue` 호출. 출력: `docs/delivery/<slug>/needs-fit-review.md` (PII strip). 페르소나 아님.
- **Phase 6** — UI 결함 자동 체크 (`ui_check.py`): HTTP 상태 + 데스크톱·모바일 스크린샷 + console error + overflow. soft gate (FAIL=live-ui-warn, hard-stop 아님). LLM 0.
- **Phase 8** — Pipeline Monitor: 노드 그래프(9노드), SLA 감시, DEFECT_TAXONOMY 10종, CLI viewer(`pipeline_status.py`), 알림(`docs/intake-inbox/alerts.md`). G-14 가드(SPEC).

**파운더 4대 결정 (CEO+CTO 합의)**:

1. 적격 리드(score≥55, 고감도 플래그 없음)는 CEO 릴레이 없이 preview 빌드까지 자동 — **Step 5 외부 인도 게이트 불변(CEO 단독, charter §2)**.
2. 미충족 gap = 영구 배제 아닌 성장 ToDo + 누적 신호 (복리 축적 원칙).
3. audit trail(append-only hash-chain) 분쟁 대비 보존 — PIPA 보존기간은 ToDo.
4. CEO override 유지 (`--force-slug` / `processed.jsonl` 수동 편집).

**토폴로지 (불변)**:

- VPS (`apps/intake/`): 제출·점수·변환·audit·inbox까지 — repo/git/toolchain 없음.
- 로컬 (`intake_sync.py`): SSH pull → draft승급·scaffold·deploy·ui_check·needs-fit → registry 갱신·커밋.
- PII(email·free-text) 절대 커밋 금지 — `apps/intake/data-mirror/`(gitignored) + VPS에만. 커밋물엔 slug·점수·gap 카테고리만.

**auto-path 전체 LLM 0** (qualify·score·gap·convert·ui_check·pipeline_monitor 전부 deterministic). needs-fit Step 4b만 on-demand codex 호출 (인도 게이트, 자동화 아님).

**관련 파일** (신규/수정 예정 — engineer 구현 대기):
`apps/intake/{qualification_policy.yaml,qualify.py,audit.py}` · `presets/industry-defaults.yaml` · `scripts/workflow/{intake_sync.py,gap_registry_report.py,audit_export.py,ui_check.py,pipeline_emit.py,pipeline_monitor.py,pipeline_status.py}` · `docs/intake-inbox/` · `infra/registry/cases/` · `.claude/skills/pm-delivery-loop/needs-fit-prompt-template.md`

**후속 운영 4건 (2026-06-14, 동일 스레드, CTO 진행 3→2→4→1)**:

1. **deploy·ui_check `--entry-path`** — 검증기가 `/login` 을 하드코딩해 `/login` 없는 intake 앱(/ 진입)에서 false-negative. `/health` 를 권위적 liveness probe 로, UI 진입 경로는 `--entry-path`(기본 `/login`) advisory 로 분리. 교훈: "데모 스캐폴드 = `/login`" 가정이 두 곳에 하드코딩돼 있었음 — 진입 경로는 앱별 파라미터.
2. **monitor·G-14 latest-terminal-wins** — 노드 상태를 "any NODE_FAIL→failed" 가 아니라 시간순 최신 terminal 이벤트로 판정. codex Step 4b 재판정·성공 재시도가 첫 실패에 latch 안 됨. 전체 이벤트 이력은 case YAML 에 보존(audit).
3. **needs-fit codex 패스 정식화** — 사전패스(`needs_fit_audit.py`, LLM 0)는 보수적이라 `built-needs-fit-block` 은 **자동 정지 신호**일 뿐. SKILL Step 4b 에 세션 runbook 명문화: 사전패스(프롬프트 생성)→codex spawn→`record-verdict`(LLM 0 loop closer: NEEDS_FIT 재판정 이벤트·review footer·alerts 라우팅)→CEO 게이트. 핵심 통찰: codex judgment 가 키워드-휴리스틱의 false-GAP 을 교정.
4. **첫 풀-배포 리허설 (#1)** — 합성 적격 리드(score 96)로 VPS 제출→브리지→promote→scaffold→**실 Coolify 배포**→ui_check→needs-fit 전 경로 자동 검증. 라이브 `rehearsal-qa-co.n9n.co.kr` /health·/login HTTP 200 확인 후 전량 회수(Coolify app/project/manifest·compose 커밋·VPS 리드). **실 배포에서만 드러난 autonomous 3 버그 발견·수정**: (a) cp949 — 자식 Python stdout 이 em-dash 출력 시 크래시 → 브리지 subprocess 에 `PYTHONUTF8=1`; (b) 미커밋 compose — Coolify(master clone)가 못 읽어 `docker_compose_raw` 미로드 → 422 → 브리지 deploy 에 `--commit`; (c) ui_check entry-path(위 #1과 동일 클래스).

**follow-up 2건 (해결, 2026-06-14)**:

5. **triage_status 사각 해소** — `run_auto_preview` 가 case YAML 에 `_set_triage(qualify)` 설정 → G-14·pipeline_monitor 가 qualify 케이스를 추적(이전엔 triage_status=null 이라 skip, Phase 8 모니터링이 정작 가장 중요한 tier 를 못 봄). 비-qualify 경로는 이미 route_entry 에서 설정 중이었음.
6. **ui_check entity-path auth-gated 강등** — 엔티티 경로(`/contact` 등)는 vanilla-htmx 가 로그인 후 htmx partial 로 서빙 → 미인증 톱레벨 GET 은 401/403/404. entry_path 는 strict(4xx/5xx FAIL) 유지, 엔티티 경로의 401/403/404 는 WARN(auth-gated 예상)으로 강등, 5xx 는 여전히 FAIL. console error 도 엔티티 경로는 advisory(WARN). 효과: 정상 배포가 verdict=FAIL→WARN 로 — 브리지 UI_CHECKED 가 EXIT_OK(soft). 교훈: 검증기는 "미인증으로 볼 수 있는 것"과 "실제 결함"을 구분해야 함.

### Growth-38d (2026-06-12) — domain-expert v2 reconcile + CEO 지침 반영 + 스코프 확인 발송문

- **domain-expert v2 reconcile (CTO 판정)**: enrollment 흐름을 crm/lead → contact(student overlay) → project/resource-assignment 로 14 baseline 내 매핑 채택. finance invoice 복원 (AP 방향 재확인). crm에 lead·activity 추가, project 도메인 신규 진입 → domains 7개로 확정.
- **CEO 지침 반영**: Q9·Q10 확인 톤을 무거운 범위 협상 아닌 가벼운 단계 확인으로 조정. 내부 용어(Phase, entity) 노출 없는 평문 발송문 작성.
- **domains display 일반인 눈높이 최종 점검**: "학생 명단 및 지원·선발 관리" / "사업 참여 학생 배정 관리" / "사업비 집행 및 업체 지급" / "거래 업체 관리" / "교육 기자재 관리" / "사업 서류 관리" / "사업 현황 보고" — 전부 평문 한국어, 내부 용어 없음.
- **산출물**: `needs-note-edu.md` v4, `profiles/edu-program.yaml` reconcile 완료, `scope-confirm-edu.txt` 신규 (CEO 발송용).

### Growth-38c (2026-06-12) — 교육업 건1 10문항 전부 반영 + profile 갱신

- **10문항 전부 닫힘**: 학생 300명, 담당자 1인, 구축비 1,000만원, 학교 내부 서버·PostgreSQL, 결재 불필요. AP 방향(업체지급) 확정 → finance invoice 제거·procurement 추가.
- **도메인 6개 확정**: crm, finance(AP), procurement, asset, document, reporting. enrollment·학사관리·LMS 연동은 스코프 협상 전 미진입.
- **스코프 리스크 + CEO 협상 문안**: Q9 "전체 학사관리" + Q10 "LMS 연동"은 1,000만원·1인 맥락 초과. Phase 1(배치 업로드)/Phase 2(연동 고도화) 단계 제안 문안 작성 — CEO 전달 대기.
- **산출물**: `needs-note-edu.md` v3, `profiles/edu-program.yaml` 갱신 (auth.local, billing 확정, procurement 추가, security.on-premise).

### Growth-38b (2026-06-12) — 교육업 건1 follow-up 회신 반영 + draft profile 작성

- **회신 확정**: 기관 유형 = 대학교, 정부사업 수주·추진 중. datasource dialect = postgres (고객 PostgreSQL 준비 완료). 기능 3가지 ①학생 리스트 관리 ②사업비 관리 ③학사관리 (③ 범위 미확정).
- **도메인 확정 4개**: crm(contact), finance(account·invoice·payment), document(document·document-version·document-category), reporting(report-definition·report-output). order·asset·학사관리는 Q2·Q6·Q9·Q10 답변 전까지 profile 미진입.
- **추가 확인 2문항 생성**: Q9 (학사관리 범위 — 가·나·다·라 선택지), Q10 (기존 학사시스템 중복·연동 여부).
- **산출물**: `out/analysis/intake-rehearsal/needs-note-edu.md` v2 갱신, `profiles/edu-program.draft.yaml` 신규 작성 (status: draft).

### Growth-38 (2026-06-12) — intake 실제출 2건 triage (교육업 수용 / 예매앱 거절)

- **건1 수용 (교육업 staff)**: `industry: education`, `existing_system: excel_manual`. 선택 6 도메인 (customer/order/asset/finance_ledger/document/report) → catalog 매핑 가능 4개 확정 (crm/asset/document/reporting), 2개 (sales/finance) 는 Q2·Q3 follow-up 필수. IT 필드 전부 공란 — stack/dialect/auth 미결. **결론**: follow-up 2건 + IT 필드 수집 후 profile 초안 가능. 지금 당장 scaffold.py 실행 불가.
- **건2 거절 (여객열차 예매 앱)**: `free_notes` 에 "안드로이드 앱, 코레일톡 형식" 명시 — 일반 소비자향 모바일 B2C 앱. 당사 스코프 (기업/기관 내부 업무 self-host harness) 와 완전히 다름. 스코프 외 거절, backlog 등록 불필요. 거절 회신 초안 CEO 이관.
- **산출물**: `out/analysis/intake-rehearsal/needs-note-edu.md` (건1 needs 분석 + 8개 follow-up 질문 + 도메인 매핑), `out/analysis/intake-rehearsal/reject-reply.md` (건2 CEO 발송용 거절 회신).
- **FAQ 소재 발생**: "모바일 앱 개발도 가능한가요?" — `presets/skills/generic/faq.md` 누적 대상 (FAQ 파일 신설 트리거).

### Growth-37 (2026-06-12) — 웹 intake 질문 카탈로그 (`apps/intake/questions.yaml`)

- **설계 동기**: 숨고/크몽 의뢰인이 계약 전 스스로 needs를 입력하는 웹폼 필요. PM delivery loop step 0~2 (Intake → Discover → Specify) 를 디지털화하여 담당자 개입 없이 `profiles/<slug>.yaml` 초안이 생성되게 한다.
- **페르소나 분기 설계**: `persona_role` 질문(공통)으로 ceo/staff/it 를 분기 — 공통 8문항 + ceo 7문항 + staff 7문항 + it 8문항 = 총 30문항. 비기술 페르소나(ceo/staff)에게 stack/dialect 질문을 완전 차단했고, 반대로 it 페르소나에는 사업 예산·성공 기준 질문을 제외했다.
- **탈출구 원칙**: 모든 select/radio 에 "잘 모르겠어요" 옵션을 포함 — 정보 부족이 이탈 원인이 되지 않도록. PII 최소화: 이메일만 필수, 전화·회사명은 optional.
- **maps_to 커버리지**: profile 필수 필드 (`customer.industry`, `stack.frontend/backend`, `ddl.dialect`, `domains[].entities`, `datasource.*`, `billing.*`, `overlay.*`) 전부 매핑됨. needs_note 필드 (who/what/why/current/frequency/cost_of_pain) 도 전부 커버. phantom 키 0건 — `presets/ddl/catalog.yaml` 기준 도메인 slug 만 options 에 사용.
- **단일 진실**: 질문 수정은 `apps/intake/questions.yaml` 만 고친다. engineer 는 이 파일을 읽어 폼을 렌더링하므로 PM 영역과 구현 영역이 분리됨.

### Growth-23 (2026-06-11) — 인터뷰 질문 시트 초안 + profile 역분석

- **역분석 발견**: shop-demo (이커머스 2도메인 crm+sales) 와 smallmfg-demo (제조 4도메인 hr+hr-leave+approval+asset) 비교 → needs 는 도메인 선택 수 (2~4개) 로 표현된다. smallmfg escalation notes 가 "지금 안 푸는 needs" 를 명시한 점 — 인터뷰에서 미래 needs 포착 질문을 설계하는 근거.
- **기준선 확정**: stack 선택 (fastapi/vanilla-htmx/postgres) 은 IT-담당자 인터뷰 결과, auth.method 와 locale 은 조직 규모·복잡도 proxy, billing.llm_budget 은 CEO 예산 인터뷰 결과가 채운다.
- **산출물**: `docs/business/interview-sheet.md` — 3 페르소나 × 6 질문 = 총 18 주질문, 각 질문에 "이 답이 채우는 칸" 명시. 답변→profile 변환 절차 1단락 포함.
- **open loops 해소**: 인터뷰 질문 시트 초안 완료, 기존 profile 2건 역분석 완료.

### Growth-18 (2026-06-11) — PM 인격 신설 (founding)

- **계기**: CEO 직접 제안 — "지금까지는 특정 도메인을 자율적으로 발전시켰다 (공급 측). 고객 질의로 needs 를 발굴하고 구현·인도하는 절차 (수요 측) 가 별도로 필요하다."
- **신설 내용**: 역할 정의서 (`pm-agent.md`) + 실행 절차 skill (`pm-delivery-loop`) + charter v1.4 (권한 매트릭스 PM 열) + 이 ledger.
- **설계 결정 (CTO)**: ① domain-expert 와의 경계 — PM 은 *무엇이 필요한가* (needs·우선순위·인수), expert 는 *그것이 도메인적으로 무엇인가* (catalog 매핑·도메인 언어). ② loop 종료 게이트 = contribute-back (CLAUDE.md §7 과 1:1). ③ acceptance criteria 는 QA 감수 필수 — "측정 가능성 우선" 원칙을 고객 인수에도 적용. ④ honest-promise — Growth-17 Scene 5 vaporware 교훈을 고객 약속 규칙으로 승격.
- **첫 실전**: M2 첫 고객 후보 발생 시 loop #1 회전. 그 전 준비물: 3-페르소나 인터뷰 질문 시트 초안 (Initial Task 5).

### Growth-65 (2026-06-15) — intake marketing-site 분기 (P5)

- `apps/intake/questions.yaml` 수정:
  - `deliverable_kind` radio 추가 (업무시스템 / 홈페이지) — 공통 최상단 질문.
  - marketing-site 후속질문 7종: brand(브랜드명) / tagline(핵심 슬로건) / target(타겟 고객) / pages(원하는 페이지) / tone(분위기·톤) / reference(참고 사이트) / cta(전환 버튼 목적).
  - business-system 전용 질문 전원 `show_if: deliverable_kind == business_system` 게이팅 — 홈페이지 의뢰 고객에게 stack/dialect 질문 노출 0.
- answer → site 매핑:
  - `ms_tone` → theme (aurora / studio).
  - `ms_pages` → 페이지별 기본 섹션 템플릿.
  - copy placeholder 생성 (CMO / 고객 정제용 draft, 인도 전 교체 대상).
- `qualify._score_marketing_site()` 채점 신호 8종: target / pages / cta / tone / budget / reference 등. 이커머스 scope 신호 = disqualify 아님 (gap-registry 누적 대상).
- pm-delivery-loop SKILL 에 `deliverable_kind` 분기 명시 — business-system과 marketing-site 경로 분리.

## §2 — Loop 회전 기록

| # | 고객 | 시작 | 단계 | 상태 |
|---|---|---|---|---|
| 1 | 30인 법무법인 (lawfirm-demo) | 2026-06-11 | Step 5 Deliver | 인도 패키지 조립 완료 (`docs/delivery/lawfirm-demo/`) + CISO 보안 게이트 PASS (CAVEAT 3건 해소, Growth-32). CEO 승인 대기 — 외부 전달 책임은 CEO (charter §2) |
| 2 | 교육업 staff (edu-intake-rehearsal) | 2026-06-12 | Step 2→3 Specify | domain-expert v2 reconcile 완료. domains 7개 확정 (crm·project·finance·procurement·asset·document·reporting). 스코프 확인 발송문 CEO 전달 대기. open loop 잔존 4건 (학사관리 확인·LMS·budget-line·resource-assignment 크로스도메인). |

### CEO 인터뷰 답변 기록 (lawfirm-demo, 2026-06-11)

미답이던 2문항이 CEO 답변으로 채워짐 (인터뷰 시트 A5·A6):

- **A6 (예산)**: 초기 구축비 **500만원 (일회성)** — self-host 설치·구축·라이선스. profile `billing.setup_cost_krw: 5000000`. 월 LLM 운영 예산은 초기비와 분리, AI 검색 빈도 측정 후 별도 확정 (`llm_budget_usd_per_month: TBD` 유지).
- **A5 (보안·데이터)**: **소송 데이터 외부 유출 절대 금지, self-host 필수.** "우리가 제공하는 결과물에 보안 결함이 없도록 전달" — 인도물에 대한 명시적 보안 품질 요구. profile `security` 섹션 신설 (data_residency: on-premise, self_host: required). 이 요구가 **CISO 인격 신설 (Growth-32)** 의 직접 계기. CISO 첫 리뷰에서 A5(외부 유출 0) 충족 확인.

## §3 — Open Loops (이 인격 책임)

- ~~**인터뷰 질문 시트 초안** (3 페르소나 × 5~7 질문)~~ → **완료** (Growth-23, `docs/business/interview-sheet.md`)
- ~~**기존 profile 2건 역분석** (shop-demo, smallmfg-demo)~~ → **완료** (Growth-23, §1 기록)
- **FAQ 누적 위치 신설** (`presets/skills/<industry>/faq.md`) — 첫 고객 질문 발생 시
