/**
 * LoginScreen.tsx — auth.login screen.
 *
 * POST credentials → store token in sessionStorage → redirect to /entities/customer.
 * F-3: error branching on error.code, display messageKo.
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiLogin } from '../api/wire'
import { setToken } from '../App'
import { WIRE_VERSION } from '../contract/contract.gen'

export default function LoginScreen() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setErrorMsg('')

    const result = await apiLogin(username, password)
    setLoading(false)

    if (result.error) {
      // F-3: display messageKo branched on error.code
      setErrorMsg(result.error.messageKo)
      return
    }

    if (result.data?.token) {
      setToken(result.data.token)
      navigate('/entities/customer', { replace: true })
    } else {
      setErrorMsg('토큰을 받지 못했습니다.')
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', paddingTop: 'var(--space-inset-xl)' }}>
      <div className="card">
        <h1 style={{ textAlign: 'center', marginBottom: 'var(--space-gap-lg)' }}>로그인</h1>

        {errorMsg && (
          <div className="alert alert-danger" role="alert">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="username">사용자명</label>
            <input
              id="username"
              type="text"
              className="form-input"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
              autoFocus
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">비밀번호</label>
            <input
              id="password"
              type="password"
              className="form-input"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          <div className="form-actions" style={{ borderTop: 'none', marginTop: 0 }}>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%' }}
              disabled={loading}
            >
              {loading ? '로그인 중...' : '로그인'}
            </button>
          </div>
        </form>

        <p className="text-muted" style={{ textAlign: 'center', marginTop: 'var(--space-gap-sm)' }}>
          데모 자격증명: demo / demo
        </p>
      </div>

      <p className="wire-version">wire contract v{WIRE_VERSION}</p>
    </div>
  )
}
