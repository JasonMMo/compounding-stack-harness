"""
tests/conftest.py — fixtures for noshow-demo engine tests.

Uses an in-memory SQLite connection (schema only, no seed data by default) so
tests are fast and fully isolated from any real /data/noshow.db.
"""
import os
import sys

_PARENT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

import pytest  # noqa: E402

import db as database  # noqa: E402
import engine  # noqa: E402


@pytest.fixture
def conn():
    c = database.connect(":memory:")
    database.init_schema(c)
    try:
        yield c
    finally:
        c.close()


@pytest.fixture
def service_id(conn):
    cur = conn.execute(
        "INSERT INTO service_menu (name, price, duration_min) VALUES ('커트', 25000, 40)"
    )
    conn.commit()
    return cur.lastrowid
