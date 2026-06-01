/**
 * HealthScreen.tsx — status.health screen.
 * Route: /health
 */

import { useState, useEffect } from 'react'
import { apiHealthCheck, type HealthResponse, type WireError } from '../api/wire'
import ErrorBanner from '../components/ErrorBanner'
import { WIRE_VERSION } from '../contract/contract.gen'

export default function HealthScreen() {
  const [data, setData] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<WireError | null>(null)
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    setError(null)
    const result = await apiHealthCheck()
    setLoading(false)
    if (result.error) {
      setError(result.error)
      return
    }
    setData(result.data)
  }

  useEffect(() => { load() }, [])

  function statusBadge(status: string) {
    if (status === 'ok') return <span className="badge badge-success">{status}</span>
    if (status === 'degraded') return <span className="badge badge-neutral">{status}</span>
    return <span className="badge badge-danger">{status}</span>
  }

  return (
    <div>
      <div className="page-header">
        <h1>상태 확인</h1>
        <button className="btn btn-secondary btn-sm" onClick={load} disabled={loading}>
          새로고침
        </button>
      </div>

      {loading && <div className="loading">확인 중...</div>}
      {error && <ErrorBanner error={error} onRetry={error.retriable ? load : undefined} />}

      {data && (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-gap-md)', marginBottom: 'var(--space-gap-md)' }}>
            <span className="form-label" style={{ marginBottom: 0 }}>전체 상태</span>
            {statusBadge(data.status)}
          </div>

          <div className="form-group">
            <span className="form-label">계약 버전</span>
            <code>{data.version}</code>
          </div>

          {data.checks && data.checks.length > 0 && (
            <div>
              <h2>컴포넌트 상태</h2>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>컴포넌트</th>
                      <th>상태</th>
                      <th>메시지</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.checks.map((c, i) => (
                      <tr key={i}>
                        <td>{c.name}</td>
                        <td>{statusBadge(c.status)}</td>
                        <td className="text-muted">{c.message ?? ''}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      <p className="wire-version">wire contract v{WIRE_VERSION}</p>
    </div>
  )
}
