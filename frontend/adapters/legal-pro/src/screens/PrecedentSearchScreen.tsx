/**
 * PrecedentSearchScreen.tsx — 판례 검색 화면 (Phase A 핵심 스크린).
 *
 * Ports services/legal-rag/web/app.js search behavior to React/TypeScript.
 *
 * Design contracts preserved exactly:
 *  - Calls POST /search with { query, top_k, match_mode, case_id? }
 *  - Renders CitationOut.relevance as "관련도 N%" (NOT raw rrf_score)
 *  - Citation cards: 1:1 chunk binding (chunk_id), zero-hallucination
 *  - Korean lexical match badges (fts_rank != null → "키워드 일치")
 *  - Word-match badge (단어 N/M 일치) — excerpt-based, same rule as app.js
 *  - Search highlight: textContent-safe mark insertion (XSS-safe)
 *  - Empty-query, no-results, error (incl. 503 sidecar-down), 429 states
 *  - AND/OR match mode toggle
 *  - Skeleton loading cards
 *
 * Phase B deferred: case filter select (requires /cases endpoint — blocked G-1~G-6).
 * The case_id param is wired but the select UI is left as a Phase B TODO.
 *
 * Does NOT re-implement search ranking, threshold, or RLS — backend concerns.
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { apiSearch, apiHealth, type CitationOut, type WireError } from '../api/wire'

// ── Types ──────────────────────────────────────────────────────────────────

type ResultsState = 'initial' | 'loading' | 'results' | 'empty' | 'error' | 'sidecar-down'
type MatchMode = 'or' | 'and'

// ── Text utilities (ported from app.js) ───────────────────────────────────

/**
 * expandQueryTermsForHighlight — public-token + 2-gram bigram set.
 * Mirrors app.js expandQueryTermsForHighlight() exactly.
 */
function expandQueryTermsForHighlight(query: string): string[] {
  const rawTokens = query.split(/\s+/).filter(Boolean)
  const terms = new Set<string>()

  for (const tok of rawTokens) {
    const clean = tok.replace(/[^\w가-힣]/g, '')
    if (!clean) continue
    terms.add(clean)
    if (clean.length >= 2) {
      for (let i = 0; i < clean.length - 1; i++) {
        terms.add(clean.slice(i, i + 2))
      }
    }
  }

  return Array.from(terms).filter(Boolean)
}

/**
 * countMatchedWords — excerpt-based word match count.
 * Mirrors app.js countMatchedWords() exactly.
 */
function countMatchedWords(excerptText: string, query: string): { matched: number; total: number } {
  if (!excerptText || !query) return { matched: 0, total: 0 }
  const rawTokens = query.trim().split(/\s+/).filter(Boolean)
  const words = rawTokens
    .map(t => t.replace(/[^\w가-힣]/g, ''))
    .filter(Boolean)
  if (words.length === 0) return { matched: 0, total: 0 }

  const lowerExcerpt = excerptText.toLowerCase()
  let matched = 0
  for (const w of words) {
    if (lowerExcerpt.includes(w.toLowerCase())) matched++
  }
  return { matched, total: words.length }
}

// ── Highlight component (XSS-safe mark insertion) ─────────────────────────

interface HighlightedTextProps {
  text: string
  queryTerms: string[]
}

function HighlightedText({ text, queryTerms }: HighlightedTextProps) {
  if (!queryTerms.length) {
    return <>{text}</>
  }

  const escaped = queryTerms
    .filter(Boolean)
    .map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))

  if (!escaped.length) return <>{text}</>

  const pattern = new RegExp(`(${escaped.join('|')})`, 'gi')
  const parts = text.split(pattern)

  return (
    <>
      {parts.map((part, i) =>
        pattern.test(part)
          ? <mark key={i} className="search-highlight">{part}</mark>
          : <span key={i}>{part}</span>
      )}
    </>
  )
}

// ── Skeleton loading cards ─────────────────────────────────────────────────

function SkeletonCards() {
  return (
    <ul className="results-list" aria-busy="true">
      {[0, 1, 2].map(i => (
        <li key={i} className="skeleton-card" aria-hidden="true" />
      ))}
    </ul>
  )
}

// ── Citation card ─────────────────────────────────────────────────────────

interface CitationCardProps {
  cit: CitationOut
  queryTerms: string[]
  lastQuery: string
}

function CitationCard({ cit, queryTerms, lastQuery }: CitationCardProps) {
  const isPrecedent = cit.source_type === 'precedent'
  const typeClass = isPrecedent ? 'citation-card--precedent' : 'citation-card--document'

  const wordMatch = countMatchedWords(cit.chunk_text_excerpt, lastQuery)

  // Relevance display — prefer CitationOut.relevance (backend-computed %)
  const relevanceText =
    cit.relevance != null
      ? `관련도 ${Math.round(cit.relevance * 100)}%`
      : `관련도 ${cit.rrf_score.toFixed(2)}`

  // Meta fields by source type
  const metaFields: string[] = isPrecedent
    ? [cit.court, cit.case_number, cit.decision_date].filter((v): v is string => Boolean(v))
    : [cit.document_type, cit.document_title].filter((v): v is string => Boolean(v))

  return (
    <li className={`citation-card ${typeClass}`}>
      {/* Header: badges + meta */}
      <div className="citation-card__header">
        <span
          className={`citation-badge ${isPrecedent ? 'citation-badge--precedent' : 'citation-badge--document'}`}
          aria-label={`출처 유형: ${isPrecedent ? '판례' : '사건문서'}`}
        >
          {isPrecedent ? '판례' : '사건문서'}
        </span>

        {/* 키워드 일치 뱃지 — fts_rank 있을 때만 (ported from app.js) */}
        {cit.fts_rank != null && (
          <span
            className="citation-badge citation-badge--keyword"
            title="검색 키워드가 본문에 직접 일치 — 의미 유사도 외 추가 가점으로 상위 노출"
            aria-label="검색 키워드 본문 일치"
          >
            키워드 일치
          </span>
        )}

        {/* 단어 일치 배지 — excerpt 기준, 2단어 이상일 때만 */}
        {wordMatch.total >= 2 && (
          <span
            className={`match-count-badge ${
              wordMatch.matched === wordMatch.total
                ? 'match-count-badge--full'
                : 'match-count-badge--partial'
            }`}
            aria-label={`질의어 ${wordMatch.total}개 중 ${wordMatch.matched}개 미리보기에서 일치`}
          >
            단어 {wordMatch.matched}/{wordMatch.total} 일치
          </span>
        )}

        {/* Meta row */}
        <div className="citation-card__meta">
          {metaFields.map((field, i) => (
            <span key={i}>
              {i > 0 && <span className="meta-sep" aria-hidden="true">·</span>}
              <span className="meta-item">{field}</span>
            </span>
          ))}
        </div>
      </div>

      {/* 판시요지 (판례만, holding_summary 있을 때) */}
      {isPrecedent && cit.holding_summary && (
        <div className="citation-card__holding">{cit.holding_summary}</div>
      )}

      {/* 본문 발췌 — 검색어 강조 */}
      <div className="citation-card__excerpt">
        <HighlightedText text={cit.chunk_text_excerpt} queryTerms={queryTerms} />
      </div>

      {/* 푸터: 관련도 · 청크 · IT 상세 */}
      <div className="citation-card__footer">
        <span className="relevance-score">{relevanceText}</span>
        <span className="chunk-ref">청크 #{cit.chunk_index}</span>

        {/* IT 페르소나용 상세 */}
        {(cit.fts_rank != null || cit.ann_rank != null) && (
          <details className="details-toggle">
            <summary>상세 ▾</summary>
            <div className="details-content">
              {[
                `chunk_id: ${cit.chunk_id}`,
                cit.fts_rank != null ? `fts_rank: ${cit.fts_rank}` : null,
                cit.ann_rank != null ? `ann_rank: ${cit.ann_rank}` : null,
              ]
                .filter(Boolean)
                .join('\n')}
            </div>
          </details>
        )}

        {/* 원문 보기 — Phase B TODO: implement slide-over drawer (openDocDrawer) */}
        <button
          type="button"
          className="citation-card__link"
          aria-label={`원문 보기: ${isPrecedent ? (cit.case_number ?? cit.citation ?? '판례') : (cit.document_title ?? '사건문서')}`}
          onClick={() => {
            /* Phase B TODO: open doc drawer with cit.source_type + cit.source_id */
            alert(`원문 보기 기능은 Phase B 예정입니다.\nsource_id: ${cit.source_id}`)
          }}
        >
          원문 보기 →
        </button>
      </div>
    </li>
  )
}

// ── Main screen ────────────────────────────────────────────────────────────

export default function PrecedentSearchScreen() {
  // OQ-3: ?case_id= query-param → 사건 필터 드롭다운 초기값 (Phase B 최소 연결)
  const [searchParams] = useSearchParams()
  const initialCaseId = searchParams.get('case_id') ?? ''

  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [matchMode, setMatchMode] = useState<MatchMode>('or')
  // case_id 필터 — Phase B: URL query-param 으로 초기값 주입, 드롭다운 UI는 후속 패스
  const [selectedCaseId] = useState<string>(initialCaseId)
  const [resultsState, setResultsState] = useState<ResultsState>('initial')
  const [results, setResults] = useState<CitationOut[]>([])
  const [searchError, setSearchError] = useState<WireError | null>(null)
  const [lastQuery, setLastQuery] = useState('')
  const [usedMatchMode, setUsedMatchMode] = useState<MatchMode>('or')
  const [note, setNote] = useState<string | null>(null)
  const [healthMsg, setHealthMsg] = useState<{ severity: 'warn' | 'down'; text: string } | null>(null)
  const queryTermsRef = useRef<string[]>([])

  // Health polling (30s interval, matches app.js behavior)
  const checkHealth = useCallback(async () => {
    const res = await apiHealth()
    if (res.error) {
      setHealthMsg({ severity: 'down', text: '서비스 상태를 확인할 수 없습니다. IT 담당자에게 문의하세요.' })
      return
    }
    const data = res.data!
    if (data.status === 'ok') {
      setHealthMsg(null)
    } else if (data.embed_sidecar === 'error') {
      setHealthMsg({ severity: 'warn', text: `서비스 저하 — 검색 엔진 응답 없음 (DB: ${data.db_pool ?? '?'})` })
    } else {
      setHealthMsg({ severity: 'warn', text: `서비스 저하 — DB: ${data.db_pool ?? '?'}, 임베딩: ${data.embed_sidecar ?? '?'}` })
    }
  }, [])

  useEffect(() => {
    checkHealth()
    const timer = setInterval(checkHealth, 30000)
    return () => clearInterval(timer)
  }, [checkHealth])

  async function doSearch() {
    const q = query.trim()
    if (!q) return

    setLastQuery(q)
    setUsedMatchMode(matchMode)
    setResultsState('loading')
    setSearchError(null)
    setNote(null)
    queryTermsRef.current = []

    const res = await apiSearch({
      query: q,
      top_k: topK,
      match_mode: matchMode,
      case_id: selectedCaseId || null,
    })

    if (res.error) {
      if (res.error.code === 'SIDECAR_DOWN') {
        setResultsState('sidecar-down')
      } else {
        setSearchError(res.error)
        setResultsState('error')
      }
      return
    }

    const data = res.data!
    const items = data.results ?? []

    if (items.length === 0) {
      setResultsState('empty')
      return
    }

    queryTermsRef.current = expandQueryTermsForHighlight(q)
    setResults(items)
    setNote(data.note ?? null)
    setResultsState('results')
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      doSearch()
    }
  }

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <main className="page-main" style={{ padding: 0, flex: 1 }}>
      {/* Health banner */}
      {healthMsg && (
        <div className={`health-banner health-banner--${healthMsg.severity}`} role="status">
          {healthMsg.text}
        </div>
      )}

      {/* Search bar (sticky below header via top: 52px in app.css) */}
      <div className="search-bar-section">
        <div className="search-bar">
          <textarea
            className="search-bar__input"
            placeholder="검색어 입력 (Enter로 검색, Shift+Enter 줄바꿈)"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            aria-label="검색어"
          />
          <button
            type="button"
            className="btn btn--primary search-bar__btn"
            onClick={doSearch}
            disabled={resultsState === 'loading'}
            aria-busy={resultsState === 'loading'}
          >
            검색
          </button>
        </div>

        <div className="search-bar-controls">
          {/* Top-K selector */}
          <select
            className="search-param-select"
            value={topK}
            onChange={e => setTopK(Number(e.target.value))}
            aria-label="검색 결과 수"
          >
            {[3, 5, 10, 20].map(n => (
              <option key={n} value={n}>{n}건</option>
            ))}
          </select>

          {/* Match mode toggle (AND / OR) */}
          <div className="match-mode-toggle" role="group" aria-label="검색 매치 방식">
            <button
              type="button"
              className={`match-mode-btn${matchMode === 'and' ? ' match-mode-btn--active' : ''}`}
              aria-pressed={matchMode === 'and'}
              onClick={() => setMatchMode('and')}
            >
              모두 포함
            </button>
            <button
              type="button"
              className={`match-mode-btn${matchMode === 'or' ? ' match-mode-btn--active' : ''}`}
              aria-pressed={matchMode === 'or'}
              onClick={() => setMatchMode('or')}
            >
              하나라도
            </button>
          </div>

          {/* Phase B: case_id URL param 수신 시 사건 필터 표시 (읽기전용, AC-07) */}
          {selectedCaseId && (
            <span
              className="ingest-status-badge ingest-badge--indexed"
              style={{ alignSelf: 'center' }}
              aria-label={`사건 필터 적용 중: ${selectedCaseId}`}
              title={`사건 필터: ${selectedCaseId}`}
            >
              사건 필터 적용
            </span>
          )}
        </div>
      </div>

      {/* Results area */}
      <div
        className={`results-section results--${resultsState}`}
        style={{ maxWidth: 960, margin: '0 auto', padding: '24px 24px' }}
      >
        {/* Results header */}
        {resultsState === 'results' && (
          <div className="results-header" aria-live="polite">
            검색 결과 {results.length}건
            <span aria-hidden="true"> · </span>
            <span
              className="results-mode-label"
              aria-label={`검색 모드: ${usedMatchMode === 'and' ? '모두 포함(AND)' : '하나라도(OR)'}`}
            >
              {usedMatchMode === 'and' ? '모두 포함' : '하나라도'}
            </span>
            <span aria-hidden="true"> · </span>
            <em>"{lastQuery}"</em>
            {note && (
              <>
                <span aria-hidden="true"> · </span>
                <span className="results-header__note">출처 인용만 제공 — 생성형 답변 없음</span>
              </>
            )}
          </div>
        )}

        {/* State: initial */}
        {resultsState === 'initial' && (
          <p className="results-message">
            검색어를 입력하면 관련 문서를 출처와 함께 보여줍니다.
          </p>
        )}

        {/* State: loading — skeleton cards */}
        {resultsState === 'loading' && <SkeletonCards />}

        {/* State: empty */}
        {resultsState === 'empty' && (
          <p className="results-message">
            입력하신 내용과 일치하는 문서가 없습니다. 다른 표현으로 다시 검색해 보세요.
          </p>
        )}

        {/* State: error */}
        {resultsState === 'error' && (
          <p className="results-message" role="alert">
            {searchError?.messageKo ?? '검색 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.'}
          </p>
        )}

        {/* State: sidecar-down */}
        {resultsState === 'sidecar-down' && (
          <p className="results-message" role="alert">
            검색 서비스가 일시적으로 이용 불가합니다. IT 담당자에게 문의하세요.
          </p>
        )}

        {/* State: results — citation cards */}
        {resultsState === 'results' && (
          <ul className="results-list">
            {results.map(cit => (
              <CitationCard
                key={cit.chunk_id}
                cit={cit}
                queryTerms={queryTermsRef.current}
                lastQuery={lastQuery}
              />
            ))}
          </ul>
        )}
      </div>
    </main>
  )
}
