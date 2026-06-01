"""
wire_response.py — Wire-protocol-compliant response builders.

Success: payload fields at top level, no 'error' key.
Failure: { "error": { "code", "message", "details"? } }

Mirrors WireResponse.java + ErrorEnvelope.java behavior.
HTTP status for errors is resolved via ContractLoader (from codes.yaml — G-1).
"""

from __future__ import annotations

from typing import Any

from fastapi import Response
from fastapi.responses import JSONResponse

from contract_loader import contract


def ok(fields: dict[str, Any], status_code: int = 200) -> JSONResponse:
    """Return a success JSONResponse. No 'error' key in the body."""
    return JSONResponse(content=fields, status_code=status_code)


def error(code: str, details: dict[str, Any] | None = None) -> JSONResponse:
    """
    Return an error JSONResponse.
    HTTP status resolved from codes.yaml via ContractLoader (G-1 compliant).
    """
    http_status = contract.http_status_for(code)
    message = contract.message_for(code)

    envelope: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        envelope["details"] = details

    return JSONResponse(content={"error": envelope}, status_code=http_status)
