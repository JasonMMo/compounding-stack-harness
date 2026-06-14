"""tests/test_vision_qa_phase4.py — Phase 4 vision-QA gate tests (L1 pytest).

Covers:
  A. ui_check --full-vision: request generation (fixture dir), PII-free content,
     graceful behaviour when no screenshots exist.
  B. diagnose G-15: SPEC when no marketing-site cases / no case dir;
     FAIL when a delivered marketing-site case has no verdict;
     PASS when verdict=PASS exists.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# ── resolve repo root so imports work without install ────────────────────────
_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "scripts"))
sys.path.insert(0, str(_REPO / "scripts" / "workflow"))

import diagnose  # noqa: E402
from ui_check import _emit_vision_review_request  # noqa: E402


# ===========================================================================
# A. ui_check --full-vision: _emit_vision_review_request
# ===========================================================================

class TestEmitVisionReviewRequest:
    """_emit_vision_review_request generates correct JSON, no LLM, PII-free."""

    def _make_shot_dir(self, tmp: Path) -> Path:
        shot_dir = tmp / "ui-shots" / "fixture-slug"
        shot_dir.mkdir(parents=True)
        return shot_dir

    def test_empty_shot_dir_returns_empty_list_no_error(self, tmp_path: Path) -> None:
        """No screenshots -> empty list, file still written (graceful)."""
        shot_dir = self._make_shot_dir(tmp_path)
        out_dir = tmp_path / "ui-checks"

        import io
        import contextlib
        buf = io.StringIO()
        # The function prints a WARNING to stderr; capture it.
        with contextlib.redirect_stderr(buf):
            req_path = _emit_vision_review_request(
                slug="fixture-slug",
                shot_dir=shot_dir,
                out_dir=out_dir,
            )

        assert req_path.exists()
        data = json.loads(req_path.read_text(encoding="utf-8"))
        assert data["slug"] == "fixture-slug"
        assert data["screenshots"] == []
        assert data["generated_by"] == "ui_check --full-vision"
        assert "rubric" in data
        assert "instructions" in data
        # WARNING printed
        assert "WARNING" in buf.getvalue()

    def test_screenshots_collected_by_viewport_prefix(self, tmp_path: Path) -> None:
        """PNGs named desktop_* / mobile_* are grouped into correct viewport."""
        shot_dir = self._make_shot_dir(tmp_path)
        (shot_dir / "desktop_login.png").write_bytes(b"\x89PNG")
        (shot_dir / "desktop_root.png").write_bytes(b"\x89PNG")
        (shot_dir / "mobile_login.png").write_bytes(b"\x89PNG")

        out_dir = tmp_path / "ui-checks"
        req_path = _emit_vision_review_request(
            slug="fixture-slug",
            shot_dir=shot_dir,
            out_dir=out_dir,
        )

        data = json.loads(req_path.read_text(encoding="utf-8"))
        shots = data["screenshots"]
        assert len(shots) == 3

        viewports = {s["viewport"] for s in shots}
        assert viewports == {"desktop", "mobile"}

        pages = {s["page"] for s in shots}
        assert "/login" in pages

    def test_output_is_pii_free(self, tmp_path: Path) -> None:
        """Request JSON must not contain email patterns."""
        shot_dir = self._make_shot_dir(tmp_path)
        (shot_dir / "desktop_login.png").write_bytes(b"\x89PNG")
        out_dir = tmp_path / "ui-checks"
        req_path = _emit_vision_review_request(
            slug="fixture-slug",
            shot_dir=shot_dir,
            out_dir=out_dir,
        )
        raw = req_path.read_text(encoding="utf-8")
        import re
        # No email pattern in the JSON
        assert not re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", raw)

    def test_reference_shots_dir_included_when_exists(self, tmp_path: Path) -> None:
        """reference_shots_dir key is included only when design/references/<slug>/ exists."""
        shot_dir = self._make_shot_dir(tmp_path)
        out_dir = tmp_path / "ui-checks"

        # Temporarily patch _REPO_ROOT inside ui_check to point to tmp_path
        import ui_check as _uc
        original_root = _uc._REPO_ROOT
        _uc._REPO_ROOT = tmp_path  # type: ignore[attr-defined]

        try:
            # Without reference dir: key absent
            req_path = _emit_vision_review_request(
                slug="fixture-slug",
                shot_dir=shot_dir,
                out_dir=out_dir,
            )
            data = json.loads(req_path.read_text(encoding="utf-8"))
            assert "reference_shots_dir" not in data

            # With reference dir present: key included
            ref_dir = tmp_path / "design" / "references" / "fixture-slug"
            ref_dir.mkdir(parents=True)
            req_path2 = _emit_vision_review_request(
                slug="fixture-slug",
                shot_dir=shot_dir,
                out_dir=out_dir,
            )
            data2 = json.loads(req_path2.read_text(encoding="utf-8"))
            assert "reference_shots_dir" in data2
        finally:
            _uc._REPO_ROOT = original_root  # type: ignore[attr-defined]

    def test_output_written_to_correct_path(self, tmp_path: Path) -> None:
        """Output file is <out_dir>/<slug>-vision-request.json."""
        shot_dir = self._make_shot_dir(tmp_path)
        out_dir = tmp_path / "ui-checks"
        req_path = _emit_vision_review_request(
            slug="my-slug",
            shot_dir=shot_dir,
            out_dir=out_dir,
        )
        assert req_path == out_dir / "my-slug-vision-request.json"
        assert req_path.exists()


# ===========================================================================
# B. diagnose G-15: g15_marketing_site_visual_gate
# ===========================================================================

_SLUG = "mktsite-abc"


def _write_case(cases_dir: Path, slug: str, *, deliverable_kind: str, triage_status: str) -> None:
    """Write a minimal marketing-site case YAML into cases_dir."""
    content = (
        f"slug: {slug}\n"
        f"deliverable_kind: {deliverable_kind}\n"
        f"triage_status: {triage_status}\n"
    )
    (cases_dir / f"{slug}.yaml").write_text(content, encoding="utf-8")


def _write_verdict(ui_checks_dir: Path, slug: str, verdict: str) -> None:
    """Write a vision-verdict JSON."""
    ui_checks_dir.mkdir(parents=True, exist_ok=True)
    data = {"slug": slug, "verdict": verdict, "scores": {}}
    (ui_checks_dir / f"{slug}-vision-verdict.json").write_text(
        json.dumps(data), encoding="utf-8"
    )


class TestG15MarketingSiteVisualGate:
    """G-15 uses cases_dir / ui_checks_dir injection (same pattern as G-14)."""

    def _run(self, cases_dir: Path, ui_checks_dir: Path) -> diagnose.GuardResult:
        return diagnose.g15_marketing_site_visual_gate(
            cases_dir=cases_dir,
            ui_checks_dir=ui_checks_dir,
        )

    def test_spec_when_cases_dir_absent(self, tmp_path: Path) -> None:
        result = diagnose.g15_marketing_site_visual_gate(
            cases_dir=tmp_path / "nonexistent",
            ui_checks_dir=tmp_path / "ui-checks",
        )
        assert result.status == "SPEC"

    def test_spec_when_no_case_files(self, tmp_path: Path) -> None:
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir(parents=True)
        result = self._run(cases_dir, tmp_path / "ui-checks")
        assert result.status == "SPEC"

    def test_spec_when_no_marketing_site_case(self, tmp_path: Path) -> None:
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir(parents=True)
        _write_case(cases_dir, "biz-case", deliverable_kind="business-system", triage_status="qualify")
        result = self._run(cases_dir, tmp_path / "ui-checks")
        assert result.status == "SPEC"

    def test_pass_when_marketing_site_not_yet_delivered(self, tmp_path: Path) -> None:
        """A marketing-site case in qualify (not delivered) -> PASS (no violation yet)."""
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir(parents=True)
        _write_case(cases_dir, _SLUG, deliverable_kind="marketing-site", triage_status="qualify")
        result = self._run(cases_dir, tmp_path / "ui-checks")
        assert result.status == "PASS"
        assert result.violations == []

    def test_fail_when_delivered_without_verdict_file(self, tmp_path: Path) -> None:
        """DELIVERED marketing-site case with no verdict file -> FAIL."""
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir(parents=True)
        _write_case(cases_dir, _SLUG, deliverable_kind="marketing-site", triage_status="delivered")
        result = self._run(cases_dir, tmp_path / "ui-checks")
        assert result.status == "FAIL"
        assert any(_SLUG in v for v in result.violations)

    def test_fail_when_delivered_with_block_verdict(self, tmp_path: Path) -> None:
        """DELIVERED case with verdict=BLOCK -> FAIL."""
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir(parents=True)
        _write_case(cases_dir, _SLUG, deliverable_kind="marketing-site", triage_status="delivered")
        ui_checks_dir = tmp_path / "ui-checks"
        _write_verdict(ui_checks_dir, _SLUG, "BLOCK")
        result = self._run(cases_dir, ui_checks_dir)
        assert result.status == "FAIL"
        assert any("BLOCK" in v for v in result.violations)

    def test_pass_when_delivered_with_pass_verdict(self, tmp_path: Path) -> None:
        """DELIVERED case with verdict=PASS -> PASS."""
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir(parents=True)
        _write_case(cases_dir, _SLUG, deliverable_kind="marketing-site", triage_status="delivered")
        ui_checks_dir = tmp_path / "ui-checks"
        _write_verdict(ui_checks_dir, _SLUG, "PASS")
        result = self._run(cases_dir, ui_checks_dir)
        assert result.status == "PASS"
        assert result.violations == []

    def test_readme_excluded_from_case_files(self, tmp_path: Path) -> None:
        """README.yaml in cases dir is not treated as a case file."""
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir(parents=True)
        (cases_dir / "README.yaml").write_text("# readme\n", encoding="utf-8")
        result = self._run(cases_dir, tmp_path / "ui-checks")
        assert result.status == "SPEC"

    def test_case_with_nested_deliverable_kind(self, tmp_path: Path) -> None:
        """deliverable_kind under stack: sub-key is also recognised."""
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir(parents=True)
        content = (
            f"slug: {_SLUG}\n"
            f"triage_status: delivered\n"
            f"stack:\n"
            f"  deliverable_kind: marketing-site\n"
        )
        (cases_dir / f"{_SLUG}.yaml").write_text(content, encoding="utf-8")
        result = self._run(cases_dir, tmp_path / "ui-checks")
        assert result.status == "FAIL"  # delivered + no verdict
