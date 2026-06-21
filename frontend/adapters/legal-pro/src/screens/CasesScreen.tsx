/**
 * CasesScreen.tsx — 사건 목록 화면 (Phase B, S-09/S-10/S-11/S-12).
 *
 * Design contracts:
 *  - GET /cases?limit=20&offset={n} → CasesResponse (§3.1)
 *  - status 한국어 매핑 (active→진행중, closed→종결, intake→접수중 …)
 *  - 색인 상태 뱃지 우선순위: 실패 > 대기 > 완료 (§3.1)
 *  - total 기반 페이지네이션 (§4.2)
 *  - 행 클릭 → /cases/:id, [검색] → /search?case_id=<uuid> (OQ-2, OQ-3)
 *  - 삭제 UI 없음 (AC-10, F-07)
 *  - 401 → clearToken + 로그인 리디렉션 (AC-09)
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  apiListCases,
  type CaseSummary,
  type WireError,
} from '../api/wire'

// ── Constants ──────────────────────────────────────────────────────────────

const PAGE_SIZE = 20

// ── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_MAP: Record<string, string> = {
  active: '진행중',
  closed: '종결',
  intake: '접수중',
  trial: '재판중',
  appeal: '항소중',
  withdrawn: '취하',
}

function statusLabel(raw: string): string {
  return STATUS_MAP[raw] ?? raw
}

/** 색인 상태 뱃지: 우선순위 실패 > 대기 > 완료 */
function IngestBadge({ failed, pending }: { failed: number; pending: number }) {
  if (failed > 0) {
    return (
      <span className="ingest-status-badge ingest-badge--failed" aria-label="색인 실패">
        실패
      </span>
    )
  }
  if (pending > 0) {
    return (
      <span className="ingest-status-badge ingest-badge--pending" aria-label="색인 대기">
        대기중
      </span>
    )
  }
  return (
    <span className="ingest-status-badge ingest-badge--indexed" aria-label="색인 완료">
      완료
    </span>
  )
}

// ── Main screen ────────────────────────────────────────────────────────────

export default function CasesScreen() {
  const navigate = useNavigate()

  const [cases, setCases] = useState<CaseSummary[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<WireError | null>(null)

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1

  const load = useCallback(async (nextOffset: number) => {
    setLoading(true)
    setError(null)

    const res = await apiListCases(PAGE_SIZE, nextOffset)

    setLoading(false)

    if (res.error) {
      if (res.error.isAuth) {
        // 401 — clearToken already called in wire.ts legalRequest
        navigate('/login', { replace: true })
        return
      }
      setError(res.error)
      return
    }

    const data = res.data!
    setCases(data.cases)
    setTotal(data.total)
    setOffset(data.offset)
  }, [navigate])

  useEffect(() => {
    load(0)
  }, [load])

  function goPage(targetOffset: number) {
    load(targetOffset)
  }

  function handleRowClick(caseId: string) {
    navigate(`/cases/${caseId}`)
  }

  function handleSearch(caseId: string, e: React.MouseEvent) {
    e.stopPropagation()
    navigate(`/search?case_id=${encodeURIComponent(caseId)}`)
  }

  // ── S-11: 빈 상태 ───────────────────────────────────────────────────────
  if (!loading && !error && total === 0 && cases.length === 0) {
    return (
      <main className="page-main">
        <div className="page-title-bar">사건 현황</div>
        <div
          className="results-message"
          role="status"
          aria-live="polite"
        >
          등록된 사건이 없습니다.
        </div>
      </main>
    )
  }

  // ── S-12: 로드 실패 ─────────────────────────────────────────────────────
  if (!loading && error) {
    return (
      <main className="page-main">
        <div className="page-title-bar">사건 현황</div>
        <p className="results-message" role="alert">
          {error.messageKo || '사건 목록을 불러오지 못했습니다.'}
        </p>
      </main>
    )
  }

  // ── S-09/S-10: 로딩 및 정상 ─────────────────────────────────────────────
  return (
    <main className="page-main" style={{ padding: 0, flex: 1 }}>
      <div className="page-title-bar">
        사건 현황
        {!loading && total > 0 && (
          <span
            style={{ fontWeight: 400, fontSize: 'var(--text-meta-size)', color: 'var(--color-text-3)', marginLeft: 8 }}
          >
            총 {total}건
          </span>
        )}
      </div>

      <div className="case-table-section">
        {loading ? (
          <p className="results-message" role="status" aria-live="polite">
            불러오는 중…
          </p>
        ) : (
          <>
            <table className="case-table" aria-label="사건 목록">
              <caption className="sr-only">사건 목록 테이블 — 행 클릭 시 사건 상세로 이동합니다</caption>
              <thead>
                <tr>
                  <th className="case-th" scope="col">사건번호</th>
                  <th className="case-th" scope="col">사건명</th>
                  <th className="case-th" scope="col">상태</th>
                  <th className="case-th" scope="col">문서</th>
                  <th className="case-th" scope="col">색인</th>
                  <th className="case-th" scope="col">
                    <span className="sr-only">작업</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {cases.map(c => (
                  <tr
                    key={c.case_id}
                    className={`case-row${c.doc_failed > 0 ? ' case-row--error' : ''}`}
                    onClick={() => handleRowClick(c.case_id)}
                    style={{ cursor: 'pointer' }}
                    tabIndex={0}
                    onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') handleRowClick(c.case_id) }}
                    aria-label={`사건 ${c.case_number} 상세 보기`}
                  >
                    <td>
                      <span className="case-number">{c.case_number}</span>
                    </td>
                    <td className="case-title">{c.title}</td>
                    <td>{statusLabel(c.status)}</td>
                    <td className="doc-count">{c.doc_total}건</td>
                    <td>
                      <IngestBadge failed={c.doc_failed} pending={c.doc_pending} />
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn--outline btn--sm"
                        onClick={e => handleSearch(c.case_id, e)}
                        aria-label={`${c.case_number} 판례 검색`}
                      >
                        검색
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* 페이지네이션 */}
            {totalPages > 1 && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  marginTop: 16,
                  justifyContent: 'center',
                }}
                role="navigation"
                aria-label="페이지 이동"
              >
                <button
                  type="button"
                  className="btn btn--outline btn--sm"
                  onClick={() => goPage(offset - PAGE_SIZE)}
                  disabled={offset - PAGE_SIZE < 0}
                  aria-disabled={offset - PAGE_SIZE < 0}
                  aria-label="이전 페이지"
                >
                  이전
                </button>
                <span style={{ fontSize: 'var(--text-meta-size)', color: 'var(--color-text-3)' }}>
                  {currentPage} / {totalPages}
                </span>
                <button
                  type="button"
                  className="btn btn--outline btn--sm"
                  onClick={() => goPage(offset + PAGE_SIZE)}
                  disabled={offset + PAGE_SIZE >= total}
                  aria-disabled={offset + PAGE_SIZE >= total}
                  aria-label="다음 페이지"
                >
                  다음
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  )
}
