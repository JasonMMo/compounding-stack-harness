"""conftest.py — add embed-adapter root to sys.path so tests can import app."""
import sys
import os

# Ensure the embed-adapter directory (where app.py lives) is on the path.
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)
