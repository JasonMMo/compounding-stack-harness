"""
knowledge_sync.py -- PostToolUse hook (Growth-21)

Watches Write/Edit tool calls for knowledge-related file changes.
On match: emits additionalContext JSON to stdout instructing the model
to review and update related skill files.
On no-match or any error: exits 0 silently (stderr log only).

stdin: Claude hook JSON {"tool_name": "Write|Edit", "tool_input": {"file_path": "..."}}
stdout: hook response JSON (only on match)
"""

import json
import sys
import pathlib

# ---------------------------------------------------------------------------
# Repo root (resolved relative to this file, cwd-independent)
# ---------------------------------------------------------------------------
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Watch rules: (glob_prefix_parts, matched_skills)
# glob_prefix_parts: tuple of Path parts that the changed file must start with
#   relative to _REPO_ROOT (normalised to forward-slash for comparison).
# ---------------------------------------------------------------------------
_WATCH_RULES = [
    # knowledge/wiki/**/*.md -> all role loops + pm-delivery-loop
    (
        ("knowledge", "wiki"),
        [
            "engineer-loop",
            "qa-loop",
            "pm-delivery-loop",
            "domain-expert-loop",
            "cto-loop",
        ],
    ),
    # knowledge/raw/** -> pm-delivery-loop
    (
        ("knowledge", "raw"),
        ["pm-delivery-loop"],
    ),
    # presets/skills/** -> domain-expert-loop
    (
        ("presets", "skills"),
        ["domain-expert-loop"],
    ),
    # presets/ddl/** -> domain-expert-loop, engineer-loop
    (
        ("presets", "ddl"),
        ["domain-expert-loop", "engineer-loop"],
    ),
    # profiles/*.yaml -> pm-delivery-loop, domain-expert-loop
    (
        ("profiles",),
        ["pm-delivery-loop", "domain-expert-loop"],
    ),
]


def _rel_parts(file_path_str: str):
    """
    Normalise an absolute or repo-relative path to a tuple of Path parts
    relative to _REPO_ROOT.  Returns None if the path is outside the repo.
    """
    try:
        p = pathlib.Path(file_path_str)
        if not p.is_absolute():
            p = (_REPO_ROOT / p).resolve()
        else:
            p = p.resolve()
        return p.relative_to(_REPO_ROOT).parts
    except (ValueError, OSError):
        return None


def _match_rules(rel_parts_tuple):
    """Return list of skill names matched by the changed file, or []."""
    if rel_parts_tuple is None:
        return []
    matched = []
    seen = set()
    for prefix_parts, skills in _WATCH_RULES:
        if rel_parts_tuple[: len(prefix_parts)] == prefix_parts:
            for s in skills:
                if s not in seen:
                    matched.append(s)
                    seen.add(s)
    return matched


def _skill_paths(skill_names):
    """Return comma-separated skill file paths (repo-relative)."""
    return ", ".join(
        f".claude/skills/{name}/SKILL.md" for name in skill_names
    )


def _build_context(file_path_str: str, skill_names: list) -> str:
    skills_list = ", ".join(skill_names)
    skill_paths = _skill_paths(skill_names)
    # Determine if it's a wiki page (build_graph re-run hint)
    rel = pathlib.Path(file_path_str)
    is_wiki = False
    try:
        p = rel if rel.is_absolute() else (_REPO_ROOT / rel)
        p.resolve().relative_to(_REPO_ROOT / "knowledge" / "wiki")
        is_wiki = True
    except ValueError:
        pass

    wiki_hint = (
        " (4) python scripts/wiki/build_graph.py 재생성 (wiki 페이지 변경 시)"
        if is_wiki
        else ""
    )

    return (
        f"[knowledge-sync] {file_path_str} 변경됨. 점검: "
        f"(1) knowledge/wiki/index.md 1줄 갱신 여부 "
        f"(2) 신뢰도 라벨 (knowledge/wiki/README.md 규약) "
        f"(3) 연관 skill ({skills_list}) 의 절차·예시가 이 변경과 어긋나지 않는지 — "
        f"어긋나면 skill 파일 갱신이 이 작업의 일부다 (CLAUDE.md §7 환류 체크)"
        f"{wiki_hint}"
    )


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        data = json.loads(raw)
    except Exception as exc:
        print(f"[knowledge-sync] stdin parse error: {exc}", file=sys.stderr)
        sys.exit(0)

    try:
        tool_name = data.get("tool_name", "")
        if tool_name not in ("Write", "Edit"):
            sys.exit(0)

        tool_input = data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        rel_parts = _rel_parts(file_path)
        skill_names = _match_rules(rel_parts)

        if not skill_names:
            sys.exit(0)

        context_text = _build_context(file_path, skill_names)
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": context_text,
            }
        }
        sys.stdout.write(json.dumps(output, ensure_ascii=False))
        sys.stdout.flush()
        sys.exit(0)

    except Exception as exc:
        print(f"[knowledge-sync] unexpected error: {exc}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
