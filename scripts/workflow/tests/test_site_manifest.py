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


# ---------------------------------------------------------------------------
# A4 artisan: gallery/parallax-scroll + lead section type (Growth-65+)
# ---------------------------------------------------------------------------

class TestCatalogA4Artisan:
    """Catalog structure tests for A4 archetype additions."""

    def test_catalog_has_lead_and_original_types(self, catalog):
        """Catalog must contain lead (new) plus all original section types."""
        sections = catalog["sections"]
        required = {"hero", "logos", "features", "pricing", "testimonial",
                    "faq", "cta", "gallery", "story", "footer", "lead"}
        assert required.issubset(set(sections.keys())), (
            f"Expected section types missing: {required - set(sections.keys())}"
        )

    def test_lead_section_present(self, catalog):
        assert "lead" in catalog["sections"], "lead section type must be in catalog"

    def test_lead_required_copy_slot(self, catalog):
        lead = catalog["sections"]["lead"]
        assert "headline" in lead["copy_slots"]["required"]

    def test_lead_variants(self, catalog):
        lead = catalog["sections"]["lead"]
        variants = lead.get("variants", [])
        assert "minimal-field" in variants
        assert "multi-field-card" in variants

    def test_gallery_parallax_scroll_variant(self, catalog):
        gallery = catalog["sections"]["gallery"]
        assert "parallax-scroll" in gallery.get("variants", [])

    def test_gallery_new_optional_item_slots(self, catalog):
        gallery = catalog["sections"]["gallery"]
        optional_slots = gallery["item_slots"].get("optional", [])
        for field in ["heading", "subheading", "body", "cta_label", "cta_href"]:
            assert field in optional_slots, f"gallery item_slots.optional missing '{field}'"

    def test_gallery_required_item_slots_unchanged(self, catalog):
        """Existing required slots must not have changed (backward compat)."""
        gallery = catalog["sections"]["gallery"]
        required = gallery["item_slots"]["required"]
        assert "src" in required
        assert "alt" in required


class TestGalleryParallaxScroll:
    """Validation + manifest threading for gallery/parallax-scroll (A4)."""

    def _parallax_site(self, items):
        return {
            "pages": [
                {
                    "slug": "work",
                    "title": "Work",
                    "sections": [
                        {
                            "type": "gallery",
                            "variant": "parallax-scroll",
                            "copy": {"headline": "Our Work"},
                            "items": items,
                        }
                    ],
                }
            ]
        }

    def test_parallax_scroll_variant_valid(self, catalog):
        site = self._parallax_site([{"src": "img/ch1.jpg", "alt": "Chapter 1"}])
        errs = validate_site(site, catalog)
        assert errs == [], f"parallax-scroll should be valid: {errs}"

    def test_parallax_scroll_enriched_items_valid(self, catalog):
        """Items with all new optional fields pass validation."""
        items = [
            {
                "src": "img/ch1.jpg",
                "alt": "Chapter 1",
                "heading": "The Craft",
                "subheading": "Made by hand",
                "body": "Every piece is shaped with intention.",
                "cta_label": "See the process",
                "cta_href": "/process",
            }
        ]
        site = self._parallax_site(items)
        errs = validate_site(site, catalog)
        assert errs == [], f"enriched parallax-scroll items should be valid: {errs}"

    def test_parallax_scroll_no_src_valid(self, catalog):
        """src is optional for parallax-scroll (renders theme material-texture when absent).
        NOTE: catalog requires src in item_slots.required, so omitting src will fail
        validation for gallery type — this test documents the current catalog constraint.
        When the component renders, it may treat absent src as theme-texture mode; the
        catalog constraint is intentionally kept for now (CTO may relax required later).
        This test verifies missing src is caught as a violation (not silently ignored)."""
        items = [{"alt": "Chapter 1", "heading": "The Craft"}]  # src absent
        site = self._parallax_site(items)
        errs = validate_site(site, catalog)
        # src is in required — violation is expected and correct catalog behavior
        assert any("src" in e for e in errs), (
            "Missing required 'src' slot must be flagged even for parallax-scroll"
        )

    def test_parallax_scroll_items_thread_through(self):
        """New optional fields thread through build_site_manifest verbatim."""
        profile = {
            "customer": {"slug": "artisan-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "artisan",
                "pages": [
                    {
                        "slug": "work",
                        "title": "Work",
                        "sections": [
                            {
                                "type": "gallery",
                                "variant": "parallax-scroll",
                                "copy": {"headline": "Our Work"},
                                "items": [
                                    {
                                        "src": "img/ch1.jpg",
                                        "alt": "Chapter 1",
                                        "heading": "The Craft",
                                        "subheading": "Made by hand",
                                        "body": "Every piece is shaped with intention.",
                                        "cta_label": "See the process",
                                        "cta_href": "/process",
                                    },
                                    {
                                        "src": "img/ch2.jpg",
                                        "alt": "Chapter 2",
                                        "caption": "Studio",  # old optional field preserved
                                    },
                                ],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        work = manifest["pages"][0]
        gallery_sec = work["sections"][0]
        assert gallery_sec["variant"] == "parallax-scroll"
        assert "items" in gallery_sec
        item0 = gallery_sec["items"][0]
        assert item0["heading"] == "The Craft"
        assert item0["subheading"] == "Made by hand"
        assert item0["body"] == "Every piece is shaped with intention."
        assert item0["cta_label"] == "See the process"
        assert item0["cta_href"] == "/process"
        # Old optional field still threads through
        assert gallery_sec["items"][1].get("caption") == "Studio"

    def test_existing_gallery_variants_still_valid(self, catalog):
        """Existing gallery variants are not broken by the parallax-scroll addition."""
        for variant in ["masonry-3col", "full-bleed-strip", "grid-2x2"]:
            site = {
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "gallery",
                                "variant": variant,
                                "copy": {"headline": "Gallery"},
                                "items": [{"src": "img/a.jpg", "alt": "A"}],
                            }
                        ],
                    }
                ]
            }
            errs = validate_site(site, catalog)
            assert errs == [], f"variant '{variant}' should still be valid: {errs}"


class TestLeadSection:
    """Validation + manifest threading for lead section type (A4 / Growth-65+)."""

    def _lead_site(self, copy, variant=None):
        section = {"type": "lead", "copy": copy}
        if variant:
            section["variant"] = variant
        return {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [section],
                }
            ]
        }

    def test_lead_minimal_field_valid(self, catalog):
        errs = validate_site(self._lead_site({"headline": "Stay in touch"}, "minimal-field"), catalog)
        assert errs == [], f"lead/minimal-field should be valid: {errs}"

    def test_lead_multi_field_card_valid(self, catalog):
        errs = validate_site(self._lead_site({"headline": "Get in touch"}, "multi-field-card"), catalog)
        assert errs == [], f"lead/multi-field-card should be valid: {errs}"

    def test_lead_missing_headline_rejected(self, catalog):
        site = self._lead_site({"subhead": "No headline here"})
        errs = validate_site(site, catalog)
        assert any("headline" in e for e in errs), f"Missing headline must be flagged: {errs}"

    def test_lead_invalid_variant_rejected(self, catalog):
        site = self._lead_site({"headline": "Subscribe"}, variant="does-not-exist")
        errs = validate_site(site, catalog)
        assert any("does-not-exist" in e for e in errs)

    def test_lead_no_variant_valid(self, catalog):
        errs = validate_site(self._lead_site({"headline": "Subscribe"}), catalog)
        assert errs == [], f"lead with no variant should be valid: {errs}"

    def test_lead_with_all_optional_slots_valid(self, catalog):
        copy = {
            "headline": "Stay in the loop",
            "subhead": "News and updates, monthly.",
            "button_label": "Subscribe",
            "success_message": "You're in!",
            "placeholder": "your@email.com",
        }
        errs = validate_site(self._lead_site(copy, "minimal-field"), catalog)
        assert errs == [], f"lead with all optional slots should be valid: {errs}"

    def test_lead_emits_in_manifest(self):
        """lead section emits correctly through build_site_manifest."""
        profile = {
            "customer": {"slug": "artisan-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "artisan",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "lead",
                                "variant": "minimal-field",
                                "copy": {
                                    "headline": "Stay in touch",
                                    "button_label": "Subscribe",
                                    "placeholder": "your@email.com",
                                },
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        home = manifest["pages"][0]
        lead_sec = home["sections"][0]
        assert lead_sec["type"] == "lead"
        assert lead_sec["variant"] == "minimal-field"
        assert lead_sec["copy"]["headline"] == "Stay in touch"
        assert lead_sec["copy"]["button_label"] == "Subscribe"
        assert lead_sec["copy"]["placeholder"] == "your@email.com"
        # lead has no items (no item_slots in catalog)
        assert "items" not in lead_sec

    def test_lead_no_items_key_emitted(self):
        """lead section must not emit an items key (no item_slots)."""
        profile = {
            "customer": {"slug": "artisan-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "artisan",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "lead",
                                "copy": {"headline": "Subscribe"},
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        lead_sec = manifest["pages"][0]["sections"][0]
        assert "items" not in lead_sec


# ---------------------------------------------------------------------------
# A4 artisan: story/timeline-year items[] (Growth-65+ additive)
# ---------------------------------------------------------------------------

class TestStoryTimelineYear:
    """story/timeline-year: item_slots added additively; founder-split unchanged."""

    def _story_site(self, variant, items=None, copy=None):
        section = {
            "type": "story",
            "variant": variant,
            "copy": copy or {"headline": "Our story"},
        }
        if items is not None:
            section["items"] = items
        return {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [section],
                }
            ]
        }

    def test_story_catalog_has_item_slots(self, catalog):
        """story type must have item_slots after additive update."""
        story = catalog["sections"]["story"]
        assert "item_slots" in story, "story must have item_slots after catalog update"
        required = story["item_slots"]["required"]
        assert "year" in required
        assert "milestone" in required

    def test_story_item_slots_optional_detail(self, catalog):
        story = catalog["sections"]["story"]
        optional = story["item_slots"].get("optional", [])
        assert "detail" in optional

    def test_timeline_year_valid_with_items(self, catalog):
        """timeline-year with well-formed items[] passes validation."""
        items = [
            {"year": "2016", "milestone": "Studio opens"},
            {"year": "2019", "milestone": "First gas kiln fired", "detail": "Built by hand."},
        ]
        errs = validate_site(self._story_site("timeline-year", items=items), catalog)
        assert errs == [], f"timeline-year with valid items should pass: {errs}"

    def test_timeline_year_item_missing_milestone_flagged(self, catalog):
        """item missing required 'milestone' produces a violation."""
        items = [{"year": "2016"}]  # milestone missing
        errs = validate_site(self._story_site("timeline-year", items=items), catalog)
        assert any("milestone" in e for e in errs), (
            f"Missing 'milestone' must be flagged: {errs}"
        )

    def test_timeline_year_item_missing_year_flagged(self, catalog):
        """item missing required 'year' produces a violation."""
        items = [{"milestone": "Studio opens"}]  # year missing
        errs = validate_site(self._story_site("timeline-year", items=items), catalog)
        assert any("year" in e for e in errs), (
            f"Missing 'year' must be flagged: {errs}"
        )

    def test_timeline_year_without_items_valid(self, catalog):
        """timeline-year without items[] is still valid (falls back to copy.body)."""
        errs = validate_site(self._story_site("timeline-year"), catalog)
        assert errs == [], f"timeline-year with no items should be valid: {errs}"

    def test_founder_split_unchanged(self, catalog):
        """founder-split variant must still be valid after additive item_slots addition."""
        errs = validate_site(self._story_site("founder-split"), catalog)
        assert errs == [], f"founder-split must remain valid: {errs}"

    def test_timeline_year_items_thread_through_manifest(self):
        """items[] thread through build_site_manifest for story/timeline-year."""
        profile = {
            "customer": {"slug": "terra-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "kiln",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "story",
                                "variant": "timeline-year",
                                "copy": {"headline": "A studio measured in firings"},
                                "items": [
                                    {"year": "2016", "milestone": "Studio opens in a converted garage"},
                                    {"year": "2019", "milestone": "First gas kiln fired", "detail": "Built in 6 weeks."},
                                ],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        story_sec = manifest["pages"][0]["sections"][0]
        assert story_sec["variant"] == "timeline-year"
        assert "items" in story_sec
        assert len(story_sec["items"]) == 2
        assert story_sec["items"][0]["year"] == "2016"
        assert story_sec["items"][0]["milestone"] == "Studio opens in a converted garage"
        assert story_sec["items"][1]["detail"] == "Built in 6 weeks."

    def test_terra_ceramics_profile_validates(self, catalog):
        """terra-ceramics.yaml profile must validate cleanly against the catalog."""
        try:
            import yaml as _yaml
        except ImportError:
            pytest.skip("PyYAML not available")
        path = PROFILES_DIR / "terra-ceramics.yaml"
        if not path.exists():
            pytest.skip("terra-ceramics.yaml not yet created")
        with open(path, encoding="utf-8") as f:
            profile = _yaml.safe_load(f)
        site = profile.get("site", {})
        errs = validate_site(site, catalog)
        assert errs == [], f"terra-ceramics.yaml has catalog violations: {errs}"


# ---------------------------------------------------------------------------
# A6 B2B services: catalog structure — process, team, logos/quote-band
# ---------------------------------------------------------------------------

class TestCatalogA6B2BServices:
    """Catalog structure tests for A6 archetype additions (Growth-78)."""

    def test_catalog_has_process_and_team(self, catalog):
        """process and team must exist in catalog after A6 additive update."""
        sections = catalog["sections"]
        assert "process" in sections, "process section type must be in catalog"
        assert "team" in sections, "team section type must be in catalog"

    def test_catalog_has_process_team_and_thirteen_total(self, catalog):
        """Catalog must contain process + team (A6 additions) for a total of 13 section types.
        Pre-A6 count: 11 (8 original + gallery + story + lead from Growth-77).
        Post-A6 count: 13 (+process +team). Header comment in catalog.yaml says 15 for
        forward reference (stats type is backlog #2); actual YAML key count is 13.
        """
        sections = catalog["sections"]
        assert "process" in sections, "process must be in catalog after A6 additions"
        assert "team" in sections, "team must be in catalog after A6 additions"
        assert len(sections) == 13, (
            f"Expected 13 section types after A6 additions, got {len(sections)}: "
            f"{sorted(sections.keys())}"
        )

    def test_process_copy_slots(self, catalog):
        process = catalog["sections"]["process"]
        assert "headline" in process["copy_slots"]["required"]
        assert "subhead" in process["copy_slots"].get("optional", [])

    def test_process_item_slots(self, catalog):
        process = catalog["sections"]["process"]
        assert "item_slots" in process
        required = process["item_slots"]["required"]
        assert "title" in required
        optional = process["item_slots"].get("optional", [])
        assert "description" in optional
        assert "step_label" in optional

    def test_process_variants(self, catalog):
        process = catalog["sections"]["process"]
        variants = process.get("variants", [])
        assert "numbered-stack" in variants
        assert "horizontal-steps" in variants
        assert "split-animation" in variants

    def test_team_copy_slots(self, catalog):
        team = catalog["sections"]["team"]
        assert "headline" in team["copy_slots"]["required"]
        assert "subhead" in team["copy_slots"].get("optional", [])

    def test_team_item_slots(self, catalog):
        team = catalog["sections"]["team"]
        assert "item_slots" in team
        required = team["item_slots"]["required"]
        assert "name" in required
        assert "role" in required
        optional = team["item_slots"].get("optional", [])
        assert "bio" in optional
        assert "photo" in optional

    def test_team_variants(self, catalog):
        team = catalog["sections"]["team"]
        variants = team.get("variants", [])
        assert "headshot-grid" in variants
        assert "headshot-list" in variants

    def test_logos_has_quote_band_variant(self, catalog):
        logos = catalog["sections"]["logos"]
        assert "quote-band" in logos.get("variants", [])

    def test_logos_quote_band_copy_slots_additive(self, catalog):
        """quote-band copy slots are additive — eyebrow remains required, new slots optional."""
        logos = catalog["sections"]["logos"]
        assert "eyebrow" in logos["copy_slots"]["required"]
        optional = logos["copy_slots"].get("optional", [])
        for slot in ["quote", "author_name", "author_title", "company"]:
            assert slot in optional, f"logos copy_slots.optional missing '{slot}'"

    def test_logos_existing_variants_unchanged(self, catalog):
        """Existing logos variants must not be broken by quote-band addition."""
        logos = catalog["sections"]["logos"]
        for variant in ["horizontal-scroll", "grid", "marquee-3d"]:
            assert variant in logos.get("variants", []), (
                f"logos variant '{variant}' must still be present"
            )

    def test_original_eight_still_present(self, catalog):
        """All original 8 types remain present after A6 additions."""
        sections = catalog["sections"]
        original = {"hero", "logos", "features", "pricing", "testimonial", "faq", "cta", "footer"}
        assert original.issubset(set(sections.keys()))


# ---------------------------------------------------------------------------
# A6 B2B services: process section — validation + manifest threading
# ---------------------------------------------------------------------------

class TestProcessSection:
    """validate_site + build_site_manifest for process section type (A6)."""

    def _process_site(self, copy, variant=None, items=None):
        section = {"type": "process", "copy": copy}
        if variant:
            section["variant"] = variant
        if items is not None:
            section["items"] = items
        return {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [section],
                }
            ]
        }

    def test_process_numbered_stack_valid(self, catalog):
        items = [
            {"title": "Discovery"},
            {"title": "Design", "description": "We prototype fast."},
            {"title": "Delivery", "description": "Shipped in 4 weeks.", "step_label": "Step 3"},
        ]
        errs = validate_site(
            self._process_site({"headline": "How it works"}, "numbered-stack", items), catalog
        )
        assert errs == [], f"process/numbered-stack should be valid: {errs}"

    def test_process_horizontal_steps_valid(self, catalog):
        items = [
            {"title": "Brief"},
            {"title": "Build"},
            {"title": "Launch"},
        ]
        errs = validate_site(
            self._process_site({"headline": "Our process"}, "horizontal-steps", items), catalog
        )
        assert errs == [], f"process/horizontal-steps should be valid: {errs}"

    def test_process_split_animation_valid(self, catalog):
        items = [{"title": "Onboard"}, {"title": "Configure"}, {"title": "Go live"}]
        errs = validate_site(
            self._process_site({"headline": "How it works"}, "split-animation", items), catalog
        )
        assert errs == [], f"process/split-animation should be valid: {errs}"

    def test_process_missing_headline_rejected(self, catalog):
        errs = validate_site(self._process_site({}), catalog)
        assert any("headline" in e for e in errs)

    def test_process_invalid_variant_rejected(self, catalog):
        errs = validate_site(
            self._process_site({"headline": "Steps"}, variant="no-such-variant"), catalog
        )
        assert any("no-such-variant" in e for e in errs)

    def test_process_item_missing_title_flagged(self, catalog):
        """item missing required 'title' produces a violation."""
        items = [{"description": "No title here"}]
        errs = validate_site(
            self._process_site({"headline": "Steps"}, items=items), catalog
        )
        assert any("title" in e for e in errs), f"Expected 'title' violation, got: {errs}"

    def test_process_no_items_valid(self, catalog):
        """process without items[] is valid (falls back to component demo steps)."""
        errs = validate_site(self._process_site({"headline": "How it works"}), catalog)
        assert errs == [], f"process without items should be valid: {errs}"

    def test_process_items_thread_through_manifest(self):
        """process items[] thread through build_site_manifest verbatim."""
        profile = {
            "customer": {"slug": "b2b-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "studio",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "process",
                                "variant": "numbered-stack",
                                "copy": {"headline": "How it works", "subhead": "Three steps."},
                                "items": [
                                    {"title": "Discovery", "description": "We learn your context."},
                                    {"title": "Design", "description": "We prototype.", "step_label": "02"},
                                    {"title": "Deliver"},
                                ],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        sec = manifest["pages"][0]["sections"][0]
        assert sec["type"] == "process"
        assert sec["variant"] == "numbered-stack"
        assert "items" in sec
        assert len(sec["items"]) == 3
        assert sec["items"][0]["title"] == "Discovery"
        assert sec["items"][0]["description"] == "We learn your context."
        assert sec["items"][1]["step_label"] == "02"
        # optional-only item (title only) still present
        assert sec["items"][2]["title"] == "Deliver"
        assert "description" not in sec["items"][2]


# ---------------------------------------------------------------------------
# A6 B2B services: team section — validation + manifest threading
# ---------------------------------------------------------------------------

class TestTeamSection:
    """validate_site + build_site_manifest for team section type (A6)."""

    def _team_site(self, copy, variant=None, items=None):
        section = {"type": "team", "copy": copy}
        if variant:
            section["variant"] = variant
        if items is not None:
            section["items"] = items
        return {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [section],
                }
            ]
        }

    def test_team_headshot_grid_valid(self, catalog):
        items = [
            {"name": "Alice Kim", "role": "CEO"},
            {"name": "Bob Lee", "role": "CTO", "bio": "20 years in managed services.", "photo": "img/bob.jpg"},
        ]
        errs = validate_site(
            self._team_site({"headline": "Meet the team"}, "headshot-grid", items), catalog
        )
        assert errs == [], f"team/headshot-grid should be valid: {errs}"

    def test_team_headshot_list_valid(self, catalog):
        items = [
            {"name": "Alice Kim", "role": "CEO", "bio": "Leads strategy."},
            {"name": "Bob Lee", "role": "CTO"},
        ]
        errs = validate_site(
            self._team_site({"headline": "Our experts"}, "headshot-list", items), catalog
        )
        assert errs == [], f"team/headshot-list should be valid: {errs}"

    def test_team_no_photo_valid(self, catalog):
        """photo is optional — a team item without photo must still pass validation."""
        items = [
            {"name": "Alice Kim", "role": "CEO"},  # no photo — monogram fallback
            {"name": "Bob Lee", "role": "CTO"},    # no photo
        ]
        errs = validate_site(
            self._team_site({"headline": "Team"}, "headshot-grid", items), catalog
        )
        assert errs == [], f"team item without photo must be valid (monogram fallback): {errs}"

    def test_team_missing_headline_rejected(self, catalog):
        errs = validate_site(self._team_site({}), catalog)
        assert any("headline" in e for e in errs)

    def test_team_invalid_variant_rejected(self, catalog):
        errs = validate_site(
            self._team_site({"headline": "Team"}, variant="unknown-layout"), catalog
        )
        assert any("unknown-layout" in e for e in errs)

    def test_team_item_missing_name_flagged(self, catalog):
        """item missing required 'name' produces a violation."""
        items = [{"role": "Engineer"}]  # name missing
        errs = validate_site(self._team_site({"headline": "Team"}, items=items), catalog)
        assert any("name" in e for e in errs), f"Expected 'name' violation, got: {errs}"

    def test_team_item_missing_role_flagged(self, catalog):
        """item missing required 'role' produces a violation."""
        items = [{"name": "Alice Kim"}]  # role missing
        errs = validate_site(self._team_site({"headline": "Team"}, items=items), catalog)
        assert any("role" in e for e in errs), f"Expected 'role' violation, got: {errs}"

    def test_team_no_items_valid(self, catalog):
        """team without items[] is valid (falls back to component demo cards)."""
        errs = validate_site(self._team_site({"headline": "The team"}), catalog)
        assert errs == [], f"team without items should be valid: {errs}"

    def test_team_items_thread_through_manifest(self):
        """team items[] thread through build_site_manifest; photo absence preserved."""
        profile = {
            "customer": {"slug": "b2b-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "studio",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "team",
                                "variant": "headshot-grid",
                                "copy": {"headline": "Meet the team"},
                                "items": [
                                    {"name": "Alice Kim", "role": "CEO", "photo": "img/alice.jpg"},
                                    {"name": "Bob Lee", "role": "CTO", "bio": "20 years exp."},
                                    {"name": "Cara Mia", "role": "COO"},  # no photo, no bio
                                ],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        sec = manifest["pages"][0]["sections"][0]
        assert sec["type"] == "team"
        assert sec["variant"] == "headshot-grid"
        assert "items" in sec
        assert len(sec["items"]) == 3
        assert sec["items"][0]["name"] == "Alice Kim"
        assert sec["items"][0]["photo"] == "img/alice.jpg"
        assert sec["items"][1]["bio"] == "20 years exp."
        assert "photo" not in sec["items"][1]   # absent in input, absent in output
        assert sec["items"][2]["name"] == "Cara Mia"
        assert "photo" not in sec["items"][2]
        assert "bio" not in sec["items"][2]


# ---------------------------------------------------------------------------
# A6 B2B services: logos/quote-band — validation + manifest threading
# ---------------------------------------------------------------------------

class TestLogosQuoteBand:
    """validate_site + build_site_manifest for logos/quote-band variant (A6)."""

    def _logos_site(self, copy, variant=None):
        section = {"type": "logos", "copy": copy}
        if variant:
            section["variant"] = variant
        return {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [section],
                }
            ]
        }

    def test_logos_quote_band_valid_minimal(self, catalog):
        """logos/quote-band with eyebrow (empty) + quote passes."""
        errs = validate_site(
            self._logos_site(
                {"eyebrow": "", "quote": "They transformed our ops.", "author_name": "Jane Doe"},
                "quote-band",
            ),
            catalog,
        )
        assert errs == [], f"logos/quote-band minimal should be valid: {errs}"

    def test_logos_quote_band_valid_full(self, catalog):
        """logos/quote-band with all optional quote-band slots passes."""
        copy = {
            "eyebrow": "",
            "quote": "Best managed services partner we have worked with.",
            "author_name": "Jane Doe",
            "author_title": "CTO",
            "company": "Acme Corp",
        }
        errs = validate_site(self._logos_site(copy, "quote-band"), catalog)
        assert errs == [], f"logos/quote-band full should be valid: {errs}"

    def test_logos_missing_eyebrow_rejected(self, catalog):
        """logos requires eyebrow (may be empty string but key must be present)."""
        errs = validate_site(
            self._logos_site({"quote": "Great service."}, "quote-band"), catalog
        )
        assert any("eyebrow" in e for e in errs), f"Missing eyebrow must be flagged: {errs}"

    def test_logos_quote_band_invalid_variant_rejected(self, catalog):
        """Confirm quote-band is valid but made-up variant is still rejected."""
        errs = validate_site(
            self._logos_site({"eyebrow": "Clients"}, "not-a-variant"), catalog
        )
        assert any("not-a-variant" in e for e in errs)

    def test_logos_existing_variants_still_valid(self, catalog):
        """All three pre-existing logos variants must still pass after quote-band addition."""
        for variant in ["horizontal-scroll", "grid", "marquee-3d"]:
            errs = validate_site(
                self._logos_site({"eyebrow": "Trusted by"}, variant), catalog
            )
            assert errs == [], f"logos/{variant} must still be valid: {errs}"

    def test_logos_quote_band_copy_threads_through_manifest(self):
        """quote-band copy slots (quote, author_name, etc.) thread verbatim into manifest."""
        profile = {
            "customer": {"slug": "b2b-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "studio",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "logos",
                                "variant": "quote-band",
                                "copy": {
                                    "eyebrow": "",
                                    "quote": "Best partners we have ever had.",
                                    "author_name": "Jane Doe",
                                    "author_title": "CTO",
                                    "company": "Acme Corp",
                                },
                                "assets": ["img/acme-logo.svg"],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        sec = manifest["pages"][0]["sections"][0]
        assert sec["type"] == "logos"
        assert sec["variant"] == "quote-band"
        copy = sec["copy"]
        assert copy["eyebrow"] == ""
        assert copy["quote"] == "Best partners we have ever had."
        assert copy["author_name"] == "Jane Doe"
        assert copy["author_title"] == "CTO"
        assert copy["company"] == "Acme Corp"
        assert "items" not in sec  # logos has no item_slots
