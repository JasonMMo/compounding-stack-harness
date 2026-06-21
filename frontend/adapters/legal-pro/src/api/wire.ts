/**
 * wire.ts — Typed fetch layer for legal-rag backend.
 *
 * Endpoints are imported from contract.gen.ts (codegen from legal-rag paths).
 * Error handling follows F-3: branch on error code, display messageKo.
 * Auth errors clear token (via clearToken from App).
 *
 * NOTE: This adapter does NOT use the generic wire-v1.yaml entity endpoints.
 * The legal-rag service has its own REST paths (/auth/login, /search, etc.)
 * that are emitted into LEGAL_RAG_ENDPOINTS by scripts/codegen.mjs.
 */

import {
  LEGAL_RAG_ENDPOINTS,
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
}

export interface WireResult<T> {
  data: T | null
  error: WireError | null
}

// Auth
export interface LoginResponse {
  access_token: string
  display_name: string
  attorney_id: string
}

// Search
export interface CitationOut {
  chunk_id: string
  chunk_index: number
  source_type: 'precedent' | 'case_document'
  source_id: string
  // Precedent fields
  court?: string | null
  case_number?: string | null
  decision_date?: string | null
  citation?: string | null
  holding_summary?: string | null
  // Case-document fields
  document_type?: string | null
  document_title?: string | null
  // Common
  chunk_text_excerpt: string
  rrf_score: number
  relevance?: number | null   // 0.0–1.0; display as Math.round(relevance*100)%
  fts_rank?: number | null
  ann_rank?: number | null
}

export interface SearchResponse {
  results: CitationOut[]
  note?: string | null
}

export interface SearchRequest {
  query: string
  top_k?: number
  match_mode?: 'or' | 'and'
  case_id?: string | null
}

// Health
export interface HealthResponse {
  status: 'ok' | 'degraded' | 'down'
  db_pool?: string
  embed_sidecar?: string
}

// Cases — list
export interface CaseSummary {
  case_id: string
  case_number: string
  title: string
  status: string
  doc_total: number
  doc_indexed: number
  doc_pending: number
  doc_failed: number
}

export interface CasesResponse {
  cases: CaseSummary[]
  total: number
  limit: number
  offset: number
}

// Cases — detail
export interface CaseDocumentItem {
  doc_id: string
  title: string | null
  document_type: string | null
  ingest_status: string | null
}

export interface CaseDetailResponse {
  case_id: string
  case_number: string
  title: string
  status: string
  case_type: string | null
  description: string | null
  opened_at: string | null
  closed_at: string | null
  documents: CaseDocumentItem[]
}

// ── Core request ──────────────────────────────────────────────────────────

async function legalRequest<T>(
  method: string,
  path: string,
  options: { body?: unknown } = {},
): Promise<WireResult<T>> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  let response: Response
  try {
    response = await fetch(path, {
      method,
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    })
  } catch {
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

  // 429 rate-limit — surface dedicated message
  if (response.status === 429) {
    return {
      data: null,
      error: {
        code: 'RATE_LIMITED',
        messageKo: '요청이 너무 많습니다. 잠시 후 다시 시도하세요.',
        retriable: true,
        isAuth: false,
      },
    }
  }

  // 503 — sidecar / embedding service down
  if (response.status === 503) {
    return {
      data: null,
      error: {
        code: 'SIDECAR_DOWN',
        messageKo: '검색 서비스가 일시적으로 이용 불가합니다. IT 담당자에게 문의하세요.',
        retriable: false,
        isAuth: false,
      },
    }
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

  // F-3: branch on error.code or HTTP error
  const errEnv = payload['detail'] as string | Record<string, unknown> | null | undefined
  if (!response.ok) {
    // FastAPI returns "detail" for error messages
    let code = 'INTERNAL'
    let koMsg = getMessageKo(code)
    if (response.status === 401) {
      code = 'UNAUTHORIZED'
      koMsg = '인증이 만료되었습니다. 다시 로그인하세요.'
      clearToken()
    } else if (typeof errEnv === 'string') {
      koMsg = errEnv
    }
    return {
      data: null,
      error: {
        code,
        messageKo: koMsg,
        retriable: isRetriable(code),
        isAuth: isAuthError(code),
      },
    }
  }

  // Check wire-protocol error envelope (error.code path for generic contract errors)
  const wireErr = payload['error'] as Record<string, unknown> | null | undefined
  if (wireErr && wireErr['code']) {
    const code = String(wireErr['code'])
    if (isAuthError(code)) clearToken()
    return {
      data: null,
      error: {
        code,
        messageKo: getMessageKo(code),
        retriable: isRetriable(code),
        isAuth: isAuthError(code),
      },
    }
  }

  return { data: payload as T, error: null }
}

// ── Public API ─────────────────────────────────────────────────────────────

export async function apiLogin(
  email: string,
  password: string,
): Promise<WireResult<LoginResponse>> {
  return legalRequest<LoginResponse>('POST', LEGAL_RAG_ENDPOINTS.auth_login, {
    body: { email, password },
  })
}

export async function apiSearch(req: SearchRequest): Promise<WireResult<SearchResponse>> {
  return legalRequest<SearchResponse>('POST', LEGAL_RAG_ENDPOINTS.search, { body: req })
}

export async function apiHealth(): Promise<WireResult<HealthResponse>> {
  return legalRequest<HealthResponse>('GET', LEGAL_RAG_ENDPOINTS.health)
}

export async function apiListCases(
  limit: number,
  offset: number,
): Promise<WireResult<CasesResponse>> {
  const url = `${LEGAL_RAG_ENDPOINTS.cases_list}?limit=${limit}&offset=${offset}`
  return legalRequest<CasesResponse>('GET', url)
}

export async function apiGetCase(caseId: string): Promise<WireResult<CaseDetailResponse>> {
  const url = LEGAL_RAG_ENDPOINTS.case_read.replace(':case_id', encodeURIComponent(caseId))
  return legalRequest<CaseDetailResponse>('GET', url)
}

// ── G-2 C1 — 사건 생성/수정 타입 및 API ─────────────────────────────────────

// DDL CHECK 기준 (hsqldb-schema.sql):
//   case_type: civil | criminal | administrative | family | commercial  (other 없음)
//   status:    intake | active | trial | appeal | closed | withdrawn
export type CaseType = 'civil' | 'criminal' | 'administrative' | 'family' | 'commercial'
export type CaseStatus = 'intake' | 'active' | 'trial' | 'appeal' | 'closed' | 'withdrawn'

export interface CaseCreateIn {
  case_number: string
  title: string
  case_type?: CaseType | null
  status?: CaseStatus
  description?: string | null
  opened_at?: string | null
}

export interface CaseUpdateIn {
  title?: string | null
  case_type?: CaseType | null
  status?: CaseStatus | null
  description?: string | null
  opened_at?: string | null
  closed_at?: string | null
}

export async function apiCreateCase(body: CaseCreateIn): Promise<WireResult<CaseSummary>> {
  return legalRequest<CaseSummary>('POST', LEGAL_RAG_ENDPOINTS.case_create, { body })
}

export async function apiUpdateCase(
  caseId: string,
  body: CaseUpdateIn,
): Promise<WireResult<CaseDetailResponse>> {
  const url = LEGAL_RAG_ENDPOINTS.case_update.replace(':case_id', encodeURIComponent(caseId))
  return legalRequest<CaseDetailResponse>('PATCH', url, { body })
}
