---
industry: telecom
domain: leadgen
skill: ai-instant-answer-leadgen
version: "1.0"
maturity: seed
added: 2026-06-18
---

# Telecom / SMB Lead-Gen — AI Instant Answer Skill Seed

> 재사용 대상: 통신 판매점, 보험 대리점, 지역 금융 서비스 등 **요금제/상품 즉답 + 상담 신청** 시나리오 전반.
> 통신에 하드코딩하지 않는다 — `knowledge_source` 교체만으로 타 SMB 도메인 전환.

## 핵심 니즈 (검증된 패턴)

| 페르소나 | 니즈 | 현재 우회 방법 | 미해결 비용 |
|---|---|---|---|
| 방문자 (잠재 고객) | 요금제 / 상품 즉답 — 영업시간 무관 | 직접 전화, 다른 사이트 이탈 | 리드 소실 |
| 판매점 운영자 (CEO) | 야간·주말 인입 리드 자동 수집 | 수동 SNS 응대, 놓친 문의 | 매출 기회 손실 |
| IT 담당자 | 고객 데이터 외부 유출 없이 운영 | 제3자 챗봇 SaaS 미도입 | 보안 리스크 회피로 도입 지연 |

## 지식베이스 구조 (KB Schema)

```yaml
# kb/<domain>-plans.yaml — 요금제/상품 지식베이스 예시 (통신)
version: "1.0"
entries:
  - id: "plan-unlimited-basic"
    title: "데이터 무제한 기본"
    body: "월 55,000원. 데이터 완전 무제한. 통화·문자 무제한."
    tags: [무제한, 데이터, 기본]
    recommendation_weight: 0.8   # 규칙 기반 추천 가중치
  - id: "plan-unlimited-premium"
    title: "데이터 무제한 프리미엄"
    body: "월 75,000원. 5G 속도 보장. 해외 로밍 10GB 포함."
    tags: [무제한, 5G, 해외로밍]
    recommendation_weight: 0.9
```

KB 는 YAML 평문 — 판매점 운영자가 직접 편집 가능. 리빌드 없이 파일 교체로 반영.

## 추천 규칙 구조 (Rule Schema)

```yaml
# rules/<domain>-recommend.yaml
version: "1.0"
rules:
  - if_tags_include: [무제한]
    then_recommend: [plan-unlimited-basic, plan-unlimited-premium]
    priority: 1
  - if_tags_include: [해외로밍]
    then_recommend: [plan-unlimited-premium]
    priority: 2
```

규칙 기반 — LLM 없음. 결정론적, 감사 가능.

## 리드 수집 필드 (SMB 표준)

```yaml
lead_fields: [name, phone, opt_in]
# opt_in: 마케팅 정보 수신 동의 (PIPA 개인정보보호법 준수 필수)
# email: 선택 — B2C 통신 판매점은 phone 이 주 연락 채널
```

## 개인정보 처리 주의 (PIPA 준수)

- 수집 최소화: 이름 + 전화번호 + 동의 여부만.
- opt_in 미체크 시 마케팅 연락 금지 (정보통신망법 §50).
- `privacy_mode: strict` 권장: 방문자 질문 내용 미저장.
- lead_destination 이 외부 CRM 이면 개인정보 처리위탁 계약 필요.

## section 타입 / 테마 연결

- section type: `ai-guide` (`presets/site-sections/catalog.yaml`)
- 권장 테마: `bridge` (`presets/themes/bridge/`)
- 권장 variant: `split-hero` (전환율 최우선) 또는 `centered-panel` (단독 랜딩)
- 데모 프로파일: `profiles/telecom-leadgen-demo.yaml`

## FAQ (판매점 운영자 실제 질문)

**Q. AI가 틀린 답변을 하면?**
생성형 AI가 아님. KB 에 있는 내용만 반환. KB 업데이트로 통제 가능.

**Q. 요금제가 바뀌면?**
`kb/<domain>-plans.yaml` 파일 교체 → 즉시 반영. 서비스 재배포 불필요.

**Q. 개인정보가 외부로 나가나?**
`privacy_mode: strict` 설정 시 질문 로그 없음. 리드 데이터는 `lead_destination` 설정 위치에만 저장 (기본값: 로컬 DB).

**Q. 통신 말고 다른 업종도 되나?**
KB + 규칙 파일 교체만으로 보험, 금융, 부동산 중개, 학원 등 모든 SMB 즉답 시나리오 적용 가능.

## 타 도메인 전환 체크리스트

- [ ] `kb/<domain>-plans.yaml` 작성
- [ ] `rules/<domain>-recommend.yaml` 작성
- [ ] `profiles/<slug>.yaml` 의 `ai_config.knowledge_source` + `lead_fields` 수정
- [ ] 개인정보 수집 항목 법무 검토 (업종별 규제 상이)
- [ ] 테마 `bridge` 유지 또는 업종 맞는 테마로 교체

## 관련 wiki

- `knowledge/wiki/concepts/smb-ai-guide-lite.md` — 기술 패턴 전체 설명
