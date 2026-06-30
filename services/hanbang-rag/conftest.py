"""
conftest.py — pytest path setup for services/hanbang-rag/.

Ensures modules (config, db, ingest, retrieve, citation, embed_client)
are importable regardless of the working directory pytest is invoked from.
"""
import sys
import os

# Insert services/hanbang-rag/ at the front of sys.path so bare module imports
# (e.g. `import retrieve`) resolve correctly from any invocation directory.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
