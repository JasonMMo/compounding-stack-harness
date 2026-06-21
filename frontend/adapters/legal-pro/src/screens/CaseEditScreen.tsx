/**
 * CaseEditScreen.tsx — 사건 수정 폼 (G-2 C1, §2.2)
 *
 * 라우트: /cases/:id/edit (RequireAuth 래핑)
 * 진입: CaseDetailScreen [사건 수정] 버튼
 * 이탈: 저장 성공 → /cases/<id>, 취소 → /cases/<id>
 *
 * 필드: case_number(readonly), title, case_type, status, description, opened_at
 * case_number 는 표시만(readonly) — PATCH 바디에 미포함(immutable, OQ-5)
 *
 * 보존 계약 §5.3: 기존 CaseDetailScreen 미수정.
 * DDL CHECK: case_type ∈ {civil,criminal,administrative,family,commercial}.
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  apiGetCase,
  apiUpdateCase,
  type CaseUpdateIn,
  type CaseType,
  type CaseStatus,
} from '../api/wire'

// ── 상수 ──────────────────────────────────────────────────────────────────────

const CASE_TYPE_OPTIONS: { value: CaseType | ''; label: string }[] = [
  { value: '', label: '-- 선택 안 함 --' },
  { value: 'civil', label: '민사' },
  { value: 'criminal', label: '형사' },
  { value: 'administrative', label: '행정' },
  { value: 'family', label: '가사' },
  { value: 'commercial', label: '상사' },
]

const STATUS_OPTIONS: { value: CaseStatus; label: string }[] = [
  { value: 'intake', label: '접수중' },
  { value: 'active', label: '진행중' },
  { value: 'trial', label: '재판중' },
  { value: 'appeal', label: '항소중' },
  { value: 'closed', label: '종결' },
  { value: 'withdrawn', label: '취하' },
]

// ── 컴포넌트 ──────────────────────────────────────────────────────────────────

export default function CaseEditScreen() {
  const { id: caseId } = useParams<{ id: string }>()
  const navigate = useNavigate()

  // 기존 사건 메타 로드 상태
  const [loadError, setLoadError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // 폼 필드 상태
  const [caseNumber, setCaseNumber] = useState('')    // readonly 표시용
  const [title, setTitle] = useState('')
  const [caseType, setCaseType] = useState<CaseType | ''>('')
  const [status, setStatus] = useState<CaseStatus>('intake')
  const [description, setDescription] = useState('')
  const [openedAt, setOpenedAt] = useState('')
  const [closedAt, setClosedAt] = useState('')

  const [submitting, setSubmitting] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  // 기존 사건 데이터 로드
  useEffect(() => {
    if (!caseId) {
      setLoadError('사건 ID가 없습니다.')
      setLoading(false)
      return
    }

    let cancelled = false

    async function load() {
      setLoading(true)
      setLoadError(null)

      const res = await apiGetCase(caseId!)
      if (cancelled) return
      setLoading(false)

      if (res.error) {
        if (res.error.isAuth) {
          navigate('/login', { replace: true })
          return
        }
        setLoadError('사건을 찾을 수 없습니다.')
        return
      }

      const d = res.data!
      setCaseNumber(d.case_number)
      setTitle(d.title)
      setCaseType((d.case_type as CaseType | null) ?? '')
      setStatus(d.status as CaseStatus)
      setDescription(d.description ?? '')
      setOpenedAt(d.opened_at ?? '')
      setClosedAt(d.closed_at ?? '')
    }

    load()
    return () => { cancelled = true }
  }, [caseId, navigate])

  function validate(): string | null {
    if (!title.trim()) return '사건명은 필수입니다.'
    if (title.length > 512) return '사건명은 최대 512자입니다.'
    if (description.length > 4000) return '사건 개요는 최대 4000자입니다.'
    if (openedAt && !/^\d{4}-\d{2}-\d{2}$/.test(openedAt)) return '접수일 형식: YYYY-MM-DD'
    if (closedAt && !/^\d{4}-\d{2}-\d{2}$/.test(closedAt)) return '종결일 형식: YYYY-MM-DD'
    return null
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErrorMsg(null)

    const err = validate()
    if (err) {
      setErrorMsg(err)
      return
    }

    if (!caseId) return

    setSubmitting(true)

    const body: CaseUpdateIn = {
      title: title.trim(),
      case_type: caseType || null,
      status,
      description: description.trim() || null,
      opened_at: openedAt || null,
      closed_at: closedAt || null,
    }

    const res = await apiUpdateCase(caseId, body)
    setSubmitting(false)

    if (res.error) {
      if (res.error.isAuth) {
        navigate('/login', { replace: true })
        return
      }
      setErrorMsg(res.error.messageKo)
      return
    }

    // 성공: 사건 상세 화면으로 이동
    navigate(`/cases/${caseId}`, { replace: true })
  }

  function handleCancel() {
    navigate(`/cases/${caseId ?? ''}`)
  }

  // ── 로딩 상태 ───────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <main className="page-main">
        <p className="results-message" role="status" aria-live="polite">
          불러오는 중…
        </p>
      </main>
    )
  }

  // ── 로드 에러 ───────────────────────────────────────────────────────────────
  if (loadError) {
    return (
      <main className="page-main">
        <div style={{ marginBottom: 12 }}>
          <button
            type="button"
            className="btn btn--outline btn--sm"
            onClick={() => navigate('/cases')}
          >
            ← 목록으로
          </button>
        </div>
        <p className="results-message" role="alert">{loadError}</p>
      </main>
    )
  }

  // ── 정상 폼 렌더 ────────────────────────────────────────────────────────────
  return (
    <main className="page-main">
      <div
        className="page-title-bar"
        style={{ display: 'flex', alignItems: 'center', gap: 12 }}
      >
        <button
          type="button"
          className="btn btn--outline btn--sm"
          onClick={handleCancel}
          aria-label="사건 상세로 돌아가기"
        >
          ← 돌아가기
        </button>
        <span>사건 수정</span>
      </div>

      <form
        onSubmit={handleSubmit}
        style={{ padding: 'var(--space-page-h, 24px)', maxWidth: 640 }}
        aria-label="사건 수정 폼"
      >
        {errorMsg && (
          <p
            className="results-message"
            role="alert"
            style={{ color: 'var(--color-error, #c00)', marginBottom: 16 }}
          >
            {errorMsg}
          </p>
        )}

        {/* 사건번호 (readonly) */}
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="case-number-ro" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            사건번호 <span style={{ fontWeight: 400, color: 'var(--color-text-3)', fontSize: '0.85em' }}>(수정 불가)</span>
          </label>
          <input
            id="case-number-ro"
            type="text"
            readOnly
            value={caseNumber}
            style={{
              width: '100%', padding: '8px 10px', boxSizing: 'border-box',
              background: 'var(--color-surface-2, #f5f5f5)',
              color: 'var(--color-text-3)',
              cursor: 'not-allowed',
            }}
            aria-readonly="true"
          />
        </div>

        {/* 사건명 */}
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="case-title" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            사건명 <span aria-hidden="true" style={{ color: 'var(--color-error, #c00)' }}>*</span>
          </label>
          <input
            id="case-title"
            type="text"
            required
            maxLength={512}
            value={title}
            onChange={e => setTitle(e.target.value)}
            style={{ width: '100%', padding: '8px 10px', boxSizing: 'border-box' }}
            aria-required="true"
          />
        </div>

        {/* 사건유형 */}
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="case-type" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            사건 유형
          </label>
          <select
            id="case-type"
            value={caseType}
            onChange={e => setCaseType(e.target.value as CaseType | '')}
            style={{ padding: '8px 10px' }}
          >
            {CASE_TYPE_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* 사건상태 */}
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="case-status" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            사건 상태 <span aria-hidden="true" style={{ color: 'var(--color-error, #c00)' }}>*</span>
          </label>
          <select
            id="case-status"
            value={status}
            required
            onChange={e => setStatus(e.target.value as CaseStatus)}
            style={{ padding: '8px 10px' }}
            aria-required="true"
          >
            {STATUS_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* 사건 개요 */}
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="case-description" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            사건 개요
          </label>
          <textarea
            id="case-description"
            maxLength={4000}
            rows={4}
            value={description}
            onChange={e => setDescription(e.target.value)}
            style={{ width: '100%', padding: '8px 10px', boxSizing: 'border-box', resize: 'vertical' }}
          />
          <small style={{ color: 'var(--color-text-3)' }}>{description.length} / 4000</small>
        </div>

        {/* 접수일 */}
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="case-opened-at" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            접수일
          </label>
          <input
            id="case-opened-at"
            type="date"
            value={openedAt}
            onChange={e => setOpenedAt(e.target.value)}
            style={{ padding: '8px 10px' }}
          />
        </div>

        {/* 종결일 (status=closed 시 활성 권고) */}
        <div style={{ marginBottom: 24 }}>
          <label htmlFor="case-closed-at" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            종결일{' '}
            <span style={{ fontWeight: 400, color: 'var(--color-text-3)', fontSize: '0.85em' }}>
              (상태가 종결인 경우 입력 권장)
            </span>
          </label>
          <input
            id="case-closed-at"
            type="date"
            value={closedAt}
            onChange={e => setClosedAt(e.target.value)}
            style={{ padding: '8px 10px' }}
          />
        </div>

        {/* 버튼 */}
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            type="submit"
            className="btn btn--primary"
            disabled={submitting}
            aria-disabled={submitting}
          >
            {submitting ? '저장 중…' : '수정 저장'}
          </button>
          <button
            type="button"
            className="btn btn--outline"
            onClick={handleCancel}
            disabled={submitting}
          >
            취소
          </button>
        </div>
      </form>
    </main>
  )
}
