"""
large_file_guard.py — PreToolUse hook for the Read tool.

Blocks context-flooding reads by two criteria:
  DATA GUARD: files in `out/` segments or with data extensions (.log/.csv/.tsv/.jsonl)
              that exceed DATA_THRESHOLD_BYTES (10 KB).
  SIZE CAP  : any file exceeding SIZE_CAP_BYTES (100 KB), regardless of type.

EXEMPTION: raster image formats are rendered by Read as *bounded visual tokens*
(a 60 KB screenshot ≈ 90 tokens, capped by the vision pipeline regardless of byte
size), so the KB→context-flood premise does not apply. Blocking them would defeat
visual verification (e.g. headless-Chrome screenshot A/B — Growth-130 WP-4). They
pass both guards. SVG is excluded from the exemption (XML text, can flood as bytes).

Writes {"decision": "block", "reason": ...} to stdout on block; exits 0 silently on pass.
"""

import json
import os
import sys

DATA_THRESHOLD_BYTES = 10 * 1024   # 10 KB — data files above this flood context
SIZE_CAP_BYTES = 100 * 1024        # 100 KB — hard cap for all files (CLAUDE.md §8)
DATA_EXTS = {".log", ".csv", ".tsv", ".jsonl"}
# Raster images render as bounded visual tokens, not raw bytes — exempt from guards.
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}


def is_data_file(path: str) -> bool:
    norm = path.replace("\\", "/")
    ext = os.path.splitext(norm)[1].lower()
    if ext in DATA_EXTS:
        return True
    # "out" must be a full path segment, not a substring of a directory name
    parts = [p for p in norm.split("/") if p]
    return "out" in parts


def main() -> None:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    if payload.get("tool_name") != "Read":
        sys.exit(0)

    file_path: str = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    if not os.path.exists(file_path):
        # Let the Read tool surface its own "file not found" error
        sys.exit(0)

    # Raster images render as bounded visual tokens — exempt (see module docstring).
    if os.path.splitext(file_path.replace("\\", "/"))[1].lower() in IMAGE_EXTS:
        sys.exit(0)

    size = os.path.getsize(file_path)
    basename = os.path.basename(file_path)
    size_kb = size / 1024

    # DATA GUARD — checked first so reason message is specific
    if is_data_file(file_path) and size > DATA_THRESHOLD_BYTES:
        reason = (
            f"[large-file-guard] DATA FILE BLOCKED: {basename} "
            f"({size_kb:.1f}KB > {DATA_THRESHOLD_BYTES // 1024}KB). "
            "Use ctx_execute_file to analyze without flooding context."
        )
        sys.stdout.write(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
        sys.exit(0)

    # SIZE CAP — applies to every file type
    if size > SIZE_CAP_BYTES:
        reason = (
            f"[large-file-guard] LARGE FILE BLOCKED: {basename} "
            f"({size_kb:.1f}KB > {SIZE_CAP_BYTES // 1024}KB cap per CLAUDE.md §8). "
            "Use ctx_execute_file for analysis, or Read with explicit edit intent."
        )
        sys.stdout.write(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
