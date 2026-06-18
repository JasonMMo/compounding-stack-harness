"""
db.py — psycopg3 connection pool + RLS session context manager.

RLS CONTRACT (from README §핵심 계약):
  - app_service role: BYPASSRLS — used for ingest writes.
  - app_user role:    RLS enforced — every query transaction must call
    SET LOCAL app.current_user_id = '<attorney_uuid>' before any data access.
  - Missing attorney_id → 0 rows returned (fail-safe, not an exception).

Usage:
    pool = await create_pool(settings)

    # For ingest (service role, no RLS):
    async with pool.connection() as conn:
        await ingest_work(conn)

    # For attorney-scoped reads (RLS enforced):
    async with pool.connection() as conn:
        async with rls_session(conn, attorney_id):
            rows = await conn.execute("SELECT ...")
"""
from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class RLSSessionError(RuntimeError):
    """Raised when RLS session setup fails (e.g. invalid UUID)."""


def _validate_uuid(value: str | uuid.UUID, name: str) -> str:
    """Return canonical UUID string or raise RLSSessionError."""
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, AttributeError) as exc:
        raise RLSSessionError(
            f"Invalid UUID for {name!r}: {value!r}"
        ) from exc


@asynccontextmanager
async def rls_session(
    conn,  # psycopg.AsyncConnection
    attorney_id: str | uuid.UUID,
) -> AsyncGenerator[None, None]:
    """Context manager that sets app.current_user_id for the current transaction.

    Wraps the body in a transaction and issues:
        SET LOCAL app.current_user_id = '<validated_attorney_uuid>'

    SET LOCAL is transaction-scoped: the variable reverts automatically
    at COMMIT/ROLLBACK, so no cleanup is needed and connection reuse is safe.

    Args:
        conn:        psycopg AsyncConnection (from pool.connection()).
        attorney_id: UUID of the attorney performing the operation.

    Raises:
        RLSSessionError: if attorney_id is not a valid UUID.
    """
    safe_id = _validate_uuid(attorney_id, "attorney_id")

    async with conn.transaction():
        await conn.execute(
            "SELECT set_config('app.current_user_id', %s, true)",
            (safe_id,),
        )
        logger.debug("RLS session opened for attorney_id=%s", safe_id)
        yield


async def create_pool(settings):
    """Create and return an async psycopg3 connection pool.

    Lazy-imports psycopg so the module is importable without psycopg installed
    (unit tests that mock DB still work).

    Args:
        settings: config.Settings instance.

    Returns:
        psycopg.AsyncConnectionPool
    """
    try:
        from psycopg_pool import AsyncConnectionPool  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "psycopg[binary] and psycopg-pool are required. "
            "Install: pip install 'psycopg[binary]' psycopg-pool"
        ) from exc

    pool = AsyncConnectionPool(
        conninfo=settings.db_dsn,
        min_size=settings.db_pool_min,
        max_size=settings.db_pool_max,
        open=False,
    )
    await pool.open()
    logger.info(
        "DB pool created: min=%d max=%d dsn=%s",
        settings.db_pool_min,
        settings.db_pool_max,
        # redact password from log
        settings.db_dsn.split("@")[-1] if "@" in settings.db_dsn else "[dsn]",
    )
    return pool
