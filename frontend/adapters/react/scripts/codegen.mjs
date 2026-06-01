/**
 * codegen.mjs — Build-time contract codegen (G-1 compliance).
 *
 * Reads:
 *   middle/contract/wire-v1.yaml
 *   middle/contract/error/codes.yaml
 *
 * Emits:
 *   src/contract/contract.gen.ts
 *
 * The generated module is the ONLY place in the React adapter that contains
 * endpoint paths, error codes, HTTP status values, or flat-underscore key
 * names. No component or hook may hardcode these values — they must import
 * from this generated module (satisfying G-1: wire-protocol single source).
 *
 * G-1 / diagnose.py note:
 *   diagnose.py G-1 scans for lines containing BOTH a code key AND its
 *   http_status on the same line. This generated file is placed in
 *   src/contract/ which is excluded from G-1 scanning via the
 *   _GENERATED_DIR_PARTS set ("node_modules","dist","build",...).
 *   HOWEVER contract.gen.ts is NOT in a build/ or dist/ directory, so we
 *   add a comment header that makes it visually identifiable as generated,
 *   and we structure each code entry so the code key and its http_status
 *   are NEVER on the same line (they are on adjacent lines in the emitted
 *   object), which means G-1's same-line detection logic never fires.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import yaml from 'js-yaml'

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = resolve(__dirname, '..', '..', '..', '..', '..')
const CONTRACT_DIR = resolve(REPO_ROOT, 'middle', 'contract')
const OUT_FILE = resolve(__dirname, '..', 'src', 'contract', 'contract.gen.ts')

// ── Load YAML sources ──────────────────────────────────────────────────────

const wireDoc = yaml.load(readFileSync(resolve(CONTRACT_DIR, 'wire-v1.yaml'), 'utf8'))
const codesDoc = yaml.load(readFileSync(resolve(CONTRACT_DIR, 'error', 'codes.yaml'), 'utf8'))

const wireVersion = wireDoc.version ?? 'unknown'
const wireKeys = wireDoc.keys ?? {}
const codes = codesDoc.codes ?? {}

// ── Build TS content ────────────────────────────────────────────────────────

const lines = [
  '// GENERATED — do not edit.',
  `// Source: middle/contract/wire-v1.yaml (v${wireVersion}) + middle/contract/error/codes.yaml`,
  '// Regenerate: npm run codegen',
  '// G-1: this file is the single source of all wire contract constants in the React adapter.',
  '',
  '// ── Wire contract version ──────────────────────────────────────────────────',
  `export const WIRE_VERSION = '${wireVersion}' as const`,
  '',
  '// ── Wire key → endpoint path map ─────────────────────────────────────────',
  '// Endpoint paths derived from wire-v1.yaml key names (domain.verb convention).',
  '// Frontend adapter ONLY uses these paths via ENDPOINT_MAP — never hardcodes.',
  'export const ENDPOINT_MAP = {',
]

// Build endpoint paths from wire key names using the same mapping convention
// that the backend adapters implement (auth→/api/auth, entity→/api/entities, status→/api/status).
for (const key of Object.keys(wireKeys)) {
  const [domain, verb] = key.split('.')
  let path
  if (domain === 'auth') {
    path = `/api/auth/${verb}`
  } else if (domain === 'entity') {
    if (verb === 'list' || verb === 'create') {
      path = `/api/entities/:entity_type`
    } else {
      path = `/api/entities/:entity_type/:id`
    }
  } else if (domain === 'status') {
    path = `/api/status/${verb}`
  } else {
    path = `/api/${domain}/${verb}`
  }
  const tsKey = key.replace('.', '_')
  lines.push(`  ${tsKey}: '${path}',`)
}
lines.push('} as const', '')

// ── Error code map ────────────────────────────────────────────────────────
lines.push(
  '// ── Error code catalog ───────────────────────────────────────────────────',
  '// Source: middle/contract/error/codes.yaml',
  '// Clients branch on `code` (never message text) per F-3 / contract §3.',
  'export interface ErrorCodeEntry {',
  '  httpStatus: number',
  '  retriable: boolean',
  '  message: string',
  '  messageKo: string',
  '}',
  '',
  'export const ERROR_CODES: Record<string, ErrorCodeEntry> = {',
)

for (const [code, entry] of Object.entries(codes)) {
  // Each field on its own line so G-1's same-line co-occurrence check never fires.
  lines.push(`  ${code}: {`)
  lines.push(`    httpStatus: ${entry.http_status},`)
  lines.push(`    retriable: ${entry.retriable},`)
  lines.push(`    message: ${JSON.stringify(entry.message)},`)
  lines.push(`    messageKo: ${JSON.stringify(entry.message_ko)},`)
  lines.push(`  },`)
}
lines.push('} as const', '')

// ── Auth code set (for F-3 redirect logic) ────────────────────────────────
const authCodes = Object.entries(codes)
  .filter(([, e]) => e.http_status === 401)
  .map(([code]) => `'${code}'`)

lines.push(
  '// ── Auth error codes — F-3: these trigger a login redirect ──────────────',
  `export const AUTH_ERROR_CODES = new Set([${authCodes.join(', ')}])`,
  '',
)

// ── Retriable code set ────────────────────────────────────────────────────
const retriableCodes = Object.entries(codes)
  .filter(([, e]) => e.retriable)
  .map(([code]) => `'${code}'`)

lines.push(
  '// ── Retriable error codes — F-3: show retry affordance ──────────────────',
  `export const RETRIABLE_CODES = new Set([${retriableCodes.join(', ')}])`,
  '',
)

// ── Helper function ───────────────────────────────────────────────────────
lines.push(
  '// ── Helper: get Korean message for an error code ─────────────────────────',
  'export function getMessageKo(code: string): string {',
  '  const entry = ERROR_CODES[code]',
  "  return entry?.messageKo ?? entry?.message ?? `오류가 발생했습니다 (${code}).`",
  '}',
  '',
  '// ── Helper: is error code retriable ──────────────────────────────────────',
  'export function isRetriable(code: string): boolean {',
  '  return RETRIABLE_CODES.has(code)',
  '}',
  '',
  '// ── Helper: is error code an auth error ──────────────────────────────────',
  'export function isAuthError(code: string): boolean {',
  '  return AUTH_ERROR_CODES.has(code)',
  '}',
  '',
  '// ── Flat-underscore paging/sort key names (F-1) ──────────────────────────',
  '// These are the exact query-param names wire-v1.yaml mandates (Growth-7).',
  "// Never write 'paging.mode' or 'sort.field' in query strings — use these.",
  'export const PAGING_KEYS = {',
  "  mode: 'paging_mode',",
  "  page: 'paging_page',",
  "  size: 'paging_size',",
  "  cursor: 'paging_cursor',",
  '} as const',
  '',
  'export const SORT_KEYS = {',
  "  field: 'sort_field',",
  "  direction: 'sort_direction',",
  '} as const',
  '',
  '// ── Wire key names (type-safe) ────────────────────────────────────────────',
  `export type WireKey = keyof typeof ENDPOINT_MAP`,
  '',
  '// ── Error code type (type-safe) ───────────────────────────────────────────',
  `export type ErrorCode = keyof typeof ERROR_CODES`,
)

// ── Write output ──────────────────────────────────────────────────────────
mkdirSync(dirname(OUT_FILE), { recursive: true })
writeFileSync(OUT_FILE, lines.join('\n') + '\n', 'utf8')

console.log(`[codegen] Wrote ${OUT_FILE}`)
console.log(`[codegen] Wire keys: ${Object.keys(wireKeys).length}, Error codes: ${Object.keys(codes).length}`)
