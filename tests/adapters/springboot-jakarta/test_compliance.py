"""
test_compliance.py -- springboot-jakarta adapter compliance shim.

Re-exports all test classes and helpers from the canonical shared suite:
    tests/adapters/_shared/test_compliance.py

Assertions live in exactly ONE place (_shared). This file contributes only
the pytest collection entry-point so that:
    pytest tests/adapters/springboot-jakarta/ -v
collects 23 tests and picks up the gradle auto-launch fixture from
this dir's conftest.py (which overrides the parent adapter_base_url fixture).

DO NOT add test logic here. Any suite change belongs in _shared/test_compliance.py.
"""
from tests.adapters._shared.test_compliance import *  # noqa: F401,F403
