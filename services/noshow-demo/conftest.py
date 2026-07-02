"""
conftest.py — pytest path setup for services/noshow-demo/.

Ensures modules (config, db, engine, api) are importable regardless of the
working directory pytest is invoked from.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
