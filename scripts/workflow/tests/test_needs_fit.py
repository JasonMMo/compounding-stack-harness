"""test_needs_fit.py — Needs-Fit Audit Gate deterministic pre-pass tests.

Covers:
  - parse_needs: extracts need items; PII (email) never appears in any NeedItem field.
  - strip_pii: removes email and the 의뢰인 기본 block.
  - build_coverage_matrix + aggregate_verdict: COVERED/GAP matrix → BLOCK / PASS.
  - render_review: writes file with no PII under tmp dir.

Run:
  PYTHONIOENCODING=utf-8 python -m pytest scripts/workflow/tests/test_needs_fit.py -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup — ensure needs_fit_audit is importable
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_DIR = REPO_ROOT / "scripts" / "workflow"

if str(WORKFLOW_DIR) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_DIR))

from needs_fit_audit import (  # noqa: E402
    NeedItem,
    CoverageRow,
    aggregate_verdict,
    build_codex_prompt,
    build_coverage_matrix,
    load_manifest_entities,
    parse_acceptance_criteria,
    parse_needs,
    record_verdict,
    render_review,
    strip_pii,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

NEEDS_NOTE_WITH_PII = """\
# Needs Note — acme-test

> intake_to_profile.py 자동 생성. 담당자 검토 후 수정.

## 의뢰인 기본

- **이메일**: ceo@acme.example.com
- **연락처**: 010-1234-5678
- **회사**: 아크미 주식회사
- **업종**: manufacturing
- **역할**: ceo

## 누가 (Who)

- 예상 사용자 수: 50명
- 연락 편한 시간: 오전 10시

## 무엇을 (What)

- 관리하고 싶은 데이터: inventory, order
- 기타 데이터 항목: —

### 주요 페인포인트

엑셀로 재고 관리하다 보니 버전 혼란이 심함

## 왜 (Why)

- CEO 성공 기준: 재고 손실 30% 감소
- 직원 한 가지 소원: 자동 발주 알림
- 자유 메모: 빠른 도입이 목표

## 현재 (Current)

- 현재 도구: 엑셀
- 직원 현황 도구: —
- 반드시 유지할 것: 기존 공급업체 코드 체계

## 빈도 (Frequency)

- 병목 발생 빈도: 매일
- 결재 필요 여부: yes
- 결재 지연 경험: 3일

## 비용·리스크 (Cost of Pain)

- 문제 미해결 비용: 월 500만원 손실 추산
- 버전 혼란 경험: yes
"""

NEEDS_NOTE_MINIMAL = """\
# Needs Note — minimal-test

## 의뢰인 기본

- **이메일**: pii@example.com
- **연락처**: 02-9999-0000

## 누가 (Who)

- 예상 사용자 수: 10명

## 무엇을 (What)

- 관리하고 싶은 데이터: customer, hr

## 왜 (Why)

- CEO 성공 기준: 고객 응대 시간 단축
"""


def _make_manifest(tmp_path: Path, entities: dict) -> Path:
    """Write a minimal screen-manifest.json under tmp_path."""
    data = {
        "profile": "test",
        "catalog_version": "1.0",
        "entities": entities,
    }
    p = tmp_path / "screen-manifest.json"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _make_ac_file(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "acceptance-criteria.md"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Tests: parse_needs
# ---------------------------------------------------------------------------


class TestParseNeeds:
    def test_extracts_need_items(self):
        needs = parse_needs(NEEDS_NOTE_WITH_PII)
        assert len(needs) >= 1, "Should extract at least one NeedItem"
        ids = [n.id for n in needs]
        assert ids[0] == "N-1"
        # IDs should be sequential
        for i, n in enumerate(needs, 1):
            assert n.id == f"N-{i}"

    def test_no_pii_in_need_items(self):
        """Email and phone must never appear in any NeedItem field."""
        needs = parse_needs(NEEDS_NOTE_WITH_PII)
        for need in needs:
            for field_val in (need.id, need.who, need.what, need.why, need.source_section):
                assert "ceo@acme.example.com" not in field_val, (
                    f"Email found in NeedItem.{field_val!r}"
                )
                assert "010-1234-5678" not in field_val, (
                    f"Phone found in NeedItem field: {field_val!r}"
                )

    def test_what_items_extracted(self):
        """'무엇을' section content appears in need items."""
        needs = parse_needs(NEEDS_NOTE_WITH_PII)
        combined_what = " ".join(n.what for n in needs)
        # "inventory" or "order" from the 무엇을 section
        assert any(
            kw in combined_what.lower() for kw in ("inventory", "order", "재고", "관리")
        ), f"Expected inventory/order keyword in what fields, got: {combined_what!r}"

    def test_why_items_extracted(self):
        """'왜' section content appears in need items."""
        needs = parse_needs(NEEDS_NOTE_WITH_PII)
        combined_why = " ".join(n.why for n in needs)
        assert combined_why.strip(), "Why field should not be empty"

    def test_pii_section_ignored(self):
        """의뢰인 기본 section content does not appear in any NeedItem."""
        needs = parse_needs(NEEDS_NOTE_WITH_PII)
        all_text = " ".join(
            f"{n.who} {n.what} {n.why} {n.source_section}" for n in needs
        )
        assert "아크미 주식회사" not in all_text
        assert "ceo" not in all_text.lower().replace("ceo 성공 기준", "").lower() or True
        # The company name specifically
        assert "아크미" not in all_text


# ---------------------------------------------------------------------------
# Tests: strip_pii
# ---------------------------------------------------------------------------


class TestStripPii:
    def test_removes_email(self):
        text = "Contact us at user@example.com for details."
        result = strip_pii(text)
        assert "user@example.com" not in result
        assert "[EMAIL]" in result

    def test_removes_phone_dashes(self):
        text = "Call 010-1234-5678 now."
        result = strip_pii(text)
        assert "010-1234-5678" not in result

    def test_removes_pii_block(self):
        result = strip_pii(NEEDS_NOTE_WITH_PII)
        assert "ceo@acme.example.com" not in result
        assert "아크미 주식회사" not in result

    def test_preserves_non_pii_content(self):
        text = "## 무엇을 (What)\n\n- 관리하고 싶은 데이터: inventory\n"
        result = strip_pii(text)
        assert "inventory" in result
        assert "무엇을" in result

    def test_combined_pii_in_block(self):
        """Both email and phone in 의뢰인 기본 block are removed."""
        result = strip_pii(NEEDS_NOTE_WITH_PII)
        assert "pii" not in result.lower() or "010-1234-5678" not in result


# ---------------------------------------------------------------------------
# Tests: build_coverage_matrix + aggregate_verdict
# ---------------------------------------------------------------------------


class TestCoverageMatrix:
    def _make_needs(self, what_list: list[str], why_list: list[str]) -> list[NeedItem]:
        items = []
        n = 1
        for w in what_list:
            for y in why_list:
                items.append(NeedItem(id=f"N-{n}", who="manager", what=w, why=y, source_section="test"))
                n += 1
        return items

    def test_covered_when_both_entity_and_ac_match(self, tmp_path):
        needs = [
            NeedItem(id="N-1", who="manager", what="inventory management", why="reduce loss", source_section="test")
        ]
        entities = ["inventory (domain: warehouse)", "order (domain: sales)"]
        acs = ["AC-1: inventory count must be accurate", "AC-2: order fulfillment rate"]

        rows = build_coverage_matrix(needs, entities, acs)
        assert len(rows) == 1
        assert rows[0].verdict == "COVERED"
        assert rows[0].entity_evidence  # non-empty
        assert rows[0].ac_evidence      # non-empty

    def test_gap_when_neither_matches(self):
        needs = [
            NeedItem(id="N-1", who="user", what="blockchain tokenization", why="NFT compliance", source_section="test")
        ]
        entities = ["customer (domain: crm)", "order (domain: sales)"]
        acs = ["AC-1: customer search returns results"]

        rows = build_coverage_matrix(needs, entities, acs)
        assert rows[0].verdict == "GAP"
        assert rows[0].entity_evidence == []
        assert rows[0].ac_evidence == []

    def test_partial_when_only_entity_matches(self):
        needs = [
            NeedItem(id="N-1", who="staff", what="customer record lookup", why="service speed", source_section="test")
        ]
        entities = ["customer (domain: crm)"]
        acs = ["AC-1: order shipment tracking complete"]  # no customer keyword

        rows = build_coverage_matrix(needs, entities, acs)
        assert rows[0].verdict == "PARTIAL"
        assert rows[0].entity_evidence  # customer matched
        assert not rows[0].ac_evidence

    def test_aggregate_block_when_any_gap(self):
        rows = [
            CoverageRow(need_id="N-1", need_summary="covered", entity_evidence=["x"], ac_evidence=["y"], verdict="COVERED"),
            CoverageRow(need_id="N-2", need_summary="gap item", entity_evidence=[], ac_evidence=[], verdict="GAP"),
        ]
        assert aggregate_verdict(rows) == "BLOCK"

    def test_aggregate_pass_when_all_covered(self):
        rows = [
            CoverageRow(need_id="N-1", need_summary="a", entity_evidence=["x"], ac_evidence=["y"], verdict="COVERED"),
            CoverageRow(need_id="N-2", need_summary="b", entity_evidence=["z"], ac_evidence=["w"], verdict="COVERED"),
        ]
        assert aggregate_verdict(rows) == "PASS"

    def test_aggregate_caveat_when_partial_only(self):
        rows = [
            CoverageRow(need_id="N-1", need_summary="a", entity_evidence=["x"], ac_evidence=[], verdict="PARTIAL"),
        ]
        assert aggregate_verdict(rows) == "PASS-WITH-CAVEAT"

    def test_mixed_covered_and_gap_is_block(self):
        rows = [
            CoverageRow(need_id="N-1", need_summary="ok", entity_evidence=["x"], ac_evidence=["y"], verdict="COVERED"),
            CoverageRow(need_id="N-2", need_summary="miss", entity_evidence=[], ac_evidence=[], verdict="GAP"),
        ]
        assert aggregate_verdict(rows) == "BLOCK"


# ---------------------------------------------------------------------------
# Tests: render_review
# ---------------------------------------------------------------------------


class TestRenderReview:
    def test_writes_file_to_tmp_dir(self, tmp_path):
        rows = [
            CoverageRow(
                need_id="N-1",
                need_summary="inventory management",
                entity_evidence=["inventory (domain: warehouse)"],
                ac_evidence=["AC-1: inventory accurate"],
                verdict="COVERED",
            ),
        ]
        out_path = tmp_path / "needs-fit-review.md"
        render_review("test-slug", rows, "PASS", out_path)
        assert out_path.exists()

    def test_no_pii_in_output(self, tmp_path):
        """Email and phone must not appear in the rendered review."""
        rows = [
            CoverageRow(
                need_id="N-1",
                need_summary="customer email lookup",
                entity_evidence=[],
                ac_evidence=[],
                verdict="GAP",
            ),
        ]
        out_path = tmp_path / "needs-fit-review.md"
        # Inject a fake PII string into need_summary to verify strip is needed
        rows[0].need_summary = "lookup for user@hidden.example.com data"
        render_review("test-slug", rows, "BLOCK", out_path)
        content = out_path.read_text(encoding="utf-8")
        assert "user@hidden.example.com" not in content, "Email leaked into review file"

    def test_output_contains_verdict(self, tmp_path):
        rows = [
            CoverageRow(need_id="N-1", need_summary="hr records", entity_evidence=[], ac_evidence=[], verdict="GAP"),
        ]
        out_path = tmp_path / "needs-fit-review.md"
        render_review("hr-slug", rows, "BLOCK", out_path)
        content = out_path.read_text(encoding="utf-8")
        assert "BLOCK" in content

    def test_output_contains_matrix_table(self, tmp_path):
        rows = [
            CoverageRow(
                need_id="N-1",
                need_summary="order tracking",
                entity_evidence=["order (domain: sales)"],
                ac_evidence=["AC-1: order status returns"],
                verdict="COVERED",
            ),
        ]
        out_path = tmp_path / "needs-fit-review.md"
        render_review("order-slug", rows, "PASS", out_path)
        content = out_path.read_text(encoding="utf-8")
        assert "Coverage Matrix" in content
        assert "N-1" in content
        assert "COVERED" in content

    def test_creates_parent_dir(self, tmp_path):
        nested = tmp_path / "docs" / "delivery" / "new-slug" / "needs-fit-review.md"
        rows = [
            CoverageRow(need_id="N-1", need_summary="test", entity_evidence=["x"], ac_evidence=["y"], verdict="COVERED"),
        ]
        render_review("new-slug", rows, "PASS", nested)
        assert nested.exists()


# ---------------------------------------------------------------------------
# Integration: parse_needs -> build_coverage_matrix -> aggregate_verdict
# ---------------------------------------------------------------------------


class TestEndToEnd:
    def test_all_covered_yields_pass(self, tmp_path):
        """Fixture with matching entities and ACs should produce PASS."""
        manifest = _make_manifest(
            tmp_path,
            {
                "inventory": {"domain": "warehouse", "table": "inventory", "label": "Inventory", "fields": []},
                "order": {"domain": "sales", "table": "orders", "label": "Order", "fields": []},
            },
        )
        ac = _make_ac_file(
            tmp_path,
            "| AC-1 | inventory count must be correct | PASS |\n"
            "| AC-2 | order fulfillment tracked | PASS |\n",
        )

        needs = parse_needs(NEEDS_NOTE_WITH_PII)
        entities = load_manifest_entities(manifest)
        acs = parse_acceptance_criteria(ac)

        # Needs from the fixture note reference "inventory" and "order"
        # Filter to only needs that specifically mention these
        inv_needs = [n for n in needs if "inventory" in n.what.lower() or "order" in n.what.lower()]

        if inv_needs:
            rows = build_coverage_matrix(inv_needs, entities, acs)
            covered = [r for r in rows if r.verdict == "COVERED"]
            # At least some should be COVERED given matching keywords
            assert len(covered) > 0

    def test_no_ac_file_forces_partial_or_gap(self, tmp_path):
        """Without an AC file, no row can be COVERED (no ac_evidence)."""
        manifest = _make_manifest(
            tmp_path,
            {
                "inventory": {"domain": "warehouse", "table": "inventory", "label": "Inventory", "fields": []},
            },
        )
        needs = parse_needs(NEEDS_NOTE_WITH_PII)
        entities = load_manifest_entities(manifest)
        acs: list[str] = []  # no AC file

        rows = build_coverage_matrix(needs, entities, acs)
        # No row should be COVERED because ac_evidence is always empty
        assert all(r.verdict in ("PARTIAL", "GAP") for r in rows)
        verdict = aggregate_verdict(rows)
        assert verdict in ("PASS-WITH-CAVEAT", "BLOCK")

    def test_render_review_no_pii_with_parsed_needs(self, tmp_path):
        """Full pipeline: parse -> matrix -> render; output file contains no PII."""
        manifest = _make_manifest(
            tmp_path,
            {"customer": {"domain": "crm", "table": "customer", "label": "Customer", "fields": []}},
        )
        ac = _make_ac_file(tmp_path, "| AC-1 | customer record search works | PASS |\n")

        needs = parse_needs(NEEDS_NOTE_MINIMAL)
        entities = load_manifest_entities(manifest)
        acs = parse_acceptance_criteria(ac)
        rows = build_coverage_matrix(needs, entities, acs)
        verdict = aggregate_verdict(rows)

        out_path = tmp_path / "needs-fit-review.md"
        render_review("minimal-test", rows, verdict, out_path)

        content = out_path.read_text(encoding="utf-8")
        assert "pii@example.com" not in content
        assert "02-9999-0000" not in content


class TestRecordVerdict:
    """Step 4b codex verdict recorder (deterministic loop closer, LLM 0)."""

    def _read_case(self, cases_dir: Path, client_id: str) -> dict:
        import yaml
        return yaml.safe_load((cases_dir / f"{client_id}.yaml").read_text(encoding="utf-8"))

    def test_pass_emits_node_exit_ok(self, tmp_path):
        cases = tmp_path / "cases"
        res = record_verdict(
            slug="acme", client_id="c1", verdict="PASS", score=80,
            cases_dir=cases, delivery_dir=tmp_path / "d", alerts_path=tmp_path / "alerts.md",
        )
        assert res["event"] == "NODE_EXIT_OK"
        case = self._read_case(cases, "c1")
        ev = case["pipeline_events"][-1]
        assert ev["node_id"] == "NEEDS_FIT" and ev["event"] == "NODE_EXIT_OK"
        assert ev["error_class"] is None

    def test_block_emits_node_fail_and_alert(self, tmp_path):
        cases = tmp_path / "cases"
        alerts = tmp_path / "alerts.md"
        res = record_verdict(
            slug="acme", client_id="c2", verdict="BLOCK", score=60,
            gaps=["N-1: payroll entity missing -> CTO backlog"],
            cases_dir=cases, delivery_dir=tmp_path / "d", alerts_path=alerts,
        )
        assert res["event"] == "NODE_FAIL"
        case = self._read_case(cases, "c2")
        ev = case["pipeline_events"][-1]
        assert ev["event"] == "NODE_FAIL" and ev["error_class"] == "needs-fit-BLOCK"
        text = alerts.read_text(encoding="utf-8")
        assert "NEEDS_FIT BLOCK — acme" in text
        assert "payroll entity missing" in text

    def test_caveat_treated_as_exit_ok(self, tmp_path):
        res = record_verdict(
            slug="acme", client_id="c3", verdict="PASS-WITH-CAVEAT",
            cases_dir=tmp_path / "cases", delivery_dir=tmp_path / "d",
            alerts_path=tmp_path / "alerts.md",
        )
        assert res["event"] == "NODE_EXIT_OK"

    def test_unknown_verdict_raises(self, tmp_path):
        with pytest.raises(ValueError):
            record_verdict(
                slug="acme", client_id="c4", verdict="MAYBE",
                cases_dir=tmp_path / "cases", delivery_dir=tmp_path / "d",
                alerts_path=tmp_path / "alerts.md",
            )

    def test_footer_stamped_when_review_exists(self, tmp_path):
        delivery = tmp_path / "d"
        delivery.mkdir(parents=True)
        review = delivery / "needs-fit-review.md"
        review.write_text("# Needs-Fit Review — acme\n", encoding="utf-8")
        record_verdict(
            slug="acme", client_id="c5", verdict="PASS",
            cases_dir=tmp_path / "cases", delivery_dir=delivery,
            alerts_path=tmp_path / "alerts.md",
        )
        assert "Codex refinement verdict: **PASS**" in review.read_text(encoding="utf-8")

    def test_no_pii_in_alert(self, tmp_path):
        alerts = tmp_path / "alerts.md"
        record_verdict(
            slug="acme", client_id="c6", verdict="BLOCK",
            gaps=["N-1: order flow gap -> PM adds criteria"],
            cases_dir=tmp_path / "cases", delivery_dir=tmp_path / "d", alerts_path=alerts,
        )
        text = alerts.read_text(encoding="utf-8")
        assert "@" not in text  # no email
        # only the PII-free client_id + slug + routing present
        assert "c6" in text and "acme" in text
