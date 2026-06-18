"""
tests/test_embed_client.py — unit tests for EmbedClient (no real sidecar).

Uses unittest.mock to simulate sidecar HTTP responses.
Tests fail-fast behavior when sidecar is unavailable.
"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import MagicMock, patch
from embed_client import EmbedClient, EmbedSidecarUnavailable, EmbedDimensionError, EMBED_DIM


def _make_vector(dim: int = EMBED_DIM) -> list[float]:
    return [0.1] * dim


class TestEmbedClientEmbed:
    def test_embed_returns_768_dim_vector(self):
        client = EmbedClient("http://localhost:8080")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": _make_vector(), "model": "test"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.post", return_value=mock_response):
            result = client.embed("테스트 텍스트")

        assert len(result) == EMBED_DIM
        assert result == _make_vector()

    def test_embed_raises_on_connect_error(self):
        import httpx

        client = EmbedClient("http://localhost:8080")
        with patch("httpx.post", side_effect=httpx.ConnectError("refused")):
            with pytest.raises(EmbedSidecarUnavailable) as exc_info:
                client.embed("테스트")
        # Error message must mention cloud fallback is disabled
        assert "cloud" in str(exc_info.value).lower() or "sidecar" in str(exc_info.value).lower()

    def test_embed_raises_on_wrong_dimension(self):
        client = EmbedClient("http://localhost:8080")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": [0.1] * 512, "model": "wrong"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.post", return_value=mock_response):
            with pytest.raises(EmbedDimensionError):
                client.embed("텍스트")

    def test_embed_raises_on_empty_text(self):
        client = EmbedClient("http://localhost:8080")
        with pytest.raises(ValueError):
            client.embed("")

    def test_embed_raises_on_whitespace_only(self):
        client = EmbedClient("http://localhost:8080")
        with pytest.raises(ValueError):
            client.embed("   ")


class TestEmbedClientBatch:
    def test_batch_empty_returns_empty(self):
        client = EmbedClient("http://localhost:8080")
        result = client.embed_batch([])
        assert result == []

    def test_batch_returns_correct_count(self):
        client = EmbedClient("http://localhost:8080")
        n = 3
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "embeddings": [_make_vector() for _ in range(n)],
            "model": "test",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.post", return_value=mock_response):
            result = client.embed_batch(["a", "b", "c"])

        assert len(result) == n
        assert all(len(v) == EMBED_DIM for v in result)

    def test_batch_raises_on_wrong_response_count(self):
        client = EmbedClient("http://localhost:8080")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "embeddings": [_make_vector()],  # only 1, sent 3
            "model": "test",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.post", return_value=mock_response):
            with pytest.raises(EmbedSidecarUnavailable):
                client.embed_batch(["a", "b", "c"])

    def test_batch_raises_on_empty_text_in_batch(self):
        client = EmbedClient("http://localhost:8080")
        with pytest.raises(ValueError):
            client.embed_batch(["valid", ""])

    def test_batch_raises_on_sidecar_error(self):
        import httpx

        client = EmbedClient("http://localhost:8080")
        with patch("httpx.post", side_effect=httpx.ConnectError("refused")):
            with pytest.raises(EmbedSidecarUnavailable):
                client.embed_batch(["text1", "text2"])


class TestEmbedClientHealthCheck:
    def test_health_check_true_on_200(self):
        client = EmbedClient("http://localhost:8080")
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.get", return_value=mock_response):
            assert client.health_check() is True

    def test_health_check_false_on_connection_error(self):
        import httpx

        client = EmbedClient("http://localhost:8080")
        with patch("httpx.get", side_effect=httpx.ConnectError("refused")):
            assert client.health_check() is False

    def test_health_check_false_on_non_200(self):
        client = EmbedClient("http://localhost:8080")
        mock_response = MagicMock()
        mock_response.status_code = 503

        with patch("httpx.get", return_value=mock_response):
            assert client.health_check() is False
