# compounding-stack-harness

> Self-host full-stack codegen harness with **domain-expert agent** included.
> Pluggable Frontend × Stable Middle × Pluggable Backend. Cost-aware by design.

## What this is

업무 한 줄을 받아 **고객사가 고른 Frontend / Backend 조합** 으로 SpringBoot+RDB / FastAPI+RDB / Node+RDB 등 풀스택 산출물을 만드는 **self-host harness**. 비전문 사용자 3 페르소나 (CEO / 업무담당자 / IT-담당자) 가 dev 환경 없이 운영 가능.

## What makes it different

| 차별화 | 설명 |
|---|---|
| **Axis-7 domain-expert agent** | 의료/제조/물류/금융 등 산업별 expert agent 가 14 preset 큐레이션. 인간 전문가 영입 없이 시작 가능 |
| **Pluggable F/B layers** | Middle wire-protocol contract 만 stable. Frontend (nexacro/react/vue/vanilla) / Backend (springboot/fastapi/node/go) 는 customer profile 한 줄로 교체 |
| **Cost-aware by design** | 모든 LLM/infra 호출 측정. multi-provider hedge, prompt cache, batch — 첫 줄부터 |
| **Self-host first** | v1.0 단일 모드. SaaS 는 4-조건 게이트 충족 시 v2.0 진입 |
| **Compounding accumulation** | Karpathy seed.md + INDEX.md 누적. 사용 횟수 = 자산 깊이 |

## Architecture

```
[Frontend adapter]  ←→  [Middle: wire-protocol]  ←→  [Backend adapter]
   (pluggable)             (stable, single-source)      (pluggable)

         + axis-7 expert-agent: per-industry preset curator
         + customer profile: per-customer convention (1 YAML)
```

상세: [`docs/architecture/swappable-layers.md`](docs/architecture/swappable-layers.md).

## Business roadmap

| Milestone | 목표 |
|---|---|
| M0 | Founding (이 문서들) |
| M1 | Generic harness baseline (14 공통 도메인) |
| M2 | First paid customer (self-host license) |
| M3 | Expert-agent first vertical (1 산업) |
| M4 | 3 vertical + marketplace alpha |
| M5 | Multi-tenant SaaS (v2.0 gate 충족 시) |

상세: [`docs/business/revenue-roadmap.md`](docs/business/revenue-roadmap.md).

## Heritage

이 repo 는 [business-fullstack-creater](../business-fullstack-creater) 의 후신이다. 79 Growth 경험 중 메타 자산만 [`docs/inherited-wisdom/`](docs/inherited-wisdom/) 으로 승계. Nexacro/uiadapter 강결합은 의도적으로 폐기.

## Status

**M0 — Founding** (2026-05-29). 코드 구현 진행 전, 헌장·아키텍처·비즈니스 로드맵 정렬 단계.
