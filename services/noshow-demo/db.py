"""
db.py — SQLite schema, connection helper, and seed/reset for noshow-demo.

Design (docs/business/noshow-demo-spec.md §4):
  - SQLite in-container, zero external DB dependency, zero volume mount.
  - Data resets on process start AND every `NOSHOW_RESET_INTERVAL_SECONDS`
    (default 6h) — public demo, reset prevents pollution/abuse accumulation.
  - Reset is a hard wipe + reseed, not a migration — schema stays tiny on purpose.
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta

import engine

DEFAULT_DB_PATH = os.environ.get("NOSHOW_DB_PATH", "/data/noshow.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS service_menu (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    price        INTEGER NOT NULL,
    duration_min INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS reservation (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id     INTEGER NOT NULL REFERENCES service_menu(id),
    customer_name  TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    slot_date      TEXT NOT NULL,
    slot_time      TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'confirmed',
    created_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reservation_slot ON reservation(slot_date, slot_time);
CREATE INDEX IF NOT EXISTS idx_reservation_status ON reservation(status);

CREATE TABLE IF NOT EXISTS waitlist (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name  TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    desired_date   TEXT NOT NULL,
    created_at     TEXT NOT NULL,
    fulfilled      INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_waitlist_pending ON waitlist(fulfilled, desired_date);

CREATE TABLE IF NOT EXISTS message_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id  INTEGER REFERENCES reservation(id),
    recipient_name  TEXT NOT NULL,
    recipient_phone TEXT NOT NULL,
    message_type    TEXT NOT NULL,
    body            TEXT NOT NULL,
    sent_at         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_message_log_reservation ON message_log(reservation_id);
CREATE INDEX IF NOT EXISTS idx_message_log_sent_at ON message_log(sent_at);
"""

_SEED_SERVICES = [
    ("커트", 25000, 40),
    ("펌", 90000, 120),
    ("염색", 80000, 90),
    ("두피케어", 60000, 60),
    ("클리닉 트리트먼트", 50000, 50),
    ("드라이 스타일링", 20000, 30),
]

# (hours_ahead from seed time, service name) — spread across today/tomorrow/+2d
# so the demo clock's "빨리감기"(24h) button progressively crosses the
# day-before (24h) and same-day (3h) reminder thresholds across a couple of
# presses instead of firing everything on seed.
_SEED_PLAN = [
    (3, "커트"),
    (6, "두피케어"),
    (20, "드라이 스타일링"),
    (30, "염색"),
    (50, "펌"),
]

_SEED_CUSTOMERS = [
    ("김민지", "010-1234-5678"),
    ("이서준", "010-2345-6789"),
    ("박하늘", "010-3456-7890"),
    ("최유진", "010-4567-8901"),
    ("정도윤", "010-5678-9012"),
]

_SEED_WAITLIST = [
    ("이대기", "010-1111-2222"),
    ("박대기", "010-3333-4444"),
]

# A reservation whose slot is already <=1h out, seeded so admin's very first
# GET (which lazily evaluates reminders via engine.evaluate_reminders) fires
# the same-day reminder immediately and engine.no_show_risk_ids() flags it
# right away — no "빨리감기" needed for the demo screenshot (CTO correction).
# Deliberately bypasses next_business_slot's business-hour clamp: slot_dt is
# `now` rounded down to the 30-min grid, so this works regardless of the
# time of day the container happens to boot.
_SEED_RISK_CUSTOMER = ("조노쇼", "010-7777-8888")


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def connect(db_path: str | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    if path != ":memory:":
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(path, timeout=5, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _reset_tables(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM message_log")
    conn.execute("DELETE FROM waitlist")
    conn.execute("DELETE FROM reservation")
    conn.execute("DELETE FROM service_menu")
    conn.execute("DELETE FROM settings")
    try:
        conn.execute("DELETE FROM sqlite_sequence")
    except sqlite3.OperationalError:
        pass  # sqlite_sequence only exists once an AUTOINCREMENT table has inserted a row
    conn.commit()


def seed_data(conn: sqlite3.Connection, now: datetime | None = None) -> None:
    """Wipe all tables and reseed deterministic demo data. Safe to call
    repeatedly (startup + periodic 6h reset)."""
    if now is None:
        now = datetime.now()

    _reset_tables(conn)
    engine.set_clock_offset_seconds(conn, 0)

    service_ids: dict[str, int] = {}
    for name, price, duration_min in _SEED_SERVICES:
        cur = conn.execute(
            "INSERT INTO service_menu (name, price, duration_min) VALUES (?, ?, ?)",
            (name, price, duration_min),
        )
        service_ids[name] = cur.lastrowid
    conn.commit()

    used_slots: set[tuple[str, str]] = set()
    for (hours_ahead, service_name), (cust_name, cust_phone) in zip(_SEED_PLAN, _SEED_CUSTOMERS):
        slot_dt = engine.next_business_slot(now, hours_ahead)
        while (slot_dt.strftime(engine.DATE_FMT), slot_dt.strftime(engine.TIME_FMT)) in used_slots:
            slot_dt = engine.next_business_slot(slot_dt, 0.5)
        used_slots.add((slot_dt.strftime(engine.DATE_FMT), slot_dt.strftime(engine.TIME_FMT)))

        engine.create_reservation(
            conn,
            service_ids[service_name],
            slot_dt.strftime(engine.DATE_FMT),
            slot_dt.strftime(engine.TIME_FMT),
            cust_name,
            cust_phone,
            now=now,
        )

    tomorrow = (now + timedelta(days=1)).strftime(engine.DATE_FMT)
    for name, phone in _SEED_WAITLIST:
        engine.create_waitlist_entry(conn, tomorrow, name, phone, now=now)

    risk_dt = now.replace(second=0, microsecond=0) - timedelta(minutes=now.minute % 30)
    while (risk_dt.strftime(engine.DATE_FMT), risk_dt.strftime(engine.TIME_FMT)) in used_slots:
        risk_dt -= timedelta(minutes=30)
    risk_name, risk_phone = _SEED_RISK_CUSTOMER
    engine.create_reservation(
        conn,
        service_ids["커트"],
        risk_dt.strftime(engine.DATE_FMT),
        risk_dt.strftime(engine.TIME_FMT),
        risk_name,
        risk_phone,
        now=now,
    )
