---
name: security-loop
description: Run the CISO security review loop — threat surface enumeration, secret/credential scan, vulnerability-class checks (SQLi/authz/XSS/path/deps), data-egress trace, PASS/BLOCK/PASS-WITH-CAVEAT verdict, ledger record. Use when security-agent reviews any customer deliverable before handoff sign-off.
---

# Security Loop

> 실행 주체: `security-agent` (`.claude/agents/security-agent.md`). 판정 권위: 거짓 안전 > 거짓 경보 우선순위. 보안 BLOCK 은 인도 sign-off 를 막는다 (CEO+CTO override 가능).

## Loop Steps

| # | 단계 | 동작 | Exit 기준 |
|---|---|---|---|
| 1 | **표면 열거** | 인도물의 신뢰 경계를 그린다: 입력 출처 (사용자 쿼리·파일·env), 데이터 저장소, 외부 네트워크 호출 (LLM API 포함), 인증·인가 지점 | threat surface 가 1줄씩 열거됨 |
| 2 | **이력 검색** ★지식 저장소 | `python scripts/ledger-index.py --symbol <대상>` + `qmd search "<대상> security" -c docs` — 같은 위치의 과거 보안 발견·caveat 확인 | 기존 보안 이력 판정 |
| 3 | **시크릿 스캔** | 추적 파일에 평문 자격증명/토큰/키 — `grep` 패턴 (password=, secret, token, key, BEGIN PRIVATE) + `.env` gitignore 준수 + git history 노출 여부 | 시크릿 노출 0 또는 에스컬레이션 |
| 4 | **취약점 클래스** | 대상별 재현 점검: SQL injection (파라미터 바인딩 여부), 인증·인가 우회, 경로 탐색, XSS (출력 이스케이프), 안전하지 않은 역직렬화, 의존성 CVE | 각 클래스 PASS/finding + 라인 근거 |
| 5 | **데이터 경계** ★법무법인 핵심 | 고객 데이터가 외부 네트워크로 나가는 경로 추적 (A5 제약). self-host 전제가 코드에서 지켜지는가 — 외부 호출이 PII/문서 본문을 실어 나르는가 | egress 경로 전부 식별·판정 |
| 6 | **판정** | PASS / BLOCK / PASS-WITH-CAVEAT. BLOCK·CAVEAT 은 재현 명령·라인 번호·PoC 와 해소 조건을 명령형으로 명시 | 판정 + 근거 기록 |
| 7 | **기록·환류** ★지식 저장소 | `docs/learn-logs/security.md` 갱신. 반복 발견 패턴은 보안 가드 후보로 CTO 제안 (3회 반복 → 가드 제안 의무). self-host 체크리스트 갱신분은 인도 패키지로 | ledger 반영 + 가드/체크리스트 환류 |

## 지식 저장소 프로토콜

- **시작**: step 2 — 과거 보안 발견·caveat 검색 없이 리뷰 시작 금지.
- **종료**: step 7 — 비자명한 보안 판정 근거와 self-host 하드닝 패턴은 wiki/체크리스트로 누적 (고객 수 증가 시 반복 리뷰를 가드로 상수화하는 hedge).

## Anti-patterns

- "안전해 보임" 판정 (재현 명령 없음) / 보안 BLOCK 을 시간 압박으로 약화 / CAVEAT 의 해소 조건 누락 / live-검증 안 된 보안 능력을 인도 문서에 약속 / 시크릿 발견을 조용히 수정 (에스컬레이션 의무 — git history rotate 필요)
