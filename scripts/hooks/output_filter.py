"""
output_filter.py -- PreToolUse hook (Bash)

Wraps Bash commands with output filters before they run.
Claude sees only the filtered result — not the full raw output.

Rules:
  test    → stderr+stdout piped through grep FAIL|ERROR, head -100
  build   → stderr+stdout piped through grep Warning|Error, head -100
  git log → -n 10 injected (limits to 10 most-recent commits)
  verbose → head -300 (docker logs, kubectl logs, journalctl, etc.)

Skip conditions:
  - command already contains | grep / | head / | tail
  - git log already has -n N or -N flag
"""

import json
import re
import sys


# ---------------------------------------------------------------------------
# Detection regexes
# ---------------------------------------------------------------------------

_TEST_RE = re.compile(
    r"(?:^|[;&|])\s*"
    r"(?:pytest\b|python\s+-m\s+pytest\b|jest\b|npx\s+jest\b|"
    r"npm\s+(?:run\s+)?test\b|yarn\s+test\b|pnpm\s+(?:run\s+)?test\b|"
    r"go\s+test\b|cargo\s+test\b|mocha\b|vitest\b|dotnet\s+test\b)",
    re.IGNORECASE,
)

_BUILD_RE = re.compile(
    r"(?:^|[;&|])\s*"
    r"(?:mvn\b|gradlew?\b|"
    r"npm\s+run\s+(?:build|compile)\b|"
    r"yarn\s+(?:build|compile)\b|"
    r"pnpm\s+(?:run\s+)?(?:build|compile)\b|"
    r"cargo\s+build\b|go\s+build\b|"
    r"docker\s+build\b|tsc\b)",
    re.IGNORECASE,
)

_GIT_LOG_RE = re.compile(r"(?:^|[;&|])\s*git\s+log\b", re.IGNORECASE)

_VERBOSE_RE = re.compile(
    r"(?:^|[;&|])\s*"
    r"(?:docker\s+logs?\b|kubectl\s+logs?\b|journalctl\b|"
    r"cat\s+\S+\.log\b|tail\s+-f\b|dmesg\b)",
    re.IGNORECASE,
)

# Skip if already filtered downstream
_ALREADY_FILTERED = re.compile(r"\|\s*(?:grep|head|tail)\b")

# Skip if git log already limits count: -n N or -N
_GIT_LOG_HAS_LIMIT = re.compile(r"git\s+log\b.*?(?:-n\s*\d+|-\d+\b)")


# ---------------------------------------------------------------------------
# Wrappers
# ---------------------------------------------------------------------------

def _wrap_filter(cmd: str, pattern: str, label: str) -> str:
    """Capture stderr+stdout, grep for pattern, show first 100 lines."""
    escaped = pattern.replace('"', '\\"')
    return (
        f'tmpf=$(mktemp) && ({cmd}) > "$tmpf" 2>&1; _rc=$?; '
        f'grep -E "{escaped}" "$tmpf" | head -100; '
        f'echo "[filter:{label}] exit=$_rc"; '
        f'rm -f "$tmpf"'
    )


def _wrap_head(cmd: str, lines: int = 300) -> str:
    """Capture stderr+stdout, pass first N lines."""
    return (
        f'tmpf=$(mktemp) && ({cmd}) > "$tmpf" 2>&1; _rc=$?; '
        f'head -{lines} "$tmpf"; '
        f'echo "[filter:verbose] exit=$_rc, truncated to {lines} lines"; '
        f'rm -f "$tmpf"'
    )


def _inject_git_limit(cmd: str) -> str:
    return re.sub(r"(git\s+log\b)", r"\1 -n 10", cmd, count=1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    cmd: str = data.get("tool_input", {}).get("command", "")
    if not cmd:
        sys.exit(0)

    # Never double-filter
    if _ALREADY_FILTERED.search(cmd):
        sys.exit(0)

    modified: str | None = None

    if _GIT_LOG_RE.search(cmd) and not _GIT_LOG_HAS_LIMIT.search(cmd):
        modified = _inject_git_limit(cmd)

    elif _TEST_RE.search(cmd):
        pattern = r"FAIL|FAILED|ERROR|error:|E\s+\w|AssertionError|Exception|--- FAIL"
        modified = _wrap_filter(cmd, pattern, "test")

    elif _BUILD_RE.search(cmd):
        pattern = r"WARNING|WARN|ERROR|warning:|error:|\[WARNING\]|\[ERROR\]|\[WARN\]"
        modified = _wrap_filter(cmd, pattern, "build")

    elif _VERBOSE_RE.search(cmd):
        modified = _wrap_head(cmd, lines=300)

    if modified and modified != cmd:
        sys.stdout.write(json.dumps({"toolInput": {"command": modified}}, ensure_ascii=False))
        sys.stdout.flush()

    sys.exit(0)


if __name__ == "__main__":
    main()
