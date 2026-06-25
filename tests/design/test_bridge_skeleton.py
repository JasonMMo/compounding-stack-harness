"""tests/design/test_bridge_skeleton.py — Design-Cloud Bridge WP-1 스켈레톤 (L1 pytest).

검증:
  A. normalize.extract_candidates — HTML/CSS 에서 색/타이포/간격 후보 추출.
  B. dtcg_schema.load_semantic_keys — semantic.json 키 로드(_meta 제외).
  C. dtcg_schema.validate_token_overrides — 화이트리스트 위반 탐지 + landing extras 허용.

설계: docs/architecture/design-cloud-bridge-execution-plan.md (WP-1).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "design"))

import normalize  # noqa: E402
import dtcg_schema  # noqa: E402


class TestExtractCandidates:
    def test_extracts_hex_fonts_spacing(self) -> None:
        text = ".h{color:#1A2B3C;font-family:Inter,sans-serif;padding:24px;margin:1.5rem}"
        c = normalize.extract_candidates(text)
        assert "#1a2b3c" in c["colors"]  # lowercased
        assert any("Inter" in f for f in c["fonts"])
        assert "24px" in c["spacings"]
        assert "1.5rem" in c["spacings"]

    def test_dedups_and_empty(self) -> None:
        c = normalize.extract_candidates("color:#fff;color:#fff;")
        assert c["colors"] == ["#fff"]
        empty = normalize.extract_candidates("<div>no tokens</div>")
        assert empty == {"colors": [], "fonts": [], "spacings": []}


class TestDtcgSchema:
    def test_semantic_keys_exclude_meta(self) -> None:
        keys = dtcg_schema.load_semantic_keys()
        # semantic.json 이 있으면 color.primary 가 있고 _meta.* 는 없어야 함
        if keys:
            assert "color.primary" in keys
            assert not any(k.startswith("_meta") for k in keys)

    def test_validate_rejects_unknown_key(self) -> None:
        keys = dtcg_schema.load_semantic_keys()
        if not keys:
            return  # semantic.json 부재 환경 — skip
        violations = dtcg_schema.validate_token_overrides(
            {"color": {"primary": "#000", "totally-bogus-key": "#fff"}}
        )
        assert "color.totally-bogus-key" in violations
        assert "color.primary" not in violations

    def test_landing_extras_allowed(self) -> None:
        keys = dtcg_schema.load_semantic_keys()
        if not keys:
            return
        violations = dtcg_schema.validate_token_overrides(
            {"color": {"hero-bg-from": "#111", "hero-bg-to": "#222"}},
            allow_landing_extras=True,
        )
        assert violations == []
