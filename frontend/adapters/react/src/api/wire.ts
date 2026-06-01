/**
 * wire.ts — Typed fetch layer for wire-protocol requests.
 *
 * All HTTP transport goes through this module. Wire keys, endpoint paths,
 * error codes, and flat-underscore paging key names are imported ONLY from
 * contract.gen.ts (G-1: single source of truth).
 *
 * F-1: flat-underscore serialization enforced by buildListParams().
 * F-3: error envelope branching on error.code, messageKo from generated map.
 * F-4: DELETE 404 → success (idempotent delete mapping).
 */

import {
  ENDPOINT_MAP,
  PAGING_KEYS,
  SORT_KEYS,
  getMessageKo,
  isRetriable,
  isAuthError,
} from '../contract/contract.gen'
import { getToken, clearToken } from '../App'

// ── Types ──────────────────────────────────────────────────────────────────

export interface WireError {
  code: string
  messageKo: string
  retriable: boolean
  isAuth: boolean
  details?: Record<string, unknown>
}

export interface WireResult<T> {
  data: T | null
  error: WireError | null
}

export interface ListParams {
  pagingMode?: 'offset' | 'cursor'
  pagingPage?: number
  pagingSize?: number
  pagingCursor?: string
  sortField?: string
  sortDirection?: 'asc' | 'desc'
  search?: string
}

export interface ListResponse {
  entity_type: string
  items: Record<string, unknown>[]
  total?: number
  next_cursor?: string
}

export interface EntityResponse {
  entity_type: string
  id: string
  data: Record<string, unknown>
}

export interface DeleteResponse {
  success: boolean
}

export interface LoginResponse {
  token: string
  expires_at: string
  user_id: string
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'down'
  version: string
  checks?: Array<{ name: string; status: string; message?: string }>
}

// ── URL builder helpers ─────────────────────────────────────────────────────

function resolveEntityPath(
  template: string,
  entityType: string,
  entityId?: string,
): string {
  let path = template.replace(':entity_type', entityType)
  if (entityId !== undefined) {
    path = path.replace(':id', entityId)
  }
  return path
}

/**
 * buildListParams — F-1 flat-underscore serialization.
 *
 * Converts structured paging/sort params to the flat-underscore key names
 * mandated by wire-v1.yaml (Growth-7). Never uses dot notation in query strings.
 */
export function buildListParams(
  entityType: string,
  params: ListParams,
): URLSearchParams {
  const p = new URLSearchParams()
  p.set('entity_type', entityType)

  const mode = params.pagingMode ?? 'offset'
  p.set(PAGING_KEYS.mode, mode)

  if (mode === 'offset') {
    if (params.pagingPage !== undefined) p.set(PAGING_KEYS.page, String(params.pagingPage))
    if (params.pagingSize !== undefined) p.set(PAGING_KEYS.size, String(params.pagingSize))
  } else if (mode === 'cursor') {
    if (params.pagingCursor) p.set(PAGING_KEYS.cursor, params.pagingCursor)
    if (params.pagingSize !== undefined) p.set(PAGING_KEYS.size, String(params.pagingSize))
  }

  if (params.sortField) {
    p.set(SORT_KEYS.field, params.sortField)
    p.set(SORT_KEYS.direction, params.sortDirection ?? 'asc')
  }

  if (params.search) {
    p.set('filter_search', params.search)
  }

  return p
}

// ── Core request function ───────────────────────────────────────────────────

async function wireRequest<T>(
  method: string,
  path: string,
  options: {
    params?: URLSearchParams
    body?: unknown
    isDelete?: boolean
  } = {},
): Promise<WireResult<T>> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  let url = path
  if (options.params) {
    url = `${path}?${options.params.toString()}`
  }

  let response: Response
  try {
    response = await fetch(url, {
      method,
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    })
  } catch (networkErr) {
    return {
      data: null,
      error: {
        code: 'UNAVAILABLE',
        messageKo: getMessageKo('UNAVAILABLE'),
        retriable: isRetriable('UNAVAILABLE'),
        isAuth: false,
      },
    }
  }

  // F-4: idempotent delete — 404 on DELETE → success
  if (options.isDelete && response.status === 404) {
    return { data: { success: true } as unknown as T, error: null }
  }

  let payload: Record<string, unknown> = {}
  try {
    const text = await response.text()
    if (text) payload = JSON.parse(text)
  } catch {
    return {
      data: null,
      error: {
        code: 'INTERNAL',
        messageKo: getMessageKo('INTERNAL'),
        retriable: isRetriable('INTERNAL'),
        isAuth: false,
      },
    }
  }

  // F-3: branch on error.code (never message text)
  const errEnv = payload['error'] as Record<string, unknown> | null | undefined
  if (errEnv && errEnv['code']) {
    const code = String(errEnv['code'])
    // Auth errors — clear token
    if (isAuthError(code)) {
      clearToken()
    }
    return {
      data: null,
      error: {
        code,
        messageKo: getMessageKo(code),
        retriable: isRetriable(code),
        isAuth: isAuthError(code),
        details: errEnv['details'] as Record<string, unknown> | undefined,
      },
    }
  }

  return { data: payload as T, error: null }
}

// ── Public API ─────────────────────────────────────────────────────────────

export async function apiLogin(
  username: string,
  password: string,
  rememberMe = false,
): Promise<WireResult<LoginResponse>> {
  return wireRequest<LoginResponse>('POST', ENDPOINT_MAP.auth_login, {
    body: { username, password, remember_me: rememberMe },
  })
}

export async function apiLogout(token: string): Promise<void> {
  await wireRequest('POST', ENDPOINT_MAP.auth_logout, { body: { token } })
}

export async function apiEntityList(
  entityType: string,
  params: ListParams,
): Promise<WireResult<ListResponse>> {
  const searchParams = buildListParams(entityType, params)
  const path = resolveEntityPath(ENDPOINT_MAP.entity_list, entityType)
  return wireRequest<ListResponse>('GET', path, { params: searchParams })
}

export async function apiEntityRead(
  entityType: string,
  id: string,
): Promise<WireResult<EntityResponse>> {
  const path = resolveEntityPath(ENDPOINT_MAP.entity_read, entityType, id)
  return wireRequest<EntityResponse>('GET', path)
}

export async function apiEntityCreate(
  entityType: string,
  data: Record<string, unknown>,
): Promise<WireResult<EntityResponse>> {
  const path = resolveEntityPath(ENDPOINT_MAP.entity_create, entityType)
  return wireRequest<EntityResponse>('POST', path, {
    body: { entity_type: entityType, data },
  })
}

export async function apiEntityUpdate(
  entityType: string,
  id: string,
  data: Record<string, unknown>,
): Promise<WireResult<EntityResponse>> {
  const path = resolveEntityPath(ENDPOINT_MAP.entity_update, entityType, id)
  return wireRequest<EntityResponse>('PATCH', path, {
    body: { entity_type: entityType, id, data },
  })
}

export async function apiEntityDelete(
  entityType: string,
  id: string,
): Promise<WireResult<DeleteResponse>> {
  const path = resolveEntityPath(ENDPOINT_MAP.entity_delete, entityType, id)
  // isDelete: true triggers F-4 mapping (404 → success)
  return wireRequest<DeleteResponse>('DELETE', path, { isDelete: true })
}

export async function apiHealthCheck(): Promise<WireResult<HealthResponse>> {
  return wireRequest<HealthResponse>('GET', ENDPOINT_MAP.status_health)
}
