/**
 * ListScreen.tsx — entity.list screen.
 *
 * F-1: paging/sort params serialized as flat-underscore via buildListParams().
 * F-2: offset (default) + cursor paging modes both supported.
 * F-3: error envelope rendered with messageKo, retriable codes get retry.
 * Route: /entities/:entityType
 */

import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate, Link, useSearchParams } from 'react-router-dom'
import { apiEntityList, type ListResponse, type ListParams } from '../api/wire'
import ErrorBanner from '../components/ErrorBanner'
import type { WireError } from '../api/wire'
import { WIRE_VERSION } from '../contract/contract.gen'

const DEFAULT_PAGE_SIZE = 20

export default function ListScreen() {
  const { entityType = 'customer' } = useParams<{ entityType: string }>()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  // Derive state from URL search params (supports browser back/forward)
  const pagingMode = (searchParams.get('paging_mode') ?? 'offset') as 'offset' | 'cursor'
  const pagingPage = parseInt(searchParams.get('paging_page') ?? '1', 10)
  const pagingSize = parseInt(searchParams.get('paging_size') ?? String(DEFAULT_PAGE_SIZE), 10)
  const pagingCursor = searchParams.get('paging_cursor') ?? ''
  const sortField = searchParams.get('sort_field') ?? ''
  const sortDirection = (searchParams.get('sort_direction') ?? 'asc') as 'asc' | 'desc'
  const search = searchParams.get('search') ?? ''

  const [data, setData] = useState<ListResponse | null>(null)
  const [error, setError] = useState<WireError | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchList = useCallback(async () => {
    setLoading(true)
    setError(null)

    const params: ListParams = {
      pagingMode,
      pagingSize,
    }

    if (pagingMode === 'offset') {
      params.pagingPage = pagingPage
    } else if (pagingMode === 'cursor' && pagingCursor) {
      params.pagingCursor = pagingCursor
    }

    if (sortField) {
      params.sortField = sortField
      params.sortDirection = sortDirection
    }

    if (search) params.search = search

    const result = await apiEntityList(entityType, params)
    setLoading(false)

    if (result.error) {
      setError(result.error)
      if (result.error.isAuth) navigate('/login', { replace: true })
      return
    }
    setData(result.data)
  }, [entityType, pagingMode, pagingPage, pagingSize, pagingCursor, sortField, sortDirection, search, navigate])

  useEffect(() => {
    fetchList()
  }, [fetchList])

  function updateParams(updates: Record<string, string>) {
    const next = new URLSearchParams(searchParams)
    for (const [k, v] of Object.entries(updates)) {
      if (v === '') next.delete(k)
      else next.set(k, v)
    }
    setSearchParams(next)
  }

  function handleSort(field: string) {
    const newDir = sortField === field && sortDirection === 'asc' ? 'desc' : 'asc'
    updateParams({ sort_field: field, sort_direction: newDir, paging_page: '1' })
  }

  function handleSearch(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const val = (e.currentTarget.elements.namedItem('q') as HTMLInputElement).value
    updateParams({ search: val, paging_page: '1' })
  }

  function handlePageChange(newPage: number) {
    updateParams({ paging_page: String(newPage) })
  }

  function handleCursorNext() {
    if (data?.next_cursor) {
      updateParams({ paging_cursor: data.next_cursor, paging_mode: 'cursor' })
    }
  }

  function switchPagingMode(mode: 'offset' | 'cursor') {
    const next = new URLSearchParams()
    next.set('paging_mode', mode)
    if (mode === 'offset') {
      next.set('paging_page', '1')
      next.set('paging_size', String(pagingSize))
    }
    setSearchParams(next)
  }

  const items = data?.items ?? []
  const total = data?.total ?? 0
  const columns = items.length > 0 ? Object.keys(items[0]) : []
  const totalPages = Math.max(1, Math.ceil(total / pagingSize))

  return (
    <div>
      <div className="page-header">
        <h1>{entityType}</h1>
        <Link to={`/entities/${entityType}/new`} className="btn btn-primary btn-sm">
          + 새 항목
        </Link>
      </div>

      {/* Toolbar */}
      <div className="toolbar">
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 'var(--space-gap-sm)' }}>
          <input
            type="search"
            name="q"
            className="search-input"
            defaultValue={search}
            placeholder="검색..."
            aria-label="검색"
          />
          <button type="submit" className="btn btn-secondary btn-sm">검색</button>
        </form>
        <span className="navbar-spacer" />
        {/* F-2: paging mode toggle */}
        <span className="text-muted" style={{ fontSize: 'var(--font-size-sm)' }}>페이징:</span>
        <button
          className={`btn btn-sm ${pagingMode === 'offset' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => switchPagingMode('offset')}
        >
          offset
        </button>
        <button
          className={`btn btn-sm ${pagingMode === 'cursor' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => switchPagingMode('cursor')}
        >
          cursor
        </button>
      </div>

      {loading && <div className="loading">불러오는 중...</div>}

      {error && (
        <ErrorBanner
          error={error}
          onRetry={error.retriable ? fetchList : undefined}
        />
      )}

      {!loading && !error && (
        <>
          {items.length === 0 ? (
            <div className="text-muted" style={{ padding: 'var(--space-inset-lg)', textAlign: 'center' }}>
              항목이 없습니다.
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    {columns.map(col => (
                      <th key={col}>
                        <button
                          style={{ background: 'none', border: 'none', cursor: 'pointer', font: 'inherit', fontWeight: 600, color: 'var(--color-text-2)' }}
                          onClick={() => handleSort(col)}
                          aria-label={`${col} 정렬`}
                        >
                          {col}
                          {sortField === col ? (sortDirection === 'asc' ? ' ▲' : ' ▼') : ''}
                        </button>
                      </th>
                    ))}
                    <th>작업</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, idx) => {
                    const id = String(item['id'] ?? idx)
                    return (
                      <tr key={id}>
                        {columns.map(col => (
                          <td key={col}>
                            {String(item[col] ?? '')}
                          </td>
                        ))}
                        <td>
                          <Link
                            to={`/entities/${entityType}/${id}`}
                            className="btn btn-secondary btn-sm"
                            style={{ marginRight: 4 }}
                          >
                            상세
                          </Link>
                          <Link
                            to={`/entities/${entityType}/${id}/delete`}
                            className="btn btn-danger btn-sm"
                          >
                            삭제
                          </Link>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* F-2: offset pagination bar */}
          {pagingMode === 'offset' && (
            <div className="pagination">
              <span className="pagination-info">
                총 {total}개 / {totalPages}페이지
              </span>
              <button
                className="page-btn"
                disabled={pagingPage <= 1}
                onClick={() => handlePageChange(pagingPage - 1)}
              >
                이전
              </button>
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                const page = Math.max(1, pagingPage - 2) + i
                if (page > totalPages) return null
                return (
                  <button
                    key={page}
                    className={`page-btn ${page === pagingPage ? 'active' : ''}`}
                    onClick={() => handlePageChange(page)}
                  >
                    {page}
                  </button>
                )
              })}
              <button
                className="page-btn"
                disabled={pagingPage >= totalPages}
                onClick={() => handlePageChange(pagingPage + 1)}
              >
                다음
              </button>
            </div>
          )}

          {/* F-2: cursor "Load more" button */}
          {pagingMode === 'cursor' && data?.next_cursor && (
            <div className="pagination">
              <button className="btn btn-secondary" onClick={handleCursorNext}>
                더 보기 (cursor: {data.next_cursor.substring(0, 12)}...)
              </button>
            </div>
          )}
          {pagingMode === 'cursor' && !data?.next_cursor && items.length > 0 && (
            <div className="pagination">
              <span className="pagination-info">마지막 페이지</span>
            </div>
          )}
        </>
      )}

      <p className="wire-version">wire contract v{WIRE_VERSION}</p>
    </div>
  )
}
