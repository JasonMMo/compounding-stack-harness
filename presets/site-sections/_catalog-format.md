# Site-Sections Catalog Format

> `presets/site-sections/catalog.yaml` is the single source of truth for marketing-site section types.
> `scripts/workflow/site_manifest.py` validates every `site.pages[].sections[]` entry against it.
> Pattern mirrors `presets/ddl/_catalog-format.md` — machine truth, not human narrative.

## 1. File Structure

```
presets/site-sections/
  _catalog-format.md        # this document (format single source)
  catalog.yaml              # 8 section types
```

## 2. Section Entry Schema

```yaml
version: "1.0"
sections:
  <type-slug>:              # ASCII slug, e.g. hero, features, cta
    label: "Human Label"    # display name for tooling / docs
    copy_slots:
      required: [headline, subhead]   # keys that MUST be present in section.copy{}
      optional: [supporting_text]     # keys that MAY be present
    asset_slots: [bg_image]           # asset ref names expected; empty list = none
    variants: [centered, split-left]  # valid values for section.variant (optional field)
```

**type-slug**: ASCII slug. Must be unique within the catalog. Used as `section.type` in profile `site.pages[].sections[]`.

**copy_slots.required**: `validate_site()` raises an error if any required key is absent from `section.copy{}`.

**copy_slots.optional**: listed for documentation; validation does not check for them.

**asset_slots**: informational — lists expected `assets[]` entries. Validation does not enforce presence (assets are always optional at schema level; theme/CDO may enforce at render time).

**variants**: valid choices for `section.variant`. If the profile sets a variant not in this list, `validate_site()` raises an error.

## 3. Profile site.pages[].sections[] Shape

```yaml
site:
  pages:
    - slug: home
      title: "Home"
      seo:
        title: "..."
        description: "..."
        og_image: "..."          # optional
      sections:
        - type: hero             # must exist in catalog sections map
          variant: centered      # optional; must be in catalog variants list if set
          copy:
            headline: "..."      # required copy_slots must be present
            subhead: "..."
          assets: ["hero-bg.jpg"]   # optional
          cta:
            label: "Get Started"
            href: "/contact"
```

## 4. Validation Rules (site_manifest.py::validate_site)

1. `page.slug` — must be ASCII (G-8).
2. `section.type` — must exist as a key in `sections:` map.
3. `section.copy` — all `copy_slots.required` keys must be present.
4. `section.variant` — if set, must appear in the catalog `variants` list.
5. `section.type` slug — must be ASCII (G-8).
6. `site.theme` — existence of `presets/themes/<slug>/theme.yaml` is a **soft** check: warning only (P2 not yet complete). Not an error.

## 5. Invariants

- Catalog is additive: adding a new section type never breaks existing profiles.
- Section types are catalog-grounded: a profile cannot reference a type not in this catalog.
- `copy_slots.required` is the minimum viable content contract per section type.
- Asset slots are informational only at schema level; visual quality gate (vision-QA, P4) enforces asset presence.
