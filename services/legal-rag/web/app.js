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
  cases: [],           // CaseOut[] — 사건 목록 캐시
  lastQuery: "",       // 직전 검색어 (검색창 유지용)
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

const casesLoading  = $("cases-loading");
const casesError    = $("cases-error");
const casesTable    = $("cases-table");
const casesTbody    = $("cases-tbody");
const casesEmpty    = $("cases-empty");

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

// ── 로그아웃 ─────────────────────────────────────────────────────────────────

btnLogout.addEventListener("click", () => {
  STATE.token = null;
  STATE.displayName = null;
  STATE.attorneyId = null;
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
  li.className = "citation-card";

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
  highlightText(excerpt, cit.chunk_text_excerpt, queryTerms);
  li.appendChild(excerpt);

  // ── 푸터 (관련도·청크·IT 상세·원문보기) ───────────────────────────────────
  const footer = document.createElement("div");
  footer.className = "citation-card__footer";

  const score = document.createElement("span");
  score.className = "relevance-score";
  score.textContent = `관련도 ${cit.rrf_score.toFixed(2)}`;
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

  // 원문 보기 링크 — 백엔드가 원문 서빙 엔드포인트를 제공하지 않으므로
  // aria-disabled 처리 (ui-spec §9 #2)
  const link = document.createElement("span");
  link.className = "citation-card__link";
  link.setAttribute("role", "button");
  link.setAttribute("aria-disabled", "true");
  link.textContent = "원문 보기 →";
  footer.appendChild(link);

  li.appendChild(footer);
  return li;
}

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

  setResultsState("loading");
  resultsHeader.hidden = true;

  try {
    const body = { query, top_k: topK };
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

    // 검색어를 공백으로 분리해 강조에 사용
    const queryTerms = query.split(/\s+/).filter(Boolean);

    resultsList.innerHTML = "";
    results.forEach((cit) => {
      const card = buildCitationCard(cit, queryTerms);
      resultsList.appendChild(card);
    });

    resultsHeader.hidden = false;
    resultsHeader.textContent = "";
    const countText = document.createTextNode(`검색 결과 ${results.length}건`);
    resultsHeader.appendChild(countText);
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

    // 사건번호
    const tdNum = document.createElement("td");
    tdNum.className = "case-number";
    tdNum.textContent = c.case_number;
    tr.appendChild(tdNum);

    // 사건명
    const tdTitle = document.createElement("td");
    tdTitle.className = "case-title";
    tdTitle.textContent = c.title;
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
      // case filter 드롭다운에서 해당 사건 선택
      for (const opt of searchCaseFilter.options) {
        if (opt.value === c.case_id) {
          opt.selected = true;
          break;
        }
      }
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
