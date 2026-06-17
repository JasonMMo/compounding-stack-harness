# LLM Wiki 방법론 채택 제안 (Growth-18 리서치)

> **상태: 채택 — CEO 승인 2026-06-11 ("진행하자", Growth-19).** CEO 가 제기한 두 문제 — ① 도메인·고객 요청을 지식으로 축적할 방법론, ② 대화·원장 누적에 따른 context 비대화 — 에 대한 GitHub "LLM Wiki" 생태계 조사와 채택안. 조사일: 2026-06-11 (GitHub API live). 도입 현황: §6.5 Phase 1 (wiki 골격) ✅ / Phase 2 (qmd 설치·3-collection 와이어링·BM25+시맨틱 embed 전부 완료, 2026-06-17 검증: 71 files·575 vectors·pending 0) ✅ / Phase 3 (graph.html + PM loop step 7 contribute-back wiring) — **보류 (파운더 결정 2026-06-17)**: 활성 고객 loop 가 없어 contribute-back 와이어링을 실검증할 트래픽 부재 + 마케팅 트랙이 라이브 우선순위. **첫 실제 intake loop 가동 시 재개.** Growth-19 는 Phase 2 까지로 종결.

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

## 6. 인프라 차용 추천 (2026-06-11 CEO 요청 — "차용 포함해서 추천")

§2 의 "도구 비채택" 을 CEO 지시로 재검토. **상시 서버·API 비용이 0 인 on-device 인프라는 차용한다** 로 기준 완화. 3-tier:

### 6.1 지금 차용 (추천 ✅)

| 차용물 | 무엇을 | 왜 |
|---|---|---|
| **tobi/qmd** (26.4k★, MIT, TS) | 검색 인프라 전체 — BM25 + vector + LLM re-rank, 전부 로컬 (node-llama-cpp + GGUF). `npm i -g @tobilu/qmd` → `qmd collection add docs/ knowledge/ presets/` → `qmd embed`. **Claude Code 공식 플러그인** (`claude plugin install qmd@qmd`) + MCP (stdio/HTTP daemon) | Karpathy 원전이 직접 추천한 그 도구. 제안 B 의 "수백 페이지 초과 시 검색엔진 필요" 갭을 처음부터 해소. API 비용 0, self-host 완전 호환 (G-6). **역할 분담**: `ledger-index.py` = 심볼→Growth 역인덱스 (구조 조회·가드 연동, 유지), qmd = 자연어·시맨틱 검색 (wiki/seed/ledger 횡단) |
| **SamurAIGPT/llm-wiki-agent** (2.9k★, MIT) 구조 | `wiki/` 레이아웃 (index·log·sources·entities·concepts·syntheses) + **graph.json/graph.html** (vis.js, 서버 없는 오프라인 지식그래프 시각화) | fork 아닌 구조 복제 — 검증된 디렉터리 규약을 설계 비용 0 으로. graph.html 은 CEO 가 브라우저 더블클릭으로 지식 지형 열람 |
| **sdyckjq-lab/llm-wiki-skill** (1.8k★) 아이디어 | 신뢰도 라벨 4종 (EXTRACTED / INFERRED / AMBIGUOUS / UNVERIFIED) + SHA256 ingest 캐시 | 고객 발언 vs 우리 추론 구분 — PM loop 의 honest-promise 원칙과 직결. skill 자체는 중국어 지향이라 라벨 규약만 차용 |

### 6.2 조건부 (CEO 취향)

- **Obsidian (읽기 전용 viewer)** — wiki 는 plain markdown+git 이므로 의존성 없이 graph view·백링크 열람용으로만. Growth-13 의 "Obsidian *의존* 비채택" 과 충돌 없음 (없어도 동작).
- **nashsu/llm_wiki 데스크톱 앱** (11.1k★) — 개인 지식베이스론 우수하나 회사 자산은 git 단일 진실이어야 해서 이원화 리스크. 부속 skill 은 60★ 미성숙. **비추천**.

### 6.3 보류 유지 (M5 게이트 재평가)

mem0 / LightRAG / GraphRAG / letta / WeKnora / PandaWiki — 상시 서버 + embedding 파이프라인 + ingest 마다 LLM 추출 비용. multi-tenant SaaS (M5) 에서 고객별 지식 격리가 필요해질 때 재평가. **deepwiki-open** (16.8k★) 은 별도 트랙: M2 고객 인도 문서 (repo→wiki) 자동 생성 후보.

### 6.4 리스크와 fallback

- qmd 는 node-llama-cpp 네이티브 빌드 의존 — **Phase 2 에서 Windows 설치 검증을 engineer 에 위임**, 실패 시 BM25-only 모드 또는 sqlite FTS5 (ledger-index 확장) fallback.
- 차용물 3종 모두 MIT (qmd·llm-wiki-agent) 또는 규약만 차용 — 라이선스 리스크 0.

### 6.5 도입 경로 갱신 (§5 대체)

| Phase | 작업 | 담당 |
|---|---|---|
| 1 | `knowledge/wiki/` 골격 (llm-wiki-agent 구조) + index.md + 신뢰도 라벨 규약 | CTO + engineer |
| 2 | qmd 설치·collection 구성·Windows 검증 (+plugin/MCP 연결), read-side 규약 CLAUDE.md 반영 | engineer + CTO |
| 3 | graph.html 생성 스크립트 + PM loop step 7 wiring (첫 고객 loop 실가동) | engineer + PM |
