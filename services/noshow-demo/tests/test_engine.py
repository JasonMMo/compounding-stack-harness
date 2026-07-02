"""
tests/test_engine.py — unit tests for engine.py (demo clock, reminders,
cancel -> waitlist auto-fill). Uses in-memory SQLite (see tests/conftest.py).
"""
from datetime import datetime, timedelta

import pytest

import engine


def test_reminder_dedup_evaluate_reminders_is_idempotent(conn, service_id):
    """A slot already past both thresholds should get exactly one day-before
    and one same-day reminder no matter how many times evaluate_reminders runs."""
    now = datetime.now()
    slot_dt = now + timedelta(hours=1)  # already inside both the 24h and 3h windows
    reservation_id = engine.create_reservation(
        conn, service_id, slot_dt.strftime(engine.DATE_FMT), slot_dt.strftime(engine.TIME_FMT),
        "홍길동", "010-0000-0001", now=now,
    )

    sent_first = engine.evaluate_reminders(conn, now=now)
    assert sent_first == 2  # day_before + same_day both due

    sent_second = engine.evaluate_reminders(conn, now=now)
    assert sent_second == 0  # dedup — already logged

    rows = conn.execute(
        "SELECT message_type FROM message_log WHERE reservation_id = ?", (reservation_id,)
    ).fetchall()
    types = {r["message_type"] for r in rows}
    assert types == {"confirm", "reminder_day_before", "reminder_same_day"}


def test_fast_forward_sends_due_reminders(conn, service_id):
    """A slot 25h out has neither reminder due yet; one 24h fast-forward should
    cross both the day-before (24h) and same-day (3h) thresholds."""
    now = datetime.now()
    slot_dt = now + timedelta(hours=25)
    reservation_id = engine.create_reservation(
        conn, service_id, slot_dt.strftime(engine.DATE_FMT), slot_dt.strftime(engine.TIME_FMT),
        "김철수", "010-0000-0002", now=now,
    )

    # nothing due yet
    assert engine.evaluate_reminders(conn, now=now) == 0

    _new_now, sent = engine.fast_forward_one_day(conn)
    assert sent == 2

    rows = conn.execute(
        "SELECT message_type FROM message_log WHERE reservation_id = ?", (reservation_id,)
    ).fetchall()
    types = {r["message_type"] for r in rows}
    assert types == {"confirm", "reminder_day_before", "reminder_same_day"}

    # a further fast-forward must not resend
    _newer_now, sent_again = engine.fast_forward_one_day(conn)
    assert sent_again == 0


def test_cancel_fills_slot_from_matching_waitlist(conn, service_id):
    """Cancelling a reservation should offer the freed slot to the first
    waitlist entry for that date and create a new confirmed reservation."""
    now = datetime.now()
    slot_dt = now + timedelta(hours=5)
    date_str, time_str = slot_dt.strftime(engine.DATE_FMT), slot_dt.strftime(engine.TIME_FMT)

    reservation_id = engine.create_reservation(
        conn, service_id, date_str, time_str, "이영희", "010-0000-0003", now=now,
    )
    engine.create_waitlist_entry(conn, date_str, "대기자1", "010-0000-0004", now=now)

    result = engine.cancel_reservation(conn, reservation_id, now=now)

    assert result["cancelled"] is True
    assert result["waitlist_filled"] is True
    new_id = result["new_reservation_id"]
    assert new_id is not None

    cancelled_row = conn.execute("SELECT status FROM reservation WHERE id = ?", (reservation_id,)).fetchone()
    assert cancelled_row["status"] == "cancelled"

    new_row = conn.execute("SELECT * FROM reservation WHERE id = ?", (new_id,)).fetchone()
    assert new_row["customer_name"] == "대기자1"
    assert new_row["slot_date"] == date_str
    assert new_row["slot_time"] == time_str
    assert new_row["status"] == "confirmed"

    waitlist_row = conn.execute("SELECT fulfilled FROM waitlist WHERE customer_name = '대기자1'").fetchone()
    assert waitlist_row["fulfilled"] == 1

    msg_types = {
        r["message_type"]
        for r in conn.execute("SELECT message_type FROM message_log WHERE reservation_id = ?", (new_id,)).fetchall()
    }
    assert "waitlist_filled" in msg_types

    offer_rows = conn.execute(
        "SELECT * FROM message_log WHERE message_type = 'waitlist_offer' AND recipient_name = '대기자1'"
    ).fetchall()
    assert len(offer_rows) == 1


def test_cancel_without_waitlist_only_cancels(conn, service_id):
    now = datetime.now()
    slot_dt = now + timedelta(hours=5)
    reservation_id = engine.create_reservation(
        conn, service_id, slot_dt.strftime(engine.DATE_FMT), slot_dt.strftime(engine.TIME_FMT),
        "박민수", "010-0000-0005", now=now,
    )

    result = engine.cancel_reservation(conn, reservation_id, now=now)

    assert result == {"cancelled": True, "waitlist_filled": False, "new_reservation_id": None}
    row = conn.execute("SELECT status FROM reservation WHERE id = ?", (reservation_id,)).fetchone()
    assert row["status"] == "cancelled"


def test_create_reservation_rejects_double_booking(conn, service_id):
    now = datetime.now()
    slot_dt = now + timedelta(hours=5)
    date_str, time_str = slot_dt.strftime(engine.DATE_FMT), slot_dt.strftime(engine.TIME_FMT)

    engine.create_reservation(conn, service_id, date_str, time_str, "선점자", "010-0000-0006", now=now)

    with pytest.raises(engine.NoShowDemoError):
        engine.create_reservation(conn, service_id, date_str, time_str, "후발주자", "010-0000-0007", now=now)


def test_sanitize_text_strips_dangerous_characters_and_truncates():
    cleaned = engine.sanitize_text('<script>alert(1)</script>이름', 10, "이름")
    assert "<" not in cleaned and ">" not in cleaned
    assert len(cleaned) <= 10

    with pytest.raises(engine.NoShowDemoError):
        engine.sanitize_text("   ", 10, "이름")


def test_no_show_risk_ids_flags_only_reminded_and_imminent_reservations(conn, service_id):
    """no_show_risk_ids is a query-time derived flag, not a stored status
    (CTO correction): a confirmed reservation counts as "노쇼 위험" only once
    its same-day reminder (slot-3h) has already fired AND the slot itself is
    now <=1h away. Same reminder sent but slot still >1h out must NOT flag."""
    now = datetime.now()

    imminent_slot = now + timedelta(minutes=30)
    imminent_id = engine.create_reservation(
        conn, service_id, imminent_slot.strftime(engine.DATE_FMT), imminent_slot.strftime(engine.TIME_FMT),
        "조노쇼", "010-0000-0008", now=now - timedelta(hours=4),
    )

    later_slot = now + timedelta(hours=2)
    later_id = engine.create_reservation(
        conn, service_id, later_slot.strftime(engine.DATE_FMT), later_slot.strftime(engine.TIME_FMT),
        "정상예약", "010-0000-0009", now=now - timedelta(hours=4),
    )

    # both slots are already within the same-day (3h) window relative to `now`
    # (and, since created 4h ago, also within the day-before window), so both
    # get their reminder_same_day fired here.
    engine.evaluate_reminders(conn, now=now)
    same_day_recipients = {
        r["reservation_id"]
        for r in conn.execute(
            "SELECT reservation_id FROM message_log WHERE message_type = 'reminder_same_day'"
        ).fetchall()
    }
    assert same_day_recipients == {imminent_id, later_id}

    risky = engine.no_show_risk_ids(conn, now=now)
    assert imminent_id in risky
    assert later_id not in risky


def test_available_slots_hides_past_times_for_today(conn):
    now = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
    engine.set_clock_offset_seconds(conn, int((now - datetime.now()).total_seconds()))

    today_str = engine.demo_now(conn).strftime(engine.DATE_FMT)
    slots = {s["time"]: s["available"] for s in engine.available_slots(conn, today_str)}

    assert slots["10:00"] is False  # already past 15:00
    assert slots["18:30"] is True  # still ahead
