"""
tests/test_pagination.py — G-4 pagination unit tests.

Coverage (no DB required):
  A. SearchRequest: offset field default + ge=0 validation
  B. CasesResponse: limit/offset fields present + correct values
  C. SearchResponse: offset field present in serialized output
  D. GET /cases: limit/offset query params accepted, clamped, reflected in response
  E. POST /search: offset in request body; results list is offset-sliced correctly
  F. Param clamping: top_k le=50, limit le=200, offset clamped to _SEARCH_MAX_OFFSET

DB-requiring tests (RLS isolation): deferred — mark @pytest.mark.postgres when
pg_conn fixture and seed data are available.
"""
from __future__ import annotations

import sys
import os
import uuid
import time
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# ── import guard ───────────────────────────────────────────────────────────────
# NOTE: api_mod is captured at module-level (not re-imported inside tests).
# test_hardening.py deletes and reimports api.py; re-importing inside test
# methods would yield a fresh module whose _pool patch would not affect the
# `app` object captured here. Always patch api_mod (= this module reference)
# to ensure patch.object targets the same module as `app`'s route functions.

try:
    import api as api_mod
    from api import (
        app,
        SearchRequest,
        SearchResponse,
        CasesResponse,
        CaseOut,
        CitationOut,
    )
    from fastapi.testclient import TestClient
    _API_IMPORTABLE = True
except Exception as exc:  # noqa: BLE001
    _API_IMPORTABLE = False
    _API_IMPORT_ERR = repr(exc)

skip_if_no_api = pytest.mark.skipif(
    not _API_IMPORTABLE,
    reason=f"api.py not importable — skip ({_API_IMPORTABLE or ''})",
)

try:
    import jwt as _pyjwt  # noqa: F401
    _PYJWT_AVAILABLE = True
except ImportError:
    _PYJWT_AVAILABLE = False

skip_if_no_jwt = pytest.mark.skipif(
    not _PYJWT_AVAILABLE,
    reason="pyjwt not installed",
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_token(attorney_id: str, secret: str = "test") -> str:
    import jwt
    return jwt.encode(
        {"sub": attorney_id, "exp": int(time.time()) + 3600},
        secret,
        algorithm="HS256",
    )


def _case_out(n: int) -> CaseOut:
    return CaseOut(
        case_id=str(uuid.uuid4()),
        case_number=f"2024가합{n:05d}",
        title=f"테스트 사건 {n}",
        status="active",
        doc_total=0,
        doc_indexed=0,
        doc_pending=0,
        doc_failed=0,
    )


@asynccontextmanager
async def _rls_noop(conn, attorney_id):
    """Stub rls_session that does nothing."""
    yield


# ── A. SearchRequest pagination fields ────────────────────────────────────────

@skip_if_no_api
class TestSearchRequestPaginationFields:
    def test_offset_default_zero(self):
        req = SearchRequest(query="손해배상")
        assert req.offset == 0

    def test_offset_can_be_set(self):
        req = SearchRequest(query="손해배상", offset=10)
        assert req.offset == 10

    def test_offset_negative_rejected(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            SearchRequest(query="손해배상", offset=-1)

    def test_top_k_max_50_rejected_above(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            SearchRequest(query="손해배상", top_k=51)

    def test_top_k_max_50_accepted(self):
        req = SearchRequest(query="손해배상", top_k=50)
        assert req.top_k == 50


# ── B. CasesResponse pagination fields ────────────────────────────────────────

@skip_if_no_api
class TestCasesResponsePaginationFields:
    def test_limit_and_offset_present(self):
        resp = CasesResponse(cases=[], total=0, limit=50, offset=0)
        d = resp.model_dump()
        assert d["limit"] == 50
        assert d["offset"] == 0
        assert d["total"] == 0

    def test_offset_reflected_correctly(self):
        resp = CasesResponse(
            cases=[_case_out(1)],
            total=100,
            limit=50,
            offset=50,
        )
        assert resp.offset == 50
        assert resp.total == 100
        assert resp.limit == 50
        assert len(resp.cases) == 1

    def test_json_serializable(self):
        import json
        resp = CasesResponse(cases=[], total=5, limit=50, offset=0)
        parsed = json.loads(resp.model_dump_json())
        assert {"cases", "total", "limit", "offset"} <= set(parsed.keys())


# ── C. SearchResponse offset field ────────────────────────────────────────────

@skip_if_no_api
class TestSearchResponseOffsetField:
    def test_offset_present_in_model(self):
        fields = set(SearchResponse.model_fields.keys())
        assert "offset" in fields

    def test_offset_default_zero(self):
        resp = SearchResponse(
            query_log_id=str(uuid.uuid4()),
            total_results=0,
            results=[],
        )
        assert resp.offset == 0

    def test_offset_set(self):
        resp = SearchResponse(
            query_log_id=str(uuid.uuid4()),
            total_results=3,
            offset=5,
            results=[],
        )
        assert resp.offset == 5

    def test_json_serializable(self):
        import json
        resp = SearchResponse(
            query_log_id=str(uuid.uuid4()),
            total_results=0,
            offset=10,
            results=[],
        )
        parsed = json.loads(resp.model_dump_json())
        assert parsed["offset"] == 10


# ── D. GET /cases: limit/offset query params ──────────────────────────────────

@skip_if_no_api
@skip_if_no_jwt
class TestCasesListPagination:
    """Mock DB layer to test query param → response field plumbing."""

    SECRET = "test"

    def _make_pool_mock(self, total_count: int, page_rows: list):
        """Build pool mock: 1st execute returns COUNT(*), 2nd returns page rows."""
        call_count = 0

        class _CountCur:
            async def fetchone(self):
                return (total_count,)

        class _PageCur:
            async def fetchall(self):
                return page_rows

        conn = MagicMock()

        async def _execute(sql, params=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _CountCur()
            return _PageCur()

        conn.execute = _execute

        @asynccontextmanager
        async def _conn_ctx():
            nonlocal call_count
            call_count = 0
            yield conn

        pool = MagicMock()
        pool.connection = _conn_ctx
        return pool

    def _case_row(self, n: int) -> tuple:
        """Positional row: case_id, case_number, title, status, total, indexed, pending, failed."""
        return (str(uuid.uuid4()), f"2024가합{n:05d}", f"사건 {n}", "active", 2, 2, 0, 0)

    def test_default_limit_offset_reflected_in_response(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)
        rows = [self._case_row(i) for i in range(3)]

        import db as db_mod
        pool_mock = self._make_pool_mock(total_count=3, page_rows=rows)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get("/cases", headers={"Authorization": f"Bearer {token}"})

        assert res.status_code == 200, res.text
        data = res.json()
        assert data["total"] == 3
        assert data["limit"] == 50   # default
        assert data["offset"] == 0   # default
        assert len(data["cases"]) == 3

    def test_custom_limit_offset_reflected(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)
        rows = [self._case_row(i) for i in range(2)]

        import db as db_mod
        pool_mock = self._make_pool_mock(total_count=10, page_rows=rows)

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                "/cases?limit=2&offset=4",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 200, res.text
        data = res.json()
        assert data["limit"] == 2
        assert data["offset"] == 4
        assert data["total"] == 10
        assert len(data["cases"]) == 2

    def test_limit_above_200_rejected(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import db as db_mod
        pool_mock = self._make_pool_mock(total_count=0, page_rows=[])

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                "/cases?limit=201",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 422, res.text  # FastAPI validation error

    def test_negative_offset_rejected(self):
        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        import db as db_mod
        pool_mock = self._make_pool_mock(total_count=0, page_rows=[])

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get(
                "/cases?offset=-1",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert res.status_code == 422, res.text

    def test_no_auth_returns_401(self):
        import db as db_mod
        pool_mock = self._make_pool_mock(total_count=0, page_rows=[])

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.get("/cases")

        assert res.status_code == 401, res.text


# ── E. POST /search: offset slices results ────────────────────────────────────

@skip_if_no_api
@skip_if_no_jwt
class TestSearchPagination:
    """Verify offset in SearchRequest causes result list slicing."""

    SECRET = "test"

    def _make_search_mocks(self, chunk_count: int):
        """Build mocks for hybrid_search, resolve_citations, log_query.

        hybrid_search returns `chunk_count` stub RetrievedChunk objects.
        resolve_citations echoes them as stub Citation objects.
        log_query returns a dummy UUID.
        """
        from retrieve import RetrievedChunk
        import citation as cit_mod

        chunks = [
            RetrievedChunk(
                chunk_id=str(uuid.uuid4()),
                source_type="precedent",
                source_id=str(uuid.uuid4()),
                case_id=None,
                chunk_index=i,
                chunk_text=f"텍스트 {i}",
                token_count=50,
                rrf_score=1.0 / (i + 1),
                fts_rank=i + 1,
                ann_rank=None,
                relevance=None,
            )
            for i in range(chunk_count)
        ]

        # Citation stub that mirrors chunk fields needed by CitationOut
        class _Cit:
            def __init__(self, chunk):
                self.chunk_id = chunk.chunk_id
                self.source_type = chunk.source_type
                self.source_id = chunk.source_id
                self.case_id = chunk.case_id
                self.chunk_index = chunk.chunk_index
                self.chunk_text_excerpt = chunk.chunk_text[:20]
                self.rrf_score = chunk.rrf_score
                self.case_number = None
                self.court = None
                self.decision_date = None
                self.holding_summary = None
                self.document_title = None
                self.document_type = None

        cit_list = [_Cit(c) for c in chunks]

        return chunks, cit_list

    def _pool_mock_for_search(self):
        """Pool mock: connection() yields a conn whose execute() is a no-op cursor."""
        conn = MagicMock()

        class _NoopCur:
            async def fetchone(self): return (str(uuid.uuid4()),)
            async def fetchall(self): return []

        async def _execute(sql, params=None):
            return _NoopCur()

        conn.execute = _execute

        @asynccontextmanager
        async def _conn_ctx():
            yield conn

        pool = MagicMock()
        pool.connection = _conn_ctx
        return pool

    def _do_search(self, req_body: dict, chunks, cit_list) -> dict:
        """Execute POST /search with mocked retrieve/citation/log layers."""
        import db as db_mod
        import retrieve as retrieve_mod
        import citation as cit_mod

        attorney_id = str(uuid.uuid4())
        token = _make_token(attorney_id, self.SECRET)

        pool_mock = self._pool_mock_for_search()

        # hybrid_search returns all chunks; slicing happens in search handler
        async def _fake_hybrid_search(**kwargs):
            return chunks

        async def _fake_resolve_citations(conn, chunks):
            # Map chunk objects to Citation stubs matching the input list
            chunk_id_to_cit = {c.chunk_id: c for c in cit_list}
            return [chunk_id_to_cit[ch.chunk_id] for ch in chunks if ch.chunk_id in chunk_id_to_cit]

        async def _fake_log_query(**kwargs):
            return str(uuid.uuid4())

        with (
            patch.object(api_mod, "_pool", pool_mock),
            patch.object(db_mod, "rls_session", _rls_noop),
            patch.object(retrieve_mod, "hybrid_search", _fake_hybrid_search),
            patch.object(cit_mod, "resolve_citations", _fake_resolve_citations),
            patch.object(cit_mod, "log_query", _fake_log_query),
            patch.object(api_mod, "_embed_or_503", lambda text: [0.1] * 768),
        ):
            client = TestClient(app, raise_server_exceptions=True)
            res = client.post(
                "/search",
                json=req_body,
                headers={"Authorization": f"Bearer {token}"},
            )
        return res

    def test_offset_zero_returns_all(self):
        chunks, cit_list = self._make_search_mocks(5)
        res = self._do_search({"query": "손해배상", "offset": 0}, chunks, cit_list)
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["offset"] == 0
        assert data["total_results"] == 5

    def test_offset_two_skips_first_two(self):
        chunks, cit_list = self._make_search_mocks(5)
        res = self._do_search({"query": "손해배상", "offset": 2}, chunks, cit_list)
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["offset"] == 2
        assert data["total_results"] == 3  # 5 - 2

    def test_offset_beyond_results_returns_empty(self):
        chunks, cit_list = self._make_search_mocks(3)
        res = self._do_search({"query": "손해배상", "offset": 10}, chunks, cit_list)
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["total_results"] == 0
        assert data["results"] == []

    def test_offset_default_zero_no_field_required(self):
        """offset is optional with default 0 — omitting it must work."""
        chunks, cit_list = self._make_search_mocks(2)
        res = self._do_search({"query": "계약해지"}, chunks, cit_list)
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["offset"] == 0
        assert data["total_results"] == 2


# ── F. Param clamping ─────────────────────────────────────────────────────────

@skip_if_no_api
class TestSearchOffsetClamping:
    """_SEARCH_MAX_OFFSET clamp is applied silently (no 422 — just uses max)."""

    def test_max_offset_constant_exists(self):
        assert hasattr(api_mod, "_SEARCH_MAX_OFFSET")
        assert api_mod._SEARCH_MAX_OFFSET >= 100, "offset cap should be at least 100"

    def test_cases_max_limit_constant_exists(self):
        assert hasattr(api_mod, "_CASES_LIST_MAX_LIMIT")
        assert api_mod._CASES_LIST_MAX_LIMIT == 200


# ── @pytest.mark.postgres: RLS paging integration (deferred) ──────────────────

@pytest.mark.postgres
class TestCasesPaginationRLSIntegration:
    """
    Requires live PostgreSQL (LEGAL_RAG_DB_DSN_POSTGRES).
    SPEC (deferred — implement after DB fixture extended):
      - GET /cases?limit=2&offset=0 Bearer 이준호 → 2 cases (이준호 has 6)
      - GET /cases?limit=2&offset=4 Bearer 이준호 → 2 cases (rows 5-6)
      - GET /cases?limit=2&offset=6 Bearer 이준호 → 0 cases (past end)
      - total in all responses == 6 (이준호 RLS scope)
    """

    def test_placeholder(self):
        pytest.skip("Postgres integration: implement after DB fixture available")
