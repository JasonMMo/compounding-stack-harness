---
slug: case-document
confidence: EXTRACTED
updated: 2026-06-11
source: lawfirm-demo (Growth-24 PM loop #1)
---

# case-document (사건 문서)

> catalog entity: `case-document` (domain: `legal`). seed: `presets/skills/legal/case-management.seed.md`.

## 정의

사건에 첨부된 법적 문서 메타데이터 단위. 실제 파일은 `document_version.storage_key` 참조 (cross-domain). `[EXTRACTED]` — 법무 업무에서 서류 관리는 핵심 요구사항.

## 문서 유형 (document_type)

| 값 | 의미 |
|---|---|
| `complaint` | 소장 |
| `brief` | 준비서면 |
| `evidence` | 증거 |
| `court-order` | 법원 명령·결정문 |
| `contract` | 계약서 |
| `correspondence` | 서신·통지서 |
| `other` | 기타 |

## 법적 감사 추적

`case-document` 는 append-only — 삭제 불가 (법적 감사 요건). 수정 시 새 행 추가 + 이전 행 보존 (application layer).

## 관계

- `case_id` → [[legal-case]] (cascade delete — 사건 삭제 시 함께 삭제)
- `storage_key` → `document.document-version.storage_key` (cross-domain, FK 생략)
