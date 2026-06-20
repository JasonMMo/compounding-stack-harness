"""
api.py — FastAPI application for legal RAG service.

Endpoints:
  POST /auth/login — email+password → JWT (attorney login)
  GET  /cases      — list assigned cases with doc ingest status (Bearer JWT)
  POST /ingest     — ingest a file (PDF/DOCX/txt) into legal_document_chunk
  POST /search     — hybrid search (FTS+ANN+RRF), return ranked chunks + citations
  GET  /documents/{source_type}/{source_id} — fetch full source document (Bearer JWT)
  GET  /health        — shallow liveness probe ({"status":"ok"}, no internals)
  GET  /health/detail — deep health check (DB+sidecar), requires X-Service-Token
  GET  /app/*      — static files (vanilla frontend)

AUTH CONTRACTS (B-1):
  /search:  Authorization: Bearer <JWT>
            JWT must be HS256, signed with LEGAL_RAG_JWT_SECRET.
            `sub` claim = attorney UUID → used as app.current_user_id for RLS.
            Body does NOT carry attorney_id (removed).
  /ingest:  X-Service-Token: <token>
            Must equal LEGAL_RAG_SERVICE_TOKEN env var. Static service credential.
  /auth/login: email + password in JSON body. Returns JWT on success.
               Always 401 on failure (no email enumeration).

DESIGN CONTRACTS:
  - /search returns chunks + citations only (Lite tier). No answer_text generated.
  - Cloud embedding API is never called (EmbedSidecarUnavailable = 503).
  - /ingest file_path validated against LEGAL_RAG_INGEST_ROOT (path-traversal guard).

Run from services/legal-rag/:
  uvicorn api:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import auth as auth_mod
import config as cfg
import db as database
import embed_client as ec
import ingest as ingest_mod
import retrieve as retrieve_mod
import citation as citation_mod

logger = logging.getLogger(__name__)

# ── App state ─────────────────────────────────────────────────────────────────

# Settings are loaded eagerly at import time so that FastAPI app creation can
# conditionally disable auto-docs in prod mode.  Lifespan reuses this instance
# instead of calling cfg.load() a second time.
_settings: cfg.Settings = cfg.load()
_pool = None
_embedder: ec.EmbedClient | None = None


# ── Typed accessors ───────────────────────────────────────────────────────────

def _get_settings() -> cfg.Settings:
    return _settings


def _get_pool():
    assert _pool is not None, "DB pool not initialized — lifespan not complete"
    return _pool


def _get_embedder() -> ec.EmbedClient:
    assert _embedder is not None, "EmbedClient not initialized — lifespan not complete"
    return _embedder


# ── FastAPI dependency instances (bound to _get_settings at module level) ────

_attorney_dep = auth_mod.make_attorney_dep(_get_settings)
_service_token_dep = auth_mod.make_service_token_dep(_get_settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pool, _embedder

    # _settings already loaded at module import time (cfg.load() called above).
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


_docs_kwargs: dict = (
    {"docs_url": None, "redoc_url": None, "openapi_url": None}
    if _settings.env == "prod"
    else {}
)
app = FastAPI(
    title="Legal RAG Service",
    description=(
        "Hybrid search (FTS + vector ANN + RRF) over legal precedents "
        "and case documents. Lite tier: returns ranked chunks + citations only. "
        "LLM answer generation is NOT implemented (Pro tier gate)."
    ),
    version="0.1.0",
    lifespan=lifespan,
    **_docs_kwargs,
)


# ── Security helpers ──────────────────────────────────────────────────────────

def _validate_ingest_path(file_path: str, ingest_root: str) -> str:
    """Resolve file_path and verify it is under ingest_root.

    Uses os.path.realpath to normalise symlinks and .. traversal.
    Raises HTTPException(400) if the resolved path escapes ingest_root.
    """
    resolved = os.path.realpath(os.path.abspath(file_path))
    root = os.path.realpath(os.path.abspath(ingest_root))

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
    """Search request. attorney_id is derived from JWT — do NOT supply in body."""

    query: str = Field(..., min_length=1, description="Search query text (Korean/mixed).")
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
    relevance: float | None = None
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


class HealthDetailResponse(BaseModel):
    status: str
    db_pool: str
    embed_sidecar: str


class LoginRequest(BaseModel):
    email: str = Field(..., description="Attorney email address.")
    password: str = Field(..., description="Attorney password (plaintext, TLS in transit).")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    attorney_id: str
    display_name: str


class CaseOut(BaseModel):
    case_id: str
    case_number: str
    title: str
    status: str
    doc_total: int
    doc_indexed: int
    doc_pending: int
    doc_failed: int


class CasesResponse(BaseModel):
    cases: list[CaseOut]
    total: int


class DocumentResponse(BaseModel):
    source_type: str
    source_id: str
    title: str | None = None
    citation: str | None = None
    court: str | None = None
    decided_date: str | None = None
    case_type: str | None = None
    keywords: str | None = None
    document_type: str | None = None
    filed_at: str | None = None
    body: str | None = None
    body_is_holding_fallback: bool = False


class CaseDocumentItem(BaseModel):
    doc_id: str
    title: str | None = None
    document_type: str | None = None
    ingest_status: str | None = None


class CaseDetailResponse(BaseModel):
    case_id: str
    case_number: str
    title: str
    status: str
    case_type: str | None = None
    description: str | None = None
    opened_at: str | None = None
    closed_at: str | None = None
    documents: list[CaseDocumentItem]


# ── Login helper ──────────────────────────────────────────────────────────────

_LOGIN_FAIL_MSG = "이메일 또는 비밀번호가 올바르지 않습니다."

# 임의 비번과 일치하지 않는 유효 bcrypt 해시 — 이메일 열거 타이밍가드용.
# 이 해시는 실제 비밀번호와 절대 일치하지 않으며, 존재하지 않는 이메일 조회 시
# bcrypt.checkpw 를 한 번 수행해 응답 시간을 실제 검증과 유사하게 맞춘다.
# 분리 연결 금지 — 단일 리터럴이어야 bcrypt 포맷 60바이트 조건을 충족한다.
_DUMMY_HASH = b"$2b$12$WZ0mFgAfr0FC4XCL6GzSY.yyKVdGxcp5TSNqAYfdlQ/g1/STGB6ga"


def _bcrypt_verify(password: str, password_hash: str) -> bool:
    """Constant-time bcrypt verification. Returns True if password matches hash."""
    try:
        import bcrypt  # lazy import — available at runtime
    except ImportError as exc:
        raise ImportError(
            "bcrypt is required for login. Install: pip install 'bcrypt>=4.0,<5.0'"
        ) from exc
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/auth/login", response_model=LoginResponse, tags=["auth"])
async def login(req: LoginRequest):
    """Authenticate an attorney by email + password and return a JWT.

    Uses app_service (BYPASSRLS) connection to look up the attorney row.
    bcrypt.checkpw is always called (even for unknown emails) to prevent
    timing-based email enumeration. Both wrong-email and wrong-password
    return 401 with an identical message.

    TIMING NOTE: For unknown emails, a dummy hash is checked so response
    time is similar to a real bcrypt comparison. This is not perfect
    constant-time (hash existence leaks), but is sufficient for MVP
    self-host deployment where the attorney count is small and the service
    is internal-only.
    """
    pool = _get_pool()
    settings = _get_settings()

    # app_service has BYPASSRLS — safe to use for login lookup
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            SELECT id::text, password_hash, is_active, display_name
            FROM legal_attorney
            WHERE email = %s
            """,
            (req.email,),
        )
        row = await cur.fetchone()

    if row is None:
        # Always call bcrypt to prevent timing oracle (email enumeration)
        _bcrypt_verify(req.password, _DUMMY_HASH.decode("utf-8"))
        raise HTTPException(status_code=401, detail=_LOGIN_FAIL_MSG)

    # row columns: id, password_hash, is_active, display_name (positional)
    attorney_id: str = row[0]
    password_hash: str = row[1]
    is_active: bool = row[2]
    display_name: str = row[3]

    if not _bcrypt_verify(req.password, password_hash):
        raise HTTPException(status_code=401, detail=_LOGIN_FAIL_MSG)

    if not is_active:
        raise HTTPException(status_code=401, detail=_LOGIN_FAIL_MSG)

    token = auth_mod.mint_token(attorney_id, settings.jwt_secret)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        attorney_id=attorney_id,
        display_name=display_name,
    )


@app.get("/cases", response_model=CasesResponse, tags=["cases"])
async def list_cases(
    attorney_id: Annotated[str, Depends(_attorney_dep)],
):
    """List cases assigned to the authenticated attorney, with document ingest status.

    RLS enforces that only cases where assigned_attorney_id or partner_id
    matches the JWT sub claim are returned. Document counts are aggregated
    per case from legal_case_document.ingest_status.

    ingest_status values from DDL: 'pending' | 'processing' | 'done' | 'error' | NULL
    UI maps: done→indexed, pending+processing→pending, error→failed.
    """
    pool = _get_pool()

    async with pool.connection() as conn:
        async with database.rls_session(conn, attorney_id):
            cur = await conn.execute(
                """
                SELECT
                  lc.id::text            AS case_id,
                  lc.case_number,
                  lc.title,
                  lc.status,
                  COUNT(lcd.id)          AS doc_total,
                  COUNT(lcd.id) FILTER (WHERE lcd.ingest_status = 'done')
                                         AS doc_indexed,
                  COUNT(lcd.id) FILTER (
                    WHERE lcd.ingest_status IN ('pending', 'processing')
                       OR lcd.ingest_status IS NULL
                  )                      AS doc_pending,
                  COUNT(lcd.id) FILTER (WHERE lcd.ingest_status = 'error')
                                         AS doc_failed
                FROM legal_case lc
                LEFT JOIN legal_case_document lcd ON lcd.case_id = lc.id
                GROUP BY lc.id, lc.case_number, lc.title, lc.status
                ORDER BY lc.case_number
                """,
            )
            rows = await cur.fetchall()

    # row columns (positional): case_id, case_number, title, status,
    #                           doc_total, doc_indexed, doc_pending, doc_failed
    cases = [
        CaseOut(
            case_id=r[0],
            case_number=r[1],
            title=r[2],
            status=r[3],
            doc_total=r[4],
            doc_indexed=r[5],
            doc_pending=r[6],
            doc_failed=r[7],
        )
        for r in rows
    ]
    return CasesResponse(cases=cases, total=len(cases))


@app.get("/cases/{case_id}", response_model=CaseDetailResponse, tags=["cases"])
async def get_case(
    case_id: str,
    attorney_id: Annotated[str, Depends(_attorney_dep)],
):
    """Fetch a single case and its document list (read-only, S-16).

    Requires Authorization: Bearer <JWT>.
    RLS enforces visibility: only cases where assigned_attorney_id or partner_id
    matches the JWT sub claim are returned. If the case exists but the attorney
    has no access, the result is 0 rows → 404 (existence not disclosed).

    UUID format error → 400.
    """
    try:
        uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(400, f"case_id is not a valid UUID: {case_id!r}")

    pool = _get_pool()

    async with pool.connection() as conn:
        async with database.rls_session(conn, attorney_id):
            # Case meta — RLS filters cross-attorney rows
            cur = await conn.execute(
                """
                SELECT
                  id::text,
                  case_number,
                  title,
                  status,
                  case_type,
                  description,
                  opened_at::text,
                  closed_at::text
                FROM legal_case
                WHERE id = %s
                """,
                (case_id,),
            )
            row = await cur.fetchone()

            if row is None:
                # 404: cross-attorney case or non-existent — same response (existence not disclosed)
                raise HTTPException(status_code=404, detail="사건을 찾을 수 없습니다.")

            (
                _case_id, case_number, title, status,
                case_type, description, opened_at, closed_at,
            ) = row

            # Document list for this case (RLS already scoped by session above)
            dcur = await conn.execute(
                """
                SELECT
                  id::text,
                  title,
                  document_type,
                  ingest_status
                FROM legal_case_document
                WHERE case_id = %s
                ORDER BY filed_at NULLS LAST, id
                """,
                (case_id,),
            )
            doc_rows = await dcur.fetchall()

    documents = [
        CaseDocumentItem(
            doc_id=dr[0],
            title=dr[1],
            document_type=dr[2],
            ingest_status=dr[3],
        )
        for dr in doc_rows
    ]

    return CaseDetailResponse(
        case_id=_case_id,
        case_number=case_number,
        title=title,
        status=status,
        case_type=case_type,
        description=description,
        opened_at=opened_at,
        closed_at=closed_at,
        documents=documents,
    )


@app.get("/health", response_model=HealthResponse, tags=["ops"])
async def health():
    """Shallow liveness probe: returns 200 + {"status": "ok"}.

    No internal component state is exposed to prevent infrastructure
    reconnaissance. Coolify/Traefik liveness probes only need 200.
    """
    return HealthResponse(status="ok")


@app.get("/health/detail", response_model=HealthDetailResponse, tags=["ops"])
async def health_detail(
    _: Annotated[None, Depends(_service_token_dep)],
):
    """Deep health check: DB pool + embed sidecar reachability.

    Requires X-Service-Token header (same credential as /ingest).
    Not for public/liveness use — internal ops only.
    """
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
    """Ingest a file into legal_document_chunk.

    Requires X-Service-Token header. File must be under LEGAL_RAG_INGEST_ROOT.
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
async def search(
    req: SearchRequest,
    attorney_id: Annotated[str, Depends(_attorney_dep)],
):
    """Hybrid search: FTS + vector ANN + RRF.

    Requires Authorization: Bearer <JWT>.
    attorney_id is extracted from JWT `sub` claim — body does not carry it.
    DOES NOT generate an LLM answer (Lite tier guarantee).
    """
    settings = _get_settings()
    pool = _get_pool()

    if req.case_id:
        try:
            uuid.UUID(req.case_id)
        except ValueError:
            raise HTTPException(400, f"case_id is not a valid UUID: {req.case_id!r}")

    top_k = req.top_k or settings.top_k
    t0 = time.monotonic()

    query_vec = _embed_or_503(req.query)

    async with pool.connection() as conn:
        async with database.rls_session(conn, attorney_id):
            chunks = await retrieve_mod.hybrid_search(
                conn=conn,
                query_text=req.query,
                query_embedding=query_vec,
                top_k=top_k,
                fts_limit=settings.fts_candidate_limit,
                ann_limit=settings.ann_candidate_limit,
                rrf_k=settings.rrf_k,
                min_relevance=settings.search_min_relevance,
            )
            citations = await citation_mod.resolve_citations(
                conn=conn,
                chunks=chunks,
            )
            latency_ms = int((time.monotonic() - t0) * 1000)
            log_id = await citation_mod.log_query(
                conn=conn,
                attorney_id=attorney_id,
                query_text=req.query,
                query_embedding=query_vec,
                citations=citations,
                case_id=req.case_id,
                latency_ms=latency_ms,
            )

    chunk_rank_map = {
        c.chunk_id: (c.fts_rank, c.ann_rank, c.relevance) for c in chunks
    }
    results_out = []
    for cit in citations:
        fts_r, ann_r, relevance = chunk_rank_map.get(cit.chunk_id, (None, None, None))
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
                relevance=relevance,
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


@app.get("/documents/{source_type}/{source_id}", response_model=DocumentResponse, tags=["documents"])
async def get_document(
    source_type: str,
    source_id: str,
    attorney_id: Annotated[str, Depends(_attorney_dep)],
):
    """Fetch full source document (precedent or case_document) for slide-over view.

    Requires Authorization: Bearer <JWT>.
    RLS is applied: case_document rows not visible to the requesting attorney
    return 404 (same response as not-found — existence is not disclosed).

    source_type='precedent': returns full_text (or holding as fallback if full_text is NULL).
    source_type='case_document': returns content_text, RLS auto-filters cross-attorney rows.
    source_type=other: 400.
    """
    _VALID_SOURCE_TYPES = {"precedent", "case_document"}
    if source_type not in _VALID_SOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"source_type must be one of {sorted(_VALID_SOURCE_TYPES)}",
        )

    try:
        uuid.UUID(source_id)
    except ValueError:
        raise HTTPException(400, f"source_id is not a valid UUID: {source_id!r}")

    pool = _get_pool()

    async with pool.connection() as conn:
        async with database.rls_session(conn, attorney_id):
            if source_type == "precedent":
                cur = await conn.execute(
                    """
                    SELECT
                        citation,
                        court,
                        decided_date::text,
                        case_type,
                        holding,
                        full_text,
                        keywords
                    FROM legal_precedent
                    WHERE id = %s
                    """,
                    (source_id,),
                )
                row = await cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="원문을 찾을 수 없습니다.")

                citation, court, decided_date, case_type, holding, full_text, keywords = row
                body_is_fallback = full_text is None
                body = full_text if not body_is_fallback else holding

                return DocumentResponse(
                    source_type=source_type,
                    source_id=source_id,
                    title=citation,
                    citation=citation,
                    court=court,
                    decided_date=decided_date,
                    case_type=case_type,
                    keywords=keywords,
                    body=body,
                    body_is_holding_fallback=body_is_fallback,
                )

            else:  # case_document
                cur = await conn.execute(
                    """
                    SELECT
                        document_type,
                        title,
                        filed_at::text,
                        content_text
                    FROM legal_case_document
                    WHERE id = %s
                    """,
                    (source_id,),
                )
                row = await cur.fetchone()
                # 0 rows: either doesn't exist or RLS hid it — return 404 without disclosing
                if row is None:
                    raise HTTPException(status_code=404, detail="원문을 찾을 수 없습니다.")

                document_type, title, filed_at, content_text = row

                return DocumentResponse(
                    source_type=source_type,
                    source_id=source_id,
                    title=title,
                    document_type=document_type,
                    filed_at=filed_at,
                    body=content_text,
                    body_is_holding_fallback=False,
                )


# ── Static frontend ────────────────────────────────────────────────────────────
# Mounted last so API routes take precedence over the catch-all html=True handler.
# Serves the vanilla JS SPA at /app/ (index.html).

_WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
app.mount("/app", StaticFiles(directory=_WEB_DIR, html=True), name="web")
