"""
api.py — FastAPI application for noshow-demo ("노쇼가드").

Public demo of a hair-salon booking + no-show automation flow:
  GET  /                          -- landing placeholder (replaced by CMO copy pass)
  GET  /demo                      -- customer-facing booking SPA
  GET  /admin                     -- shop-owner dashboard SPA
  GET  /health                    -- liveness probe (no auth)
  GET  /api/services              -- service menu
  GET  /api/slots                 -- available 30-min slots for a date
  POST /api/reservations          -- create a booking (+ confirm message)
  POST /api/reservations/{id}/cancel -- cancel (+ waitlist auto-fill)
  POST /api/waitlist              -- join the waitlist for a date
  GET  /api/admin/reservations    -- dashboard: today/tomorrow bookings
  GET  /api/admin/waitlist        -- dashboard: waitlist
  GET  /api/admin/messages        -- dashboard: sent-message log (카톡 스타일)
  POST /api/admin/fast-forward    -- demo clock +24h, fires due reminders
  GET  /api/clock                 -- current demo_now (banner display)

No auth (public demo by design — spec §2/§3). No LLM calls, no external DB —
SQLite in-container, wiped + reseeded on boot and every
NOSHOW_RESET_INTERVAL_SECONDS (default 6h, see db.py).
"""
from __future__ import annotations

import asyncio
import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Iterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import config as cfg
import db as database
import engine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_settings: cfg.Settings = cfg.load()
_reset_task: asyncio.Task | None = None


async def _periodic_reset(interval_seconds: int) -> None:
    while True:
        await asyncio.sleep(interval_seconds)
        conn = database.connect(_settings.db_path)
        try:
            database.seed_data(conn)
            logger.info("noshow-demo: periodic reset complete (interval=%ss).", interval_seconds)
        finally:
            conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _reset_task
    conn = database.connect(_settings.db_path)
    try:
        database.init_schema(conn)
        database.seed_data(conn)
    finally:
        conn.close()

    _reset_task = asyncio.create_task(_periodic_reset(_settings.reset_interval_seconds))
    logger.info(
        "noshow-demo service started. db_path=%s reset_interval=%ss",
        _settings.db_path, _settings.reset_interval_seconds,
    )

    yield

    if _reset_task is not None:
        _reset_task.cancel()
        try:
            await _reset_task
        except asyncio.CancelledError:
            pass
    logger.info("noshow-demo service stopped.")


_docs_kwargs = (
    {}
    if _settings.env != "prod"
    else {"docs_url": None, "redoc_url": None, "openapi_url": None}
)

app = FastAPI(
    title="noshow-demo",
    description="노쇼가드 — 미용실 예약·노쇼 자동화 공개 데모 (시뮬레이션, 실발송 없음).",
    version="0.1.0",
    lifespan=lifespan,
    **_docs_kwargs,
)


# ── DB dependency ────────────────────────────────────────────────────────────

def get_conn() -> Iterator[sqlite3.Connection]:
    conn = database.connect(_settings.db_path)
    try:
        yield conn
    finally:
        conn.close()


def get_conn_admin(conn: sqlite3.Connection = Depends(get_conn)) -> Iterator[sqlite3.Connection]:
    """Admin routes lazily evaluate reminders on every GET (spec: 예약 생성·
    빨리감기·admin 조회 시 lazy 평가)."""
    engine.evaluate_reminders(conn)
    yield conn


# ── Schemas ───────────────────────────────────────────────────────────────────

class ServiceOut(BaseModel):
    id: int
    name: str
    price: int
    duration_min: int


class SlotOut(BaseModel):
    time: str
    available: bool


class ReservationCreate(BaseModel):
    service_id: int
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    name: str = Field(..., min_length=1, max_length=30)
    phone: str = Field(..., min_length=1, max_length=20)


class ReservationOut(BaseModel):
    id: int
    service_id: int
    service_name: str
    customer_name: str
    customer_phone: str
    slot_date: str
    slot_time: str
    status: str
    created_at: str
    no_show_risk: bool = False
    """Query-time derived flag (engine.no_show_risk_ids) — never a stored
    column. Only /api/admin/reservations computes it; other endpoints that
    return a ReservationOut (booking creation) default to False."""


class WaitlistCreate(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    name: str = Field(..., min_length=1, max_length=30)
    phone: str = Field(..., min_length=1, max_length=20)


class WaitlistOut(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    desired_date: str
    created_at: str
    fulfilled: bool


class MessageOut(BaseModel):
    id: int
    reservation_id: int | None
    recipient_name: str
    recipient_phone: str
    message_type: str
    body: str
    sent_at: str


class ClockOut(BaseModel):
    demo_now: str
    offset_seconds: int


class FastForwardResult(BaseModel):
    demo_now: str
    messages_sent: int


class CancelResult(BaseModel):
    cancelled: bool
    waitlist_filled: bool
    new_reservation_id: int | None


class HealthResponse(BaseModel):
    status: str


_MESSAGE_TYPE_LABEL = {
    "confirm": "예약 확인",
    "reminder_day_before": "전일 리마인더",
    "reminder_same_day": "당일 리마인더",
    "waitlist_offer": "대기 제안",
    "waitlist_filled": "대기 확정",
}


def _row_to_reservation(row: sqlite3.Row, risky_ids: set[int] | None = None) -> ReservationOut:
    return ReservationOut(
        id=row["id"],
        service_id=row["service_id"],
        service_name=row["service_name"],
        customer_name=row["customer_name"],
        customer_phone=row["customer_phone"],
        slot_date=row["slot_date"],
        slot_time=row["slot_time"],
        status=row["status"],
        created_at=row["created_at"],
        no_show_risk=(risky_ids is not None and row["id"] in risky_ids),
    )


# ── Endpoints: public health ────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["ops"])
async def health():
    return HealthResponse(status="ok")


@app.get("/api/clock", response_model=ClockOut, tags=["demo"])
async def get_clock(conn: sqlite3.Connection = Depends(get_conn)):
    now = engine.demo_now(conn)
    return ClockOut(demo_now=now.isoformat(timespec="seconds"), offset_seconds=engine.get_clock_offset_seconds(conn))


# ── Endpoints: customer-facing (/demo) ──────────────────────────────────────

@app.get("/api/services", response_model=list[ServiceOut], tags=["demo"])
async def list_services(conn: sqlite3.Connection = Depends(get_conn)):
    rows = conn.execute("SELECT id, name, price, duration_min FROM service_menu ORDER BY id").fetchall()
    return [ServiceOut(**dict(r)) for r in rows]


@app.get("/api/dates", response_model=list[str], tags=["demo"])
async def list_dates(conn: sqlite3.Connection = Depends(get_conn)):
    return engine.bookable_dates(engine.demo_now(conn))


@app.get("/api/slots", response_model=list[SlotOut], tags=["demo"])
async def get_slots(date: str, conn: sqlite3.Connection = Depends(get_conn)):
    if date not in engine.bookable_dates(engine.demo_now(conn)):
        raise HTTPException(400, "예약 가능 기간(오늘~7일 후)을 벗어난 날짜입니다.")
    return [SlotOut(**s) for s in engine.available_slots(conn, date)]


@app.post("/api/reservations", response_model=ReservationOut, tags=["demo"])
async def create_reservation(req: ReservationCreate, conn: sqlite3.Connection = Depends(get_conn)):
    try:
        reservation_id = engine.create_reservation(
            conn, req.service_id, req.date, req.time, req.name, req.phone,
        )
    except engine.NoShowDemoError as exc:
        raise HTTPException(400, str(exc)) from exc

    engine.evaluate_reminders(conn)

    row = conn.execute(
        """
        SELECT r.id, r.service_id, s.name AS service_name, r.customer_name, r.customer_phone,
               r.slot_date, r.slot_time, r.status, r.created_at
        FROM reservation r JOIN service_menu s ON s.id = r.service_id
        WHERE r.id = ?
        """,
        (reservation_id,),
    ).fetchone()
    return _row_to_reservation(row)


@app.post("/api/waitlist", response_model=WaitlistOut, tags=["demo"])
async def create_waitlist(req: WaitlistCreate, conn: sqlite3.Connection = Depends(get_conn)):
    try:
        waitlist_id = engine.create_waitlist_entry(conn, req.date, req.name, req.phone)
    except engine.NoShowDemoError as exc:
        raise HTTPException(400, str(exc)) from exc

    row = conn.execute("SELECT * FROM waitlist WHERE id = ?", (waitlist_id,)).fetchone()
    return WaitlistOut(
        id=row["id"], customer_name=row["customer_name"], customer_phone=row["customer_phone"],
        desired_date=row["desired_date"], created_at=row["created_at"], fulfilled=bool(row["fulfilled"]),
    )


# ── Endpoints: admin dashboard (/admin) ─────────────────────────────────────

@app.get("/api/admin/reservations", response_model=list[ReservationOut], tags=["admin"])
async def admin_list_reservations(conn: sqlite3.Connection = Depends(get_conn_admin)):
    rows = conn.execute(
        """
        SELECT r.id, r.service_id, s.name AS service_name, r.customer_name, r.customer_phone,
               r.slot_date, r.slot_time, r.status, r.created_at
        FROM reservation r JOIN service_menu s ON s.id = r.service_id
        ORDER BY r.slot_date ASC, r.slot_time ASC
        """
    ).fetchall()
    # get_conn_admin already ran evaluate_reminders on this conn/request, so
    # reminder_same_day rows (if due) are already in message_log below.
    risky_ids = engine.no_show_risk_ids(conn)
    return [_row_to_reservation(r, risky_ids) for r in rows]


@app.get("/api/admin/waitlist", response_model=list[WaitlistOut], tags=["admin"])
async def admin_list_waitlist(conn: sqlite3.Connection = Depends(get_conn_admin)):
    rows = conn.execute("SELECT * FROM waitlist ORDER BY fulfilled ASC, created_at ASC").fetchall()
    return [
        WaitlistOut(
            id=r["id"], customer_name=r["customer_name"], customer_phone=r["customer_phone"],
            desired_date=r["desired_date"], created_at=r["created_at"], fulfilled=bool(r["fulfilled"]),
        )
        for r in rows
    ]


@app.get("/api/admin/messages", response_model=list[MessageOut], tags=["admin"])
async def admin_list_messages(conn: sqlite3.Connection = Depends(get_conn_admin)):
    rows = conn.execute(
        "SELECT * FROM message_log ORDER BY sent_at DESC, id DESC LIMIT 200"
    ).fetchall()
    return [
        MessageOut(
            id=r["id"], reservation_id=r["reservation_id"], recipient_name=r["recipient_name"],
            recipient_phone=r["recipient_phone"], message_type=r["message_type"], body=r["body"],
            sent_at=r["sent_at"],
        )
        for r in rows
    ]


@app.post("/api/admin/fast-forward", response_model=FastForwardResult, tags=["admin"])
async def admin_fast_forward(conn: sqlite3.Connection = Depends(get_conn)):
    now, sent = engine.fast_forward_one_day(conn)
    return FastForwardResult(demo_now=now.isoformat(timespec="seconds"), messages_sent=sent)


@app.post("/api/admin/reservations/{reservation_id}/cancel", response_model=CancelResult, tags=["admin"])
async def admin_cancel_reservation(reservation_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    try:
        result = engine.cancel_reservation(conn, reservation_id)
    except engine.NoShowDemoError as exc:
        raise HTTPException(404, str(exc)) from exc
    return CancelResult(**result)


# ── Pages + static assets ───────────────────────────────────────────────────
# Mounted last so /api/* takes precedence. web/ absence (rare dev checkout)
# must not crash the API.

_WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


@app.get("/", include_in_schema=False)
async def page_landing():
    return FileResponse(os.path.join(_WEB_DIR, "index.html"))


@app.get("/demo", include_in_schema=False)
async def page_demo():
    return FileResponse(os.path.join(_WEB_DIR, "demo.html"))


@app.get("/admin", include_in_schema=False)
async def page_admin():
    return FileResponse(os.path.join(_WEB_DIR, "admin.html"))


if os.path.isdir(_WEB_DIR):
    app.mount("/static", StaticFiles(directory=_WEB_DIR), name="static")
