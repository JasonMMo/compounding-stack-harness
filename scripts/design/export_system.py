#!/usr/bin/env python3
"""Design System Export — main 레포 토큰 계층을 격리 sibling 레포로 sanitize export.

Usage:
    python scripts/design/export_system.py [--target ../harness-design-system]

실행 위치: compounding-stack-harness 루트.

동작:
  1. design/tokens/{raw.json, semantic.json, persona/*.json} 에 누출 가드 실행
  2. 가드 PASS 시 --target/tokens/ 로 복사 (멱등, 덮어쓰기)
  3. 복사 파일 수 + 가드 PASS 요약 출력

누출 가드: 토큰 파일 내용에 금지 패턴이 있으면 즉시 abort (exit code 1).
금지 패턴(대소문자 무시):
  legal, attorney, case_document, RLS, n9n.co.kr, 한빛테크, 미래솔루션,
  이준호, 박서연, profiles, .sql, DSN, password, secret, supabase

설계: docs/architecture/design-cloud-bridge.md
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Windows 콘솔 utf-8 재설정 (normalize.py 패턴 동일)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── 금지 패턴 (대소문자 무시) — 2차 안전망 (defense-in-depth) ────────────────
# 역할 재정의 (v2 WP-E): 이 denylist 는 더 이상 *1차* 누출 게이트가 아니다.
#   1차 = G-21 shell conformance (allowlist) — 셸 텍스트는 {{슬롯}}|chrome 만 허용.
#     allowlist 는 fail-safe(누락 시 BLOCK)라 미래 도메인 용어 누락 누출이 원천 불가능.
#   2차 = 이 denylist — conformance 통과분을 한 번 더 거르는 보강망. denylist 의 구조적
#     한계(개방형 집합 → 미래 용어 열거 불가, Growth-130 판례 사고)는 1차가 이미 차단하므로,
#     여기서는 "알려진 고위험 식별자 즉시 차단"의 보조 역할만 한다.
#   설계: docs/architecture/design-cloud-bridge-v2-structural.md §4.
FORBIDDEN_PATTERNS: list[str] = [
    r"legal",
    r"attorney",
    r"case_document",
    r"\bRLS\b",
    r"n9n\.co\.kr",
    r"한빛테크",
    r"미래솔루션",
    r"이준호",
    r"박서연",
    r"\bprofiles\b",
    r"\.sql",
    r"\bDSN\b",
    r"\bpassword\b",
    r"\bsecret\b",
    r"\bsupabase\b",
    # legal 버티컬 도메인 어휘 (Growth-130 sibling 누출 사고 환류 — 익명 셸이
    # 판례/대법원 용어를 잔존시켜 cloud 업로드된 사고. 이 목록은 main 레포(비노출)
    # 에만 존재하므로 실 용어를 담아도 안전.)
    r"판례",
    r"대법원",
    r"손해배상",
    r"피고",
    r"\bprecedent\b",
    r"\bcourt\b",
    r"\bplaintiff\b",
    r"\bdefendant\b",
    r"\blitigation\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in FORBIDDEN_PATTERNS]


def check_leakage(path: Path) -> list[tuple[str, str]]:
    """파일 내용을 스캔해 금지 패턴 매칭 목록 반환. 빈 리스트 = 클린."""
    text = path.read_text(encoding="utf-8", errors="replace")
    hits: list[tuple[str, str]] = []
    for pattern, compiled in zip(FORBIDDEN_PATTERNS, _COMPILED):
        if compiled.search(text):
            hits.append((pattern, str(path)))
    return hits


def collect_token_files(tokens_dir: Path) -> list[Path]:
    """export 대상 파일 목록: raw.json, semantic.json, persona/*.json."""
    files: list[Path] = []
    for name in ("raw.json", "semantic.json"):
        f = tokens_dir / name
        if f.exists():
            files.append(f)
    persona_dir = tokens_dir / "persona"
    if persona_dir.is_dir():
        files.extend(sorted(persona_dir.glob("*.json")))
    return files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export main repo design tokens to sibling repo (sanitized)."
    )
    parser.add_argument(
        "--target",
        default="../harness-design-system",
        help="Sibling repo root (default: ../harness-design-system)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    tokens_dir = repo_root / "design" / "tokens"
    target_root = (repo_root / args.target).resolve()
    target_tokens_dir = target_root / "tokens"

    print(f"[export_system] Source : {tokens_dir}")
    print(f"[export_system] Target : {target_tokens_dir}")
    print()

    # ── 1. 파일 수집 ──────────────────────────────────────────────────────
    files = collect_token_files(tokens_dir)
    if not files:
        print("[export_system] ERROR: 토큰 파일을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    # ── 2. 누출 가드 ──────────────────────────────────────────────────────
    print("[export_system] 누출 가드 실행 중...")
    all_hits: list[tuple[str, str, str]] = []  # (file, pattern, -)
    for f in files:
        hits = check_leakage(f)
        for pattern, path in hits:
            all_hits.append((path, pattern, ""))
            print(f"  [FAIL] {f.relative_to(repo_root)}: 금지 패턴 '{pattern}' 발견", file=sys.stderr)

    if all_hits:
        print(file=sys.stderr)
        print(f"[export_system] ABORT: 누출 가드 {len(all_hits)}건 FAIL — export 중단.", file=sys.stderr)
        sys.exit(1)

    print(f"[export_system] 가드 PASS — {len(files)}개 파일 모두 클린")
    print()

    # ── 3. 복사 (멱등, 덮어쓰기) ─────────────────────────────────────────
    if not target_root.exists():
        print(f"[export_system] ERROR: target 경로 없음: {target_root}", file=sys.stderr)
        print("  sibling 레포 스캐폴드를 먼저 생성하세요.", file=sys.stderr)
        sys.exit(1)

    copied = 0
    for src in files:
        # 상대 경로 유지: raw.json → tokens/raw.json, persona/ceo.json → tokens/persona/ceo.json
        rel = src.relative_to(tokens_dir)
        dst = target_tokens_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  [copy] {rel}  →  {dst.relative_to(target_root)}")
        copied += 1

    print()
    print(f"[export_system] 완료: {copied}개 파일 복사, 가드 PASS")


if __name__ == "__main__":
    main()
