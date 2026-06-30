"""
ingest.py — file ingestion pipeline for hanbang RAG.

Pipeline:
  1. Verify source_id exists in hanbang_rag_notice (Gap-3: source existence invariant).
  2. Extract text from PDF / DOCX / plain-text file.
  3. Chunk text into ~500-token windows with overlap.
  4. Batch-embed chunks via local sidecar (embed_client).
  5. Upsert rows into hanbang_rag_document_chunk (ON CONFLICT source+type+index).

Source type: 'notice' only (한방 고시 단일 소스타입 — case_document 분기 없음).

External dependencies:
  - pypdf    (PDF text extraction)
  - python-docx (DOCX text extraction)
  Both are lazy-imported so the module loads without them in unit tests.

Role requirement: conn must be authenticated as app_service (BYPASSRLS)
for chunk writes. RLS on hanbang_rag_document_chunk denies app_user inserts.
"""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from embed_client import EmbedClient

logger = logging.getLogger(__name__)

_CHARS_PER_TOKEN_APPROX = 3


@dataclass
class Chunk:
    index: int
    text: str
    token_count: int


def chunk_text(
    text: str,
    token_target: int = 500,
    overlap_tokens: int = 50,
) -> list[Chunk]:
    """Split text into overlapping chunks of ~token_target tokens."""
    if not text or not text.strip():
        return []

    char_target = token_target * _CHARS_PER_TOKEN_APPROX
    char_overlap = overlap_tokens * _CHARS_PER_TOKEN_APPROX

    _paragraph_re = re.compile(r"\n{2,}")
    _sentence_re = re.compile(r"(?<=[.。！？])\s+")

    def _split_at_boundary(s: str) -> list[str]:
        parts = _paragraph_re.split(s)
        if len(parts) > 1:
            return [p.strip() for p in parts if p.strip()]
        parts = _sentence_re.split(s)
        return [p.strip() for p in parts if p.strip()]

    chunks: list[Chunk] = []
    segments = _split_at_boundary(text)

    buffer = ""
    for seg in segments:
        if len(buffer) + len(seg) + 1 > char_target and buffer:
            chunks.append(
                Chunk(
                    index=len(chunks),
                    text=buffer.strip(),
                    token_count=max(1, len(buffer) // _CHARS_PER_TOKEN_APPROX),
                )
            )
            buffer = buffer[-char_overlap:] + " " + seg if char_overlap > 0 else seg
        else:
            buffer = (buffer + " " + seg).strip() if buffer else seg

    if buffer.strip():
        chunks.append(
            Chunk(
                index=len(chunks),
                text=buffer.strip(),
                token_count=max(1, len(buffer) // _CHARS_PER_TOKEN_APPROX),
            )
        )

    return chunks


# ── Text extraction ───────────────────────────────────────────────────────────

def extract_text(file_path: str | Path) -> str:
    """Extract plain text from PDF, DOCX, or plain-text file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)
    elif suffix in (".docx",):
        return _extract_docx(path)
    elif suffix in (".txt", ".md", ".text"):
        return path.read_text(encoding="utf-8", errors="replace")
    else:
        raise ValueError(
            f"Unsupported file extension {suffix!r}. "
            "Supported: .pdf, .docx, .txt, .md"
        )


def _extract_pdf(path: Path) -> str:
    try:
        import pypdf  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "pypdf is required for PDF extraction. Install: pip install pypdf"
        ) from exc

    reader = pypdf.PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n\n".join(pages)


def _extract_docx(path: Path) -> str:
    try:
        import docx  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "python-docx is required for DOCX extraction. "
            "Install: pip install python-docx"
        ) from exc

    doc = docx.Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


# ── Source existence validation (Gap-3) ───────────────────────────────────────

# 한방은 notice 단일 소스타입. case_document 분기 없음.
_CHECK_NOTICE_SQL = "SELECT 1 FROM hanbang_rag_notice WHERE id = %s::uuid"


class SourceNotFoundError(ValueError):
    """Raised when source_id does not exist in hanbang_rag_notice (Gap-3 invariant)."""


async def validate_source_exists(
    conn,
    source_type: str,
    source_id: str,
) -> None:
    """Verify source_id exists in hanbang_rag_notice before ingesting.

    Args:
        conn:        psycopg AsyncConnection (app_service, no RLS restriction).
        source_type: must be 'notice'.
        source_id:   UUID string.

    Raises:
        SourceNotFoundError: if the source row does not exist.
        ValueError: if source_type is not 'notice'.
    """
    if source_type != "notice":
        raise ValueError(
            f"source_type must be 'notice', got {source_type!r}"
        )
    cur = await conn.execute(_CHECK_NOTICE_SQL, (source_id,))
    row = await cur.fetchone()
    if row is None:
        raise SourceNotFoundError(
            f"source_id {source_id!r} not found in hanbang_rag_notice. "
            "Ingest rejected to preserve citation integrity."
        )


# ── DB upsert ─────────────────────────────────────────────────────────────────

_UPSERT_CHUNK_SQL = """
INSERT INTO hanbang_rag_document_chunk
  (source_type, source_id, chunk_index, chunk_text, token_count,
   embedding, embedded_at, model_version)
VALUES
  (%s, %s, %s, %s, %s, %s::vector, %s, %s)
ON CONFLICT (source_id, source_type, chunk_index)
DO UPDATE SET
  chunk_text    = EXCLUDED.chunk_text,
  token_count   = EXCLUDED.token_count,
  embedding     = EXCLUDED.embedding,
  embedded_at   = EXCLUDED.embedded_at,
  model_version = EXCLUDED.model_version,
  updated_at    = now()
"""

# 재인제스트 시 청크 수가 줄어들면 높은 idx의 옛 청크가 고아(orphan)로 잔존한다.
# upsert 루프 완료 후 len(chunks) 이상의 idx를 일괄 삭제해 정합성을 보장한다.
_DELETE_ORPHAN_CHUNK_SQL = """
DELETE FROM hanbang_rag_document_chunk
WHERE source_id = %s::uuid AND source_type = %s AND chunk_index >= %s
"""


async def ingest_file(
    *,
    conn,
    embed_client: "EmbedClient",
    model_version: str,
    file_path: str | Path,
    source_type: str,
    source_id: str | uuid.UUID,
    chunk_token_target: int = 500,
    chunk_overlap_tokens: int = 50,
    batch_size: int = 32,
) -> int:
    """Ingest a single file into hanbang_rag_document_chunk.

    Steps:
      0. Validate source_id exists in hanbang_rag_notice (Gap-3).
      1. Extract text from file.
      2. Chunk text.
      3. Batch-embed via sidecar.
      4. Upsert chunks into hanbang_rag_document_chunk.

    Raises:
        ValueError: Invalid source_type (must be 'notice').
        SourceNotFoundError: source_id not found in hanbang_rag_notice.
        EmbedSidecarUnavailable: Local sidecar unreachable.
    """
    if source_type != "notice":
        raise ValueError(
            f"source_type must be 'notice', got {source_type!r}"
        )

    source_id_str = str(uuid.UUID(str(source_id)))
    logger.info(
        "Ingest start: file=%s source_type=%s source_id=%s",
        file_path, source_type, source_id_str,
    )

    # Step 0: verify source existence (Gap-3 invariant)
    await validate_source_exists(conn, source_type, source_id_str)

    # Step 1: extract text
    text = extract_text(file_path)
    if not text.strip():
        logger.warning("No text extracted from %s — ingest skipped.", file_path)
        return 0

    # Step 2: chunk
    chunks = chunk_text(text, chunk_token_target, chunk_overlap_tokens)
    logger.info("Produced %d chunks from %s", len(chunks), file_path)

    # Step 3+4: batch embed + upsert
    now = datetime.now(timezone.utc)
    upserted = 0

    for batch_start in range(0, len(chunks), batch_size):
        batch = chunks[batch_start : batch_start + batch_size]
        texts = [c.text for c in batch]
        vectors = embed_client.embed_batch(texts)

        rows = [
            (
                source_type,
                source_id_str,
                chunk.index,
                chunk.text,
                chunk.token_count,
                vectors[i],
                now,
                model_version,
            )
            for i, chunk in enumerate(batch)
        ]
        async with conn.cursor() as cur:
            await cur.executemany(_UPSERT_CHUNK_SQL, rows)
        upserted += len(rows)
        logger.debug("Upserted chunks %d-%d", batch_start, batch_start + len(batch) - 1)

    # 재인제스트 고아 청크 삭제
    await conn.execute(
        _DELETE_ORPHAN_CHUNK_SQL,
        (source_id_str, source_type, len(chunks)),
    )

    logger.info(
        "Ingest complete: source_id=%s chunks=%d", source_id_str, upserted
    )
    return upserted
