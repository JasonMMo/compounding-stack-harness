# LLM Wiki 방법론 채택 제안 (Growth-18 리서치)

> **상태: CEO 결정 대기.** CEO 가 제기한 두 문제 — ① 도메인·고객 요청을 지식으로 축적할 방법론, ② 대화·원장 누적에 따른 context 비대화 — 에 대한 GitHub "LLM Wiki" 생태계 조사와 채택안. 조사일: 2026-06-11 (GitHub API live).

## 1. 원전 — Karpathy llm-wiki 패턴

생태계의 공통 뿌리는 Andrej Karpathy 의 [llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). 핵심:

- **RAG 와의 차이**: 질의 때마다 원문에서 재추론하지 않고, LLM 이 **persistent wiki 를 점진적으로 빌드·유지**한다. "지식은 한 번 컴파일되고 계속 최신으로 유지된다 (compiled once, kept current)" — 누적이 복리로 작동.
- **3-layer**: Raw sources (불변 원문) → Wiki (LLM 이 전적으로 작성·유지하는 markdown, `[[wikilink]]` + YAML frontmatter) → Schema (CLAUDE.md 류 — wiki 구조·컨벤션·워크플로 규약).
- **3 operations**: **Ingest** (새 소스 → 요약 페이지 + 관련 entity/concept 페이지 갱신 + index/log 갱신), **Query** (index 먼저 읽고 관련 페이지만 드릴다운, 좋은 답은 wiki 에 환류), **Lint** (모순·고아 페이지·stale 주장·누락 링크 정기 점검).
- **index.md** (내용 카탈로그, 페이지당 1줄) + **log.md** (append-only 시간순, grep-parseable 프리픽스) 이중 내비게이션. **~100 소스 / 수백 페이지 규모까지 embedding RAG 없이 index 만으로 충분**하다는 것이 원전의 명시적 주장.
- 역할 분담: 인간은 소스 큐레이션·질문, LLM 이 bookkeeping 전부. wiki 는 그냥 git repo of markdown.

## 2. GitHub 생태계 조사 (2026-06-11, ★ = stars)

| Repo | ★ | 성격 | self-host | 우리 적합성 |
|---|---|---|---|---|
| Tencent/WeKnora | 16.2k | 문서→질의형 지식 플랫폼 (서버) | ✅ (무거움) | ✗ 인프라 과다 |
| AsyncFuncAI/deepwiki-open | 16.8k | **코드 repo → wiki 자동 생성** (read-side) | ✅ | △ 고객 인도 문서 자동화에 M2 참고 |
| nashsu/llm_wiki | 11.1k | Karpathy 패턴의 데스크톱 앱 구현 (graph·vector 검색 포함) | ✅ | △ 패턴 참조용 (앱 자체는 비채택) |
| chaitin/PandaWiki | 9.8k | AI 지식베이스 구축 시스템 (서버) | ✅ (무거움) | ✗ 인프라 과다 |
| AgriciDaniel/claude-obsidian | 6.5k | Obsidian + Claude Code 자기조직 second brain | ✅ | △ 아이디어만 (Growth-13 에서 Obsidian 의존 비채택 전례) |
| mem0ai/mem0 | 58.3k | agent 용 메모리 레이어 (embedding/DB) | ✅ | ✗ infra+비용, M5 재평가 |
| HKUDS/LightRAG / microsoft/graphrag | 36.4k / 33.6k | 그래프 기반 RAG | ✅ | ✗ LLM 추출 비용 상시 발생 |
| letta-ai/letta | 23.2k | stateful agent 플랫폼 (MemGPT 계열) | ✅ | ✗ 플랫폼 락인 |
| SamurAIGPT/llm-wiki-agent | 2.9k | **순수 skill 구현** — raw/→wiki/ (index·log·entities·syntheses), markdown+git 만 | ✅ (zero-infra) | ◎ 구조 차용 1순위 |
| AnswerDotAI/llms-txt | 2.4k | `llms.txt` 표준 — 사이트/repo 의 LLM 진입점 1장 | — | ○ 진입점 패턴 차용 |
| sdyckjq-lab/llm-wiki-skill | 1.8k | Karpathy 방법론 skill (置信度 라벨·SHA256 캐시·대화 결정화) | ✅ (zero-infra) | ○ 신뢰도 라벨 아이디어 차용 |

**판정**: 도구 도입이 아니라 **방법론 채택**이 답. 서버형 (WeKnora/PandaWiki), embedding형 (mem0/GraphRAG/LightRAG) 은 Growth-13 의 "아이디어 채택, 인프라 비채택" 원칙과 충돌 (신규 infra + 상시 LLM 비용 + self-host 단순성 훼손). zero-infra skill 구현체 (llm-wiki-agent) 가 증명하듯 markdown+git+index 만으로 패턴이 성립하고, **우리는 이미 절반을 갖고 있다** — seed.md 가 Karpathy 형식, learn-log 가 log.md, ledger-index.py 가 검색 CLI.

## 3. 제안 A — 지식 축적: `knowledge/` 를 LLM Wiki 구조로 승격

기존 자산을 Karpathy 3-layer 에 매핑하고 빈 곳만 채운다:

| Karpathy layer | 현재 자산 | 갭 (신설) |
|---|---|---|
| Raw sources | 고객 요청 원문·인터뷰 기록 (PII 제거) | `knowledge/raw/<customer>/` — 불변 보관 |
| Wiki | `presets/skills/*.seed.md` (concept), `profiles/*.yaml` (entity), verified-profiles (case) | `knowledge/wiki/` — 도메인·고객 횡단 synthesis 페이지, `[[wikilink]]` + frontmatter |
| Schema | CLAUDE.md + 이 문서 | wiki 규약 절 추가 (1회) |
| index.md | 없음 ← **핵심 갭** | `knowledge/wiki/index.md` — 페이지당 1줄 카탈로그 |
| log.md | `learn-log.md` (이미 동일 역할) | 그대로 (신설 불필요) |

운영: **PM delivery loop step 7 (contribute-back) 이 Ingest 트리거** — 고객 요청 1건 인도 시 wiki 페이지 갱신 + index 1줄. **Lint 는 분기 synthesis (기존 `synthesis-template.md`) 에 통합**. 신뢰도 라벨 (EXTRACTED/INFERRED/UNVERIFIED, llm-wiki-skill 차용) 으로 고객 발언 vs 우리 추론을 구분.

## 4. 제안 B — context 비대화: read-side 규약 (progressive disclosure)

같은 방법론의 **읽기 측** 적용. 원전의 "index 먼저, 본문은 드릴다운" 규약을 세션 운영에 박는다:

1. **세션 시작 로딩 상한** — CLAUDE.md + index.md (+ learn-log §6 최근 3 entries) 만. 전체 원장 read 금지.
2. **Query 경로 표준화** — 과거 지식 필요 시: `ledger-index.py --symbol` (이미 보유, Growth-13) → index.md 스캔 → 해당 페이지만 read. ledger-index 를 `knowledge/wiki/` 까지 인덱싱하도록 확장 (engineer 1 round).
3. **rollup cap 의 일반화** — G-9 (본문 10행/슬림 §6) 정신을 wiki 페이지에도: 페이지가 비대해지면 분할 + 링크 (lint 항목).
4. **`llms.txt` 진입점** — repo 루트에 1장: "이 repo 를 처음 보는 LLM 은 무엇을 어떤 순서로 읽나" (CLAUDE.md 요약 + index 포인터). 외부 AI agent (AGENTS.md 사용자) 와 공유.
5. **비채택**: embedding/vector 검색 — 원전 기준 수백 페이지까지 index 로 충분. 초과 시점에 qmd 류 로컬 검색 재평가 (그때도 zero-infra 우선).

## 5. 도입 경로 (CEO 승인 시)

| Phase | 작업 | 담당 | 비용 |
|---|---|---|---|
| 1 | `knowledge/wiki/` 골격 + index.md + 규약 절 | CTO 설계 + engineer | 0 infra |
| 2 | ledger-index.py 의 wiki 인덱싱 확장 + read-side 규약 CLAUDE.md 반영 | engineer + CTO | 0 infra |
| 3 | PM loop step 7 과 wiring (첫 고객 loop 부터 실가동) | PM + CTO | loop 당 ~1 turn 증분 |

**Milestone 기여**: M2 (고객 지식이 재사용 자산화 → 2번째 고객 한계비용 하락), M3 (vertical agent 의 지식 기반). **비용 영향**: 신규 infra 0, LLM 증분은 ingest 시 wiki 갱신 turn (~\$0.1/건).
