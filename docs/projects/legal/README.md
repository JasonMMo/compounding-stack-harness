# 법무 통합 제품 — 문서화 골격 & 산출물 매핑

> [← docs](../../) · 법무 vertical (M3 첫 버티컬) 의 **통합 단일 제품** 문서화 anchor.
> 흩어진 기존 자산을 정식 산출물 슬롯에 매핑하고, 페르소나 owner·DFD 검증 게이트를 정의한다.
> 작성: 2026-06-20 (CTO). 상태: **골격 — 정식 문서 드래프팅 대기.**

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

| # | 문서 | owner | 상태 | 기존 원자재 (정식화 대상) |
|---|---|---|---|---|
| D1 | **기능명세서** | PM | 원자재 산재, 정식 미작성 | `profiles/lawfirm-demo.yaml`(domains/entities) · `services/legal-rag/api.py`(엔드포인트 계약) · `docs/runbooks/legal-rag-install.md` · `docs/business/positioning-legal.md` |
| D2 | **유저플로우** | PM·CDO | 부분 존재 | `design/legal-rag/ui-spec.md`(3 페르소나: CEO/업무담당자/IT담당자) · `services/legal-rag/web/app.js`(로그인→검색→사건현황 실동작) |
| D3 | **와이어프레임** | CDO | 라이브 구현 존재, 문서 미정리 | `design/legal-rag/ui-spec.md` · 라이브 SPA `legal-rag.n9n.co.kr/app` · `web/index.html` |
| D4 | **ERD** | DBA | DDL 존재, 다이어그램 미작성 | `presets/ddl/augments/legal/*.sql`(legal_case·precedent·case_party·case_document·legal_attorney·legal_document_chunk + RLS) · `presets/ddl/render.py`(4 base 엔티티) |
| D5 | **DFD** | DBA·QA | **신규 작성 필요** | (없음 — §4 게이트 정의 따라 신규) |

> 상태 표기는 정직하게: D1~D4 는 "원자재/구현은 있으나 **정식 standalone 문서 미작성**", D5 는 처음부터 작성.

## 4. DFD 검증 게이트 (설계 검증)

기존 검증은 코드 **後** 4계층 풀테스트(L1~L4). DFD 게이트는 코드 **前** 설계검증 — "데이터가 프로세스대로 올바르게 흐르는가" 를 본다.

**검증 대상 3 흐름 (초안):**
1. **Ingest**: file → extract(pdf/docx/txt) → chunk(~500tok) → embed(`passage:` prefix, 768d) → upsert `legal_document_chunk` (writer=app_service, BYPASSRLS). source 실존검증(Gap-3) 선행.
2. **Search**: query → embed(`query:` prefix) → FTS(plainto_tsquery) ∥ ANN(`<=>` HNSW) → RRF(k=60) → **RLS 필터(app_user, SET LOCAL user_id+ROLE)** → 인용(chunk_id 1:1 바인딩, 환각0).
3. **Auth/격리**: login → bcrypt verify → JWT mint → 요청마다 `SET LOCAL app.current_user_id` + `SET LOCAL ROLE app_user` → 사건/청크 격리(목록+검색 양층).

**자동 vs 수동:** 1차는 수동 리뷰 게이트(DBA 작성·QA 검증). 일부는 이미 자동화됨 — RLS 격리 흐름(흐름 3)은 `deploy/preview/legal-rag.verify-search.sh` 의 A/B/C 단언으로 라이브 실증 가능. 향후 DFD 노드별 단언을 `pytest -m postgres`(Open loop C2)로 흡수.

## 5. 통합 아키텍처 스케치 (다음 단계, 미확정)

- 새 adapter 가칭 `frontend/adapters/legal-pro/` — 사건관리 화면 + 판례 검색 패널 **통합 1앱**. middle contract 읽기전용.
- `legal-rag` 서비스의 `/search`·`/cases`·`/auth` 를 그대로 backend 로, 새 adapter 가 프런트.
- vanilla-htmx 와의 관계(별 adapter vs theme 레이어)는 CDO·engineer 설계 패스에서 확정.

## 6. 다음 단계 — 페르소나 드래프팅

> ⚠️ 현재 세션 컨텍스트 고갈 임박. **체크포인트 후 새 컨텍스트에서** 페르소나별 드래프팅 권장.

1. **PM** → D1 기능명세서 + D2 유저플로우 (`pm-delivery-loop`)
2. **CDO** → D3 와이어프레임 + adapter/theme 디자인 토큰
3. **DBA** → D4 ERD 다이어그램 + D5 DFD
4. **QA** → D5 DFD 검증 게이트 명세 (무엇을 체크/자동·수동 경계)

각 산출물은 본 README 의 슬롯(D1~D5)을 채우고 상태를 갱신한다. 산출 후 `learn-log.md` 1줄 + 메모리 환류.
