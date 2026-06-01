import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { WIRE_VERSION } from './contract/contract.gen'
import LoginScreen from './screens/LoginScreen'
import ListScreen from './screens/ListScreen'
import DetailScreen from './screens/DetailScreen'
import CreateScreen from './screens/CreateScreen'
import DeleteScreen from './screens/DeleteScreen'
import HealthScreen from './screens/HealthScreen'

// Auth state is held in module-level storage (sessionStorage) so it survives
// React re-renders but not page reload — matching vanilla-htmx session behavior.
const TOKEN_KEY = 'csh_token'

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY)
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  if (!getToken()) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

const PERSONAS = ['ops', 'ceo', 'it'] as const
type Persona = (typeof PERSONAS)[number]

export default function App() {
  const navigate = useNavigate()
  const [persona, setPersona] = useState<Persona>('ops')

  function handlePersonaChange(p: Persona) {
    setPersona(p)
    document.documentElement.setAttribute('data-persona', p)
  }

  function handleLogout() {
    clearToken()
    navigate('/login')
  }

  const isLoggedIn = Boolean(getToken())

  return (
    <div className="layout">
      <nav className="navbar">
        <Link to="/entities/customer" className="navbar-brand">
          Compounding Stack Harness
        </Link>
        <span className="navbar-spacer" />
        {isLoggedIn && (
          <>
            <select
              className="persona-select"
              value={persona}
              onChange={e => handlePersonaChange(e.target.value as Persona)}
              aria-label="페르소나 선택"
            >
              {PERSONAS.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
            <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
              로그아웃
            </button>
          </>
        )}
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/login" element={<LoginScreen />} />
          <Route
            path="/entities/:entityType"
            element={<RequireAuth><ListScreen /></RequireAuth>}
          />
          <Route
            path="/entities/:entityType/new"
            element={<RequireAuth><CreateScreen /></RequireAuth>}
          />
          <Route
            path="/entities/:entityType/:entityId/delete"
            element={<RequireAuth><DeleteScreen /></RequireAuth>}
          />
          <Route
            path="/entities/:entityType/:entityId"
            element={<RequireAuth><DetailScreen /></RequireAuth>}
          />
          <Route path="/health" element={<HealthScreen />} />
          <Route path="/" element={<Navigate to="/entities/customer" replace />} />
        </Routes>

        <p className="wire-version">wire contract v{WIRE_VERSION}</p>
      </main>
    </div>
  )
}
