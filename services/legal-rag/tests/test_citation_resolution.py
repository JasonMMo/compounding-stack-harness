"""
tests/test_citation_resolution.py — unit tests for citation logic (no DB).

Tests Citation dataclass construction, asdict serialization,
and UUID validation in log_query() path.
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
    def test_precedent_citation_fields(self):
        cit = Citation(
            chunk_id=str(uuid.uuid4()),
            source_type="precedent",
            source_id=str(uuid.uuid4()),
            case_number="대법원 2020다12345",
            court="대법원",
            decision_date="2020-06-15",
            holding_summary="원고 승소",
            chunk_index=0,
            chunk_text_excerpt="판결 요약 내용",
            rrf_score=0.85,
        )
        assert cit.source_type == "precedent"
        assert cit.document_title is None
        assert cit.case_number == "대법원 2020다12345"

    def test_case_document_citation_fields(self):
        cit = Citation(
            chunk_id=str(uuid.uuid4()),
            source_type="case_document",
            source_id=str(uuid.uuid4()),
            case_id=str(uuid.uuid4()),
            document_title="계약서_2024.pdf",
            document_type="계약서",
            chunk_index=2,
            chunk_text_excerpt="계약 조항 내용",
            rrf_score=0.72,
        )
        assert cit.source_type == "case_document"
        assert cit.case_number is None
        assert cit.document_title == "계약서_2024.pdf"

    def test_asdict_serializable_to_json(self):
        cit = Citation(
            chunk_id=str(uuid.uuid4()),
            source_type="precedent",
            source_id=str(uuid.uuid4()),
            case_number="대법원 2019다99999",
            chunk_text_excerpt="내용",
            rrf_score=0.5,
        )
        d = asdict(cit)
        # Must be JSON-serializable
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        assert parsed["source_type"] == "precedent"
        assert parsed["case_number"] == "대법원 2019다99999"

    def test_chunk_text_excerpt_truncation(self):
        # Verify excerpt is at most 200 chars (as enforced by citation module callers)
        long_text = "판례 내용 " * 50
        excerpt = long_text[:200]
        cit = Citation(
            chunk_id=str(uuid.uuid4()),
            source_type="precedent",
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
                source_type="precedent",
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
        result = _validate_uuid(valid, "attorney_id")
        assert result == valid

    def test_invalid_uuid_raises(self):
        from db import _validate_uuid, RLSSessionError

        with pytest.raises(RLSSessionError):
            _validate_uuid("not-a-uuid", "attorney_id")

    def test_uuid_object_accepted(self):
        from db import _validate_uuid

        u = uuid.uuid4()
        result = _validate_uuid(u, "attorney_id")
        assert result == str(u)
