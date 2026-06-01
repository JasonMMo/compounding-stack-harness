/**
 * TypedField.tsx — Renders a typed form field from the screen manifest.
 *
 * Supports all control types defined in ManifestField.control:
 *   text | textarea | number | date | datetime | select | checkbox | fk-text
 *
 * Falls back to a text input for unknown control types.
 * FK fields show the fk_entity hint and a "FK dropdown deferred (M1)" note.
 */

import type { ManifestField } from '../api/manifest'

interface Props {
  field: ManifestField
  value: string
  onChange: (name: string, value: string) => void
  disabled?: boolean
  fieldError?: string
}

export default function TypedField({ field, value, onChange, disabled, fieldError }: Props) {
  const id = `field-${field.name}`

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    onChange(field.name, e.target.value)
  }

  function renderControl() {
    switch (field.control) {
      case 'textarea':
        return (
          <textarea
            id={id}
            name={field.name}
            className="form-textarea"
            value={value}
            onChange={handleChange}
            disabled={disabled}
            rows={3}
            maxLength={field.max_length}
            required={field.required}
          />
        )

      case 'number':
        return (
          <input
            id={id}
            name={field.name}
            type="number"
            className="form-input"
            value={value}
            onChange={handleChange}
            disabled={disabled}
            required={field.required}
          />
        )

      case 'date':
        return (
          <input
            id={id}
            name={field.name}
            type="date"
            className="form-input"
            value={value}
            onChange={handleChange}
            disabled={disabled}
            required={field.required}
          />
        )

      case 'datetime':
        return (
          <input
            id={id}
            name={field.name}
            type="datetime-local"
            className="form-input"
            value={value}
            onChange={handleChange}
            disabled={disabled}
            required={field.required}
          />
        )

      case 'select':
        return (
          <select
            id={id}
            name={field.name}
            className="form-select"
            value={value}
            onChange={handleChange}
            disabled={disabled}
            required={field.required}
          >
            <option value="">-- 선택 --</option>
            {field.options?.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        )

      case 'checkbox':
        return (
          <input
            id={id}
            name={field.name}
            type="checkbox"
            checked={value === 'true' || value === '1'}
            onChange={e => onChange(field.name, e.target.checked ? 'true' : 'false')}
            disabled={disabled}
          />
        )

      case 'fk-text':
        return (
          <>
            <input
              id={id}
              name={field.name}
              type="text"
              className="form-input"
              value={value}
              onChange={handleChange}
              disabled={disabled}
              required={field.required}
              placeholder={`${field.fk_entity ?? ''} ID`}
            />
            <span className="form-hint">
              FK: {field.fk_entity ?? '?'} — FK dropdown deferred (M1)
            </span>
          </>
        )

      case 'text':
      default:
        return (
          <input
            id={id}
            name={field.name}
            type="text"
            className="form-input"
            value={value}
            onChange={handleChange}
            disabled={disabled}
            required={field.required}
            maxLength={field.max_length}
          />
        )
    }
  }

  return (
    <div className="form-group">
      <label htmlFor={id} className="form-label">
        {field.label}
        {field.required && <span className="required" aria-hidden="true">*</span>}
        {field.unique && <span className="text-muted"> (고유)</span>}
      </label>
      {renderControl()}
      {field.note && field.control !== 'fk-text' && (
        <span className="form-hint">{field.note}</span>
      )}
      {fieldError && <div className="form-error-field">{fieldError}</div>}
    </div>
  )
}
