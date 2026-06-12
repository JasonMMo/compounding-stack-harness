"""manifest.py — catalog → screen manifest emitter.

Library function + thin CLI. Part of the creater (orchestrator) axis.

Usage:
  python scripts/workflow/manifest.py --profile shop-demo
  python scripts/workflow/manifest.py --profile shop-demo --entities contact sales-order

Output JSON shape: docs/architecture/screen-manifest.md
Single-source: frontend reads this; never reimplements the column classification.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Hidden field names (system columns — excluded from fields list)
# ---------------------------------------------------------------------------

_HIDDEN_NAMES: frozenset[str] = frozenset({"id", "created_at", "updated_at"})

# ---------------------------------------------------------------------------
# Column classification — THE core logic (single source of truth)
# ---------------------------------------------------------------------------

_SYSTEM_TIMESTAMP_NAMES: frozenset[str] = frozenset({"created_at", "updated_at"})


def _label(name: str) -> str:
    """Convert snake_case column name to Title Case human label."""
    return " ".join(word.capitalize() for word in name.split("_"))


def _classify_column(col_name: str, col_def: dict[str, Any]) -> dict[str, Any]:
    """Return a field descriptor dict for one catalog column.

    Rules (in priority order):
    1. FK present          → control fk-text, fk_entity, note
    2. type enum           → control select, options
    3. type string         → control text (carry max_length from length)
    4. type text           → control textarea
    5. type integer/decimal → control number
    6. type boolean        → control checkbox
    7. type date           → control date
    8. type timestamp (non-system) → control datetime
    9. type uuid (non-FK)  → control text (treat as opaque string input)
    """
    col_type: str = col_def.get("type", "string")
    nullable: bool = col_def.get("nullable", True)
    fk: dict | None = col_def.get("fk")

    field: dict[str, Any] = {
        "name": col_name,
        "type": col_type,
        "required": not nullable,
    }

    # label
    field["label"] = _label(col_name)

    # unique (carry when true)
    if col_def.get("unique"):
        field["unique"] = True

    # FK takes priority over all other type rules
    if fk and isinstance(fk, dict):
        field["control"] = "fk-text"
        field["fk_entity"] = fk.get("entity", "")
        field["note"] = "FK dropdown deferred (M1)"
        return field

    if col_type == "enum":
        field["control"] = "select"
        field["options"] = list(col_def.get("values") or [])
        return field

    if col_type == "string":
        field["control"] = "text"
        if "length" in col_def:
            field["max_length"] = col_def["length"]
        return field

    if col_type == "text":
        field["control"] = "textarea"
        return field

    if col_type in ("integer", "decimal"):
        field["control"] = "number"
        return field

    if col_type == "boolean":
        field["control"] = "checkbox"
        return field

    if col_type == "date":
        field["control"] = "date"
        return field

    if col_type == "timestamp":
        field["control"] = "datetime"
        return field

    # uuid (non-FK) and any unknown type → text
    field["control"] = "text"
    return field


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_manifest(
    profile_slug: str,
    entity_keys: list[str],
    catalog: dict[str, Any],
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a screen manifest dict from catalog entities.

    Parameters
    ----------
    profile_slug:
        Customer profile slug (e.g. "shop-demo").
    entity_keys:
        Ordered list of catalog entity keys to include.
    catalog:
        Full catalog dict as returned by render.py's load_catalog().
    profile:
        Optional full profile dict (loaded by scaffold.py). When provided,
        ``customer.display``, ``domains[].display``,
        ``overlay.feedback_url``, and ``domains[].entity_labels`` overrides
        are included / applied so the frontend renders personalised labels.
        When None (backward compat / manifest.py CLI), these keys are
        omitted and the frontend falls back to generic labels.

    Returns
    -------
    dict with shape documented in docs/architecture/screen-manifest.md.
    Deterministic: stable key insertion order; all lists in catalog order.
    """
    all_entities: dict[str, Any] = catalog.get("entities", {})
    catalog_version: str = str(catalog.get("version", "1.0"))

    # ── Determine locale for label selection ─────────────────────────────────
    # profile.defaults.locale drives label_ko preference.
    # When profile is absent (manifest.py CLI mode) locale is treated as non-KR.
    _use_ko: bool = False
    _profile_entity_labels: dict[str, str] = {}  # entity_key → override label

    if profile is not None:
        defaults_block: dict[str, Any] = profile.get("defaults") or {}
        locale: str = str(defaults_block.get("locale", ""))
        _use_ko = locale.startswith("ko")

        # Collect all entity_labels overrides from every domain block.
        # profile.domains[].entity_labels is a slug→label map (optional key).
        # Last-write wins if the same key appears in multiple domain blocks
        # (should not happen, but be deterministic).
        for domain_block in profile.get("domains") or []:
            overrides: dict[str, Any] = domain_block.get("entity_labels") or {}
            for ek, lbl in overrides.items():
                if lbl:
                    _profile_entity_labels[ek] = str(lbl)

    entities_out: dict[str, Any] = {}

    for key in entity_keys:
        ent = all_entities[key]  # caller guarantees key exists
        domain: str = ent.get("domain", "")
        table: str = ent.get("table", "")
        columns: dict[str, Any] = ent.get("columns", {})

        # ── Entity label — three-tier priority ───────────────────────────────
        # 1. profile.domains[].entity_labels[key]  (customer term, highest)
        # 2. catalog.label_ko                      (when locale starts with "ko")
        # 3. key with hyphens→spaces, title-cased  (English fallback)
        if key in _profile_entity_labels:
            label = _profile_entity_labels[key]
        elif _use_ko and ent.get("label_ko"):
            label = ent["label_ko"]
        else:
            label = " ".join(word.capitalize() for word in key.replace("-", " ").split())

        fields: list[dict[str, Any]] = []
        hidden_fields: list[str] = []

        for col_name, col_def in columns.items():
            if col_name in _HIDDEN_NAMES:
                hidden_fields.append(col_name)
            else:
                fields.append(_classify_column(col_name, col_def))

        entities_out[key] = {
            "domain": domain,
            "table": table,
            "label": label,
            "fields": fields,
            "hidden_fields": hidden_fields,
        }

    manifest: dict[str, Any] = {
        "profile": profile_slug,
        "catalog_version": catalog_version,
        "entities": entities_out,
    }

    # ── Profile-derived display data (optional — absent when profile not passed) ──
    # Included when scaffold.py passes the full profile dict so the frontend
    # can render a personalised home screen (customer heading + domain cards).
    # Absent in manifest → frontend falls back to generic rendering (backward compat).
    if profile is not None:
        customer_block: dict[str, Any] = profile.get("customer") or {}
        customer_display: str = customer_block.get("display", profile_slug)
        manifest["customer_display"] = customer_display

        # Build domain card list: slug + display + entity keys in that domain.
        # display fallback: domain slug (hyphens→spaces, title-cased).
        domain_cards: list[dict[str, Any]] = []
        for domain_block in profile.get("domains") or []:
            d_slug: str = domain_block.get("slug", "")
            raw_display: str = domain_block.get("display", "")
            if not raw_display:
                raw_display = " ".join(
                    w.capitalize() for w in d_slug.replace("-", " ").split()
                )
            # Only include entities that are present in this manifest.
            d_entities: list[str] = [
                k for k in (domain_block.get("entities") or [])
                if k in entities_out
            ]
            if d_entities:  # skip domains whose entities were not scaffolded
                domain_cards.append(
                    {
                        "slug": d_slug,
                        "display": raw_display,
                        "entities": d_entities,
                    }
                )
        manifest["domains"] = domain_cards

        # Optional feedback CTA URL (overlay.feedback_url).
        overlay: dict[str, Any] = profile.get("overlay") or {}
        feedback_url: str = overlay.get("feedback_url", "")
        if feedback_url:
            manifest["feedback_url"] = feedback_url

    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit screen manifest JSON from catalog entities."
    )
    parser.add_argument("--profile", required=True, help="Customer profile slug.")
    parser.add_argument(
        "--entities",
        nargs="+",
        help="Entity keys to include (space-separated). Default: all catalog entities.",
    )
    args = parser.parse_args(argv)

    # Import load_catalog from render.py (single-source catalog loader)
    render_dir = Path(__file__).resolve().parent.parent.parent / "presets" / "ddl"
    sys.path.insert(0, str(render_dir))
    try:
        from render import load_catalog  # type: ignore[import]
    except ImportError as e:
        print(f"Cannot import render.py: {e}", file=sys.stderr)
        return 1

    catalog = load_catalog()
    all_entity_keys = list(catalog.get("entities", {}).keys())

    entity_keys = args.entities if args.entities else all_entity_keys

    # Validate
    missing = [k for k in entity_keys if k not in catalog.get("entities", {})]
    if missing:
        print(f"Entity key(s) not found in catalog: {', '.join(missing)}", file=sys.stderr)
        return 1

    manifest = build_manifest(args.profile, entity_keys, catalog)
    print(json.dumps(manifest, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
