"""
engine.py — pure(ish) demo logic for noshow-demo: demo clock, reminder rules,
cancel -> waitlist auto-fill. All functions take an open sqlite3.Connection
(row_factory=sqlite3.Row) and are unit-testable without the FastAPI app.

DEMO CLOCK: `demo_now(conn)` = wall-clock time + an offset stored in
`settings.clock_offset_seconds`. The "하루 빨리감기" admin button advances the
offset by 24h so reminder thresholds can be demonstrated in seconds instead
of waiting real hours/days.

REMINDER DEDUP: message_log rows are the source of truth for "already sent" —
evaluate_reminders() is idempotent and safe to call on every request (lazy
eval per docs/business/noshow-demo-spec.md, no background scheduler needed
for reminder timing — only for the 6h full reseed in db.py).
"""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timedelta

DATE_FMT = "%Y-%m-%d"
TIME_FMT = "%H:%M"

_WEEKDAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]

_SHOP_NAME = "데모 미용실"

_BUSINESS_START_HOUR = 10
_BUSINESS_LAST_SLOT_HOUR = 18
_BUSINESS_LAST_SLOT_MINUTE = 30


class NoShowDemoError(ValueError):
    """User-facing validation error (400s at the API layer)."""


# ── Slot / date helpers ─────────────────────────────────────────────────────

def business_slots() -> list[str]:
    """30-min slot start times, 10:00 .. 18:30 (last slot ends 19:00)."""
    return [f"{h:02d}:{m:02d}" for h in range(_BUSINESS_START_HOUR, 19) for m in (0, 30)]


def bookable_dates(today: datetime, days_ahead: int = 7) -> list[str]:
    """오늘 ~ +days_ahead (inclusive), as YYYY-MM-DD strings."""
    base = today.date()
    return [(base + timedelta(days=i)).strftime(DATE_FMT) for i in range(days_ahead + 1)]


def parse_slot_dt(date_str: str, time_str: str) -> datetime:
    try:
        return datetime.strptime(f"{date_str} {time_str}", f"{DATE_FMT} {TIME_FMT}")
    except ValueError as exc:
        raise NoShowDemoError(f"날짜/시간 형식이 올바르지 않습니다: {date_str} {time_str}") from exc


def next_business_slot(base: datetime, hours_ahead: float) -> datetime:
    """Round `base + hours_ahead` up to the next 30-min mark, then clamp into
    business hours (10:00-18:30), rolling to the next day if needed."""
    target = base + timedelta(hours=hours_ahead)
    discard = timedelta(minutes=target.minute % 30, seconds=target.second, microseconds=target.microsecond)
    target -= discard
    if discard > timedelta(0):
        target += timedelta(minutes=30)

    while True:
        if target.hour < _BUSINESS_START_HOUR:
            target = target.replace(hour=_BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
            break
        if target.hour > _BUSINESS_LAST_SLOT_HOUR or (
            target.hour == _BUSINESS_LAST_SLOT_HOUR and target.minute > _BUSINESS_LAST_SLOT_MINUTE
        ):
            target = (target + timedelta(days=1)).replace(
                hour=_BUSINESS_START_HOUR, minute=0, second=0, microsecond=0
            )
            continue
        break
    return target


def _fmt_date_kr(date_str: str) -> str:
    d = datetime.strptime(date_str, DATE_FMT).date()
    return f"{d.month}월 {d.day}일({_WEEKDAYS_KR[d.weekday()]})"


# ── Input sanitation (defense in depth — the UI also uses textContent, never
#    innerHTML, but message_log bodies embed user-supplied names/phones and
#    must be safe regardless of render path) ────────────────────────────────

_STRIP_RE = re.compile(r"[\x00-\x1f\x7f<>\"'`]")


def sanitize_text(value: str | None, max_len: int, field_label: str = "입력값") -> str:
    if value is None:
        raise NoShowDemoError(f"{field_label}이(가) 필요합니다.")
    v = _STRIP_RE.sub("", str(value).strip())
    if not v:
        raise NoShowDemoError(f"{field_label}이(가) 비어 있습니다.")
    return v[:max_len]


# ── Demo clock ───────────────────────────────────────────────────────────────

def get_clock_offset_seconds(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT value FROM settings WHERE key = 'clock_offset_seconds'"
    ).fetchone()
    return int(row["value"]) if row is not None else 0


def set_clock_offset_seconds(conn: sqlite3.Connection, seconds: int) -> None:
    conn.execute(
        """
        INSERT INTO settings(key, value) VALUES ('clock_offset_seconds', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (str(seconds),),
    )
    conn.commit()


def demo_now(conn: sqlite3.Connection) -> datetime:
    return datetime.now() + timedelta(seconds=get_clock_offset_seconds(conn))


def fast_forward_one_day(conn: sqlite3.Connection) -> tuple[datetime, int]:
    """Advance the demo clock by 24h, then lazily evaluate reminders.
    Returns (new demo_now, count of messages sent by this call)."""
    offset = get_clock_offset_seconds(conn)
    set_clock_offset_seconds(conn, offset + 24 * 3600)
    now = demo_now(conn)
    sent = evaluate_reminders(conn, now)
    return now, sent


# ── Message templates ───────────────────────────────────────────────────────

def _tpl_confirm(service_name: str, date_str: str, time_str: str) -> str:
    return (
        f"[{_SHOP_NAME}] 예약이 확정되었습니다. {_fmt_date_kr(date_str)} {time_str} · "
        f"{service_name}. 예약일이 다가오면 리마인더를 보내드릴게요!"
    )


def _tpl_day_before(service_name: str, date_str: str, time_str: str) -> str:
    return (
        f"[{_SHOP_NAME}] 내일 {_fmt_date_kr(date_str)} {time_str} {service_name} "
        f"예약이 있습니다. 잊지 말고 방문해주세요!"
    )


def _tpl_same_day(service_name: str, date_str: str, time_str: str) -> str:
    return (
        f"[{_SHOP_NAME}] 오늘 {time_str} {service_name} 예약 시간이 다가옵니다. "
        f"곧 뵙겠습니다!"
    )


def _tpl_waitlist_offer(name: str, date_str: str, time_str: str, service_name: str) -> str:
    return (
        f"[{_SHOP_NAME}] {name}님, 대기 신청하신 {_fmt_date_kr(date_str)}에 빈 자리가 "
        f"생겼습니다! {time_str} {service_name}으로 예약을 확정해드렸습니다."
    )


def _tpl_waitlist_filled(name: str, date_str: str, time_str: str, service_name: str) -> str:
    return (
        f"[{_SHOP_NAME}] {name}님, {_fmt_date_kr(date_str)} {time_str} {service_name} "
        f"예약이 확정되었습니다. 감사합니다!"
    )


def _log_message(
    conn: sqlite3.Connection,
    reservation_id: int | None,
    recipient_name: str,
    recipient_phone: str,
    message_type: str,
    body: str,
    sent_at: datetime,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO message_log
            (reservation_id, recipient_name, recipient_phone, message_type, body, sent_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (reservation_id, recipient_name, recipient_phone, message_type, body, sent_at.isoformat(timespec="seconds")),
    )
    return cur.lastrowid


# ── Reservation lifecycle ───────────────────────────────────────────────────

def create_reservation(
    conn: sqlite3.Connection,
    service_id: int,
    date_str: str,
    time_str: str,
    name: str,
    phone: str,
    now: datetime | None = None,
) -> int:
    name = sanitize_text(name, 30, "이름")
    phone = sanitize_text(phone, 20, "연락처")
    if now is None:
        now = demo_now(conn)

    svc = conn.execute(
        "SELECT id, name FROM service_menu WHERE id = ?", (service_id,)
    ).fetchone()
    if svc is None:
        raise NoShowDemoError("존재하지 않는 시술입니다.")

    parse_slot_dt(date_str, time_str)  # format validation

    taken = conn.execute(
        "SELECT 1 FROM reservation WHERE slot_date = ? AND slot_time = ? AND status = 'confirmed'",
        (date_str, time_str),
    ).fetchone()
    if taken is not None:
        raise NoShowDemoError("이미 예약된 시간입니다. 다른 시간을 선택해주세요.")

    cur = conn.execute(
        """
        INSERT INTO reservation
            (service_id, customer_name, customer_phone, slot_date, slot_time, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'confirmed', ?)
        """,
        (service_id, name, phone, date_str, time_str, now.isoformat(timespec="seconds")),
    )
    reservation_id = cur.lastrowid
    _log_message(
        conn, reservation_id, name, phone, "confirm",
        _tpl_confirm(svc["name"], date_str, time_str), now,
    )
    conn.commit()
    return reservation_id


def create_waitlist_entry(
    conn: sqlite3.Connection,
    date_str: str,
    name: str,
    phone: str,
    now: datetime | None = None,
) -> int:
    name = sanitize_text(name, 30, "이름")
    phone = sanitize_text(phone, 20, "연락처")
    if now is None:
        now = demo_now(conn)
    try:
        datetime.strptime(date_str, DATE_FMT)
    except ValueError as exc:
        raise NoShowDemoError(f"날짜 형식이 올바르지 않습니다: {date_str}") from exc

    cur = conn.execute(
        """
        INSERT INTO waitlist (customer_name, customer_phone, desired_date, created_at, fulfilled)
        VALUES (?, ?, ?, ?, 0)
        """,
        (name, phone, date_str, now.isoformat(timespec="seconds")),
    )
    conn.commit()
    return cur.lastrowid


def evaluate_reminders(conn: sqlite3.Connection, now: datetime | None = None) -> int:
    """Lazily send day-before (slot-24h) and same-day (slot-3h) reminders for
    every confirmed reservation, deduped via message_log. Call on: reservation
    creation, fast-forward, and every admin GET (per spec — no background
    scheduler for reminder timing, only for the 6h reseed)."""
    if now is None:
        now = demo_now(conn)

    rows = conn.execute(
        """
        SELECT r.id, r.customer_name, r.customer_phone, r.slot_date, r.slot_time,
               s.name AS service_name
        FROM reservation r
        JOIN service_menu s ON s.id = r.service_id
        WHERE r.status = 'confirmed'
        """
    ).fetchall()

    sent_count = 0
    for row in rows:
        slot_dt = parse_slot_dt(row["slot_date"], row["slot_time"])
        existing = {
            r["message_type"]
            for r in conn.execute(
                "SELECT message_type FROM message_log WHERE reservation_id = ?", (row["id"],)
            ).fetchall()
        }

        if now >= slot_dt - timedelta(hours=24) and "reminder_day_before" not in existing:
            _log_message(
                conn, row["id"], row["customer_name"], row["customer_phone"],
                "reminder_day_before",
                _tpl_day_before(row["service_name"], row["slot_date"], row["slot_time"]),
                now,
            )
            sent_count += 1

        if now >= slot_dt - timedelta(hours=3) and "reminder_same_day" not in existing:
            _log_message(
                conn, row["id"], row["customer_name"], row["customer_phone"],
                "reminder_same_day",
                _tpl_same_day(row["service_name"], row["slot_date"], row["slot_time"]),
                now,
            )
            sent_count += 1

    conn.commit()
    return sent_count


def no_show_risk_ids(conn: sqlite3.Connection, now: datetime | None = None) -> set[int]:
    """Reservation ids flagged "노쇼 위험" for the admin dashboard.

    Deliberately NOT based on customer non-response — the demo has no reply
    channel, so "무응답" can't be derived. Decision rule (CTO correction,
    docs/business/noshow-demo-spec.md follow-up): a confirmed reservation is
    at risk once its same-day reminder (slot-3h) has already been sent AND
    the appointment itself is now within 1h. This is a query-time derived
    flag, not a stored status — no reservation.status write happens here."""
    if now is None:
        now = demo_now(conn)

    rows = conn.execute(
        "SELECT id, slot_date, slot_time FROM reservation WHERE status = 'confirmed'"
    ).fetchall()

    risky: set[int] = set()
    for row in rows:
        slot_dt = parse_slot_dt(row["slot_date"], row["slot_time"])
        if now < slot_dt - timedelta(hours=1):
            continue
        sent = conn.execute(
            "SELECT 1 FROM message_log WHERE reservation_id = ? AND message_type = 'reminder_same_day'",
            (row["id"],),
        ).fetchone()
        if sent is not None:
            risky.add(row["id"])
    return risky


def cancel_reservation(
    conn: sqlite3.Connection, reservation_id: int, now: datetime | None = None
) -> dict:
    """Cancel a confirmed reservation. If a waitlist entry exists (preferring
    one matching the freed slot's date, else the oldest overall), auto-fill
    the slot: offer message -> new reservation -> filled message."""
    if now is None:
        now = demo_now(conn)

    res = conn.execute("SELECT * FROM reservation WHERE id = ?", (reservation_id,)).fetchone()
    if res is None:
        raise NoShowDemoError("존재하지 않는 예약입니다.")
    if res["status"] != "confirmed":
        return {"cancelled": False, "waitlist_filled": False, "new_reservation_id": None}

    conn.execute("UPDATE reservation SET status = 'cancelled' WHERE id = ?", (reservation_id,))

    candidate = conn.execute(
        "SELECT * FROM waitlist WHERE fulfilled = 0 AND desired_date = ? ORDER BY created_at ASC, id ASC LIMIT 1",
        (res["slot_date"],),
    ).fetchone()
    if candidate is None:
        candidate = conn.execute(
            "SELECT * FROM waitlist WHERE fulfilled = 0 ORDER BY created_at ASC, id ASC LIMIT 1"
        ).fetchone()

    result: dict = {"cancelled": True, "waitlist_filled": False, "new_reservation_id": None}

    if candidate is not None:
        svc = conn.execute(
            "SELECT name FROM service_menu WHERE id = ?", (res["service_id"],)
        ).fetchone()
        service_name = svc["name"] if svc is not None else "시술"

        _log_message(
            conn, None, candidate["customer_name"], candidate["customer_phone"],
            "waitlist_offer",
            _tpl_waitlist_offer(candidate["customer_name"], res["slot_date"], res["slot_time"], service_name),
            now,
        )

        cur = conn.execute(
            """
            INSERT INTO reservation
                (service_id, customer_name, customer_phone, slot_date, slot_time, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'confirmed', ?)
            """,
            (
                res["service_id"], candidate["customer_name"], candidate["customer_phone"],
                res["slot_date"], res["slot_time"], now.isoformat(timespec="seconds"),
            ),
        )
        new_reservation_id = cur.lastrowid

        _log_message(
            conn, new_reservation_id, candidate["customer_name"], candidate["customer_phone"],
            "waitlist_filled",
            _tpl_waitlist_filled(candidate["customer_name"], res["slot_date"], res["slot_time"], service_name),
            now,
        )

        conn.execute("UPDATE waitlist SET fulfilled = 1 WHERE id = ?", (candidate["id"],))

        result["waitlist_filled"] = True
        result["new_reservation_id"] = new_reservation_id

    conn.commit()
    return result


def available_slots(conn: sqlite3.Connection, date_str: str) -> list[dict]:
    """business_slots() for date_str, marked unavailable if already booked or
    (for today) already in the past relative to demo_now."""
    now = demo_now(conn)
    today_str = now.strftime(DATE_FMT)

    taken = {
        row["slot_time"]
        for row in conn.execute(
            "SELECT slot_time FROM reservation WHERE slot_date = ? AND status = 'confirmed'",
            (date_str,),
        ).fetchall()
    }

    out = []
    for t in business_slots():
        avail = t not in taken
        if avail and date_str == today_str:
            if parse_slot_dt(date_str, t) <= now:
                avail = False
        out.append({"time": t, "available": avail})
    return out
