"""tests/design/test_bridge_guards.py — Design-Cloud Bridge WP-2 가드 5종 (L1 pytest).

scripts/diagnose.py 의 G-16~G-20 (Growth-130) 단위테스트. 각 가드는 g14/g15 패턴대로
디렉터리 주입을 받으므로 임시 디렉터리로 PASS/FAIL/SPEC 세 경로를 모두 검증한다.

  G-16 upload scope     — staging PII/시크릿 누출 차단
  G-17 cloud-coupling   — 인도물 claude.ai 결합 흔적 0
  G-18 cross-tenant     — 복제본에 타 테넌트 slug 0
  G-19 DTCG schema      — 토큰 override semantic 화이트리스트 준수
  G-20 normalization    — production 직붙임(정규화 우회) 차단

설계: docs/architecture/design-cloud-bridge-execution-plan.md (WP-2).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts"))

import diagnose  # noqa: E402


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# ── G-16 upload scope ──────────────────────────────────────────────────────
class TestG16UploadScope:
    def test_spec_when_no_staging(self, tmp_path: Path) -> None:
        r = diagnose.g16_design_upload_scope(staging_dir=tmp_path / "absent")
        assert r.status == "SPEC"

    def test_pass_clean_component(self, tmp_path: Path) -> None:
        _write(tmp_path / "hero/index.html", "<section class='hero'>Welcome</section>")
        r = diagnose.g16_design_upload_scope(staging_dir=tmp_path)
        assert r.status == "PASS", r.violations

    def test_fail_on_email_and_rrn(self, tmp_path: Path) -> None:
        _write(tmp_path / "card/c.html", "<p>client: hong@example.com 880101-1234567</p>")
        r = diagnose.g16_design_upload_scope(staging_dir=tmp_path)
        assert r.status == "FAIL"
        assert any("email" in v for v in r.violations)
        assert any("RRN" in v for v in r.violations)

    def test_fail_on_secret_path_ref(self, tmp_path: Path) -> None:
        _write(tmp_path / "x/y.css", "/* import apps/intake/data/clients.csv */")
        r = diagnose.g16_design_upload_scope(staging_dir=tmp_path)
        assert r.status == "FAIL"
        assert any("apps/intake/data" in v for v in r.violations)

    def test_readme_only_is_spec(self, tmp_path: Path) -> None:
        _write(tmp_path / "README.md", "staging convention")
        r = diagnose.g16_design_upload_scope(staging_dir=tmp_path)
        assert r.status == "SPEC"


# ── G-17 cloud-coupling leak ───────────────────────────────────────────────
class TestG17CloudCoupling:
    def test_spec_when_no_roots(self, tmp_path: Path) -> None:
        r = diagnose.g17_cloud_coupling_leak(scan_roots=(tmp_path / "absent",))
        assert r.status == "SPEC"

    def test_pass_clean_delivery(self, tmp_path: Path) -> None:
        _write(tmp_path / "src/index.astro", "<h1>Acme</h1><style>.a{color:#111}</style>")
        r = diagnose.g17_cloud_coupling_leak(scan_roots=(tmp_path,))
        assert r.status == "PASS", r.violations

    def test_fail_on_cloud_token(self, tmp_path: Path) -> None:
        _write(tmp_path / "src/app.js", "fetch('https://claude.ai/design/sync')")
        r = diagnose.g17_cloud_coupling_leak(scan_roots=(tmp_path,))
        assert r.status == "FAIL"
        assert any("claude.ai" in v for v in r.violations)


# ── G-18 cross-tenant leak ─────────────────────────────────────────────────
class TestG18CrossTenant:
    def test_spec_when_no_replica_root(self, tmp_path: Path) -> None:
        r = diagnose.g18_cross_tenant_leak(replica_root=tmp_path / "absent")
        assert r.status == "SPEC"

    def test_pass_own_slug_only(self, tmp_path: Path) -> None:
        rroot = tmp_path / "replicas"
        _write(rroot / "cust-alpha/index.html", "<h1>cust-alpha portal</h1>")
        _write(rroot / "cust-beta/index.html", "<h1>cust-beta portal</h1>")
        r = diagnose.g18_cross_tenant_leak(
            replica_root=rroot, profiles_dir=tmp_path / "p", cases_dir=tmp_path / "c",
        )
        assert r.status == "PASS", r.violations

    def test_fail_on_foreign_slug(self, tmp_path: Path) -> None:
        rroot = tmp_path / "replicas"
        _write(rroot / "cust-alpha/data.json", '{"ref": "cust-beta"}')
        _write(rroot / "cust-beta/index.html", "<h1>cust-beta</h1>")
        r = diagnose.g18_cross_tenant_leak(
            replica_root=rroot, profiles_dir=tmp_path / "p", cases_dir=tmp_path / "c",
        )
        assert r.status == "FAIL"
        assert any("cust-beta" in v and "cust-alpha" in v for v in r.violations)


# ── G-19 DTCG schema ───────────────────────────────────────────────────────
class TestG19DtcgSchema:
    def test_spec_when_no_token_files(self, tmp_path: Path) -> None:
        (tmp_path / "comp").mkdir(parents=True)
        r = diagnose.g19_dtcg_schema(staging_dir=tmp_path)
        # semantic.json 존재 시 SPEC(토큰파일 없음); 부재 시도 SPEC.
        assert r.status == "SPEC"

    def test_pass_valid_override(self, tmp_path: Path) -> None:
        _write(tmp_path / "hero/hero.tokens.json", '{"color": {"primary": "#101010"}}')
        r = diagnose.g19_dtcg_schema(staging_dir=tmp_path)
        # semantic.json 부재 환경이면 SPEC, 존재하면 PASS.
        assert r.status in {"PASS", "SPEC"}, r.violations

    def test_fail_on_unknown_key(self, tmp_path: Path) -> None:
        _write(tmp_path / "hero/hero.tokens.json", '{"color": {"totally-bogus": "#fff"}}')
        r = diagnose.g19_dtcg_schema(staging_dir=tmp_path)
        if r.status == "SPEC":
            return  # semantic.json 부재 환경 — 검증 불가, skip
        assert r.status == "FAIL"
        assert any("totally-bogus" in v for v in r.violations)


# ── G-20 normalization gate ────────────────────────────────────────────────
class TestG20NormalizationGate:
    def test_spec_when_no_roots(self, tmp_path: Path) -> None:
        r = diagnose.g20_normalization_gate(production_roots=(tmp_path / "absent",))
        assert r.status == "SPEC"

    def test_pass_clean_production(self, tmp_path: Path) -> None:
        _write(tmp_path / "themes/acme/theme.yaml", "color:\n  primary: '#111'\n")
        r = diagnose.g20_normalization_gate(production_roots=(tmp_path,))
        assert r.status == "PASS", r.violations

    def test_fail_on_staging_marker(self, tmp_path: Path) -> None:
        _write(tmp_path / "adapters/x/raw.html", "<!-- design-sync:staging -->\n<div>raw</div>")
        r = diagnose.g20_normalization_gate(production_roots=(tmp_path,))
        assert r.status == "FAIL"
        assert any("bypassed the normalization gate" in v for v in r.violations)
