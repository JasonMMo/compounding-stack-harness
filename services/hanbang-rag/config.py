"""
config.py — environment-driven configuration for hanbang-rag service.

All secrets/URLs come from environment variables (prefix: HANBANG_RAG_*).
Fail-fast at import if required vars are missing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _require(var: str) -> str:
    """Return env var value or raise RuntimeError if unset/empty."""
    val = os.environ.get(var, "").strip()
    if not val:
        raise RuntimeError(
            f"Required environment variable {var!r} is not set. "
            "See services/hanbang-rag/README.md for setup instructions."
        )
    return val


def _optional(var: str, default: str) -> str:
    return os.environ.get(var, default).strip() or default


@dataclass(frozen=True)
class Settings:
    # ── Database ─────────────────────────────────────────────────────────────
    db_dsn: str
    """psycopg DSN for app_service role, e.g.
    postgresql://app_service:pw@localhost:5432/hanbangdb"""

    # ── Embedding sidecar ────────────────────────────────────────────────────
    embed_url: str
    """Base URL of local embedding sidecar, e.g. http://localhost:8080.
    No cloud fallback. Missing = service refuses to start."""

    embed_model_version: str
    """Model version string recorded in hanbang_rag_document_chunk.model_version."""

    # ── Chunking ─────────────────────────────────────────────────────────────
    chunk_token_target: int
    """Target token count per chunk (default 500)."""

    chunk_overlap_tokens: int
    """Overlap between adjacent chunks in tokens (default 50)."""

    # ── Retrieval ────────────────────────────────────────────────────────────
    rrf_k: int
    """RRF constant k (default 60). Higher = smoother rank fusion."""

    top_k: int
    """Number of chunks to return from hybrid search (default 10)."""

    fts_candidate_limit: int
    """Max rows fetched by FTS stage before RRF (default 100)."""

    ann_candidate_limit: int
    """Max rows fetched by ANN stage before RRF (default 100)."""

    search_min_relevance: float
    """Minimum cosine relevance [0.0, 1.0] for ANN-only results to be returned.
    Results that have an FTS match bypass this threshold (lexical hits are always kept).
    Default 0.0 = filter OFF (all results pass). Set via HANBANG_RAG_SEARCH_MIN_RELEVANCE."""

    # ── Connection pool ───────────────────────────────────────────────────────
    db_pool_min: int
    db_pool_max: int

    # ── Security ─────────────────────────────────────────────────────────────
    ingest_root: str
    """Absolute path to the allowed root directory for ingest file_path inputs.
    POST /ingest rejects any path that does not resolve under this directory.
    Prevents path-traversal attacks."""

    jwt_secret: str
    """HS256 signing secret for user JWT tokens (HANBANG_RAG_JWT_SECRET).
    Required. Service refuses to start if unset."""

    service_token: str
    """Static bearer token for /ingest endpoint (HANBANG_RAG_SERVICE_TOKEN).
    Required. Must match X-Service-Token header on all ingest requests."""

    env: str
    """Deployment environment: 'dev' (default) | 'prod'.
    In prod mode FastAPI auto-docs (/docs, /redoc, /openapi.json) are disabled.
    Set via HANBANG_RAG_ENV environment variable."""

    # ── Document storage ──────────────────────────────────────────────────────
    storage_root: str
    """Absolute path to root directory for uploaded files (corpus ingestion).
    Empty string = not configured.
    Set via HANBANG_RAG_STORAGE_ROOT. Import-time fail-fast is intentionally disabled."""


def _load_min_relevance() -> float:
    """Parse HANBANG_RAG_SEARCH_MIN_RELEVANCE; validate [0.0, 1.0]. Default 0.0."""
    raw = _optional("HANBANG_RAG_SEARCH_MIN_RELEVANCE", "0.0")
    try:
        val = float(raw)
    except ValueError:
        raise RuntimeError(
            f"HANBANG_RAG_SEARCH_MIN_RELEVANCE must be a float in [0.0, 1.0], got {raw!r}"
        )
    if not (0.0 <= val <= 1.0):
        raise RuntimeError(
            f"HANBANG_RAG_SEARCH_MIN_RELEVANCE must be in [0.0, 1.0], got {val}"
        )
    return val


def load() -> Settings:
    """Load settings from environment. Call once at startup."""
    return Settings(
        db_dsn=_require("HANBANG_RAG_DB_DSN"),
        embed_url=_require("HANBANG_RAG_EMBED_URL").rstrip("/"),
        embed_model_version=_optional(
            "HANBANG_RAG_EMBED_MODEL_VERSION", "multilingual-e5-base"
        ),
        chunk_token_target=int(_optional("HANBANG_RAG_CHUNK_TOKENS", "500")),
        chunk_overlap_tokens=int(_optional("HANBANG_RAG_CHUNK_OVERLAP", "50")),
        rrf_k=int(_optional("HANBANG_RAG_RRF_K", "60")),
        top_k=int(_optional("HANBANG_RAG_TOP_K", "10")),
        fts_candidate_limit=int(_optional("HANBANG_RAG_FTS_LIMIT", "100")),
        ann_candidate_limit=int(_optional("HANBANG_RAG_ANN_LIMIT", "100")),
        search_min_relevance=_load_min_relevance(),
        db_pool_min=int(_optional("HANBANG_RAG_POOL_MIN", "2")),
        db_pool_max=int(_optional("HANBANG_RAG_POOL_MAX", "10")),
        ingest_root=_require("HANBANG_RAG_INGEST_ROOT"),
        jwt_secret=_require("HANBANG_RAG_JWT_SECRET"),
        service_token=_require("HANBANG_RAG_SERVICE_TOKEN"),
        env=_optional("HANBANG_RAG_ENV", "dev").lower(),
        storage_root=_optional("HANBANG_RAG_STORAGE_ROOT", ""),
    )
