/**
 * app.js — 한방 급여기준 검색 SPA (hanbang-rag)
 *
 * 설계 원칙:
 *  - CDN/외부 의존 없음. vanilla fetch + DOM API만 사용.
 *  - innerHTML 직접조립 금지. 모든 동적 텍스트는 textContent 또는 safe DOM API.
 *  - 검색어 강조(mark): textContent로 텍스트 삽입 후 안전하게 mark 노드 삽입.
 *  - JWT는 메모리(sessionStorage 불사용)에 보관. 브라우저 탭 닫으면 자동 소멸.
 *    사내망 self-host 환경이므로 메모리 보관 수준 허용.
 *  - 생성형 답변 영역 없음 — 검색+인용 도구임을 화면에서 정직하게 표현.
 *  - 사건(case) 기능 없음 — 한방 고시 검색 단일 화면.
 */

"use strict";

// ── 상태 ─────────────────────────────────────────────────────────────────────

const STATE = {
  token: null,       // JWT 문자열 (메모리)
  userId: null,      // user_id (서버 응답값)
  role: null,        // role (서버 응답값)
  lastQuery: "",     // 직전 검색어 (검색창 유지용)
  matchMode: "or",   // 'or' | 'and' — 검색 매치 방식 (기본: 하나라도)
};

// ── DOM 참조 ─────────────────────────────────────────────────────────────────

const $ = (id) => document.getElementById(id);

const screens = {
  login: $("screen-login"),
  app:   $("screen-app"),
};

const loginAlert    = $("login-alert");
const loginForm     = $("login-form");
const loginEmail    = $("login-email");
const loginPassword = $("login-password");
const loginBtn      = $("login-btn");

const headerUsername = $("header-username");
const btnLogout      = $("btn-logout");

const healthBanner   = $("health-banner");
const searchInput    = $("search-input");
const searchTopK     = $("search-top-k");
const btnSearch      = $("btn-search");
const resultsSection = $("results-section");
const resultsHeader  = $("results-header");
const resultsMessage = $("results-message");
const resultsList    = $("results-list");

// ── 매치모드 토글 DOM 참조 ───────────────────────────────────────────────────
const matchModeAndBtn = $("match-mode-and");
const matchModeOrBtn  = $("match-mode-or");

// ── 원문 슬라이드오버 드로어 DOM 참조 ────────────────────────────────────────
const docDrawer         = $("doc-drawer");
const docDrawerBackdrop = $("doc-drawer-backdrop");
const docDrawerClose    = $("doc-drawer-close");
const docDrawerTitle    = $("doc-drawer-title");
const docDrawerCitation = $("doc-drawer-citation");
const docDrawerMeta     = $("doc-drawer-meta");
const docDrawerBody     = $("doc-drawer-body");

// ── 화면 전환 ────────────────────────────────────────────────────────────────

function showScreen(name) {
  Object.entries(screens).forEach(([key, el]) => {
    el.hidden = key !== name;
  });
}

// ── 매치모드 토글 ─────────────────────────────────────────────────────────────

function _setMatchMode(mode) {
  STATE.matchMode = mode;
  const isAnd = mode === "and";
  matchModeAndBtn.classList.toggle("match-mode-btn--active", isAnd);
  matchModeAndBtn.setAttribute("aria-pressed", isAnd ? "true" : "false");
  matchModeOrBtn.classList.toggle("match-mode-btn--active", !isAnd);
  matchModeOrBtn.setAttribute("aria-pressed", isAnd ? "false" : "true");
}

matchModeAndBtn.addEventListener("click", () => _setMatchMode("and"));
matchModeOrBtn.addEventListener("click",  () => _setMatchMode("or"));

// ── 로그인 ───────────────────────────────────────────────────────────────────

function showLoginAlert(msg) {
  loginAlert.textContent = msg;
  loginAlert.hidden = false;
}

function clearLoginAlert() {
  loginAlert.textContent = "";
  loginAlert.hidden = true;
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearLoginAlert();

  const email    = loginEmail.value.trim();
  const password = loginPassword.value;

  if (!email || !password) {
    showLoginAlert("이메일과 비밀번호를 모두 입력하세요.");
    return;
  }

  loginBtn.disabled = true;
  loginBtn.textContent = "로그인 중...";
  loginBtn.setAttribute("aria-busy", "true");

  try {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (res.status === 429) {
      showLoginAlert("요청이 너무 많습니다. 잠시 후 다시 시도하세요.");
      return;
    }

    if (res.status === 401) {
      const data = await res.json().catch(() => ({}));
      showLoginAlert(data.detail || "이메일 또는 비밀번호가 올바르지 않습니다.");
      return;
    }

    if (!res.ok) {
      showLoginAlert("서버에 연결할 수 없습니다. IT 담당자에게 문의하세요.");
      return;
    }

    const data = await res.json();
    // hanbang auth 응답: {token, user_id, role}
    STATE.token  = data.token;
    STATE.userId = data.user_id;
    STATE.role   = data.role || null;

    // 헤더 사용자 표시: 이메일 또는 role
    headerUsername.textContent = STATE.role ? `${email} (${STATE.role})` : email;
    loginPassword.value = "";
    showScreen("app");
    pollHealth();

  } catch (err) {
    console.error("Login fetch error", err);
    showLoginAlert("서버에 연결할 수 없습니다. IT 담당자에게 문의하세요.");
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = "로그인";
    loginBtn.removeAttribute("aria-busy");
  }
});

// ── 로그아웃 ─────────────────────────────────────────────────────────────────

btnLogout.addEventListener("click", () => {
  // 드로어가 열려 있으면 즉시 숨김 (transition 없이)
  if (docDrawer.classList.contains("is-open")) {
    docDrawer.classList.remove("is-open");
    docDrawerBackdrop.classList.remove("is-open");
    docDrawerBackdrop.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    document.removeEventListener("keydown", _drawerKeyHandler);
    docDrawer.hidden = true;
    _drawerTrigger = null;
  }
  STATE.token     = null;
  STATE.userId    = null;
  STATE.role      = null;
  STATE.lastQuery = "";
  searchInput.value = "";
  setResultsState("initial");
  showScreen("login");
  loginEmail.focus();
  stopHealthPoll();
});

// ── Health 폴링 (IT 담당자용 — 30초 주기) ─────────────────────────────────

let _healthPollTimer = null;

async function checkHealth() {
  try {
    const res = await fetch("/health");
    if (!res.ok) {
      showHealthBanner("down", "서비스 이상 감지 — IT 담당자에게 문의하세요.");
      return;
    }
    const data = await res.json();
    if (data.status === "ok") {
      healthBanner.hidden = true;
      healthBanner.className = "health-banner health-banner--ok";
    } else {
      showHealthBanner("warn", "서비스 저하 — IT 담당자에게 문의하세요.");
    }
  } catch {
    showHealthBanner("down", "서비스 상태를 확인할 수 없습니다. IT 담당자에게 문의하세요.");
  }
}

function showHealthBanner(severity, msg) {
  healthBanner.hidden = false;
  healthBanner.className = `health-banner health-banner--${severity}`;
  healthBanner.textContent = msg;
}

function pollHealth() {
  checkHealth();
  _healthPollTimer = setInterval(checkHealth, 30000);
}

function stopHealthPoll() {
  if (_healthPollTimer) {
    clearInterval(_healthPollTimer);
    _healthPollTimer = null;
  }
}

// ── 원문 슬라이드오버 드로어 ─────────────────────────────────────────────────

let _drawerTrigger = null; // 드로어를 연 버튼 (닫을 때 포커스 복귀용)

/** 드로어 열기: 로딩 상태 먼저 표시 후 API 호출 */
async function openDocDrawer(sourceType, sourceId, triggerEl) {
  _drawerTrigger = triggerEl || null;

  _drawerSetLoading();
  _drawerOpen();

  try {
    // hanbang: GET /documents/notice/{sourceId} (sourceType 항상 "notice")
    const res = await fetch(`/documents/notice/${encodeURIComponent(sourceId)}`, {
      headers: { "Authorization": `Bearer ${STATE.token}` },
    });

    if (res.status === 404) {
      _drawerSetError("원문을 찾을 수 없습니다.");
      return;
    }

    if (res.status === 401) {
      _drawerSetError("인증이 만료되었습니다. 다시 로그인하세요.");
      return;
    }

    if (!res.ok) {
      _drawerSetError("원문을 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.");
      return;
    }

    const doc = await res.json();
    _drawerRender(doc);

  } catch (err) {
    console.error("DocDrawer fetch error", err);
    _drawerSetError("네트워크 오류로 원문을 불러올 수 없습니다.");
  }
}

function _drawerOpen() {
  docDrawer.hidden = false;
  requestAnimationFrame(() => {
    docDrawer.classList.add("is-open");
    docDrawerBackdrop.classList.add("is-open");
    docDrawerBackdrop.removeAttribute("aria-hidden");
  });
  document.body.style.overflow = "hidden";
  requestAnimationFrame(() => docDrawerClose.focus());
  document.addEventListener("keydown", _drawerKeyHandler);
}

function closeDocDrawer() {
  docDrawer.classList.remove("is-open");
  docDrawerBackdrop.classList.remove("is-open");
  docDrawerBackdrop.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  document.removeEventListener("keydown", _drawerKeyHandler);

  const TRANSITION_MS = 160;
  setTimeout(() => {
    docDrawer.hidden = true;
  }, TRANSITION_MS);

  if (_drawerTrigger) {
    _drawerTrigger.focus();
    _drawerTrigger = null;
  }
}

function _drawerKeyHandler(e) {
  if (e.key === "Escape") {
    e.preventDefault();
    closeDocDrawer();
    return;
  }
  // 포커스 트랩: Tab/Shift+Tab 을 드로어 내부로 한정
  if (e.key === "Tab") {
    const focusable = Array.from(
      docDrawer.querySelectorAll(
        'button:not([disabled]), [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    ).filter((el) => !el.closest("[hidden]"));
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }
}

function _drawerSetLoading() {
  docDrawerTitle.textContent = "고시 원문 불러오는 중...";
  docDrawerCitation.hidden = true;
  docDrawerMeta.hidden = true;
  docDrawerMeta.innerHTML = "";
  docDrawerBody.innerHTML = "";
  const status = document.createElement("div");
  status.className = "doc-drawer__status";
  status.textContent = "불러오는 중...";
  docDrawerBody.appendChild(status);
}

function _drawerSetError(msg) {
  docDrawerTitle.textContent = "고시 원문 보기";
  docDrawerCitation.hidden = true;
  docDrawerMeta.hidden = true;
  docDrawerBody.innerHTML = "";
  const status = document.createElement("div");
  status.className = "doc-drawer__status doc-drawer__status--error";
  status.textContent = msg;
  docDrawerBody.appendChild(status);
}

function _drawerRender(doc) {
  // 헤더: notice_number 를 타이틀로
  docDrawerTitle.textContent = doc.notice_number || "고시 원문 보기";
  docDrawerCitation.hidden = true;

  // 메타: ministry + issued_date
  docDrawerMeta.innerHTML = "";
  const metaItems = [];
  if (doc.ministry)     metaItems.push(["소관부처",  doc.ministry]);
  if (doc.issued_date)  metaItems.push(["발령일",    doc.issued_date]);
  if (doc.summary)      metaItems.push(["요약",      doc.summary]);

  if (metaItems.length > 0) {
    metaItems.forEach(([label, value]) => {
      const span = document.createElement("span");
      span.className = "doc-drawer__meta-item";
      const strong = document.createElement("strong");
      strong.textContent = label + ":";
      span.appendChild(strong);
      span.appendChild(document.createTextNode(" " + value));
      docDrawerMeta.appendChild(span);
    });
    docDrawerMeta.hidden = false;
  } else {
    docDrawerMeta.hidden = true;
  }

  // 본문: full_text
  docDrawerBody.innerHTML = "";
  const bodyText = document.createElement("div");
  bodyText.className = "doc-drawer__body-text";
  bodyText.textContent = doc.full_text || "(본문 없음)";
  docDrawerBody.appendChild(bodyText);
}

// 이벤트: 닫기 버튼, 백드롭 클릭
docDrawerClose.addEventListener("click", closeDocDrawer);
docDrawerBackdrop.addEventListener("click", closeDocDrawer);

// ── 검색 ─────────────────────────────────────────────────────────────────────

function setResultsState(state, message) {
  const modifier = {
    "initial":      "results--empty-initial",
    "loading":      "results--loading",
    "results":      "results--has-results",
    "empty":        "results--empty",
    "error":        "results--error",
    "sidecar-down": "results--sidecar-down",
  }[state] || "results--empty-initial";

  resultsSection.className = `results-section ${modifier}`;

  const messages = {
    "initial":      "검색어를 입력하면 관련 고시를 출처와 함께 보여줍니다.",
    "loading":      "",
    "empty":        "입력하신 내용과 일치하는 고시가 없습니다. 다른 표현으로 다시 검색해 보세요.",
    "error":        "검색 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.",
    "sidecar-down": "검색 서비스가 일시적으로 이용 불가합니다. IT 담당자에게 문의하세요.",
  };

  if (state === "loading") {
    resultsMessage.hidden = true;
    resultsMessage.textContent = "";
    renderSkeletons();
    resultsSection.setAttribute("aria-busy", "true");
  } else {
    resultsSection.removeAttribute("aria-busy");
    resultsMessage.hidden = false;
    if (messages[state] !== undefined) {
      resultsMessage.textContent = messages[state] || (message || "");
    } else {
      resultsMessage.textContent = message || "";
    }
    resultsList.innerHTML = "";
  }

  if (state === "results") {
    resultsMessage.hidden = true;
  }

  if (exampleQueriesEl) {
    exampleQueriesEl.hidden = state !== "initial";
  }
}

function renderSkeletons() {
  resultsList.innerHTML = "";
  for (let i = 0; i < 3; i++) {
    const li = document.createElement("li");
    li.className = "skeleton-card";
    li.setAttribute("aria-hidden", "true");
    resultsList.appendChild(li);
  }
}

/**
 * countMatchedWords(excerptText, query) → { matched: number, total: number }
 */
function countMatchedWords(excerptText, query) {
  if (!excerptText || !query) return { matched: 0, total: 0 };
  const rawTokens = query.trim().split(/\s+/).filter(Boolean);
  const words = rawTokens
    .map((t) => t.replace(/[^\w가-힣]/g, ""))
    .filter(Boolean);
  if (words.length === 0) return { matched: 0, total: 0 };

  const lowerExcerpt = excerptText.toLowerCase();
  let matched = 0;
  words.forEach((w) => {
    if (lowerExcerpt.includes(w.toLowerCase())) matched++;
  });
  return { matched, total: words.length };
}

/**
 * expandQueryTermsForHighlight(query) → string[]
 *
 * 공백 토큰 + 다문자 토큰의 2-gram을 합쳐 강조 후보 집합을 반환한다.
 */
function expandQueryTermsForHighlight(query) {
  const rawTokens = query.split(/\s+/).filter(Boolean);
  const terms = new Set();

  rawTokens.forEach((tok) => {
    const clean = tok.replace(/[^\w가-힣]/g, "");
    if (!clean) return;

    terms.add(clean);

    if (clean.length >= 2) {
      for (let i = 0; i < clean.length - 1; i++) {
        terms.add(clean.slice(i, i + 2));
      }
    }
  });

  return Array.from(terms).filter(Boolean);
}

// excerpt 표시 정제: 인제스트 아티팩트 제거
function sanitizeExcerpt(text) {
  if (!text) return "";
  return text
    .split("\n")
    .filter(line => !/^\s*=+\s*$/.test(line))
    .filter(line => !/^\s*\[.*(RAG ingest|테스트용|이 문서는).*\]\s*$/.test(line))
    .join("\n")
    .replace(/={3,}/g, " ")
    .replace(/[ \t]{2,}/g, " ")
    .replace(/\n{2,}/g, "\n")
    .trim();
}

// 검색어 강조: textContent 기반 안전 DOM 조작 (XSS 방지)
function highlightText(container, fullText, queryTerms) {
  if (!queryTerms || queryTerms.length === 0) {
    container.textContent = fullText;
    return;
  }

  const escaped = queryTerms
    .filter(Boolean)
    .map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));

  if (escaped.length === 0) {
    container.textContent = fullText;
    return;
  }

  const pattern = new RegExp(`(${escaped.join("|")})`, "gi");
  const parts = fullText.split(pattern);

  parts.forEach((part) => {
    if (pattern.test(part)) {
      const mark = document.createElement("mark");
      mark.className = "search-highlight";
      mark.textContent = part;
      container.appendChild(mark);
    } else {
      container.appendChild(document.createTextNode(part));
    }
    pattern.lastIndex = 0;
  });
}

function createMetaItem(text) {
  const span = document.createElement("span");
  span.className = "meta-item";
  span.textContent = text;
  return span;
}

function createMetaSep() {
  const span = document.createElement("span");
  span.className = "meta-sep";
  span.setAttribute("aria-hidden", "true");
  span.textContent = "·";
  return span;
}

/**
 * buildCitationCard(cit, queryTerms) → <li>
 *
 * 고시 인용 카드 생성.
 * result 필드: chunk_id, source_id, chunk_index, chunk_text_excerpt,
 *              rrf_score, notice_number, ministry, issued_date, summary
 */
function buildCitationCard(cit, queryTerms) {
  const li = document.createElement("li");
  li.className = "citation-card citation-card--document";

  // ── 헤더 (뱃지 + 메타) ──────────────────────────────────────────────────
  const header = document.createElement("div");
  header.className = "citation-card__header";

  // 뱃지: 고시 유형
  const badge = document.createElement("span");
  badge.className = "citation-badge citation-badge--document";
  badge.textContent = "고시";
  badge.setAttribute("aria-label", "출처 유형: 정부 고시");
  header.appendChild(badge);

  // 단어 일치 배지
  const cleanExcerpt = sanitizeExcerpt(cit.chunk_text_excerpt);
  if (queryTerms && queryTerms.length > 0) {
    const wordMatch = countMatchedWords(cleanExcerpt, STATE.lastQuery);
    if (wordMatch.total >= 2 && wordMatch.matched > 0) {
      const mBadge = document.createElement("span");
      const isFull = wordMatch.matched === wordMatch.total;
      mBadge.className = `match-count-badge${isFull ? " match-count-badge--full" : " match-count-badge--partial"}`;
      mBadge.textContent = `단어 ${wordMatch.matched}/${wordMatch.total} 일치`;
      mBadge.setAttribute("aria-label", `질의어 ${wordMatch.total}개 중 ${wordMatch.matched}개 미리보기에서 일치`);
      header.appendChild(mBadge);
    }
  }

  // 메타: notice_number, ministry, issued_date
  const meta = document.createElement("div");
  meta.className = "citation-card__meta";

  const metaFields = [cit.notice_number, cit.ministry, cit.issued_date].filter(Boolean);
  metaFields.forEach((field, i) => {
    if (i > 0) meta.appendChild(createMetaSep());
    meta.appendChild(createMetaItem(field));
  });

  header.appendChild(meta);
  li.appendChild(header);

  // ── 카드 제목: notice_number ──────────────────────────────────────────────
  if (cit.notice_number) {
    const holding = document.createElement("div");
    holding.className = "citation-card__holding";
    holding.textContent = cit.notice_number;
    li.appendChild(holding);
  }

  // ── 본문 발췌 (검색어 강조) ───────────────────────────────────────────────
  const excerpt = document.createElement("div");
  excerpt.className = "citation-card__excerpt";
  highlightText(excerpt, cleanExcerpt, queryTerms);
  li.appendChild(excerpt);

  // ── 푸터 (관련도·청크·원문보기) ─────────────────────────────────────────
  const footer = document.createElement("div");
  footer.className = "citation-card__footer";

  const score = document.createElement("span");
  score.className = "relevance-score";
  if (cit.rrf_score != null) {
    score.textContent = `관련도 ${cit.rrf_score.toFixed(4)}`;
  }
  footer.appendChild(score);

  const chunkRef = document.createElement("span");
  chunkRef.className = "chunk-ref";
  chunkRef.textContent = `청크 #${cit.chunk_index}`;
  footer.appendChild(chunkRef);

  // 고시 원문 보기 버튼
  const link = document.createElement("button");
  link.type = "button";
  link.className = "citation-card__link";
  link.textContent = "고시 원문 보기 →";
  link.setAttribute("aria-label", `원문 보기: ${cit.notice_number || "고시"}`);
  link.addEventListener("click", () => {
    openDocDrawer("notice", cit.source_id, link);
  });
  footer.appendChild(link);

  li.appendChild(footer);
  return li;
}

// ── 예시 질의 칩 ─────────────────────────────────────────────────────────────

const EXAMPLE_QUERIES = [
  "추나요법 급여",
  "비급여 진료비용 보고",
  "의료급여 본인부담",
  "상대가치점수",
  "보건의료기술 분류",
];

const exampleQueriesEl = $("example-queries");

EXAMPLE_QUERIES.forEach((q) => {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "example-chip";
  btn.textContent = q;
  btn.addEventListener("click", () => {
    searchInput.value = q;
    doSearch();
  });
  exampleQueriesEl.appendChild(btn);
});

btnSearch.addEventListener("click", doSearch);
searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    doSearch();
  }
});

async function doSearch() {
  const query = searchInput.value.trim();
  if (!query) return;

  STATE.lastQuery = query;
  const topK = parseInt(searchTopK.value, 10);
  // 검색 시점 모드를 고정
  const usedMode = STATE.matchMode;

  setResultsState("loading");
  resultsHeader.hidden = true;

  try {
    // hanbang: case_id 절대 보내지 않음
    const body = {
      query,
      top_k: topK,
      match_mode: STATE.matchMode,
    };

    const res = await fetch("/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${STATE.token}`,
      },
      body: JSON.stringify(body),
    });

    if (res.status === 503) {
      setResultsState("sidecar-down");
      return;
    }

    if (res.status === 401) {
      setResultsState("error");
      setTimeout(() => {
        alert("세션이 만료되었습니다. 다시 로그인하세요.");
        btnLogout.click();
      }, 500);
      return;
    }

    if (!res.ok) {
      setResultsState("error");
      return;
    }

    const data = await res.json();
    const results = data.results || [];

    if (results.length === 0) {
      setResultsState("empty");
      return;
    }

    setResultsState("results");

    const queryTerms = expandQueryTermsForHighlight(query);

    resultsList.innerHTML = "";
    results.forEach((cit) => {
      const card = buildCitationCard(cit, queryTerms);
      resultsList.appendChild(card);
    });

    resultsHeader.hidden = false;
    resultsHeader.textContent = "";

    const countText = document.createTextNode(`검색 결과 ${results.length}건`);
    resultsHeader.appendChild(countText);

    const modeSep = document.createElement("span");
    modeSep.setAttribute("aria-hidden", "true");
    modeSep.textContent = " · ";
    resultsHeader.appendChild(modeSep);

    const modeLabel = document.createElement("span");
    modeLabel.className = "results-mode-label";
    modeLabel.textContent = usedMode === "and" ? "모두 포함" : "하나라도";
    modeLabel.setAttribute("aria-label", `검색 모드: ${usedMode === "and" ? "모두 포함(AND)" : "하나라도(OR)"}`);
    resultsHeader.appendChild(modeLabel);

    const sep = document.createElement("span");
    sep.setAttribute("aria-hidden", "true");
    sep.textContent = " · ";
    resultsHeader.appendChild(sep);

    const queryText = document.createElement("em");
    queryText.textContent = `"${query}"`;
    resultsHeader.appendChild(queryText);

  } catch (err) {
    console.error("Search error", err);
    setResultsState("error");
  }
}

// ── 초기화 ───────────────────────────────────────────────────────────────────

showScreen("login");
loginEmail.focus();
