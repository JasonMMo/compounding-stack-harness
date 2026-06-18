"""
api.py — FastAPI application for legal RAG service.

Endpoints:
  POST /ingest   — ingest a file (PDF/DOCX/txt) into legal_document_chunk
  POST /search   — hybrid search (FTS+ANN+RRF), return ranked chunks + citations
  GET  /health   — liveness probe (DB pool + embed sidecar reachability)

DESIGN CONTRACTS:
  - /search returns chunks + citations only (Lite tier). No answer_text generated.
    LLM generation is gated to Pro tier (not implemented here).
  - All /search requests run inside rls_session() — attorney_id is mandatory.
  - Ingest uses app_service role (BYPASSRLS) — no rls_session needed.
  - Cloud embedding API is never called (EmbedSidecarUnavailable = 503).
  - /ingest file_path is validated against LEGAL_RAG_INGEST_ROOT (path-traversal guard).

Run from services/legal-rag/:
  uvicorn api:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import config as cfg
import db as database
import embed_client as ec
import ingest as ingest_mod
import retrieve as retrieve_mod
import citation as citation_mod

logger = logging.getLogger(__name__)

# ── App state ─────────────────────────────────────────────────────────────────

_settings: cfg.Settings | None = None
_pool = None
_embedder: ec.EmbedClient | None = None


# ── Typed accessors (eliminate Optional member-access warnings) ───────────────

def _get_settings() -> cfg.Settings:
    assert _settings is not None, "Settings not initialized — lifespan not complete"
    return _settings


def _get_pool():
    assert _pool is not None, "DB pool not initialized — lifespan not complete"
    return _pool


def _get_embedder() -> ec.EmbedClient:
    assert _embedder is not None, "EmbedClient not initialized — lifespan not complete"
    return _embedder


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _settings, _pool, _embedder

    _settings = cfg.load()
    _embedder = ec.EmbedClient(
        base_url=_settings.embed_url,
        timeout=30.0,
    )
    _pool = await database.create_pool(_settings)
    logger.info("legal-rag service started. embed_url=%s", _settings.embed_url)

    yield

    pool = _pool
    if pool is not None:
        await pool.close()
    logger.info("legal-rag service stopped.")


app = FastAPI(
    title="Legal RAG Service",
    description=(
        "Hybrid search (FTS + vector ANN + RRF) over legal precedents "
        "and case documents. Lite tier: returns ranked chunks + citations only. "
        "LLM answer generation is NOT implemented (Pro tier gate)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# ── Security helpers ──────────────────────────────────────────────────────────

def _validate_ingest_path(file_path: str, ingest_root: str) -> str:
    """Resolve file_path and verify it is under ingest_root.

    Uses os.path.realpath to normalise symlinks and .. traversal.
    Raises HTTPException(400) if the resolved path escapes ingest_root.

    Args:
        file_path:   Raw path string from the request.
        ingest_root: Allowed root directory (from settings.ingest_root).

    Returns:
        Resolved absolute path string (safe to pass to ingest_file).
    """
    resolved = os.path.realpath(os.path.abspath(file_path))
    root = os.path.realpath(os.path.abspath(ingest_root))

    # os.path.commonpath raises ValueError if paths are on different drives (Windows)
    try:
        common = os.path.commonpath([resolved, root])
    except ValueError:
        common = ""

    if common != root:
        raise HTTPException(
            status_code=400,
            detail=(
                f"file_path {file_path!r} resolves outside the permitted "
                f"ingest root. Path traversal is not allowed."
            ),
        )
    return resolved


# ── Embed helper ──────────────────────────────────────────────────────────────

def _embed_or_503(text: str) -> list[float]:
    """Embed text via local sidecar; convert sidecar errors to HTTP 503."""
    try:
        return _get_embedder().embed(text)
    except ec.EmbedSidecarUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Embedding sidecar unavailable: {exc}. "
                   "No cloud fallback is provided by design.",
        ) from exc


# ── Schemas ───────────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    file_path: str = Field(..., description="Absolute path to the file on the server.")
    source_type: str = Field(
        ..., description="'precedent' or 'case_document'."
    )
    source_id: str = Field(
        ..., description="UUID FK to legal_precedent.id or legal_case_document.id."
    )
    case_id: str | None = Field(
        None,
        description="UUID FK to legal_case.id (required when source_type='case_document').",
    )


class IngestResponse(BaseModel):
    chunks_upserted: int
    source_id: str
    source_type: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query text (Korean/mixed).")
    attorney_id: str = Field(
        ..., description="UUID of the querying attorney (RLS enforcement)."
    )
    case_id: str | None = Field(
        None, description="Optional: scope search to a specific case."
    )
    top_k: int | None = Field(None, ge=1, le=50, description="Override default top-k.")


class CitationOut(BaseModel):
    chunk_id: str
    source_type: str
    source_id: str
    case_id: str | None
    chunk_index: int
    chunk_text_excerpt: str
    rrf_score: float
    fts_rank: int | None = None
    ann_rank: int | None = None
    # Resolved metadata
    case_number: str | None = None
    court: str | None = None
    decision_date: str | None = None
    holding_summary: str | None = None
    document_title: str | None = None
    document_type: str | None = None


class SearchResponse(BaseModel):
    query_log_id: str
    total_results: int
    results: list[CitationOut]
    note: str = (
        "Lite tier: ranked chunks + citations returned. "
        "LLM answer generation is gated to Pro tier."
    )


class HealthResponse(BaseModel):
    status: str
    db_pool: str
    embed_sidecar: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["ops"])
async def health():
    """Liveness probe: checks DB pool and embedding sidecar reachability."""
    db_ok = False
    embed_ok = False

    pool = _pool
    embedder = _embedder

    if pool is not None:
        try:
            async with pool.connection() as conn:
                await conn.execute("SELECT 1")
            db_ok = True
        except Exception:
            db_ok = False

    if embedder is not None:
        embed_ok = embedder.health_check()

    overall = "ok" if (db_ok and embed_ok) else "degraded"
    return HealthResponse(
        status=overall,
        db_pool="ok" if db_ok else "error",
        embed_sidecar="ok" if embed_ok else "error",
    )


@app.post("/ingest", response_model=IngestResponse, tags=["ingest"])
async def ingest(req: IngestRequest):
    """Ingest a file into legal_document_chunk.

    Requires app_service DB role (BYPASSRLS). File must be accessible
    on the server filesystem under LEGAL_RAG_INGEST_ROOT.
    Idempotent: re-ingest overwrites existing chunks.
    """
    settings = _get_settings()
    pool = _get_pool()
    embedder = _get_embedder()

    try:
        uuid.UUID(req.source_id)
    except ValueError:
        raise HTTPException(400, f"source_id is not a valid UUID: {req.source_id!r}")

    if req.source_type == "case_document":
        if not req.case_id:
            raise HTTPException(
                400, "case_id is required when source_type='case_document'"
            )
        try:
            uuid.UUID(req.case_id)
        except ValueError:
            raise HTTPException(400, f"case_id is not a valid UUID: {req.case_id!r}")

    # Path-traversal guard (CISO gate)
    safe_path = _validate_ingest_path(req.file_path, settings.ingest_root)

    async with pool.connection() as conn:
        try:
            n = await ingest_mod.ingest_file(
                conn=conn,
                embed_client=embedder,
                model_version=settings.embed_model_version,
                file_path=safe_path,
                source_type=req.source_type,
                source_id=req.source_id,
                case_id=req.case_id,
                chunk_token_target=settings.chunk_token_target,
                chunk_overlap_tokens=settings.chunk_overlap_tokens,
            )
        except FileNotFoundError as exc:
            raise HTTPException(404, str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        except ec.EmbedSidecarUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc

    return IngestResponse(
        chunks_upserted=n,
        source_id=req.source_id,
        source_type=req.source_type,
    )


@app.post("/search", response_model=SearchResponse, tags=["search"])
async def search(req: SearchRequest):
    """Hybrid search: FTS + vector ANN + RRF.

    Returns ranked chunks with resolved citations.
    DOES NOT generate an LLM answer (Lite tier guarantee).
    attorney_id is mandatory — enforces RLS scoping.
    """
    settings = _get_settings()
    pool = _get_pool()

    try:
        uuid.UUID(req.attorney_id)
    except ValueError:
        raise HTTPException(400, f"attorney_id is not a valid UUID: {req.attorney_id!r}")

    if req.case_id:
        try:
            uuid.UUID(req.case_id)
        except ValueError:
            raise HTTPException(400, f"case_id is not a valid UUID: {req.case_id!r}")

    top_k = req.top_k or settings.top_k
    t0 = time.monotonic()

    # Embed query via local sidecar (no cloud fallback)
    query_vec = _embed_or_503(req.query)

    async with pool.connection() as conn:
        async with database.rls_session(conn, req.attorney_id):
            chunks = await retrieve_mod.hybrid_search(
                conn=conn,
                query_text=req.query,
                query_embedding=query_vec,
                top_k=top_k,
                fts_limit=settings.fts_candidate_limit,
                ann_limit=settings.ann_candidate_limit,
                rrf_k=settings.rrf_k,
            )
            citations = await citation_mod.resolve_citations(
                conn=conn,
                chunks=chunks,
            )
            latency_ms = int((time.monotonic() - t0) * 1000)
            log_id = await citation_mod.log_query(
                conn=conn,
                attorney_id=req.attorney_id,
                query_text=req.query,
                query_embedding=query_vec,
                citations=citations,
                case_id=req.case_id,
                latency_ms=latency_ms,
            )

    # Build response — merge RetrievedChunk rank info with Citation metadata
    chunk_rank_map = {
        c.chunk_id: (c.fts_rank, c.ann_rank) for c in chunks
    }
    results_out = []
    for cit in citations:
        fts_r, ann_r = chunk_rank_map.get(cit.chunk_id, (None, None))
        results_out.append(
            CitationOut(
                chunk_id=cit.chunk_id,
                source_type=cit.source_type,
                source_id=cit.source_id,
                case_id=cit.case_id,
                chunk_index=cit.chunk_index,
                chunk_text_excerpt=cit.chunk_text_excerpt,
                rrf_score=cit.rrf_score,
                fts_rank=fts_r,
                ann_rank=ann_r,
                case_number=cit.case_number,
                court=cit.court,
                decision_date=cit.decision_date,
                holding_summary=cit.holding_summary,
                document_title=cit.document_title,
                document_type=cit.document_type,
            )
        )

    return SearchResponse(
        query_log_id=log_id,
        total_results=len(results_out),
        results=results_out,
    )
