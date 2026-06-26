"""
tests/test_ingest_unit.py — Gap-2: ingest_file() state machine unit tests.

Covers:
  - pending → processing → done (happy path, case_document)
  - empty text early-return → error status
  - chunk batch upsert (executemany called with correct rows)
  - source_id not found → SourceNotFoundError (Gap-3, skip if not patched)

Uses unittest.mock for DB conn + EmbedClient. No real DB or sidecar.
"""
import sys
import os
import uuid
import importlib.util
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

import pytest

# ── Import ingest module (patched version preferred) ─────────────────────────

def _try_load_patched(name: str, patched_path: str):
    """Load a .patched file as Python module, or return None on failure."""
    if not os.path.exists(patched_path):
        return None
    # Read file, compile, exec in fresh namespace
    with open(patched_path, encoding="utf-8") as fh:
        source = fh.read()
    code = compile(source, patched_path, "exec")
    ns: dict = {"__name__": name, "__file__": patched_path}
    try:
        exec(code, ns)
    except Exception:
        return None
    # Wrap namespace as a simple object
    class _Mod:
        pass
    mod = _Mod()
    for k, v in ns.items():
        setattr(mod, k, v)
    return mod


_patched_path = os.path.join(_PARENT, "ingest.py.patched")
_ingest_patched = _try_load_patched("ingest_patched", _patched_path)

import ingest as _ingest_current

# Use patched if available, else current
_ingest = _ingest_patched if _ingest_patched is not None else _ingest_current

chunk_text = _ingest.chunk_text
ingest_file = _ingest.ingest_file
extract_text = _ingest.extract_text

# Gap-3 availability
_has_gap3 = hasattr(_ingest, "SourceNotFoundError")
if _has_gap3:
    SourceNotFoundError = _ingest.SourceNotFoundError
    validate_source_exists = _ingest.validate_source_exists


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_mock_conn(source_exists: bool = True):
    """Build a mock psycopg AsyncConnection mirroring the real psycopg3 API.

    Real API:
      - conn.execute(sql, params)  → coroutine returning a cursor  (shortcut, real)
      - conn.cursor()              → async context manager → cursor with .executemany
    """
    conn = MagicMock()

    async def _execute(sql, params=None):
        cursor = MagicMock()
        if "SELECT 1 FROM" in sql:
            cursor.fetchone = AsyncMock(return_value=(1,) if source_exists else None)
        else:
            cursor.fetchone = AsyncMock(return_value=None)
        return cursor

    conn.execute = AsyncMock(side_effect=_execute)

    # cursor() must be an async context manager whose __aenter__ yields a cursor
    mock_cursor = MagicMock()
    mock_cursor.executemany = AsyncMock(return_value=None)

    async def _cursor_aenter():
        return mock_cursor

    async def _cursor_aexit(*args):
        pass

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(side_effect=_cursor_aenter)
    cm.__aexit__ = AsyncMock(side_effect=_cursor_aexit)
    conn.cursor = MagicMock(return_value=cm)

    # Expose the inner cursor so tests can assert on it
    conn._mock_cursor = mock_cursor
    return conn


def _make_mock_embedder(dim: int = 768):
    embedder = MagicMock()
    embedder.embed_batch = MagicMock(
        side_effect=lambda texts: [[0.1] * dim for _ in texts]
    )
    return embedder


def _make_text_file(tmp_path: Path, content: str, suffix: str = ".txt") -> Path:
    f = tmp_path / f"doc{suffix}"
    f.write_text(content, encoding="utf-8")
    return f


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ingest_happy_path_precedent(tmp_path):
    """Happy path: precedent, full pipeline, chunks returned >= 1."""
    content = "판례 내용입니다. " * 20
    file = _make_text_file(tmp_path, content)
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=True)
    embedder = _make_mock_embedder()

    result = await ingest_file(
        conn=conn,
        embed_client=embedder,
        model_version="test-model",
        file_path=str(file),
        source_type="precedent",
        source_id=source_id,
        chunk_token_target=50,
        chunk_overlap_tokens=0,
        batch_size=10,
    )

    assert result >= 1
    assert conn._mock_cursor.executemany.called
    assert embedder.embed_batch.called
    for call_args in embedder.embed_batch.call_args_list:
        texts = call_args[0][0]
        assert all(t.strip() for t in texts)


@pytest.mark.asyncio
async def test_ingest_case_document_status_transitions(tmp_path):
    """case_document: status processing → done, two UPDATE calls."""
    content = "계약서 내용입니다. " * 10
    file = _make_text_file(tmp_path, content)
    source_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())

    executed_sqls: list[str] = []

    conn = MagicMock()

    async def _execute(sql, params=None):
        executed_sqls.append(sql.strip())
        cursor = MagicMock()
        cursor.fetchone = AsyncMock(return_value=(1,))
        return cursor

    conn.execute = AsyncMock(side_effect=_execute)

    _cur2 = MagicMock()
    _cur2.executemany = AsyncMock(return_value=None)
    _cm2 = MagicMock()
    _cm2.__aenter__ = AsyncMock(return_value=_cur2)
    _cm2.__aexit__ = AsyncMock(return_value=None)
    conn.cursor = MagicMock(return_value=_cm2)

    embedder = _make_mock_embedder()

    await ingest_file(
        conn=conn,
        embed_client=embedder,
        model_version="test-model",
        file_path=str(file),
        source_type="case_document",
        source_id=source_id,
        case_id=case_id,
        chunk_token_target=50,
        chunk_overlap_tokens=0,
    )

    update_sqls = [s for s in executed_sqls if "UPDATE legal_case_document" in s]
    assert len(update_sqls) >= 2, f"Expected >=2 UPDATE calls, got: {update_sqls}"


@pytest.mark.asyncio
async def test_ingest_empty_text_early_return(tmp_path):
    """Empty file → 0 chunks, error status, no embed calls."""
    file = _make_text_file(tmp_path, "   \n\n  ")
    source_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=True)
    embedder = _make_mock_embedder()

    result = await ingest_file(
        conn=conn,
        embed_client=embedder,
        model_version="test-model",
        file_path=str(file),
        source_type="case_document",
        source_id=source_id,
        case_id=case_id,
    )

    assert result == 0
    assert not embedder.embed_batch.called

    calls_with_error = [
        c for c in conn.execute.call_args_list
        if c.args and len(c.args) > 1 and c.args[1] and c.args[1][0] == "error"
    ]
    assert len(calls_with_error) >= 1


@pytest.mark.asyncio
async def test_ingest_batch_upsert_rows_correct(tmp_path):
    """executemany rows have correct (source_type, source_id, model_version)."""
    content = "내용 " * 30
    file = _make_text_file(tmp_path, content)
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=True)
    embedder = _make_mock_embedder()

    await ingest_file(
        conn=conn,
        embed_client=embedder,
        model_version="v1",
        file_path=str(file),
        source_type="precedent",
        source_id=source_id,
        chunk_token_target=30,
        chunk_overlap_tokens=0,
        batch_size=5,
    )

    assert conn._mock_cursor.executemany.called
    all_rows: list = []
    for c in conn._mock_cursor.executemany.call_args_list:
        all_rows.extend(c.args[1])

    for row in all_rows:
        assert row[0] == "precedent"
        assert row[1] == source_id
        assert row[2] is None           # case_id_str (None for precedent)
        assert isinstance(row[3], int)  # chunk_index
        assert isinstance(row[4], str)  # chunk_text
        assert row[8] == "v1"           # model_version


@pytest.mark.asyncio
async def test_ingest_invalid_source_type_raises():
    conn = _make_mock_conn()
    embedder = _make_mock_embedder()

    with pytest.raises(ValueError, match="source_type"):
        await ingest_file(
            conn=conn,
            embed_client=embedder,
            model_version="v1",
            file_path="/tmp/x.txt",
            source_type="invalid",
            source_id=str(uuid.uuid4()),
        )


@pytest.mark.asyncio
async def test_ingest_case_document_requires_case_id():
    conn = _make_mock_conn()
    embedder = _make_mock_embedder()

    with pytest.raises(ValueError, match="case_id"):
        await ingest_file(
            conn=conn,
            embed_client=embedder,
            model_version="v1",
            file_path="/tmp/x.txt",
            source_type="case_document",
            source_id=str(uuid.uuid4()),
            case_id=None,
        )


# ── Gap-3: source existence validation ────────────────────────────────────────

@pytest.mark.skipif(not _has_gap3, reason="Gap-3 not in current ingest.py — apply ingest.py.patched")
@pytest.mark.asyncio
async def test_validate_source_exists_found():
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=True)
    await validate_source_exists(conn, "precedent", source_id)


@pytest.mark.skipif(not _has_gap3, reason="Gap-3 not in current ingest.py — apply ingest.py.patched")
@pytest.mark.asyncio
async def test_validate_source_exists_not_found_raises():
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=False)
    with pytest.raises(SourceNotFoundError):
        await validate_source_exists(conn, "precedent", source_id)


@pytest.mark.asyncio
async def test_reingest_shorter_removes_orphan_chunks(tmp_path):
    """재인제스트 시 청크 수 축소 → 고아 청크 삭제 확인.

    1. 긴 텍스트 ingest → N청크 upsert 확인
    2. 같은 source_id로 짧은 텍스트 재ingest → M(<N) 청크
    3. DELETE 호출의 마지막 인자(threshold)가 정확히 M임을 assert
       (즉, chunk_index >= M 이상 행을 삭제하는 올바른 orphan 삭제 요청)
    """
    source_id = str(uuid.uuid4())
    embedder = _make_mock_embedder()

    # ── 1차 ingest: 긴 텍스트 ──────────────────────────────────────────────────
    long_text = "판례 내용입니다. " * 60  # token_target=30 기준 여러 청크 생성
    file_long = _make_text_file(tmp_path, long_text, suffix=".txt")

    delete_calls_first: list[tuple] = []

    conn1 = _make_mock_conn(source_exists=True)
    _orig_execute1 = conn1.execute.side_effect

    async def _execute1_spy(sql, params=None):
        if "DELETE FROM legal_document_chunk" in sql and params:
            delete_calls_first.append(params)
        return await _orig_execute1(sql, params)

    conn1.execute = AsyncMock(side_effect=_execute1_spy)

    chunks_first = await ingest_file(
        conn=conn1,
        embed_client=embedder,
        model_version="v1",
        file_path=str(file_long),
        source_type="precedent",
        source_id=source_id,
        chunk_token_target=30,
        chunk_overlap_tokens=0,
        batch_size=10,
    )
    assert chunks_first >= 2, "긴 텍스트는 2개 이상 청크를 생성해야 한다"
    assert len(delete_calls_first) == 1, "orphan DELETE가 1회 호출되어야 한다"
    # 1차: orphan threshold == 전체 청크 수 (삭제 대상 없음이지만 DELETE는 실행)
    assert delete_calls_first[0][2] == chunks_first

    # ── 2차 ingest: 짧은 텍스트 (1청크만 생성) ──────────────────────────────────
    short_text = "짧은 문서."
    file_short = _make_text_file(tmp_path, short_text, suffix=".txt")

    delete_calls_second: list[tuple] = []

    conn2 = _make_mock_conn(source_exists=True)
    _orig_execute2 = conn2.execute.side_effect

    async def _execute2_spy(sql, params=None):
        if "DELETE FROM legal_document_chunk" in sql and params:
            delete_calls_second.append(params)
        return await _orig_execute2(sql, params)

    conn2.execute = AsyncMock(side_effect=_execute2_spy)

    chunks_second = await ingest_file(
        conn=conn2,
        embed_client=embedder,
        model_version="v1",
        file_path=str(file_short),
        source_type="precedent",
        source_id=source_id,
        chunk_token_target=30,
        chunk_overlap_tokens=0,
        batch_size=10,
    )
    assert chunks_second < chunks_first, "짧은 텍스트는 이전보다 적은 청크를 만들어야 한다"
    assert len(delete_calls_second) == 1, "orphan DELETE가 1회 호출되어야 한다"

    # 핵심 assert: DELETE threshold == 새 청크 수 M, 즉 chunk_index >= M 삭제
    orphan_threshold = delete_calls_second[0][2]
    assert orphan_threshold == chunks_second, (
        f"orphan DELETE threshold는 새 청크 수({chunks_second})여야 하는데 "
        f"{orphan_threshold}가 전달됐다"
    )
    # source_id, source_type 파라미터 정합성도 확인
    assert delete_calls_second[0][0] == source_id
    assert delete_calls_second[0][1] == "precedent"


@pytest.mark.skipif(not _has_gap3, reason="Gap-3 not in current ingest.py — apply ingest.py.patched")
@pytest.mark.asyncio
async def test_ingest_rejects_nonexistent_source(tmp_path):
    content = "내용입니다."
    file = _make_text_file(tmp_path, content)
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=False)
    embedder = _make_mock_embedder()

    with pytest.raises(SourceNotFoundError):
        await ingest_file(
            conn=conn,
            embed_client=embedder,
            model_version="v1",
            file_path=str(file),
            source_type="precedent",
            source_id=source_id,
        )
    assert not embedder.embed_batch.called
