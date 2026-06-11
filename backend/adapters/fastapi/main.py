"""
main.py — FastAPI backend adapter entrypoint.

Serves all 8 wire keys from middle/contract/wire-v1.yaml.
Contract loaded at startup from middle/contract/ — NOT hardcoded (G-1).

Launch:
    uvicorn main:app --port 8081

Port is env-configurable:
    PORT=9090 uvicorn main:app --port 9090

Default port: 8081 (springboot-jakarta uses 8080; Growth-7 hit port conflicts).
"""

from __future__ import annotations

import os

# Load .env before any module-level env-var reads (e.g. legal._DB_URL).
# python-dotenv is optional — if absent, env vars must be set manually.
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"), override=False)
except ImportError:
    pass

from fastapi import FastAPI

from routers import auth, entity, legal, status

app = FastAPI(
    title="compounding-stack backend adapter — fastapi",
    description=(
        "FastAPI implementation of the middle/contract/wire-v1.yaml wire protocol. "
        "Swap-compatible with springboot-jakarta adapter via customer profile stack.backend key."
    ),
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(entity.router)
app.include_router(legal.router)
app.include_router(status.router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8081"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
