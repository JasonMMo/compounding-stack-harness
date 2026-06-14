/**
 * codegen.mjs — Build-time contract codegen for landing-astro adapter (G-1).
 *
 * Reads:
 *   middle/contract/wire-v1.yaml
 *   middle/contract/error/codes.yaml
 *
 * Emits:
 *   src/lib/contract.gen.ts
 *
 * Focus: entity.create for contact form (DEC-5).
 * The generated module is the single source of wire contract constants.
 * No component may hardcode endpoint paths or entity_type values.
 *
 * G-1 / open-closed: middle contract is READ, not reimplemented.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import yaml from 'js-yaml'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ADAPTER_ROOT = resolve(__dirname, '..')
const REPO_ROOT = resolve(__dirname, '..', '..', '..', '..')
const CONTRACT_DIR = resolve(REPO_ROOT, 'middle', 'contract')
const OUT_FILE = resolve(ADAPTER_ROOT, 'src', 'lib', 'contract.gen.ts')

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
  '// G-1: single source of all wire contract constants in the landing-astro adapter.',
  '',
  '// ── Wire contract version ──────────────────────────────────────────────────',
  `export const WIRE_VERSION = '${wireVersion}' as const`,
  '',
  '// ── Wire key → endpoint path map ─────────────────────────────────────────',
  'export const ENDPOINT_MAP = {',
]

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

// ── entity.create request schema (contact form — DEC-5) ────────────────────
// Typed shape used by ContactForm component. Entity type is "lead".
lines.push(
  '// ── Lead contact form schema (DEC-5: entity.create with entity_type=lead) ──',
  '// Form fields per site-manifest contact.fields: [name, email, message].',
  'export interface LeadData {',
  '  name: string',
  '  email: string',
  '  message: string',
  '}',
  '',
  'export interface EntityCreateRequest {',
  '  entity_type: string',
  '  data: Record<string, unknown>',
  '}',
  '',
  'export interface EntityCreateResponse {',
  '  entity_type: string',
  '  id: string',
  '  data: Record<string, unknown>',
  '  error?: { code: string; message: string; details?: unknown }',
  '}',
  '',
  '// Contact form POST helper — builds entity.create request for lead capture.',
  '// Resolves endpoint from ENDPOINT_MAP["entity_create"] with entity_type=lead.',
  "export const LEAD_ENTITY_TYPE = 'lead' as const",
  '',
)

// ── Error code map ────────────────────────────────────────────────────────
lines.push(
  '// ── Error code catalog ───────────────────────────────────────────────────',
  'export interface ErrorCodeEntry {',
  '  httpStatus: number',
  '  retriable: boolean',
  '  message: string',
  '}',
  '',
  'export const ERROR_CODES: Record<string, ErrorCodeEntry> = {',
)

for (const [code, entry] of Object.entries(codes)) {
  lines.push(`  ${code}: {`)
  lines.push(`    httpStatus: ${entry.http_status},`)
  lines.push(`    retriable: ${entry.retriable},`)
  lines.push(`    message: ${JSON.stringify(entry.message)},`)
  lines.push(`  },`)
}
lines.push('} as const', '')

lines.push(
  '// ── Wire key type ─────────────────────────────────────────────────────────',
  'export type WireKey = keyof typeof ENDPOINT_MAP',
  '',
  '// ── Error code type ───────────────────────────────────────────────────────',
  'export type ErrorCode = keyof typeof ERROR_CODES',
)

// ── Write output ──────────────────────────────────────────────────────────
mkdirSync(dirname(OUT_FILE), { recursive: true })
writeFileSync(OUT_FILE, lines.join('\n') + '\n', 'utf8')

console.log(`[codegen] Wrote ${OUT_FILE}`)
console.log(`[codegen] Wire keys: ${Object.keys(wireKeys).length}, Error codes: ${Object.keys(codes).length}`)
