#!/usr/bin/env python3
"""Design-Cloud Bridge — 정규화 게이트 (WP-1 스켈레톤).

claude.ai/design 에서 `/design-sync` 로 내려온 staging 컴포넌트를 읽어, craft 결정을
**DTCG 토큰 override + site-section variant 명세**로 추출한다 (axis-8 복리 환류).

설계: docs/architecture/design-cloud-bridge.md §3 (B 정규화 게이트, 비협상)
       docs/architecture/design-cloud-bridge-execution-plan.md (WP-1)

이 스켈레톤이 하는 것 (WP-1):
  · staging/design-sync/<component>/ 의 HTML/CSS 에서 후보 색/타이포/간격을 추출
  · 추출 결과를 사람이 읽는 정규화 리포트로 출력 (no-op transform)

아직 TODO (WP-2/WP-4):
  · 후보 색 → semantic.json 키 매핑 (CDO 검수)
  · theme.yaml override / catalog variants 자동 생성
  · DTCG 스키마 검증 (scripts/design/dtcg_schema.py 연동)

규약: 이 스크립트의 출력(제안)은 **CDO(design-agent) 검수 후에만** repo 에 반영한다.
      컴포넌트 HTML 을 production 경로에 직접 커밋하지 않는다 (G-정규화게이트 가드가 차단).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 추출 정규식 (후보 토큰 발견용 — 매핑은 CDO 검수)
_HEX = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
_FONT = re.compile(r"font-family\s*:\s*([^;{}]+)", re.IGNORECASE)
_SPACING = re.compile(r"\b(\d+(?:\.\d+)?)(px|rem|em)\b")


def _read_component(component_dir: Path) -> str:
    """staging 컴포넌트 디렉터리의 모든 html/css 텍스트를 합쳐 반환."""
    if not component_dir.is_dir():
        raise FileNotFoundError(f"component dir not found: {component_dir}")
    chunks: list[str] = []
    for path in sorted(component_dir.rglob("*")):
        if path.suffix.lower() in {".html", ".css", ".htm"} and path.is_file():
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


def extract_candidates(text: str) -> dict:
    """craft 결정의 후보를 추출 (정규화 입력). 매핑/검증은 후속 WP."""
    colors = sorted({m.group(0).lower() for m in _HEX.finditer(text)})
    fonts = sorted({m.group(1).strip() for m in _FONT.finditer(text)})
    spacings = sorted({f"{m.group(1)}{m.group(2)}" for m in _SPACING.finditer(text)})
    return {"colors": colors, "fonts": fonts, "spacings": spacings}


def render_report(name: str, candidates: dict) -> str:
    lines = [
        f"# 정규화 리포트 (WP-1 skeleton) — {name}",
        "",
        "> CDO 검수용 후보 추출. 토큰 매핑/variant 생성은 후속 WP (TODO).",
        "",
        f"## 후보 색 ({len(candidates['colors'])})",
        *(f"- `{c}`  → semantic 키 매핑 TODO" for c in candidates["colors"]),
        "",
        f"## 후보 타이포 ({len(candidates['fonts'])})",
        *(f"- `{f}`" for f in candidates["fonts"]),
        "",
        f"## 후보 간격 ({len(candidates['spacings'])})",
        *(f"- `{s}`" for s in candidates["spacings"]),
        "",
        "## 다음 단계 (TODO)",
        "- [ ] 후보 색 → design/tokens/semantic.json 키 매핑 (CDO)",
        "- [ ] theme.yaml override 초안 생성 (override-only)",
        "- [ ] presets/site-sections/catalog.yaml variants 항목 추가",
        "- [ ] DTCG 스키마 검증 (dtcg_schema.py) 통과",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    # Windows 콘솔(cp949)에서 비-ASCII 출력 깨짐 방지 — G-8 정신(ASCII slug)과 별개로
    # 리포트 본문은 한글을 담으므로 stdout 을 utf-8 로 재설정.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "component",
        help="staging 컴포넌트 디렉터리 (예: staging/design-sync/hero-glow)",
    )
    args = parser.parse_args(argv)

    component_dir = Path(args.component)
    try:
        text = _read_component(component_dir)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    candidates = extract_candidates(text)
    print(render_report(component_dir.name, candidates))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
