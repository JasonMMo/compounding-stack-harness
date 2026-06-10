"""build_graph.py — knowledge/wiki 지식그래프 오프라인 HTML 생성.

knowledge/wiki/{sources,entities,concepts,syntheses}/*.md 를 파싱해
노드(페이지)/엣지([[wikilink]]) 그래프를 JSON + 완전 self-contained HTML로 출력.

Usage:
  python scripts/wiki/build_graph.py
  python scripts/wiki/build_graph.py --wiki-dir knowledge/wiki --out-dir out
  python scripts/wiki/build_graph.py --help

Exit codes:
  0 — success (0 pages도 valid HTML 생성)
  1 — I/O error
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo layout
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WIKI_DIR = REPO_ROOT / "knowledge" / "wiki"
DEFAULT_OUT_DIR = REPO_ROOT / "out"

WIKI_SUBDIRS = ("sources", "entities", "concepts", "syntheses")
EXCLUDED_STEMS = {"README", "index"}

# G-8: ASCII slug pattern (no Korean filenames — enforced by catalog)
_WIKILINK_RE = re.compile(r"\[\[([A-Za-z0-9_\-]+)\]\]")
_FM_START = re.compile(r"^---\s*$")
_FM_KV = re.compile(r"^(\w+)\s*:\s*(.+)$")

# ---------------------------------------------------------------------------
# Frontmatter parser (stdlib only — no PyYAML)
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter_dict, body_text).

    Handles only simple ``key: value`` lines — sufficient for wiki pages.
    Multi-line values and YAML arrays are read as raw strings.
    """
    lines = text.splitlines(keepends=True)
    fm: dict[str, str] = {}
    body_start = 0

    if lines and _FM_START.match(lines[0]):
        for i, line in enumerate(lines[1:], start=1):
            if _FM_START.match(line):
                body_start = i + 1
                break
            m = _FM_KV.match(line.rstrip())
            if m:
                fm[m.group(1)] = m.group(2).strip()

    body = "".join(lines[body_start:])
    return fm, body


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph(wiki_dir: Path) -> dict:
    """Parse wiki pages and return {nodes: [...], edges: [...]} graph dict."""
    nodes: dict[str, dict] = {}   # slug -> node
    raw_edges: list[tuple[str, str]] = []

    for subdir in WIKI_SUBDIRS:
        sub_path = wiki_dir / subdir
        if not sub_path.is_dir():
            continue
        for md_file in sorted(sub_path.glob("*.md")):
            slug = md_file.stem
            if slug in EXCLUDED_STEMS:
                continue
            try:
                text = md_file.read_text(encoding="utf-8")
            except OSError as exc:
                print(f"WARNING: cannot read {md_file}: {exc}", file=sys.stderr)
                continue

            fm, body = _parse_frontmatter(text)
            label = fm.get("title") or slug
            group = fm.get("type") or subdir

            nodes[slug] = {
                "id": slug,
                "label": label,
                "group": group,
                "dangling": False,
            }

            for target in _WIKILINK_RE.findall(body):
                raw_edges.append((slug, target))

    # Resolve dangling targets
    seen_edges: set[tuple[str, str]] = set()
    edges: list[dict] = []

    for src, tgt in raw_edges:
        if src == tgt:
            continue  # self-loop — skip
        key = (src, tgt)
        if key in seen_edges:
            continue
        seen_edges.add(key)

        if tgt not in nodes:
            nodes[tgt] = {
                "id": tgt,
                "label": tgt,
                "group": "dangling",
                "dangling": True,
            }
        edges.append({"source": src, "target": tgt})

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
    }


# ---------------------------------------------------------------------------
# HTML generator — ~100-line inline vanilla JS force-directed canvas
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>Wiki Knowledge Graph</title>
<style>
  body {{ margin: 0; background: #1a1a2e; color: #e0e0e0; font-family: sans-serif; overflow: hidden; }}
  #canvas {{ display: block; }}
  #info {{ position: fixed; top: 10px; left: 10px; background: rgba(0,0,0,.6);
           padding: 8px 12px; border-radius: 6px; font-size: 13px; pointer-events: none; }}
  #tooltip {{ position: fixed; background: rgba(0,0,0,.8); color: #fff;
              padding: 6px 10px; border-radius: 4px; font-size: 12px;
              pointer-events: none; display: none; white-space: nowrap; }}
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div id="info">{node_count} pages &nbsp;|&nbsp; {edge_count} links &nbsp;|&nbsp; drag · scroll-zoom</div>
<div id="tooltip"></div>
<script>
const GRAPH = {graph_json};

// ---- colour palette per group ----
const PALETTE = {{
  sources:    "#4fc3f7",
  entities:   "#81c784",
  concepts:   "#ffb74d",
  syntheses:  "#ce93d8",
  dangling:   "#666677",
}};
function nodeColor(n) {{ return PALETTE[n.group] || "#90caf9"; }}

// ---- layout state ----
const canvas = document.getElementById("canvas");
const ctx    = canvas.getContext("2d");
const tip    = document.getElementById("tooltip");

let W, H;
function resize() {{ W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }}
window.addEventListener("resize", () => {{ resize(); draw(); }});
resize();

// init positions
const nodes = GRAPH.nodes.map((n, i) => {{
  const angle = (2 * Math.PI * i) / Math.max(GRAPH.nodes.length, 1);
  const r = Math.min(W, H) * 0.33;
  return {{ ...n, x: W/2 + r * Math.cos(angle), y: H/2 + r * Math.sin(angle), vx: 0, vy: 0 }};
}});
const nodeMap = {{}};
nodes.forEach(n => nodeMap[n.id] = n);
const edges = GRAPH.edges;

// ---- force-directed simulation ----
const K_REPEL  = 4000;
const K_SPRING = 0.05;
const K_DAMP   = 0.85;
const REST_LEN = 120;

function simulate() {{
  const n = nodes.length;
  // repulsion
  for (let i = 0; i < n; i++) {{
    for (let j = i + 1; j < n; j++) {{
      let dx = nodes[j].x - nodes[i].x;
      let dy = nodes[j].y - nodes[i].y;
      let d2 = dx*dx + dy*dy + 1;
      let f  = K_REPEL / d2;
      nodes[i].vx -= f * dx; nodes[i].vy -= f * dy;
      nodes[j].vx += f * dx; nodes[j].vy += f * dy;
    }}
  }}
  // spring attraction along edges
  edges.forEach(e => {{
    const a = nodeMap[e.source], b = nodeMap[e.target];
    if (!a || !b) return;
    let dx = b.x - a.x, dy = b.y - a.y;
    let d  = Math.sqrt(dx*dx + dy*dy) || 1;
    let f  = K_SPRING * (d - REST_LEN);
    let fx = f * dx / d, fy = f * dy / d;
    a.vx += fx; a.vy += fy;
    b.vx -= fx; b.vy -= fy;
  }});
  // centre gravity
  nodes.forEach(n => {{
    n.vx += (W/2 - n.x) * 0.002;
    n.vy += (H/2 - n.y) * 0.002;
  }});
  // integrate + damp + pin dragged
  nodes.forEach(n => {{
    if (n === dragging) return;
    n.vx *= K_DAMP; n.vy *= K_DAMP;
    n.x  += n.vx;   n.y  += n.vy;
  }});
}}

// ---- pan/zoom state ----
let offsetX = 0, offsetY = 0, scale = 1;

function toWorld(px, py) {{
  return [(px - offsetX) / scale, (py - offsetY) / scale];
}}

// ---- drag state ----
let dragging = null, dragOffX = 0, dragOffY = 0;
let panning  = false, panStartX = 0, panStartY = 0, panOX = 0, panOY = 0;

function nodeAt(wx, wy) {{
  for (let i = nodes.length - 1; i >= 0; i--) {{
    let n = nodes[i], dx = n.x - wx, dy = n.y - wy;
    if (dx*dx + dy*dy < 14*14) return n;
  }}
  return null;
}}

canvas.addEventListener("mousedown", e => {{
  const [wx, wy] = toWorld(e.clientX, e.clientY);
  const hit = nodeAt(wx, wy);
  if (hit) {{ dragging = hit; dragOffX = wx - hit.x; dragOffY = wy - hit.y; }}
  else      {{ panning = true; panStartX = e.clientX; panStartY = e.clientY; panOX = offsetX; panOY = offsetY; }}
}});
canvas.addEventListener("mousemove", e => {{
  const [wx, wy] = toWorld(e.clientX, e.clientY);
  if (dragging) {{ dragging.x = wx - dragOffX; dragging.y = wy - dragOffY; }}
  else if (panning) {{
    offsetX = panOX + (e.clientX - panStartX);
    offsetY = panOY + (e.clientY - panStartY);
  }}
  const hit = nodeAt(wx, wy);
  if (hit) {{
    tip.style.display = "block";
    tip.style.left = (e.clientX + 12) + "px";
    tip.style.top  = (e.clientY + 12) + "px";
    tip.textContent = hit.label + " [" + hit.group + "]";
  }} else {{ tip.style.display = "none"; }}
}});
canvas.addEventListener("mouseup", () => {{ dragging = null; panning = false; }});
canvas.addEventListener("wheel",   e => {{
  e.preventDefault();
  const factor = e.deltaY < 0 ? 1.1 : 0.9;
  const [wx, wy] = toWorld(e.clientX, e.clientY);
  scale   *= factor;
  offsetX  = e.clientX - wx * scale;
  offsetY  = e.clientY - wy * scale;
}}, {{ passive: false }});

// ---- draw ----
function draw() {{
  ctx.setTransform(1,0,0,1,0,0);
  ctx.clearRect(0, 0, W, H);
  ctx.setTransform(scale, 0, 0, scale, offsetX, offsetY);

  // edges
  edges.forEach(e => {{
    const a = nodeMap[e.source], b = nodeMap[e.target];
    if (!a || !b) return;
    const isDangling = (b && b.dangling);
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    if (isDangling) {{
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = "#555566";
    }} else {{
      ctx.setLineDash([]);
      ctx.strokeStyle = "#444466";
    }}
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.setLineDash([]);
  }});

  // nodes
  const R = 11;
  nodes.forEach(n => {{
    ctx.beginPath();
    ctx.arc(n.x, n.y, R, 0, 2*Math.PI);
    ctx.fillStyle = nodeColor(n);
    ctx.fill();
    if (n.dangling) {{
      ctx.setLineDash([3, 3]);
      ctx.strokeStyle = "#999";
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.setLineDash([]);
    }}
    // label
    ctx.fillStyle = "#ddd";
    ctx.font = "10px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(n.label.length > 18 ? n.label.slice(0,17)+"…" : n.label, n.x, n.y + R + 12);
  }});
}}

// ---- animation loop ----
function loop() {{
  simulate();
  draw();
  requestAnimationFrame(loop);
}}

if (nodes.length === 0) {{
  // empty wiki — show placeholder
  ctx.setTransform(1,0,0,1,0,0);
  ctx.fillStyle = "#555";
  ctx.font = "20px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("0 pages — wiki is empty", W/2, H/2);
}} else {{
  loop();
}}
</script>
</body>
</html>
"""


def build_html(graph: dict) -> str:
    graph_json = json.dumps(graph, ensure_ascii=False)
    return _HTML_TEMPLATE.format(
        node_count=len(graph["nodes"]),
        edge_count=len(graph["edges"]),
        graph_json=graph_json,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build knowledge/wiki graph HTML (offline, no CDN)."
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=DEFAULT_WIKI_DIR,
        help="Root of wiki pages (default: knowledge/wiki)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for JSON + HTML (default: out/)",
    )
    args = parser.parse_args(argv)

    wiki_dir: Path = args.wiki_dir
    out_dir: Path = args.out_dir

    if not wiki_dir.is_dir():
        print(f"ERROR: wiki-dir not found: {wiki_dir}", file=sys.stderr)
        return 1

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"ERROR: cannot create out-dir {out_dir}: {exc}", file=sys.stderr)
        return 1

    graph = build_graph(wiki_dir)

    json_path = out_dir / "wiki-graph.json"
    html_path = out_dir / "wiki-graph.html"

    try:
        json_path.write_text(
            json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        html_path.write_text(build_html(graph), encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: write failed: {exc}", file=sys.stderr)
        return 1

    n_nodes = len(graph["nodes"])
    n_edges = len(graph["edges"])
    n_dangling = sum(1 for nd in graph["nodes"] if nd["dangling"])
    print(
        f"OK  nodes={n_nodes} (dangling={n_dangling})  edges={n_edges}\n"
        f"    {json_path}\n"
        f"    {html_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
