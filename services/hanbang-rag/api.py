"""
api.py -- FastAPI application for hanbang-rag service.

Endpoints:
  POST /auth/login              -- email+password -> JWT
  GET  /health                  -- shallow liveness probe (no auth)
  GET  /health/detail           -- deep health check: DB + embed sidecar (X-Service-Token)
  POST /search                  -- hybrid FTS+ANN+RRF + citation resolution (Bearer JWT)
  POST /ingest                  -- ingest a notice file (X-Service-Token)
  GET  /documents/notice/{id}   -- fetch hanbang_rag_notice.full_text (Bearer JWT)

AUTH CONTRACTS (B-1 from auth.py):
  /search, /documents/*:  Authorization: Bearer <JWT>  (user identity from JWT sub claim)
  /health/detail, /ingest: X-Service-Token: <token>   (== HANBANG_RAG_SERVICE_TOKEN env var)
  /auth/login:             email + password JSON body -> JWT on success; 401 on any failure.
  /health:                 no auth (shallow ping only).

DESIGN CONTRACTS:
  - source_type is ALWAYS 'notice'. No case_document, no case_id.
  - No LLM answer generation. Lite tier: ranked chunks + citations returned only.
  - bcrypt.checkpw is always called on login (even for unknown emails) to prevent
    timing-based email enumeration.
  - /documents/notice/{id}: returns raw government notice text -- NOT an AI answer.
    Displayed to convey citation trust to the user ("이건 AI 답변 아니라 고시 원문").

DDL-CODE CONTRACT (verified against sql/02~06):
  - hanbang_rag_user:         SELECT id, password_hash, role WHERE email = %s  (app_service)
  - hanbang_rag_notice:       SELECT id, notice_number, ministry, issued_date, summary, full_text
  - hanbang_rag_document_chunk: no case_id column (D1 DDL). UNIQUE(source_id, source_type, chunk_index).
  - hanbang_rag_query_log:    INSERT (user_id, query_text, query_embedding, retrieved_chunk_ids,
                                       citations_summary, status, latency_ms)  via citation.log_query()
  - 06_grants: app_user = SELECT notice+chunk, SELECT+INSERT query_log. NO access to hanbang_rag_user.
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import auth
import citation as citation_mod
import config as cfg
import db as database
import embed_client as ec
import ingest as ingest_mod
import retrieve as retrieve_mod

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ── Startup singletons ────────────────────────────────────────────────────────

_settings: cfg.Settings = cfg.load()
_pool = None
_embedder: ec.EmbedClient | None = None


def _get_settings() -> cfg.Settings:
    return _settings


def _get_pool():
    assert _pool is not None, "DB pool not initialized — lifespan not complete"
    return _pool


def _get_embedder() -> ec.EmbedClient:
    assert _embedder is not None, "EmbedClient not initialized — lifespan not complete"
    return _embedder


# FastAPI dependency instances (bound to _get_settings at module level)
_user_dep = auth.make_user_dep(_get_settings)
_service_token_dep = auth.make_service_token_dep(_get_settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pool, _embedder
    _embedder = ec.EmbedClient(
        base_url=_settings.embed_url,
        timeout=30.0,
    )
    _pool = await database.create_pool(_settings)
    logger.info("hanbang-rag service started. embed_url=%s", _settings.embed_url)

    yield

    if _pool:
        await _pool.close()
    logger.info("hanbang-rag service stopped.")


_docs_kwargs = (
    {}
    if _settings.env != "prod"
    else {"docs_url": None, "redoc_url": None, "openapi_url": None}
)

app = FastAPI(
    title="hanbang-rag",
    description=(
        "Self-host RAG for 한방 급여 고시 (Korean herbal medicine reimbursement notices). "
        "Lite tier: FTS+ANN+RRF retrieval + citation. No LLM answer generation."
    ),
    version="0.1.0",
    lifespan=lifespan,
    **_docs_kwargs,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ────────────────────────────────────────────────────────────────────

def _embed_or_503(text: str) -> list[float]:
    """Embed text via local sidecar; convert sidecar errors to HTTP 503."""
    try:
        return _get_embedder().embed(text)
    except ec.EmbedSidecarUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Embedding sidecar unavailable: {exc}. No cloud fallback by design.",
        ) from exc


# ── Schemas ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address.")
    password: str = Field(..., description="User password (plaintext; TLS in transit).")


class LoginResponse(BaseModel):
    token: str
    user_id: str
    role: str


class HealthResponse(BaseModel):
    status: str


class HealthDetailResponse(BaseModel):
    status: str
    db_pool: str
    embed_sidecar: str


class IngestRequest(BaseModel):
    file_path: str = Field(
        ..., description="Absolute path to the notice file on the server."
    )
    source_id: str = Field(
        ..., description="UUID FK to hanbang_rag_notice.id. Must exist before ingest."
    )


class IngestResponse(BaseModel):
    chunks_upserted: int
    source_id: str
    source_type: str = "notice"


class SearchRequest(BaseModel):
    """Search request. user_id is derived from JWT -- do NOT supply in body."""

    query: str = Field(..., min_length=1, description="Search query text (Korean/mixed).")
    top_k: int | None = Field(
        None, ge=1, le=50, description="Override default top-k (max 50). Default from config."
    )
    match_mode: str = Field(
        "or",
        pattern="^(or|and)$",
        description="'or'=any term (default, high recall), 'and'=all terms (precise).",
    )


class CitationOut(BaseModel):
    chunk_id: str
    source_id: str
    chunk_index: int
    chunk_text_excerpt: str
    rrf_score: float
    notice_number: str | None = None
    ministry: str | None = None
    issued_date: str | None = None
    summary: str | None = None


class SearchResponse(BaseModel):
    query_log_id: str
    total_results: int
    results: list[CitationOut]
    note: str = (
        "Lite tier: ranked chunks + citations returned. "
        "LLM answer generation is gated to Pro tier."
    )


class NoticeResponse(BaseModel):
    id: str
    notice_number: str
    ministry: str
    issued_date: str
    summary: str | None = None
    full_text: str | None = None


# ── Auth constants ─────────────────────────────────────────────────────────────

_LOGIN_FAIL_MSG = "이메일 또는 비밀번호가 올바르지 않습니다."
# Dummy bcrypt hash for timing-guard on unknown-email path.
# Never matches any real password. 60-byte $2b$ format required for bcrypt.checkpw.
_DUMMY_HASH = b"$2b$12$WZ0mFgAfr0FC4XCL6GzSY.yyKVdGxcp5TSNqAYfdlQ/g1/STGB6ga"


def _bcrypt_verify(password: str, password_hash: str) -> bool:
    """Constant-time bcrypt verification. Returns True if password matches hash."""
    try:
        import bcrypt  # lazy import -- available at runtime
    except ImportError as exc:
        raise ImportError(
            "bcrypt is required for login. Install: pip install 'bcrypt>=4.0,<5.0'"
        ) from exc
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/auth/login", response_model=LoginResponse, tags=["auth"])
async def login(req: LoginRequest):
    """Authenticate a user by email + password and return a JWT.

    Uses app_service (BYPASSRLS) connection to SELECT from hanbang_rag_user.
    bcrypt.checkpw is always called (even for unknown emails) to prevent
    timing-based email enumeration. Both wrong-email and wrong-password
    return 401 with the same message.

    TIMING NOTE: For unknown emails, a dummy hash is checked so response
    time is similar to a real bcrypt comparison. Not perfect constant-time
    (hash existence leaks), but sufficient for MVP self-host deployment.
    """
    pool = _get_pool()
    settings = _get_settings()

    # app_service has BYPASSRLS -- safe to use for login lookup.
    # app_user does NOT have SELECT on hanbang_rag_user (06_grants.sql).
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            SELECT id::text, password_hash, role
            FROM hanbang_rag_user
            WHERE email = %s
            """,
            (req.email,),
        )
        row = await cur.fetchone()

    if row is None:
        # Always call bcrypt to prevent timing oracle (email enumeration)
        _bcrypt_verify(req.password, _DUMMY_HASH.decode("utf-8"))
        raise HTTPException(status_code=401, detail=_LOGIN_FAIL_MSG)

    # row columns: id, password_hash, role (positional)
    user_id: str = row[0]
    password_hash: str = row[1]
    role: str = row[2]

    if not _bcrypt_verify(req.password, password_hash):
        raise HTTPException(status_code=401, detail=_LOGIN_FAIL_MSG)

    token = auth.mint_token(user_id, settings.jwt_secret)
    return LoginResponse(token=token, user_id=user_id, role=role)


@app.get("/health", response_model=HealthResponse, tags=["ops"])
async def health():
    """Shallow liveness probe: returns 200 + {"status": "ok"}.

    No internal component state is exposed. Use /health/detail for deep probe.
    """
    return HealthResponse(status="ok")


@app.get("/health/detail", response_model=HealthDetailResponse, tags=["ops"])
async def health_detail(
    _: Annotated[None, Depends(_service_token_dep)],
):
    """Deep health check: DB pool + embed sidecar reachability.

    Requires X-Service-Token header (same credential as /ingest).
    Not for public/liveness use -- internal ops only.
    """
    pool = _get_pool()
    db_ok = False
    embed_ok = False

    try:
        async with pool.connection() as conn:
            await conn.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False

    embedder = _embedder
    if embedder is not None:
        embed_ok = embedder.health_check()

    overall = "ok" if (db_ok and embed_ok) else "degraded"
    return HealthDetailResponse(
        status=overall,
        db_pool="ok" if db_ok else "error",
        embed_sidecar="ok" if embed_ok else "error",
    )


@app.post("/ingest", response_model=IngestResponse, tags=["ingest"])
async def ingest(
    req: IngestRequest,
    _: Annotated[None, Depends(_service_token_dep)],
):
    """Ingest a notice file into hanbang_rag_document_chunk.

    Requires X-Service-Token header. File must resolve under HANBANG_RAG_INGEST_ROOT.
    Idempotent: re-ingest overwrites existing chunks for the same source_id.
    source_type is always 'notice' -- no other source types in hanbang-rag.

    Gap-3 invariant: source_id must exist in hanbang_rag_notice before ingest.
    ingest.validate_source_exists() enforces this.
    """
    settings = _get_settings()
    pool = _get_pool()
    embedder = _get_embedder()

    try:
        uuid.UUID(req.source_id)
    except ValueError:
        raise HTTPException(400, f"source_id is not a valid UUID: {req.source_id!r}")

    # Path-traversal guard -- file_path must resolve under ingest_root
    ingest_root = os.path.realpath(settings.ingest_root)
    safe_path = os.path.realpath(req.file_path)
    if not safe_path.startswith(ingest_root + os.sep) and safe_path != ingest_root:
        raise HTTPException(400, "파일 경로가 허용 범위를 벗어났습니다.")

    async with pool.connection() as conn:
        try:
            n = await ingest_mod.ingest_file(
                conn=conn,
                embed_client=embedder,
                model_version=settings.embed_model_version,
                file_path=safe_path,
                source_type="notice",
                source_id=req.source_id,
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
    )


_SEARCH_MAX_TOP_K = 50  # hard cap matching SearchRequest.top_k le=50


@app.post("/search", response_model=SearchResponse, tags=["search"])
async def search(
    req: SearchRequest,
    user_id: Annotated[str, Depends(_user_dep)],
):
    """Hybrid search: FTS + vector ANN + RRF over 한방 급여 고시 chunks.

    Requires Authorization: Bearer <JWT>.
    user_id is extracted from JWT sub claim -- body does not carry it.
    Does NOT generate an LLM answer (Lite tier guarantee).
    """
    settings = _get_settings()
    pool = _get_pool()

    t0 = time.monotonic()
    eff_top_k = min(req.top_k or settings.top_k, _SEARCH_MAX_TOP_K)

    query_vec = _embed_or_503(req.query)

    async with pool.connection() as conn:
        async with database.rls_session(conn, user_id):
            chunks = await retrieve_mod.hybrid_search(
                conn=conn,
                query_text=req.query,
                query_embedding=query_vec,
                top_k=eff_top_k,
                rrf_k=settings.rrf_k,
                fts_limit=settings.fts_candidate_limit,
                ann_limit=settings.ann_candidate_limit,
                min_relevance=settings.search_min_relevance,
                match_mode=req.match_mode,
            )
            citations = await citation_mod.resolve_citations(
                conn=conn,
                chunks=chunks,
            )
            latency_ms = int((time.monotonic() - t0) * 1000)
            log_id = await citation_mod.log_query(
                conn=conn,
                user_id=user_id,
                query_text=req.query,
                query_embedding=query_vec,
                citations=citations,
                latency_ms=latency_ms,
            )

    results_out: list[CitationOut] = [
        CitationOut(
            chunk_id=cit.chunk_id,
            source_id=cit.source_id,
            chunk_index=cit.chunk_index,
            chunk_text_excerpt=cit.chunk_text_excerpt,
            rrf_score=cit.rrf_score,
            notice_number=cit.notice_number,
            ministry=cit.ministry,
            issued_date=cit.issued_date,
            summary=cit.summary,
        )
        for cit in citations
    ]

    return SearchResponse(
        query_log_id=log_id,
        total_results=len(results_out),
        results=results_out,
    )


@app.get("/documents/notice/{notice_id}", response_model=NoticeResponse, tags=["documents"])
async def get_notice(
    notice_id: str,
    user_id: Annotated[str, Depends(_user_dep)],
):
    """Fetch full original notice text for slide-over display.

    Returns full_text from hanbang_rag_notice.
    This is the raw government notice, NOT an AI-generated answer.
    Displayed to the user to convey citation trust:
    "이건 AI 답변 아니라 고시 원문입니다."

    Requires Authorization: Bearer <JWT>.
    app_user has SELECT on hanbang_rag_notice (06_grants.sql).
    """
    try:
        uuid.UUID(notice_id)
    except ValueError:
        raise HTTPException(400, f"notice_id is not a valid UUID: {notice_id!r}")

    pool = _get_pool()

    async with pool.connection() as conn:
        async with database.rls_session(conn, user_id):
            cur = await conn.execute(
                """
                SELECT id::text, notice_number, ministry,
                       issued_date::text, summary, full_text
                FROM hanbang_rag_notice
                WHERE id = %s::uuid
                """,
                (notice_id,),
            )
            row = await cur.fetchone()

    if row is None:
        raise HTTPException(404, f"Notice {notice_id!r} not found.")

    return NoticeResponse(
        id=row[0],
        notice_number=row[1],
        ministry=row[2],
        issued_date=row[3],
        summary=row[4],
        full_text=row[5],
    )


# ── Static frontend ────────────────────────────────────────────────────────────
# Mounted last so API routes take precedence over the catch-all html=True handler.
# Serves the vanilla JS SPA at /app/ (index.html). Conditional mount: if web/ is
# absent (e.g. dev checkout without built assets) the API still boots cleanly.
_WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
if os.path.isdir(_WEB_DIR):
    app.mount("/app", StaticFiles(directory=_WEB_DIR, html=True), name="web")
