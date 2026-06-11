#!/usr/bin/env python3
"""render.py — DDL renderer for compounding-stack-harness.

Reads presets/ddl/catalog.yaml + presets/ddl/dialects/<dialect>.yaml and
emits CREATE TABLE statements to stdout.

Usage:
  python presets/ddl/render.py --dialect postgres
  python presets/ddl/render.py --dialect hsqldb
  python presets/ddl/render.py --dialect hsqldb --domain hr
  python presets/ddl/render.py --dialect postgres --entity employee
  python presets/ddl/render.py --dialect hsqldb > presets/ddl/build/hsqldb-schema.sql

Tables are emitted in topological order so FK targets precede referrers.
Pure stdlib + PyYAML (already a project dependency).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

DDL_DIR = Path(__file__).resolve().parent
CATALOG_PATH = DDL_DIR / "catalog.yaml"


# ---------------------------------------------------------------------------
# Loader helpers
# ---------------------------------------------------------------------------

def load_catalog() -> dict[str, Any]:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_dialect(name: str) -> dict[str, Any]:
    path = DDL_DIR / "dialects" / f"{name}.yaml"
    if not path.exists():
        available = [p.stem for p in (DDL_DIR / "dialects").glob("*.yaml")]
        print(
            f"Dialect '{name}' not found. Available: {', '.join(sorted(available))}",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Topological sort (FK targets must precede referrers)
# ---------------------------------------------------------------------------

def topological_order(
    entities: dict[str, Any],
) -> tuple[list[str], dict[tuple[str, str], dict]]:
    """Return (ordered_keys, deferred_fks).

    ordered_keys — entity keys in topological order (FK targets first).
    deferred_fks — mapping of (owner_entity_key, col_key) -> fk dict for every
        FK whose target was still being visited when the edge was encountered
        (i.e. a cycle back-edge).  These must be emitted as ALTER TABLE … ADD
        FOREIGN KEY statements AFTER the target table has been created, not
        inline in the CREATE TABLE body.
    """
    # Build adjacency: entity -> set of entities it depends on (FK targets)
    deps: dict[str, set[str]] = {key: set() for key in entities}
    for key, ent in entities.items():
        for col_def in ent.get("columns", {}).values():
            fk = col_def.get("fk")
            if fk and isinstance(fk, dict):
                target = fk.get("entity")
                # Skip self-references and references to unknown entities
                if target and target != key and target in entities:
                    deps[key].add(target)

    ordered: list[str] = []
    visited: set[str] = set()
    visiting: set[str] = set()  # cycle detection
    # (owner_entity_key, col_key) -> fk dict
    deferred_fks: dict[tuple[str, str], dict] = {}

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            # Back-edge: this node is an ancestor in the current DFS path.
            # The caller will record the FK as deferred.
            return
        visiting.add(node)
        for dep in sorted(deps[node]):  # sorted for determinism
            visit(dep)
        visiting.discard(node)
        visited.add(node)
        ordered.append(node)

    for key in sorted(entities.keys()):
        visit(key)

    # Identify deferred FKs: any FK whose target was not yet in `ordered` at
    # the point the owning entity was processed.  We reconstruct this by
    # checking, for each FK, whether the target appears AFTER the owner in
    # the final ordered list (meaning the owner was emitted before its target).
    position = {key: i for i, key in enumerate(ordered)}
    for key, ent in entities.items():
        for col_key, col_def in ent.get("columns", {}).items():
            fk = col_def.get("fk")
            if not fk or not isinstance(fk, dict):
                continue
            target = fk.get("entity")
            if not target or target == key or target not in entities:
                continue
            if position.get(target, -1) > position.get(key, -1):
                # Target comes after owner — this FK is a back-edge; defer it.
                deferred_fks[(key, col_key)] = fk

    return ordered, deferred_fks


# ---------------------------------------------------------------------------
# Type rendering
# ---------------------------------------------------------------------------

def render_type(
    col_key: str,
    col_def: dict[str, Any],
    dialect: dict[str, Any],
) -> str:
    """Return the SQL type string for a column (without constraints)."""
    neutral = col_def["type"]
    type_map = dialect["type_map"]
    defaults = dialect.get("defaults", {})
    sql_type = type_map.get(neutral, neutral)

    if neutral == "uuid":
        # Some dialects embed the length in the type_map value (e.g. VARCHAR(36))
        return sql_type

    if neutral == "string":
        length = col_def.get("length", defaults.get("string_length", 255))
        # If the type_map value already contains parens (e.g. VARCHAR2) strip them
        base = sql_type.split("(")[0]
        return f"{base}({length})"

    if neutral == "decimal":
        precision = col_def.get("precision", 18)
        scale = col_def.get("scale", 4)
        base = sql_type.split("(")[0]
        return f"{base}({precision},{scale})"

    if neutral == "integer":
        # Oracle uses NUMBER(10); others use plain INTEGER
        return sql_type

    if neutral == "enum":
        enum_length = defaults.get("enum_length", 255)
        base = sql_type.split("(")[0]
        return f"{base}({enum_length})"

    if neutral == "boolean":
        return sql_type

    if neutral in ("text", "date", "timestamp"):
        return sql_type

    return sql_type


# ---------------------------------------------------------------------------
# Column DDL
# ---------------------------------------------------------------------------

def render_column(
    col_key: str,
    col_def: dict[str, Any],
    dialect: dict[str, Any],
    q: str,
) -> str:
    """Render a single column definition line (without trailing comma)."""
    sql_type = render_type(col_key, col_def, dialect)
    parts = [f"    {q}{col_key}{q}", sql_type]

    # Default value — must come BEFORE NOT NULL (standard SQL / HSQLDB requirement)
    if "default" in col_def:
        val = col_def["default"]
        if isinstance(val, bool):
            # Booleans need dialect-aware rendering
            if dialect["type_map"].get("boolean", "BOOLEAN") == "TINYINT(1)":
                parts.append(f"DEFAULT {'1' if val else '0'}")
            else:
                parts.append(f"DEFAULT {'TRUE' if val else 'FALSE'}")
        elif isinstance(val, str):
            parts.append(f"DEFAULT '{val}'")
        else:
            parts.append(f"DEFAULT {val}")

    # NOT NULL — after DEFAULT
    if not col_def.get("nullable", True):
        parts.append("NOT NULL")

    # Inline UNIQUE (single-column only; multi-col uniques go in constraints block)
    if col_def.get("unique"):
        parts.append("UNIQUE")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Constraint DDL
# ---------------------------------------------------------------------------

# SQL keywords / operators that must NOT be quoted when they appear in CHECK exprs.
_CHECK_KEYWORDS: frozenset[str] = frozenset({
    "IS", "NULL", "OR", "AND", "NOT", "IN", "TRUE", "FALSE",
})

_BARE_IDENT_RE = re.compile(r"\b([a-z][a-z0-9_]*)\b")


def _quote_check_expr(expr: str, q: str) -> str:
    """Wrap bare lowercase column-name tokens in CHECK expr with the dialect quote char.

    Tokens that are SQL keywords or pure numeric literals are left untouched.
    Example (q='"'):
        "probability >= 0 AND probability <= 100"
        -> '"probability" >= 0 AND "probability" <= 100'
    """
    def _replace(m: re.Match) -> str:
        tok = m.group(1)
        if tok.upper() in _CHECK_KEYWORDS:
            return tok
        return f"{q}{tok}{q}"

    return _BARE_IDENT_RE.sub(_replace, expr)


def render_enum_check(
    col_key: str,
    col_def: dict[str, Any],
    q: str,
) -> str | None:
    """Return a CHECK constraint string for an enum column, or None."""
    if col_def.get("type") != "enum":
        return None
    values = col_def.get("values", [])
    if not values:
        return None
    in_list = ", ".join(f"'{v}'" for v in values)
    return f"    CHECK ({q}{col_key}{q} IN ({in_list}))"


def render_fk(
    col_key: str,
    col_def: dict[str, Any],
    entities: dict[str, Any],
    dialect: dict[str, Any],
    q: str,
) -> str | None:
    """Return a FOREIGN KEY constraint line or None."""
    fk = col_def.get("fk")
    if not fk or not isinstance(fk, dict):
        return None
    target_entity = fk.get("entity")
    target_col = fk.get("column", "id")
    on_delete = fk.get("on_delete", "restrict")

    if not target_entity or target_entity not in entities:
        return None  # cross-domain FK omitted (see catalog notes)

    target_table = entities[target_entity]["table"]
    on_delete_sql = dialect.get("on_delete_map", {}).get(on_delete, on_delete.upper().replace("_", " "))

    return (
        f"    FOREIGN KEY ({q}{col_key}{q}) "
        f"REFERENCES {q}{target_table}{q} ({q}{target_col}{q}) "
        f"ON DELETE {on_delete_sql}"
    )


# ---------------------------------------------------------------------------
# Main table renderer
# ---------------------------------------------------------------------------

def render_table(
    entity_key: str,
    ent: dict[str, Any],
    entities: dict[str, Any],
    dialect: dict[str, Any],
    deferred_fk_cols: set[str] | None = None,
) -> str:
    """Render CREATE TABLE DDL for one entity.

    deferred_fk_cols — column names whose FK must be emitted later as ALTER TABLE.
        These columns are still created normally; only the inline FOREIGN KEY
        constraint line is suppressed.
    """
    q = dialect.get("quote", '"')
    table_name = ent["table"]
    pk_col = ent.get("primary_key", "id")
    columns = ent.get("columns", {})
    constraints = ent.get("constraints", []) or []
    _deferred = deferred_fk_cols or set()

    lines: list[str] = []
    lines.append(f"CREATE TABLE {q}{table_name}{q} (")

    col_lines: list[str] = []

    # Column definitions
    for col_key, col_def in columns.items():
        col_lines.append(render_column(col_key, col_def, dialect, q))

    # Primary key
    col_lines.append(f"    CONSTRAINT {q}pk_{table_name}{q} PRIMARY KEY ({q}{pk_col}{q})")

    # Enum CHECK constraints (one per enum column)
    for col_key, col_def in columns.items():
        chk = render_enum_check(col_key, col_def, q)
        if chk:
            col_lines.append(chk)

    # Explicit CHECK constraints from catalog
    for c in constraints:
        if c.get("type") == "check":
            expr = _quote_check_expr(c.get("expr", ""), q)
            col_lines.append(f"    CHECK ({expr})")
        elif c.get("type") == "unique":
            cols = c.get("columns", [])
            if cols:
                col_list = ", ".join(f"{q}{col}{q}" for col in cols)
                name_suffix = "_".join(cols)
                col_lines.append(
                    f"    CONSTRAINT {q}uq_{table_name}_{name_suffix}{q} UNIQUE ({col_list})"
                )

    # Foreign keys — skip back-edges that must be deferred to ALTER TABLE
    for col_key, col_def in columns.items():
        if col_key in _deferred:
            continue
        fk_line = render_fk(col_key, col_def, entities, dialect, q)
        if fk_line:
            col_lines.append(fk_line)

    # Assemble
    for i, line in enumerate(col_lines):
        sep = "," if i < len(col_lines) - 1 else ""
        lines.append(f"{line}{sep}")

    lines.append(");")
    lines.append("")

    # Indexes (CREATE INDEX statements)
    for idx_def in (ent.get("indexes") or []):
        idx_cols = idx_def.get("columns", [])
        if not idx_cols:
            continue
        idx_col_str = "_".join(idx_cols)
        idx_name = f"idx_{table_name}_{idx_col_str}"
        col_list = ", ".join(f"{q}{c}{q}" for c in idx_cols)
        lines.append(f"CREATE INDEX {q}{idx_name}{q} ON {q}{table_name}{q} ({col_list});")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render catalog.yaml to CREATE TABLE DDL for a target dialect."
    )
    parser.add_argument(
        "--dialect", "-d",
        default="postgres",
        help="Dialect name (postgres | hsqldb | mysql | oracle). Default: postgres.",
    )
    parser.add_argument(
        "--domain",
        help="Emit only entities belonging to this domain slug.",
    )
    parser.add_argument(
        "--entity",
        help="Emit only the named entity.",
    )
    parser.add_argument(
        "--entities",
        help="Comma-separated list of entity keys to emit (subset of catalog).",
    )
    args = parser.parse_args(argv)

    catalog = load_catalog()
    dialect = load_dialect(args.dialect)
    all_entities: dict[str, Any] = catalog.get("entities", {})

    # Filter — priority: --entity (singular) > --entities (plural) > --domain > all
    if args.entity:
        if args.entity not in all_entities:
            print(f"Entity '{args.entity}' not found in catalog.", file=sys.stderr)
            return 1
        subset = {args.entity: all_entities[args.entity]}
    elif args.entities:
        keys = [k.strip() for k in args.entities.split(",") if k.strip()]
        missing = [k for k in keys if k not in all_entities]
        if missing:
            print(f"Unknown entity keys: {', '.join(missing)}", file=sys.stderr)
            return 1
        subset = {k: all_entities[k] for k in keys}
    elif args.domain:
        subset = {k: v for k, v in all_entities.items() if v.get("domain") == args.domain}
        if not subset:
            print(f"No entities found for domain '{args.domain}'.", file=sys.stderr)
            return 1
    else:
        subset = all_entities

    # Topological order (full graph for FK resolution, then filter).
    # deferred_fks: (owner_entity_key, col_key) -> fk dict for back-edge FKs.
    full_order, deferred_fks = topological_order(all_entities)
    ordered_keys = [k for k in full_order if k in subset]

    # Build per-entity set of deferred column names (for render_table).
    # Also build a lookup: target_entity_key -> list of ALTER TABLE statements
    # to emit immediately after the target table + its indexes are printed.
    deferred_by_owner: dict[str, set[str]] = {}
    alter_after_target: dict[str, list[str]] = {}

    q = dialect.get("quote", '"')
    on_delete_map = dialect.get("on_delete_map", {})

    for (owner_key, col_key), fk in deferred_fks.items():
        deferred_by_owner.setdefault(owner_key, set()).add(col_key)
        target_entity = fk.get("entity")
        if not target_entity or target_entity not in all_entities:
            continue
        target_table = all_entities[target_entity]["table"]
        owner_table = all_entities[owner_key]["table"]
        target_col = fk.get("column", "id")
        on_delete = fk.get("on_delete", "restrict")
        on_delete_sql = on_delete_map.get(on_delete, on_delete.upper().replace("_", " "))
        alter = (
            f'ALTER TABLE {q}{owner_table}{q} ADD FOREIGN KEY ({q}{col_key}{q}) '
            f'REFERENCES {q}{target_table}{q} ({q}{target_col}{q}) '
            f'ON DELETE {on_delete_sql};'
        )
        alter_after_target.setdefault(target_entity, []).append(alter)

    # Header
    header_lines = [
        f"-- DDL generated by render.py",
        f"-- dialect : {args.dialect}",
        f"-- catalog : presets/ddl/catalog.yaml",
        f"-- entities: {len(ordered_keys)}",
        f"-- Note    : FK constraints referencing entities outside this subset are omitted.",
        f"-- Note    : Circular back-edge FKs emitted as ALTER TABLE after target table.",
        f"",
    ]
    print("\n".join(header_lines))

    for key in ordered_keys:
        ent = all_entities[key]
        # Pass the set of deferred FK cols so they are skipped inline.
        deferred_cols = deferred_by_owner.get(key, set())
        ddl = render_table(key, ent, all_entities, dialect, deferred_cols)
        print(ddl)

        # Emit ALTER TABLE statements for back-edge FKs whose target is this table.
        for alter in alter_after_target.get(key, []):
            print(alter)
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
