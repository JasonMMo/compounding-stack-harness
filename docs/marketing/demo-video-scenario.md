# Demo Video Scenario — compounding-stack-harness M1 → M2 GTM

[← positioning.md](positioning.md)

> Version: 1.0 (2026-06-02). CTO sign-off required before filming begins.
> This document covers three sections: (1) script, (2) production method, (3) asset checklist, (4) distribution hooks.

---

## 1. Scenario and Script

### Strategic framing

The demo addresses the **M2 gate**: a qualified lead (업무담당자 or the CEO who forwards the link) must watch this video and say "우리 회사도 이렇게 되나?" — the exact question positioning.md names as the M1→M2 transition signal.

**Total run time target: 3 minutes 30 seconds** (sales demo length, per best-practice research).

**Hero persona: 업무담당자** (Persona B). The CEO reads the first 30 seconds and delegates. The IT-담당자 reads scene 4. Every scene is labeled with its primary persona.

**Hero profile: smallmfg-demo** (중소제조, 직원 50명, 인사+설비 관리). This profile was live-verified 2026-06-02. The shop-demo profile (e-commerce, CRM+Sales) appears briefly in scene 4 as a second-stack demonstration.

**HARD CONSTRAINT (honest marketing)**: Every screen shown must be an actual `scaffold.py` output or a live running adapter. Do not mock up multi-tenant, marketplace, or M3+ screens. Roadmap callouts are labeled explicitly.

---

### Scene-by-scene script

---

#### SCENE 0 — Hook (0:00–0:12) | Persona: CEO + 업무담당자

**On screen**: Black frame. Single line of white text fades in:

> "엑셀 5개, 반복 입력, 외주 SI 납기 6개월."

Then a second line:

> "같은 날 끝낼 수 있다면?"

**Voiceover (VO)**:
> 한국 중소기업의 현장 담당자가 매일 겪는 일입니다. 오늘 그 흐름을 바꾸는 시연을 보여드립니다.

*Rationale*: Research confirms viewers drop off before 30 seconds if they cannot see the product's end result. We show the problem first (3 seconds), then imply the solution (9 seconds), before any product UI appears. This hooks all three personas simultaneously.

---

#### SCENE 1 — Expert-Agent Interview (0:12–0:55) | Persona: 업무담당자

**On screen**: Split view. Left half: a terminal or simple chat UI showing the domain-expert-generic agent asking questions in Korean. Right half: a partially filled `profiles/smallmfg-demo.yaml` appearing line by line as if typed in real time.

Agent questions shown in sequence (real transcript from an actual agent session — do not fabricate):
1. "어떤 업무를 시스템화하고 싶으신가요?"
2. "직원 수와 부서 구조는 어떻게 되어 있나요?"
3. "현재 엑셀이나 그룹웨어로 처리하는 업무 중 가장 불편한 것은?"
4. "설비 유지보수 이력은 어디에 기록하고 계신가요?"

The right panel shows the YAML populating:
```yaml
domains:
  - slug: hr
    display: "인사 관리"
    entities: [employee, department, position, leave-request]
  - slug: asset
    display: "설비 관리"
    entities: [asset, asset-category, maintenance-record]
```

**VO**:
> AI 도메인 전문가가 업무담당자와 대화합니다. 코드 한 줄 없이, 인터뷰만으로 customer profile YAML 한 장이 완성됩니다. 이 파일이 시스템의 단일 진실입니다.

*Screen annotation (callout box)*: "customer profile — 고객사 관습의 단일 진실"

---

#### SCENE 2 — One Command, Full Scaffold (0:55–1:35) | Persona: 업무담당자 + IT-담당자

**On screen**: Terminal window, full screen. Clean dark terminal. Cursor blinks. Then:

```
$ python scripts/workflow/scaffold.py --profile smallmfg-demo
```

Terminal output scrolls (real output from actual run — capture this verbatim):
```
scaffold complete — profile: smallmfg-demo
  entities scaffolded : 11 (employee, department, position, leave-request,
                            approval-request, approval-step, approver,
                            approval-decision, asset-category, asset,
                            maintenance-record)
  DDL output          : out/smallmfg-demo/ddl/postgres.sql
  manifest output     : out/smallmfg-demo/screen-manifest.json
```

Pause 2 seconds on the final output. Then zoom into `screen-manifest.json` — show the first screen entry for `employee` (typed-form fields: `employee_id`, `full_name`, `department_id`, `status`).

**VO**:
> 명령어 하나. 11개 entity 의 DDL 과 화면 설계 manifest 가 동시에 나옵니다. 이것이 creater 축 — 7개 축을 한 번에 엮는 thin orchestration 입니다.

*Screen annotation (callout box at DDL line)*: "catalog 검증 게이트 통과 — 없는 entity 는 빌드 오류"

*Screen annotation (callout box at manifest line)*: "screen-manifest.json — Frontend 가 이 파일을 읽어 typed form 을 자동 구동"

---

#### SCENE 3 — Live Typed Form (1:35–2:20) | Persona: 업무담당자

**On screen**: Browser window. URL bar shows `localhost:8000` (or a live demo URL if available by filming time). The vanilla-htmx frontend is running — this is the actual running adapter, not a mockup.

Show two screens in sequence:

**3A — Employee list screen** (5 seconds): The HR 직원 목록 screen, populated with 3–4 sample rows (fictional names: 김민준, 박서연, 이도윤). Status badges show "active" / "휴가중".

**3B — Leave request form** (20 seconds): Click "+ 휴가 신청". A form appears with fields: `leave_type` (dropdown: 연차/병가/무급), `start_date`, `end_date`, `reason`. Fill in one entry live. Submit. The list updates.

**3C — Asset maintenance record** (15 seconds): Switch to 설비 관리 tab. Show `CNC-001` asset with `next_due_date: 2026-06-15` flagged in amber. Click to open a maintenance record. Show `maintenance_type: inspection` form.

**VO**:
> 인터뷰가 끝난 당일, 업무담당자는 자기 회사 화면 초안을 직접 씁니다. 코드도, 컨설턴트도, 납기 6개월도 없습니다. Frontend 는 vanilla-htmx — 추가 설치 없이 브라우저에서 바로 동작합니다.

*Screen annotation (top of browser)*: "Frontend: vanilla-htmx | Backend: FastAPI | 사내망 self-host"

---

#### SCENE 4 — Stack Swap in 2 Lines (2:20–2:50) | Persona: IT-담당자 + CEO

**On screen**: Side-by-side. Left: `profiles/smallmfg-demo.yaml` with these two lines highlighted:

```yaml
stack:
  frontend: vanilla-htmx
  backend: fastapi
```

Right: `profiles/shop-demo.yaml` with:

```yaml
stack:
  frontend: vanilla-htmx
  backend: fastapi
```

Then animate the left profile changing to:

```yaml
stack:
  frontend: react
  backend: springboot
```

And show a second terminal run:

```
$ python scripts/workflow/scaffold.py --profile smallmfg-demo
scaffold complete — profile: smallmfg-demo
  ...
```

Cut to the same employee screen, now rendered live in the React frontend (`npm run dev`). The React + SpringBoot corner is live-verified (react↔springboot L4 36 PASS, 2026-06-02), so film the real running screen — no roadmap callout needed.

**VO**:
> Frontend 와 Backend 는 고객사가 고릅니다. YAML 두 줄. Middle layer 의 wire-protocol contract 만 stable — adapter 는 교체해도 데이터 구조는 바뀌지 않습니다. 기존 WAS 가 Java 면 SpringBoot, AI 연동 팀이 Python 이면 FastAPI. 둘 다 같은 screen-manifest 를 읽습니다.

*Screen annotation*: "Middle contract — adapter 가 이것만 읽는다. 재구현 금지."

**CTO sign-off (2026-06-02)**: All four corners are live-verified and filmable — vanilla-htmx+fastapi, vanilla-htmx+springboot, react+fastapi, and react+springboot (react↔springboot L4 36 PASS; the 2 skips are Vite-preview SPA harness items, not capability gaps). Scene 4's swap (vanilla-htmx/fastapi → react/springboot) is fully honest. The only items requiring a "[로드맵]" label are **vue** and **nexacro** adapters (M2-후) — do not depict those as existing.

---

#### SCENE 5 — Self-Host Architecture [로드맵] (2:50–3:15) | Persona: IT-담당자

> **CTO honest-marketing block (2026-06-02)**: The ops pack (docker-compose + Vault Agent + Keycloak SSO) is a **documented M1 promise in positioning.md but is NOT yet built** — no compose file, no Vault/Keycloak config exists in the repo, and `smallmfg-demo.yaml` ships with `vault_agent: false` / `sso_keycloak: false`. This scene therefore CANNOT be filmed as a live/shipped capability. It must be presented as an explicitly labeled **roadmap** slide, with future tense, or cut entirely until the ops pack exists. Backends today run via `uvicorn` / `bootRun` directly. **Decision flagged to CEO** (open question 6 below).

**On screen**: A static architecture diagram (CDO to produce), clearly watermarked **"로드맵 — 개발 예정"**. Three boxes:

```
[고객사 서버 (사내망)]   ← 로드맵 (개발 예정)
  └─ docker-compose up
       ├─ FastAPI / SpringBoot backend
       ├─ vanilla-htmx / react frontend
       ├─ PostgreSQL
       └─ Vault Agent + Keycloak SSO (사이드카)
```

Arrow labeled "데이터 흐름 → 사내망 밖으로 나가지 않음 (설계 목표)"

**VO** (future tense — no present-tense "기본 포함 / 완료" claims):
> 사내망 self-host 가 이 제품의 설계 목표입니다. 로드맵 상, 설치는 docker-compose 한 번 — Vault Agent 와 Keycloak SSO 사이드카를 포함하고, 데이터는 고객사 서버를 벗어나지 않습니다. 감사로그·접근권한·SSO 를 기본 탑재하는 것이 IT-담당자 인수 기준입니다.

*Screen annotation*: "Self-host 아키텍처 — 로드맵 (외부 클라우드 Zero 설계)"

> **Alternative (recommended if CEO wants a fully-honest cut)**: cut Scene 5 entirely and end on Scene 4 → Scene 6. A 3-minute video showing only live-verified capability is stronger than 3:30 with a roadmap caveat. Final call deferred to CEO.

---

#### SCENE 6 — Call to Action (3:15–3:30) | Persona: CEO

**On screen**: Clean slide. Logo (placeholder until CDO finalizes CI). Two lines:

> "14 공통 도메인. 당신의 업무 언어로."
>
> "trial 문의 → [연락처 / CTA URL]"

**VO**:
> 인사, 재고, 영업, 설비 — 14개 공통 도메인이 준비되어 있습니다. 산업 특화 도메인은 함께 만들어 갑니다. 사내망 self-host 풀스택 codegen. 지금 trial 문의를 시작하세요.

*Note for CEO*: CTA URL / contact method is CEO's decision (positioning.md §6 open question: inbound vs outbound). Placeholder must be replaced before publishing.

---

### Full VO script (clean copy for recording)

> [Scene 0] 한국 중소기업의 현장 담당자가 매일 겪는 일입니다. 오늘 그 흐름을 바꾸는 시연을 보여드립니다.

> [Scene 1] AI 도메인 전문가가 업무담당자와 대화합니다. 코드 한 줄 없이, 인터뷰만으로 customer profile YAML 한 장이 완성됩니다. 이 파일이 시스템의 단일 진실입니다.

> [Scene 2] 명령어 하나. 11개 entity 의 DDL 과 화면 설계 manifest 가 동시에 나옵니다. 이것이 creater 축 — 7개 축을 한 번에 엮는 thin orchestration 입니다.

> [Scene 3] 인터뷰가 끝난 당일, 업무담당자는 자기 회사 화면 초안을 직접 씁니다. 코드도, 컨설턴트도, 납기 6개월도 없습니다. Frontend 는 vanilla-htmx — 추가 설치 없이 브라우저에서 바로 동작합니다.

> [Scene 4] Frontend 와 Backend 는 고객사가 고릅니다. YAML 두 줄. Middle layer 의 wire-protocol contract 만 stable — adapter 는 교체해도 데이터 구조는 바뀌지 않습니다. 기존 WAS 가 Java 면 SpringBoot, AI 연동 팀이 Python 이면 FastAPI. 둘 다 같은 screen-manifest 를 읽습니다.

> [Scene 5 — 로드맵 cut] 사내망 self-host 가 이 제품의 설계 목표입니다. 로드맵 상, 설치는 docker-compose 한 번 — Vault Agent 와 Keycloak SSO 사이드카를 포함하고, 데이터는 고객사 서버를 벗어나지 않습니다. 감사로그·접근권한·SSO 를 기본 탑재하는 것이 IT-담당자 인수 기준입니다. *(CEO 가 Scene 5 cut 을 택하면 이 VO 생략.)*

> [Scene 6] 인사, 재고, 영업, 설비 — 14개 공통 도메인이 준비되어 있습니다. 산업 특화 도메인은 함께 만들어 갑니다. 사내망 self-host 풀스택 codegen. 지금 trial 문의를 시작하세요.

---

## 2. Production Method

### Recommended recording tool

**OBS Studio** (free, open-source). Reasons:
- Captures terminal + browser in a single pass at 1920×1080 60fps without lag.
- Supports scene switching (terminal → browser → static diagram) without re-recording.
- Exports to MP4/H.264, the universal distribution format.
- Camtasia ($299 one-time) is an alternative with built-in callout/zoom tools if budget allows, but OBS + DaVinci Resolve (free) achieves the same result at zero cost.

**Screen resolution**: 1920×1080 minimum. Use a system font size ≥14pt in terminal so code is legible on mobile (where 60–70% of LinkedIn viewers watch).

**Zoom effects**: Apply 1.5–2x zoom on key interactions — the `scaffold.py` output line, the manifest JSON fields, and the YAML diff in Scene 4. This is the single most impactful edit for mobile viewers. DaVinci Resolve free tier handles this.

### Voiceover — recommendation: AI TTS (ElevenLabs), Korean primary

**Recommendation: ElevenLabs Creator plan ($22/month) for a Korean male professional voice.**

Rationale:
- The full VO script is approximately 750 Korean characters + 150 English technical terms — well within the 100K character/month Creator plan limit. One-time cost if the plan is cancelled after production: $22.
- ElevenLabs explicitly supports Korean (32 languages) with natural prosody. OpenAI TTS and Google TTS both support Korean but ElevenLabs delivers more expressive pacing, which matters for a 3.5-minute narrative video.
- Cost comparison: A professional Korean voiceover actor costs ₩300,000–₩700,000 ($220–$520) for a 3–4 minute studio recording. ElevenLabs is 10–25x cheaper and allows unlimited re-takes when the script changes (which it will during CTO/CEO review).
- Quality threshold: For a B2B self-host enterprise product, Korean IT-담당자 and 업무담당자 audiences are accustomed to AI TTS in product videos — quality is not a differentiator at this stage. Human voiceover is a M3+ upgrade when paying customers are producing case study videos.
- **One exception**: If the CEO prefers to record their own voice for Scene 6 (CTA), this adds authenticity to the "trust" signal. ElevenLabs handles scenes 0–5; CEO voice for scene 6 is a low-cost hybrid approach.

### Captions

- Korean captions: primary. Generated from the VO script using ElevenLabs' transcript export or a free tool (Subtitle Edit, open-source). Burned in or as a separate SRT file depending on hosting platform.
- English captions: translated from Korean using Claude (zero marginal cost). Required for GitHub README embed and any English-language community distribution.
- Standard: SRT format. Maximum 2 lines, 42 characters per line. Sync to VO timestamps.

### Editing

**DaVinci Resolve (free tier)** — sufficient for:
- Scene cuts and transitions (simple cross-dissolve between scenes 1→2, 2→3).
- Zoom/crop effects on terminal output (scene 2).
- Callout box overlays (scenes 2, 3, 4 annotations).
- Caption SRT import.
- Color grade: minimal. Dark terminal is already high contrast. No color grading needed for scene 0 text fade.

Estimated editing time: 4–6 hours for first cut, 2 hours for revision after CTO/CEO review.

### Hosting — recommendation: YouTube unlisted (primary) + Loom (sales use)

**YouTube unlisted (free)**:
- Unlimited storage, embeds in GitHub README, landing page, LinkedIn posts.
- Captions: upload SRT directly. YouTube auto-generates but SRT upload gives control.
- Analytics: watch-time, drop-off by scene — directly actionable for script iteration.
- Privacy: unlisted means no public search indexing until CEO decides to go public. A single URL change from unlisted to public when the time comes.
- Note: Vimeo is not recommended at this stage. Bending Spoons' 2026 acquisition and subsequent engineering team layoffs make the platform's long-term roadmap uncertain (per search results, January 2026 confirmation).

**Loom (free tier, up to 25 videos)**:
- For 1:1 sales outreach: CEO sends a Loom link in a LinkedIn DM or email. Loom shows whether the recipient watched and how far. This is the sales-enablement use case distinct from the broad YouTube link.
- Record a shorter 90-second version (scenes 0, 1, 2, 6 only) specifically for outbound Loom.

### Rough cost estimate

| Item | Tool | Cost |
|---|---|---|
| Screen recording | OBS Studio | $0 |
| Editing | DaVinci Resolve free | $0 |
| AI TTS (Korean VO) | ElevenLabs Creator, 1 month | $22 |
| Captions (Korean) | Subtitle Edit + ElevenLabs transcript | $0 |
| Captions (English) | Claude translation | ~$0.10 |
| Hosting (primary) | YouTube unlisted | $0 |
| Hosting (sales) | Loom free tier | $0 |
| Architecture diagram (Scene 5) | CDO produces | CMO/CDO shared |
| **Total** | | **~$22 one-time** |

If CEO prefers to upgrade the VO to human voiceover at M2+ (when a paying customer is involved in a case study video), budget ₩300,000–₩500,000 at that time.

### Recommended production path (single recommendation)

**Record with OBS Studio → Edit with DaVinci Resolve free → VO with ElevenLabs Creator Korean → Captions with Subtitle Edit → Host on YouTube unlisted → Distribute via Loom 90-sec cut for outbound sales.**

This path costs $22, requires no paid software, and can be executed by the CEO + CMO working asynchronously in 2–3 days total. It produces a 3.5-minute YouTube video and a 90-second Loom cut. All tools are available on Windows 11 (the repo environment). No external agency required.

---

## 3. Asset Checklist

### Pre-production (required before filming)

- [ ] **CTO sign-off**: Confirm which 4-corner stacks are fully filmable (live HTTP response, not mock). Specifically: is SpringBoot adapter live enough to show in Scene 4, or must Scene 4 use the "[로드맵]" callout?
- [ ] **CEO decision**: CTA URL / contact method for Scene 6. GitHub Discussions, email form, or Calendly link?
- [ ] **CEO decision**: Will CEO record Scene 6 VO personally, or full ElevenLabs?
- [ ] **CDO deliverable** (only if CEO keeps Scene 5): Static architecture diagram, watermarked "로드맵 — 개발 예정", brand colors per CI. Resolution: 1920×1080 PNG. **Blocked-on**: CEO decision on Scene 5 keep-vs-cut (open question 6).
- [ ] **CDO deliverable**: Logo / wordmark for Scene 6 end card. Resolution: 1920×1080 PNG, transparent background version for overlay.
- [ ] **Live demo environment**: `smallmfg-demo` profile running locally with sample data (fictional Korean names, 3–4 employees, 2 assets). CTO or Engineer to prepare seed data SQL.
- [ ] **Expert-agent interview transcript**: A real (not fabricated) 4-question interview session with the domain-expert-generic agent using smallmfg-demo context. CMO to conduct and record the terminal session. Approximately 5–10 minutes of actual agent interaction.

### Recording assets

- [ ] OBS Studio installed, configured for 1920×1080, system audio + microphone input separated.
- [ ] Terminal font: JetBrains Mono or Fira Code, size 16pt minimum, dark theme (Dracula or Solarized Dark).
- [ ] Browser: Chrome or Firefox, zoom at 100%, no bookmarks bar visible.
- [ ] `profiles/smallmfg-demo.yaml` open in a syntax-highlighted editor for Scene 1 right panel.
- [ ] ElevenLabs account created (Creator plan, $22/month).
- [ ] VO script (clean copy, section above) pasted into ElevenLabs. Korean voice selected. Test render of Scene 0 (28 characters) before committing to full render.

### Post-production assets

- [ ] DaVinci Resolve installed (free tier).
- [ ] Subtitle Edit installed (free, Windows).
- [ ] ElevenLabs SRT export or manual timestamp alignment.
- [ ] English SRT: translated from Korean SRT (use Claude, prompt: "Translate this SRT file from Korean to English, preserving SRT format and timestamps exactly.").
- [ ] YouTube channel under CEO's Google account (or a brand account linked to CEO's account). Set to private initially.
- [ ] Loom desktop app installed on CEO's machine for the 90-second outbound cut.

---

## 4. Distribution Hooks

### Hook A — GitHub README (IT-담당자 + 업무담당자 inbound)

Embed the YouTube unlisted link in the top section of `README.md`, above the fold. Format:

```
[![Demo: 3분 30초 — smallmfg 인사·설비 관리 scratch to typed form](https://img.youtube.com/vi/<VIDEO_ID>/maxresdefault.jpg)](https://youtu.be/<VIDEO_ID>)
```

This makes README the lead-generation first page (CMO operating principle #1: GitHub README = SEO 100점). The thumbnail showing the scaffold terminal output is immediately recognizable to IT-담당자 personas browsing GitHub.

CTO to merge this README edit after CMO provides the VIDEO_ID.

### Hook B — LinkedIn post (CEO persona inbound)

CEO publishes a 150-word LinkedIn post (CMO drafts, CEO publishes). Core message:

> "코더 없이 사내 시스템을 만드는 방법이 있습니다. AI 도메인 전문가와 인터뷰 한 번 — 같은 날 화면 초안이 나옵니다. 중소 제조업체 시연 영상 [링크]"

Post includes: the YouTube thumbnail image as an attachment (LinkedIn prioritizes posts with images over plain text). Tags: #중소기업IT #사내시스템 #AI #자동화 (Korean hashtags, CEO's audience).

Target: 1–3 qualified inbound leads within 72 hours of posting. If zero responses, CMO to escalate to CEO for outbound strategy (positioning.md §6 open question: inbound vs outbound).

### Hook C — Loom 90-second cut (outbound sales)

The 90-second Loom cut (scenes 0, 1, 2, 6) is the CEO's outbound DM attachment. When CEO identifies a target company (LinkedIn, referral, community), send:

> "저희 시스템 90초 시연입니다. [Loom link]. 다음 주 30분 통화 가능하시면 알려주세요."

Loom's view-tracking tells CEO whether the link was opened and how far the viewer got — qualifying signal before the 30-minute call.

### Hook D — Korean SI community (IT-담당자 inbound)

Target communities (CMO to identify specific thread timing):
- 클리앙 IT 포럼 / OKKY (Java + Spring 개발자 커뮤니티) — approach as CTO's technical post, not an ad. Post the scaffold.py terminal output as a "오픈소스 소개" thread.
- 인크루트·사람인 IT 관리자 커뮤니티 — IT-담당자 직군.

Timing: After YouTube video is published and GitHub README is updated, so the community post has landing material to link to.

### Hook E — Demo-video-as-sales-deck slide

The 1920×1080 thumbnail from Scene 2 (scaffold terminal output with 11 entities) and Scene 3 (live typed form) are extracted as PNG and inserted into the sales pitch deck (separate CMO deliverable). These screenshots serve as "evidence" slides in the CEO persona pitch: "이미 돌아가고 있습니다."

### Funnel sequence

```
YouTube unlisted video (public after CEO decision)
    │
    ├─── GitHub README embed ──────────→ IT-담당자 inbound → trial 문의
    ├─── LinkedIn post (CEO) ──────────→ CEO inbound → 30분 통화 → 계약
    ├─── Loom 90s cut (outbound DM) ──→ targeted CEO outbound → 30분 통화
    └─── SI community thread ─────────→ IT-담당자 inbound → GitHub star → trial
```

---

## Open Questions for CEO Input

1. **CTA target (Scene 6)**: What URL or contact method goes on the end card? Options: (a) GitHub Discussions thread, (b) email address, (c) Calendly link for 30-minute call. This is the single most important decision before filming Scene 6.

2. **Scene 4 stack-swap honesty gate**: CTO needs to confirm which adapters are filmable live (verified HTTP response) vs. require a "[로드맵]" callout. CMO cannot make this determination. CTO response needed before recording session is scheduled.

3. **CEO voice for Scene 6**: A CEO's real voice on the CTA has higher trust signal than TTS for B2B Korean enterprise. This is a 20-second recording (one take, 2–3 retakes maximum). Recommended: CEO records Scene 6 VO on any smartphone in a quiet room; ElevenLabs handles scenes 0–5.

4. **Publish timing (unlisted → public)**: The video will be uploaded as YouTube unlisted. CEO decides when to flip to public (which triggers SEO indexing and makes the link shareable without restriction). Recommended gate: after the first qualified lead responds to the Loom outbound, confirming the message resonates.

5. **Sample data language**: The live form in Scene 3 will show fictional Korean names and data (김민준, 박서연 etc.). If the primary outbound target is a specific industry or company type, CMO can tailor the seed data to match (e.g., manufacturing part numbers for a factory CEO target). CEO to indicate if a specific first outbound target is in mind.

6. **Scene 5 keep-vs-cut + ops-pack gap (CTO-flagged, 2026-06-02)**: The ops pack (docker-compose + Vault + Keycloak SSO) that Scene 5 depicts, and that positioning.md (lines 72/76/123) names as the **IT-담당자 M1 persona-acceptance criterion**, does **not yet exist** in the repo. Two consequences: (a) **Video** — Scene 5 must be a labeled roadmap slide or be cut (CTO recommends cut for a fully-honest 3:00 video). (b) **M1 maturity** — the IT-담당자 persona acceptance is unmet, which may conflict with the "M1 기술 성숙 달성" claim; CTO requests CEO confirm whether the ops pack is in-scope for M1 maturity or deferred to M2 (the T-1~T-6 technical criteria did not include it). This is a real gap, surfaced honestly per the guards-must-work principle.
