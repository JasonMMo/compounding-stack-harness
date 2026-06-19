"""
tests/test_adapter.py — Unit tests for embed-adapter reshaping logic.

Tests mock the TEI httpx call using respx so no real network is needed.
Each test asserts contract compliance with embed_client.py byte-for-byte.
"""
from __future__ import annotations

import os

import pytest
import respx
import httpx
from fastapi.testclient import TestClient

# Set TEI_BASE_URL before importing app so config is fixed for tests.
os.environ.setdefault("TEI_BASE_URL", "http://tei-test:80")
os.environ.setdefault("EMBED_MODEL_NAME", "intfloat/multilingual-e5-base")
os.environ.setdefault("EMBED_QUERY_PREFIX", "query: ")
os.environ.setdefault("EMBED_PASSAGE_PREFIX", "passage: ")

from app import app, EMBED_DIM  # noqa: E402 — must come after env setup

client = TestClient(app)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _fake_vec(value: float = 0.1) -> list[float]:
    """Return a 768-dim vector filled with `value`."""
    return [value] * EMBED_DIM


def _tei_url() -> str:
    return f"{os.environ['TEI_BASE_URL']}/embed"


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_returns_200() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200


# ── POST /embed ───────────────────────────────────────────────────────────────

@respx.mock
def test_single_embed_happy_path() -> None:
    """POST /embed reshapes TEI bare array → {"embedding": [...], "model": str}."""
    vec = _fake_vec(0.42)
    respx.post(_tei_url()).mock(
        return_value=httpx.Response(200, json=[vec])
    )

    resp = client.post("/embed", json={"text": "테스트 문서"})

    assert resp.status_code == 200
    body = resp.json()
    assert "embedding" in body, f"missing 'embedding' key: {body}"
    assert "model" in body, f"missing 'model' key: {body}"
    assert len(body["embedding"]) == EMBED_DIM
    assert body["embedding"] == vec
    assert body["model"] == "intfloat/multilingual-e5-base"


@respx.mock
def test_single_embed_sends_query_prefix_to_tei() -> None:
    """POST /embed (query path) must send 'query: <text>' to TEI.

    Invariant: /embed is called ONLY by api.py (search), so query: prefix
    is always correct here.
    """
    vec = _fake_vec()
    captured: dict = {}

    def capture(request: httpx.Request) -> httpx.Response:
        import json
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json=[vec])

    respx.post(_tei_url()).mock(side_effect=capture)

    client.post("/embed", json={"text": "hello"})

    assert "inputs" in captured["body"]
    inputs = captured["body"]["inputs"]
    # inputs may be str or list; TEI accepts both.
    first = inputs[0] if isinstance(inputs, list) else inputs
    assert first.startswith("query: "), (
        f"Expected query prefix 'query: ' on /embed but got: {first!r}"
    )
    assert first == "query: hello", (
        f"Expected 'query: hello' but got: {first!r}"
    )


@respx.mock
def test_batch_embed_sends_passage_prefix_to_tei() -> None:
    """POST /embed/batch (passage ingest path) must send 'passage: <text>' for each item.

    Invariant: /embed/batch is called ONLY by ingest.py (document passages), so
    passage: prefix is always correct here.
    """
    texts = ["doc A", "doc B"]
    vecs = [_fake_vec(0.1), _fake_vec(0.2)]
    captured: dict = {}

    def capture(request: httpx.Request) -> httpx.Response:
        import json
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json=vecs)

    respx.post(_tei_url()).mock(side_effect=capture)

    client.post("/embed/batch", json={"texts": texts})

    assert "inputs" in captured["body"]
    inputs = captured["body"]["inputs"]
    assert isinstance(inputs, list), f"Expected list of inputs but got: {type(inputs)}"
    assert inputs[0] == "passage: doc A", (
        f"Expected 'passage: doc A' but got: {inputs[0]!r}"
    )
    assert inputs[1] == "passage: doc B", (
        f"Expected 'passage: doc B' but got: {inputs[1]!r}"
    )


@respx.mock
def test_single_embed_dimension_mismatch_raises_502() -> None:
    """If TEI returns wrong-dim vector, adapter must raise 502."""
    bad_vec = [0.1] * 512  # wrong dim
    respx.post(_tei_url()).mock(
        return_value=httpx.Response(200, json=[bad_vec])
    )

    resp = client.post("/embed", json={"text": "bad dim"})

    assert resp.status_code == 502
    assert "512" in resp.json()["detail"] or "dim" in resp.json()["detail"].lower()


def test_single_embed_empty_text_rejected() -> None:
    """Empty text must be rejected (422) without calling TEI."""
    resp = client.post("/embed", json={"text": "   "})
    assert resp.status_code == 422


# ── POST /embed/batch ─────────────────────────────────────────────────────────

@respx.mock
def test_batch_embed_happy_path() -> None:
    """POST /embed/batch reshapes TEI 2-D array → {"embeddings": [...], "model": str}."""
    texts = ["문서 A", "문서 B", "문서 C"]
    vecs = [_fake_vec(float(i) / 10) for i in range(len(texts))]
    respx.post(_tei_url()).mock(
        return_value=httpx.Response(200, json=vecs)
    )

    resp = client.post("/embed/batch", json={"texts": texts})

    assert resp.status_code == 200
    body = resp.json()
    assert "embeddings" in body, f"missing 'embeddings' key: {body}"
    assert "model" in body, f"missing 'model' key: {body}"
    assert len(body["embeddings"]) == len(texts)
    for i, vec in enumerate(body["embeddings"]):
        assert len(vec) == EMBED_DIM, (
            f"embeddings[{i}] has dim {len(vec)}, expected {EMBED_DIM}"
        )
    assert body["model"] == "intfloat/multilingual-e5-base"


@respx.mock
def test_batch_embed_dimension_mismatch_raises_502() -> None:
    """Batch: any wrong-dim vector triggers 502."""
    vecs = [_fake_vec(), [0.0] * 512]  # second vec is wrong
    respx.post(_tei_url()).mock(
        return_value=httpx.Response(200, json=vecs)
    )

    resp = client.post("/embed/batch", json={"texts": ["A", "B"]})

    assert resp.status_code == 502


def test_batch_empty_list_rejected() -> None:
    """Empty texts list must be rejected (422)."""
    resp = client.post("/embed/batch", json={"texts": []})
    assert resp.status_code == 422


def test_batch_empty_string_in_list_rejected() -> None:
    """Empty string inside texts must be rejected (422)."""
    resp = client.post("/embed/batch", json={"texts": ["valid", "  "]})
    assert resp.status_code == 422


@respx.mock
def test_tei_connect_error_raises_502() -> None:
    """If TEI is unreachable, adapter must return 502."""
    respx.post(_tei_url()).mock(side_effect=httpx.ConnectError("refused"))

    resp = client.post("/embed", json={"text": "test"})

    assert resp.status_code == 502
