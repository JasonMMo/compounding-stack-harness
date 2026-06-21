/**
 * CaseCreateScreen.tsx — 사건 생성 폼 (G-2 C1, S-17, §2.1)
 *
 * 라우트: /cases/new (RequireAuth 래핑)
 * 진입: CasesScreen [새 사건 등록] 버튼
 * 이탈: 저장 성공 → /cases/<new_case_id>, 취소 → /cases
 *
 * 필드: case_number(필수), title(필수), case_type(선택), status(필수 기본=intake),
 *       description(선택), opened_at(선택)
 *
 * 보존 계약 §5.3: 기존 CasesScreen / CaseDetailScreen 미수정.
 * DDL CHECK: case_type ∈ {civil,criminal,administrative,family,commercial} — other 없음.
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  apiCreateCase,
  type CaseCreateIn,
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

export default function CaseCreateScreen() {
  const navigate = useNavigate()

  const [caseNumber, setCaseNumber] = useState('')
  const [title, setTitle] = useState('')
  const [caseType, setCaseType] = useState<CaseType | ''>('')
  const [status, setStatus] = useState<CaseStatus>('intake')
  const [description, setDescription] = useState('')
  const [openedAt, setOpenedAt] = useState('')

  const [submitting, setSubmitting] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  // 클라이언트 측 필수 검증
  function validate(): string | null {
    if (!caseNumber.trim()) return '사건번호는 필수입니다.'
    if (caseNumber.includes(' ')) return '사건번호에 공백을 포함할 수 없습니다.'
    if (caseNumber.length > 64) return '사건번호는 최대 64자입니다.'
    if (!title.trim()) return '사건명은 필수입니다.'
    if (title.length > 512) return '사건명은 최대 512자입니다.'
    if (description.length > 4000) return '사건 개요는 최대 4000자입니다.'
    if (openedAt && !/^\d{4}-\d{2}-\d{2}$/.test(openedAt)) {
      return '접수일 형식: YYYY-MM-DD'
    }
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

    setSubmitting(true)

    const body: CaseCreateIn = {
      case_number: caseNumber.trim(),
      title: title.trim(),
      case_type: caseType || null,
      status,
      description: description.trim() || null,
      opened_at: openedAt || null,
    }

    const res = await apiCreateCase(body)
    setSubmitting(false)

    if (res.error) {
      if (res.error.isAuth) {
        navigate('/login', { replace: true })
        return
      }
      setErrorMsg(res.error.messageKo)
      return
    }

    // 성공: 새 사건 상세 화면으로 이동
    const newCase = res.data!
    navigate(`/cases/${newCase.case_id}`, { replace: true })
  }

  function handleCancel() {
    navigate('/cases')
  }

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
          aria-label="사건 목록으로 돌아가기"
        >
          ← 목록으로
        </button>
        <span>새 사건 등록</span>
      </div>

      <form
        onSubmit={handleSubmit}
        style={{ padding: 'var(--space-page-h, 24px)', maxWidth: 640 }}
        aria-label="사건 생성 폼"
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

        {/* 사건번호 */}
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="case-number" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            사건번호 <span aria-hidden="true" style={{ color: 'var(--color-error, #c00)' }}>*</span>
          </label>
          <input
            id="case-number"
            type="text"
            required
            maxLength={64}
            value={caseNumber}
            onChange={e => setCaseNumber(e.target.value)}
            placeholder="예: 2026가합99001"
            style={{ width: '100%', padding: '8px 10px', boxSizing: 'border-box' }}
            aria-required="true"
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
            placeholder="예: 손해배상(기)"
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
            placeholder="사건 내용을 간략히 입력하세요."
            style={{ width: '100%', padding: '8px 10px', boxSizing: 'border-box', resize: 'vertical' }}
          />
          <small style={{ color: 'var(--color-text-3)' }}>{description.length} / 4000</small>
        </div>

        {/* 접수일 */}
        <div style={{ marginBottom: 24 }}>
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

        {/* 버튼 */}
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            type="submit"
            className="btn btn--primary"
            disabled={submitting}
            aria-disabled={submitting}
          >
            {submitting ? '등록 중…' : '사건 등록'}
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
