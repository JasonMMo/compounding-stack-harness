# Session Handoff — 2026-06-14 (updated)

## 이번 세션 범위 (최신)

**자율 고객 intake 파이프라인 (Growth-62) → 파이프라인 장애 대응 대시보드 (Growth-63)**.
플랜 `idempotent-nibbling-puddle.md` Phase 8(Pipeline Monitor)의 후속 — CLI 모니터 위에 **localhost 전용 웹 대시보드 + 노드별 에러/deadlock breakdown**을 얹었다. 목적: 장애 발생 시 빠른 드릴인·대처.

> ✅ **Growth-63 learn-log 환류 완료** (커밋 `2c7dcfd` engineer ledger + `663f9ba` §6 rollup). G-9 PASS 유지(199/200, 1행 헤드룸 — 다음 회전은 cap 재접근 시). 전 가드 0 FAIL, workflow 테스트 223 PASS.

---

## 완료 항목 (이번 세션)

### Growth-63 — Pipeline 장애 대응 대시보드 (2026-06-14, 미기록)

목적: 파운더가 customer intake 파이프라인의 노드별 상태·결함·stall 을 **로컬 웹 화면**에서 빠르게 진단. **LLM 0 / PII-free / localhost 전용** 불변.

- **신규 `scripts/workflow/pipeline_dashboard.py`** — `http.server.ThreadingHTTPServer`, stdlib only. `127.0.0.1` 바인딩(비루프백 host 경고), 15초 auto-refresh `<meta refresh>`.
  - 핵심 순수함수 `render_dashboard_html(cases, health, now, *, evidence_dir, mirror_dir) -> str`.
  - 렌더 구성: 헤더+mirror 신선도 → **Incidents triage**(상단, severity 정렬, `#case-<slug>` 앵커) → Health 카드 → Alerts → 케이스별 컬러 노드 칩 → 실패/stall 노드 **drill-in**.
  - drill-in 내용: 권장 액션+owner 배지+런북 링크(`../runbooks/pipeline-monitor.md<anchor>`), SLA breakdown(dwell/sla/%초과, AUTO|HUMAN, OVER SLA 태그), 접이식 inline evidence(html.escape 처리된 stderr tail), copy-paste 다음 단계(`python scripts/workflow/pipeline_status.py --case <client_id>` + 접이식 codex 프롬프트).
  - 재사용: `pipeline_monitor` 의 `NODES/load_cases/project_node_states/aggregate_health/action_hint/_load_processed` + `pipeline_status.analyze_node_with_llm`(프롬프트 생성만, LLM **호출 안 함**).
  - CLI: `--host`(기본 127.0.0.1) `--port`(기본 8787) `--cases-dir` `--evidence-dir` `--once`(HTML stdout).
  - 보안: `_pii_safe_case` 화이트리스트 `{client_id, slug, triage_status, score, pipeline_events}` — email/free_text/revision 절대 미접근.
- **수정 `scripts/workflow/pipeline_monitor.py`**:
  - `DEFECT_ACTIONS: dict` — 10 DEFECT_TAXONOMY 클래스 → `{owner, action, runbook_anchor}` 단일 진실 + `action_hint(defect_class)`. CLI·대시보드 공유.
  - 버그픽스: `aggregate_health` 의 loop 후 stray `if ts == "closed"` 블록 제거(빈 cases 시 UnboundLocalError + closed 중복 계산).
- **수정 `scripts/workflow/pipeline_status.py`**: `action_hint` import, drill-in 에 owner+권장액션 출력(CLI 패리티).
- **테스트**: `tests/test_pipeline_dashboard.py`(신규 38) + `tests/test_pipeline_monitor.py`(DEFECT_ACTIONS 파라미터 커버리지 추가) → **111 PASS, 가드 FAIL 0**.
- **검증**: 라이브 서버 띄워 HTTP 200 확인(포트 8787 WinError 10013 충돌 → 7654 로 우회 데모), PII grep 0건, html.escape XSS 단위테스트 통과. 데모 후 **서버 중지 + `out/demo-*` 전량 삭제** 완료(repo clean).

### Growth-62 — 자율 고객 intake 파이프라인 (선행, 기록됨)
- 파운더 수동 릴레이 제거 + 적격 정책(qualify.py/qualification_policy.yaml) + gap 성장 레지스트리 + audit hash-chain + needs-fit 게이트 + ui_check + intake_sync 브리지 + Phase8 모니터. learn-log Growth-62 + pm.md 참조.

---

## 핵심 불변 (다음 세션 필독)

- **토폴로지**: intake 앱 = **VPS**(Coolify, 앱만). repo·toolchain·**모니터링은 전부 로컬 Windows**. VPS lean 유지 + PII 노출 회피가 토폴로지 불변.
- **모니터링 = 로컬 전용**: CLI `pipeline_status.py`/`pipeline_monitor.py` + 웹 `pipeline_dashboard.py`(127.0.0.1). 실 운영: `python scripts/workflow/pipeline_dashboard.py` (기본 `infra/registry/cases/` + `docs/intake-inbox/evidence/`).
- **PII 규율(HARD)**: 모니터는 커밋된 PII-free `infra/registry/cases/*.yaml` 만 읽음. data-mirror revision/email/free_text 절대 미접근·미커밋.
- **LLM 0**: 모든 auto-path·모니터링 deterministic. 대시보드는 codex 프롬프트를 **표시**만 하고 호출 안 함.
- **Windows 인코딩**: `diagnose.py` 등은 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 로 실행(cp949 em-dash crash 회피).
- **포트**: 8787 이 점유돼 있으면(WinError 10013) `--port 7654` 등으로 우회.

---

## 라이브 데모 상태 (이전 세션, 참조용 — 모두 HTTP 200)

| URL | 용도 |
|---|---|
| https://demo.n9n.co.kr | 데모 포털 (7개 업종 카드) |
| https://logistics-demo.n9n.co.kr/login | 물류·운송 |
| https://distribution-demo.n9n.co.kr/login | 도매·유통 |
| https://construction-demo.n9n.co.kr/login | 건설·시공 |
| https://itservice-demo.n9n.co.kr/login | IT서비스 |
| https://trading-demo.n9n.co.kr/login | 무역·수출입 |
| https://edu-program.n9n.co.kr/login | 교육기관 |
| https://manufacturing-demo.n9n.co.kr/login | 제조업 |

로그인: `demo` / `demo` (포털 카드 표기 기준, Growth-57)

### Coolify 앱 UUID 맵
| slug | uuid |
|---|---|
| edu-program | `tp0608w5b013sypb4euwplld` |
| demo-portal (active) | `s6872cr0asfp02sc0vgw8wi2` |
| logistics-demo | `hmb6jp67w6stmhsdi6e4h73o` |
| distribution-demo | `gufoc3trwh2umw53k93bjdyp` |
| construction-demo | `l3dyahzqjssm4l15tjpc75cj` |
| itservice-demo | `iguqvhla1cnhhjm14f3xgi2h` |
| trading-demo | `ybawqjqryxst5ofwnekaxpak` |
| manufacturing-demo | `ufbllprbzrg8pktn9yfhsybq` |
| server | `n12vdydjpwp81hu5i15n1gsb` |

### 인프라 핵심 사실
- **FastAPI 백엔드**: `InMemoryEntityStore` — PostgreSQL 없음. `SEED_FILE` env 로 JSON 주입.
- **Compose build context**: Coolify 는 repo root 기준 (`COPY demo-portal/index.html`).
- **Coolify race**: 앱 생성 후 `docker_compose_raw` 로드까지 10~15초, domain PATCH 전 polling 필요.
- **배포 엔드포인트**: `GET /applications/{uuid}/start` (POST /deploy 아님).
- **domain PATCH**: `{"docker_compose_domains":[...], "force_domain_override":True}` — raw list, json.dumps 금지.
- **토큰 보안**: `TOKEN=$(tr -d ' \t\r\n' < infra/secrets/coolify_api_token)` 길이만 확인, 값 출력 금지.
- **SSH key**: `~/.ssh/n9n_preview_ed25519` (repo 외부 operator-local).
- **배포 전 git push 필수** — 미커밋 시 compose_raw null. ([[push-before-deploy]] 메모리)

---

## 오픈 루프 (우선순위 순)

### ~~P0 — Growth-63 learn-log 환류~~ ✅ 완료 (2026-06-14)
- engineer ledger(`2c7dcfd`) + §6 rollup(`663f9ba`) 작성·푸시. G-9 PASS(199/200), 223 테스트 PASS.

### P1 — 외부/원격 모니터링 (TODO, 당장 불필요)
- 파운더가 외출 중에도 파이프라인 확인 희망. **"외부 모니터링 만들자" 명시 요청 시에만** 착수. 1순위 경로: Cloudflare Tunnel + Access(이메일 OTP) 로 localhost 대시보드만 노출, VPS/PII 무변경. 상세 메모리 [[todo-external-pipeline-monitor]].

### P2 — Capacitor 로컬 플랫폼 setup
- `frontend/adapters/capacitor/` 에서 `npm install && npm run add:android && npm run add:ios` (로컬 직접 실행). 현재 `package.json` 수정 + `package-lock.json` untracked 가 그 흔적(커밋 보류).

### P3 — Supabase L4 live (Growth-58 잔여)
- 어댑터 코드·RLS·유닛 16 green 완료. Supabase 프로젝트 프로비저닝 후 `SUPABASE_URL`+`SUPABASE_SERVICE_ROLE_KEY` → pytest → uvicorn HTTP smoke. + GoTrue auth(현재 demo/demo) / PostgREST filter·sort·paging pushdown.

---

## 최신 git (master)

```
663f9ba log(growth-63): §6 rollup — pipeline 대시보드 + engineer ledger pointer
2c7dcfd log(growth-63): engineer ledger — pipeline 장애 대응 대시보드 상세
7e0161a log(handoff): pipeline 대시보드(Growth-63) 세션 핸드오프 + P0 learn-log 환류 플래그
cc810a6 test(pipeline-monitor): DEFECT_ACTIONS coverage of every taxonomy class
... (d031800..cc810a6 = 대시보드 구현/테스트 8개)
```
`663f9ba` 가 origin/master HEAD (전부 push 완료).

### 미커밋 / untracked (의도적 보류)
- `M frontend/adapters/capacitor/package.json` + `?? frontend/adapters/capacitor/package-lock.json` — P2 로컬 setup 산출물.

---

## 다음 세션 시작 체크리스트

1. 대시보드 동작 확인: `python scripts/workflow/pipeline_dashboard.py --once` (HTML stdout) 또는 서버 후 `http://127.0.0.1:8787`(점유 시 `--port` 우회)
2. `PYTHONUTF8=1 python -m pytest scripts/workflow/tests -q` (223 PASS 기대) + `PYTHONUTF8=1 python scripts/diagnose.py` (0 FAIL)
3. 오픈 루프 중 파운더 지시 따라 선택 (외부 모니터링 P1 은 명시 요청 시에만)
