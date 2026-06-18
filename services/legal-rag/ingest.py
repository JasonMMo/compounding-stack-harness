"""
ingest.py — file ingestion pipeline for legal RAG.

Pipeline:
  1. Extract text from PDF / DOCX / plain-text file.
  2. Chunk text into ~500-token windows with overlap.
  3. Batch-embed chunks via local sidecar (embed_client).
  4. Upsert rows into legal_document_chunk (ON CONFLICT source+type+index).
  5. Update legal_case_document.ingest_status / ingested_at (for case_document).

External dependencies:
  - pypdf    (PDF text extraction)
  - python-docx (DOCX text extraction)
  Both are lazy-imported so the module loads without them in unit tests.

Role requirement: conn must be authenticated as app_service (BYPASSRLS)
for chunk writes. RLS on legal_document_chunk denies app_user inserts.
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

# ── Chunking ──────────────────────────────────────────────────────────────────

# Approximate chars-per-token for Korean/legal text (conservative estimate).
# Pure-python chunker: avoids tiktoken dependency; caller can pass actual
# token counts if they have a tokenizer.
_CHARS_PER_TOKEN_APPROX = 3


@dataclass
class Chunk:
    index: int          # 0-based position within source document
    text: str
    token_count: int    # estimated


def chunk_text(
    text: str,
    token_target: int = 500,
    overlap_tokens: int = 50,
) -> list[Chunk]:
    """Split text into overlapping chunks of ~token_target tokens.

    Uses character-based approximation (3 chars ≈ 1 token for Korean/mixed text).
    Splits preferentially at paragraph / sentence boundaries.

    Args:
        text:           Full document text.
        token_target:   Target tokens per chunk.
        overlap_tokens: Overlap between adjacent chunks.

    Returns:
        List of Chunk objects, 0-indexed.
    """
    if not text or not text.strip():
        return []

    char_target = token_target * _CHARS_PER_TOKEN_APPROX
    char_overlap = overlap_tokens * _CHARS_PER_TOKEN_APPROX

    # Prefer splitting at double-newline (paragraph), then single newline, then space.
    _paragraph_re = re.compile(r"\n{2,}")
    _sentence_re = re.compile(r"(?<=[.。！？])\s+")

    def _split_at_boundary(s: str) -> list[str]:
        parts = _paragraph_re.split(s)
        if len(parts) > 1:
            return [p.strip() for p in parts if p.strip()]
        parts = _sentence_re.split(s)
        return [p.strip() for p in parts if p.strip()]

    # Greedy accumulator
    chunks: list[Chunk] = []
    segments = _split_at_boundary(text)

    # Merge small segments until char_target is reached, then emit chunk.
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
            # Keep overlap: last `char_overlap` chars of buffer
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
    """Extract plain text from PDF, DOCX, or plain-text file.

    Lazy-imports pypdf and python-docx so this module loads without them
    in environments that don't need file ingestion.

    Args:
        file_path: Path to the file.

    Returns:
        Extracted text string (may be empty for image-only PDFs).

    Raises:
        ValueError: Unsupported file extension.
        FileNotFoundError: File does not exist.
    """
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
        import docx  # type: ignore[import]  # python-docx
    except ImportError as exc:
        raise ImportError(
            "python-docx is required for DOCX extraction. "
            "Install: pip install python-docx"
        ) from exc

    doc = docx.Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


# ── DB upsert ─────────────────────────────────────────────────────────────────

_UPSERT_CHUNK_SQL = """
INSERT INTO legal_document_chunk
  (source_type, source_id, case_id, chunk_index, chunk_text, token_count,
   embedding, embedded_at, model_version)
VALUES
  (%s, %s, %s, %s, %s, %s, %s::vector, %s, %s)
ON CONFLICT (source_id, source_type, chunk_index)
DO UPDATE SET
  chunk_text    = EXCLUDED.chunk_text,
  token_count   = EXCLUDED.token_count,
  embedding     = EXCLUDED.embedding,
  embedded_at   = EXCLUDED.embedded_at,
  model_version = EXCLUDED.model_version,
  updated_at    = now()
"""

_UPDATE_CASE_DOC_STATUS_SQL = """
UPDATE legal_case_document
SET ingest_status = %s, ingested_at = %s
WHERE id = %s
"""


async def ingest_file(
    *,
    conn,           # psycopg AsyncConnection (app_service role)
    embed_client: "EmbedClient",
    model_version: str,
    file_path: str | Path,
    source_type: str,           # 'precedent' or 'case_document'
    source_id: str | uuid.UUID, # FK to legal_precedent.id or legal_case_document.id
    case_id: str | uuid.UUID | None = None,  # required when source_type='case_document'
    chunk_token_target: int = 500,
    chunk_overlap_tokens: int = 50,
    batch_size: int = 32,
) -> int:
    """Ingest a single file into legal_document_chunk.

    Steps:
      1. Extract text from file.
      2. Chunk text.
      3. Batch-embed via sidecar.
      4. Upsert chunks into legal_document_chunk.
      5. If source_type='case_document', update ingest_status on parent table.

    Args:
        conn:                 psycopg AsyncConnection authenticated as app_service.
        embed_client:         EmbedClient instance.
        model_version:        Model version string (recorded in chunk.model_version).
        file_path:            Path to source file.
        source_type:          'precedent' or 'case_document'.
        source_id:            UUID FK to parent precedent or case_document.
        case_id:              UUID FK to legal_case (required for case_document).
        chunk_token_target:   Target tokens per chunk.
        chunk_overlap_tokens: Overlap tokens between chunks.
        batch_size:           Embed batch size (avoid sidecar OOM on large docs).

    Returns:
        Number of chunks upserted.

    Raises:
        ValueError: Invalid source_type or missing case_id for case_document.
        EmbedSidecarUnavailable: Local sidecar unreachable.
    """
    if source_type not in ("precedent", "case_document"):
        raise ValueError(
            f"source_type must be 'precedent' or 'case_document', got {source_type!r}"
        )
    if source_type == "case_document" and case_id is None:
        raise ValueError("case_id is required when source_type='case_document'")

    source_id_str = str(uuid.UUID(str(source_id)))
    case_id_str = str(uuid.UUID(str(case_id))) if case_id else None

    logger.info(
        "Ingest start: file=%s source_type=%s source_id=%s",
        file_path, source_type, source_id_str,
    )

    # 1. Extract text
    text = extract_text(file_path)
    if not text.strip():
        logger.warning("No text extracted from %s — ingest skipped.", file_path)
        if source_type == "case_document":
            await conn.execute(
                _UPDATE_CASE_DOC_STATUS_SQL,
                ("error", datetime.now(timezone.utc), source_id_str),
            )
        return 0

    # Mark processing
    if source_type == "case_document":
        await conn.execute(
            _UPDATE_CASE_DOC_STATUS_SQL,
            ("processing", None, source_id_str),
        )

    # 2. Chunk
    chunks = chunk_text(text, chunk_token_target, chunk_overlap_tokens)
    logger.info("Produced %d chunks from %s", len(chunks), file_path)

    # 3. Batch embed
    now = datetime.now(timezone.utc)
    upserted = 0

    for batch_start in range(0, len(chunks), batch_size):
        batch = chunks[batch_start : batch_start + batch_size]
        texts = [c.text for c in batch]
        vectors = embed_client.embed_batch(texts)

        # 4. Upsert batch
        rows = [
            (
                source_type,
                source_id_str,
                case_id_str,
                chunk.index,
                chunk.text,
                chunk.token_count,
                # psycopg passes list[float] to vector column via cast in SQL
                vectors[i],
                now,
                model_version,
            )
            for i, chunk in enumerate(batch)
        ]
        await conn.executemany(_UPSERT_CHUNK_SQL, rows)
        upserted += len(rows)
        logger.debug("Upserted chunks %d-%d", batch_start, batch_start + len(batch) - 1)

    # 5. Update parent status
    if source_type == "case_document":
        await conn.execute(
            _UPDATE_CASE_DOC_STATUS_SQL,
            ("done", datetime.now(timezone.utc), source_id_str),
        )

    logger.info(
        "Ingest complete: source_id=%s chunks=%d", source_id_str, upserted
    )
    return upserted
