/* services/noshow-demo/web/demo.js
 * Customer-facing booking flow (/demo). Vanilla JS, no build step.
 * All server-supplied strings are inserted via textContent — never
 * innerHTML — so sanitize_text() on the backend is defense-in-depth, not
 * the only XSS guard.
 */
(() => {
  "use strict";

  const WEEKDAYS_KR = ["일", "월", "화", "수", "목", "금", "토"];

  const state = {
    services: [],
    dates: [],
    serviceId: null,
    date: null,
    time: null,
  };

  const el = {
    serviceList: document.getElementById("service-list"),
    dateChips: document.getElementById("date-chips"),
    slotGrid: document.getElementById("slot-grid"),
    slotEmptyMsg: document.getElementById("slot-empty-msg"),
    contactStep: document.getElementById("contact-step"),
    bookingForm: document.getElementById("booking-form"),
    bookingAlert: document.getElementById("booking-alert"),
    nameInput: document.getElementById("booking-name"),
    phoneInput: document.getElementById("booking-phone"),
    screenBooking: document.getElementById("screen-booking"),
    screenComplete: document.getElementById("screen-complete"),
    completeSummary: document.getElementById("complete-summary"),
    btnBookAnother: document.getElementById("btn-book-another"),
    btnToggleWaitlist: document.getElementById("btn-toggle-waitlist"),
    waitlistPanel: document.getElementById("waitlist-panel"),
    waitlistForm: document.getElementById("waitlist-form"),
    waitlistAlert: document.getElementById("waitlist-alert"),
    waitlistSuccess: document.getElementById("waitlist-success"),
    waitlistDateSelect: document.getElementById("waitlist-date"),
    waitlistName: document.getElementById("waitlist-name"),
    waitlistPhone: document.getElementById("waitlist-phone"),
  };

  function dateLabel(dateStr, idx) {
    if (idx === 0) return "오늘";
    if (idx === 1) return "내일";
    const d = new Date(`${dateStr}T00:00:00`);
    return `${d.getMonth() + 1}/${d.getDate()}(${WEEKDAYS_KR[d.getDay()]})`;
  }

  function showAlert(node, message) {
    node.textContent = message;
    node.hidden = false;
  }

  function hideAlert(node) {
    node.hidden = true;
    node.textContent = "";
  }

  async function fetchJSON(url, opts) {
    const res = await fetch(url, opts);
    const body = await res.json().catch(() => null);
    if (!res.ok) {
      const detail = (body && body.detail) || "요청을 처리하지 못했습니다.";
      throw new Error(detail);
    }
    return body;
  }

  // ── Rendering ──────────────────────────────────────────────────────────

  function renderServices() {
    el.serviceList.innerHTML = "";
    for (const svc of state.services) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "service-card";
      btn.setAttribute("role", "radio");
      btn.setAttribute("aria-checked", String(svc.id === state.serviceId));

      const name = document.createElement("span");
      name.className = "service-card__name";
      name.textContent = svc.name;

      const meta = document.createElement("span");
      meta.className = "service-card__meta";
      meta.textContent = `${svc.price.toLocaleString("ko-KR")}원 · ${svc.duration_min}분`;

      btn.append(name, meta);
      btn.addEventListener("click", () => {
        state.serviceId = svc.id;
        state.time = null;
        renderServices();
        renderContactStep();
        refreshSlots();
      });
      el.serviceList.appendChild(btn);
    }
  }

  function renderDateChips() {
    el.dateChips.innerHTML = "";
    state.dates.forEach((dateStr, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "date-chip";
      btn.setAttribute("role", "radio");
      btn.setAttribute("aria-checked", String(dateStr === state.date));
      btn.textContent = dateLabel(dateStr, idx);
      btn.addEventListener("click", () => {
        state.date = dateStr;
        state.time = null;
        renderDateChips();
        renderContactStep();
        refreshSlots();
      });
      el.dateChips.appendChild(btn);
    });
  }

  function renderSlots(slots) {
    el.slotGrid.innerHTML = "";
    if (!state.serviceId || !state.date) {
      el.slotGrid.appendChild(el.slotEmptyMsg);
      return;
    }
    if (!slots.length) {
      const p = document.createElement("p");
      p.className = "slot-grid__empty";
      p.textContent = "선택 가능한 시간이 없습니다.";
      el.slotGrid.appendChild(p);
      return;
    }
    for (const slot of slots) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "slot-btn";
      btn.textContent = slot.time;
      btn.disabled = !slot.available;
      btn.setAttribute("role", "radio");
      btn.setAttribute("aria-checked", String(slot.time === state.time));
      if (slot.available) {
        btn.addEventListener("click", () => {
          state.time = slot.time;
          renderContactStep();
          // re-render just the aria-checked state without refetching
          [...el.slotGrid.children].forEach((c) => {
            if (c.tagName === "BUTTON") c.setAttribute("aria-checked", String(c.textContent === state.time));
          });
        });
      }
      el.slotGrid.appendChild(btn);
    }
  }

  function renderContactStep() {
    el.contactStep.hidden = !(state.serviceId && state.date && state.time);
  }

  async function refreshSlots() {
    hideAlert(el.bookingAlert);
    if (!state.date) {
      renderSlots([]);
      return;
    }
    try {
      const slots = await fetchJSON(`/api/slots?date=${encodeURIComponent(state.date)}`);
      renderSlots(slots);
    } catch (err) {
      showAlert(el.bookingAlert, err.message);
    }
  }

  function serviceById(id) {
    return state.services.find((s) => s.id === id);
  }

  // ── Actions ────────────────────────────────────────────────────────────

  async function loadInitialData() {
    const [services, dates] = await Promise.all([
      fetchJSON("/api/services"),
      fetchJSON("/api/dates"),
    ]);
    state.services = services;
    state.dates = dates;
    state.date = dates[0] || null;

    renderServices();
    renderDateChips();
    renderSlots([]);
    populateWaitlistDates();
    await refreshSlots();
  }

  function populateWaitlistDates() {
    el.waitlistDateSelect.innerHTML = "";
    state.dates.forEach((dateStr, idx) => {
      const opt = document.createElement("option");
      opt.value = dateStr;
      opt.textContent = `${dateLabel(dateStr, idx)} (${dateStr})`;
      el.waitlistDateSelect.appendChild(opt);
    });
  }

  async function submitBooking(evt) {
    evt.preventDefault();
    hideAlert(el.bookingAlert);
    const name = el.nameInput.value.trim();
    const phone = el.phoneInput.value.trim();
    if (!name || !phone) {
      showAlert(el.bookingAlert, "이름과 연락처를 입력해주세요.");
      return;
    }
    try {
      const reservation = await fetchJSON("/api/reservations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          service_id: state.serviceId,
          date: state.date,
          time: state.time,
          name,
          phone,
        }),
      });
      const svc = serviceById(reservation.service_id);
      el.completeSummary.textContent =
        `${reservation.slot_date} ${reservation.slot_time} · ${svc ? svc.name : reservation.service_name} · ${reservation.customer_name}님`;
      el.screenBooking.hidden = true;
      el.screenComplete.hidden = false;
    } catch (err) {
      showAlert(el.bookingAlert, err.message);
    }
  }

  function resetBookingFlow() {
    state.serviceId = null;
    state.time = null;
    el.nameInput.value = "";
    el.phoneInput.value = "";
    el.screenComplete.hidden = true;
    el.screenBooking.hidden = false;
    renderServices();
    renderContactStep();
    loadInitialData();
  }

  async function submitWaitlist(evt) {
    evt.preventDefault();
    hideAlert(el.waitlistAlert);
    el.waitlistSuccess.hidden = true;
    const name = el.waitlistName.value.trim();
    const phone = el.waitlistPhone.value.trim();
    const date = el.waitlistDateSelect.value;
    if (!name || !phone || !date) {
      showAlert(el.waitlistAlert, "날짜, 이름, 연락처를 모두 입력해주세요.");
      return;
    }
    try {
      await fetchJSON("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date, name, phone }),
      });
      el.waitlistForm.reset();
      showAlert(el.waitlistSuccess, "대기명단에 등록되었습니다. 빈 자리가 생기면 알려드릴게요!");
      el.waitlistSuccess.hidden = false;
    } catch (err) {
      showAlert(el.waitlistAlert, err.message);
    }
  }

  // ── Wire up ────────────────────────────────────────────────────────────

  el.bookingForm.addEventListener("submit", submitBooking);
  el.btnBookAnother.addEventListener("click", resetBookingFlow);
  el.btnToggleWaitlist.addEventListener("click", () => {
    el.waitlistPanel.hidden = !el.waitlistPanel.hidden;
  });
  el.waitlistForm.addEventListener("submit", submitWaitlist);

  loadInitialData().catch((err) => {
    showAlert(el.bookingAlert, err.message || "초기 데이터를 불러오지 못했습니다.");
  });
})();
