# Cost Monitoring & Hedging

> 기능·사용자 증가 = LLM API + infra 비용 증가. **첫 줄부터 측정**. CTO 의무: 월 1회 cost-report.

## Cost Categories

### 1. LLM (agent inference)

| 발생 지점 | 측정 단위 | 평균 호출당 cost (2026-Q2 가이드) |
|---|---|---|
| domain-expert-generic agent 응답 | input + output token | \$0.005 ~ \$0.05 (모델별) |
| domain-expert-<vertical> agent 응답 | input + output token | 동일 |
| profile 작성 도움 | 인터뷰 대화 평균 10턴 | \$0.05 ~ \$0.5 |
| preset 추천 (RAG over INDEX.md) | embedding + LLM | \$0.01 ~ \$0.1 |
| PR 자동 리뷰 (marketplace M4+) | 코드량 비례 | \$0.1 ~ \$1.0 |

### 2. Infra (compute / storage)

| 발생 지점 | 측정 단위 | 모드 |
|---|---|---|
| Self-host 모드 | **0** (고객사 인프라) | M1~M2 기본 |
| 데모 호스팅 | 1 VM/월 | M1 demo only |
| SaaS 호스팅 | 테넌트당 compute + storage | M5 |
| CI/CD | GitHub Actions minutes | 모든 milestone |

### 3. 인적 (support)

| 발생 지점 | 측정 단위 |
|---|---|
| 고객 onboarding (CTO 시간) | 시간 |
| 고객 support ticket | 건수 + 평균 해결 시간 |
| Sales 대화 (CEO 시간) | 시간 |

## Per-Customer Cost Ledger

각 customer 가 자기 비용을 본다 (self-host 라도 LLM 호출은 우리 API 경유 시):

```
profiles/<slug>.yaml 와 함께
metrics/<slug>/
  2026-06.json    # 그 달의 LLM 호출 누적
  2026-07.json
  ...
```

JSON 형식 (예):
```json
{
  "month": "2026-06",
  "customer": "acme",
  "llm": {
    "calls": 1234,
    "input_tokens": 5678900,
    "output_tokens": 234500,
    "cost_usd": 23.45,
    "by_agent": {
      "domain-expert-generic": {"calls": 800, "cost_usd": 12.30},
      "domain-expert-medical": {"calls": 434, "cost_usd": 11.15}
    }
  },
  "infra": {"hours_compute": 0, "gb_storage": 0, "cost_usd": 0}
}
```

## Hedging Strategy — 5 lever

### Lever 1: Multi-provider Fallback

LLM 한 곳 의존 = 가격 인상에 무방비. 첫 줄부터 추상화:

```
llm/
  providers/
    anthropic.py    # primary
    openai.py       # fallback (gpt-5 / 4o)
    google.py       # fallback (gemini-pro)
    deepseek.py     # cost hedge (저가)
    local-ollama.py # ultimate hedge (self-host LLM)
  router.py         # cost-aware routing: 단순 작업 → 저가 모델, 복잡 작업 → primary
```

**Routing 규칙** (CTO 결정):
- domain-expert agent 응답: primary (Anthropic Opus/Sonnet)
- 단순 분류 / preset matching: 저가 (DeepSeek / Haiku)
- PR 리뷰 (코드 이해): primary
- profile 인터뷰: primary (대화 품질이 중요)

### Lever 2: Prompt Cache (Anthropic / OpenAI)

도메인 전문가 agent 의 INDEX.md + skill 라이브러리는 **모든 호출에서 동일**. cache 적중 시 input cost 90% 절감.

→ 모든 agent prompt 는 **stable prefix + variable suffix** 패턴 강제:

```
[cache key 1: persona + INDEX.md, ~5000 tokens]
[cache key 2: 그 산업 skill 리스트, ~3000 tokens]
[variable: 고객 질문, ~200 tokens]
```

prompt 작성 시 stable prefix 가 깨지지 않도록 lint (Growth-? 단계에서 가드 추가 예정).

### Lever 3: Prepaid Credits

가격 인상 hedge. 매분기 향후 6개월 사용 예측치의 50% 를 prepaid 로 lock.

| 분기 | 예측 사용량 | prepaid (50%) |
|---|---|---|
| M0~M1 | 미정 | — (사용량 미발생) |
| M2 | TBD | TBD |

### Lever 4: Batch API

비실시간 작업 (preset 검증, PR 리뷰, 야간 분석) 은 Anthropic/OpenAI batch API (50% 할인) 사용.

- **realtime**: 고객 인터랙션 (인터뷰, 즉답)
- **batch**: 마켓플레이스 PR 리뷰, 야간 cost report, 산업 컨벤션 정합성 정기 점검

### Lever 5: Self-host LLM (ultimate hedge)

vertical 이 깊어지면 (M3+) 그 산업 전용 small LLM 을 self-host. Llama / Qwen / DeepSeek fine-tuned on 산업 corpus.

게이트:
- 월 LLM 비용 \$5K 초과 시 검토
- 월 LLM 비용 \$15K 초과 시 실행

## Alert Thresholds (CTO 자동 알림)

```yaml
alerts:
  - name: monthly_llm_overrun
    condition: month_cost_usd > budget_usd * 1.2
    action: CTO 에게 알림 + 다음 달 budget revisit
  - name: per_customer_outlier
    condition: customer.month_cost_usd > median * 5
    action: 그 customer 의 사용 패턴 점검
  - name: provider_price_increase
    condition: provider.input_price changed
    action: 30일 내 router 재평가
  - name: cache_hit_drop
    condition: prompt_cache_hit_rate < 0.6
    action: prompt 구조 검토 — stable prefix 깨졌을 가능성
```

## CTO 월간 Cost Report 양식

매월 1일 (전월 마감), CTO 가 `learn-log.md §5` 에 1줄 + `cost-reports/<YYYY-MM>.md` 에 상세:

```markdown
### 2026-07 Cost Report
- LLM 총: $X (전월 대비 ±Y%)
- 최대 비용 customer: <slug> ($Z)
- 캐시 적중률: N%
- Multi-provider 분포: anthropic A% / openai B% / deepseek C%
- 이상 알림: 0~N 건
- Hedge action: <다음 달 적용할 변경>
```

## Decision Triggers

| Trigger | 결정 |
|---|---|
| Anthropic 가격 20% 인상 | Lever 1 router 재평가 → 다른 provider 비중 증가 |
| 월 LLM cost > 매출의 30% | unit economics 위반 — 즉시 routing 조정 |
| customer 1명의 cost > 월 결제액 50% | 그 customer 별 quota 도입 |
| cache hit rate < 50% | prompt 구조 root cause 분석 |
| 월 LLM cost > \$15K | self-host LLM 도입 결정 |

## Out of Scope (현재)

- **Infra 비용 최적화** (M5 SaaS 진입 후 본격화) — M1~M4 동안은 self-host 가 기본이므로 우리 측 infra 비용 거의 0
- **인적 cost optimization** — 파트너십 단계라 인건비 산정 자체가 모호. M3 매출 발생 후 정식 보상 모델 (`partnership-charter.md` 참조)
