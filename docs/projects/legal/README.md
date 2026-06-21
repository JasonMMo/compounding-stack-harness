# 법무 통합 제품 — 문서화 골격 & 산출물 매핑

> [← docs](../../) · 법무 vertical (M3 첫 버티컬) 의 **통합 단일 제품** 문서화 anchor.
> 흩어진 기존 자산을 정식 산출물 슬롯에 매핑하고, 페르소나 owner·DFD 검증 게이트를 정의한다.
> 작성: 2026-06-20 (CTO). 상태: **D1~D5 페르소나 드래프팅 완료** (PM·CDO·DBA·QA). DFD 게이트 의심 1건은 CTO 독립검증으로 false positive 기각 → §7 참조.

## 1. 결정 (2026-06-20, founder)

| 갈림길 | 결정 | 함의 |
|---|---|---|
| 앱 구성 | **통합 단일 법무 제품** | 사건관리(CRUD) + 판례 RAG 검색을 하나의 bespoke 법무앱으로. `legal-rag /search` 를 사건 화면 컨텍스트에서 호출 — 별도 2앱이 아니라 하나의 내러티브. |
| 템플릿 수준 | **재사용 가능한 adapter/theme** | 법무 전용 룩을 새 frontend adapter(또는 8번째 theme 축)로 — 다음 버티컬(의료·금융)이 차용. middle contract **읽기전용** 유지(§4 open-closed 불변). 일회성 스노우플레이크 금지. |

**왜 지금**: 업무 데모가 전부 vanilla-htmx 한 템플릿이라 업종이 달라도 "하나처럼" 보인다 — 5백만원 구축비 내는 법무법인엔 약점. legal 을 vertical **flagship** 으로 끌어올린다(킬러앱). `profiles/lawfirm-demo.yaml` escalation 이 이미 "AI 판례검색(RAG)" 을 예고 → legal-rag 가 그 실현.

## 2. 산출 문서의 3중 용도 (복리)

각 문서를 **한 번 작성해 세 곳에 쓴다**:
1. **영업·마케팅** — 비전문 구매자 대상 차별화 근거
2. **의뢰인 인도물** — self-host 설치 시 함께 제공하는 산출물 패키지
3. **구현 입력** — adapter/theme·서비스 구현의 명세

이것이 web-agency형 "B급 professional 자동화" 를 법무 vertical 에 적용한 형태. 매번 손으로 쓰는 게 아니라 **페르소나가 산출**한다 (`pm-delivery-loop` SKILL 확장).

## 3. 문서 산출물 세트 — owner · 상태 · 기존 소스 매핑

| # | 문서 | owner | 상태 | 산출물 (정식 문서) |
|---|---|---|---|---|
| D1 | **기능명세서** | PM | ✅ 작성 완료 | [`D1-functional-spec.md`](D1-functional-spec.md) — F-01~F-22 (5 모듈), NFR 22건, 추적성 매트릭스, 열린질문 Q-1~Q-5 |
| D2 | **유저플로우** | PM·CDO | ✅ 작성 완료 | [`D2-user-flow.md`](D2-user-flow.md) — 4 플로우(3 페르소나 + 통합 시나리오), screen inventory S-01~S-17, 갭 G-1~G-6 |
| D3 | **와이어프레임** | CDO | ✅ 작성 완료 | [`D3-wireframe.md`](D3-wireframe.md) — 16 유니크 뷰 ASCII wire, theme `legal-pro` 권고(navy+gold 토큰), UX 갭 6건 |
| D4 | **ERD** | DBA | ✅ 작성 완료 | [`D4-erd.md`](D4-erd.md) — 8 엔티티 / 10 관계 Mermaid, RLS·인용 환각0 체인, data store R/W 매핑 |
| D5 | **DFD** | DBA·QA | ✅ 작성 완료 (활성 BLOCK 없음) | [`D5-dfd.md`](D5-dfd.md) — P1~P25 (Context+3 흐름), §9 검증게이트 21 단언, BLK-1 철회(§7) |

> 상태 표기는 정직하게: 5개 모두 정식 standalone 문서로 산출됨. D5 검증게이트의 의심 1건(BLK-1)은 CTO 독립검증으로 false positive 기각 — §7 참조.

## 4. DFD 검증 게이트 (설계 검증)

기존 검증은 코드 **後** 4계층 풀테스트(L1~L4). DFD 게이트는 코드 **前** 설계검증 — "데이터가 프로세스대로 올바르게 흐르는가" 를 본다.

**검증 대상 3 흐름 (초안):**
1. **Ingest**: file → extract(pdf/docx/txt) → chunk(~500tok) → embed(`passage:` prefix, 768d) → upsert `legal_document_chunk` (writer=app_service, BYPASSRLS). source 실존검증(Gap-3) 선행.
2. **Search**: query → embed(`query:` prefix) → FTS(plainto_tsquery) ∥ ANN(`<=>` HNSW) → RRF(k=60) → **RLS 필터(app_user, SET LOCAL user_id+ROLE)** → 인용(chunk_id 1:1 바인딩, 환각0).
3. **Auth/격리**: login → bcrypt verify → JWT mint → 요청마다 `SET LOCAL app.current_user_id` + `SET LOCAL ROLE app_user` → 사건/청크 격리(목록+검색 양층).

**자동 vs 수동:** 1차는 수동 리뷰 게이트(DBA 작성·QA 검증). 일부는 이미 자동화됨 — RLS 격리 흐름(흐름 3)은 `deploy/preview/legal-rag.verify-search.sh` 의 A/B/C 단언으로 라이브 실증 가능. 향후 DFD 노드별 단언을 `pytest -m postgres`(Open loop C2)로 흡수.

## 5. 통합 아키텍처 — 확정 (2026-06-21, founder)

- **별도 frontend adapter `frontend/adapters/legal-pro/`** (React+Vite, 기존 `react` 어댑터 변형). vanilla-htmx 위 theme 레이어 ✗. 동기: 7 데모가 한 디자인이라 의뢰자에게 "하나처럼" 보이는 약점 → legal 은 시각적으로 다른 프리미엄 제품. CTO 권장(라이브 vanilla-JS SPA 승격)을 founder 가 기각, React 택함(컴포넌트화·인터랙션 우선).
- 사건관리 화면 + 판례 검색 패널 **통합 1앱**. middle contract **읽기전용**(open-closed 불변). backend = `legal-rag` 서비스의 `/search`·`/cases`·`/auth`.
- `legal-pro` 테마(navy+gold, `presets/themes/legal-pro/`) baked-in.

**페이즈 분리** (의존성 기반):

| 페이즈 | 범위 | 차단 |
|---|---|---|
| **A** | 스캐폴드 + legal-pro 테마 + 판례검색 화면(라이브 `/search`, 응답계약 보존: relevance%·citation 1:1·min_relevance) + 로그인(JWT) | 없음 — 즉시 빌드 (engineer 위임, L3 npm build 게이트) |
| **B** | 사건관리 CRUD 화면(목록/상세/생성) | `/cases` 엔드포인트 G-1~G-6 미구현 + Q-1(CRUD 범위) 미확정 |

## 6. 페르소나 드래프팅 — 완료 (2026-06-20)

3 wave 오케스트레이션으로 D1~D5 산출(각 페르소나 envelope 반환, subagent-output-protocol):

1. ✅ **PM** → D1 기능명세서, D2 유저플로우
2. ✅ **CDO** → D3 와이어프레임 + theme `legal-pro` 디자인 토큰 권고
3. ✅ **DBA** → D4 ERD, D5 DFD(Context+3 흐름, P1~P25)
4. ✅ **QA** → D5 §9 검증 게이트(21 단언, 자동/수동 경계, merge BLOCK 기준)

산출물은 §3 슬롯에 매핑됨. 다음 단계: §7 BLK-1 해소 → 미해결 갭(아래) triage → adapter/theme 구현 패스.

## 7. DFD 게이트 운영 결과 & 미해결 갭

**DFD 검증 게이트 + CTO 독립검증 2단 프로세스가 작동.** QA 가 코드 前 설계검증에서 의심 1건(I-1 prefix 미적용)을 제기 → CTO 가 founder 보고 전 소스 독립검증 → **false positive 로 확정·기각**. 게이트의 가치는 "결함을 잡는 것" 뿐 아니라 **검증되지 않은 주장이 founder 까지 가지 않게 거르는 것** 임을 입증.

| ID | 의심 | 검증 결과 | 비고 |
|---|---|---|---|
| ~~BLK-1~~ | 임베딩 `passage:`/`query:` prefix 미적용 (QA 가 `embed_client.py` thin wrapper 만 보고 제기) | **철회 (false positive)** | prefix 는 **embed-adapter 사이드카**(`embed-adapter/app.py`)가 적용: `/embed`→query·`/embed/batch`→passage, 호출부 정합(ingest=batch/passage, search=single/query), 사이드카 불변식 테스트 존재. 활성 BLOCK 없음. |

> ✅ **founder 메모**: 라이브 검색의 prefix·관련도(rrf_score) 품질은 **정상**. legal-rag 메모리의 "LIVE·검색 동작" 유효 + prefix 정합 확인. 내일 rrf_score 설명 시 "prefix 비대칭 임베딩 정상 작동" 전제로 안내 가능.
> 🧭 **교훈(learn-log 환류)**: 서브에이전트 결함 판정은 cross-service/사이드카 경계를 추적하지 않으면 거짓일 수 있음 → **founder-facing 주장은 CTO 독립검증 후 보고**.

**기타 갭** (BLOCK 아님, triage 대상):
- **엔드포인트 갭** (D2 §9): G-1 `GET /cases/{id}` 부재 → 사건 상세 화면 구현 불가 · G-2 `POST/PATCH /cases` (Q-1 미확정) · G-3 원문 서빙 부재 · G-4 검색 페이지네이션 부재 · G-6 app.js 429 미분기.
- **성능** (I-2): `retrieve.py` FTS+ANN 순차 await — N-16(검색<3s) 목표 시 `asyncio.gather` 병렬화 검토.
- **데이터 모델** (D4): `legal_document_chunk.source_id` polymorphic FK(앱 레이어 강제) · `legal_precedent.keywords` 1NF 위배(FTS 대체 중, 태그 UI 시 분리) · `legal_rag_query_log.attorney_id` 물리 FK 부재.
- **열린 질문** (D1): Q-1 사건 CRUD 범위 · Q-3 `query_text` 평문 저장 PIPA 협의 — CEO·업무담당자 확인 필요.

각 산출 후 `learn-log.md` 1줄 + 메모리 환류 완료.
