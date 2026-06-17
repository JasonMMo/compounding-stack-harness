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
        """src is optional for parallax-scroll via variant_overrides (Growth-83).
        When src is absent the component renders a theme material-texture field.
        validate_site must NOT raise a violation for missing src on parallax-scroll."""
        items = [{"alt": "Chapter 1", "heading": "The Craft"}]  # src absent
        site = self._parallax_site(items)
        errs = validate_site(site, catalog)
        assert errs == [], (
            "parallax-scroll with no src must pass (variant_overrides relaxes src): "
            f"{errs}"
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

    def test_catalog_has_process_team_and_fourteen_total(self, catalog):
        """Catalog must contain process + team (A6) + stats (A1/Growth-80) section types.
        Pre-A6 count: 11 (8 original + gallery + story + lead from Growth-77).
        Post-A6 count: 13 (+process +team).
        Post-A1 count: 14 (+stats — Growth-80 ticker-band, was backlog #2).
        """
        sections = catalog["sections"]
        assert "process" in sections, "process must be in catalog after A6 additions"
        assert "team" in sections, "team must be in catalog after A6 additions"
        assert "stats" in sections, "stats must be in catalog after Growth-80 (A1 FLUX)"
        assert len(sections) == 14, (
            f"Expected 14 section types after A1 stats addition, got {len(sections)}: "
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


# ---------------------------------------------------------------------------
# A5 Mobile App: variant_overrides slot relaxation (Growth-83, closes P2)
# ---------------------------------------------------------------------------

class TestVariantOverrides:
    """validate_site respects catalog variant_overrides for item_optional and copy_optional.

    Rules:
      1. gallery/grid-2x2 with items lacking src → NO violation (src relaxed for this variant).
      2. gallery/masonry-3col with items lacking src → violation (relaxation is variant-scoped).
      3. testimonial/pull-quote-wall with copy missing quote/author_name → NO violation.
      4. testimonial/single-card missing quote → violation (relaxation is variant-scoped).
    """

    def _gallery_site(self, variant, items):
        return {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "gallery",
                            "variant": variant,
                            "copy": {"headline": "Gallery"},
                            "items": items,
                        }
                    ],
                }
            ]
        }

    def _testimonial_site(self, variant, copy):
        return {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [
                        {
                            "type": "testimonial",
                            "variant": variant,
                            "copy": copy,
                        }
                    ],
                }
            ]
        }

    # ── Rule 1: gallery/grid-2x2 src-absent items pass ──────────────────────

    def test_grid_2x2_items_without_src_no_violation(self, catalog):
        """gallery/grid-2x2 with items that have only alt → no violation.
        src is relaxed for grid-2x2 via variant_overrides.item_optional."""
        items = [
            {"alt": "Today screen"},
            {"alt": "Insights screen"},
            {"alt": "Focus screen"},
            {"alt": "Profile screen"},
        ]
        errs = validate_site(self._gallery_site("grid-2x2", items), catalog)
        assert errs == [], (
            f"gallery/grid-2x2 items without src must pass (variant_overrides): {errs}"
        )

    def test_grid_2x2_items_with_src_still_valid(self, catalog):
        """gallery/grid-2x2 with src present must also pass (src is optional, not forbidden)."""
        items = [{"src": "img/a.jpg", "alt": "Screen A"}]
        errs = validate_site(self._gallery_site("grid-2x2", items), catalog)
        assert errs == [], f"grid-2x2 with src should still be valid: {errs}"

    def test_grid_2x2_items_without_alt_still_violation(self, catalog):
        """gallery/grid-2x2 items missing alt (not relaxed) must still be flagged."""
        items = [{"caption": "Today"}]  # neither src nor alt
        errs = validate_site(self._gallery_site("grid-2x2", items), catalog)
        assert any("alt" in e for e in errs), (
            f"alt is not relaxed for grid-2x2 — must still be flagged: {errs}"
        )

    # ── Rule 2: gallery/masonry-3col src-absent items fail ───────────────────

    def test_masonry_3col_items_without_src_violation(self, catalog):
        """gallery/masonry-3col with items lacking src → violation.
        Relaxation is variant-scoped to grid-2x2 and parallax-scroll only."""
        items = [{"alt": "Image A"}]  # src absent, variant is masonry-3col
        errs = validate_site(self._gallery_site("masonry-3col", items), catalog)
        assert any("src" in e for e in errs), (
            f"gallery/masonry-3col must still require src (no variant_override): {errs}"
        )

    def test_full_bleed_strip_items_without_src_violation(self, catalog):
        """gallery/full-bleed-strip with items lacking src → violation (not relaxed)."""
        items = [{"alt": "Hero image"}]  # src absent
        errs = validate_site(self._gallery_site("full-bleed-strip", items), catalog)
        assert any("src" in e for e in errs), (
            f"gallery/full-bleed-strip must still require src: {errs}"
        )

    # ── Rule 3: testimonial/pull-quote-wall missing quote/author_name pass ───

    def test_pull_quote_wall_missing_copy_no_violation(self, catalog):
        """testimonial/pull-quote-wall with copy missing quote and author_name → no violation.
        These slots are relaxed via variant_overrides.copy_optional for pull-quote-wall
        (quotes live in items[], not section-level copy)."""
        copy = {}  # both quote and author_name absent
        errs = validate_site(self._testimonial_site("pull-quote-wall", copy), catalog)
        assert errs == [], (
            f"testimonial/pull-quote-wall must pass without quote/author_name: {errs}"
        )

    def test_pull_quote_wall_with_copy_still_valid(self, catalog):
        """testimonial/pull-quote-wall with quote/author_name present must also pass."""
        copy = {"quote": "Transformative.", "author_name": "Jane D."}
        errs = validate_site(self._testimonial_site("pull-quote-wall", copy), catalog)
        assert errs == [], f"pull-quote-wall with copy should still pass: {errs}"

    # ── Rule 4: testimonial/single-card missing quote is a violation ─────────

    def test_single_card_missing_quote_violation(self, catalog):
        """testimonial/single-card with copy missing quote → violation.
        Relaxation is variant-scoped to pull-quote-wall; single-card is unchanged."""
        copy = {"author_name": "Jane D."}  # quote missing
        errs = validate_site(self._testimonial_site("single-card", copy), catalog)
        assert any("quote" in e for e in errs), (
            f"testimonial/single-card must still require quote: {errs}"
        )

    def test_single_card_missing_author_name_violation(self, catalog):
        """testimonial/single-card missing author_name → violation (not relaxed)."""
        copy = {"quote": "Great product."}  # author_name missing
        errs = validate_site(self._testimonial_site("single-card", copy), catalog)
        assert any("author_name" in e for e in errs), (
            f"testimonial/single-card must still require author_name: {errs}"
        )


# ---------------------------------------------------------------------------
# A7 API Platform: hero/bento-grid variant (Growth-84+)
# ---------------------------------------------------------------------------

class TestHeroBentoGrid:
    """Catalog and manifest threading tests for hero/bento-grid (A7 archetype)."""

    def _bento_site(self, copy=None, variant="bento-grid", bento_items=None, cta_secondary=None):
        section = {
            "type": "hero",
            "variant": variant,
            "copy": copy or {"headline": "Know your API.", "subhead": "Real-time visibility."},
        }
        if bento_items is not None:
            section["bento_items"] = bento_items
        if cta_secondary is not None:
            section["cta_secondary"] = cta_secondary
        return {
            "pages": [
                {
                    "slug": "home",
                    "title": "Home",
                    "sections": [section],
                }
            ]
        }

    # ── Catalog: variant registered ──────────────────────────────────────────

    def test_bento_grid_in_hero_variants(self, catalog):
        """bento-grid must appear in hero.variants (catalog registered)."""
        hero = catalog["sections"]["hero"]
        assert "bento-grid" in hero.get("variants", []), (
            "hero.variants must contain 'bento-grid'"
        )

    def test_bento_grid_does_not_break_other_variants(self, catalog):
        """All pre-existing hero variants must still be in the catalog."""
        hero = catalog["sections"]["hero"]
        original_variants = [
            "centered", "split-left", "split-right",
            "fullscreen-video", "glowy-waves", "brew", "headline-only",
        ]
        for v in original_variants:
            assert v in hero.get("variants", []), (
                f"Pre-existing hero variant '{v}' must still be in catalog"
            )

    def test_hero_catalog_has_variant_overrides(self, catalog):
        """hero catalog entry must have variant_overrides for bento-grid."""
        hero = catalog["sections"]["hero"]
        assert "variant_overrides" in hero, "hero must have variant_overrides"
        assert "bento-grid" in hero["variant_overrides"], (
            "bento-grid must appear in hero.variant_overrides"
        )

    # ── Validation: bento-grid accepts valid section ─────────────────────────

    def test_bento_grid_valid_with_required_copy(self, catalog):
        """hero/bento-grid with headline + subhead must pass validation."""
        errs = validate_site(self._bento_site(), catalog)
        assert errs == [], f"hero/bento-grid with required copy must be valid: {errs}"

    def test_bento_grid_with_badge_valid(self, catalog):
        """Badge (optional copy slot) must not cause a violation."""
        copy = {
            "headline": "Know your API.",
            "subhead": "Real-time visibility.",
            "badge": "API Observability Platform",
        }
        errs = validate_site(self._bento_site(copy=copy), catalog)
        assert errs == [], f"hero/bento-grid with badge should be valid: {errs}"

    def test_bento_grid_missing_subhead_rejected(self, catalog):
        """hero/bento-grid missing required subhead → violation."""
        copy = {"headline": "Know your API."}
        errs = validate_site(self._bento_site(copy=copy), catalog)
        assert any("subhead" in e for e in errs), (
            f"Missing subhead must be flagged for bento-grid: {errs}"
        )

    def test_bento_grid_missing_headline_rejected(self, catalog):
        """hero/bento-grid missing required headline → violation."""
        copy = {"subhead": "Real-time visibility."}
        errs = validate_site(self._bento_site(copy=copy), catalog)
        assert any("headline" in e for e in errs), (
            f"Missing headline must be flagged for bento-grid: {errs}"
        )

    # ── Manifest threading: bento_items[] passthrough ────────────────────────

    def test_bento_items_thread_through_manifest(self):
        """bento_items[] from profile must appear in manifest section output."""
        stat_card = {
            "type": "stat",
            "icon_label": "API requests tracked",
            "primary_value": "847M",
            "primary_label": "Requests monitored today",
            "progress_label": "Error budget consumed",
            "progress_value": 4,
            "progress_max": 100,
            "mini_stats": [
                {"value": "99.97%", "label": "Uptime"},
                {"value": "12ms", "label": "P50"},
            ],
            "tags": [{"label": "All systems operational", "status": "ok"}],
        }
        marquee_card = {
            "type": "marquee",
            "eyebrow": "Used by platform teams at",
            "companies": ["Acme Platform", "Vortex Systems"],
        }
        profile = {
            "customer": {"slug": "prism-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "prism",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "hero",
                                "variant": "bento-grid",
                                "copy": {
                                    "headline": "Know your API.",
                                    "subhead": "Real-time visibility.",
                                    "badge": "API Observability Platform",
                                },
                                "cta": {"label": "Start free", "href": "#contact"},
                                "cta_secondary": {"label": "Read the docs", "href": "#docs"},
                                "bento_items": [stat_card, marquee_card],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        hero_sec = manifest["pages"][0]["sections"][0]
        assert hero_sec["variant"] == "bento-grid"
        assert "bento_items" in hero_sec, "bento_items must thread through manifest"
        assert len(hero_sec["bento_items"]) == 2
        assert hero_sec["bento_items"][0]["type"] == "stat"
        assert hero_sec["bento_items"][0]["primary_value"] == "847M"
        assert hero_sec["bento_items"][1]["type"] == "marquee"
        assert "Acme Platform" in hero_sec["bento_items"][1]["companies"]

    def test_cta_secondary_threads_through_manifest(self):
        """cta_secondary from profile must appear in manifest section output."""
        profile = {
            "customer": {"slug": "prism-co"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "prism",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "hero",
                                "variant": "bento-grid",
                                "copy": {
                                    "headline": "Know your API.",
                                    "subhead": "Real-time visibility.",
                                },
                                "cta": {"label": "Start free", "href": "#contact"},
                                "cta_secondary": {"label": "Read the docs", "href": "#docs"},
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        hero_sec = manifest["pages"][0]["sections"][0]
        assert "cta_secondary" in hero_sec, "cta_secondary must thread through manifest"
        assert hero_sec["cta_secondary"]["label"] == "Read the docs"
        assert hero_sec["cta_secondary"]["href"] == "#docs"

    def test_hero_bento_grid_no_bento_items_still_valid(self, catalog):
        """hero/bento-grid with no bento_items[] must still validate (items are optional)."""
        errs = validate_site(self._bento_site(), catalog)
        assert errs == [], (
            f"hero/bento-grid without bento_items must still be valid: {errs}"
        )

    def test_prism_demo_profile_validates(self, catalog):
        """prism-demo.yaml must validate cleanly against the catalog."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")
        profile_path = PROFILES_DIR / "prism-demo.yaml"
        if not profile_path.exists():
            pytest.skip("prism-demo.yaml not found")
        with open(profile_path, encoding="utf-8") as f:
            profile = yaml.safe_load(f)
        site = profile.get("site", {})
        errs = validate_site(site, catalog)
        assert errs == [], f"prism-demo.yaml site block has violations: {errs}"

    def test_prism_demo_manifest_has_bento_items(self):
        """prism-demo build_site_manifest output must include bento_items in hero section."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")
        profile_path = PROFILES_DIR / "prism-demo.yaml"
        if not profile_path.exists():
            pytest.skip("prism-demo.yaml not found")
        with open(profile_path, encoding="utf-8") as f:
            profile = yaml.safe_load(f)
        manifest = build_site_manifest(profile)
        home = next((p for p in manifest["pages"] if p["slug"] == "home"), None)
        assert home is not None
        hero = next((s for s in home["sections"] if s["type"] == "hero"), None)
        assert hero is not None
        assert hero.get("variant") == "bento-grid"
        assert "bento_items" in hero, "hero bento-grid section must have bento_items in manifest"
        stat = next((it for it in hero["bento_items"] if it.get("type") == "stat"), None)
        marquee = next((it for it in hero["bento_items"] if it.get("type") == "marquee"), None)
        assert stat is not None, "stat card must be in bento_items"
        assert stat["primary_value"] == "847M"
        assert marquee is not None, "marquee card must be in bento_items"
        assert "Acme Platform" in marquee["companies"]


# ---------------------------------------------------------------------------
# Growth-85: process/split-animation — validation + manifest threading
# ---------------------------------------------------------------------------

class TestProcessSplitAnimation:
    """validate_site + build_site_manifest for process/split-animation variant.

    Covers:
      (a) Catalog: split-animation variant registered.
      (b) Validation: valid split-animation section passes.
      (c) Validation: status enum values accepted (completed/active/upcoming).
      (d) Validation: subtasks with required title pass; missing title fails.
      (e) Manifest threading: subtasks + status + tools pass through verbatim.
      (f) SSR contract: section emits items[] in manifest (component handles display).
      (g) flux-demo.yaml profile validates cleanly (contains split-animation).
      (h) flux-demo manifest contains split-animation process section.
    """

    def _split_site(self, copy, items=None):
        section = {"type": "process", "variant": "split-animation", "copy": copy}
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

    # ── (a) Catalog: variant registered ─────────────────────────────────────

    def test_split_animation_in_process_variants(self, catalog):
        """split-animation must appear in process.variants."""
        process = catalog["sections"]["process"]
        assert "split-animation" in process.get("variants", []), (
            "process.variants must contain 'split-animation'"
        )

    def test_catalog_process_item_slots_has_status_and_subtasks(self, catalog):
        """item_slots.optional must include status and subtasks (Growth-85 extension)."""
        process = catalog["sections"]["process"]
        optional = process["item_slots"].get("optional", [])
        assert "status" in optional, "item_slots.optional must contain 'status'"
        assert "subtasks" in optional, "item_slots.optional must contain 'subtasks'"

    # ── (b) Validation: valid split-animation passes ─────────────────────────

    def test_split_animation_minimal_valid(self, catalog):
        """process/split-animation with headline and items[title] passes."""
        items = [
            {"title": "소스 연결", "status": "completed"},
            {"title": "SLO 정의", "status": "active"},
            {"title": "배포", "status": "upcoming"},
        ]
        errs = validate_site(
            self._split_site({"headline": "도입 단계"}, items), catalog
        )
        assert errs == [], f"split-animation minimal should be valid: {errs}"

    def test_split_animation_no_items_valid(self, catalog):
        """process/split-animation without items[] is valid (component uses demo fallback)."""
        errs = validate_site(
            self._split_site({"headline": "도입 단계"}), catalog
        )
        assert errs == [], f"split-animation without items must be valid: {errs}"

    def test_split_animation_missing_headline_rejected(self, catalog):
        """process/split-animation missing headline → violation."""
        errs = validate_site(self._split_site({}), catalog)
        assert any("headline" in e for e in errs), (
            f"Missing headline must be flagged: {errs}"
        )

    # ── (c) Status enum accepted ─────────────────────────────────────────────

    def test_split_animation_all_status_values_valid(self, catalog):
        """All three status values (completed/active/upcoming) pass item_slots validation."""
        items = [
            {"title": "완료된 단계", "status": "completed"},
            {"title": "진행 중 단계", "status": "active"},
            {"title": "예정 단계", "status": "upcoming"},
        ]
        errs = validate_site(
            self._split_site({"headline": "단계"}, items), catalog
        )
        assert errs == [], f"All status values must be accepted: {errs}"

    # ── (d) Subtasks: required title; missing title fails ────────────────────

    def test_split_animation_with_subtasks_valid(self, catalog):
        """Items with subtasks[] pass when subtask has title (required)."""
        items = [
            {
                "title": "소스 연결",
                "status": "completed",
                "subtasks": [
                    {"title": "커넥터 설정", "status": "completed"},
                    {
                        "title": "스키마 검증",
                        "description": "스키마 트리가 올바르게 매핑됐는지 확인합니다.",
                        "status": "completed",
                        "tools": ["schema-explorer", "cli"],
                    },
                ],
            }
        ]
        errs = validate_site(
            self._split_site({"headline": "단계"}, items), catalog
        )
        assert errs == [], f"Items with valid subtasks must pass: {errs}"

    def test_split_animation_item_missing_title_flagged(self, catalog):
        """process/split-animation item missing required 'title' → violation."""
        items = [{"description": "설명만 있고 title 없음", "status": "active"}]
        errs = validate_site(
            self._split_site({"headline": "단계"}, items), catalog
        )
        assert any("title" in e for e in errs), (
            f"Missing item title must be flagged: {errs}"
        )

    # ── (e) Manifest threading: subtasks + status + tools ───────────────────

    def test_split_animation_subtasks_thread_through_manifest(self):
        """subtasks[], status, tools thread verbatim through build_site_manifest."""
        profile = {
            "customer": {"slug": "flux-test"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "flux",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "process",
                                "variant": "split-animation",
                                "copy": {
                                    "headline": "도입 단계",
                                    "subhead": "4단계로 완성합니다.",
                                },
                                "items": [
                                    {
                                        "title": "소스 연결",
                                        "description": "Kafka, S3 등을 연결합니다.",
                                        "status": "completed",
                                        "subtasks": [
                                            {
                                                "title": "커넥터 설정",
                                                "description": "YAML 작성.",
                                                "status": "completed",
                                                "tools": ["flux-connector", "cli"],
                                            },
                                            {
                                                "title": "스키마 검증",
                                                "status": "completed",
                                            },
                                        ],
                                    },
                                    {
                                        "title": "SLO 정의",
                                        "status": "active",
                                        "subtasks": [
                                            {"title": "SLO 기준값 수집", "status": "completed"},
                                            {"title": "규칙 작성", "status": "active", "tools": ["flux-slo-editor"]},
                                        ],
                                    },
                                    {
                                        "title": "배포",
                                        "status": "upcoming",
                                    },
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
        assert sec["variant"] == "split-animation"
        assert "items" in sec
        items = sec["items"]
        assert len(items) == 3

        # Item 0: completed with subtasks + tools
        item0 = items[0]
        assert item0["title"] == "소스 연결"
        assert item0["status"] == "completed"
        assert "subtasks" in item0
        assert len(item0["subtasks"]) == 2
        sub0 = item0["subtasks"][0]
        assert sub0["title"] == "커넥터 설정"
        assert sub0["status"] == "completed"
        assert "tools" in sub0
        assert "flux-connector" in sub0["tools"]
        assert "cli" in sub0["tools"]
        sub1 = item0["subtasks"][1]
        assert sub1["title"] == "스키마 검증"
        assert "tools" not in sub1  # tools absent in input → absent in output

        # Item 1: active with mixed subtask statuses
        item1 = items[1]
        assert item1["status"] == "active"
        assert item1["subtasks"][1]["status"] == "active"
        assert "flux-slo-editor" in item1["subtasks"][1]["tools"]

        # Item 2: upcoming, no subtasks
        item2 = items[2]
        assert item2["title"] == "배포"
        assert item2["status"] == "upcoming"
        assert "subtasks" not in item2

    def test_split_animation_copy_threads_through_manifest(self):
        """copy.subhead for split-animation threads into manifest."""
        profile = {
            "customer": {"slug": "flux-test"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "flux",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "process",
                                "variant": "split-animation",
                                "copy": {
                                    "headline": "4단계",
                                    "subhead": "간단한 도입 절차입니다.",
                                },
                                "items": [{"title": "시작"}],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        sec = manifest["pages"][0]["sections"][0]
        assert sec["copy"]["headline"] == "4단계"
        assert sec["copy"]["subhead"] == "간단한 도입 절차입니다."

    # ── (f) SSR contract: items emitted ──────────────────────────────────────

    def test_split_animation_items_key_present_in_manifest(self):
        """process/split-animation section must emit items[] key when items are provided."""
        profile = {
            "customer": {"slug": "flux-test"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "flux",
                "pages": [
                    {
                        "slug": "home",
                        "title": "Home",
                        "sections": [
                            {
                                "type": "process",
                                "variant": "split-animation",
                                "copy": {"headline": "단계"},
                                "items": [{"title": "Step 1"}],
                            }
                        ],
                    }
                ],
            },
        }
        manifest = build_site_manifest(profile)
        sec = manifest["pages"][0]["sections"][0]
        assert "items" in sec, "items[] must be present in manifest when provided"
        assert len(sec["items"]) == 1
        assert sec["items"][0]["title"] == "Step 1"

    # ── (g) flux-demo.yaml validates cleanly ─────────────────────────────────

    def test_flux_demo_profile_validates(self, catalog):
        """flux-demo.yaml (with split-animation process section) must validate cleanly."""
        try:
            import yaml as _yaml
        except ImportError:
            pytest.skip("PyYAML not available")
        path = PROFILES_DIR / "flux-demo.yaml"
        if not path.exists():
            pytest.skip("flux-demo.yaml not found")
        with open(path, encoding="utf-8") as f:
            profile = _yaml.safe_load(f)
        site = profile.get("site", {})
        errs = validate_site(site, catalog)
        assert errs == [], f"flux-demo.yaml site block has violations: {errs}"

    # ── (h) flux-demo manifest contains split-animation process section ──────

    def test_flux_demo_manifest_has_split_animation_process(self):
        """flux-demo build_site_manifest output must include process/split-animation."""
        try:
            import yaml as _yaml
        except ImportError:
            pytest.skip("PyYAML not available")
        path = PROFILES_DIR / "flux-demo.yaml"
        if not path.exists():
            pytest.skip("flux-demo.yaml not found")
        with open(path, encoding="utf-8") as f:
            profile = _yaml.safe_load(f)
        manifest = build_site_manifest(profile)
        home = next((p for p in manifest["pages"] if p["slug"] == "home"), None)
        assert home is not None
        process_sec = next(
            (s for s in home["sections"]
             if s["type"] == "process" and s.get("variant") == "split-animation"),
            None,
        )
        assert process_sec is not None, (
            "home page must have process/split-animation section in manifest"
        )
        assert "items" in process_sec
        assert len(process_sec["items"]) >= 3
        # First item: completed
        item0 = process_sec["items"][0]
        assert item0.get("status") == "completed"
        assert "subtasks" in item0
        assert len(item0["subtasks"]) >= 2
        # Second item: active
        item1 = process_sec["items"][1]
        assert item1.get("status") == "active"
        # Tools present in subtasks
        tools_found = any(
            "tools" in sub
            for item in process_sec["items"]
            for sub in item.get("subtasks", [])
        )
        assert tools_found, "At least one subtask must have tools[] in flux-demo"


# ---------------------------------------------------------------------------
# Growth-86: locale field — build_site_manifest emits manifest['locale']
# ---------------------------------------------------------------------------

class TestLocaleEmit:
    """(a) profile with defaults.locale=ko-KR → manifest['locale']=='ko-KR'.
    (b) profile without defaults block → manifest['locale']=='en-US' (default).
    (c) profile with defaults block but no locale key → 'en-US' default.
    """

    def _minimal_profile(self, defaults=None):
        profile: dict = {
            "customer": {"slug": "test-locale"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": {
                "theme": "aurora",
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
                ],
            },
        }
        if defaults is not None:
            profile["defaults"] = defaults
        return profile

    def test_locale_ko_kr_emitted(self):
        """(a) defaults.locale=ko-KR → manifest['locale']=='ko-KR'."""
        profile = self._minimal_profile(defaults={"locale": "ko-KR", "timezone": "Asia/Seoul"})
        manifest = build_site_manifest(profile)
        assert "locale" in manifest, "manifest must contain 'locale' key"
        assert manifest["locale"] == "ko-KR", (
            f"Expected 'ko-KR', got '{manifest['locale']}'"
        )

    def test_locale_default_when_no_defaults_block(self):
        """(b) profile without defaults block → manifest['locale']=='en-US'."""
        profile = self._minimal_profile(defaults=None)
        manifest = build_site_manifest(profile)
        assert "locale" in manifest, "manifest must contain 'locale' key"
        assert manifest["locale"] == "en-US", (
            f"Expected 'en-US' default, got '{manifest['locale']}'"
        )

    def test_locale_default_when_locale_key_absent(self):
        """(c) defaults block present but no locale key → 'en-US' default."""
        profile = self._minimal_profile(defaults={"timezone": "UTC"})
        manifest = build_site_manifest(profile)
        assert manifest["locale"] == "en-US", (
            f"Expected 'en-US' when locale key absent, got '{manifest['locale']}'"
        )

    def test_locale_en_us_explicit(self):
        """Explicit en-US passes through unchanged."""
        profile = self._minimal_profile(defaults={"locale": "en-US"})
        manifest = build_site_manifest(profile)
        assert manifest["locale"] == "en-US"

    def test_gtm_landing_locale_ko_kr(self):
        """gtm-landing.yaml (defaults.locale=ko-KR) → manifest locale is ko-KR."""
        try:
            import yaml as _yaml
        except ImportError:
            pytest.skip("PyYAML not available")
        path = PROFILES_DIR / "gtm-landing.yaml"
        if not path.exists():
            pytest.skip("gtm-landing.yaml not found")
        with open(path, encoding="utf-8") as f:
            profile = _yaml.safe_load(f)
        manifest = build_site_manifest(profile)
        assert manifest.get("locale") == "ko-KR", (
            f"gtm-landing manifest locale must be 'ko-KR', got '{manifest.get('locale')}'"
        )


# ---------------------------------------------------------------------------
# Growth-87: scroll_mode + motion emit + validation + 3-variant dispatch
# ---------------------------------------------------------------------------

class TestScrollModeMotionEmit:
    def _profile(self, scroll_mode=None, motion=None):
        site = {
            "theme": "aurora",
            "pages": [{
                "slug": "home",
                "title": "Home",
                "sections": [{
                    "type": "hero",
                    "copy": {"headline": "H", "subhead": "S"},
                }],
            }],
        }
        if scroll_mode is not None:
            site["scroll_mode"] = scroll_mode
        if motion is not None:
            site["motion"] = motion
        return {
            "customer": {"slug": "test-motion"},
            "stack": {"deliverable_kind": "marketing-site"},
            "site": site,
        }

    def test_scroll_mode_snap_emitted(self, catalog):
        profile = self._profile(scroll_mode="snap", motion="subtle")
        manifest = build_site_manifest(profile)
        assert manifest["scroll_mode"] == "snap"

    def test_motion_subtle_emitted(self, catalog):
        profile = self._profile(scroll_mode="snap", motion="subtle")
        manifest = build_site_manifest(profile)
        assert manifest["motion"] == "subtle"

    def test_motion_rich_emitted(self, catalog):
        profile = self._profile(motion="rich")
        manifest = build_site_manifest(profile)
        assert manifest["motion"] == "rich"

    def test_defaults_normal_off_when_absent(self, catalog):
        profile = self._profile()
        manifest = build_site_manifest(profile)
        assert manifest["scroll_mode"] == "normal", manifest.get("scroll_mode")
        assert manifest["motion"] == "off", manifest.get("motion")

    def test_invalid_scroll_mode_rejected(self, catalog):
        profile = self._profile(scroll_mode="fullpage")
        violations = validate_site(profile["site"], catalog)
        assert any("scroll_mode" in v for v in violations), violations

    def test_invalid_motion_rejected(self, catalog):
        profile = self._profile(motion="max")
        violations = validate_site(profile["site"], catalog)
        assert any("motion" in v for v in violations), violations

    def test_valid_scroll_motion_combinations(self, catalog):
        for sm in ("normal", "snap"):
            for m in ("off", "subtle", "rich"):
                profile = self._profile(scroll_mode=sm, motion=m)
                violations = validate_site(profile["site"], catalog)
                assert not violations, f"scroll_mode={sm} motion={m}: {violations}"

    def test_gtm_landing_snap_subtle(self, catalog):
        try:
            import yaml as _yaml
        except ImportError:
            import pytest
            pytest.skip("PyYAML not available")
        path = PROFILES_DIR / "gtm-landing.yaml"
        if not path.exists():
            import pytest
            pytest.skip("gtm-landing.yaml not found")
        with open(path, encoding="utf-8") as f:
            profile = _yaml.safe_load(f)
        manifest = build_site_manifest(profile)
        assert manifest["scroll_mode"] == "snap", manifest.get("scroll_mode")
        assert manifest["motion"] == "subtle", manifest.get("motion")


class TestMotionVariantDispatch:
    def _site(self, sec_type, variant, copy, items=None):
        section = {"type": sec_type, "variant": variant, "copy": copy}
        if items:
            section["items"] = items
        return {
            "theme": "aurora",
            "scroll_mode": "snap",
            "motion": "subtle",
            "pages": [{
                "slug": "home",
                "title": "Home",
                "sections": [section],
            }],
        }

    def test_hero_scroll_reveal_valid(self, catalog):
        site = self._site("hero", "scroll-reveal",
                          {"headline": "테스트", "subhead": "서브"})
        violations = validate_site(site, catalog)
        assert not violations, violations

    def test_gallery_full_bleed_strip_valid(self, catalog):
        site = self._site("gallery", "full-bleed-strip",
                          {"headline": "갤러리"},
                          items=[{"src": "/img.jpg", "alt": "설명"}])
        violations = validate_site(site, catalog)
        assert not violations, violations

    def test_stats_pinned_staged_valid(self, catalog):
        site = self._site("stats", "pinned-staged",
                          {"headline": "지표"},
                          items=[{"value": "14+", "label": "도메인"}])
        violations = validate_site(site, catalog)
        assert not violations, violations

    def test_gtm_landing_profile_valid(self, catalog):
        try:
            import yaml as _yaml
        except ImportError:
            import pytest
            pytest.skip("PyYAML not available")
        path = PROFILES_DIR / "gtm-landing.yaml"
        if not path.exists():
            import pytest
            pytest.skip("gtm-landing.yaml not found")
        with open(path, encoding="utf-8") as f:
            profile = _yaml.safe_load(f)
        violations = validate_site(profile["site"], catalog)
        assert not violations, violations
