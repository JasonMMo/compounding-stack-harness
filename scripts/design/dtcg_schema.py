#!/usr/bin/env python3
"""Design-Cloud Bridge — DTCG 토큰 경계 검증 (WP-1 스켈레톤).

경계를 넘는 토큰 JSON 이 DTCG(W3C Community Group, v2025.10) 모양 + 우리 semantic 키
화이트리스트를 지키는지 검증한다. semantic 키의 단일 진실은 design/tokens/semantic.json
(하드코딩하지 않고 런타임 로드 — 복리/단일소스).

설계: docs/architecture/design-cloud-bridge.md §1 C5, §5 (DTCG 스키마 가드)
주의: DTCG 는 완전한 W3C Recommendation 이 아니다 — "표준 준수" 광고 금지.

WP-2 의 DTCG 스키마 가드(g16~)가 이 모듈의 validate_token_overrides() 를 호출한다.
"""
from __future__ import annotations

import json
from pathlib import Path

# REPO_ROOT: 이 파일은 <repo>/scripts/design/dtcg_schema.py
REPO_ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_JSON = REPO_ROOT / "design" / "tokens" / "semantic.json"


def _flatten_keys(obj: dict, prefix: str = "") -> set[str]:
    """중첩 토큰 트리를 'color.primary' 같은 dotted 키 집합으로."""
    keys: set[str] = set()
    for k, v in obj.items():
        if k.startswith("$"):  # DTCG 메타($type/$value/$description)는 키로 안 셈
            continue
        if not prefix and k == "_meta":  # 파일 메타(_meta.*)는 토큰 키 아님
            continue
        dotted = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and "$value" not in v:
            keys |= _flatten_keys(v, dotted)
        else:
            keys.add(dotted)
    return keys


def load_semantic_keys() -> set[str]:
    """semantic.json 의 허용 키 화이트리스트 (단일 진실)."""
    if not SEMANTIC_JSON.is_file():
        return set()
    data = json.loads(SEMANTIC_JSON.read_text(encoding="utf-8"))
    return _flatten_keys(data)


def validate_token_overrides(overrides: dict, *, allow_landing_extras: bool = True) -> list[str]:
    """override 토큰이 semantic 화이트리스트 안인지 검사. 위반 키 리스트 반환(빈 리스트=PASS).

    allow_landing_extras: theme-specific landing 전용 키(hero-bg-from 등)는 허용.
    """
    allowed = load_semantic_keys()
    if not allowed:
        return ["semantic.json not found — cannot validate (WP-1 skeleton)"]
    # landing 전용 추가 키 (theme-format.md 명시)
    landing_extras = {
        "color.hero-bg-from", "color.hero-bg-to",
        "color.section-alt-bg", "color.accent-glow",
    }
    candidate_keys = _flatten_keys(overrides)
    violations = []
    for key in sorted(candidate_keys):
        if key in allowed:
            continue
        if allow_landing_extras and key in landing_extras:
            continue
        violations.append(key)
    return violations


if __name__ == "__main__":
    keys = load_semantic_keys()
    print(f"semantic.json keys loaded: {len(keys)}")
    for k in sorted(keys):
        print(f"  {k}")
