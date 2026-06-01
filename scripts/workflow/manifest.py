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

    Returns
    -------
    dict with shape documented in docs/architecture/screen-manifest.md.
    Deterministic: stable key insertion order; all lists in catalog order.
    """
    all_entities: dict[str, Any] = catalog.get("entities", {})
    catalog_version: str = str(catalog.get("version", "1.0"))

    entities_out: dict[str, Any] = {}

    for key in entity_keys:
        ent = all_entities[key]  # caller guarantees key exists
        domain: str = ent.get("domain", "")
        table: str = ent.get("table", "")
        columns: dict[str, Any] = ent.get("columns", {})

        # entity label: key with hyphens→spaces, title-cased
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

    return {
        "profile": profile_slug,
        "catalog_version": catalog_version,
        "entities": entities_out,
    }


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
