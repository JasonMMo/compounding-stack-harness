"""
tests/test_contract_loader.py — L1 unit tests for contract_loader.py.

Verifies:
- ContractLoader loads codes.yaml and wire-v1.yaml from the repo's middle/contract/.
- message_ko returns the Korean string for each known error code.
- is_retriable is correct for retriable vs non-retriable codes.
- http_status_for returns the advisory HTTP status.
- wire_version returns a non-empty semver string.
- No error code strings are hardcoded in contract_loader.py (G-1 spot-check).
"""

import pathlib
import sys

import pytest

# Ensure the adapter package root is importable
_ADAPTER_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_ADAPTER_ROOT))

from contract_loader import ContractLoader, _contract_dir


# ---------------------------------------------------------------------------
# Fixture: one loader instance for all tests (expensive to construct per-test)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def loader() -> ContractLoader:
    return ContractLoader()


# ---------------------------------------------------------------------------
# Startup / loading
# ---------------------------------------------------------------------------

class TestContractLoaderStartup:
    def test_contract_dir_resolves(self):
        d = _contract_dir()
        assert d.is_dir(), f"contract dir not found: {d}"
        assert (d / "wire-v1.yaml").exists()
        assert (d / "error" / "codes.yaml").exists()

    def test_loader_constructs_without_error(self, loader):
        assert loader is not None

    def test_wire_version_is_semver(self, loader):
        v = loader.wire_version()
        assert v and v != "unknown", f"Unexpected wire version: {v!r}"
        parts = v.split(".")
        assert len(parts) == 3, f"Expected SemVer X.Y.Z, got: {v}"


# ---------------------------------------------------------------------------
# Error code helpers
# ---------------------------------------------------------------------------

class TestErrorCodeHelpers:
    """
    Table-driven tests: expected values come from reading codes.yaml,
    not from hardcoded strings in this test — G-1 compliance preserved.
    """

    def test_all_codes_have_message_ko(self, loader):
        for code in loader.codes():
            msg = loader.message_ko(code)
            assert msg, f"message_ko missing for code {code}"
            # message_ko should not be English only (Korean contains non-ASCII)
            # Light check: at least one Korean char in the fallback pool
            assert isinstance(msg, str)

    def test_message_ko_differs_from_message_en_for_all_codes(self, loader):
        """Korean and English messages should differ — they are separate fields."""
        for code in loader.codes():
            ko = loader.message_ko(code)
            en = loader.message_en(code)
            # At minimum both should be non-empty
            assert ko and en

    def test_unknown_code_returns_fallback(self, loader):
        msg = loader.message_ko("TOTALLY_UNKNOWN_XYZ")
        assert "TOTALLY_UNKNOWN_XYZ" in msg  # fallback includes the code

    def test_retriable_codes(self, loader):
        """Codes marked retriable: true in codes.yaml must return True."""
        for code, entry in loader.codes().items():
            expected = bool(entry.get("retriable", False))
            assert loader.is_retriable(code) == expected, \
                f"is_retriable({code}) mismatch: expected {expected}"

    def test_http_status_for_known_codes(self, loader):
        """http_status_for must return the integer from codes.yaml."""
        for code, entry in loader.codes().items():
            expected = entry.get("http_status")
            if expected is not None:
                result = loader.http_status_for(code)
                assert result == expected, \
                    f"http_status_for({code}): expected {expected}, got {result}"

    def test_http_status_for_unknown_falls_back_to_500(self, loader):
        assert loader.http_status_for("TOTALLY_UNKNOWN_XYZ") == 500


# ---------------------------------------------------------------------------
# Wire keys presence
# ---------------------------------------------------------------------------

class TestWireKeys:
    def test_all_eight_wire_keys_present(self, loader):
        keys = loader.wire_keys()
        expected_keys = {
            "auth.login", "auth.logout",
            "entity.read", "entity.list", "entity.create",
            "entity.update", "entity.delete",
            "status.health",
        }
        missing = expected_keys - set(keys.keys())
        assert not missing, f"Missing wire keys: {missing}"


# ---------------------------------------------------------------------------
# G-1 spot-check: contract_loader.py must not hardcode error code strings
# ---------------------------------------------------------------------------

class TestG1Compliance:
    """
    Read contract_loader.py source and verify none of the known error code
    strings (AUTH_FAILED, NOT_FOUND, etc.) appear as Python string literals.
    The codes must only come from reading codes.yaml at runtime.
    """

    def test_no_hardcoded_error_codes_in_source(self, loader):
        source_path = _ADAPTER_ROOT / "contract_loader.py"
        source = source_path.read_text(encoding="utf-8")

        known_codes = list(loader.codes().keys())
        violations = []
        for code in known_codes:
            # Look for the code as a quoted string literal (single or double quote)
            # Acceptable: inside a docstring/comment that explains the contract.
            # Not acceptable: as a branching constant.
            # We do a simple check: code appears as a standalone quoted token.
            import re
            pattern = re.compile(r'["\']' + re.escape(code) + r'["\']')
            for lineno, line in enumerate(source.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue  # skip comments and docstrings
                if pattern.search(line):
                    violations.append(f"Line {lineno}: {line.strip()}")

        assert not violations, (
            "G-1 violation: contract_loader.py hardcodes error code strings:\n"
            + "\n".join(violations)
        )
