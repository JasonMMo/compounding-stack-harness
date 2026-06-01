"""
routers/status.py — status domain router.

Wire key → HTTP mapping:
  status.health → GET /api/status/health
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

import wire_response
from contract_loader import contract

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get("/health")
async def health() -> JSONResponse:
    return wire_response.ok(
        {
            "status": "ok",
            "version": contract.wire_version(),
            "checks": [
                {"name": "store", "status": "ok"},
                {"name": "contract", "status": "ok"},
            ],
        }
    )
