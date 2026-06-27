#!/usr/bin/env python3
"""Preflight — sibling 디자인 레포 전체를 cloud 연결 직전 누출 스캔.

claude.ai/design 에 `/design-sync` 로 연결하기 직전, 격리 sibling 레포
(harness-design-system) 트리 **전체**를 export_system.py 의 금지 패턴으로
훑어 단 1건이라도 매칭되면 abort(exit 1) 한다.

왜 main 레포에 두나:
  스캐너는 금지 패턴(실 고객명·인프라 URL 등)을 담는다. 이 목록을 cloud
  노출 레포(sibling)에 두면 그 자체가 누출이다. 따라서 게이트는 노출되지
  않는 main 레포에 두고, sibling 트리를 바깥에서 스캔한다.

Usage:
    python scripts/design/preflight_sibling.py [--target ../harness-design-system]

동작:
  1. export_system.FORBIDDEN_PATTERNS 재사용 (단일 진실, DRY).
  2. target 트리 전체를 워킹 — .git/.serena/node_modules/dist 등 제외,
     바이너리 확장자 제외.
  3. 텍스트 파일을 라인 단위로 스캔, 매칭 시 file:line:pattern 보고.
  4. 1건이라도 있으면 exit 1, 없으면 exit 0 + "CLEAN — 연결 안전".

설계: docs/architecture/design-cloud-bridge.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Windows 콘솔 utf-8 재설정 (export_system.py 패턴 동일)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 금지 패턴 단일 진실 재사용
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_system import FORBIDDEN_PATTERNS, _COMPILED  # noqa: E402

# 워킹 시 제외할 디렉터리 / 확장자
# skip: VCS·로컬 전용 sync 툴링(.ds-sync, 업로드 안 됨)·서드파티 프레임워크(_vendor,
# React 등 — 우리 콘텐츠 아님)·생성 빌드 메타. 우리가 authored/생성한 콘텐츠는 스캔.
_SKIP_DIRS = {".git", ".serena", "node_modules", "dist", "build", ".astro",
              "__pycache__", ".ds-sync", "_vendor", ".cache"}
_BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".pdf", ".zip", ".gz", ".tar", ".mp4", ".mov", ".webm",
}


def scan_tree(root: Path) -> list[tuple[str, int, str]]:
    """root 트리 전체 텍스트 파일을 스캔. 매칭 (rel_path, lineno, pattern) 목록 반환."""
    hits: list[tuple[str, int, str]] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in _BINARY_EXTS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # 바이너리/읽기불가 → 건너뜀
        rel = str(path.relative_to(root))
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern, compiled in zip(FORBIDDEN_PATTERNS, _COMPILED):
                if compiled.search(line):
                    hits.append((rel, lineno, pattern))
    return hits


def run_conformance(target_root: Path) -> list[str]:
    """G-21 shell conformance 를 sibling components/ 에 실행 (구조적 도메인-프리 1차 게이트).

    diagnose.g21_shell_conformance 재사용(DRY). 위반 메시지 목록 반환(빈=PASS).
    sibling components/ 부재 시 빈 리스트(SPEC).
    """
    scripts_dir = Path(__file__).resolve().parent.parent  # scripts/
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        import diagnose  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover
        return [f"diagnose.py import 실패 — conformance 미실행: {exc}"]
    result = diagnose.g21_shell_conformance(components_dir=target_root / "components")
    return list(result.violations)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preflight leak scan of the cloud-exposed sibling repo before /design-sync."
    )
    parser.add_argument(
        "--target",
        default="../harness-design-system",
        help="Sibling repo root (default: ../harness-design-system)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    target_root = (repo_root / args.target).resolve()

    print(f"[preflight] Target : {target_root}")
    print(f"[preflight] 패턴   : {len(FORBIDDEN_PATTERNS)}종 (export_system 단일 진실)")
    print()

    if not target_root.is_dir():
        print(f"[preflight] ERROR: target 디렉터리 없음: {target_root}", file=sys.stderr)
        sys.exit(1)

    hits = scan_tree(target_root)

    if hits:
        for rel, lineno, pattern in hits:
            print(f"  [LEAK] {rel}:{lineno}  ← 패턴 '{pattern}'", file=sys.stderr)
        print(file=sys.stderr)
        print(
            f"[preflight] ABORT: 누출 {len(hits)}건 — cloud 연결 금지. 위 라인 제거 후 재실행.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("[preflight] denylist CLEAN — 금지 패턴 0건 (2차 안전망).")

    # ── G-21 conformance (구조적 도메인-프리, 1차 게이트) ──────────────────
    conf = run_conformance(target_root)
    if conf:
        for v in conf:
            print(f"  [CONFORMANCE] {v}", file=sys.stderr)
        print(
            f"[preflight] ABORT: G-21 conformance {len(conf)}건 — 셸에 도메인 텍스트 잔존. "
            "{{슬롯}}/allowlist 로 옮긴 뒤 재실행.",
            file=sys.stderr,
        )
        sys.exit(1)
    print("[preflight] conformance CLEAN — 셸 0위반 (1차 게이트).")
    print("[preflight] CLEAN — /design-sync 연결 안전.")


if __name__ == "__main__":
    main()
