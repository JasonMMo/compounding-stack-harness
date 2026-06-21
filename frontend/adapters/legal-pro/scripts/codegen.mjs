/**
 * codegen.mjs — legal-pro adapter contract codegen.
 *
 * Reads:  middle/contract/error/codes.yaml  (shared error catalog)
 *
 * Emits:  src/contract/contract.gen.ts
 *
 * NOTE: The legal-rag service does NOT use the generic wire-v1.yaml entity
 * endpoints. Its own endpoints (/auth/login, /search, /health, /documents,
 * /cases) are defined in this script as LEGAL_RAG_ENDPOINTS — these are the
 * actual paths the live service exposes. The generic ENDPOINT_MAP is omitted
 * from this adapter to avoid confusion; only legal-rag paths are exported.
 *
 * Error codes from codes.yaml are still emitted for F-3 compliance (error
 * envelope branching on code, Korean message display).
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import yaml from 'js-yaml'

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = resolve(__dirname, '..', '..', '..', '..')
const CONTRACT_DIR = resolve(REPO_ROOT, 'middle', 'contract')
const OUT_FILE = resolve(__dirname, '..', 'src', 'contract', 'contract.gen.ts')

// ── Load shared error codes ────────────────────────────────────────────────
const codesDoc = yaml.load(readFileSync(resolve(CONTRACT_DIR, 'error', 'codes.yaml'), 'utf8'))
const codes = codesDoc.codes ?? {}

// ── Legal-rag service endpoint map ────────────────────────────────────────
// These paths are the live legal-rag service's HTTP API (not wire-v1.yaml generic paths).
const LEGAL_RAG_ENDPOINTS = {
  auth_login:    '/auth/login',
  auth_logout:   '/auth/logout',
  search:        '/search',
  health:        '/health',
  document_read: '/documents/:source_type/:source_id',
  cases_list:    '/cases',
  case_read:     '/cases/:case_id',
}

// ── Build TS content ────────────────────────────────────────────────────────
const lines = [
  '// GENERATED — do not edit.',
  '// Source: legal-pro adapter codegen (scripts/codegen.mjs)',
  '// Error codes: middle/contract/error/codes.yaml',
  '// Regenerate: npm run codegen',
  '',
  '// ── Legal-RAG service endpoint paths ─────────────────────────────────────',
  '// These are the live paths exposed by services/legal-rag (FastAPI).',
  '// Do NOT use ENDPOINT_MAP from the generic react adapter here — wrong paths.',
  'export const LEGAL_RAG_ENDPOINTS = {',
]

for (const [key, path] of Object.entries(LEGAL_RAG_ENDPOINTS)) {
  lines.push(`  ${key}: '${path}',`)
}
lines.push('} as const', '')

// ── Error code map ────────────────────────────────────────────────────────
lines.push(
  '// ── Error code catalog (shared) ─────────────────────────────────────────',
  '// Source: middle/contract/error/codes.yaml',
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
  lines.push(`  ${code}: {`)
  lines.push(`    httpStatus: ${entry.http_status},`)
  lines.push(`    retriable: ${entry.retriable},`)
  lines.push(`    message: ${JSON.stringify(entry.message)},`)
  lines.push(`    messageKo: ${JSON.stringify(entry.message_ko)},`)
  lines.push(`  },`)
}
lines.push('} as const', '')

// ── Auth code set ────────────────────────────────────────────────────────
const authCodes = Object.entries(codes)
  .filter(([, e]) => e.http_status === 401)
  .map(([code]) => `'${code}'`)

lines.push(
  '// ── Auth error codes — F-3: these trigger login redirect ────────────────',
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

// ── Helpers ───────────────────────────────────────────────────────────────
lines.push(
  '// ── Helper: Korean message for an error code ─────────────────────────────',
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
)

// ── Write output ──────────────────────────────────────────────────────────
mkdirSync(dirname(OUT_FILE), { recursive: true })
writeFileSync(OUT_FILE, lines.join('\n') + '\n', 'utf8')

console.log(`[codegen] Wrote ${OUT_FILE}`)
console.log(`[codegen] Error codes: ${Object.keys(codes).length}`)
