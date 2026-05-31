# learn-log — QA (CQO)

> Quality gate. 가드 통과 기준·4계층 풀테스트·agent 산출물 감사 인격의 ledger.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 인격 헌장: [`.claude/agents/qa-agent.md`](../../.claude/agents/qa-agent.md).

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Audit target: <감사 대상 — 가드 / 풀테스트 / agent 산출물>
- Pass criteria defined / refined: <통과 기준 결정 사항>
- False PASS / False FAIL risks: <발견·평가한 위험>
- Regression cases: <PASS→FAIL 전환 사례>
- Blocks issued: <머지 차단 카운트>
- Cost: <turns / 추정 $>
```

## §2 — Growth History

(이 인격은 Growth-4 에서 신설됨. 첫 실전 가동은 M1 진입 시 — 4계층 풀테스트 통과 기준 문서화.)

### Growth-5a (2026-05-29) — G-9 통과 기준 위임 검토 (QA agent 미가동, CTO 임시 권한)

- **Audit target**: G-9 가드 (main learn-log §6 슬림 cap)
- **Pass criteria defined / refined** (CTO 가 QA 부재 동안 임시로 박음, QA 첫 가동 시 재검토):
  - 본문 비-blank ≤ 10행 / `### Growth-N` 엔트리
  - 슬림 §6 (divider 이후) 전체 비-blank ≤ 200행
  - 코드 펜스 (```...```) 내부는 카운트 제외 — spec template 이 자기 가드에 안 걸려야 함
- **False PASS / False FAIL risks (CTO 가 미리 노트)**:
  - 거짓 PASS: 한 줄에 긴 prose 가 박히면 줄 수는 통과해도 가독성 손실 — 향후 길이 cap 추가 검토
  - 거짓 FAIL: 코드 펜스 외 인용 블록 (`>`) 은 활성으로 카운트됨, 의도된 행동
- **Regression cases**: 없음 (신설)
- **Blocks issued**: 0 (감사 인격 미가동)
- **Cost**: 0 turns (CTO 가 위임 권한으로 박음)
- **Note**: 본 엔트리는 *위임 결정 기록* 으로, QA agent 가 M1 진입 시 첫 가동되면 본 통과 기준을 인수·재평가한다.

### Growth-7 (2026-05-29) — QA 첫 실전 가동: springboot-jakarta compliance 게이트 BLOCK→PASS

- **Audit target**: 첫 backend adapter (springboot-jakarta) — swappable-layers §6 4-dimension compliance 게이트
- **Pass criteria defined**: black-box HTTP compliance suite (`tests/adapters/springboot-jakarta/`, pytest, `ADAPTER_BASE_URL` 파라미터화 — 모든 backend adapter 재사용 가능). 23 test = DIM-1 contract round-trip(8) + DIM-2 error envelope(5) + DIM-3 paging(6) + DIM-4 Growth-5d 표준(4). http_status 는 codes.yaml 에서 읽어 대조 (테스트도 single-source 준수, 하드코딩 금지).
- **False PASS / False FAIL risks**: cursor 요청 키 `mode` vs adapter `paging_mode` 불일치 적발 → contract HTTP 직렬화 컨벤션 미정 issue 를 CTO 에 에스컬레이션 (flat-underscore 표준으로 해소).
- **Regression cases**: 초기 BLOCK 2건 사후분석 — 일부는 테스트측 결함 (autouse fixture 가 entity_type 누적 오염, cursor 키 불일치). 테스트 수정 + adapter 수정 양측 환류 후 23/23 green.
- **Blocks issued**: 1 (DIM-3 2 FAIL → engineer 수정 → 재검증 해제). CQO 머지 BLOCK 권한 첫 행사.
- **G-9 통과 기준 인수**: CTO 임시 박음 (Growth-5a) → QA 정식 인수, 현행 cap (본문 10 / §6 200) 유지 판정.
- **Cost**: ~2 round Sonnet


### Growth-8 (2026-05-29) — QA 두 번째 실전 가동: vanilla-htmx frontend adapter compliance 게이트 PASS

- **Audit target**: 첫 frontend adapter (vanilla-htmx) — frontend-adapter-contract.md §3~4 4-dimension compliance 게이트
- **Pass criteria defined**:
  - DIM-1 (F-1): entity_list route 가 _proxy_request 에 넘기는 params dict 에 flat-underscore 키 (paging_mode, paging_page, paging_size, paging_cursor, sort_field, sort_direction) 만 포함. dot-notation 키 (paging.mode 등) 부재 필수. 5개 test.
  - DIM-2 (F-3): codes.yaml 의 11개 코드 전부에 대해 mock _proxy_request -> 해당 code 반환 시, 렌더 HTML 에 codes.yaml 의 message_ko 포함. AUTH_REQUIRED/AUTH_EXPIRED 는 /login redirect 검증. retriable 플래그 -> 재시도 힌트 표시/비표시. 22개 test (2개 skip = AUTH redirect codes).
  - DIM-3 (F-2): offset 마지막 페이지 disabled Next 버튼 확인, 비마지막 페이지 Next 링크 확인, cursor 모드 next_cursor 있을 때 Load-more 링크, 없을 때 end 메시지. 4개 test.
  - DIM-4 (F-4): 첫 DELETE 200 -> 삭제 완료 렌더, 두 번째 DELETE (F-4 mapped success) -> 삭제 완료 렌더, _proxy_request unit (404+DELETE -> {success:True}/200), 음성 (404+GET 미재매핑), GET confirm+NOT_FOUND -> success 페이지. 5개 test.
  - L1: frontend/adapters/vanilla-htmx/tests/ subprocess rc=0. 1개 test.
  - L3: build_tokens.py exits 0, tokens.css >= 5 CSS custom property. 2개 test.
  - L4: live adapter /health + /login 검증 (optional, skip if not running). 2개 test (skipped).
  - **총 41개 collected / 37 PASSED / 4 SKIPPED (AUTH redirect x2 + L4 live x2) / 0 FAILED / RC=0**
- **Single-source 준수**: message_ko / retriable / http_status 모두 ContractLoader().codes() 에서 런타임 로드. 코드 문자열 하드코딩 없음. 템플릿 실제 문자열은 template 파일 파싱으로 추출 후 assertion 에 삽입.
- **False PASS / False FAIL risks**:
  - 거짓 PASS 위험: flask_client fixture 가 importlib.reload(server) 로 app 재생성 — 픽스처 간 상태 누적 방지 (Growth-7 교훈 적용). FakeHTTPError 가 b{} 빈 바디 반환 -> _proxy_request 가 {} 를 파싱, 404+DELETE 는 mapping 전에 분기되므로 payload 검사 불필요. 검증됨.
  - 거짓 FAIL 위험: conftest flask_client 가 session token 자동 주입 — _require_login 데코레이터 우회. 없으면 모든 entity route 가 redirect 해 F-1/F-2/F-3/F-4 테스트 전부 false-FAIL.
- **CSRF 부재 (Known Gap)**: engineer README.md 가 M1 dev-mode known-gap 으로 명시. 생산 hardening (flask-wtf 또는 custom CSRF) 는 M1 이후 Growth. 이 게이트의 범위 밖 — CSRF 는 wire-protocol compliance (F-1~F-4) 와 무관한 보안 레이어. QA 스코프: contract compliance. CSRF 는 보안 audit (별도 게이트 예정).
- **Regression cases**: 없음 (신설)
- **Blocks issued**: 0 (37/37 green, 4 explicit skip)
- **Cost**: ~3 round Sonnet

## §3 — Open Loops (이 인격 책임)

- 현행 가드 9개 (G-1~G-9) 의 거짓 PASS / 거짓 FAIL 위험 평가 — 첫 가동 시
- G-9 통과 기준 인수·재평가 (CTO 임시 박음 → QA 정식 검토)
- M1 진입 게이트 통과 기준 문서화 — L1~L4 각각의 PASS 정의
- regression 이력 섹션 초기화 (이 파일 §4 로 분리 예정)
