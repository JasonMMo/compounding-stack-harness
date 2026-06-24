"""
routers/task_search.py — Lite-AI semantic issue search endpoint.

Wire key (registered in middle/contract/wire-v1.yaml, Growth-123):
  project.search-similar

Endpoint:
  POST /api/project/search-similar
  Body: { "query_text": str, "exclude_id": str|null, "top_n": int (default 5) }

  GET  /api/project/search-similar
  Params: query_text, exclude_id (optional), top_n (optional, default 5)

Response:
  {
    "mode": "semantic" | "lexical",   -- ALWAYS present; surface to user as a badge
    "items": [
      {
        "id": "...",
        "score": 0.85,
        "name": "...",
        ...all task fields
      },
      ...
    ],
    "total": <int>
  }

Honesty contract:
  - mode="semantic" only when TASKFLOW_EMBED_URL is set and call succeeds.
  - mode="lexical"  when env is unset or embedding call fails (graceful fallback).
  - Callers MUST display the mode badge to users.
  - Cloud API usage: ZERO. $0 per-request cost boundary maintained.

Pattern: mirrors legal.py (optional DB + graceful no-op fallback, JSONResponse).
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from store import entity_store
from services.task_search import search_similar

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/project", tags=["project-search"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class SearchSimilarBody(BaseModel):
    query_text: str = Field(..., description="Search query text")
    exclude_id: Optional[str] = Field(None, description="Entity id to exclude from results")
    top_n: int = Field(5, ge=1, le=50, description="Maximum results to return")


# ---------------------------------------------------------------------------
# Shared handler logic
# ---------------------------------------------------------------------------

def _run_search(
    query_text: str,
    exclude_id: str | None,
    top_n: int,
) -> JSONResponse:
    if not query_text or not query_text.strip():
        return JSONResponse(
            content={"mode": "lexical", "items": [], "total": 0},
            status_code=200,
        )

    candidates: list[dict[str, Any]] = entity_store.find_all("task")

    try:
        result = search_similar(
            query_text=query_text,
            candidates=candidates,
            top_n=top_n,
            exclude_id=exclude_id,
        )
    except Exception as exc:  # noqa: BLE001
        log.error("task_search router: search_similar raised — %s", exc)
        return JSONResponse(
            content={
                "error": {
                    "code": "INTERNAL",
                    "message": "검색 중 오류가 발생했습니다. 관리자에게 문의하세요.",
                }
            },
            status_code=500,
        )

    return JSONResponse(
        content={
            "mode": result["mode"],
            "items": result["items"],
            "total": len(result["items"]),
        },
        status_code=200,
    )


# ---------------------------------------------------------------------------
# GET endpoint (query params)
# ---------------------------------------------------------------------------

@router.get("/search-similar")
async def search_similar_get(
    query_text: str = "",
    exclude_id: str | None = None,
    top_n: int = 5,
) -> JSONResponse:
    """
    GET /api/project/search-similar

    Query params:
      query_text  — search text (required; empty returns empty list)
      exclude_id  — optional task id to exclude
      top_n       — max results (default 5, max 50)
    """
    return _run_search(
        query_text=query_text,
        exclude_id=exclude_id,
        top_n=max(1, min(top_n, 50)),
    )


# ---------------------------------------------------------------------------
# POST endpoint (JSON body)
# ---------------------------------------------------------------------------

@router.post("/search-similar")
async def search_similar_post(body: SearchSimilarBody) -> JSONResponse:
    """
    POST /api/project/search-similar

    Body (JSON):
      { "query_text": "...", "exclude_id": "uuid-or-null", "top_n": 5 }
    """
    return _run_search(
        query_text=body.query_text,
        exclude_id=body.exclude_id,
        top_n=body.top_n,
    )
