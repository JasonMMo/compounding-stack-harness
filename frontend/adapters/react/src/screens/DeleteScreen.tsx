/**
 * DeleteScreen.tsx — entity.delete confirm + execute screen.
 *
 * F-4: DELETE called twice both render success.
 *   - If GET /entity returns NOT_FOUND on the confirm step → already deleted → success.
 *   - If DELETE returns 404 → wire.ts maps to success before returning here.
 * Route: /entities/:entityType/:entityId/delete
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { apiEntityRead, apiEntityDelete, type WireError } from '../api/wire'
import ErrorBanner from '../components/ErrorBanner'
import { WIRE_VERSION } from '../contract/contract.gen'

type State =
  | { phase: 'loading' }
  | { phase: 'confirm'; data: Record<string, unknown> }
  | { phase: 'already-deleted' }
  | { phase: 'error'; error: WireError }
  | { phase: 'deleting' }
  | { phase: 'success' }

export default function DeleteScreen() {
  const { entityType = '', entityId = '' } = useParams<{ entityType: string; entityId: string }>()
  const navigate = useNavigate()
  const [state, setState] = useState<State>({ phase: 'loading' })

  useEffect(() => {
    async function loadConfirm() {
      const result = await apiEntityRead(entityType, entityId)

      if (result.error) {
        // F-4: NOT_FOUND on confirm step → already deleted → show success
        if (result.error.code === 'NOT_FOUND') {
          setState({ phase: 'already-deleted' })
          return
        }
        if (result.error.isAuth) {
          navigate('/login', { replace: true })
          return
        }
        setState({ phase: 'error', error: result.error })
        return
      }

      setState({ phase: 'confirm', data: result.data?.data ?? {} })
    }
    loadConfirm()
  }, [entityType, entityId, navigate])

  async function handleDelete() {
    setState({ phase: 'deleting' })

    const result = await apiEntityDelete(entityType, entityId)

    if (result.error) {
      // F-4: should not happen (wire.ts maps 404→success), but handle gracefully
      if (result.error.isAuth) {
        navigate('/login', { replace: true })
        return
      }
      setState({ phase: 'error', error: result.error })
      return
    }

    // Success — including F-4 idempotent second call
    setState({ phase: 'success' })
  }

  if (state.phase === 'loading' || state.phase === 'deleting') {
    return <div className="loading">{state.phase === 'deleting' ? '삭제 중...' : '불러오는 중...'}</div>
  }

  if (state.phase === 'success' || state.phase === 'already-deleted') {
    return (
      <div>
        <div className="card">
          <div className="alert alert-success" role="status">
            삭제 완료 — {entityType} / {entityId}
            {state.phase === 'already-deleted' && ' (이미 삭제된 항목)'}
          </div>
          <div className="form-actions" style={{ borderTop: 'none', paddingTop: 0 }}>
            <Link to={`/entities/${entityType}`} className="btn btn-primary">
              목록으로
            </Link>
          </div>
        </div>
        <p className="wire-version">wire contract v{WIRE_VERSION}</p>
      </div>
    )
  }

  if (state.phase === 'error') {
    return (
      <div>
        <ErrorBanner error={state.error} />
        <Link to={`/entities/${entityType}`} className="btn btn-secondary">
          목록으로
        </Link>
        <p className="wire-version">wire contract v{WIRE_VERSION}</p>
      </div>
    )
  }

  // Confirm phase
  const entries = Object.entries(state.data).slice(0, 8)

  return (
    <div>
      <div className="page-header">
        <h1>삭제 확인</h1>
      </div>

      <div className="card">
        <div className="alert alert-warning">
          <strong>{entityType}</strong> 항목 <code>{entityId}</code>를 삭제합니다.
          이 작업은 취소할 수 없습니다.
        </div>

        {entries.length > 0 && (
          <table style={{ marginBottom: 'var(--space-gap-md)' }}>
            <tbody>
              {entries.map(([k, v]) => (
                <tr key={k}>
                  <td style={{ fontWeight: 500, paddingRight: 'var(--space-gap-md)', color: 'var(--color-text-2)' }}>{k}</td>
                  <td>{String(v ?? '')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div className="form-actions">
          <button
            type="button"
            className="btn btn-danger"
            onClick={handleDelete}
          >
            삭제 확인
          </button>
          <Link to={`/entities/${entityType}/${entityId}`} className="btn btn-secondary">
            취소
          </Link>
        </div>
      </div>

      <p className="wire-version">wire contract v{WIRE_VERSION}</p>
    </div>
  )
}
