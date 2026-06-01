/**
 * manifest.ts — Screen-manifest loader for typed form rendering (Growth-14).
 *
 * Mirrors vanilla-htmx/manifest_loader.py behavior.
 * Source: out/<profile>/screen-manifest.json
 *
 * Resolution order:
 *   1. VITE_MANIFEST_URL env var (absolute URL or path) — fetched at runtime.
 *   2. /manifest.json — served from public/ if baked into the build.
 *   3. No manifest — falls back to generic key/value rendering.
 *
 * G-1 note: this loader is render-only. It does NOT re-derive classification
 * logic from catalog — it reads the manifest produced by scripts/workflow/manifest.py.
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

export interface ManifestEntity {
  domain: string
  table: string
  label: string
  fields: ManifestField[]
  hidden_fields: string[]
}

export interface ScreenManifest {
  profile: string
  catalog_version: string
  entities: Record<string, ManifestEntity>
}

// Module-level cache
let _manifest: ScreenManifest | null = null
let _loaded = false
let _loadPromise: Promise<void> | null = null

const MANIFEST_URL = (import.meta.env.VITE_MANIFEST_URL as string | undefined) ?? '/manifest.json'

async function _load(): Promise<void> {
  if (_loaded) return
  try {
    const resp = await fetch(MANIFEST_URL)
    if (!resp.ok) {
      console.info(`[manifest] ${MANIFEST_URL} returned ${resp.status} — fallback rendering active.`)
      _loaded = true
      return
    }
    const doc: ScreenManifest = await resp.json()
    _manifest = doc
    _loaded = true
    console.info(
      `[manifest] loaded profile='${doc.profile}', entities=${Object.keys(doc.entities).join(', ')}`,
    )
  } catch (e) {
    console.info('[manifest] fetch failed — fallback rendering active.', e)
    _loaded = true
  }
}

export function ensureManifestLoaded(): Promise<void> {
  if (_loaded) return Promise.resolve()
  if (!_loadPromise) {
    _loadPromise = _load()
  }
  return _loadPromise
}

export function getEntityFields(entityType: string): ManifestField[] | null {
  if (!_manifest) return null
  return _manifest.entities[entityType]?.fields ?? null
}

export function getHiddenFields(entityType: string): string[] {
  if (!_manifest) return []
  return _manifest.entities[entityType]?.hidden_fields ?? []
}

export function getEntityLabel(entityType: string): string | null {
  if (!_manifest) return null
  return _manifest.entities[entityType]?.label ?? null
}

export function isManifestLoaded(): boolean {
  return _loaded && _manifest !== null
}
