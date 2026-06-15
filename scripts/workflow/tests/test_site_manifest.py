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
        # Catalog grows as new archetypes are added (A2 added gallery + story).
        # Invariant: original 8 types must still be present; new types are additive.
        sections = catalog["sections"]
        original_eight = {"hero", "logos", "features", "pricing", "testimonial", "faq", "cta", "footer"}
        assert original_eight.issubset(set(sections.keys())), (
            f"Original 8 section types missing from catalog: "
            f"{original_eight - set(sections.keys())}"
        )

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


# ---------------------------------------------------------------------------
# items threading: build_site_manifest passes items through
# ---------------------------------------------------------------------------

class TestItemsThreading:
    """(a) items thread through build_site_manifest into the manifest output."""

    def test_items_present_in_manifest_output(self):
        """items[] from profile section appear verbatim in manifest section output."""
        profile = {
            "customer": {"slug": "test-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "aurora",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "features",
                                "copy": {"headline": "Our Features"},
                                "items": [
                                    {"title": "Fast", "description": "Ships in seconds."},
                                    {"title": "Reliable", "description": "99.9% uptime."},
                                ],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        home = manifest["pages"][0]
        features_sec = home["sections"][0]
        assert "items" in features_sec
        assert len(features_sec["items"]) == 2
        assert features_sec["items"][0]["title"] == "Fast"
        assert features_sec["items"][1]["description"] == "99.9% uptime."

    def test_section_without_items_omits_key(self):
        """A section with no items list must not include an 'items' key in the manifest."""
        profile = {
            "customer": {"slug": "test-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "aurora",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "features",
                                "copy": {"headline": "Our Features"},
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        features_sec = manifest["pages"][0]["sections"][0]
        assert "items" not in features_sec

    def test_faq_items_thread_through(self):
        """FAQ items thread through just as features items do."""
        profile = {
            "customer": {"slug": "test-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "aurora",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "faq",
                                "copy": {"headline": "FAQ"},
                                "items": [
                                    {"question": "What is this?", "answer": "A great product."},
                                ],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        faq_sec = manifest["pages"][0]["sections"][0]
        assert "items" in faq_sec
        assert faq_sec["items"][0]["question"] == "What is this?"


# ---------------------------------------------------------------------------
# items validation: validate_site checks item_slots.required
# ---------------------------------------------------------------------------

class TestItemSlotsValidation:
    """(b) validate_site flags a features item missing required 'description'.
    (c) validate_site passes when items are well-formed.
    (d) a section with no items list still validates (no false error).
    """

    def test_features_item_missing_description_flagged(self, catalog):
        """(b) item missing required 'description' produces a violation."""
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "features",
                            "copy": {"headline": "Features"},
                            "items": [
                                {"title": "Fast"},  # description missing
                            ],
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert any("description" in e for e in errs), f"Expected violation for 'description', got: {errs}"
        assert any("item[0]" in e for e in errs)

    def test_features_item_missing_title_flagged(self, catalog):
        """item missing required 'title' produces a violation."""
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "features",
                            "copy": {"headline": "Features"},
                            "items": [
                                {"description": "Some text"},  # title missing
                            ],
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert any("title" in e for e in errs), f"Expected violation for 'title', got: {errs}"

    def test_faq_item_missing_answer_flagged(self, catalog):
        """FAQ item missing required 'answer' produces a violation."""
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "faq",
                            "copy": {"headline": "FAQ"},
                            "items": [
                                {"question": "What is this?"},  # answer missing
                            ],
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert any("answer" in e for e in errs), f"Expected violation for 'answer', got: {errs}"

    def test_well_formed_features_items_pass(self, catalog):
        """(c) validate_site passes when all required item slots are present."""
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "features",
                            "copy": {"headline": "Features"},
                            "items": [
                                {"title": "Fast", "description": "Ships in seconds."},
                                {"title": "Reliable", "description": "99.9% uptime.", "icon": "shield"},
                            ],
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert errs == [], f"Expected no violations for well-formed items, got: {errs}"

    def test_well_formed_faq_items_pass(self, catalog):
        """(c) well-formed FAQ items pass validation."""
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "faq",
                            "copy": {"headline": "FAQ"},
                            "items": [
                                {"question": "How much?", "answer": "Free tier available."},
                            ],
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert errs == [], f"Expected no violations for well-formed FAQ items, got: {errs}"

    def test_section_without_items_no_error(self, catalog):
        """(d) a features/faq section with no items list must not produce a violation."""
        site = {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "features",
                            "copy": {"headline": "Features"},
                            # no items key at all — fallback to demo items in component
                        },
                        {
                            "type": "faq",
                            "copy": {"headline": "FAQ"},
                            # no items key at all
                        },
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert errs == [], f"Expected no violations when items omitted, got: {errs}"

    def test_violation_message_includes_page_section_and_index(self, catalog):
        """Violation message includes page slug, section type, and item index."""
        site = {
            "pages": [
                {
                    "slug": "services",
                    "title": "Services",
                    "sections": [
                        {
                            "type": "features",
                            "copy": {"headline": "Features"},
                            "items": [
                                {"title": "OK", "description": "Fine"},      # item[0] good
                                {"title": "Missing desc"},                    # item[1] bad
                            ],
                        }
                    ],
                }
            ]
        }
        errs = validate_site(site, catalog)
        assert len(errs) == 1
        assert "services" in errs[0]
        assert "features" in errs[0]
        assert "item[1]" in errs[0]
        assert "description" in errs[0]
