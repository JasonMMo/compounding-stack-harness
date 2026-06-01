/**
 * DetailScreen.tsx — entity.read + entity.update screen.
 *
 * Fetches entity by ID, renders typed form from manifest (falls back to
 * generic key/value when no manifest). PATCH on submit.
 * F-3: error envelope rendered with messageKo on update failure.
 * Route: /entities/:entityType/:entityId
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { apiEntityRead, apiEntityUpdate, type WireError } from '../api/wire'
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

export default function DetailScreen() {
  const { entityType = '', entityId = '' } = useParams<{ entityType: string; entityId: string }>()
  const navigate = useNavigate()

  const [loadError, setLoadError] = useState<WireError | null>(null)
  const [saveError, setSaveError] = useState<WireError | null>(null)
  const [saveFieldErrors, setSaveFieldErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [rawData, setRawData] = useState<Record<string, unknown>>({})
  const [manifestFields, setManifestFields] = useState<ManifestField[] | null>(null)
  const [hiddenFields, setHiddenFields] = useState<string[]>([])
  const [entityLabel, setEntityLabel] = useState<string>('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      setLoadError(null)
      await ensureManifestLoaded()

      const fields = getEntityFields(entityType)
      const hidden = getHiddenFields(entityType)
      const label = getEntityLabel(entityType) ?? entityType
      setManifestFields(fields)
      setHiddenFields(hidden)
      setEntityLabel(label)

      const result = await apiEntityRead(entityType, entityId)
      setLoading(false)

      if (result.error) {
        setLoadError(result.error)
        if (result.error.isAuth) navigate('/login', { replace: true })
        return
      }

      const data = result.data?.data ?? {}
      setRawData(data)
      // Initialize formData with string values for controlled inputs
      const init: Record<string, string> = {}
      for (const [k, v] of Object.entries(data)) {
        init[k] = v == null ? '' : String(v)
      }
      setFormData(init)
    }
    load()
  }, [entityType, entityId, navigate])

  function handleFieldChange(name: string, value: string) {
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setSaveError(null)
    setSaveFieldErrors({})

    const hiddenSet = new Set(hiddenFields)
    const patch: Record<string, unknown> = {}
    for (const [k, v] of Object.entries(formData)) {
      if (!hiddenSet.has(k) && v !== '') patch[k] = v
    }

    const result = await apiEntityUpdate(entityType, entityId, patch)
    setSaving(false)

    if (result.error) {
      setSaveError(result.error)
      if (result.error.isAuth) navigate('/login', { replace: true })
      // Extract per-field errors from details.fields
      const fieldErrors = (result.error.details?.['fields'] as Record<string, string>) ?? {}
      setSaveFieldErrors(fieldErrors)
      return
    }

    navigate(`/entities/${entityType}/${entityId}`, { replace: true })
  }

  if (loading) return <div className="loading">불러오는 중...</div>
  if (loadError) return <ErrorBanner error={loadError} />

  const hiddenSet = new Set(hiddenFields)
  const allKeys = Object.keys(rawData)

  return (
    <div>
      <div className="page-header">
        <h1>{entityLabel} 상세 — {entityId}</h1>
        <Link to={`/entities/${entityType}`} className="btn btn-secondary btn-sm">
          목록으로
        </Link>
        <Link to={`/entities/${entityType}/${entityId}/delete`} className="btn btn-danger btn-sm">
          삭제
        </Link>
      </div>

      {saveError && (
        <ErrorBanner error={saveError} onRetry={saveError.retriable ? () => setSaveError(null) : undefined} />
      )}

      <div className="card">
        <form onSubmit={handleSubmit}>
          {manifestFields ? (
            // Typed form from manifest
            manifestFields
              .filter(f => !hiddenSet.has(f.name))
              .map(f => (
                <TypedField
                  key={f.name}
                  field={f}
                  value={formData[f.name] ?? ''}
                  onChange={handleFieldChange}
                  disabled={saving}
                  fieldError={saveFieldErrors[f.name]}
                />
              ))
          ) : (
            // Generic key/value fallback
            allKeys
              .filter(k => !hiddenSet.has(k))
              .map(k => (
                <div className="form-group" key={k}>
                  <label className="form-label" htmlFor={`field-${k}`}>{k}</label>
                  <input
                    id={`field-${k}`}
                    type="text"
                    className="form-input"
                    value={formData[k] ?? ''}
                    onChange={e => handleFieldChange(k, e.target.value)}
                    disabled={saving}
                  />
                  {saveFieldErrors[k] && (
                    <div className="form-error-field">{saveFieldErrors[k]}</div>
                  )}
                </div>
              ))
          )}

          {/* Read-only hidden fields */}
          {hiddenFields.filter(h => rawData[h] !== undefined).map(h => (
            <div className="form-group" key={h}>
              <label className="form-label">{h}</label>
              <input
                type="text"
                className="form-input"
                value={String(rawData[h] ?? '')}
                disabled
                readOnly
              />
            </div>
          ))}

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? '저장 중...' : '저장'}
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
