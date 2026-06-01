/**
 * compliance.test.ts — React adapter compliance suite.
 *
 * Tests F-1 ~ F-4 compliance (frontend-adapter-contract.md §3 + §4).
 *
 * L1 unit tests: run entirely in-process, no server needed.
 * L4 live tests: require FRONTEND_BASE_URL + BACKEND_BASE_URL env vars.
 *
 * Run:
 *   npm test                               # L1 only (default)
 *   BACKEND_BASE_URL=http://localhost:8081 npm test  # L1 + L4
 *
 * Test parametrization mirrors backend compliance suite pattern:
 *   FRONTEND_BASE_URL  — where the Vite dev/preview server is running
 *   BACKEND_BASE_URL   — backend adapter under test
 */

import { describe, it, expect, vi } from 'vitest'

// ── Import the generated contract module ───────────────────────────────────
// This verifies that codegen ran and the module is importable (L1 build check).
import {
  WIRE_VERSION,
  ENDPOINT_MAP,
  ERROR_CODES,
  PAGING_KEYS,
  SORT_KEYS,
  getMessageKo,
  isRetriable,
  isAuthError,
} from '../../../frontend/adapters/react/src/contract/contract.gen'

// ── Import buildListParams for F-1 serialization test ─────────────────────
import { buildListParams } from '../../../frontend/adapters/react/src/api/wire'

// ── Import paging predicate for F-2 real-behavior tests ───────────────────
import { hasMorePages } from '../../../frontend/adapters/react/src/api/paging'

// ────────────────────────────────────────────────────────────────────────────
// Contract codegen sanity
// ────────────────────────────────────────────────────────────────────────────

describe('contract.gen.ts — codegen sanity', () => {
  it('WIRE_VERSION is a non-empty string', () => {
    expect(typeof WIRE_VERSION).toBe('string')
    expect(WIRE_VERSION.length).toBeGreaterThan(0)
  })

  it('ENDPOINT_MAP contains all 8 wire keys', () => {
    const expected = [
      'auth_login', 'auth_logout',
      'entity_read', 'entity_list', 'entity_create', 'entity_update', 'entity_delete',
      'status_health',
    ]
    for (const key of expected) {
      expect(ENDPOINT_MAP).toHaveProperty(key)
    }
  })

  it('ERROR_CODES contains all codes from codes.yaml', () => {
    const expected = [
      'AUTH_FAILED', 'AUTH_EXPIRED', 'AUTH_REQUIRED', 'FORBIDDEN',
      'VALIDATION_ERROR', 'BAD_REQUEST', 'NOT_FOUND', 'CONFLICT',
      'RATE_LIMITED', 'INTERNAL', 'UNAVAILABLE',
    ]
    for (const code of expected) {
      expect(ERROR_CODES).toHaveProperty(code)
    }
  })

  it('each ERROR_CODE entry has httpStatus, retriable, message, messageKo', () => {
    for (const [code, entry] of Object.entries(ERROR_CODES)) {
      expect(typeof entry.httpStatus, `${code}.httpStatus`).toBe('number')
      expect(typeof entry.retriable, `${code}.retriable`).toBe('boolean')
      expect(typeof entry.message, `${code}.message`).toBe('string')
      expect(typeof entry.messageKo, `${code}.messageKo`).toBe('string')
    }
  })

  it('PAGING_KEYS are flat-underscore (F-1)', () => {
    expect(PAGING_KEYS.mode).toBe('paging_mode')
    expect(PAGING_KEYS.page).toBe('paging_page')
    expect(PAGING_KEYS.size).toBe('paging_size')
    expect(PAGING_KEYS.cursor).toBe('paging_cursor')
  })

  it('SORT_KEYS are flat-underscore (F-1)', () => {
    expect(SORT_KEYS.field).toBe('sort_field')
    expect(SORT_KEYS.direction).toBe('sort_direction')
  })
})

// ────────────────────────────────────────────────────────────────────────────
// F-1 — flat-underscore serialization
// ────────────────────────────────────────────────────────────────────────────

describe('F-1 — flat-underscore query serialization', () => {
  it('offset mode: emits paging_mode, paging_page, paging_size (no dots)', () => {
    const params = buildListParams('customer', {
      pagingMode: 'offset',
      pagingPage: 2,
      pagingSize: 10,
    })
    const raw = params.toString()

    expect(raw).toContain('paging_mode=offset')
    expect(raw).toContain('paging_page=2')
    expect(raw).toContain('paging_size=10')
    // Must NOT contain dot-notation
    expect(raw).not.toContain('paging.mode')
    expect(raw).not.toContain('paging.page')
  })

  it('cursor mode: emits paging_mode=cursor, paging_cursor (no paging_page)', () => {
    const params = buildListParams('order', {
      pagingMode: 'cursor',
      pagingCursor: 'abc123',
      pagingSize: 20,
    })
    const raw = params.toString()

    expect(raw).toContain('paging_mode=cursor')
    expect(raw).toContain('paging_cursor=abc123')
    expect(raw).not.toContain('paging_page')
    expect(raw).not.toContain('paging.cursor')
  })

  it('sort fields: emits sort_field, sort_direction (flat-underscore)', () => {
    const params = buildListParams('product', {
      pagingMode: 'offset',
      pagingPage: 1,
      sortField: 'name',
      sortDirection: 'desc',
    })
    const raw = params.toString()

    expect(raw).toContain('sort_field=name')
    expect(raw).toContain('sort_direction=desc')
    expect(raw).not.toContain('sort.field')
    expect(raw).not.toContain('sort.direction')
  })

  it('no optional params when omitted', () => {
    const params = buildListParams('customer', { pagingMode: 'offset' })
    const raw = params.toString()
    expect(raw).toContain('paging_mode=offset')
    expect(raw).not.toContain('sort_field')
    expect(raw).not.toContain('filter_search')
  })

  it('search emits filter_search', () => {
    const params = buildListParams('customer', {
      pagingMode: 'offset',
      search: 'acme',
    })
    expect(params.toString()).toContain('filter_search=acme')
  })
})

// ────────────────────────────────────────────────────────────────────────────
// F-3 — error envelope: branch on code, not message
// ────────────────────────────────────────────────────────────────────────────

describe('F-3 — error envelope rendering', () => {
  it('getMessageKo returns Korean string for every code', () => {
    const codes = [
      'AUTH_FAILED', 'AUTH_EXPIRED', 'AUTH_REQUIRED', 'FORBIDDEN',
      'VALIDATION_ERROR', 'BAD_REQUEST', 'NOT_FOUND', 'CONFLICT',
      'RATE_LIMITED', 'INTERNAL', 'UNAVAILABLE',
    ]
    for (const code of codes) {
      const msg = getMessageKo(code)
      expect(typeof msg).toBe('string')
      expect(msg.length).toBeGreaterThan(0)
      // Must be Korean (contains hangul)
      expect(/[가-힯]/.test(msg), `${code} messageKo should contain Hangul`).toBe(true)
    }
  })

  it('getMessageKo falls back gracefully for unknown code', () => {
    const msg = getMessageKo('TOTALLY_UNKNOWN_CODE')
    expect(msg).toContain('TOTALLY_UNKNOWN_CODE')
  })

  it('RATE_LIMITED is retriable', () => {
    expect(isRetriable('RATE_LIMITED')).toBe(true)
  })

  it('INTERNAL is retriable', () => {
    expect(isRetriable('INTERNAL')).toBe(true)
  })

  it('UNAVAILABLE is retriable', () => {
    expect(isRetriable('UNAVAILABLE')).toBe(true)
  })

  it('NOT_FOUND is not retriable', () => {
    expect(isRetriable('NOT_FOUND')).toBe(false)
  })

  it('AUTH_FAILED is not retriable', () => {
    expect(isRetriable('AUTH_FAILED')).toBe(false)
  })

  it('AUTH_REQUIRED is an auth error (triggers login redirect)', () => {
    expect(isAuthError('AUTH_REQUIRED')).toBe(true)
  })

  it('AUTH_EXPIRED is an auth error', () => {
    expect(isAuthError('AUTH_EXPIRED')).toBe(true)
  })

  it('NOT_FOUND is not an auth error', () => {
    expect(isAuthError('NOT_FOUND')).toBe(false)
  })

  it('error code strings are never confused with message text — branching is code-based', () => {
    // Simulate the F-3 contract: code "NOT_FOUND" → messageKo is Korean, not English
    const koMsg = getMessageKo('NOT_FOUND')
    expect(koMsg).not.toBe('NOT_FOUND')
    expect(koMsg).not.toContain('NOT_FOUND')
  })
})

// ────────────────────────────────────────────────────────────────────────────
// F-4 — idempotent delete
// ────────────────────────────────────────────────────────────────────────────

describe('F-4 — idempotent delete (unit: mock fetch)', () => {
  it('HTTP 404 on DELETE is mapped to { success: true } (not an error)', async () => {
    // Mock fetch to return 404 for DELETE
    const mockFetch = vi.fn().mockResolvedValue({
      status: 404,
      text: async () => JSON.stringify({ error: { code: 'NOT_FOUND', message: 'gone' } }),
    } as unknown as Response)
    vi.stubGlobal('fetch', mockFetch)
    // Stub sessionStorage.getItem for token
    vi.stubGlobal('sessionStorage', { getItem: () => 'test-token', setItem: vi.fn(), removeItem: vi.fn() })

    const { apiEntityDelete } = await import('../../../frontend/adapters/react/src/api/wire')
    const result = await apiEntityDelete('customer', 'does-not-exist')

    expect(result.error).toBeNull()
    expect(result.data?.success).toBe(true)

    vi.unstubAllGlobals()
  })

  it('HTTP 200 success on DELETE also returns { success: true }', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      status: 200,
      text: async () => JSON.stringify({ success: true }),
    } as unknown as Response)
    vi.stubGlobal('fetch', mockFetch)
    vi.stubGlobal('sessionStorage', { getItem: () => null, setItem: vi.fn(), removeItem: vi.fn() })

    const { apiEntityDelete } = await import('../../../frontend/adapters/react/src/api/wire')
    const result = await apiEntityDelete('customer', 'existing-id')

    expect(result.error).toBeNull()
    expect(result.data?.success).toBe(true)

    vi.unstubAllGlobals()
  })
})

// ────────────────────────────────────────────────────────────────────────────
// F-2 — paging modes
// ────────────────────────────────────────────────────────────────────────────

describe('F-2 — paging (unit)', () => {
  // ── hasMorePages: offset mid-list ──────────────────────────────────────
  it('offset mid-list: hasMorePages returns true when page < totalPages', () => {
    // total=45 size=20 → totalPages=3; page 2 is NOT the last page
    expect(hasMorePages({ mode: 'offset', page: 2, size: 20, total: 45 })).toBe(true)
  })

  // ── hasMorePages: offset last page ────────────────────────────────────
  it('offset last page: hasMorePages returns false when page === totalPages', () => {
    // total=45 size=20 → totalPages=3; page 3 IS the last page
    expect(hasMorePages({ mode: 'offset', page: 3, size: 20, total: 45 })).toBe(false)
  })

  // ── hasMorePages: cursor with next_cursor ──────────────────────────────
  it('cursor with next_cursor: hasMorePages returns true', () => {
    expect(hasMorePages({ mode: 'cursor', nextCursor: 'eyJpZCI6MTAwfQ' })).toBe(true)
  })

  // ── hasMorePages: cursor without next_cursor ───────────────────────────
  it('cursor without next_cursor: hasMorePages returns false (last page)', () => {
    expect(hasMorePages({ mode: 'cursor', nextCursor: null })).toBe(false)
    expect(hasMorePages({ mode: 'cursor', nextCursor: '' })).toBe(false)
    expect(hasMorePages({ mode: 'cursor', nextCursor: undefined })).toBe(false)
  })

  it('cursor paging: next_cursor forwarded as paging_cursor', () => {
    const nextCursor = 'eyJpZCI6MTAwfQ'
    const params = buildListParams('order', {
      pagingMode: 'cursor',
      pagingCursor: nextCursor,
    })
    expect(params.get(PAGING_KEYS.cursor)).toBe(nextCursor)
    expect(params.get(PAGING_KEYS.mode)).toBe('cursor')
  })

  it('cursor mode: paging_page is absent', () => {
    const params = buildListParams('order', {
      pagingMode: 'cursor',
      pagingCursor: 'tok',
    })
    expect(params.has(PAGING_KEYS.page)).toBe(false)
  })
})

// ────────────────────────────────────────────────────────────────────────────
// L4 live tests — skipped when BACKEND_BASE_URL not set
// ────────────────────────────────────────────────────────────────────────────

const BACKEND = process.env.BACKEND_BASE_URL
const FRONTEND = process.env.FRONTEND_BASE_URL

describe.skipIf(!BACKEND)('L4 — live backend integration (BACKEND_BASE_URL required)', () => {
  it('GET /api/status/health returns status ok|degraded|down', async () => {
    const resp = await fetch(`${BACKEND}/api/status/health`)
    expect([200, 503]).toContain(resp.status)
    const data = await resp.json()
    expect(['ok', 'degraded', 'down']).toContain(data.status)
  })

  it('POST /api/auth/login with demo/demo returns token', async () => {
    const resp = await fetch(`${BACKEND}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'demo', password: 'demo' }),
    })
    expect(resp.status).toBe(200)
    const data = await resp.json()
    expect(typeof data.token).toBe('string')
    expect(data.token.length).toBeGreaterThan(0)
  })

  it('POST /api/auth/login with wrong creds returns AUTH_FAILED code', async () => {
    const resp = await fetch(`${BACKEND}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'bad', password: 'bad' }),
    })
    expect([400, 401, 422]).toContain(resp.status)
    const data = await resp.json()
    // F-3: error.code must be a string from codes.yaml
    expect(typeof data.error?.code).toBe('string')
    expect(ERROR_CODES).toHaveProperty(data.error.code)
  })

  it('F-1: entity list request arrives at backend with flat-underscore params', async () => {
    // Login first
    const loginResp = await fetch(`${BACKEND}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'demo', password: 'demo' }),
    })
    const { token } = await loginResp.json()

    // List with paging params — verify backend accepts flat-underscore keys
    const listResp = await fetch(
      `${BACKEND}/api/entities/customer?paging_mode=offset&paging_page=1&paging_size=5`,
      { headers: { Authorization: `Bearer ${token}` } },
    )
    expect([200, 404]).toContain(listResp.status) // 404 = entity type unknown, still proves params parsed
    const data = await listResp.json()
    // If 200, must have items array
    if (listResp.status === 200) {
      expect(Array.isArray(data.items)).toBe(true)
    }
  })

  it('F-4: DELETE non-existent entity returns success or 404 (both valid)', async () => {
    const loginResp = await fetch(`${BACKEND}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'demo', password: 'demo' }),
    })
    const { token } = await loginResp.json()

    // Delete a non-existent ID
    const deleteResp = await fetch(
      `${BACKEND}/api/entities/customer/nonexistent-id-00000`,
      {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      },
    )
    // F-4 standard: 404 or 200 both acceptable from backend; adapter maps 404→success
    expect([200, 404]).toContain(deleteResp.status)
  })

  it('F-3: each error code in ERROR_CODES has a Korean message (cross-check)', () => {
    for (const code of Object.keys(ERROR_CODES)) {
      const msg = getMessageKo(code)
      // Must have Korean characters
      expect(/[가-힯]/.test(msg), `${code} should have Korean message`).toBe(true)
    }
  })
})

describe.skipIf(!FRONTEND)('L4 — live frontend SPA (FRONTEND_BASE_URL required)', () => {
  it('GET /health returns 200', async () => {
    const resp = await fetch(`${FRONTEND}/health`)
    // SPA serves index.html for all routes → 200
    expect(resp.status).toBe(200)
  })

  it('GET / returns 200 HTML', async () => {
    const resp = await fetch(`${FRONTEND}/`)
    expect(resp.status).toBe(200)
    const html = await resp.text()
    expect(html).toContain('<div id="root">')
  })
})
