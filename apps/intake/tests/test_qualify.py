"""
apps/intake/tests/test_qualify.py

pytest test suite for qualify.py and gap_registry_report.py (Phase 1).
Run: python -m pytest apps/intake/tests/test_qualify.py -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — make repo root importable
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from apps.intake.qualify import (
    detect_gaps,
    load_policy,
    qualify,
    score_answers,
)
from scripts.workflow.gap_registry_report import (
    load_registry,
    render_summary,
    tally_gaps,
)

# Shared policy path
POLICY_PATH = REPO_ROOT / "apps" / "intake" / "qualification_policy.yaml"


# ---------------------------------------------------------------------------
# Helper: well-completed manufacturing CEO submission
# ---------------------------------------------------------------------------

def _manufacturing_ceo_answers() -> dict:
    """A well-completed manufacturing CEO submission that should qualify."""
    return {
        "company_name": "한국정밀제조",
        "industry": "manufacturing",
        "data_domains": ["customer", "order", "inventory"],
        "existing_system": "legacy_system",
        "persona_role": "ceo",
        "ceo_pain_bottleneck": "재고 현황을 실시간으로 파악하기 어려워 과잉 발주가 반복됩니다.",
        "ceo_pain_frequency": "daily",
        "ceo_success_criteria": "재고 오차율 5% 이하, 발주 실수 0건",
        "ceo_user_count": "6-20",
        "ceo_budget_setup": "500_1000",
        "ceo_data_security": "onpremise_only",
        "it_db_dialect": "postgres",
        "it_frontend_pref": "react",
        "it_backend_pref": "fastapi",
        "it_auth_method": "simple_session",
        "contact_email": "test@example.com",
        "contact_preferred_time": "morning",
        "free_notes": "",
    }


# ---------------------------------------------------------------------------
# Test 1: qualify — well-completed manufacturing CEO -> qualify, score>=55
# ---------------------------------------------------------------------------

class TestQualifyManufacturingCeo:
    def test_status_qualify(self):
        answers = _manufacturing_ceo_answers()
        result = qualify(answers, POLICY_PATH)
        assert result.status == "qualify", (
            f"Expected 'qualify', got '{result.status}' (score={result.score})"
        )

    def test_score_at_least_55(self):
        answers = _manufacturing_ceo_answers()
        result = qualify(answers, POLICY_PATH)
        assert result.score >= 55, f"Expected score>=55, got {result.score}"

    def test_not_disqualified(self):
        answers = _manufacturing_ceo_answers()
        result = qualify(answers, POLICY_PATH)
        assert result.disqualified is False

    def test_has_reasons(self):
        answers = _manufacturing_ceo_answers()
        result = qualify(answers, POLICY_PATH)
        assert len(result.reasons) > 0


# ---------------------------------------------------------------------------
# Test 2: sparse submission -> defer or gap_only
# ---------------------------------------------------------------------------

class TestSparseSubmission:
    def _sparse_answers(self) -> dict:
        return {
            "company_name": "",
            "industry": "generic",
            "data_domains": [],
            "existing_system": "unknown",
            "persona_role": "other",
            "ceo_pain_frequency": "occasional",
            "ceo_user_count": "1-5",
            "ceo_budget_setup": "under_300",
            "ceo_data_security": "unknown",
            "it_db_dialect": "unknown",
            "it_frontend_pref": "unknown",
            "it_backend_pref": "unknown",
            "it_auth_method": "unknown",
            "contact_email": "anon@example.com",
            "free_notes": "",
        }

    def test_status_defer_or_gap_only(self):
        answers = self._sparse_answers()
        result = qualify(answers, POLICY_PATH)
        assert result.status in {"defer", "gap_only"}, (
            f"Sparse submission should defer or gap_only, got '{result.status}' (score={result.score})"
        )

    def test_not_disqualified(self):
        answers = self._sparse_answers()
        result = qualify(answers, POLICY_PATH)
        assert result.disqualified is False


# ---------------------------------------------------------------------------
# Test 3: gap detection — onpremise_only -> GapRecord, disqualified=False
# ---------------------------------------------------------------------------

class TestGapOnpremiseOnly:
    def test_gap_record_emitted(self):
        answers = {
            **_manufacturing_ceo_answers(),
            "ceo_data_security": "onpremise_only",
        }
        result = qualify(answers, POLICY_PATH)
        gap_categories = [g.gap_category for g in result.gaps]
        assert "deploy-model-onpremise" in gap_categories, (
            f"Expected 'deploy-model-onpremise' gap, got: {gap_categories}"
        )

    def test_onpremise_does_not_disqualify(self):
        answers = {
            **_manufacturing_ceo_answers(),
            "ceo_data_security": "onpremise_only",
        }
        result = qualify(answers, POLICY_PATH)
        assert result.disqualified is False, "onpremise_only must NEVER disqualify"

    def test_status_still_qualify(self):
        """onpremise_only gap must not drop a qualifying lead below qualify threshold."""
        answers = {
            **_manufacturing_ceo_answers(),
            "ceo_data_security": "onpremise_only",
        }
        result = qualify(answers, POLICY_PATH)
        # A well-completed mfg CEO with onpremise should still qualify
        assert result.status == "qualify", (
            f"onpremise_only must not block qualify; got '{result.status}' (score={result.score})"
        )


# ---------------------------------------------------------------------------
# Test 4: gap detection — mssql -> GapRecord dialect-mssql
# ---------------------------------------------------------------------------

class TestGapMssql:
    def test_mssql_gap_detected(self):
        answers = {
            **_manufacturing_ceo_answers(),
            "it_db_dialect": "mssql",
        }
        result = qualify(answers, POLICY_PATH)
        gap_categories = [g.gap_category for g in result.gaps]
        assert "dialect-mssql" in gap_categories, (
            f"Expected 'dialect-mssql' gap, got: {gap_categories}"
        )

    def test_mssql_gap_axis_is_ddl(self):
        answers = {
            **_manufacturing_ceo_answers(),
            "it_db_dialect": "mssql",
        }
        result = qualify(answers, POLICY_PATH)
        mssql_gaps = [g for g in result.gaps if g.gap_category == "dialect-mssql"]
        assert mssql_gaps, "dialect-mssql gap not found"
        assert mssql_gaps[0].todo_axis == "ddl"

    def test_mssql_does_not_disqualify(self):
        answers = {
            **_manufacturing_ceo_answers(),
            "it_db_dialect": "mssql",
        }
        result = qualify(answers, POLICY_PATH)
        assert result.disqualified is False


# ---------------------------------------------------------------------------
# Test 5: legal NOT a gap — industry=legal -> no disqualify, no vertical-legal gap
# ---------------------------------------------------------------------------

class TestLegalNotAGap:
    def _legal_answers(self) -> dict:
        base = _manufacturing_ceo_answers()
        base["industry"] = "legal"
        return base

    def test_legal_does_not_disqualify(self):
        result = qualify(self._legal_answers(), POLICY_PATH)
        assert result.disqualified is False

    def test_legal_no_vertical_legal_gap(self):
        """legal is already_served — no GapRecord should be emitted for it."""
        result = qualify(self._legal_answers(), POLICY_PATH)
        all_cats = [g.gap_category for g in result.gaps]
        # already_served:true means detect_gaps skips domain-expert-legal entirely
        assert "domain-expert-legal" not in all_cats, (
            f"legal is already_served and must NOT appear as a gap. Got gaps: {all_cats}"
        )
        # Confirm via direct detect_gaps call as well
        policy = load_policy(POLICY_PATH)
        direct_gaps = detect_gaps(self._legal_answers(), policy)
        legal_gaps = [g for g in direct_gaps if "legal" in g.gap_category.lower()]
        assert legal_gaps == [], (
            f"detect_gaps must emit no legal gaps (already_served). Got: {legal_gaps}"
        )

    def test_legal_can_qualify(self):
        """A well-completed legal firm submission should be able to qualify."""
        result = qualify(self._legal_answers(), POLICY_PATH)
        assert result.status in {"qualify", "defer"}, (
            f"Legal industry should not be gap_only from industry alone. "
            f"Got '{result.status}' (score={result.score}, gaps={[g.gap_category for g in result.gaps]})"
        )


# ---------------------------------------------------------------------------
# Test 6: scope_reject — consumer app mention
# ---------------------------------------------------------------------------

class TestScopeReject:
    def _consumer_app_answers(self) -> dict:
        base = _manufacturing_ceo_answers()
        base["free_notes"] = "We want to build a consumer app for end-users to book tickets."
        return base

    def test_status_scope_reject(self):
        result = qualify(self._consumer_app_answers(), POLICY_PATH)
        assert result.status == "scope_reject", (
            f"Expected 'scope_reject', got '{result.status}'"
        )

    def test_disqualified_true(self):
        result = qualify(self._consumer_app_answers(), POLICY_PATH)
        assert result.disqualified is True

    def test_gap_has_scope_category(self):
        result = qualify(self._consumer_app_answers(), POLICY_PATH)
        assert len(result.gaps) > 0
        assert result.gaps[0].gap_category.startswith("scope-"), (
            f"Expected scope- category, got {result.gaps[0].gap_category}"
        )


# ---------------------------------------------------------------------------
# Test 7: gap_registry_report — tally and render with 4 fake records
# ---------------------------------------------------------------------------

class TestGapRegistryReport:
    def _write_fake_registry(self, tmp_path: Path) -> Path:
        """Write 4 fake records: 3 with same category, 1 different."""
        registry_path = tmp_path / "gap-registry.jsonl"
        records = [
            {"ts": "2026-06-01T10:00:00Z", "slug": "alpha-mfg", "score": 45, "gap_category": "dialect-mssql", "todo_axis": "ddl"},
            {"ts": "2026-06-02T11:00:00Z", "slug": "beta-corp", "score": 38, "gap_category": "dialect-mssql", "todo_axis": "ddl"},
            {"ts": "2026-06-03T12:00:00Z", "slug": "gamma-ltd", "score": 42, "gap_category": "dialect-mssql", "todo_axis": "ddl"},
            {"ts": "2026-06-04T13:00:00Z", "slug": "delta-co",  "score": 35, "gap_category": "auth-sso-keycloak", "todo_axis": "creater"},
        ]
        with open(registry_path, "w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec) + "\n")
        return registry_path

    def test_load_registry(self, tmp_path):
        registry_path = self._write_fake_registry(tmp_path)
        records = load_registry(registry_path)
        assert len(records) == 4

    def test_tally_repeated_category_count_3(self, tmp_path):
        registry_path = self._write_fake_registry(tmp_path)
        records = load_registry(registry_path)
        tallied = tally_gaps(records)
        assert "dialect-mssql" in tallied
        assert tallied["dialect-mssql"]["count"] == 3, (
            f"Expected count=3 for dialect-mssql, got {tallied['dialect-mssql']['count']}"
        )

    def test_tally_second_category_count_1(self, tmp_path):
        registry_path = self._write_fake_registry(tmp_path)
        records = load_registry(registry_path)
        tallied = tally_gaps(records)
        assert "auth-sso-keycloak" in tallied
        assert tallied["auth-sso-keycloak"]["count"] == 1

    def test_render_summary_flags_promote(self, tmp_path):
        registry_path = self._write_fake_registry(tmp_path)
        records = load_registry(registry_path)
        tallied = tally_gaps(records)

        # Load real policy
        with open(POLICY_PATH, encoding="utf-8") as fh:
            import yaml
            policy = yaml.safe_load(fh)

        out_path = tmp_path / "gap-summary.md"
        render_summary(tallied, policy, out_path)

        assert out_path.exists(), "gap-summary.md was not created"
        content = out_path.read_text(encoding="utf-8")
        assert "PROMOTE" in content, (
            "Expected PROMOTE flag for dialect-mssql (count=3 >= threshold=3)"
        )
        assert "dialect-mssql" in content

    def test_render_summary_shows_closed_gaps(self, tmp_path):
        """Closed gaps (already_served:true) should appear in the 'Recently Closed' section."""
        registry_path = self._write_fake_registry(tmp_path)
        records = load_registry(registry_path)
        tallied = tally_gaps(records)

        with open(POLICY_PATH, encoding="utf-8") as fh:
            import yaml
            policy = yaml.safe_load(fh)

        out_path = tmp_path / "gap-summary.md"
        render_summary(tallied, policy, out_path)
        content = out_path.read_text(encoding="utf-8")
        # legal and finance are already_served in policy
        assert "Recently Closed Gaps" in content

    def test_empty_registry(self, tmp_path):
        """Empty registry should still render without errors."""
        registry_path = tmp_path / "empty.jsonl"
        registry_path.write_text("", encoding="utf-8")
        records = load_registry(registry_path)
        assert records == []
        tallied = tally_gaps(records)
        assert tallied == {}

        with open(POLICY_PATH, encoding="utf-8") as fh:
            import yaml
            policy = yaml.safe_load(fh)

        out_path = tmp_path / "empty-summary.md"
        render_summary(tallied, policy, out_path)
        assert out_path.exists()


# ---------------------------------------------------------------------------
# Test 8: score_answers — verify deterministic scoring
# ---------------------------------------------------------------------------

class TestScoreAnswers:
    def test_base_score_is_50_for_empty_answers(self):
        policy = load_policy(POLICY_PATH)
        score = score_answers({}, policy)
        # base_score=50, no additions, no subtractions
        assert score == 50

    def test_score_increases_with_known_stack(self):
        policy = load_policy(POLICY_PATH)
        base = score_answers({}, policy)
        with_stack = score_answers(
            {"it_frontend_pref": "react", "it_backend_pref": "fastapi"},
            policy,
        )
        assert with_stack > base

    def test_score_clamped_0_100(self):
        """Score must never exceed 100 or go below 0."""
        policy = load_policy(POLICY_PATH)
        # Max out positive signals
        answers = {
            "company_name": "TestCo",
            "data_domains": ["customer", "order", "inventory", "hr", "hr_leave", "approval"],
            "ceo_budget_setup": "over_1000",
            "existing_system": "legacy_system",
            "ceo_pain_frequency": "daily",
            "ceo_user_count": "51-100",
            "it_frontend_pref": "react",
            "it_backend_pref": "fastapi",
            "it_db_dialect": "postgres",
        }
        score = score_answers(answers, policy)
        assert 0 <= score <= 100
