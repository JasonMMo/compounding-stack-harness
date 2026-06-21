/**
 * ErrorBanner.tsx — Error envelope renderer (F-3 compliance).
 *
 * Branches on error.code, displays messageKo.
 * Retriable errors show a retry affordance.
 */

import type { WireError } from '../api/wire'

interface Props {
  error: WireError
  onRetry?: () => void
}

export default function ErrorBanner({ error, onRetry }: Props) {
  return (
    <div
      className="login-card__alert"
      role="alert"
      data-error-code={error.code}
      style={{ display: 'block' }}
    >
      {error.messageKo}
      {error.retriable && onRetry && (
        <button
          type="button"
          onClick={onRetry}
          style={{
            marginLeft: 8,
            fontWeight: 500,
            cursor: 'pointer',
            color: 'var(--color-danger)',
            background: 'none',
            border: 'none',
            padding: 0,
            fontSize: 'inherit',
            textDecoration: 'underline',
          }}
        >
          다시 시도
        </button>
      )}
    </div>
  )
}
