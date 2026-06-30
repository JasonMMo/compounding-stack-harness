"""
tests/test_ingest_unit.py — ingest_file() state machine unit tests for hanbang-rag.

Covers:
  - notice source_type happy path (ingest + embed + upsert)
  - empty text early-return (notice — no status update unlike case_document)
  - chunk batch upsert (executemany called with correct rows)
  - source_id not found → SourceNotFoundError (Gap-3)
  - orphan chunk deletion on re-ingest

한방 RAG: source_type='notice' 단일. case_document 분기 테스트 제거.
Uses unittest.mock for DB conn + EmbedClient. No real DB or sidecar.
"""
import sys
import os
import uuid
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

import pytest

import ingest as _ingest

chunk_text = _ingest.chunk_text
ingest_file = _ingest.ingest_file
extract_text = _ingest.extract_text
SourceNotFoundError = _ingest.SourceNotFoundError
validate_source_exists = _ingest.validate_source_exists


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_mock_conn(source_exists: bool = True):
    """Build a mock psycopg AsyncConnection mirroring the real psycopg3 API."""
    conn = MagicMock()

    async def _execute(sql, params=None):
        cursor = MagicMock()
        if "SELECT 1 FROM" in sql:
            cursor.fetchone = AsyncMock(return_value=(1,) if source_exists else None)
        else:
            cursor.fetchone = AsyncMock(return_value=None)
        return cursor

    conn.execute = AsyncMock(side_effect=_execute)

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
async def test_ingest_happy_path_notice(tmp_path):
    """Happy path: notice source_type, full pipeline, chunks returned >= 1."""
    content = "첩약 급여 고시 내용입니다. " * 20
    file = _make_text_file(tmp_path, content)
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=True)
    embedder = _make_mock_embedder()

    result = await ingest_file(
        conn=conn,
        embed_client=embedder,
        model_version="test-model",
        file_path=str(file),
        source_type="notice",
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
async def test_ingest_empty_text_early_return(tmp_path):
    """Empty file → 0 chunks, no embed calls. Notice has no status update."""
    file = _make_text_file(tmp_path, "   \n\n  ")
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=True)
    embedder = _make_mock_embedder()

    result = await ingest_file(
        conn=conn,
        embed_client=embedder,
        model_version="test-model",
        file_path=str(file),
        source_type="notice",
        source_id=source_id,
    )

    assert result == 0
    assert not embedder.embed_batch.called
    # Notice pipeline has no status UPDATE on empty text (unlike case_document)
    # Only the Gap-3 SELECT 1 FROM hanbang_rag_notice should have been called.
    select_calls = [
        c for c in conn.execute.call_args_list
        if c.args and "SELECT 1 FROM" in str(c.args[0])
    ]
    assert len(select_calls) >= 1


@pytest.mark.asyncio
async def test_ingest_batch_upsert_rows_correct(tmp_path):
    """executemany rows have correct (source_type='notice', source_id, model_version)."""
    content = "고시 내용 " * 30
    file = _make_text_file(tmp_path, content)
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=True)
    embedder = _make_mock_embedder()

    await ingest_file(
        conn=conn,
        embed_client=embedder,
        model_version="v1",
        file_path=str(file),
        source_type="notice",
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
        assert row[0] == "notice"          # source_type
        assert row[1] == source_id         # source_id
        assert isinstance(row[2], int)     # chunk_index
        assert isinstance(row[3], str)     # chunk_text
        assert row[7] == "v1"              # model_version


@pytest.mark.asyncio
async def test_ingest_invalid_source_type_raises():
    """source_type other than 'notice' must raise ValueError."""
    conn = _make_mock_conn()
    embedder = _make_mock_embedder()

    # 'precedent' is invalid in hanbang-rag (was valid in legal-rag)
    with pytest.raises(ValueError, match="source_type"):
        await ingest_file(
            conn=conn,
            embed_client=embedder,
            model_version="v1",
            file_path="/tmp/x.txt",
            source_type="precedent",
            source_id=str(uuid.uuid4()),
        )

    # 'case_document' is also invalid
    with pytest.raises(ValueError, match="source_type"):
        await ingest_file(
            conn=conn,
            embed_client=embedder,
            model_version="v1",
            file_path="/tmp/x.txt",
            source_type="case_document",
            source_id=str(uuid.uuid4()),
        )


# ── Gap-3: source existence validation ────────────────────────────────────────

@pytest.mark.asyncio
async def test_validate_source_exists_found():
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=True)
    await validate_source_exists(conn, "notice", source_id)


@pytest.mark.asyncio
async def test_validate_source_exists_not_found_raises():
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=False)
    with pytest.raises(SourceNotFoundError):
        await validate_source_exists(conn, "notice", source_id)


@pytest.mark.asyncio
async def test_validate_source_exists_wrong_type_raises():
    """validate_source_exists rejects non-notice source_type immediately."""
    source_id = str(uuid.uuid4())
    conn = _make_mock_conn(source_exists=True)
    with pytest.raises(ValueError, match="notice"):
        await validate_source_exists(conn, "precedent", source_id)


@pytest.mark.asyncio
async def test_reingest_shorter_removes_orphan_chunks(tmp_path):
    """재인제스트 시 청크 수 축소 → 고아 청크 삭제 확인.

    1. 긴 텍스트 ingest → N청크 upsert 확인
    2. 같은 source_id로 짧은 텍스트 재ingest → M(<N) 청크
    3. DELETE 호출의 마지막 인자(threshold)가 정확히 M임을 assert
    """
    source_id = str(uuid.uuid4())
    embedder = _make_mock_embedder()

    # ── 1차 ingest: 긴 텍스트 ──────────────────────────────────────────────────
    long_text = "고시 내용입니다. " * 60  # token_target=30 기준 여러 청크 생성
    file_long = _make_text_file(tmp_path, long_text, suffix=".txt")

    delete_calls_first: list[tuple] = []

    conn1 = _make_mock_conn(source_exists=True)
    _orig_execute1 = conn1.execute.side_effect

    async def _execute1_spy(sql, params=None):
        if "DELETE FROM hanbang_rag_document_chunk" in sql and params:
            delete_calls_first.append(params)
        return await _orig_execute1(sql, params)

    conn1.execute = AsyncMock(side_effect=_execute1_spy)

    chunks_first = await ingest_file(
        conn=conn1,
        embed_client=embedder,
        model_version="v1",
        file_path=str(file_long),
        source_type="notice",
        source_id=source_id,
        chunk_token_target=30,
        chunk_overlap_tokens=0,
        batch_size=10,
    )
    assert chunks_first >= 2, "긴 텍스트는 2개 이상 청크를 생성해야 한다"
    assert len(delete_calls_first) == 1, "orphan DELETE가 1회 호출되어야 한다"
    assert delete_calls_first[0][2] == chunks_first

    # ── 2차 ingest: 짧은 텍스트 (1청크만 생성) ──────────────────────────────────
    short_text = "짧은 고시."
    file_short = _make_text_file(tmp_path, short_text, suffix=".txt")

    delete_calls_second: list[tuple] = []

    conn2 = _make_mock_conn(source_exists=True)
    _orig_execute2 = conn2.execute.side_effect

    async def _execute2_spy(sql, params=None):
        if "DELETE FROM hanbang_rag_document_chunk" in sql and params:
            delete_calls_second.append(params)
        return await _orig_execute2(sql, params)

    conn2.execute = AsyncMock(side_effect=_execute2_spy)

    chunks_second = await ingest_file(
        conn=conn2,
        embed_client=embedder,
        model_version="v1",
        file_path=str(file_short),
        source_type="notice",
        source_id=source_id,
        chunk_token_target=30,
        chunk_overlap_tokens=0,
        batch_size=10,
    )
    assert chunks_second < chunks_first, "짧은 텍스트는 이전보다 적은 청크를 만들어야 한다"
    assert len(delete_calls_second) == 1, "orphan DELETE가 1회 호출되어야 한다"

    orphan_threshold = delete_calls_second[0][2]
    assert orphan_threshold == chunks_second, (
        f"orphan DELETE threshold는 새 청크 수({chunks_second})여야 하는데 "
        f"{orphan_threshold}가 전달됐다"
    )
    assert delete_calls_second[0][0] == source_id
    assert delete_calls_second[0][1] == "notice"


@pytest.mark.asyncio
async def test_ingest_rejects_nonexistent_source(tmp_path):
    """Gap-3: 존재하지 않는 notice source_id → SourceNotFoundError, 임베딩 호출 없음."""
    content = "고시 내용입니다."
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
            source_type="notice",
            source_id=source_id,
        )
    assert not embedder.embed_batch.called
