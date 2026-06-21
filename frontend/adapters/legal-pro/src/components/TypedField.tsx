/**
 * TypedField.tsx — Typed form field renderer (manifest-driven).
 *
 * Included for adapter structure completeness (open-closed contract).
 * Phase A does not use this in any screen — it is reserved for Phase B
 * case-management forms.
 *
 * Mirrors the react adapter's TypedField for structural consistency.
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

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
  ) {
    onChange(field.name, e.target.value)
  }

  function renderControl() {
    switch (field.control) {
      case 'textarea':
        return (
          <textarea
            id={id}
            name={field.name}
            className="form-input"
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
    <div className="form-field">
      <label htmlFor={id} className="form-label">
        {field.label}
        {field.required && <span aria-hidden="true" style={{ color: 'var(--color-danger)', marginLeft: 2 }}>*</span>}
      </label>
      {renderControl()}
      {fieldError && (
        <div className="form-error" role="alert">
          {fieldError}
        </div>
      )}
    </div>
  )
}
