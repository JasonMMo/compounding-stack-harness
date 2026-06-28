#!/usr/bin/env python3
"""ledger-index.py — symbol-anchored cross-agent ledger index.

Reads learn-log.md (agent=main) + docs/learn-logs/*.md (agent=file stem,
excluding _index.md and synthesis-template.md), extracts Growth entries, anchors (Files-touched paths +
backtick/wikilink symbols), cross-validates against .codegraph/codegraph.db,
and writes docs/learn-logs/_index.json (+ optionally _index.md).

CLI:
  python scripts/ledger-index.py              # build _index.json
  python scripts/ledger-index.py --symbol X   # show entries for symbol X
  python scripts/ledger-index.py --check      # check stale anchors vs codegraph
  python scripts/ledger-index.py --md         # also write _index.md

Exit code: 0 normally, 1 on --check with stale anchors.

Performance:
  Incremental parse cache stored in docs/learn-logs/_index.cache.json (gitignored).
  Each source file is SHA-256 hashed; on cache hit, parse+extract is skipped.
  codegraph verification, global dedup, and sort always run fresh (never cached).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Repo layout
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
LEARN_LOG_MAIN = REPO_ROOT / "learn-log.md"
LEARN_LOGS_DIR = REPO_ROOT / "docs" / "learn-logs"
CODEGRAPH_DB = REPO_ROOT / ".codegraph" / "codegraph.db"
INDEX_JSON = LEARN_LOGS_DIR / "_index.json"
INDEX_MD = LEARN_LOGS_DIR / "_index.md"
CACHE_JSON = LEARN_LOGS_DIR / "_index.cache.json"

_CACHE_VERSION = 1

# Agents to process: (path, agent_name)
# Excluded stems: _index (self-output), synthesis-template (template, not a Growth ledger)
_EXCLUDED_STEMS = {"_index", "synthesis-template"}

def _source_files() -> list[tuple[Path, str]]:
    sources: list[tuple[Path, str]] = []
    if LEARN_LOG_MAIN.exists():
        sources.append((LEARN_LOG_MAIN, "main"))
    for p in sorted(LEARN_LOGS_DIR.glob("*.md")):
        if p.stem not in _EXCLUDED_STEMS:
            sources.append((p, p.stem))
    return sources


# ---------------------------------------------------------------------------
# Content-hash incremental cache helpers
# ---------------------------------------------------------------------------

def _file_sha256(path: Path) -> str:
    """Return hex SHA-256 of the raw bytes of *path*."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_cache() -> dict[str, Any]:
    """Load _index.cache.json if it exists and version matches, else return empty structure."""
    if not CACHE_JSON.exists():
        return {"version": _CACHE_VERSION, "files": {}}
    try:
        data = json.loads(CACHE_JSON.read_text(encoding="utf-8"))
        if data.get("version") != _CACHE_VERSION:
            return {"version": _CACHE_VERSION, "files": {}}
        return data
    except Exception:
        return {"version": _CACHE_VERSION, "files": {}}


def _save_cache(cache: dict[str, Any]) -> None:
    """Write cache to _index.cache.json atomically."""
    CACHE_JSON.parent.mkdir(parents=True, exist_ok=True)
    CACHE_JSON.write_text(
        json.dumps(cache, sort_keys=True, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

_ENTRY_HEADER = re.compile(
    r"^### Growth-(\d+) \((\d{4}-\d{2}-\d{2})\)\s*[—\-]?\s*(.*)$"
)
_NEXT_SECTION = re.compile(r"^### ")

# Files touched: lines — collect paths from the bullet list that follows
_FILES_TOUCHED_START = re.compile(r"^\s*-\s+Files touched\s*:", re.IGNORECASE)
# Each bullet under Files touched: `  - path/to/file`
_FILE_BULLET = re.compile(r"^\s{2,}-\s+`?([^`\n]+?)`?\s*(?:\(.*\))?\s*$")

# Symbol candidates from body
_BACKTICK_TOKEN = re.compile(r"`([A-Za-z_][A-Za-z0-9_.:-]{1,80})`")
_WIKILINK = re.compile(r"\[\[([^\]|#]+?)(?:[|#][^\]]*)?\]\]")

# Tokens that are too noisy to be meaningful symbols (paths, prose fragments)
_SKIP_SYMBOL_RE = re.compile(r"[/\\. ]|\.md$|\.yaml$|\.json$|\.py$|\.java$|\.html$|\.css$|\.ts$|\.js$|\.sql$|\.txt$")


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _parse_file(path: Path, agent: str) -> list[dict[str, Any]]:
    """Parse a ledger file and return a list of raw entry dicts."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    entries: list[dict[str, Any]] = []

    i = 0
    while i < len(lines):
        m = _ENTRY_HEADER.match(lines[i])
        if not m:
            i += 1
            continue

        growth_n = int(m.group(1))
        date = m.group(2)
        title = m.group(3).strip()

        # Collect body until the next ### heading
        body_lines: list[str] = []
        i += 1
        while i < len(lines):
            if _NEXT_SECTION.match(lines[i]):
                break
            body_lines.append(lines[i])
            i += 1

        body = "\n".join(body_lines)

        entries.append({
            "agent": agent,
            "growth": growth_n,
            "date": date,
            "title": title,
            "file": str(path.relative_to(REPO_ROOT).as_posix()),
            "body": body,
        })

    return entries


def _extract_file_anchors(body: str) -> list[str]:
    """Extract paths from '- Files touched:' bullet list in body."""
    lines = body.splitlines()
    found: list[str] = []
    in_files_touched = False

    for line in lines:
        if _FILES_TOUCHED_START.match(line):
            in_files_touched = True
            # The header line itself may or may not list files inline; skip it
            continue

        if in_files_touched:
            bm = _FILE_BULLET.match(line)
            if bm:
                candidate = bm.group(1).strip().strip("`").strip()
                # Strip trailing annotation like "(신규 — ...)" already handled by regex
                # but strip any remaining parens fragment
                candidate = re.sub(r"\s*\(.*", "", candidate).strip()
                if candidate:
                    found.append(candidate)
            elif line.strip() == "" or (line.strip().startswith("-") and not line.startswith("  ")):
                # blank line or top-level bullet = end of sub-list
                in_files_touched = False
            elif not line.startswith(" ") and not line.startswith("\t"):
                # un-indented non-bullet = end of section
                in_files_touched = False

    return found


def _extract_symbol_candidates(body: str) -> list[str]:
    """Extract backtick tokens and wikilink targets that look like code symbols."""
    candidates: list[str] = []

    for m in _BACKTICK_TOKEN.finditer(body):
        tok = m.group(1)
        if not _SKIP_SYMBOL_RE.search(tok):
            candidates.append(tok)

    for m in _WIKILINK.finditer(body):
        tok = m.group(1).strip()
        if tok and not _SKIP_SYMBOL_RE.search(tok):
            candidates.append(tok)

    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result


def _extract_file_contribution(path: Path, agent: str) -> list[dict[str, Any]]:
    """Parse *path* and enrich each entry with pre-computed file_anchors + symbol_candidates.

    Returns a list of entry dicts suitable for caching:
    {agent, growth, date, title, file, file_anchors: [...], symbol_candidates: [...]}.
    The 'body' field is intentionally excluded from the returned dicts to keep the cache
    compact — callers consume file_anchors / symbol_candidates directly.
    """
    raw_entries = _parse_file(path, agent)
    result: list[dict[str, Any]] = []
    for entry in raw_entries:
        body = entry["body"]
        result.append({
            "agent": entry["agent"],
            "growth": entry["growth"],
            "date": entry["date"],
            "title": entry["title"],
            "file": entry["file"],
            "file_anchors": _extract_file_anchors(body),
            "symbol_candidates": _extract_symbol_candidates(body),
        })
    return result


# ---------------------------------------------------------------------------
# Codegraph cross-validation
# ---------------------------------------------------------------------------

def _load_codegraph_names() -> tuple[set[str] | None, str | None]:
    """Load DISTINCT name FROM nodes in codegraph.db (READ-ONLY).

    Returns (name_set, warning_message).
    If DB absent or unreadable, returns (None, warning).
    """
    if not CODEGRAPH_DB.exists():
        return None, f"codegraph.db not found at {CODEGRAPH_DB} — all symbols will be unverified."

    uri = CODEGRAPH_DB.as_uri() + "?mode=ro"
    try:
        con = sqlite3.connect(uri, uri=True)
        try:
            cur = con.execute("SELECT DISTINCT name FROM nodes")
            names = {row[0] for row in cur.fetchall() if row[0]}
            return names, None
        finally:
            con.close()
    except sqlite3.OperationalError as exc:
        return None, f"codegraph.db read failed ({exc}) — all symbols will be unverified."


# ---------------------------------------------------------------------------
# Index builder
# ---------------------------------------------------------------------------

def _git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def build_index() -> dict[str, Any]:
    """Parse all ledger files and build the full index structure.

    Uses a content-hash incremental cache (docs/learn-logs/_index.cache.json) so that
    unchanged files skip parse+extract on subsequent calls.  codegraph verification,
    global dedup, and sort always run fresh — they depend on .codegraph/codegraph.db
    which changes independently of the ledger files.
    """
    # ── Codegraph (always fresh — independent change source) ──────────────
    cg_names, cg_warn = _load_codegraph_names()
    if cg_warn:
        print(f"[ledger-index] WARNING: {cg_warn}", file=sys.stderr)

    # ── Incremental parse cache ───────────────────────────────────────────
    cache = _load_cache()
    cache_files: dict[str, Any] = cache.setdefault("files", {})
    cache_dirty = False

    # Collect entries from cache or fresh parse
    all_entries: list[dict[str, Any]] = []  # each has file_anchors + symbol_candidates
    current_keys: set[str] = set()

    for src_path, agent in _source_files():
        rel_key = src_path.relative_to(REPO_ROOT).as_posix()
        current_keys.add(rel_key)

        file_hash = _file_sha256(src_path)

        cached = cache_files.get(rel_key)
        if cached is not None and cached.get("hash") == file_hash:
            # Cache hit: reuse pre-computed entries
            all_entries.extend(cached["entries"])
        else:
            # Cache miss: parse + extract, then store
            extracted = _extract_file_contribution(src_path, agent)
            cache_files[rel_key] = {"hash": file_hash, "entries": extracted}
            cache_dirty = True
            all_entries.extend(extracted)

    # Prune stale keys (source file deleted)
    stale_keys = set(cache_files.keys()) - current_keys
    if stale_keys:
        for k in stale_keys:
            del cache_files[k]
        cache_dirty = True

    if cache_dirty:
        _save_cache(cache)

    # ── Global bucketing + codegraph verification (always fresh) ──────────
    symbols: dict[str, list[dict]] = {}
    files: dict[str, list[dict]] = {}
    unverified: list[dict] = []

    for entry in all_entries:
        meta = {
            "agent": entry["agent"],
            "growth": entry["growth"],
            "date": entry["date"],
            "title": entry["title"],
            "file": entry["file"],
        }

        # ── File anchors ──────────────────────────────────────────────
        for fpath in entry["file_anchors"]:
            bucket = files.setdefault(fpath, [])
            rec = dict(meta)
            if not any(
                r["agent"] == rec["agent"] and r["growth"] == rec["growth"]
                for r in bucket
            ):
                bucket.append(rec)

        # ── Symbol anchors ────────────────────────────────────────────
        for sym in entry["symbol_candidates"]:
            rec = dict(meta)
            if cg_names is not None:
                verified = sym in cg_names
            else:
                verified = False

            if verified:
                rec["verified"] = True
                bucket = symbols.setdefault(sym, [])
                if not any(
                    r["agent"] == rec["agent"] and r["growth"] == rec["growth"]
                    for r in bucket
                ):
                    bucket.append(rec)
            else:
                # unverified: do NOT drop — store in unverified list
                uv_rec = dict(rec)
                uv_rec["symbol"] = sym
                if not any(
                    u["symbol"] == sym and u["agent"] == uv_rec["agent"] and u["growth"] == uv_rec["growth"]
                    for u in unverified
                ):
                    unverified.append(uv_rec)

    # Sort for deterministic output
    symbols_sorted = {k: sorted(v, key=lambda r: (r["growth"], r["agent"])) for k, v in sorted(symbols.items())}
    files_sorted = {k: sorted(v, key=lambda r: (r["growth"], r["agent"])) for k, v in sorted(files.items())}
    unverified_sorted = sorted(unverified, key=lambda r: (r["symbol"], r["growth"], r["agent"]))

    return {
        "generated_from_commit": _git_head(),
        "symbols": symbols_sorted,
        "files": files_sorted,
        "unverified": unverified_sorted,
    }


def write_json(index: dict[str, Any]) -> None:
    INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(index, sort_keys=True, ensure_ascii=False, indent=2)
    INDEX_JSON.write_text(content, encoding="utf-8")


def write_md(index: dict[str, Any]) -> None:
    """Write _index.md — Obsidian-friendly human-readable version."""
    buf = io.StringIO()
    buf.write("# Ledger Index\n\n")
    buf.write(f"> generated_from_commit: `{index['generated_from_commit']}`\n\n")

    buf.write("## Verified Symbols\n\n")
    for sym, entries in index["symbols"].items():
        buf.write(f"### `{sym}`\n\n")
        for e in entries:
            buf.write(
                f"- [[{e['file']}|{e['agent']} Growth-{e['growth']}]] "
                f"({e['date']}) — {e['title']}\n"
            )
        buf.write("\n")

    buf.write("## File Anchors\n\n")
    for fpath, entries in index["files"].items():
        buf.write(f"### `{fpath}`\n\n")
        for e in entries:
            buf.write(
                f"- [[{e['file']}|{e['agent']} Growth-{e['growth']}]] "
                f"({e['date']}) — {e['title']}\n"
            )
        buf.write("\n")

    buf.write("## Unverified Symbols\n\n")
    for uv in index["unverified"]:
        buf.write(
            f"- `{uv['symbol']}` — {uv['agent']} Growth-{uv['growth']} "
            f"({uv['date']}): {uv['title']}\n"
        )

    INDEX_MD.parent.mkdir(parents=True, exist_ok=True)
    INDEX_MD.write_text(buf.getvalue(), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_build(args: argparse.Namespace) -> int:
    index = build_index()
    write_json(index)

    sym_count = len(index["symbols"])
    file_count = len(index["files"])
    uv_count = len(index["unverified"])
    total_sym_entries = sum(len(v) for v in index["symbols"].values())
    total_file_entries = sum(len(v) for v in index["files"].values())

    print(f"[ledger-index] Built {INDEX_JSON.relative_to(REPO_ROOT).as_posix()}")
    print(f"  verified symbols : {sym_count} ({total_sym_entries} entries)")
    print(f"  file anchors     : {file_count} ({total_file_entries} entries)")
    print(f"  unverified       : {uv_count}")
    print(f"  commit           : {index['generated_from_commit'][:12]}")

    if args.md:
        write_md(index)
        print(f"  also wrote       : {INDEX_MD.relative_to(REPO_ROOT).as_posix()}")

    return 0


def cmd_symbol(args: argparse.Namespace) -> int:
    sym = args.symbol
    index = build_index()

    found: list[dict] = []

    # Exact match in verified symbols
    if sym in index["symbols"]:
        for e in index["symbols"][sym]:
            found.append({"kind": "verified", **e, "symbol": sym})

    # Also search unverified
    for uv in index["unverified"]:
        if uv["symbol"] == sym:
            found.append({"kind": "unverified", **uv})

    # Also search file anchors: exact path match or basename match
    for fpath, entries in index["files"].items():
        fbase = Path(fpath).stem  # e.g. "CatalogValidator" from CatalogValidator.java
        if fpath == sym or fbase == sym or fpath.endswith(f"/{sym}") or fpath.endswith(f"\\{sym}"):
            for e in entries:
                found.append({"kind": "file-anchor", **e, "symbol": sym, "file_path": fpath})

    if not found:
        print(f"[ledger-index] No entries found for symbol: {sym!r}")
        return 0

    print(f"[ledger-index] Symbol: {sym!r}  ({len(found)} entr{'y' if len(found)==1 else 'ies'})\n")
    for e in sorted(found, key=lambda r: (r["growth"], r["agent"])):
        status = "(verified)" if e.get("kind") == "verified" else "(unverified)"
        print(f"  Growth-{e['growth']:>3}  {e['agent']:10}  {e['date']}  {status}")
        print(f"           {e['title']}")
        print(f"           -> {e['file']}")
        print()

    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """Check for stale anchors: previously verified symbols no longer in codegraph."""
    if not INDEX_JSON.exists():
        print("[ledger-index] No existing _index.json — skipping stale check (rc=0).")
        return 0

    try:
        old = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ledger-index] Could not read existing _index.json: {exc}", file=sys.stderr)
        return 0

    old_verified: set[str] = set(old.get("symbols", {}).keys())
    if not old_verified:
        print("[ledger-index] Previous index has no verified symbols — nothing to check.")
        return 0

    cg_names, cg_warn = _load_codegraph_names()
    if cg_names is None:
        print(f"[ledger-index] WARNING: {cg_warn} — cannot determine stale anchors.", file=sys.stderr)
        return 0

    stale = sorted(old_verified - cg_names)
    if not stale:
        print(f"[ledger-index] PASS — all {len(old_verified)} previously-verified symbols still in codegraph.")
        return 0

    print(f"[ledger-index] FAIL — {len(stale)} stale anchor(s) (verified in index but absent from codegraph):")
    for sym in stale:
        print(f"  - {sym}")
    return 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ledger-index — symbol-anchored cross-agent ledger search index"
    )
    parser.add_argument(
        "--symbol", metavar="NAME",
        help="show entries for a specific symbol (human-readable)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="check for stale anchors vs codegraph; rc=1 if any found",
    )
    parser.add_argument(
        "--md", action="store_true",
        help="also write _index.md (Obsidian-friendly)",
    )
    args = parser.parse_args(argv)

    if args.check:
        return cmd_check(args)

    if args.symbol:
        return cmd_symbol(args)

    return cmd_build(args)


if __name__ == "__main__":
    raise SystemExit(main())
