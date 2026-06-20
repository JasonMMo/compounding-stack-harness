---
slug: legal-case
confidence: EXTRACTED
updated: 2026-06-11
source: lawfirm-demo (Growth-24 PM loop #1)
---

# legal-case (사건)

> catalog entity: `legal-case` (domain: `legal`). seed: `presets/skills/legal/case-management.seed.md`.

## 정의

법무법인이 수임한 사건 1건의 생애 주기를 관리하는 단위. `case_number` (사건번호) 가 unique key. `[EXTRACTED]` — 업무담당자 인터뷰에서 직접 언급된 주요 업무 객체.

## 핵심 필드

| 필드 | 의미 | 비고 |
|---|---|---|
| `case_number` | 사건번호 (법원 부여) | unique, 예: "2024가합12345" |
| `case_type` | 사건 유형 | civil/criminal/administrative/family/commercial |
| `status` | 진행 단계 | intake→active→trial→appeal→closed\|withdrawn |
| `next_hearing_date` | 다음 기일 | 일정 알림 트리거 |
| `assigned_attorney_id` | 담당 변호사 | → `hr.employee` |
| `client_contact_id` | 의뢰인 | → `crm.contact` (nullable) |
| `summary` | 사건 요약 | tsvector FTS 대상 |

## 상태 흐름

```
intake → active → trial → appeal → closed
                         ↓
                      withdrawn
```

`closed` / `withdrawn` 은 terminal — 재활성화 불가 (application layer).

## AI 검색 연결

`summary`/`fts_vector` → postgres tsvector GIN index → 키워드 기반 사건 검색. RAG 하이브리드 검색(FTS∥ANN→RRF)은 **구현·라이브**(Growth-93/97, `legal-rag` 서비스, 청크 레벨) — Growth-24 escalation 항목이었으나 완료됨. 상세 [[legal-rag-pattern]].

## 관련 엔티티

- [[case-party]] — 1:N 당사자 목록
- [[case-document]] — 1:N 첨부 문서
- [[precedent]] — 전략 수립 시 참조 (M:N, junction table 미등록)
