import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import LoginScreen from './screens/LoginScreen'
import PrecedentSearchScreen from './screens/PrecedentSearchScreen'

// ── Auth token helpers (sessionStorage — clears on tab close) ─────────────
const TOKEN_KEY = 'lp_token'
const DISPLAY_KEY = 'lp_display_name'

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string, displayName?: string): void {
  sessionStorage.setItem(TOKEN_KEY, token)
  if (displayName) sessionStorage.setItem(DISPLAY_KEY, displayName)
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(DISPLAY_KEY)
}

export function getDisplayName(): string {
  return sessionStorage.getItem(DISPLAY_KEY) ?? ''
}

// ── Auth guard ─────────────────────────────────────────────────────────────

function RequireAuth({ children }: { children: React.ReactNode }) {
  if (!getToken()) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

// ── App shell ──────────────────────────────────────────────────────────────

export default function App() {
  const navigate = useNavigate()
  // displayName is held in state so header re-renders after login
  const [displayName, setDisplayNameState] = useState<string>(getDisplayName())

  function handleLoginSuccess(token: string, name: string) {
    setToken(token, name)
    setDisplayNameState(name)
    navigate('/search', { replace: true })
  }

  function handleLogout() {
    clearToken()
    setDisplayNameState('')
    navigate('/login', { replace: true })
  }

  const isLoggedIn = Boolean(getToken())

  return (
    <div className="app-root">
      {/* ── Header (navy-900 + gold authority strip) ── */}
      <header className="app-header">
        <span className="header-wordmark">법무 판례 검색</span>
        {isLoggedIn && (
          <div className="header-controls">
            <span className="header-user">{displayName}</span>
            <button className="btn btn--ghost btn--sm" onClick={handleLogout} type="button">
              로그아웃
            </button>
          </div>
        )}
      </header>

      {/* ── Routes ── */}
      <Routes>
        <Route
          path="/login"
          element={<LoginScreen onLoginSuccess={handleLoginSuccess} />}
        />
        <Route
          path="/search"
          element={
            <RequireAuth>
              <PrecedentSearchScreen />
            </RequireAuth>
          }
        />
        {/*
         * Phase B — case-management CRUD screens (DEFERRED).
         * Blocked on:
         *   G-1: /cases endpoints not implemented in backend (GET /cases, GET /cases/:id)
         *   G-2: /cases POST/PATCH/DELETE endpoints missing
         *   G-3: case_document ingest pipeline incomplete
         *   G-4: CaseOut schema not yet stabilised
         *   G-5: role-based access policy for case mutations TBD
         *   G-6: RLS row isolation for case-scoped search not end-to-end tested
         *   Q-1: open question — should Phase B be a separate micro-frontend or same SPA?
         * TODO (Phase B): add /cases route here pointing to CasesScreen.tsx
         */}
        <Route path="/" element={<Navigate to={isLoggedIn ? '/search' : '/login'} replace />} />
        <Route path="*" element={<Navigate to={isLoggedIn ? '/search' : '/login'} replace />} />
      </Routes>
    </div>
  )
}
