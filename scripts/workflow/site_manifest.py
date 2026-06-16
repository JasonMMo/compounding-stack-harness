"""site_manifest.py — marketing-site manifest builder.

Library function + thin CLI. Part of the creater (orchestrator) axis.
Mirrors manifest.py pattern; handles deliverable_kind=marketing-site profiles.

Usage:
  python scripts/workflow/site_manifest.py --profile agency-demo
  python scripts/workflow/site_manifest.py --profile agency-demo --out out/

Output JSON shape: docs/architecture/site-manifest.md
Single-source: landing-astro adapter reads this; never reimplements section validation.

Invariants:
  - G-1: does NOT reimplement middle contract. contact block yields a wire key reference only.
  - G-8: page.slug and section.type must be ASCII.
  - LLM 0: deterministic, no inference calls.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Repo root: site_manifest.py lives at scripts/workflow/site_manifest.py
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Default catalog path
_DEFAULT_CATALOG_PATH = REPO_ROOT / "presets" / "site-sections" / "catalog.yaml"

# ASCII-only pattern (G-8)
_ASCII_RE = re.compile(r'^[A-Za-z0-9_\-]+$')


# ---------------------------------------------------------------------------
# Catalog loader
# ---------------------------------------------------------------------------

def load_section_catalog(path: Path | str | None = None) -> dict[str, Any]:
    """Load the site-sections catalog YAML.

    Parameters
    ----------
    path:
        Path to catalog.yaml. Defaults to presets/site-sections/catalog.yaml.

    Returns
    -------
    Full catalog dict (top-level keys: version, sections).
    """
    catalog_path = Path(path) if path else _DEFAULT_CATALOG_PATH
    if not catalog_path.exists():
        raise FileNotFoundError(f"Site-sections catalog not found: {catalog_path}")
    with open(catalog_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Site-sections catalog is not a YAML mapping: {catalog_path}")
    return data


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_site(site: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    """Validate the site block against the section catalog.

    Parameters
    ----------
    site:
        The ``site:`` block from a marketing-site profile.
    catalog:
        Section catalog dict as returned by load_section_catalog().

    Returns
    -------
    List of violation messages. Empty list means valid.
    Rules:
      - Each page.slug must be ASCII (G-8).
      - Each section.type must exist in catalog.sections.
      - Each section.type slug must be ASCII (G-8).
      - All copy_slots.required keys must be present in section.copy.
      - section.variant (if set) must appear in catalog variants list.
      - If catalog entry has item_slots AND section.items is present, each item must
        contain all item_slots.required keys. Omitting items entirely is not an error.
      - site.theme existence is a soft/warning check only (P2 incomplete).
    """
    violations: list[str] = []
    sections_catalog: dict[str, Any] = catalog.get("sections", {})

    # Soft check: theme existence
    theme_slug: str = site.get("theme", "")
    if theme_slug:
        theme_yaml = REPO_ROOT / "presets" / "themes" / theme_slug / "theme.yaml"
        if not theme_yaml.exists():
            warnings.warn(
                f"Theme '{theme_slug}' not found at presets/themes/{theme_slug}/theme.yaml "
                f"(P2 incomplete — warning only, not an error)",
                stacklevel=2,
            )

    pages: list[dict[str, Any]] = site.get("pages", [])
    for page in pages:
        page_slug: str = str(page.get("slug", ""))

        # G-8: page slug must be ASCII
        if not _ASCII_RE.match(page_slug):
            violations.append(
                f"page slug '{page_slug}' contains non-ASCII characters (G-8)"
            )

        page_sections: list[dict[str, Any]] = page.get("sections", [])
        for section in page_sections:
            sec_type: str = str(section.get("type", ""))

            # G-8: section type must be ASCII
            if not _ASCII_RE.match(sec_type):
                violations.append(
                    f"page '{page_slug}': section type '{sec_type}' contains "
                    f"non-ASCII characters (G-8)"
                )
                continue

            # section.type must exist in catalog
            if sec_type not in sections_catalog:
                violations.append(
                    f"page '{page_slug}': unknown section type '{sec_type}' "
                    f"(not in presets/site-sections/catalog.yaml)"
                )
                continue

            cat_entry: dict[str, Any] = sections_catalog[sec_type]

            # Determine variant up front so variant_overrides can be applied to both loops.
            variant: str = section.get("variant", "")

            # variant_overrides: per-variant relaxation of normally-required slots.
            # e.g. gallery/grid-2x2 makes src optional; testimonial/pull-quote-wall
            # makes quote/author_name optional (they live in items[] instead).
            variant_overrides: dict[str, Any] = cat_entry.get("variant_overrides", {})
            vo: dict[str, Any] = variant_overrides.get(variant, {})

            copy_slots: dict[str, Any] = cat_entry.get("copy_slots", {})
            required_slots: list[str] = copy_slots.get("required", [])
            # Subtract slots relaxed by this variant from the required set.
            vo_copy_optional: set[str] = set(vo.get("copy_optional", []))
            effective_required_slots = [s for s in required_slots if s not in vo_copy_optional]
            section_copy: dict[str, Any] = section.get("copy") or {}

            # All effective required copy_slots must be present
            for slot in effective_required_slots:
                if slot not in section_copy:
                    violations.append(
                        f"page '{page_slug}' section '{sec_type}': "
                        f"required copy slot '{slot}' is missing"
                    )

            # variant (if set) must be in catalog variants
            if variant:
                cat_variants: list[str] = cat_entry.get("variants", [])
                if variant not in cat_variants:
                    violations.append(
                        f"page '{page_slug}' section '{sec_type}': "
                        f"variant '{variant}' is not in catalog variants {cat_variants}"
                    )

            # item_slots validation: only when catalog has item_slots AND section has items.
            # variant_overrides.item_optional: slots normally required but relaxed for this variant.
            item_slots: dict[str, Any] = cat_entry.get("item_slots", {})
            if item_slots:
                section_items: list[Any] = section.get("items") or []
                required_item_slots: list[str] = item_slots.get("required", [])
                vo_item_optional: set[str] = set(vo.get("item_optional", []))
                effective_item_slots = [s for s in required_item_slots if s not in vo_item_optional]
                for idx, item in enumerate(section_items):
                    for slot in effective_item_slots:
                        if slot not in item:
                            violations.append(
                                f"page '{page_slug}' section '{sec_type}' item[{idx}]: "
                                f"required item slot '{slot}' is missing"
                            )

    return violations


# ---------------------------------------------------------------------------
# Manifest builder
# ---------------------------------------------------------------------------

def build_site_manifest(profile: dict[str, Any]) -> dict[str, Any]:
    """Build a site manifest dict from a marketing-site profile.

    Parameters
    ----------
    profile:
        Full profile dict (loaded via yaml.safe_load). Must contain site: block.

    Returns
    -------
    dict with shape:
      {
        "slug": "<customer.slug>",
        "deliverable_kind": "marketing-site",
        "theme": "<site.theme>",
        "pages": [
          {
            "slug": "<page.slug>",
            "title": "<page.title>",
            "seo": { "title": ..., "description": ..., "og_image": ... (optional) },
            "sections": [
              {
                "type": "<type>",
                "variant": "<variant>",   # omitted if not set
                "copy": { ... },
                "assets": [ ... ],        # omitted if empty/absent
                "cta": { ... },           # omitted if absent
                "items": [ ... ]          # omitted if absent; repeated item entries (features, faq)
              }
            ]
          }
        ],
        "contact": { ... }  # omitted if site.contact absent or disabled
      }

    G-1 invariant: contact block carries only wire key reference metadata.
    No middle contract reimplementation.
    """
    customer_block: dict[str, Any] = profile.get("customer") or {}
    slug: str = customer_block.get("slug", "unknown")

    site: dict[str, Any] = profile.get("site") or {}
    theme: str = site.get("theme", "")

    pages_out: list[dict[str, Any]] = []
    for page in site.get("pages", []):
        seo_raw: dict[str, Any] = page.get("seo") or {}
        seo_out: dict[str, Any] = {}
        if seo_raw.get("title"):
            seo_out["title"] = seo_raw["title"]
        if seo_raw.get("description"):
            seo_out["description"] = seo_raw["description"]
        if seo_raw.get("og_image"):
            seo_out["og_image"] = seo_raw["og_image"]

        sections_out: list[dict[str, Any]] = []
        for section in page.get("sections", []):
            sec_out: dict[str, Any] = {"type": section.get("type", "")}

            variant = section.get("variant", "")
            if variant:
                sec_out["variant"] = variant

            copy_val = section.get("copy")
            if copy_val:
                sec_out["copy"] = dict(copy_val)

            assets_val = section.get("assets")
            if assets_val:
                sec_out["assets"] = list(assets_val)

            cta_val = section.get("cta")
            if cta_val:
                sec_out["cta"] = dict(cta_val)

            items_val = section.get("items")
            if items_val:
                sec_out["items"] = [dict(it) for it in items_val]

            # pills: optional list[str] — used by glowy-waves hero variant.
            pills_val = section.get("pills")
            if pills_val:
                sec_out["pills"] = list(pills_val)

            # stats: optional list[{label, value}] — used by glowy-waves hero variant.
            stats_val = section.get("stats")
            if stats_val:
                sec_out["stats"] = [dict(s) for s in stats_val]

            # images: optional list[str] — used by logos/marquee-3d variant (proof wall).
            images_val = section.get("images")
            if images_val:
                sec_out["images"] = list(images_val)

            # companies: optional list[str] — used by logos/horizontal-scroll for
            # asset-free text wordmark rendering (zero image files, no 404s).
            companies_val = section.get("companies")
            if companies_val:
                sec_out["companies"] = list(companies_val)

            # bento_items: optional list[dict] — used by hero/bento-grid variant.
            # Carries BentoStatItem and BentoMarqueeItem dicts (CDO spec §3).
            # Passed through as-is; no deep validation here (catalog validates shape).
            bento_items_val = section.get("bento_items")
            if bento_items_val:
                sec_out["bento_items"] = [dict(it) for it in bento_items_val]

            # cta_secondary: optional {label, href} — used by hero/bento-grid and
            # other variants that support a second CTA button.
            cta_secondary_val = section.get("cta_secondary")
            if cta_secondary_val:
                sec_out["cta_secondary"] = dict(cta_secondary_val)

            sections_out.append(sec_out)

        page_out: dict[str, Any] = {
            "slug": page.get("slug", ""),
            "title": page.get("title", ""),
        }
        if seo_out:
            page_out["seo"] = seo_out
        page_out["sections"] = sections_out

        pages_out.append(page_out)

    # locale: BCP-47 tag from profile defaults.locale. Falls back to "en-US".
    # Used by frontend adapter to set <html lang="..."> (language subtag only).
    defaults_block: dict[str, Any] = profile.get("defaults") or {}
    locale: str = defaults_block.get("locale") or "en-US"

    manifest: dict[str, Any] = {
        "slug": slug,
        "deliverable_kind": "marketing-site",
        "theme": theme,
        "locale": locale,
        "pages": pages_out,
    }

    # contact block — G-1: wire key reference only, no contract reimplementation.
    # DEC-5: reuse existing entity.create wire key with entity_type "lead".
    # "contact.lead_capture" was a placeholder; entity.create is the correct key.
    contact_raw: dict[str, Any] = site.get("contact") or {}
    if contact_raw.get("enabled"):
        manifest["contact"] = {
            "enabled": True,
            "fields": list(contact_raw.get("fields", [])),
            # wire key: entity.create (wire-v1.yaml, middle contract single source).
            # adapter POSTs to entity.create with entity_type="lead".
            "wire_key": "entity.create",
            "entity_type": "lead",
        }

    return manifest


# ---------------------------------------------------------------------------
# Manifest emitter
# ---------------------------------------------------------------------------

def emit_site_manifest(
    profile: dict[str, Any],
    slug: str,
    out_dir: Path,
) -> Path:
    """Validate + build + write out/<slug>/site-manifest.json.

    Parameters
    ----------
    profile:
        Full profile dict.
    slug:
        Customer profile slug (used for output path).
    out_dir:
        Root output directory (e.g. repo_root/out).

    Returns
    -------
    Path to the written site-manifest.json.

    Exits with rc=1 (via sys.exit) if validate_site returns any violations.
    """
    site: dict[str, Any] = profile.get("site") or {}

    # Load section catalog
    catalog = load_section_catalog()

    # Validate
    violations = validate_site(site, catalog)
    if violations:
        print("ERROR: site block validation failed:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        sys.exit(1)

    # Build manifest
    manifest = build_site_manifest(profile)

    # Write output
    site_out_dir = out_dir / slug
    site_out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = site_out_dir / "site-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit site manifest JSON from a marketing-site customer profile."
    )
    parser.add_argument("--profile", required=True, help="Customer profile slug.")
    parser.add_argument(
        "--out", default=None,
        help="Output root directory. Default: out/ (repo root).",
    )
    args = parser.parse_args(argv)

    profiles_dir = REPO_ROOT / "profiles"
    profile_path = profiles_dir / f"{args.profile}.yaml"
    if not profile_path.exists():
        print(f"ERROR: Profile not found: {profile_path}", file=sys.stderr)
        return 1

    with open(profile_path, encoding="utf-8") as f:
        profile = yaml.safe_load(f)

    out_root = Path(args.out).resolve() if args.out else REPO_ROOT / "out"

    manifest_path = emit_site_manifest(profile, args.profile, out_root)

    print(f"site-manifest complete — profile: {args.profile}")
    print(f"  manifest output: {manifest_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
