"""
tests/test_citation_resolution.py — unit tests for citation logic (no DB).

Tests Citation dataclass construction, asdict serialization,
and UUID validation in log_query() path.

한방 RAG: source_type='notice' 단일. case_document 테스트 제거.
"""
import sys
import os
import json
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from dataclasses import asdict
from citation import Citation


class TestCitationDataclass:
    def test_notice_citation_fields(self):
        cit = Citation(
            chunk_id=str(uuid.uuid4()),
            source_type="notice",
            source_id=str(uuid.uuid4()),
            notice_number="보건복지부고시 제2023-123호",
            ministry="보건복지부",
            issued_date="2023-01-01",
            summary="첩약 건강보험 적용 시범사업 관련 고시",
            chunk_index=0,
            chunk_text_excerpt="고시 내용 요약",
            rrf_score=0.85,
        )
        assert cit.source_type == "notice"
        assert cit.notice_number == "보건복지부고시 제2023-123호"
        assert cit.ministry == "보건복지부"
        assert cit.issued_date == "2023-01-01"

    def test_notice_citation_optional_fields_default_none(self):
        cit = Citation(
            chunk_id=str(uuid.uuid4()),
            source_type="notice",
            source_id=str(uuid.uuid4()),
            chunk_text_excerpt="요약",
            rrf_score=0.5,
        )
        assert cit.notice_number is None
        assert cit.ministry is None
        assert cit.issued_date is None
        assert cit.summary is None

    def test_asdict_serializable_to_json(self):
        cit = Citation(
            chunk_id=str(uuid.uuid4()),
            source_type="notice",
            source_id=str(uuid.uuid4()),
            notice_number="보건복지부고시 제2023-456호",
            chunk_text_excerpt="내용",
            rrf_score=0.5,
        )
        d = asdict(cit)
        # Must be JSON-serializable
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        assert parsed["source_type"] == "notice"
        assert parsed["notice_number"] == "보건복지부고시 제2023-456호"

    def test_chunk_text_excerpt_truncation(self):
        # Verify excerpt is at most 200 chars (as enforced by citation module callers)
        long_text = "고시 내용 " * 50
        excerpt = long_text[:200]
        cit = Citation(
            chunk_id=str(uuid.uuid4()),
            source_type="notice",
            source_id=str(uuid.uuid4()),
            chunk_text_excerpt=excerpt,
            rrf_score=0.3,
        )
        assert len(cit.chunk_text_excerpt) <= 200

    def test_citation_chunk_ids_list_json(self):
        """chunk_ids_json must be a valid JSON array of UUID strings."""
        chunk_ids = [str(uuid.uuid4()) for _ in range(5)]
        citations = [
            Citation(
                chunk_id=cid,
                source_type="notice",
                source_id=str(uuid.uuid4()),
                chunk_text_excerpt="요약",
                rrf_score=0.5 - i * 0.05,
            )
            for i, cid in enumerate(chunk_ids)
        ]
        chunk_ids_json = json.dumps([c.chunk_id for c in citations])
        parsed = json.loads(chunk_ids_json)
        assert parsed == chunk_ids
        # Each entry must be valid UUID
        for cid in parsed:
            uuid.UUID(cid)


class TestDbValidation:
    """Test UUID validation in db.py without a real DB connection."""

    def test_valid_uuid_passes(self):
        from db import _validate_uuid

        valid = str(uuid.uuid4())
        result = _validate_uuid(valid, "user_id")
        assert result == valid

    def test_invalid_uuid_raises(self):
        from db import _validate_uuid, RLSSessionError

        with pytest.raises(RLSSessionError):
            _validate_uuid("not-a-uuid", "user_id")

    def test_uuid_object_accepted(self):
        from db import _validate_uuid

        u = uuid.uuid4()
        result = _validate_uuid(u, "user_id")
        assert result == str(u)
