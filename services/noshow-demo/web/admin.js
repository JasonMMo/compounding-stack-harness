/* services/noshow-demo/web/admin.js
 * Shop-owner dashboard (/admin). Vanilla JS, no build step.
 * All server-supplied strings render via textContent — never innerHTML.
 */
(() => {
  "use strict";

  const MESSAGE_TYPE_LABEL = {
    confirm: "예약 확인",
    reminder_day_before: "전일 리마인더",
    reminder_same_day: "당일 리마인더",
    waitlist_offer: "대기 제안",
    waitlist_filled: "대기 확정",
  };

  const STATUS_LABEL = {
    confirmed: "예약중",
    cancelled: "취소됨",
  };

  const el = {
    clockValue: document.getElementById("clock-value"),
    btnFastForward: document.getElementById("btn-fast-forward"),
    fastForwardResult: document.getElementById("fast-forward-result"),
    reservationsTbody: document.getElementById("reservations-tbody"),
    waitlistList: document.getElementById("waitlist-list"),
    messageLog: document.getElementById("message-log"),
  };

  async function fetchJSON(url, opts) {
    const res = await fetch(url, opts);
    const body = await res.json().catch(() => null);
    if (!res.ok) {
      const detail = (body && body.detail) || "요청을 처리하지 못했습니다.";
      throw new Error(detail);
    }
    return body;
  }

  function fmtSentAt(iso) {
    // "2026-07-02T14:30:00" -> "07/02 14:30"
    const m = iso.match(/^\d{4}-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
    return m ? `${m[1]}/${m[2]} ${m[3]}:${m[4]}` : iso;
  }

  // ── Renderers ──────────────────────────────────────────────────────────

  function renderClock(demoNow) {
    const m = demoNow.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
    el.clockValue.textContent = m ? `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}` : demoNow;
  }

  function renderReservations(reservations) {
    el.reservationsTbody.innerHTML = "";
    if (!reservations.length) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 6;
      td.className = "table-empty";
      td.textContent = "예약이 없습니다.";
      tr.appendChild(td);
      el.reservationsTbody.appendChild(tr);
      return;
    }
    for (const r of reservations) {
      const tr = document.createElement("tr");

      const tdDate = document.createElement("td");
      tdDate.textContent = r.slot_date;
      const tdTime = document.createElement("td");
      tdTime.textContent = r.slot_time;
      const tdService = document.createElement("td");
      tdService.textContent = r.service_name;
      const tdCustomer = document.createElement("td");
      tdCustomer.textContent = `${r.customer_name} (${r.customer_phone})`;

      const tdStatus = document.createElement("td");
      const badge = document.createElement("span");
      badge.className = `status-badge status-badge--${r.status}`;
      badge.textContent = STATUS_LABEL[r.status] || r.status;
      tdStatus.appendChild(badge);
      if (r.no_show_risk) {
        const riskBadge = document.createElement("span");
        riskBadge.className = "status-badge status-badge--risk";
        riskBadge.textContent = "⚠ 노쇼 위험";
        tdStatus.appendChild(riskBadge);
      }

      const tdAction = document.createElement("td");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn--cancel-row";
      btn.textContent = "취소";
      btn.disabled = r.status !== "confirmed";
      btn.addEventListener("click", () => cancelReservation(r.id));
      tdAction.appendChild(btn);

      tr.append(tdDate, tdTime, tdService, tdCustomer, tdStatus, tdAction);
      el.reservationsTbody.appendChild(tr);
    }
  }

  function renderWaitlist(entries) {
    el.waitlistList.innerHTML = "";
    if (!entries.length) {
      const li = document.createElement("li");
      li.className = "table-empty";
      li.textContent = "대기명단이 없습니다.";
      el.waitlistList.appendChild(li);
      return;
    }
    for (const w of entries) {
      const li = document.createElement("li");
      li.className = "waitlist-item" + (w.fulfilled ? " waitlist-item--fulfilled" : "");

      const left = document.createElement("span");
      left.textContent = `${w.customer_name} (${w.customer_phone})`;
      const right = document.createElement("span");
      right.textContent = w.fulfilled ? `${w.desired_date} · 채움 완료` : `${w.desired_date} 희망`;

      li.append(left, right);
      el.waitlistList.appendChild(li);
    }
  }

  function renderMessages(messages) {
    el.messageLog.innerHTML = "";
    if (!messages.length) {
      const p = document.createElement("p");
      p.className = "table-empty";
      p.textContent = "발송된 메시지가 없습니다.";
      el.messageLog.appendChild(p);
      return;
    }
    for (const msg of messages) {
      const bubble = document.createElement("div");
      bubble.className = "chat-bubble";

      const meta = document.createElement("div");
      meta.className = "chat-bubble__meta";
      const label = document.createElement("span");
      label.textContent = `${MESSAGE_TYPE_LABEL[msg.message_type] || msg.message_type} → ${msg.recipient_name}`;
      const time = document.createElement("span");
      time.textContent = fmtSentAt(msg.sent_at);
      meta.append(label, time);

      const body = document.createElement("div");
      body.className = "chat-bubble__body";
      body.textContent = msg.body;

      bubble.append(meta, body);
      el.messageLog.appendChild(bubble);
    }
  }

  // ── Data loading ───────────────────────────────────────────────────────

  async function refreshAll() {
    const [clock, reservations, waitlist, messages] = await Promise.all([
      fetchJSON("/api/clock"),
      fetchJSON("/api/admin/reservations"),
      fetchJSON("/api/admin/waitlist"),
      fetchJSON("/api/admin/messages"),
    ]);
    renderClock(clock.demo_now);
    renderReservations(reservations);
    renderWaitlist(waitlist);
    renderMessages(messages);
  }

  async function cancelReservation(id) {
    try {
      await fetchJSON(`/api/admin/reservations/${id}/cancel`, { method: "POST" });
      await refreshAll();
    } catch (err) {
      window.alert(err.message || "취소에 실패했습니다.");
    }
  }

  async function fastForward() {
    el.btnFastForward.disabled = true;
    el.fastForwardResult.hidden = true;
    try {
      const result = await fetchJSON("/api/admin/fast-forward", { method: "POST" });
      await refreshAll();
      el.fastForwardResult.textContent =
        result.messages_sent > 0
          ? `${result.messages_sent}건의 새 메시지가 발송되었습니다.`
          : "시간이 하루 지났지만 새로 발송된 메시지는 없습니다.";
      el.fastForwardResult.hidden = false;
    } catch (err) {
      window.alert(err.message || "빨리감기에 실패했습니다.");
    } finally {
      el.btnFastForward.disabled = false;
    }
  }

  el.btnFastForward.addEventListener("click", fastForward);

  refreshAll().catch((err) => {
    el.reservationsTbody.innerHTML = "";
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 6;
    td.className = "table-empty";
    td.textContent = err.message || "데이터를 불러오지 못했습니다.";
    tr.appendChild(td);
    el.reservationsTbody.appendChild(tr);
  });
})();
