"""test_site_manifest.py — site_manifest.py unit + integration tests.

Layers covered:
  L1 (pytest): build_site_manifest(agency-demo) success.
  L1 (pytest): validate_site rejects unknown section type.
  L1 (pytest): validate_site rejects missing required copy_slot.
  L1 (pytest): validate_site rejects invalid variant.
  L1 (pytest): validate_site accepts valid section.
  L1 (regression): business-system scaffold path (shop-demo) unchanged.
  L1 (dogfood): scaffold.py --profile agency-demo produces site-manifest.json, no DDL.

Run:
  pytest scripts/workflow/tests/test_site_manifest.py -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WORKFLOW_DIR = REPO_ROOT / "scripts" / "workflow"
PROFILES_DIR = REPO_ROOT / "profiles"

if str(WORKFLOW_DIR) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_DIR))

from site_manifest import (  # noqa: E402
    load_section_catalog,
    validate_site,
    build_site_manifest,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def catalog():
    return load_section_catalog()


@pytest.fixture(scope="session")
def agency_profile():
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not available")
    path = PROFILES_DIR / "agency-demo.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def minimal_site():
    """Minimal valid site block with one hero section."""
    return {
        "pages": [
            {
                "slug": "home",
                "title": "Home",
                "sections": [
                    {
                        "type": "hero",
                        "copy": {"headline": "Hello", "subhead": "World"},
                    }
                ],
            }
        ]
    }


# ---------------------------------------------------------------------------
# Catalog: structure
# ---------------------------------------------------------------------------

class TestCatalogLoad:
    def test_catalog_loads(self, catalog):
        assert isinstance(catalog, dict)
        assert "sections" in catalog

    def test_catalog_version(self, catalog):
        assert catalog.get("version") == "1.0"

    def test_eight_section_types(self, catalog):
        sections = catalog["sections"]
        expected = {"hero", "logos", "features", "pricing", "testimonial", "faq", "cta", "footer"}
        assert set(sections.keys()) == expected

    def test_each_section_has_required_copy_slots(self, catalog):
        for sec_type, entry in catalog["sections"].items():
            assert "copy_slots" in entry, f"{sec_type}: missing copy_slots"
            assert "required" in entry["copy_slots"], f"{sec_type}: missing copy_slots.required"

    def test_hero_required_slots(self, catalog):
        hero = catalog["sections"]["hero"]
        assert "headline" in hero["copy_slots"]["required"]
        assert "subhead" in hero["copy_slots"]["required"]

    def test_footer_required_slots(self, catalog):
        footer = catalog["sections"]["footer"]
        assert "brand_name" in footer["copy_slots"]["required"]


# ---------------------------------------------------------------------------
# validate_site: happy path
# ---------------------------------------------------------------------------

class TestValidateSiteHappy:
    def test_minimal_site_valid(self, catalog, minimal_site):
        errs = validate_site(minimal_site, catalog)
        assert errs == [], f"Expected no violations, got: {errs}"

    def test_agency_demo_site_valid(self, catalog, agency_profile):
        site = agency_profile.get("site", {})
        errs = validate_site(site, catalog)
        assert errs == [], f"agency-demo site block has violations: {errs}"

    def test_valid_variant_accepted(self, catalog):
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "hero",
                            "variant": "split-left",
                            "copy": {"headline": "Hi", "subhead": "There"},
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert errs == []


# ---------------------------------------------------------------------------
# validate_site: unknown section type
# ---------------------------------------------------------------------------

class TestValidateSiteUnknownType:
    def test_unknown_type_detected(self, catalog):
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "nonexistent-section-xyz",
                            "copy": {"headline": "Hi"},
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert len(errs) == 1
        assert "nonexistent-section-xyz" in errs[0]

    def test_error_message_names_page(self, catalog):
        site = {
            "pages": [
                {
                    "slug": "about",
                    "title": "About",
                    "sections": [{"type": "bogus", "copy": {}}],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert any("about" in e for e in errs)


# ---------------------------------------------------------------------------
# validate_site: missing required copy_slot
# ---------------------------------------------------------------------------

class TestValidateSiteRequiredCopy:
    def test_missing_headline_detected(self, catalog):
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "hero",
                            # headline and subhead both missing
                            "copy": {},
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert any("headline" in e for e in errs)
        assert any("subhead" in e for e in errs)

    def test_missing_one_slot_of_two(self, catalog):
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "hero",
                            "copy": {"headline": "Hi"},  # subhead missing
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert len(errs) == 1
        assert "subhead" in errs[0]

    def test_missing_footer_brand_name(self, catalog):
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "footer",
                            "copy": {},  # brand_name missing
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert any("brand_name" in e for e in errs)


# ---------------------------------------------------------------------------
# validate_site: invalid variant
# ---------------------------------------------------------------------------

class TestValidateSiteVariant:
    def test_invalid_variant_rejected(self, catalog):
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "hero",
                            "variant": "does-not-exist",
                            "copy": {"headline": "Hi", "subhead": "There"},
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert len(errs) == 1
        assert "does-not-exist" in errs[0]

    def test_no_variant_is_valid(self, catalog):
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "hero",
                            "copy": {"headline": "Hi", "subhead": "There"},
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert errs == []


# ---------------------------------------------------------------------------
# build_site_manifest: structure
# ---------------------------------------------------------------------------

class TestBuildSiteManifest:
    def test_agency_demo_manifest_structure(self, agency_profile):
        manifest = build_site_manifest(agency_profile)
        assert manifest["slug"] == "agency-demo"
        assert manifest["deliverable_kind"] == "marketing-site"
        assert "pages" in manifest
        assert len(manifest["pages"]) >= 1

    def test_pages_have_required_fields(self, agency_profile):
        manifest = build_site_manifest(agency_profile)
        for page in manifest["pages"]:
            assert "slug" in page
            assert "title" in page
            assert "sections" in page

    def test_sections_have_type(self, agency_profile):
        manifest = build_site_manifest(agency_profile)
        for page in manifest["pages"]:
            for section in page["sections"]:
                assert "type" in section
                assert section["type"]

    def test_contact_present_when_enabled(self, agency_profile):
        manifest = build_site_manifest(agency_profile)
        assert "contact" in manifest
        assert manifest["contact"]["enabled"] is True
        assert "wire_key" in manifest["contact"]

    def test_contact_wire_key_not_reimplemented(self, agency_profile):
        """G-1: wire_key is a reference string, not a contract implementation.
        DEC-5: contact uses entity.create wire key with entity_type=lead.
        """
        manifest = build_site_manifest(agency_profile)
        wire_key = manifest["contact"]["wire_key"]
        # Must be a simple reference string, not a dict/implementation
        assert isinstance(wire_key, str)
        # DEC-5: uses entity.create (reusing existing wire key, no new key created)
        assert wire_key == "entity.create"
        assert manifest["contact"]["entity_type"] == "lead"

    def test_theme_present(self, agency_profile):
        manifest = build_site_manifest(agency_profile)
        assert "theme" in manifest

    def test_deterministic(self, agency_profile):
        m1 = build_site_manifest(agency_profile)
        m2 = build_site_manifest(agency_profile)
        assert m1 == m2

    def test_no_entity_keys_in_manifest(self, agency_profile):
        """marketing-site manifest must not contain business-system entity keys."""
        manifest = build_site_manifest(agency_profile)
        assert "entities" not in manifest
        assert "catalog_version" not in manifest

    def test_home_page_hero_section(self, agency_profile):
        manifest = build_site_manifest(agency_profile)
        home = next((p for p in manifest["pages"] if p["slug"] == "home"), None)
        assert home is not None
        hero = next((s for s in home["sections"] if s["type"] == "hero"), None)
        assert hero is not None
        assert "copy" in hero
        assert "headline" in hero["copy"]


# ---------------------------------------------------------------------------
# Regression: business-system path unchanged
# ---------------------------------------------------------------------------

class TestRegressionBusinessSystem:
    def test_shop_demo_still_produces_screen_manifest(self, tmp_path):
        """scaffold.py --profile shop-demo must still emit screen-manifest.json (no regression)."""
        result = subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "shop-demo",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"business-system scaffold regression: rc={result.returncode}\n{result.stderr}"
        )
        screen_manifest = tmp_path / "shop-demo" / "screen-manifest.json"
        assert screen_manifest.exists(), "screen-manifest.json must exist for business-system"
        data = json.loads(screen_manifest.read_text(encoding="utf-8"))
        assert data["profile"] == "shop-demo"
        assert "entities" in data

    def test_shop_demo_no_site_manifest(self, tmp_path):
        """shop-demo must not produce a site-manifest.json."""
        result = subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "shop-demo",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
        site_manifest = tmp_path / "shop-demo" / "site-manifest.json"
        assert not site_manifest.exists(), "shop-demo must not produce site-manifest.json"


# ---------------------------------------------------------------------------
# Dogfood: agency-demo scaffold → site-manifest.json, no DDL
# ---------------------------------------------------------------------------

class TestDogfoodAgencyDemo:
    def test_scaffold_produces_site_manifest(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "agency-demo",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"scaffold.py --profile agency-demo failed:\n{result.stderr}"
        )
        site_manifest_path = tmp_path / "agency-demo" / "site-manifest.json"
        assert site_manifest_path.exists(), "site-manifest.json must be created"

    def test_scaffold_no_ddl_for_marketing_site(self, tmp_path):
        subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "agency-demo",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
            check=True,
        )
        ddl_dir = tmp_path / "agency-demo" / "ddl"
        assert not ddl_dir.exists(), "DDL directory must NOT be created for marketing-site"

    def test_scaffold_no_screen_manifest_for_marketing_site(self, tmp_path):
        subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "agency-demo",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
            check=True,
        )
        screen_manifest = tmp_path / "agency-demo" / "screen-manifest.json"
        assert not screen_manifest.exists(), (
            "screen-manifest.json must NOT be created for marketing-site"
        )

    def test_site_manifest_json_valid(self, tmp_path):
        subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "agency-demo",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
            check=True,
        )
        site_manifest_path = tmp_path / "agency-demo" / "site-manifest.json"
        data = json.loads(site_manifest_path.read_text(encoding="utf-8"))
        assert data["slug"] == "agency-demo"
        assert data["deliverable_kind"] == "marketing-site"
        assert len(data["pages"]) >= 2
        assert data["contact"]["enabled"] is True

    def test_site_manifest_home_page_sections(self, tmp_path):
        subprocess.run(
            [sys.executable, str(WORKFLOW_DIR / "scaffold.py"),
             "--profile", "agency-demo",
             "--out", str(tmp_path)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
            check=True,
        )
        data = json.loads(
            (tmp_path / "agency-demo" / "site-manifest.json").read_text(encoding="utf-8")
        )
        home = next(p for p in data["pages"] if p["slug"] == "home")
        section_types = [s["type"] for s in home["sections"]]
        assert "hero" in section_types
        assert "footer" in section_types
