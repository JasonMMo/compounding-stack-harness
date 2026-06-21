"""
tests/test_fts_or_tsquery.py — unit tests for _build_or_tsquery() and _build_tsquery() (pure functions).

No DB / sidecar required. Tests sanitize logic, OR/AND joining, and edge cases.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retrieve import _build_or_tsquery, _build_tsquery


class TestBuildOrTsquery:
    # ── basic OR joining ──────────────────────────────────────────────────────

    def test_two_korean_tokens_joined_with_or(self):
        result = _build_or_tsquery("손해배상 계약해지")
        assert result == "손해배상 | 계약해지"

    def test_single_token_returned_as_is(self):
        result = _build_or_tsquery("손해배상")
        assert result == "손해배상"

    def test_three_tokens(self):
        result = _build_or_tsquery("손해배상 계약 해지")
        assert result == "손해배상 | 계약 | 해지"

    # ── sanitize ─────────────────────────────────────────────────────────────

    def test_special_chars_stripped(self):
        # to_tsquery raises on '!', '&', etc. — must be removed.
        result = _build_or_tsquery("손해배상! 계약?해지")
        assert result == "손해배상 | 계약해지"

    def test_token_with_only_special_chars_dropped(self):
        result = _build_or_tsquery("손해배상 !!! 계약해지")
        assert result == "손해배상 | 계약해지"

    def test_mixed_ascii_korean(self):
        result = _build_or_tsquery("contract 손해배상")
        assert result == "contract | 손해배상"

    def test_digits_kept(self):
        result = _build_or_tsquery("2024년 판결")
        assert result == "2024년 | 판결"

    # ── empty / degenerate ────────────────────────────────────────────────────

    def test_empty_string_returns_none(self):
        assert _build_or_tsquery("") is None

    def test_whitespace_only_returns_none(self):
        assert _build_or_tsquery("   ") is None

    def test_all_special_chars_returns_none(self):
        assert _build_or_tsquery("!!! ???") is None

    # ── whitespace normalization ──────────────────────────────────────────────

    def test_extra_whitespace_between_tokens(self):
        result = _build_or_tsquery("손해배상   계약해지")
        assert result == "손해배상 | 계약해지"

    def test_leading_trailing_whitespace(self):
        result = _build_or_tsquery("  손해배상  ")
        assert result == "손해배상"


class TestBuildTsqueryAndOperator:
    """_build_tsquery with AND operator (' & ')."""

    def test_two_tokens_joined_with_and(self):
        result = _build_tsquery("손해배상 계약해지", " & ")
        assert result == "손해배상 & 계약해지"

    def test_single_token_returned_as_is(self):
        result = _build_tsquery("손해배상", " & ")
        assert result == "손해배상"

    def test_none_on_empty_string(self):
        assert _build_tsquery("", " & ") is None

    def test_none_on_special_chars_only(self):
        assert _build_tsquery("!!! ???", " & ") is None

    def test_three_tokens(self):
        result = _build_tsquery("손해배상 계약 해지", " & ")
        assert result == "손해배상 & 계약 & 해지"

    def test_or_operator_still_works_via_build_tsquery(self):
        result = _build_tsquery("손해배상 계약해지", " | ")
        assert result == "손해배상 | 계약해지"
