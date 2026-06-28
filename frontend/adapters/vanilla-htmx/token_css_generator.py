"""
token_css_generator.py — Design token JSON → CSS custom properties generator.

Implements the generator contract from design/tokens/README.md:

  1. raw.json    → :root block with --raw-<path> variables
  2. semantic.json → :root block with --<semantic-key> variables
                    (resolves {dot.path} references against raw.json)
  3. persona/*.json → [data-persona="<name>"] scoped override blocks
                     (only the keys declared in each persona file)

Strip rules (README §5): _meta, _density, note keys are never emitted.

Font shorthand rule (README §4): font.body / font.heading-* / font.label /
font.caption / font.code are documentation hints — skipped in CSS output.
Only the component-part keys (font.size-*, font.line-*, font.weight-*,
font.family-*) are emitted.

Key naming (README §"Key naming"):
  raw:      dots → hyphens, prefixed --raw-
  semantic: dots → hyphens, no prefix

This module is called by build_tokens.py (one-shot) and can also be imported
by the server for cache-busting rebuilds.
"""

import json
import re
import pathlib
import logging
from typing import Any

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Keys stripped at any nesting level — not emitted as CSS variables
_STRIP_KEYS = {"_meta", "_density", "note"}

# Semantic font shorthand keys — documentation hints, skip in CSS output
_FONT_SHORTHAND_KEYS = {
    "body", "label", "caption", "heading-1", "heading-2", "heading-3", "code"
}

# Reference pattern: {some.dotted.path}
_REF_RE = re.compile(r"^\{([^}]+)\}$")

# ---------------------------------------------------------------------------
# Pico CSS v2 override map
# Maps --pico-* variables to our semantic CSS custom properties so that
# Pico's classless styles (applied to bare <button>, <table>, <input>, etc.)
# inherit our design language instead of Pico's default palette.
# Load order: Open Props → Pico classless → tokens.css → app.css
# This block is injected into tokens.css at build time so it survives every
# token rebuild without manual editing.
# ---------------------------------------------------------------------------

_PICO_OVERRIDES = """\
  /* Typography */
  --pico-font-family: var(--font-family-body);
  --pico-font-family-sans-serif: var(--font-family-body);
  --pico-font-family-monospace: var(--font-family-mono);
  --pico-font-size: 87.5%;
  --pico-line-height: 1.5;
  --pico-font-weight: var(--font-weight-body);

  /* Colors — surface & text */
  --pico-background-color: var(--color-surface-2);
  --pico-color: var(--color-text-1);
  --pico-muted-color: var(--color-text-3);
  --pico-muted-border-color: var(--color-border);

  /* Primary action color */
  --pico-primary: var(--color-primary);
  --pico-primary-background: var(--color-primary);
  --pico-primary-border: var(--color-primary);
  --pico-primary-hover: var(--color-primary-hover);
  --pico-primary-hover-background: var(--color-primary-hover);
  --pico-primary-hover-border: var(--color-primary-hover);
  --pico-primary-focus: var(--color-border-focus);
  --pico-primary-inverse: var(--color-text-on-primary);
  --pico-primary-underline: transparent;
  --pico-primary-hover-underline: transparent;

  /* Secondary (maps to our ghost/secondary tier) */
  --pico-secondary: var(--color-text-2);
  --pico-secondary-background: var(--color-surface-1);
  --pico-secondary-border: var(--color-border-strong);
  --pico-secondary-hover: var(--color-text-1);
  --pico-secondary-hover-background: var(--color-surface-2);
  --pico-secondary-hover-border: var(--color-border-strong);
  --pico-secondary-focus: var(--color-border-focus);
  --pico-secondary-inverse: var(--color-text-1);
  --pico-secondary-underline: transparent;
  --pico-secondary-hover-underline: transparent;

  /* Borders & radius */
  --pico-border-color: var(--color-border);
  --pico-border-radius: var(--radius-control);
  --pico-border-width: 1px;
  --pico-outline-width: 2px;

  /* Card */
  --pico-card-background-color: var(--color-surface-1);
  --pico-card-border-color: var(--color-border);
  --pico-card-box-shadow: var(--shadow-card);
  --pico-card-sectioning-background-color: var(--color-surface-2);

  /* Form elements */
  --pico-form-element-background-color: var(--color-surface-1);
  --pico-form-element-border-color: var(--color-border-input);
  --pico-form-element-color: var(--color-text-1);
  --pico-form-element-active-background-color: var(--color-surface-1);
  --pico-form-element-active-border-color: var(--color-border-focus);
  --pico-form-element-focus-color: var(--color-border-focus);
  --pico-form-element-placeholder-color: var(--color-text-3);
  --pico-form-element-invalid-border-color: var(--color-danger);
  --pico-form-element-invalid-active-border-color: var(--color-danger-hover);
  --pico-form-element-invalid-focus-color: var(--color-danger);
  --pico-form-element-valid-border-color: var(--color-success);
  --pico-form-element-valid-active-border-color: var(--color-success);
  --pico-form-element-valid-focus-color: var(--color-success);
  --pico-form-label-font-weight: var(--font-weight-label);

  /* Table */
  --pico-table-border-color: var(--color-border);
  --pico-table-row-stripped-background-color: var(--color-surface-2);

  /* Spacing — keep compact to match our density tokens */
  --pico-spacing: 1rem;
  --pico-block-spacing-vertical: 0.75rem;
  --pico-block-spacing-horizontal: 1rem;
  --pico-form-element-spacing-vertical: 4px;
  --pico-form-element-spacing-horizontal: 12px;

  /* Box shadow */
  --pico-box-shadow: var(--shadow-card);
  --pico-button-box-shadow: var(--shadow-xs);
  --pico-button-hover-box-shadow: var(--shadow-sm);

  /* Transition — control micro-interaction: 150ms standard (구 transition-control 보존) */
  --pico-transition: var(--motion-duration-fast) var(--motion-ease-standard);

  /* Nav */
  --pico-nav-element-spacing-horizontal: var(--space-inset-md);
  --pico-nav-element-spacing-vertical: var(--space-inset-sm);
  --pico-nav-link-spacing-horizontal: var(--space-inset-sm);
  --pico-nav-link-spacing-vertical: var(--space-inset-xs);

  /* Modal overlay */
  --pico-modal-overlay-background-color: var(--color-surface-overlay);

  /* Code */
  --pico-code-background-color: var(--color-surface-3);
  --pico-code-color: var(--color-text-2);\
"""


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _tokens_dir() -> pathlib.Path:
    """Locate design/tokens/ by walking upward from this file."""
    here = pathlib.Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        guess = candidate / "design" / "tokens"
        if guess.is_dir():
            return guess
    raise FileNotFoundError(
        "Cannot locate design/tokens/. Run from within the repo or set cwd appropriately."
    )


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Raw value resolution
# ---------------------------------------------------------------------------

def _get_nested(obj: Any, dotted_path: str) -> Any:
    """Traverse a nested dict using a dotted path string."""
    parts = dotted_path.split(".")
    current = obj
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _resolve_ref(value: str, raw: dict[str, Any]) -> str:
    """
    If value matches {dotted.path}, resolve it against raw.json.
    Otherwise return value unchanged.
    Raises ValueError if the reference cannot be resolved.
    """
    m = _REF_RE.match(value)
    if not m:
        return value
    path = m.group(1)
    resolved = _get_nested(raw, path)
    if resolved is None:
        raise ValueError(f"Unresolvable token reference: {{{path}}}")
    # Resolved value should be a primitive string/number
    return str(resolved)


# ---------------------------------------------------------------------------
# CSS property name construction
# ---------------------------------------------------------------------------

def _raw_css_name(path_parts: list[str]) -> str:
    """
    Construct a --raw-* CSS property name from path parts.
    Dots → hyphens, underscores in keys → hyphens.
    """
    joined = "-".join(p.replace("_", "-") for p in path_parts)
    return f"--raw-{joined}"


def _semantic_css_name(path_parts: list[str]) -> str:
    """
    Construct a semantic CSS property name from path parts.
    Dots → hyphens, underscores → hyphens, no prefix.
    """
    joined = "-".join(p.replace("_", "-") for p in path_parts)
    return f"--{joined}"


# ---------------------------------------------------------------------------
# Flattening walkers
# ---------------------------------------------------------------------------

def _flatten_raw(obj: Any, path: list[str], output: list[tuple[str, str]]) -> None:
    """
    Recursively flatten raw.json into (css_var_name, value) pairs.
    Skips _STRIP_KEYS and non-leaf nodes.
    """
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in _STRIP_KEYS:
                continue
            _flatten_raw(val, path + [key], output)
    elif isinstance(obj, (str, int, float)):
        css_name = _raw_css_name(path)
        output.append((css_name, str(obj)))
    # Lists and other types are skipped (no raw list values in this schema)


def _flatten_semantic(
    obj: Any,
    path: list[str],
    raw: dict[str, Any],
    output: list[tuple[str, str]],
    is_font_section: bool = False,
) -> None:
    """
    Recursively flatten semantic.json into (css_var_name, resolved_value) pairs.
    - Resolves {ref} syntax against raw.json.
    - Skips _STRIP_KEYS.
    - Skips font shorthand keys when inside the 'font' section.
    """
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in _STRIP_KEYS:
                continue
            in_font = is_font_section or (len(path) == 0 and key == "font") or (len(path) == 1 and path[0] == "font")
            # Skip font shorthand documentation keys
            if is_font_section and key in _FONT_SHORTHAND_KEYS:
                continue
            _flatten_semantic(val, path + [key], raw, output, is_font_section=in_font)
    elif isinstance(obj, (str, int, float)):
        val_str = str(obj)
        try:
            resolved = _resolve_ref(val_str, raw)
        except ValueError as exc:
            log.warning("token_css_generator: %s — emitting raw value", exc)
            resolved = val_str
        css_name = _semantic_css_name(path)
        output.append((css_name, resolved))


def _flatten_persona(
    obj: Any,
    path: list[str],
    raw: dict[str, Any],
    output: list[tuple[str, str]],
    is_font_section: bool = False,
) -> None:
    """
    Same as _flatten_semantic but for persona override files.
    Keys starting with _ are stripped (e.g. _border-input-note).
    """
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in _STRIP_KEYS or key.startswith("_"):
                continue
            in_font = is_font_section or (len(path) == 0 and key == "font") or (len(path) == 1 and path[0] == "font")
            if is_font_section and key in _FONT_SHORTHAND_KEYS:
                continue
            _flatten_persona(val, path + [key], raw, output, is_font_section=in_font)
    elif isinstance(obj, (str, int, float)):
        val_str = str(obj)
        try:
            resolved = _resolve_ref(val_str, raw)
        except ValueError as exc:
            log.warning("token_css_generator (persona): %s — emitting raw value", exc)
            resolved = val_str
        css_name = _semantic_css_name(path)
        output.append((css_name, resolved))


# ---------------------------------------------------------------------------
# CSS block builders
# ---------------------------------------------------------------------------

def _vars_block(pairs: list[tuple[str, str]], indent: str = "  ") -> str:
    lines = [f"{indent}{name}: {value};" for name, value in pairs]
    return "\n".join(lines)


def generate(tokens_dir: pathlib.Path | None = None, ui_theme: str = "saas") -> str:
    """
    Generate the full tokens.css content string.

    Merge order: raw → semantic → persona (each persona scoped).
    Returns a single CSS string ready to write to static/css/tokens.css.

    ui_theme: "saas" (default) — includes Pico CSS v2 overrides.
              "public-sector"  — skips Pico overrides; KRDS CDN covers base styles.
    """
    if tokens_dir is None:
        tokens_dir = _tokens_dir()

    raw = _load_json(tokens_dir / "raw.json")
    semantic = _load_json(tokens_dir / "semantic.json")

    sections: list[str] = [
        "/* Auto-generated by token_css_generator.py — DO NOT EDIT MANUALLY */",
        f"/* Source: design/tokens/raw.json + semantic.json + persona/*.json | ui_theme={ui_theme} */",
        "",
    ]
    if ui_theme == "public-sector":
        sections += [
            "/* ui_theme=public-sector: Pico overrides skipped. KRDS CDN covers base styles. */",
            "/* CDN required in base.html: */",
            "/*   <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/krds-uiux@1.1.0/resources/cdn/krds.min.css\"> */",
            "/*   <script src=\"https://cdn.jsdelivr.net/npm/krds-uiux@1.1.0/resources/cdn/krds.min.js\"></script> */",
            "",
        ]

    # ── 1. Raw layer → :root --raw-* variables ───────────────────────────────
    raw_pairs: list[tuple[str, str]] = []
    _flatten_raw(raw, [], raw_pairs)

    sections.append("/* ── Raw token layer ── */")
    sections.append(":root {")
    sections.append(_vars_block(raw_pairs))
    sections.append("}")
    sections.append("")

    # ── 2. Semantic layer → :root --* variables ──────────────────────────────
    sem_pairs: list[tuple[str, str]] = []
    _flatten_semantic(semantic, [], raw, sem_pairs)

    sections.append("/* ── Semantic token layer ── */")
    sections.append(":root {")
    sections.append(_vars_block(sem_pairs))
    sections.append("}")
    sections.append("")

    # ── 3. Persona overrides → [data-persona="<name>"] scoped blocks ─────────
    persona_dir = tokens_dir / "persona"
    if persona_dir.is_dir():
        for persona_file in sorted(persona_dir.glob("*.json")):
            persona_name = persona_file.stem  # e.g. "ceo", "ops", "it"
            persona_data = _load_json(persona_file)

            persona_pairs: list[tuple[str, str]] = []
            _flatten_persona(persona_data, [], raw, persona_pairs)

            if not persona_pairs:
                continue  # ops has no overrideable keys (it IS the baseline)

            sections.append(f'/* ── Persona: {persona_name} ── */')
            sections.append(f'[data-persona="{persona_name}"] {{')
            sections.append(_vars_block(persona_pairs))
            sections.append("}")
            sections.append("")

    # ── 4. Pico CSS v2 override layer (saas only) ────────────────────────────
    # Skipped for public-sector: KRDS CDN replaces Pico as the base style layer.
    if ui_theme != "public-sector":
        sections.append("/* ── Pico CSS v2 override — map --pico-* to our semantic tokens ── */")
        sections.append(":root {")
        sections.append(_PICO_OVERRIDES)
        sections.append("}")
        sections.append("")

        # ── 5. Pico regression fixes ──────────────────────────────────────────
        sections.append("/* ── Pico regression fix — button width ── */")
        sections.append("button.btn {")
        sections.append("  width: auto;")
        sections.append("}")
        sections.append("")
        sections.append("/* Login card: restore full-width submit inside .login-card */")
        sections.append(".login-card button.btn[type=submit] {")
        sections.append("  width: 100%;")
        sections.append("}")
        sections.append("")

    # ── 6. prefers-reduced-motion: override all --motion-duration-* to near-zero
    # WCAG 2.3.3 / KWCAG — easing kept intact, only duration collapsed.
    # Derived from sem_pairs so new tokens are covered automatically (no hardcoding).
    duration_names = sorted(
        name for name, _ in sem_pairs if name.startswith("--motion-duration-")
    )
    sections.append("/* ── a11y: prefers-reduced-motion override (WCAG 2.3.3 / KWCAG) ── */")
    sections.append("@media (prefers-reduced-motion: reduce) {")
    sections.append("  :root {")
    for name in duration_names:
        sections.append(f"    {name}: 0.01ms;")
    sections.append("  }")
    sections.append("}")
    sections.append("")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# CLI entry point (called by build_tokens.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui-theme", dest="ui_theme", default="saas",
                        choices=["saas", "public-sector"])
    args = parser.parse_args()
    out_path = pathlib.Path(__file__).parent / "static" / "css" / "tokens.css"
    css = generate(ui_theme=args.ui_theme)
    out_path.write_text(css, encoding="utf-8")
    print(f"Generated {out_path} ({len(css)} bytes, {css.count(chr(10))} lines) [ui_theme={args.ui_theme}]")
