"""
tests/test_path_traversal.py — unit tests for _validate_ingest_path().

Verifies path-traversal guard in api.py.
No DB, sidecar, or FastAPI test client required — pure function tests.
"""
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi import HTTPException

# Import the guard function directly (not via FastAPI app startup)
from api import _validate_ingest_path


class TestValidateIngestPath:

    def test_path_within_root_is_accepted(self, tmp_path):
        allowed_root = str(tmp_path)
        target = str(tmp_path / "docs" / "case1.pdf")
        # Does not need to exist — only path resolution is checked
        result = _validate_ingest_path(target, allowed_root)
        assert result.startswith(os.path.realpath(allowed_root))

    def test_exact_root_path_is_accepted(self, tmp_path):
        allowed_root = str(tmp_path)
        result = _validate_ingest_path(str(tmp_path / "file.txt"), allowed_root)
        assert result is not None

    def test_dotdot_traversal_is_rejected(self, tmp_path):
        allowed_root = str(tmp_path / "ingest")
        traversal = str(tmp_path / "ingest" / ".." / ".." / "etc" / "passwd")
        with pytest.raises(HTTPException) as exc_info:
            _validate_ingest_path(traversal, allowed_root)
        assert exc_info.value.status_code == 400
        assert "traversal" in exc_info.value.detail.lower() or "permitted" in exc_info.value.detail.lower()

    def test_absolute_path_outside_root_is_rejected(self, tmp_path):
        allowed_root = str(tmp_path / "ingest")
        outside = str(tmp_path / "other" / "secret.txt")
        with pytest.raises(HTTPException) as exc_info:
            _validate_ingest_path(outside, allowed_root)
        assert exc_info.value.status_code == 400

    def test_root_itself_as_file_path_is_accepted(self, tmp_path):
        # Requesting a file directly at root level is allowed
        allowed_root = str(tmp_path)
        target = str(tmp_path / "top.txt")
        result = _validate_ingest_path(target, allowed_root)
        assert os.path.realpath(allowed_root) in result

    def test_deeply_nested_path_within_root_is_accepted(self, tmp_path):
        allowed_root = str(tmp_path)
        deep = str(tmp_path / "a" / "b" / "c" / "d" / "file.pdf")
        result = _validate_ingest_path(deep, allowed_root)
        assert result.startswith(os.path.realpath(allowed_root))

    def test_path_with_encoded_traversal_is_rejected(self, tmp_path):
        # Ensure realpath normalisation catches non-obvious traversals
        allowed_root = str(tmp_path / "ingest")
        # Construct a path that resolves outside via extra slashes / current-dir refs
        traversal = str(tmp_path / "ingest" / "." / ".." / "shadow")
        with pytest.raises(HTTPException) as exc_info:
            _validate_ingest_path(traversal, allowed_root)
        assert exc_info.value.status_code == 400
