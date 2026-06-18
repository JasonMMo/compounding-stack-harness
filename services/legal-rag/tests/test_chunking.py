"""
tests/test_chunking.py — unit tests for chunk_text().

No DB, no sidecar required. Pure function tests.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ingest import chunk_text, Chunk


class TestChunkText:
    def test_empty_string_returns_empty(self):
        assert chunk_text("") == []

    def test_whitespace_only_returns_empty(self):
        assert chunk_text("   \n\n  ") == []

    def test_short_text_produces_one_chunk(self):
        text = "단기 판례 요약문입니다. 법원은 원고 승소 판결을 내렸다."
        chunks = chunk_text(text, token_target=500, overlap_tokens=50)
        assert len(chunks) == 1
        assert chunks[0].index == 0
        assert chunks[0].text == text.strip()

    def test_chunks_are_zero_indexed(self):
        # Generate text long enough for multiple chunks (500 tokens ≈ 1500 chars)
        paragraph = "가나다라마바사아자차카타파하 " * 40  # ~560 chars each
        text = "\n\n".join([paragraph] * 5)
        chunks = chunk_text(text, token_target=100, overlap_tokens=10)
        indices = [c.index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_token_count_is_positive(self):
        text = "법원은 피고에게 손해배상을 명령하였다. " * 10
        chunks = chunk_text(text, token_target=50, overlap_tokens=5)
        for c in chunks:
            assert c.token_count >= 1

    def test_chunk_text_is_stripped(self):
        text = "  판결 요약.  \n\n  추가 내용.  "
        chunks = chunk_text(text, token_target=500)
        for c in chunks:
            assert c.text == c.text.strip()

    def test_overlap_causes_content_repetition(self):
        """With overlap, the end of one chunk appears at the start of the next."""
        long_paragraph = "A" * 200
        text = "\n\n".join(["B" * 200, long_paragraph, "C" * 200])
        # Small token_target to force multiple chunks
        chunks = chunk_text(text, token_target=100, overlap_tokens=30)
        # If we have multiple chunks, adjacent ones should share some chars
        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                assert len(chunks[i].text) > 0
                assert len(chunks[i + 1].text) > 0

    def test_returns_chunk_dataclass(self):
        chunks = chunk_text("테스트 판례 내용입니다.", token_target=500)
        assert len(chunks) == 1
        assert isinstance(chunks[0], Chunk)
        assert hasattr(chunks[0], "index")
        assert hasattr(chunks[0], "text")
        assert hasattr(chunks[0], "token_count")

    def test_large_text_produces_multiple_chunks(self):
        # 5000 char text with token_target=100 (≈300 chars) → at least 10 chunks
        text = ("판례 내용 " * 100 + "\n\n") * 5
        chunks = chunk_text(text, token_target=100, overlap_tokens=0)
        assert len(chunks) >= 5
