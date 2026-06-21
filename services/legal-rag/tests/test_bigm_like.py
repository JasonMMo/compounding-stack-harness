"""
tests/test_bigm_like.py — unit tests for _build_bigm_like() (pure function).

No DB / sidecar required. Tests fragment construction, param format,
AND/OR operator handling, and edge cases (empty / special-chars-only input).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retrieve import _build_bigm_like


class TestBuildBigmLike:
    # ── AND operator ─────────────────────────────────────────────────────────

    def test_two_tokens_and_fragment(self):
        result = _build_bigm_like("손해배상 계약해지", "AND")
        assert result is not None
        frag, params = result
        assert frag == "(chunk_text LIKE %s AND chunk_text LIKE %s)"
        assert params == ["%손해배상%", "%계약해지%"]

    def test_single_token_and_fragment(self):
        result = _build_bigm_like("손해배상", "AND")
        assert result is not None
        frag, params = result
        assert frag == "(chunk_text LIKE %s)"
        assert params == ["%손해배상%"]

    def test_three_tokens_and_fragment(self):
        result = _build_bigm_like("손해배상 계약 해지", "AND")
        assert result is not None
        frag, params = result
        assert frag == "(chunk_text LIKE %s AND chunk_text LIKE %s AND chunk_text LIKE %s)"
        assert params == ["%손해배상%", "%계약%", "%해지%"]

    # ── OR operator ──────────────────────────────────────────────────────────

    def test_two_tokens_or_fragment(self):
        result = _build_bigm_like("손해배상 계약해지", "OR")
        assert result is not None
        frag, params = result
        assert frag == "(chunk_text LIKE %s OR chunk_text LIKE %s)"
        assert params == ["%손해배상%", "%계약해지%"]

    def test_single_token_or_fragment(self):
        result = _build_bigm_like("손해배상", "OR")
        assert result is not None
        frag, params = result
        assert frag == "(chunk_text LIKE %s)"
        assert params == ["%손해배상%"]

    # ── None cases ───────────────────────────────────────────────────────────

    def test_empty_string_returns_none(self):
        assert _build_bigm_like("", "AND") is None

    def test_whitespace_only_returns_none(self):
        assert _build_bigm_like("   ", "AND") is None

    def test_special_chars_only_returns_none(self):
        assert _build_bigm_like("!!! ???", "AND") is None

    # ── sanitize ─────────────────────────────────────────────────────────────

    def test_special_chars_stripped_from_tokens(self):
        result = _build_bigm_like("손해배상! 계약?해지", "AND")
        assert result is not None
        _, params = result
        assert params == ["%손해배상%", "%계약해지%"]

    def test_mixed_ascii_korean(self):
        result = _build_bigm_like("contract 손해배상", "AND")
        assert result is not None
        _, params = result
        assert params == ["%contract%", "%손해배상%"]

    # ── LIKE param does not contain SQL injection vectors ────────────────────

    def test_percent_in_search_term_preserved_in_value(self):
        """Token-level '%' is stripped by sanitize (not ASCII word / Korean)."""
        result = _build_bigm_like("100%완성", "AND")
        # '%' is stripped → token becomes '100완성'
        assert result is not None
        _, params = result
        assert params == ["%100완성%"]
