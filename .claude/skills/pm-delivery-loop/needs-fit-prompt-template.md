# Needs-Fit Audit Gate — Codex Prompt Template

> Filled by `scripts/workflow/needs_fit_audit.py::build_codex_prompt()`.
> Placeholder tokens: `{slug}`, `{needs_note_path}`, `{manifest_path}`, `{profile_path}`, `{acceptance_criteria_path}`.
> This prompt is fed to `Agent(subagent_type='codex:codex-rescue', ...)` by a Claude session.

---

You are executing the **Needs-Fit Audit Gate** (pm-delivery-loop Step 4b) for customer slug **{slug}**.

## Your inputs

Read these four files exactly as found on disk:

1. Needs-note: `{needs_note_path}`
2. Screen manifest: `{manifest_path}`
3. Customer profile: `{profile_path}`
4. Acceptance criteria: `{acceptance_criteria_path}`

## PII handling — CRITICAL

The needs-note contains a section `## 의뢰인 기본` with email, phone, and company name.

**NEVER echo, quote, or include any content from `## 의뢰인 기본`** in your output.
Strip all email addresses (patterns: `\S+@\S+\.\S+`) and phone numbers (patterns: `\d{2,4}-\d{3,4}-\d{4}` or `0\d{9,10}`) from any text you write.
If in doubt, omit.

## Step 1 — Extract atomic need items

From the sections `## 누가 (Who)`, `## 무엇을 (What)`, and `## 왜 (Why)` of the needs-note, extract every concrete need.
Assign each a stable ID: **N-1, N-2, N-3, …**

For each need item capture:
- `id`: N-K
- `who`: the user/role affected (from 누가)
- `what`: the data object or action needed (from 무엇을)
- `why`: the business reason (from 왜)
- `source_section`: which section it came from

Ignore the sections `## 의뢰인 기본`, `## 현재`, `## 빈도`, `## 비용·리스크`, and `## IT 기술 메모` for need extraction.

## Step 2 — Build coverage matrix

For each need item N-K, determine:

**entity_evidence**: list of entity keys from the manifest's `entities` map whose slug, domain, or field names contain keywords from the need's `what`/`who` text. Use case-insensitive substring and slug-overlap matching.

**ac_evidence**: list of AC IDs from the acceptance-criteria file whose `기준` text contains keywords from the need's `what`/`why` text. If the acceptance-criteria file is absent or empty, `ac_evidence` is always `[]`.

**verdict**:
- `COVERED` — `entity_evidence` is non-empty AND `ac_evidence` is non-empty
- `PARTIAL` — exactly one of `entity_evidence` or `ac_evidence` is non-empty
- `GAP` — both are empty

## Step 3 — Aggregate

- `PASS` — zero GAP rows
- `PASS-WITH-CAVEAT` — zero GAP rows but one or more PARTIAL rows
- `BLOCK` — one or more GAP rows

## Step 4 — Write full report

Write the complete audit report to `docs/delivery/{slug}/needs-fit-review.md`.

The report must contain:
1. A header: `# Needs-Fit Review — {slug}` with audit date (today's date)
2. A one-line aggregate verdict: `PASS`, `PASS-WITH-CAVEAT`, or `BLOCK`
3. A coverage matrix table: columns `| Need ID | Who | What | Why | Entity Evidence | AC Evidence | Verdict |`
4. A summary section: count of COVERED / PARTIAL / GAP
5. If BLOCK: a `### GAP items` list — for each GAP: need ID, what, recommended action (entity missing → CTO backlog; AC missing → PM adds criteria)
6. If PASS-WITH-CAVEAT: a `### CAVEAT items` list — each PARTIAL with recommendation
7. A footer note: `> Codex refinement pass — deterministic pre-pass ran first (needs_fit_audit.py).`

Do NOT include any PII (email, phone, company contact details, or the 의뢰인 기본 section content) anywhere in the report.

## Step 5 — Return envelope only

After writing the report file, return ONLY the following envelope to the calling Claude session (max 30 lines):

```
VERDICT: <PASS|PASS-WITH-CAVEAT|BLOCK>
REPORT:  docs/delivery/{slug}/needs-fit-review.md
COVERED: <count>
PARTIAL: <count>
GAP:     <count>
```

If BLOCK, append (one line per GAP, max 5):
```
BLOCK-ITEM: N-K — <what> — <recommended action>
```

If PASS-WITH-CAVEAT, append (one line per PARTIAL, max 5):
```
CAVEAT-ITEM: N-K — <what> — <recommendation>
```

No other text. No code fences around the envelope. No PII anywhere in the envelope.
