"""
apps/intake/qualify.py — Pure deterministic qualification engine.

NO LLM, NO network calls. stdlib + PyYAML only.

Usage:
    from apps.intake.qualify import qualify, QualificationResult
    result = qualify(answers)
    print(result.status, result.score, result.gaps, result.reasons)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Module-level policy cache (load once per process)
# ---------------------------------------------------------------------------

_POLICY_CACHE: dict[str, Any] = {}
_DEFAULT_POLICY_PATH = Path(__file__).resolve().parent / "qualification_policy.yaml"

# These dialect values are supported (from DIALECT_MAP in intake_to_profile.py)
_SUPPORTED_DIALECTS = {"postgres", "mysql", "oracle", "hsqldb"}

# Frontend/backend "known" = anything except unknown/empty
_UNKNOWN_STACK_VALUES = {"unknown", "", None}


# ---------------------------------------------------------------------------
# Public data classes
# ---------------------------------------------------------------------------

@dataclass
class GapRecord:
    gap_category: str
    todo_axis: str
    trigger: str
    expansion_note: str


@dataclass
class QualificationResult:
    score: int
    status: str           # "qualify" | "defer" | "gap_only" | "scope_reject"
    gaps: list[GapRecord]
    reasons: list[str]
    disqualified: bool


# ---------------------------------------------------------------------------
# Policy loader
# ---------------------------------------------------------------------------

def load_policy(path: Path | None = None) -> dict:
    """Load qualification_policy.yaml, cached by resolved path."""
    resolved = str((path or _DEFAULT_POLICY_PATH).resolve())
    if resolved not in _POLICY_CACHE:
        with open(resolved, encoding="utf-8") as fh:
            _POLICY_CACHE[resolved] = yaml.safe_load(fh)
    return _POLICY_CACHE[resolved]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_answers(answers: dict, policy: dict) -> int:
    """Apply scoring weights deterministically. Returns int clamped 0..100."""
    w = policy["scoring"]["weights"]
    score = policy["scoring"]["base_score"]

    # has_company_name
    if answers.get("company_name", "").strip():
        score += w["has_company_name"]

    # domain_count_per (capped)
    domains = _as_list(answers.get("data_domains", []))
    cap = int(w["domain_count_cap"])
    effective = min(len(domains), cap)
    score += effective * int(w["domain_count_per"])

    # budget
    budget = answers.get("ceo_budget_setup", "")
    if budget in ("500_1000", "over_1000"):
        score += w["budget_over_500"]
    elif budget == "300_500":
        score += w["budget_300_500"]
    elif budget == "under_300":
        score += w["budget_under_300"]

    # existing_system
    existing = answers.get("existing_system", "")
    if existing == "legacy_system":
        score += w["existing_system_legacy"]
    elif existing in ("excel_manual", "messenger"):
        score += w["existing_system_excel"]

    # pain_frequency
    freq = answers.get("ceo_pain_frequency", "")
    if freq == "daily":
        score += w["pain_frequency_daily"]
    elif freq == "weekly":
        score += w["pain_frequency_weekly"]

    # user_count
    user_count = answers.get("ceo_user_count", "")
    if user_count == "1-5":
        score += w["user_count_1_5"]
    elif user_count == "6-20":
        score += w["user_count_6_20"]
    elif user_count == "21-50":
        score += w["user_count_21_50"]
    elif user_count in ("51-100", "100+"):
        score += w["user_count_51_plus"]

    # stack_known_frontend
    fe = answers.get("it_frontend_pref", "")
    if fe not in _UNKNOWN_STACK_VALUES:
        score += w["stack_known_frontend"]

    # stack_known_backend
    be = answers.get("it_backend_pref", "")
    if be not in _UNKNOWN_STACK_VALUES:
        score += w["stack_known_backend"]

    # dialect_supported
    dialect = answers.get("it_db_dialect", "")
    if dialect in _SUPPORTED_DIALECTS:
        score += w["dialect_supported"]

    return max(0, min(100, score))


# ---------------------------------------------------------------------------
# Gap detection
# ---------------------------------------------------------------------------

def detect_gaps(answers: dict, policy: dict) -> list[GapRecord]:
    """
    Inspect answer fields and emit a GapRecord per matched gap_definition.
    Skips entries with already_served:true (they are served, not gaps).
    """
    gap_defs = policy.get("gap_definitions", {})
    records: list[GapRecord] = []

    # ── data_residency (ceo_data_security) ──
    data_security = answers.get("ceo_data_security", "")
    residency_defs = gap_defs.get("data_residency", {})
    if data_security in residency_defs:
        defn = residency_defs[data_security]
        if not defn.get("already_served", False):
            records.append(GapRecord(
                gap_category=defn["gap_category"],
                todo_axis=defn["todo_axis"],
                trigger=f"ceo_data_security={data_security}",
                expansion_note=defn.get("expansion_note", "").strip(),
            ))

    # ── auth_method (it_auth_method) ──
    auth = answers.get("it_auth_method", "")
    auth_defs = gap_defs.get("auth_method", {})
    if auth in auth_defs:
        defn = auth_defs[auth]
        if not defn.get("already_served", False):
            records.append(GapRecord(
                gap_category=defn["gap_category"],
                todo_axis=defn["todo_axis"],
                trigger=f"it_auth_method={auth}",
                expansion_note=defn.get("expansion_note", "").strip(),
            ))

    # ── db_dialect (it_db_dialect) ──
    dialect = answers.get("it_db_dialect", "")
    dialect_defs = gap_defs.get("db_dialect", {})
    # Gap only when dialect is unsupported (mssql) AND in the definitions
    if dialect in dialect_defs:
        defn = dialect_defs[dialect]
        if not defn.get("already_served", False):
            records.append(GapRecord(
                gap_category=defn["gap_category"],
                todo_axis=defn["todo_axis"],
                trigger=f"it_db_dialect={dialect}",
                expansion_note=defn.get("expansion_note", "").strip(),
            ))

    # ── industry_vertical (industry) ──
    industry = answers.get("industry", "")
    vertical_defs = gap_defs.get("industry_vertical", {})
    if industry in vertical_defs:
        defn = vertical_defs[industry]
        if not defn.get("already_served", False):
            records.append(GapRecord(
                gap_category=defn["gap_category"],
                todo_axis=defn["todo_axis"],
                trigger=f"industry={industry}",
                expansion_note=defn.get("expansion_note", "").strip(),
            ))

    return records


# ---------------------------------------------------------------------------
# Scope mismatch detection
# ---------------------------------------------------------------------------

def _detect_scope_mismatch(answers: dict, policy: dict) -> GapRecord | None:
    """
    Check scope_mismatch triggers. Returns first matching GapRecord (with
    disqualifies semantics baked in by caller), or None.
    Only keyword-based trigger supported (trigger_field + trigger_keywords).
    """
    scope_defs = policy.get("scope_mismatch", {})
    for _name, defn in scope_defs.items():
        if not defn.get("disqualifies", False):
            continue
        field_val = str(answers.get(defn.get("trigger_field", ""), "") or "").lower()
        keywords = defn.get("trigger_keywords", [])
        for kw in keywords:
            if kw.lower() in field_val:
                return GapRecord(
                    gap_category=defn["gap_category"],
                    todo_axis="scope",
                    trigger=f"{defn.get('trigger_field', 'free_notes')} contains '{kw}'",
                    expansion_note=defn.get("description", "").strip(),
                )
    return None


# ---------------------------------------------------------------------------
# Main qualification entry point
# ---------------------------------------------------------------------------

def qualify(answers: dict, policy_path: Path | None = None) -> QualificationResult:
    """
    Qualify an intake answers dict.

    Steps:
      1. Check scope_mismatch — if triggered, status=scope_reject, disqualified=True.
      2. score_answers to get numeric score.
      3. detect_gaps for capability gap records.
      4. Determine status from thresholds.
      5. Build human-readable reasons list.

    Returns QualificationResult.
    """
    policy = load_policy(policy_path)

    # Step 1: scope mismatch (hard reject)
    scope_gap = _detect_scope_mismatch(answers, policy)
    if scope_gap is not None:
        return QualificationResult(
            score=0,
            status="scope_reject",
            gaps=[scope_gap],
            reasons=[
                f"Scope mismatch: {scope_gap.gap_category} — {scope_gap.expansion_note[:120]}"
            ],
            disqualified=True,
        )

    # Step 2: scoring
    score = score_answers(answers, policy)

    # Step 3: gap detection
    gaps = detect_gaps(answers, policy)

    # Step 4: status from thresholds
    qualify_threshold = int(policy["qualify_threshold"])
    defer_threshold = int(policy["defer_threshold"])

    if score >= qualify_threshold:
        status = "qualify"
    elif score >= defer_threshold:
        status = "defer"
    else:
        status = "gap_only"

    # Step 5: reasons
    reasons: list[str] = []
    reasons.append(f"Score {score}: {'qualifies' if status == 'qualify' else 'deferred' if status == 'defer' else 'gap-only'} (thresholds: qualify>={qualify_threshold}, defer>={defer_threshold})")

    if gaps:
        gap_summary = ", ".join(f"{g.gap_category}[{g.todo_axis}]" for g in gaps)
        reasons.append(f"Capability gaps detected (expansion ToDos): {gap_summary}")
        # Note: gaps do NOT change status — they are growth signals, not blockers
        reasons.append("Gaps are recorded as growth signals; qualification status is NOT affected by gaps.")

    return QualificationResult(
        score=score,
        status=status,
        gaps=gaps,
        reasons=reasons,
        disqualified=False,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _as_list(val: Any) -> list:
    """Normalize a value to a list. Handles str, list, None."""
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [val] if val else []
    return list(val)
