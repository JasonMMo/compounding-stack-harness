"""
tests/test_token_css_generator.py — L1 unit tests for token_css_generator.py.

Verifies the generator contract from design/tokens/README.md:
1. raw.json  → --raw-* variables emitted in :root
2. semantic.json → {ref} resolved, variables emitted without --raw- prefix
3. persona files → [data-persona="<name>"] scoped override blocks
4. _meta / _density / note / font shorthand keys are stripped
5. No raw hex values appear in component styles (spot-check app.css)
"""

import pathlib
import re
import sys

import pytest

_ADAPTER_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_ADAPTER_ROOT))

from token_css_generator import generate, _tokens_dir, _resolve_ref, _get_nested


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def css() -> str:
    return generate()


@pytest.fixture(scope="module")
def tokens_dir() -> pathlib.Path:
    return _tokens_dir()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _find_css_var(css_text: str, var_name: str) -> str | None:
    """Return the value for a CSS custom property declaration, or None."""
    m = re.search(rf"({re.escape(var_name)})\s*:\s*([^;]+);", css_text)
    return m.group(2).strip() if m else None


# ---------------------------------------------------------------------------
# Raw layer
# ---------------------------------------------------------------------------

class TestRawLayer:
    def test_raw_color_gray_900_emitted(self, css):
        val = _find_css_var(css, "--raw-color-gray-900")
        assert val == "#111827", f"Expected #111827, got {val!r}"

    def test_raw_space_8_emitted(self, css):
        val = _find_css_var(css, "--raw-space-8")
        assert val == "16px", f"Expected 16px, got {val!r}"

    def test_raw_accent_600_emitted(self, css):
        val = _find_css_var(css, "--raw-color-accent-600")
        assert val == "#2563EB", f"Expected #2563EB, got {val!r}"

    def test_raw_vars_in_root_block(self, css):
        # The :root block must exist and contain --raw- vars
        assert "--raw-color-gray-900: #111827;" in css

    def test_meta_key_not_emitted(self, css):
        assert "--raw--meta" not in css
        assert "--raw-meta" not in css

    def test_note_key_not_emitted(self, css):
        # The 'note' key inside color.accent should not be emitted
        assert "--raw-color-accent-note" not in css


# ---------------------------------------------------------------------------
# Semantic layer — reference resolution
# ---------------------------------------------------------------------------

class TestSemanticLayer:
    def test_color_primary_resolves_to_accent_600(self, css):
        # semantic: color.primary = {color.accent.600} = #2563EB
        val = _find_css_var(css, "--color-primary")
        assert val == "#2563EB", f"Expected #2563EB, got {val!r}"

    def test_color_danger_resolves_to_red_600(self, css):
        # semantic: color.danger = {color.red.600} = #DC2626
        val = _find_css_var(css, "--color-danger")
        assert val == "#DC2626", f"Expected #DC2626, got {val!r}"

    def test_font_family_body_resolves(self, css):
        val = _find_css_var(css, "--font-family-body")
        assert val and "-apple-system" in val

    def test_space_inset_md_resolves(self, css):
        # semantic: space.inset-md = {space.8} = 16px
        val = _find_css_var(css, "--space-inset-md")
        assert val == "16px", f"Expected 16px, got {val!r}"

    def test_font_shorthand_body_not_emitted(self, css):
        # 'body', 'label', 'caption', 'heading-*', 'code' are doc hints — skip
        assert "--font-body:" not in css
        assert "--font-label:" not in css
        assert "--font-heading-1:" not in css
        assert "--font-code:" not in css

    def test_font_size_md_emitted(self, css):
        val = _find_css_var(css, "--font-size-md")
        assert val == "14px", f"Expected 14px, got {val!r}"

    def test_shadow_focus_ring_emitted_without_extra_quotes(self, css):
        val = _find_css_var(css, "--shadow-focus-ring")
        assert val and "rgba" in val
        # Must not have leading/trailing extra quotes
        assert not val.startswith('"') and not val.startswith("'")

    def test_zindex_dropdown_emitted(self, css):
        val = _find_css_var(css, "--zindex-dropdown")
        assert val == "100"


# ---------------------------------------------------------------------------
# Persona overrides
# ---------------------------------------------------------------------------

class TestPersonaOverrides:
    def test_ceo_persona_block_present(self, css):
        assert '[data-persona="ceo"]' in css

    def test_it_persona_block_present(self, css):
        assert '[data-persona="it"]' in css

    def test_ceo_space_inset_md_overrides_semantic(self, css):
        # ceo.json overrides space.inset-md to 20px
        # Find the value INSIDE the [data-persona="ceo"] block
        ceo_block_m = re.search(
            r'\[data-persona="ceo"\]\s*\{([^}]+)\}', css, re.DOTALL
        )
        assert ceo_block_m, "CEO persona block not found"
        block = ceo_block_m.group(1)
        val = _find_css_var(block, "--space-inset-md")
        assert val == "20px", f"CEO space-inset-md expected 20px, got {val!r}"

    def test_it_persona_space_inset_md_overrides_to_6px(self, css):
        it_block_m = re.search(
            r'\[data-persona="it"\]\s*\{([^}]+)\}', css, re.DOTALL
        )
        assert it_block_m, "IT persona block not found"
        block = it_block_m.group(1)
        val = _find_css_var(block, "--space-inset-md")
        assert val == "6px", f"IT space-inset-md expected 6px, got {val!r}"

    def test_ceo_border_input_resolves_to_gray_300(self, css):
        # ceo.json: color.border-input = {color.gray.300} = #D1D5DB
        ceo_block_m = re.search(
            r'\[data-persona="ceo"\]\s*\{([^}]+)\}', css, re.DOTALL
        )
        assert ceo_block_m
        block = ceo_block_m.group(1)
        val = _find_css_var(block, "--color-border-input")
        assert val == "#D1D5DB", f"CEO border-input expected #D1D5DB, got {val!r}"

    def test_border_input_note_key_not_emitted(self, css):
        # _border-input-note is a doc key, must be stripped
        assert "--color--border-input-note" not in css
        assert "border-input-note" not in css


# ---------------------------------------------------------------------------
# Strip rules
# ---------------------------------------------------------------------------

class TestStripRules:
    def test_meta_stripped_everywhere(self, css):
        assert "--raw--meta" not in css and "--_meta" not in css

    def test_density_stripped(self, css):
        assert "_density" not in css

    def test_note_stripped(self, css):
        assert "--raw-color-accent-note" not in css


# ---------------------------------------------------------------------------
# Reference resolver unit tests
# ---------------------------------------------------------------------------

class TestRefResolver:
    def test_plain_value_passthrough(self):
        raw = {"color": {"gray": {"900": "#111827"}}}
        assert _resolve_ref("#FFFFFF", raw) == "#FFFFFF"

    def test_dotted_ref_resolves(self):
        raw = {"color": {"accent": {"600": "#2563EB"}}}
        assert _resolve_ref("{color.accent.600}", raw) == "#2563EB"

    def test_missing_ref_raises(self):
        raw = {}
        with pytest.raises(ValueError, match="Unresolvable"):
            _resolve_ref("{color.missing.key}", raw)


# ---------------------------------------------------------------------------
# app.css consumption check (no raw hex values)
# ---------------------------------------------------------------------------

class TestAppCssTokenConsumption:
    def test_app_css_contains_no_raw_hex(self):
        """
        app.css must not reference raw hex color values directly.
        Every color must come through var(--*) token.
        """
        app_css_path = _ADAPTER_ROOT / "static" / "css" / "app.css"
        if not app_css_path.exists():
            pytest.skip("app.css not present yet")

        source = app_css_path.read_text(encoding="utf-8")
        # Strip comments first
        source_no_comments = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)

        hex_pattern = re.compile(r'(?<!var\()#[0-9A-Fa-f]{3,8}\b')
        violations = []
        for lineno, line in enumerate(source_no_comments.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("/*") or stripped.startswith("*"):
                continue
            for m in hex_pattern.finditer(line):
                violations.append(f"Line {lineno}: {line.strip()}")

        assert not violations, (
            "app.css references raw hex values (must use var(--*) tokens):\n"
            + "\n".join(violations[:10])
        )
