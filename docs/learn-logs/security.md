# CISO Ledger — 인격별 상세 기록

> 실행 주체: `security-agent` (`.claude/agents/security-agent.md`). main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 이 파일은 CISO 가 닿은 Growth 의 보안 리뷰 상세 (대상·발견·조치·재현 명령) 를 담는다. main §6 은 1줄 rollup + 이 ledger pointer.

판정 권위: **거짓 안전 > 거짓 경보**. 보안 BLOCK 은 인도 sign-off 를 막는다 (CEO+CTO override 가능). 절차: [`.claude/skills/security-loop/SKILL.md`](../../.claude/skills/security-loop/SKILL.md).

## §1 — Growth 상세


### Growth-34 (2026-06-11) — 인프라 변경 회귀 점검 (codegraph 0.9.9 / mcp-openai 제거 / claude-mem 비활성화)

- **대상**: codegraph MCP 서버 추가, @mzxrai/mcp-openai 제거, claude-mem 비활성화
- **판정**: PASS-WITH-CAVEAT
- **상세 보고서**: [`out/analysis/security-infra-review-2026-06-11.md`](../../out/analysis/security-infra-review-2026-06-11.md)
- **주요 발견**:
  - egress: codegraph dist JS 외부 호출 0건 (stdio 전용). mcp-openai 제거로 OpenAI egress 차단 (개선).
  - 시크릿: .env gitignored -> codegraph 인덱싱 제외 확인. git history .env 커밋 이력 0.
  - CAV-1 [medium]: AuthController.java DEMO_PASSWORD="demo" (M1 stub, Growth-32 기존 이관, M2 교체 필수).
  - CAV-2 [informational]: 1인 메인테이너 npm 패키지 - 업그레이드 시 CISO 재검토 + 버전 고정 권장.
  - claude-mem DB 잔존: 비활성화 상태, 로컬 디스크 잔존만 (PASS, informational).
- **보안 가드 후보**: "npm global 보안 도구 신규 설치 시 버전 고정 + CISO 리뷰" (2회 인식, 3회 시 가드 제안 의무).

### Growth-32 (2026-06-11) — CISO 인격 신설 (founding)

- **계기**: CEO 직접 요구 — "우리가 제공하는 결과물에 보안 결함이 없도록 전달하자" + "보안 관련 담당 agent 가 필요하면 추가해줘" (인터뷰 A5 보안 답변에 연동).
- **결정 (CEO 위임 → CTO 설계)**: 보안을 QA 에 통합하지 않고 전담 8번째 인격으로 분리. 근거 — ① QA 역할 정의에 보안 언급 0 (기능 PASS 축과 보안 PASS 축은 다름) ② 첫 고객이 법무법인 (데이터 외부 유출 절대 금지, self-host) 이라 보안이 인도 전제 조건 ③ charter 의 "직무별 인격" 철학.
- **신설 자산**: `.claude/agents/security-agent.md` (CISO 헌장) + `.claude/skills/security-loop/SKILL.md` (7단계 리뷰 절차) + charter v1.5 (8-인격) + CLAUDE.md §1 동기화 + INDEX.md 행.
- **권한**: 인도 전 보안 리뷰 게이트 (보안 사유 BLOCK, QA 머지 BLOCK 과 동급, CEO+CTO override). delivery sign-off = CEO + PM + QA(기능) + CISO(보안).
- **첫 임무**: lawfirm-demo 인도 패키지 + legal vertical 코드 첫 보안 리뷰 (아래 §2).

## §2 — Loop 회전 기록 (보안 리뷰)

> 각 행: 대상 인도물 | 리뷰 일자 | 판정 (PASS/BLOCK/CAVEAT) | 발견 요약 | ledger 절

| 대상 | 일자 | 판정 | 발견 요약 |
|---|---|---|---|
| lawfirm-demo 인도물 (legal vertical + 인도 패키지) | 2026-06-11 | PASS-WITH-CAVEAT → **PASS** (CAVEAT 해소 후) | 아래 상세 |
| 인프라 변경 회귀 점검 (codegraph/mcp-openai/claude-mem) | 2026-06-11 | PASS-WITH-CAVEAT | CAV-1: AuthController DEMO_PASSWORD(기존 M1 stub, 체크리스트 이관). CAV-2: 1인 메인테이너 버전 고정 권장. egress 0건. |

**첫 리뷰 상세 (security-loop 7단계 수행)**:

- **A5 데이터 외부 유출 — PASS**: `backend/adapters/fastapi/` 전체에서 외부 네트워크 호출(`requests`/`httpx`/`openai`/`anthropic`/`http(s)://`) **0건**. 판례 검색 = 사용자 쿼리 → FastAPI → psycopg2 → 로컬 PostgreSQL tsvector → 결과. 소송 데이터 외부 유출 경로 없음. self-host 전제 코드에서 준수됨.
- **0 findings (점검·이상없음)**: SQL injection (`legal.py` `%s` 파라미터 바인딩, case_type 은 하드코딩 2분기 + 바인딩), XSS (`legal_precedent_search.html` 의 `escHtml()` 전수 이스케이프), 시크릿 노출 (`.env` gitignore 준수, git history `.env` 커밋 이력 0), 인도 문서 평문 시크릿 없음.
- **CAVEAT 3건 → 전부 해소 (engineer, 당일)**:
  - **C2 [medium]** `legal.py:137` 500 응답에 `str(exc)` (DB 예외 원문) 노출 → 고정 메시지로 교체, 원문은 `log.error` 에만. ✅ CISO 재검증 (line 135/137 확인).
  - **C3 [medium]** `.env.example` 평문 비밀번호 예시 → `YOUR_SECURE_PASSWORD` 플레이스홀더. ✅
  - **C1 [medium]** 인도 README 에 자격증명 변경·포트 격리 경고 부재 → "보안 주의사항" 섹션 추가. ✅
- **잔여 medium (인도 범위 밖, 체크리스트로 이관)**: `legal.py` 검색 엔드포인트 인증 없음 → M2 토큰 인증 roadmap + 사내망 격리로 보완 (체크리스트 #3·#4). `main.py` `host=0.0.0.0` 바인딩 → 체크리스트 #7.
- **산출**: `docs/delivery/lawfirm-demo/security-checklist.md` (self-host 보안 체크리스트 v1, 7항목) — 인도 패키지 첨부. fastapi 테스트 49 passed (회귀 0).
- **판정 승격**: CAVEAT C1~C3 해소 확인 → **PASS**. 인도 sign-off 의 보안 게이트 통과 (CEO+PM delivery sign-off 의 CISO 보고 의무 충족).

## §3 — Open Loops (이 인격 책임)

- self-host 보안 체크리스트 v1 작성 → lawfirm 인도 패키지 첨부 (완료 Growth-32)
- 시크릿 커밋 금지 정적 가드 (G-N 후보) → CTO 제안 (진행 중)
- 의존성 CVE 점검 자동화 (반복 리뷰 turn 비용 상수화 hedge) (진행 중)
- npm global 보안 도구 버전 고정 가드 (G-N 후보) — 2회 인식, 3회 시 의무 제안 (신규 Growth-34)
