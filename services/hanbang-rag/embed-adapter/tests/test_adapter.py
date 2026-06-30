"""
tests/test_adapter.py — Unit tests for embed-adapter local inference logic.

All tests monkeypatch `app._encode` so no real model download or GPU/CPU
inference is required.  The `_encode` function is the sole boundary between
the adapter logic and sentence-transformers; patching it is sufficient.

Model singleton (_model) is never loaded during tests because:
  - TestClient with raise_server_exceptions=True does not trigger the lifespan
    startup event unless explicitly requested.
  - We explicitly skip lifespan by constructing TestClient without the app's
    lifespan (FastAPI TestClient does NOT run lifespan by default).

Key invariants verified:
  (a) POST /embed sends "query: <text>" into _encode  (query prefix)
  (b) POST /embed/batch sends "passage: <text>" into _encode (passage prefix)
"""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

# Set env before importing app so config is fixed for tests.
os.environ.setdefault("EMBED_MODEL_ID", "intfloat/multilingual-e5-base")
os.environ.setdefault("EMBED_MODEL_NAME", "intfloat/multilingual-e5-base")
os.environ.setdefault("EMBED_QUERY_PREFIX", "query: ")
os.environ.setdefault("EMBED_PASSAGE_PREFIX", "passage: ")

import app as adapter_module  # noqa: E402
from app import app, EMBED_DIM  # noqa: E402

# ── Helpers ───────────────────────────────────────────────────────────────────

def _fake_vec(value: float = 0.1) -> list[float]:
    """Return a 768-dim vector filled with `value`."""
    return [value] * EMBED_DIM


def _make_fake_encode(_n_inputs: int, value: float = 0.1):
    """Return a _encode replacement that yields one 768-dim vector per input."""
    def fake(prefixed_texts: list[str]) -> list[list[float]]:
        return [_fake_vec(value) for _ in prefixed_texts]
    return fake


def _make_capture_encode(return_vecs: list[list[float]]) -> tuple:
    """Return (fake_encode, captured_dict).

    fake_encode records the texts it received into captured_dict["texts"].
    """
    captured: dict = {}

    def fake(prefixed_texts: list[str]) -> list[list[float]]:
        captured["texts"] = list(prefixed_texts)
        return return_vecs

    return fake, captured


# ── TestClient (no lifespan — model not loaded) ───────────────────────────────
# FastAPI TestClient skips lifespan events unless with_lifespan=True (default
# False in Starlette < 0.36).  We rely on this to avoid loading the real model.

client = TestClient(app)


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_returns_200() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200


# ── POST /embed — query prefix invariant (a) ──────────────────────────────────

def test_single_embed_sends_query_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /embed must pass 'query: <text>' into _encode (query head invariant)."""
    fake, captured = _make_capture_encode([_fake_vec()])
    monkeypatch.setattr(adapter_module, "_encode", fake)

    resp = client.post("/embed", json={"text": "hello"})

    assert resp.status_code == 200
    assert "texts" in captured, "_encode was not called"
    assert len(captured["texts"]) == 1
    assert captured["texts"][0] == "query: hello", (
        f"Expected 'query: hello' but got: {captured['texts'][0]!r}"
    )


def test_single_embed_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /embed → {"embedding": [float x 768], "model": str}."""
    vec = _fake_vec(0.42)
    monkeypatch.setattr(adapter_module, "_encode", _make_fake_encode(1, 0.42))

    resp = client.post("/embed", json={"text": "테스트 문서"})

    assert resp.status_code == 200
    body = resp.json()
    assert "embedding" in body, f"missing 'embedding' key: {body}"
    assert "model" in body, f"missing 'model' key: {body}"
    assert len(body["embedding"]) == EMBED_DIM
    assert body["embedding"] == vec
    assert body["model"] == "intfloat/multilingual-e5-base"


# ── POST /embed/batch — passage prefix invariant (b) ─────────────────────────

def test_batch_embed_sends_passage_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /embed/batch must pass 'passage: <text>' into _encode for each item."""
    vecs = [_fake_vec(0.1), _fake_vec(0.2)]
    fake, captured = _make_capture_encode(vecs)
    monkeypatch.setattr(adapter_module, "_encode", fake)

    resp = client.post("/embed/batch", json={"texts": ["doc A", "doc B"]})

    assert resp.status_code == 200
    assert "texts" in captured, "_encode was not called"
    assert captured["texts"][0] == "passage: doc A", (
        f"Expected 'passage: doc A' but got: {captured['texts'][0]!r}"
    )
    assert captured["texts"][1] == "passage: doc B", (
        f"Expected 'passage: doc B' but got: {captured['texts'][1]!r}"
    )


def test_batch_embed_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /embed/batch → {"embeddings": [[float x 768], ...], "model": str}."""
    texts = ["문서 A", "문서 B", "문서 C"]
    vecs = [_fake_vec(float(i) / 10) for i in range(len(texts))]
    monkeypatch.setattr(adapter_module, "_encode", lambda _: vecs)

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


# ── Dimension mismatch → 502 ──────────────────────────────────────────────────

def test_single_embed_dimension_mismatch_raises_502(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If _encode returns wrong-dim vector, adapter must raise 502."""
    bad_vec = [0.1] * 512  # wrong dim
    monkeypatch.setattr(adapter_module, "_encode", lambda _: [bad_vec])

    resp = client.post("/embed", json={"text": "bad dim"})

    assert resp.status_code == 502
    detail = resp.json()["detail"]
    assert "512" in detail or "dim" in detail.lower()


def test_batch_embed_dimension_mismatch_raises_502(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Batch: any wrong-dim vector triggers 502."""
    vecs = [_fake_vec(), [0.0] * 512]  # second vec wrong dim
    monkeypatch.setattr(adapter_module, "_encode", lambda _: vecs)

    resp = client.post("/embed/batch", json={"texts": ["A", "B"]})

    assert resp.status_code == 502


# ── 422 validation ────────────────────────────────────────────────────────────

def test_single_embed_empty_text_rejected() -> None:
    """Empty text must be rejected (422) without calling _encode."""
    resp = client.post("/embed", json={"text": "   "})
    assert resp.status_code == 422


def test_batch_empty_list_rejected() -> None:
    """Empty texts list must be rejected (422)."""
    resp = client.post("/embed/batch", json={"texts": []})
    assert resp.status_code == 422


def test_batch_empty_string_in_list_rejected() -> None:
    """Empty string inside texts must be rejected (422)."""
    resp = client.post("/embed/batch", json={"texts": ["valid", "  "]})
    assert resp.status_code == 422
