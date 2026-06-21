/**
 * manifest.ts — stub for legal-pro adapter.
 *
 * The legal-pro adapter does not use the generic screen-manifest (Growth-14)
 * because the legal-rag search UI is purpose-built, not entity-generic.
 * This file exists to satisfy the adapter structure contract (open-closed:
 * all adapters have src/api/manifest.ts) but is not used by any screen.
 *
 * If Phase B (case-management CRUD) is implemented, a case-specific manifest
 * or typed-form approach should be added here.
 */

export interface ManifestField {
  name: string
  type: string
  required: boolean
  label: string
  control: 'text' | 'textarea' | 'number' | 'date' | 'datetime' | 'select' | 'checkbox' | 'fk-text'
  options?: string[]
  fk_entity?: string
  note?: string
  max_length?: number
  unique?: boolean
}

// Phase B TODO: implement manifest loading for case-management screens.
export function getEntityFields(_entityType: string): ManifestField[] | null {
  return null
}

export function isManifestLoaded(): boolean {
  return false
}
