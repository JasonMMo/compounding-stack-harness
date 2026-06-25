"""tests/design/test_build_replica.py — Design-Cloud Bridge WP-3 복제본 빌더 (L1 pytest).

scaffold/npm 같은 외부 단계 없이 WP-3 고유 로직(격리 복제 + 누출 3종 게이트)을 픽스처
dist 로 결정적으로 검증한다. 실제 astro 빌드는 production Dockerfile 경로로 별도 검증.

  isolate_bundle  — dist → <replica_root>/<slug>/ 격리 복제(정리 후)
  verify_no_leak  — 번들에 cloud 결합(G-17)·타 테넌트 slug(G-18)·raw PII 0

설계: docs/architecture/design-cloud-bridge-execution-plan.md (WP-3).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "design"))

import build_replica as br  # noqa: E402


def _dist(root: Path, files: dict[str, str]) -> Path:
    d = root / "dist"
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return d


def _empty(root: Path) -> Path:
    p = root / "none"
    p.mkdir(parents=True, exist_ok=True)
    return p


class TestDeliverableKind:
    def test_nested_and_flat(self) -> None:
        assert br._deliverable_kind({"stack": {"deliverable_kind": "marketing-site"}}) == "marketing-site"
        assert br._deliverable_kind({"deliverable_kind": "business-system"}) == "business-system"
        assert br._deliverable_kind({}) == ""


class TestIsolate:
    def test_copies_and_overwrites(self, tmp_path: Path) -> None:
        src = _dist(tmp_path / "a", {"index.html": "<h1>x</h1>", "_astro/app.css": ".a{}"})
        rroot = tmp_path / "replicas"
        dest = br.isolate_bundle(src, "acme", rroot)
        assert (dest / "index.html").is_file()
        assert (dest / "_astro/app.css").is_file()
        # 재빌드 시 stale 파일 제거 확인
        (dest / "stale.txt").write_text("old", encoding="utf-8")
        src2 = _dist(tmp_path / "b", {"index.html": "<h1>y</h1>"})
        dest2 = br.isolate_bundle(src2, "acme", rroot)
        assert not (dest2 / "stale.txt").exists()
        assert (dest2 / "index.html").read_text(encoding="utf-8") == "<h1>y</h1>"


class TestVerifyNoLeak:
    def _build(self, tmp_path: Path, files: dict[str, str], slug: str = "acme") -> tuple[Path, Path]:
        src = _dist(tmp_path / "src", files)
        return tmp_path / "replicas", br.isolate_bundle(src, slug, tmp_path / "replicas")

    def test_clean_bundle_passes(self, tmp_path: Path) -> None:
        rroot, _ = self._build(tmp_path, {"index.html": "<h1>Acme Co</h1><style>.a{color:#111}</style>"})
        v = br.verify_no_leak(rroot, "acme", profiles_dir=_empty(tmp_path), cases_dir=_empty(tmp_path))
        assert v == [], v

    def test_detects_cloud_ref(self, tmp_path: Path) -> None:
        rroot, _ = self._build(tmp_path, {"app.js": "fetch('https://claude.ai/design/x')"})
        v = br.verify_no_leak(rroot, "acme", profiles_dir=_empty(tmp_path), cases_dir=_empty(tmp_path))
        assert any(x.startswith("[G-17]") for x in v), v

    def test_detects_foreign_tenant_slug(self, tmp_path: Path) -> None:
        rroot = tmp_path / "replicas"
        br.isolate_bundle(_dist(tmp_path / "a", {"d.json": '{"ref":"cust-beta"}'}), "cust-alpha", rroot)
        br.isolate_bundle(_dist(tmp_path / "b", {"index.html": "<h1>beta</h1>"}), "cust-beta", rroot)
        v = br.verify_no_leak(rroot, "cust-alpha", profiles_dir=_empty(tmp_path), cases_dir=_empty(tmp_path))
        assert any(x.startswith("[G-18]") and "cust-beta" in x for x in v), v

    def test_detects_raw_pii(self, tmp_path: Path) -> None:
        rroot, _ = self._build(tmp_path, {"about.html": "<p>contact: hong@example.com</p>"})
        v = br.verify_no_leak(rroot, "acme", profiles_dir=_empty(tmp_path), cases_dir=_empty(tmp_path))
        assert any(x.startswith("[PII]") for x in v), v
