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


def generate(tokens_dir: pathlib.Path | None = None) -> str:
    """
    Generate the full tokens.css content string.

    Merge order: raw → semantic → persona (each persona scoped).
    Returns a single CSS string ready to write to static/css/tokens.css.
    """
    if tokens_dir is None:
        tokens_dir = _tokens_dir()

    raw = _load_json(tokens_dir / "raw.json")
    semantic = _load_json(tokens_dir / "semantic.json")

    sections: list[str] = [
        "/* Auto-generated by token_css_generator.py — DO NOT EDIT MANUALLY */",
        "/* Source: design/tokens/raw.json + semantic.json + persona/*.json */",
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

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# CLI entry point (called by build_tokens.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    out_path = pathlib.Path(__file__).parent / "static" / "css" / "tokens.css"
    css = generate()
    out_path.write_text(css, encoding="utf-8")
    print(f"Generated {out_path} ({len(css)} bytes, {css.count(chr(10))} lines)")
