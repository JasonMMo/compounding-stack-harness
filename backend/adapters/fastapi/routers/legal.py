"""
routers/legal.py — law-firm vertical: precedent full-text search.

Wire key: legal.precedents.search
  GET /api/legal/precedents/search?q=<keyword>[&case_type=<optional>]

Uses PostgreSQL tsvector full-text search with 'simple' dictionary.
The GIN index (idx_precedent_fts) is created by scripts/demo/setup_lawfirm.py.

Falls back gracefully if DATABASE_URL is not set: returns an empty list with
a warning so generic entity smoke tests keep passing.

Response body (top 10):
  {
    "items": [
      {
        "citation": "대법원 2020다12345",
        "court": "대법원",
        "decided_date": "2020-05-21",
        "case_type": "civil",
        "holding": "...",
        "keywords": "..."
      },
      ...
    ],
    "total": <int>
  }
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/legal", tags=["legal"])

# ---------------------------------------------------------------------------
# DB connection helper — optional; no-op if DATABASE_URL is absent
# ---------------------------------------------------------------------------

_DB_URL = os.environ.get("DATABASE_URL", "")


def _get_connection():
    """Return a psycopg2 connection or None if unavailable."""
    if not _DB_URL:
        return None
    try:
        import psycopg2  # type: ignore
        return psycopg2.connect(_DB_URL)
    except Exception as exc:  # noqa: BLE001
        log.warning("legal router: DB connection failed — %s", exc)
        return None


# ---------------------------------------------------------------------------
# Search endpoint
# ---------------------------------------------------------------------------

_SEARCH_SQL = """
SELECT
    citation,
    court,
    decided_date::text,
    case_type,
    holding,
    keywords
FROM legal_precedent
WHERE
    to_tsvector('simple', holding || ' ' || COALESCE(keywords, ''))
    @@ plainto_tsquery('simple', %s)
    {case_type_filter}
ORDER BY decided_date DESC
LIMIT 10
"""


@router.get("/precedents/search")
async def search_precedents(
    q: str = "",
    case_type: str | None = None,
) -> JSONResponse:
    """
    Full-text search over legal_precedent.holding + keywords.

    Query params:
      q          — search keyword (required; empty string returns empty list)
      case_type  — optional filter: civil | criminal | administrative | family | commercial
    """
    if not q.strip():
        return JSONResponse(
            content={"items": [], "total": 0},
            status_code=200,
        )

    conn = _get_connection()
    if conn is None:
        log.warning("legal router: no DB connection — returning empty result")
        return JSONResponse(
            content={
                "items": [],
                "total": 0,
                "warning": "DATABASE_URL not configured or DB unavailable",
            },
            status_code=200,
        )

    try:
        case_type_filter = ""
        params: list[Any] = [q.strip()]
        if case_type:
            case_type_filter = "AND case_type = %s"
            params.append(case_type)

        final_sql = _SEARCH_SQL.format(case_type_filter=case_type_filter)

        with conn:
            cur = conn.cursor()
            cur.execute(final_sql, params)
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]

        items = [dict(zip(cols, row)) for row in rows]
        return JSONResponse(
            content={"items": items, "total": len(items)},
            status_code=200,
        )
    except Exception as exc:  # noqa: BLE001
        log.error("legal router: search query failed — %s", exc)
        return JSONResponse(
            content={"error": {"code": "INTERNAL", "message": str(exc)}},
            status_code=500,
        )
    finally:
        conn.close()
