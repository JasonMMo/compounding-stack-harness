/**
 * app.js — 법무법인 legal-rag 검색 도구 SPA
 *
 * 설계 원칙:
 *  - CDN/외부 의존 없음. vanilla fetch + DOM API만 사용.
 *  - innerHTML 직접조립 금지. 모든 동적 텍스트는 textContent 또는 safe DOM API.
 *  - 검색어 강조(mark): textContent로 텍스트 삽입 후 안전하게 mark 노드 삽입.
 *  - JWT는 메모리(sessionStorage)에 보관. 브라우저 탭 닫으면 자동 소멸.
 *    사내망 self-host 환경이므로 sessionStorage 수준 허용.
 *  - 생성형 답변 영역 없음 — 검색+인용 도구임을 화면에서 정직하게 표현.
 */

"use strict";

// ── 상태 ─────────────────────────────────────────────────────────────────────

const STATE = {
  token: null,         // JWT 문자열 (메모리)
  displayName: null,   // 로그인한 변호사 이름
  attorneyId: null,    // UUID
  role: null,          // attorney role ('partner' | 'associate' | null)
  cases: [],           // CaseOut[] — 사건 목록 캐시
  lastQuery: "",       // 직전 검색어 (검색창 유지용)
  matchMode: "or",     // 'or' | 'and' — 검색 매치 방식 (기본: 하나라도)
};

// ── DOM 참조 ─────────────────────────────────────────────────────────────────

const $ = (id) => document.getElementById(id);

const screens = {
  login: $("screen-login"),
  app:   $("screen-app"),
};

const loginAlert   = $("login-alert");
const loginForm    = $("login-form");
const loginEmail   = $("login-email");
const loginPassword = $("login-password");
const loginBtn     = $("login-btn");

const headerUsername  = $("header-username");
const btnLogout       = $("btn-logout");

const tabSearch    = $("tab-search");
const tabCases     = $("tab-cases");
const panelSearch  = $("panel-search");
const panelCases   = $("panel-cases");

const healthBanner  = $("health-banner");
const searchInput   = $("search-input");
const searchTopK    = $("search-top-k");
const searchCaseFilter = $("search-case-filter");
const btnSearch     = $("btn-search");
const resultsSection = $("results-section");
const resultsHeader  = $("results-header");
const resultsMessage = $("results-message");
const resultsList    = $("results-list");

// ── 매치모드 토글 DOM 참조 ───────────────────────────────────────────────────
const matchModeAndBtn = $("match-mode-and");
const matchModeOrBtn  = $("match-mode-or");

const casesLoading  = $("cases-loading");
const casesError    = $("cases-error");
const casesTable    = $("cases-table");
const casesTbody    = $("cases-tbody");
const casesEmpty    = $("cases-empty");
const casesPartnerCaption = $("cases-partner-caption");

// ── 사건 상세 패널 DOM 참조 (S-16) ──────────────────────────────────────────
const caseDetailPanel     = $("case-detail-panel");
const caseDetailBackdrop  = $("case-detail-backdrop");
const caseDetailClose     = $("case-detail-close");
const caseDetailTitle     = $("case-detail-title");
const caseDetailNumber    = $("case-detail-number");
const caseDetailMeta      = $("case-detail-meta");
const caseDetailStatus    = $("case-detail-status");
const caseDetailDocList   = $("case-detail-doc-list");
const caseDetailSearchBtn = $("case-detail-search-btn");

// ── 원문 슬라이드오버 드로어 DOM 참조 ────────────────────────────────────────
const docDrawer         = $("doc-drawer");
const docDrawerBackdrop = $("doc-drawer-backdrop");
const docDrawerClose    = $("doc-drawer-close");
const docDrawerTitle    = $("doc-drawer-title");
const docDrawerCitation = $("doc-drawer-citation");
const docDrawerMeta     = $("doc-drawer-meta");
const docDrawerBody     = $("doc-drawer-body");
const docDrawerStatus   = $("doc-drawer-status");

// ── 화면 전환 ────────────────────────────────────────────────────────────────

function showScreen(name) {
  Object.entries(screens).forEach(([key, el]) => {
    el.hidden = key !== name;
  });
}

// ── 탭 전환 ──────────────────────────────────────────────────────────────────

function switchTab(tabName) {
  const isSearch = tabName === "search";
  tabSearch.classList.toggle("tab-btn--active", isSearch);
  tabSearch.setAttribute("aria-selected", isSearch ? "true" : "false");
  panelSearch.hidden = !isSearch;

  tabCases.classList.toggle("tab-btn--active", !isSearch);
  tabCases.setAttribute("aria-selected", !isSearch ? "true" : "false");
  panelCases.hidden = isSearch;

  if (!isSearch) {
    loadCases();
  }
}

tabSearch.addEventListener("click", () => switchTab("search"));
tabCases.addEventListener("click",  () => switchTab("cases"));

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
      // G-6: rate-limit 전용 메시지 (D2 §6)
      showLoginAlert("요청이 너무 많습니다. 잠시 후 다시 시도하세요.");
      return;
    }

    if (res.status === 401) {
      const data = await res.json();
      showLoginAlert(data.detail || "이메일 또는 비밀번호가 올바르지 않습니다.");
      return;
    }

    if (!res.ok) {
      showLoginAlert("서버에 연결할 수 없습니다. IT 담당자에게 문의하세요.");
      return;
    }

    const data = await res.json();
    STATE.token = data.access_token;
    STATE.displayName = data.display_name;
    STATE.attorneyId = data.attorney_id;

    // JWT payload 클라이언트 디코드 — role 클레임 추출 (검증 없이 표시 전용)
    try {
      const payloadB64 = data.access_token.split(".")[1];
      const payload = JSON.parse(atob(payloadB64));
      STATE.role = payload.role || null;
    } catch {
      STATE.role = null;
    }

    headerUsername.textContent = STATE.displayName;
    loginPassword.value = "";   // 비밀번호 필드 클리어
    showScreen("app");
    switchTab("search");
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

// ── 원문 슬라이드오버 드로어 ─────────────────────────────────────────────────

let _drawerTrigger = null; // 드로어를 연 버튼 (닫을 때 포커스 복귀용)

/** 드로어 열기: 로딩 상태 먼저 표시 후 API 호출 */
async function openDocDrawer(sourceType, sourceId, triggerEl) {
  _drawerTrigger = triggerEl || null;

  // 로딩 상태로 초기화
  _drawerSetLoading();
  _drawerOpen();

  try {
    const res = await fetch(`/documents/${encodeURIComponent(sourceType)}/${encodeURIComponent(sourceId)}`, {
      headers: { "Authorization": `Bearer ${STATE.token}` },
    });

    if (res.status === 404) {
      _drawerSetError("권한이 없거나 원문을 찾을 수 없습니다.");
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
  // hidden 제거 후 다음 frame 에 class 추가해야 transition 동작
  requestAnimationFrame(() => {
    docDrawer.classList.add("is-open");
    docDrawerBackdrop.classList.add("is-open");
    docDrawerBackdrop.removeAttribute("aria-hidden");
  });
  document.body.style.overflow = "hidden";
  // 포커스 트랩: 드로어 닫기 버튼으로 이동
  requestAnimationFrame(() => docDrawerClose.focus());
  document.addEventListener("keydown", _drawerKeyHandler);
}

function closeDocDrawer() {
  docDrawer.classList.remove("is-open");
  docDrawerBackdrop.classList.remove("is-open");
  docDrawerBackdrop.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  document.removeEventListener("keydown", _drawerKeyHandler);

  // transition 완료 후 hidden 처리 (transition: 150ms)
  const TRANSITION_MS = 160;
  setTimeout(() => {
    docDrawer.hidden = true;
  }, TRANSITION_MS);

  // 포커스 복귀
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
  docDrawerTitle.textContent = "원문 불러오는 중...";
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
  docDrawerTitle.textContent = "원문 보기";
  docDrawerCitation.hidden = true;
  docDrawerMeta.hidden = true;
  docDrawerBody.innerHTML = "";
  const status = document.createElement("div");
  status.className = "doc-drawer__status doc-drawer__status--error";
  status.textContent = msg;
  docDrawerBody.appendChild(status);
}

function _drawerRender(doc) {
  // 헤더
  if (doc.source_type === "precedent") {
    docDrawerTitle.textContent = doc.citation || doc.title || "판례";
    if (doc.citation && doc.citation !== doc.title) {
      docDrawerCitation.textContent = doc.citation;
      docDrawerCitation.hidden = false;
    } else {
      docDrawerCitation.hidden = true;
    }
  } else {
    docDrawerTitle.textContent = doc.title || "사건문서";
    docDrawerCitation.hidden = true;
  }

  // 메타
  docDrawerMeta.innerHTML = "";
  const metaItems = [];
  if (doc.source_type === "precedent") {
    if (doc.court)        metaItems.push(["법원",     doc.court]);
    if (doc.decided_date) metaItems.push(["선고일",   doc.decided_date]);
    if (doc.case_type)    metaItems.push(["사건유형", doc.case_type]);
    if (doc.keywords)     metaItems.push(["키워드",   doc.keywords]);
  } else {
    if (doc.document_type) metaItems.push(["문서유형", doc.document_type]);
    if (doc.filed_at)      metaItems.push(["접수일",   doc.filed_at]);
  }

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

  // 본문
  docDrawerBody.innerHTML = "";

  if (doc.body_is_holding_fallback) {
    const badge = document.createElement("div");
    badge.className = "doc-drawer__fallback-badge";
    badge.textContent = "전문 미등록 — 판시요지 표시";
    docDrawerBody.appendChild(badge);
  }

  const bodyText = document.createElement("div");
  bodyText.className = "doc-drawer__body-text";
  bodyText.textContent = doc.body || "(본문 없음)";
  docDrawerBody.appendChild(bodyText);
}

// 이벤트: 닫기 버튼, 백드롭 클릭
docDrawerClose.addEventListener("click", closeDocDrawer);
docDrawerBackdrop.addEventListener("click", closeDocDrawer);

// ── 로그아웃 ─────────────────────────────────────────────────────────────────

btnLogout.addEventListener("click", () => {
  // 사건 상세 패널이 열려 있으면 즉시 숨김
  if (caseDetailPanel.classList.contains("is-open")) {
    caseDetailPanel.classList.remove("is-open");
    caseDetailBackdrop.classList.remove("is-open");
    caseDetailBackdrop.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    document.removeEventListener("keydown", _caseDetailKeyHandler);
    caseDetailPanel.hidden = true;
    _caseDetailTrigger = null;
    _caseDetailCurrentId = null;
  }
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
  STATE.token = null;
  STATE.displayName = null;
  STATE.attorneyId = null;
  STATE.role = null;
  STATE.cases = [];
  STATE.lastQuery = "";
  searchInput.value = "";
  setResultsState("initial");
  clearSearchCaseFilter();
  showScreen("login");
  loginEmail.focus();
  stopHealthPoll();
});

// ── Health 폴링 (IT 담당자 — 사건현황 탭 진입 시 + 30초 주기) ───────────────

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
    } else if (data.embed_sidecar === "error") {
      showHealthBanner("warn", `서비스 저하 — 검색 엔진 응답 없음 (DB: ${data.db_pool})`);
    } else {
      showHealthBanner("warn", `서비스 저하 — DB: ${data.db_pool}, 임베딩: ${data.embed_sidecar}`);
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

// ── 검색 ─────────────────────────────────────────────────────────────────────

function setResultsState(state, message) {
  // state: "initial" | "loading" | "results" | "empty" | "error" | "sidecar-down"
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
    "initial":      "검색어를 입력하면 관련 문서를 출처와 함께 보여줍니다.",
    "loading":      "",   // skeleton cards 표시
    "empty":        "입력하신 내용과 일치하는 문서가 없습니다. 다른 표현으로 다시 검색해 보세요.",
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

  // 예시 칩 컨테이너: 초기(empty) 상태에서만 노출
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
 *
 * excerpt 에 실제로 보이는(하이라이트되는) 단어 기준 일치 수를 반환한다.
 * - 질의어를 공백으로 분해한 의미 단위 '단어'를 기준으로 함 (bigram 아님).
 * - 각 단어를 동일 sanitize(한글+ASCII 영숫자만)로 정규화 후 대소문자 무시 substring 검색.
 * - highlightText() 의 정규화와 동일 규칙을 사용해 카운트와 하이라이트가 항상 일치한다.
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
 * 예) "계약해지 손해배상" →
 *     ["계약해지", "계약", "약해", "해지", "손해배상", "손해", "해배", "배상"]
 *
 * 규칙:
 *  - 한글 음절(가-힣)과 ASCII 영숫자(\\w)만 남기고 sanitize.
 *  - 길이 1 토큰은 bigram 분해 대상에서 제외 (노이즈 방지).
 *  - 중복 제거 후 반환.
 *  - 정규식 이스케이프는 highlightText() 에서 수행 (이 함수는 raw string 반환).
 */
function expandQueryTermsForHighlight(query) {
  const rawTokens = query.split(/\s+/).filter(Boolean);
  const terms = new Set();

  rawTokens.forEach((tok) => {
    // sanitize: 한글 + ASCII 영숫자만 유지
    const clean = tok.replace(/[^\w가-힣]/g, "");
    if (!clean) return;

    terms.add(clean);

    // 2-gram 분해: 2글자 이상 토큰만
    if (clean.length >= 2) {
      for (let i = 0; i < clean.length - 1; i++) {
        terms.add(clean.slice(i, i + 2));
      }
    }
  });

  return Array.from(terms).filter(Boolean);
}

// excerpt 표시 정제: 인제스트 아티팩트(구분선/메타 대괄호) 제거 — 실고객 문서가 지저분해도 방어
function sanitizeExcerpt(text) {
  if (!text) return "";
  return text
    .split("\n")
    .filter(line => !/^\s*=+\s*$/.test(line))                                   // 순수 구분선 줄
    .filter(line => !/^\s*\[.*(가명 처리|RAG ingest|테스트용|이 문서는).*\]\s*$/.test(line)) // 메타 대괄호 줄
    .join("\n")
    .replace(/={3,}/g, " ")        // 줄 중간에 끼인 ==== 런 제거
    .replace(/[ \t]{2,}/g, " ")    // 다중 공백 축약
    .replace(/\n{2,}/g, "\n")      // 다중 개행 축약
    .trim();
}

// 검색어 강조: textContent 기반 안전 DOM 조작 (XSS 방지)
// terms를 이스케이프 없이 TextNode로 처리한 뒤 mark 노드 삽입
function highlightText(container, fullText, queryTerms) {
  if (!queryTerms || queryTerms.length === 0) {
    container.textContent = fullText;
    return;
  }

  // 정규식 이스케이프
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
    // RegExp.lastIndex 리셋 (split 후 test 재사용 시 필요)
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

function buildCitationCard(cit, queryTerms) {
  const li = document.createElement("li");
  const typeClass = cit.source_type === "precedent"
    ? "citation-card--precedent"
    : "citation-card--document";
  li.className = `citation-card ${typeClass}`;

  // ── 헤더 (뱃지 + 메타) ──────────────────────────────────────────────────
  const header = document.createElement("div");
  header.className = "citation-card__header";

  const badge = document.createElement("span");
  badge.className = cit.source_type === "precedent"
    ? "citation-badge citation-badge--precedent"
    : "citation-badge citation-badge--document";
  badge.textContent = cit.source_type === "precedent" ? "판례" : "사건문서";
  badge.setAttribute("aria-label", `출처 유형: ${cit.source_type === "precedent" ? "판례" : "사건문서"}`);
  header.appendChild(badge);

  // 키워드 일치(FTS 매치) 뱃지 — RRF 상위 노출 이유 설명
  if (cit.fts_rank != null) {
    const kw = document.createElement("span");
    kw.className = "citation-badge citation-badge--keyword";
    kw.textContent = "🔑 키워드 일치";
    kw.setAttribute("title", "검색 키워드가 본문에 직접 일치 — 의미 유사도 외 추가 가점으로 상위 노출");
    kw.setAttribute("aria-label", "검색 키워드 본문 일치");
    header.appendChild(kw);
  }

  // 단어 일치 배지 — excerpt 기준 (하이라이트와 동일 규범)
  // cleanExcerpt: sanitize 적용본 — 아티팩트 제거 후 카운트·하이라이트 정합성 유지
  const cleanExcerpt = sanitizeExcerpt(cit.chunk_text_excerpt);
  if (queryTerms && queryTerms.length > 0) {
    // buildCitationCard 는 expandQueryTermsForHighlight 결과(queryTerms)가 아닌
    // 원본 query 를 받지 않으므로, queryTerms 에서 원본 '단어'만 역추출한다:
    // expandQueryTermsForHighlight 가 항상 rawToken 자체를 terms 에 먼저 add 하므로,
    // 공백 split 으로 얻은 sanitized 토큰이 queryTerms 안에 포함되어 있다.
    // 단어 배지는 원본 query 를 직접 받지 않으므로, STATE.lastQuery 를 참조한다.
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

  const meta = document.createElement("div");
  meta.className = "citation-card__meta";

  // source_type별 메타 필드
  if (cit.source_type === "precedent") {
    const metaFields = [cit.court, cit.case_number, cit.decision_date].filter(Boolean);
    metaFields.forEach((field, i) => {
      if (i > 0) meta.appendChild(createMetaSep());
      meta.appendChild(createMetaItem(field));
    });
  } else {
    const metaFields = [cit.document_type, cit.document_title].filter(Boolean);
    metaFields.forEach((field, i) => {
      if (i > 0) meta.appendChild(createMetaSep());
      meta.appendChild(createMetaItem(field));
    });
  }

  header.appendChild(meta);
  li.appendChild(header);

  // ── 판시요지 (판례만, holding_summary가 있을 때만) ──────────────────────
  if (cit.source_type === "precedent" && cit.holding_summary) {
    const holding = document.createElement("div");
    holding.className = "citation-card__holding";
    holding.textContent = cit.holding_summary;
    li.appendChild(holding);
  }

  // ── 본문 발췌 (검색어 강조) ───────────────────────────────────────────────
  const excerpt = document.createElement("div");
  excerpt.className = "citation-card__excerpt";
  highlightText(excerpt, cleanExcerpt, queryTerms);
  li.appendChild(excerpt);

  // ── 푸터 (관련도·청크·IT 상세·원문보기) ───────────────────────────────────
  const footer = document.createElement("div");
  footer.className = "citation-card__footer";

  const score = document.createElement("span");
  score.className = "relevance-score";
  if (cit.relevance != null) {
    score.textContent = `관련도 ${Math.round(cit.relevance * 100)}%`;
  } else {
    score.textContent = `관련도 ${cit.rrf_score.toFixed(2)}`;
  }
  footer.appendChild(score);

  const chunkRef = document.createElement("span");
  chunkRef.className = "chunk-ref";
  chunkRef.textContent = `청크 #${cit.chunk_index}`;
  footer.appendChild(chunkRef);

  // IT 페르소나용 상세 (details/summary 네이티브 HTML)
  if (cit.fts_rank !== null || cit.ann_rank !== null) {
    const details = document.createElement("details");
    details.className = "details-toggle";
    const summary = document.createElement("summary");
    summary.textContent = "상세 ▾";
    details.appendChild(summary);
    const content = document.createElement("div");
    content.className = "details-content";
    const lines = [];
    lines.push(`chunk_id: ${cit.chunk_id}`);
    if (cit.fts_rank !== null) lines.push(`fts_rank: ${cit.fts_rank}`);
    if (cit.ann_rank !== null) lines.push(`ann_rank: ${cit.ann_rank}`);
    content.textContent = lines.join("\n");
    details.appendChild(content);
    footer.appendChild(details);
  }

  // 원문 보기 버튼 — GET /documents/{source_type}/{source_id} 호출
  const link = document.createElement("button");
  link.type = "button";
  link.className = "citation-card__link";
  link.textContent = "원문 보기 →";
  link.setAttribute("aria-label", `원문 보기: ${cit.source_type === "precedent" ? (cit.case_number || cit.citation || "판례") : (cit.document_title || "사건문서")}`);
  link.addEventListener("click", () => {
    openDocDrawer(cit.source_type, cit.source_id, link);
  });
  footer.appendChild(link);

  li.appendChild(footer);
  return li;
}

// ── 예시 질의 칩 (수정 C) ────────────────────────────────────────────────────

const EXAMPLE_QUERIES = [
  "소프트웨어 공급계약 해지 손해배상",
  "기간제 근로 부당해고",
  "주택임대차 보증금 반환",
  "저작권 침해 손해배상",
];

const exampleQueriesEl = $("example-queries");

// 칩 생성 (정적 마크업 대신 JS 생성 — 쿼리 목록을 한 곳에서 관리)
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
  const caseFilterValue = searchCaseFilter.value || null;
  // 검색 시점 모드를 고정 — 결과 표시 후 토글이 바뀌어도 이 결과의 모드 유지
  const usedMode = STATE.matchMode;

  setResultsState("loading");
  resultsHeader.hidden = true;

  try {
    const body = { query, top_k: topK };
    body.match_mode = STATE.matchMode;
    if (caseFilterValue) body.case_id = caseFilterValue;

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
      // 토큰 만료 — 로그아웃 처리
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

    // 검색어 강조 후보: 공백 토큰 + 2-gram (bigram 분해로 붙여쓰기 복합어 대응)
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

    // F-12: SearchResponse.note 시각화 — Lite 안내 (D3 S-05 results-header)
    if (data.note) {
      const noteSep = document.createElement("span");
      noteSep.setAttribute("aria-hidden", "true");
      noteSep.textContent = " · ";
      resultsHeader.appendChild(noteSep);
      const noteSpan = document.createElement("span");
      noteSpan.className = "results-header__note";
      noteSpan.textContent = "출처 인용만 제공 — 생성형 답변 없음";
      resultsHeader.appendChild(noteSpan);
    }

  } catch (err) {
    console.error("Search error", err);
    setResultsState("error");
  }
}

// ── 사건 상세 패널 (S-16) ────────────────────────────────────────────────────

let _caseDetailTrigger = null;  // 패널을 연 버튼 (닫을 때 포커스 복귀용)
let _caseDetailCurrentId = null; // 현재 표시 중인 case_id (검색 연동용)

function _caseDetailOpen() {
  caseDetailPanel.hidden = false;
  requestAnimationFrame(() => {
    caseDetailPanel.classList.add("is-open");
    caseDetailBackdrop.classList.add("is-open");
    caseDetailBackdrop.removeAttribute("aria-hidden");
  });
  document.body.style.overflow = "hidden";
  requestAnimationFrame(() => caseDetailClose.focus());
  document.addEventListener("keydown", _caseDetailKeyHandler);
}

function closeCaseDetailPanel() {
  caseDetailPanel.classList.remove("is-open");
  caseDetailBackdrop.classList.remove("is-open");
  caseDetailBackdrop.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  document.removeEventListener("keydown", _caseDetailKeyHandler);
  setTimeout(() => {
    caseDetailPanel.hidden = true;
  }, 160);
  if (_caseDetailTrigger) {
    _caseDetailTrigger.focus();
    _caseDetailTrigger = null;
  }
}

function _caseDetailKeyHandler(e) {
  if (e.key === "Escape") {
    e.preventDefault();
    closeCaseDetailPanel();
  }
}

function _caseDetailSetLoading(caseNumber) {
  caseDetailTitle.textContent = caseNumber || "사건 상세";
  caseDetailNumber.textContent = "";
  caseDetailMeta.innerHTML = "";
  caseDetailDocList.innerHTML = "";
  caseDetailStatus.textContent = "불러오는 중...";
  caseDetailStatus.hidden = false;
}

function _caseDetailSetError(msg) {
  caseDetailStatus.textContent = msg;
  caseDetailStatus.hidden = false;
}

function _caseDetailRender(data) {
  caseDetailTitle.textContent = data.title || "사건 상세";
  caseDetailNumber.textContent = data.case_number || "";
  caseDetailStatus.hidden = true;

  // 메타 항목
  caseDetailMeta.innerHTML = "";
  const metaFields = [
    ["사건번호", data.case_number],
    ["상태", data.status],
    ["사건유형", data.case_type],
    ["개시일", data.opened_at],
    ["종결일", data.closed_at],
  ].filter(([, v]) => v);

  metaFields.forEach(([label, value]) => {
    const span = document.createElement("span");
    span.className = "case-detail-panel__meta-item";
    const strong = document.createElement("strong");
    strong.textContent = label + ":";
    span.appendChild(strong);
    span.appendChild(document.createTextNode(" " + value));
    caseDetailMeta.appendChild(span);
  });

  // 문서 목록
  caseDetailDocList.innerHTML = "";
  const docs = data.documents || [];
  if (docs.length === 0) {
    const empty = document.createElement("li");
    empty.className = "case-detail-panel__doc-item case-detail-panel__doc-empty";
    empty.textContent = "등록된 문서가 없습니다.";
    caseDetailDocList.appendChild(empty);
  } else {
    docs.forEach((doc) => {
      const li = document.createElement("li");
      li.className = "case-detail-panel__doc-item";

      const typeSpan = document.createElement("span");
      typeSpan.className = "case-detail-panel__doc-type";
      typeSpan.textContent = doc.document_type || "문서";
      li.appendChild(typeSpan);

      const titleSpan = document.createElement("span");
      titleSpan.className = "case-detail-panel__doc-title";
      titleSpan.textContent = doc.title || "(제목 없음)";
      li.appendChild(titleSpan);

      // 원문 보기 버튼 — 기존 openDocDrawer 연결
      if (doc.doc_id) {
        const viewBtn = document.createElement("button");
        viewBtn.type = "button";
        viewBtn.className = "citation-card__link case-detail-panel__doc-view";
        viewBtn.textContent = "원문 →";
        viewBtn.setAttribute("aria-label", `원문 보기: ${doc.title || "문서"}`);
        viewBtn.addEventListener("click", () => {
          openDocDrawer("case_document", doc.doc_id, viewBtn);
        });
        li.appendChild(viewBtn);
      }

      caseDetailDocList.appendChild(li);
    });
  }
}

/** 사건 상세 패널 열기 — GET /cases/{case_id} 호출 */
async function openCaseDetailPanel(caseId, caseNumber, triggerEl) {
  _caseDetailTrigger = triggerEl || null;
  _caseDetailCurrentId = caseId;

  _caseDetailSetLoading(caseNumber);
  _caseDetailOpen();

  // "이 사건으로 검색" 버튼 — case_id 주입 후 검색 탭 이동
  caseDetailSearchBtn.onclick = () => {
    closeCaseDetailPanel();
    switchTab("search");
    searchCaseFilter.value = caseId;
    searchCaseFilter.dispatchEvent(new Event("change"));
    const caseLabel = caseNumber || caseId;
    setResultsState("initial");
    resultsMessage.textContent = `「${caseLabel}」 사건 내에서 검색합니다 — 검색어를 입력하세요.`;
    searchInput.value = "";
    searchInput.focus();
  };

  try {
    const res = await fetch(`/cases/${encodeURIComponent(caseId)}`, {
      headers: { "Authorization": `Bearer ${STATE.token}` },
    });

    if (res.status === 404) {
      _caseDetailSetError("권한이 없거나 사건을 찾을 수 없습니다.");
      return;
    }
    if (res.status === 401) {
      _caseDetailSetError("인증이 만료되었습니다. 다시 로그인하세요.");
      return;
    }
    if (!res.ok) {
      _caseDetailSetError("사건 정보를 불러오는 중 오류가 발생했습니다.");
      return;
    }

    const data = await res.json();
    _caseDetailRender(data);
  } catch (err) {
    console.error("CaseDetail fetch error", err);
    _caseDetailSetError("네트워크 오류로 사건 정보를 불러올 수 없습니다.");
  }
}

caseDetailClose.addEventListener("click", closeCaseDetailPanel);
caseDetailBackdrop.addEventListener("click", closeCaseDetailPanel);

// ── 사건현황 ─────────────────────────────────────────────────────────────────

function getIngestBadgeClass(caseRow) {
  if (caseRow.doc_failed > 0) return "ingest-badge--failed";
  if (caseRow.doc_pending > 0) return "ingest-badge--pending";
  if (caseRow.doc_indexed > 0) return "ingest-badge--indexed";
  if (caseRow.doc_total === 0) return "ingest-badge--unknown";
  return "ingest-badge--pending";
}

function getIngestBadgeText(caseRow) {
  if (caseRow.doc_failed > 0) return "색인 실패";
  if (caseRow.doc_pending > 0) return "대기 중";
  if (caseRow.doc_indexed > 0) return "색인 완료";
  return "상태 불명";
}

function getCaseRowModifier(caseRow) {
  if (caseRow.doc_failed > 0) return "case-row--error";
  if (caseRow.doc_pending > 0) return "case-row--pending";
  if (caseRow.doc_indexed > 0) return "case-row--indexed";
  return "";
}

function renderCasesTable(cases) {
  casesTbody.innerHTML = "";

  cases.forEach((c) => {
    const tr = document.createElement("tr");
    const modifier = getCaseRowModifier(c);
    tr.className = modifier ? `case-row ${modifier}` : "case-row";

    // 사건번호 — 클릭 시 S-16 사건 상세 패널
    const tdNum = document.createElement("td");
    tdNum.className = "case-number";
    const numBtn = document.createElement("button");
    numBtn.type = "button";
    numBtn.className = "case-number-link";
    numBtn.textContent = c.case_number;
    numBtn.setAttribute("aria-label", `${c.case_number} 상세 보기`);
    numBtn.addEventListener("click", () => openCaseDetailPanel(c.case_id, c.case_number, numBtn));
    tdNum.appendChild(numBtn);
    tr.appendChild(tdNum);

    // 사건명 — 클릭 시 S-16 사건 상세 패널
    const tdTitle = document.createElement("td");
    tdTitle.className = "case-title";
    const titleBtn = document.createElement("button");
    titleBtn.type = "button";
    titleBtn.className = "case-title-link";
    titleBtn.textContent = c.title;
    titleBtn.setAttribute("aria-label", `${c.title} 상세 보기`);
    titleBtn.addEventListener("click", () => openCaseDetailPanel(c.case_id, c.case_number, titleBtn));
    tdTitle.appendChild(titleBtn);
    tr.appendChild(tdTitle);

    // 색인 상태 뱃지
    const tdStatus = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = `ingest-status-badge ${getIngestBadgeClass(c)}`;
    badge.textContent = getIngestBadgeText(c);
    tdStatus.appendChild(badge);
    tr.appendChild(tdStatus);

    // 문서 수
    const tdDocs = document.createElement("td");
    tdDocs.className = "doc-count";
    tdDocs.textContent = `${c.doc_total}건`;
    tr.appendChild(tdDocs);

    // 검색 버튼
    const tdSearch = document.createElement("td");
    const searchBtn = document.createElement("button");
    searchBtn.type = "button";
    searchBtn.className = "btn btn--sm btn--outline";
    searchBtn.textContent = "검색";
    searchBtn.setAttribute("aria-label", `${c.case_number} 검색`);
    searchBtn.addEventListener("click", () => {
      // 해당 사건으로 필터 설정하고 검색 탭으로 이동
      switchTab("search");
      searchCaseFilter.value = c.case_id;
      searchCaseFilter.dispatchEvent(new Event("change"));
      const caseLabel = c.title || c.case_number;
      setResultsState("initial");
      resultsMessage.textContent = `「${caseLabel}」 사건 내에서 검색합니다 — 검색어를 입력하세요.`;
      searchInput.value = "";
      searchInput.focus();
    });
    tdSearch.appendChild(searchBtn);
    tr.appendChild(tdSearch);

    casesTbody.appendChild(tr);
  });
}

function populateSearchCaseFilter(cases) {
  // 기존 옵션 유지 (첫 번째 "모든 사건" 제외하고 지우기)
  while (searchCaseFilter.options.length > 1) {
    searchCaseFilter.remove(1);
  }
  cases.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c.case_id;
    opt.textContent = `${c.case_number} — ${c.title.substring(0, 20)}${c.title.length > 20 ? "…" : ""}`;
    searchCaseFilter.appendChild(opt);
  });
}

function clearSearchCaseFilter() {
  while (searchCaseFilter.options.length > 1) {
    searchCaseFilter.remove(1);
  }
}

async function loadCases() {
  if (!STATE.token) return;

  // 이미 캐시된 사건 목록이 있으면 재사용 (탭 전환 시 재요청 방지)
  if (STATE.cases.length > 0) {
    renderCasesTable(STATE.cases);
    casesTable.hidden = false;
    casesEmpty.hidden = true;
    casesLoading.hidden = true;
    casesError.hidden = true;
    return;
  }

  casesLoading.hidden = false;
  casesTable.hidden = true;
  casesEmpty.hidden = true;
  casesError.hidden = true;

  try {
    const res = await fetch("/cases", {
      headers: { "Authorization": `Bearer ${STATE.token}` },
    });

    if (res.status === 401) {
      casesLoading.hidden = true;
      casesError.hidden = false;
      casesError.textContent = "세션이 만료되었습니다. 다시 로그인하세요.";
      return;
    }

    if (!res.ok) {
      casesLoading.hidden = true;
      casesError.hidden = false;
      casesError.textContent = "사건 목록을 불러오지 못했습니다. 잠시 후 다시 시도하세요.";
      return;
    }

    const data = await res.json();
    const cases = data.cases || [];
    STATE.cases = cases;

    populateSearchCaseFilter(cases);

    casesLoading.hidden = true;

    if (cases.length === 0) {
      casesEmpty.hidden = false;
      return;
    }

    renderCasesTable(cases);
    casesTable.hidden = false;

    // CEO 파트너 캡션 (D3 S-10 UX-2)
    if (casesPartnerCaption) {
      casesPartnerCaption.hidden = STATE.role !== "partner";
    }

  } catch (err) {
    console.error("Cases fetch error", err);
    casesLoading.hidden = true;
    casesError.hidden = false;
    casesError.textContent = "사건 목록을 불러오지 못했습니다. 잠시 후 다시 시도하세요.";
  }
}

// ── 초기화 ───────────────────────────────────────────────────────────────────

// 비로그인 상태로 시작 — 로그인 화면 표시
showScreen("login");
loginEmail.focus();
