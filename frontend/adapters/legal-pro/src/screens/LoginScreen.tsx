/**
 * LoginScreen.tsx — 법무법인 legal-pro 로그인 화면.
 *
 * Uses legal-rag email+password auth (POST /auth/login).
 * Token stored in sessionStorage (clears on tab close — sitewide security policy).
 * Renders the navy-900 + gold authority strip card per the legal-pro theme.
 */

import { useState } from 'react'
import { apiLogin } from '../api/wire'

interface Props {
  onLoginSuccess: (token: string, displayName: string) => void
}

export default function LoginScreen({ onLoginSuccess }: Props) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!email.trim() || !password) {
      setErrorMsg('이메일과 비밀번호를 모두 입력하세요.')
      return
    }

    setLoading(true)
    setErrorMsg('')

    const result = await apiLogin(email.trim(), password)
    setLoading(false)

    if (result.error) {
      setErrorMsg(result.error.messageKo)
      return
    }

    if (result.data?.access_token) {
      onLoginSuccess(result.data.access_token, result.data.display_name ?? '')
    } else {
      setErrorMsg('토큰을 받지 못했습니다. IT 담당자에게 문의하세요.')
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-card">
        {/* Navy-900 header with subtle gold accent strip (via ::before in app.css .app-header,
            replicated here on the card header via inline border-top) */}
        <div
          className="login-card__header"
          style={{ borderTop: '3px solid var(--lr-gold-500)' }}
        >
          <div className="login-card__wordmark">법무 판례 검색</div>
          <div className="login-card__subtitle">
            출처 인용 검색 시스템 — 생성형 답변 없음
          </div>
        </div>

        <div className="login-card__body">
          {errorMsg && (
            <div className="login-card__alert" role="alert">
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div className="form-field">
              <label className="form-label" htmlFor="lp-email">이메일</label>
              <input
                id="lp-email"
                type="email"
                className="form-input"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                autoFocus
                autoComplete="email"
                placeholder="변호사 이메일"
                disabled={loading}
              />
            </div>

            <div className="form-field" style={{ marginTop: 12 }}>
              <label className="form-label" htmlFor="lp-password">비밀번호</label>
              <input
                id="lp-password"
                type="password"
                className="form-input"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className="btn btn--primary btn--full"
              style={{ marginTop: 20 }}
              disabled={loading}
              aria-busy={loading}
            >
              {loading ? '로그인 중...' : '로그인'}
            </button>
          </form>
        </div>

        <div className="login-card__footer">
          사내망 전용 시스템 · self-host · 데이터 외부 전송 없음
        </div>
      </div>
    </div>
  )
}
