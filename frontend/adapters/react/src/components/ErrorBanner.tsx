/**
 * ErrorBanner.tsx — F-3 error envelope renderer.
 *
 * Branches on error.code (never message text).
 * Shows messageKo from contract.gen.ts generated map.
 * Retriable codes get a retry affordance.
 * Auth codes trigger login redirect (handled in wire.ts, not here).
 */

import type { WireError } from '../api/wire'

interface Props {
  error: WireError
  onRetry?: () => void
}

export default function ErrorBanner({ error, onRetry }: Props) {
  return (
    <div className="alert alert-danger" role="alert" data-error-code={error.code}>
      <strong>{error.messageKo}</strong>
      {error.retriable && onRetry && (
        <button className="retry-link" onClick={onRetry} type="button">
          다시 시도
        </button>
      )}
      {error.details && (
        <div className="text-muted" style={{ marginTop: '4px', fontSize: 'var(--font-size-xs)' }}>
          {Object.entries(error.details).map(([field, msg]) => (
            <div key={field}>{field}: {String(msg)}</div>
          ))}
        </div>
      )}
    </div>
  )
}
