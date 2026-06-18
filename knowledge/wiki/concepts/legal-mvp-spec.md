---
title: Legal RAG MVP 명세 — 타깃·쿼리 패턴·MVP 경계
slug: legal-mvp-spec
type: concept
created: 2026-06-18
updated: 2026-06-18
sources: [legal-rag-mvp-domain-needs-spec]
---

domain-needs-spec.md (out/, gitignored) 요지 환류. 관련: [[legal-rag-pattern]] [[legal-ai-search-strategy]] [[smb-ai-market-2026h1]] [[smb-ai-guide-lite]]

## 1. 타깃

- 소형 법무법인 (변호사 3~15명). 대형 로펌 제외 (전산팀 자체 구축). **[EXTRACTED]**
- 지역: 수도권 외 지방 법원 소재지 우선 — 공급 공백 최대, 서울 대형사 경쟁 회피. **[INFERRED]**

| 페르소나 | 핵심 페인 |
|---|---|
| 파트너 변호사 | 신규 사건 착수 시 판례 수집 30분~2시간 (키워드 불일치 누락) |
| 어쏘시에이트 | 사내 과거 준비서면 탐색 — 파일서버 산재, 선배 통화가 빠름 (지식 이전 병목) |
| 사무직 | 의뢰인 사건 현황 즉시 답변 불가 → 고객 신뢰 리스크 |

페인 우선순위: ① 판례·준비서면 탐색 시간 ② 신입 온보딩 병목 ③ 사건 현황 즉시 응답 불가 **[EXTRACTED]**

## 2. Top 쿼리 패턴 (7개)

| Q | 쿼리 예시 | 검색 대상 | 레이어 |
|---|---|---|---|
| Q1 | 손해배상 소멸시효 3년 기산점 판례 | `precedent` | tsvector + RAG |
| Q2 | 우리 사무소 소멸시효 항변 준비서면 | `case-document` (brief) | RAG 필수 |
| Q3 | 김철수 사건 단계·다음 기일 | `legal-case` + `case-party` | CRUD (AI 선택) |
| Q4 | 2019다12345 요지 + 활용 가능성 | `precedent` citation lookup | tsvector |
| Q5 | 행정소송 처분취소 소장 패턴 | `case-document` (complaint) | RAG 필수 |
| Q6 | 손해배상 계약서 자문 의견서 | `case-document` (opinion) | RAG 필수 |
| Q7 | 형사 집행유예 최근 판례 3개 | `precedent` (criminal) | tsvector + RAG |

**[EXTRACTED]** — WTP 가설: 로앤비/Westlaw 구독자는 Q1·Q7 니즈 낮음. 사내 문서 RAG(Q2·Q5·Q6)가 진짜 gap. **[UNVERIFIED]** (PM 인터뷰로 검증 필요)

## 3. MVP IN / OUT 경계

### IN (첫 demoable 버전) **[EXTRACTED]**
- 판례 키워드 검색 (tsvector, pgroonga)
- 판례 semantic 검색 (pgvector + 로컬 임베딩)
- 사내 문서 업로드 + 청킹 + 벡터 인덱싱 (PDF 우선)
- 검색 결과 + citation 표시 UI (vanilla-htmx)
- 사건 현황 조회 (Q3 — CRUD, natural language interface)
- Row-level security (담당 변호사 / 파트너 분리)
- Self-host 설치 런북 (Coolify 기반)

### OUT (명시적 제외) **[EXTRACTED]**
- 전략 자동 생성 / 준비서면 자동 작성 (honest-promise 원칙 — Growth-17)
- HWP 자동 파싱 (Phase 2)
- 외부 판례 자동 크롤링 (저작권·법적 책임 미정리)
- 의뢰인 포털 (client-facing UI)
- 멀티 테넌트 SaaS (M5 게이트)

## 4. 데모 시나리오 요약

가상 법무법인 "법무법인 한강" (변호사 5명, 서울 마포). 어쏘 이민준의 아침 루틴: **[EXTRACTED]**
- Q1 판례 검색 → 소멸시효 판례 2건 + citation 표시
- Q2 사내 준비서면 검색 → 후유장해 준비서면 스니펫 + 문서 열기
- Q3 사건 현황 → 박지수 사건 상태·다음 기일

Seed: 판례 20건 (민사·형사·행정), 가상 사건 10건, 완전 가명화 샘플 PDF. 실제 개인정보 0.

## 5. WTP 가설 (PM 인터뷰 미검증) **[UNVERIFIED]**

| 항목 | 가설 | 검증 방법 |
|---|---|---|
| 지불의사 | 일회성 구축비 300~800만원, 월 유지 20~50만원 | PM 인터뷰 3~5곳 |
| 의사결정 사이클 | 파트너 1인 결정, 1~3개월 | 인터뷰 |
| 보안 인식 | ChatGPT 사용하나 의뢰인 정보 입력 꺼림. PIPA 조항 인식 낮음 | 인터뷰 |
| 페인 우선순위 | 사내 문서 탐색(Q2)이 1순위 | 인터뷰 |
| 전환 장벽 | 로앤비/Westlaw 구독자는 판례 검색 불필요 — 사내 RAG가 gap | 인터뷰 |

## 6. 엔지니어 제약 요약

1. citation은 DB PK 1:1 바인딩 — LLM 판례 재생성 절대 금지 **[EXTRACTED]**
2. 모든 답변에 출처 필수 — 출처 없는 답변 UI 불허 **[EXTRACTED]**
3. postgres RLS 적용, 백엔드 bypass 금지 **[EXTRACTED]**
4. 검색 스니펫 PII 최소화 (의뢰인 이름·주민번호·연락처 마스킹) **[EXTRACTED]**
5. MVP: PDF만. HWP "지원 예정" 표기 **[EXTRACTED]**
6. 판례 full_text: 대법원 공개 판례만. 수집 출처 notes 기록 **[EXTRACTED]**
7. 임베딩·추론 로컬 전용. 클라우드 API 0 **[EXTRACTED]**
