/**
 * CreateScreen.tsx — entity.create screen.
 *
 * Renders typed form from manifest when available, falls back to generic
 * key/value form. POST to create. F-3 on error. Hidden fields excluded.
 * Route: /entities/:entityType/new
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { apiEntityCreate, type WireError } from '../api/wire'
import {
  ensureManifestLoaded,
  getEntityFields,
  getHiddenFields,
  getEntityLabel,
  type ManifestField,
} from '../api/manifest'
import ErrorBanner from '../components/ErrorBanner'
import TypedField from '../components/TypedField'
import { WIRE_VERSION } from '../contract/contract.gen'

// Generic fallback: start with common fields the user can fill in
const FALLBACK_FIELDS = ['name', 'description', 'status', 'notes']

export default function CreateScreen() {
  const { entityType = '' } = useParams<{ entityType: string }>()
  const navigate = useNavigate()

  const [error, setError] = useState<WireError | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [manifestReady, setManifestReady] = useState(false)
  const [manifestFields, setManifestFields] = useState<ManifestField[] | null>(null)
  const [hiddenFields, setHiddenFields] = useState<string[]>([])
  const [entityLabel, setEntityLabel] = useState<string>('')
  const [formData, setFormData] = useState<Record<string, string>>({})
  // Fallback: extra fields the user adds manually
  const [extraKeys, setExtraKeys] = useState<string[]>(FALLBACK_FIELDS)
  const [newKey, setNewKey] = useState('')

  useEffect(() => {
    async function init() {
      await ensureManifestLoaded()
      const fields = getEntityFields(entityType)
      const hidden = getHiddenFields(entityType)
      const label = getEntityLabel(entityType) ?? entityType
      setManifestFields(fields)
      setHiddenFields(hidden)
      setEntityLabel(label)
      // Pre-populate formData keys from manifest (non-hidden fields)
      if (fields) {
        const hiddenSet = new Set(hidden)
        const init: Record<string, string> = {}
        for (const f of fields) {
          if (!hiddenSet.has(f.name)) init[f.name] = ''
        }
        setFormData(init)
      }
      setManifestReady(true)
    }
    init()
  }, [entityType])

  function handleFieldChange(name: string, value: string) {
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  function addExtraKey() {
    const k = newKey.trim()
    if (k && !extraKeys.includes(k)) {
      setExtraKeys(prev => [...prev, k])
    }
    setNewKey('')
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setFieldErrors({})

    const hiddenSet = new Set(hiddenFields)
    const data: Record<string, unknown> = {}
    for (const [k, v] of Object.entries(formData)) {
      if (!hiddenSet.has(k) && v !== '') data[k] = v
    }

    const result = await apiEntityCreate(entityType, data)
    setLoading(false)

    if (result.error) {
      setError(result.error)
      if (result.error.isAuth) navigate('/login', { replace: true })
      const fe = (result.error.details?.['fields'] as Record<string, string>) ?? {}
      setFieldErrors(fe)
      return
    }

    const newId = result.data?.id ?? ''
    navigate(`/entities/${entityType}/${newId}`, { replace: true })
  }

  if (!manifestReady) return <div className="loading">불러오는 중...</div>

  return (
    <div>
      <div className="page-header">
        <h1>{entityLabel} 새로 만들기</h1>
        <Link to={`/entities/${entityType}`} className="btn btn-secondary btn-sm">
          목록으로
        </Link>
      </div>

      {error && (
        <ErrorBanner
          error={error}
          onRetry={error.retriable ? () => setError(null) : undefined}
        />
      )}

      <div className="card">
        <form onSubmit={handleSubmit}>
          {manifestFields ? (
            // Typed form from manifest
            manifestFields
              .filter(f => !new Set(hiddenFields).has(f.name))
              .map(f => (
                <TypedField
                  key={f.name}
                  field={f}
                  value={formData[f.name] ?? ''}
                  onChange={handleFieldChange}
                  disabled={loading}
                  fieldError={fieldErrors[f.name]}
                />
              ))
          ) : (
            // Generic key/value fallback
            <>
              {extraKeys.map(k => (
                <div className="form-group" key={k}>
                  <label className="form-label" htmlFor={`field-${k}`}>{k}</label>
                  <input
                    id={`field-${k}`}
                    type="text"
                    className="form-input"
                    value={formData[k] ?? ''}
                    onChange={e => handleFieldChange(k, e.target.value)}
                    disabled={loading}
                  />
                  {fieldErrors[k] && (
                    <div className="form-error-field">{fieldErrors[k]}</div>
                  )}
                </div>
              ))}
              <div style={{ display: 'flex', gap: 'var(--space-gap-sm)', marginBottom: 'var(--space-gap-sm)' }}>
                <input
                  type="text"
                  className="form-input"
                  placeholder="필드명 추가"
                  value={newKey}
                  onChange={e => setNewKey(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addExtraKey())}
                  style={{ maxWidth: 200 }}
                />
                <button type="button" className="btn btn-secondary btn-sm" onClick={addExtraKey}>
                  + 필드
                </button>
              </div>
            </>
          )}

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '저장 중...' : '저장'}
            </button>
            <Link to={`/entities/${entityType}`} className="btn btn-secondary">
              취소
            </Link>
          </div>
        </form>
      </div>

      <p className="wire-version">wire contract v{WIRE_VERSION}</p>
    </div>
  )
}
