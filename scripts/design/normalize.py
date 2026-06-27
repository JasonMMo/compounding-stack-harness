#!/usr/bin/env python3
"""Design-Cloud Bridge — 정규화 게이트 (WP-1 스켈레톤).

claude.ai/design 에서 `/design-sync` 로 내려온 staging 컴포넌트를 읽어, craft 결정을
**DTCG 토큰 override + site-section variant 명세**로 추출한다 (axis-8 복리 환류).

설계: docs/architecture/design-cloud-bridge.md §3 (B 정규화 게이트, 비협상)
       docs/architecture/design-cloud-bridge-execution-plan.md (WP-1)

이 스크립트가 하는 것:
  · staging/design-sync/<component>/ 의 HTML/CSS 에서 후보 색/타이포/간격을 추출 (WP-1)
  · **구조 추출 (v2 WP-D, 경계 확대)** — 셸이 구조적 도메인-프리(슬롯 템플릿)가 되어
    경계가 토큰JSON → 컴포넌트 구조까지 안전하게 넓어졌다. 이제 마크업에서
    `{{슬롯}}`(데이터 계약)과 BEM modifier(`block--variant`)를 추출해 site-section
    **variant 후보**로 분해하고 catalog.yaml 스캐폴드를 제안한다.
  · 추출 결과를 사람이 읽는 정규화 리포트로 출력 (no-op transform — 반영은 CDO 검수 후)

아직 TODO (후속):
  · 후보 색 → semantic.json 키 매핑 (CDO 검수)
  · theme.yaml override 자동 생성
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

# 구조 추출 (v2 WP-D — 경계 확대: 컴포넌트 구조를 variant 후보로 분해)
_SLOT = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")
# BEM modifier: block--modifier (CSS 선택자/class 속성 양쪽에서). 단일 '-'(BEM element
# 'block__el')은 제외, '--' 만 variant 로 본다.
_BEM_MODIFIER = re.compile(r"\b([a-z][a-z0-9]*(?:-[a-z0-9]+)*--[a-z0-9]+(?:-[a-z0-9]+)*)\b")


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


_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def _strip_comments(text: str) -> str:
    """HTML/CSS 주석 제거 — 주석 속 클래스 언급/마커 설명이 구조 추출을 오염시키는 것 방지.

    (예: 주석 `chip--match-count를 DOM에` 의 뒤따르는 한글이 BEM \\b 매칭을 깨 'chip--match'
     로 백트랙, 또 주석 속 '{{마커}}' 설명이 슬롯으로 오집계되는 문제를 동시 해소.)
    """
    return _CSS_COMMENT.sub(" ", _HTML_COMMENT.sub(" ", text))


def extract_structure(text: str) -> dict:
    """컴포넌트 구조를 추출 (v2 WP-D). slots=데이터 계약, variants=BEM modifier.

    셸이 슬롯 템플릿(구조적 도메인-프리)이라 마크업 자체가 안전하게 경계를 넘는다.
    slot 집합 = 이 컴포넌트의 데이터 인터페이스(=main 레포 manifest 가 채울 자리),
    BEM modifier 집합 = site-section catalog 의 variant 후보.
    """
    text = _strip_comments(text)
    slots = sorted({m.group(1) for m in _SLOT.finditer(text)})
    # block 별 modifier 묶기: 'result-card--reference' → block 'result-card', variant 'reference'
    variants: dict[str, list[str]] = {}
    for m in _BEM_MODIFIER.finditer(text):
        cls = m.group(1)
        block, _, modifier = cls.partition("--")
        variants.setdefault(block, [])
        if modifier not in variants[block]:
            variants[block].append(modifier)
    variants = {b: sorted(v) for b, v in sorted(variants.items())}
    return {"slots": slots, "variants": variants}


def _variant_scaffold(name: str, structure: dict) -> list[str]:
    """catalog.yaml variant 후보 스캐폴드 (override-only, CDO 검수 후 반영)."""
    if not structure["variants"]:
        return ["  (BEM modifier 없음 — variant 후보 없음)"]
    out = ["```yaml", f"# presets/site-sections/catalog.yaml 후보 (component: {name})"]
    for block, mods in structure["variants"].items():
        out.append(f"{block}:")
        out.append("  variants:")
        for mod in mods:
            out.append(f"    - {mod}")
    out.append("```")
    return out


def render_report(name: str, candidates: dict, structure: dict | None = None) -> str:
    lines = [
        f"# 정규화 리포트 — {name}",
        "",
        "> CDO 검수용 후보 추출. 토큰 매핑/variant 반영은 검수 후에만 repo 에 커밋.",
        "",
        f"## 후보 색 ({len(candidates['colors'])})",
        *(f"- `{c}`  → semantic 키 매핑 TODO" for c in candidates["colors"]),
        "",
        f"## 후보 타이포 ({len(candidates['fonts'])})",
        *(f"- `{f}`" for f in candidates["fonts"]),
        "",
        f"## 후보 간격 ({len(candidates['spacings'])})",
        *(f"- `{s}`" for s in candidates["spacings"]),
    ]
    if structure is not None:
        nvar = sum(len(v) for v in structure["variants"].values())
        lines += [
            "",
            f"## 슬롯 — 데이터 계약 ({len(structure['slots'])}) (v2 WP-D)",
            "> 이 컴포넌트가 노출하는 데이터 자리. main 레포 screen-manifest 가 채운다(cloud 미도달).",
            *(f"- `{{{{{s}}}}}`" for s in structure["slots"]),
            "",
            f"## variant 후보 — BEM modifier ({nvar}) (v2 WP-D)",
            "> 경계 확대: 셸이 슬롯 템플릿이라 구조가 안전하게 넘어온다. catalog variant 로 분해.",
            *_variant_scaffold(name, structure),
        ]
    lines += [
        "",
        "## 다음 단계 (TODO)",
        "- [ ] 후보 색 → design/tokens/semantic.json 키 매핑 (CDO)",
        "- [ ] theme.yaml override 초안 생성 (override-only)",
        "- [ ] 위 variant 후보를 presets/site-sections/catalog.yaml 에 반영 (CDO 검수)",
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
    structure = extract_structure(text)
    print(render_report(component_dir.name, candidates, structure))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
