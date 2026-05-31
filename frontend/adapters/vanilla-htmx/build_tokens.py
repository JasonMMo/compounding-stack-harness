"""
build_tokens.py — One-shot CSS token build step.

Usage:
    python build_tokens.py

Reads design/tokens/ (located by walking upward from this file),
generates static/css/tokens.css via token_css_generator.py.

This is the L3 "build" step for the frontend adapter.
"""

import logging
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# Ensure the adapter package is importable when run from any cwd
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from token_css_generator import generate

out_path = pathlib.Path(__file__).parent / "static" / "css" / "tokens.css"
out_path.parent.mkdir(parents=True, exist_ok=True)

css = generate()
out_path.write_text(css, encoding="utf-8")

lines = css.count("\n")
props = css.count("--")
print(f"OK  {out_path}  ({lines} lines, {props} CSS custom properties)")
