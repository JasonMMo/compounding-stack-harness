import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import LoginScreen from './screens/LoginScreen'
import PrecedentSearchScreen from './screens/PrecedentSearchScreen'
import CasesScreen from './screens/CasesScreen'
import CaseDetailScreen from './screens/CaseDetailScreen'

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

// ── Tab navigation ─────────────────────────────────────────────────────────

interface TabNavProps {
  onLogout: () => void
  displayName: string
}

function TabNav({ onLogout, displayName }: TabNavProps) {
  const navigate = useNavigate()
  const location = useLocation()

  // 사건 현황 탭: /cases 와 /cases/:id 양쪽에서 active (OQ-2)
  const isCasesActive = location.pathname === '/cases' || location.pathname.startsWith('/cases/')
  const isSearchActive = location.pathname === '/search'

  return (
    <>
      <div className="app-tabs" role="tablist" aria-label="주요 메뉴">
        <button
          type="button"
          className="tab-btn"
          role="tab"
          aria-selected={isCasesActive}
          onClick={() => navigate('/cases')}
        >
          사건 현황
        </button>
        <button
          type="button"
          className="tab-btn"
          role="tab"
          aria-selected={isSearchActive}
          onClick={() => navigate('/search')}
        >
          문서 검색
        </button>
        <div style={{ flex: 1 }} />
        <span className="header-user" style={{ alignSelf: 'center', fontSize: 'var(--text-meta-size)', color: 'var(--color-text-3)' }}>
          {displayName}
        </span>
        <button
          className="btn btn--ghost btn--sm"
          style={{ alignSelf: 'center', marginLeft: 8, marginRight: 0 }}
          onClick={onLogout}
          type="button"
        >
          로그아웃
        </button>
      </div>
    </>
  )
}

export default function App() {
  const navigate = useNavigate()
  // displayName is held in state so header re-renders after login
  const [displayName, setDisplayNameState] = useState<string>(getDisplayName())

  function handleLoginSuccess(token: string, name: string) {
    setToken(token, name)
    setDisplayNameState(name)
    navigate('/cases', { replace: true })
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
      </header>

      {/* ── Tab nav (로그인 상태에서만) ── */}
      {isLoggedIn && (
        <TabNav onLogout={handleLogout} displayName={displayName} />
      )}

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
        {/* Phase B — 사건관리 read 화면 */}
        <Route
          path="/cases"
          element={
            <RequireAuth>
              <CasesScreen />
            </RequireAuth>
          }
        />
        <Route
          path="/cases/:id"
          element={
            <RequireAuth>
              <CaseDetailScreen />
            </RequireAuth>
          }
        />
        <Route path="/" element={<Navigate to={isLoggedIn ? '/cases' : '/login'} replace />} />
        <Route path="*" element={<Navigate to={isLoggedIn ? '/cases' : '/login'} replace />} />
      </Routes>
    </div>
  )
}
