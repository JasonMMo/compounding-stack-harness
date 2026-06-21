/**
 * CaseDetailScreen.tsx — 사건 상세 화면 (Phase B, [[S-16]]).
 *
 * Design contracts:
 *  - GET /cases/{case_id} → CaseDetailResponse (§3.2)
 *  - 메타 필드 null이면 표시 생략
 *  - 문서 ingest_status 뱃지 (done→색인완료 / pending·processing→대기중 / error→실패 / null→상태불명)
 *  - 원문 보기 버튼: aria-disabled="true" tabindex="-1" title="원문 서빙 준비 중" (G-3, AC-08)
 *  - 404 → "사건을 찾을 수 없습니다." (AC-06, 403 분기 금지)
 *  - [← 목록으로] → /cases, [검색] → /search?case_id=<uuid> (OQ-2, OQ-3)
 *  - 삭제 UI 없음 (AC-10)
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  apiGetCase,
  apiCreateParty,
  apiUpdateParty,
  type CaseDetailResponse,
  type CaseDocumentItem,
  type CaseParty,
  type PartyRole,
} from '../api/wire'

// ── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_MAP: Record<string, string> = {
  active: '진행중',
  closed: '종결',
  intake: '접수중',
  trial: '재판중',
  appeal: '항소중',
  withdrawn: '취하',
}

function statusLabel(raw: string): string {
  return STATUS_MAP[raw] ?? raw
}

/** ingest_status → 뱃지 클래스 + 레이블 */
function docIngestBadge(status: string | null): { cls: string; label: string } {
  if (status === 'done') return { cls: 'ingest-badge--indexed', label: '색인완료' }
  if (status === 'pending' || status === 'processing') return { cls: 'ingest-badge--pending', label: '대기중' }
  if (status === 'error') return { cls: 'ingest-badge--failed', label: '실패' }
  return { cls: 'ingest-badge--unknown', label: '상태불명' }
}

// ── Sub-components ───────────────────────────────────────────────────────────

interface MetaRowProps {
  label: string
  value: string | null | undefined
}

function MetaRow({ label, value }: MetaRowProps) {
  if (value == null) return null
  return (
    <div className="case-detail-panel__meta-item">
      <strong>{label}</strong>
      {value}
    </div>
  )
}

interface DocItemProps {
  doc: CaseDocumentItem
}

function DocItem({ doc }: DocItemProps) {
  const badge = docIngestBadge(doc.ingest_status)
  return (
    <li className="case-detail-panel__doc-item">
      {doc.document_type && (
        <span className="case-detail-panel__doc-type">{doc.document_type}</span>
      )}
      <span className="case-detail-panel__doc-title">
        {doc.title ?? '(제목 없음)'}
      </span>
      <span
        className={`ingest-status-badge ${badge.cls}`}
        aria-label={`색인 상태: ${badge.label}`}
        style={{ flexShrink: 0 }}
      >
        {badge.label}
      </span>
      {/* G-3 보류: 원문 보기 버튼 aria-disabled 고정 (AC-08) */}
      <button
        type="button"
        className="citation-card__link case-detail-panel__doc-view"
        aria-disabled="true"
        tabIndex={-1}
        title="원문 서빙 준비 중"
        aria-label="원문 보기 (준비 중)"
      >
        원문 보기 →
      </button>
    </li>
  )
}

// ── PartyPanel ────────────────────────────────────────────────────────────────

/** role → 한국어 UI 레이블 (§4.2) */
const ROLE_LABEL_MAP: Record<PartyRole, string> = {
  plaintiff: '원고',
  defendant: '피고',
  witness: '증인',
  'opposing-counsel': '상대방 대리인',
  'expert-witness': '전문가 증인',
}

const PARTY_ROLES: PartyRole[] = [
  'plaintiff',
  'defendant',
  'witness',
  'opposing-counsel',
  'expert-witness',
]

interface PartyPanelProps {
  caseId: string
  parties: CaseParty[]
  onRefresh: () => void
}

function PartyPanel({ caseId, parties, onRefresh }: PartyPanelProps) {
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)

  // Add form state
  const [addRole, setAddRole] = useState<PartyRole>('plaintiff')
  const [addName, setAddName] = useState('')
  const [addNotes, setAddNotes] = useState('')
  const [addError, setAddError] = useState<string | null>(null)
  const [addSaving, setAddSaving] = useState(false)

  // Edit form state (keyed by party_id via editingId)
  const [editRole, setEditRole] = useState<PartyRole>('plaintiff')
  const [editName, setEditName] = useState('')
  const [editNotes, setEditNotes] = useState('')
  const [editError, setEditError] = useState<string | null>(null)
  const [editSaving, setEditSaving] = useState(false)

  function openEdit(p: CaseParty) {
    setEditingId(p.party_id)
    setEditRole(p.role as PartyRole)
    setEditName(p.name)
    setEditNotes(p.notes ?? '')
    setEditError(null)
  }

  function cancelEdit() {
    setEditingId(null)
    setEditError(null)
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    if (!addName.trim()) {
      setAddError('당사자명을 입력하세요.')
      return
    }
    setAddSaving(true)
    setAddError(null)
    const res = await apiCreateParty(caseId, {
      role: addRole,
      name: addName.trim(),
      notes: addNotes.trim() || null,
    })
    setAddSaving(false)
    if (res.error) {
      setAddError(res.error.messageKo)
      return
    }
    // Reset form & refresh
    setAddRole('plaintiff')
    setAddName('')
    setAddNotes('')
    setShowAddForm(false)
    onRefresh()
  }

  async function handleEdit(e: React.FormEvent) {
    e.preventDefault()
    if (!editingId) return
    if (!editName.trim()) {
      setEditError('당사자명을 입력하세요.')
      return
    }
    setEditSaving(true)
    setEditError(null)
    const res = await apiUpdateParty(caseId, editingId, {
      role: editRole,
      name: editName.trim(),
      notes: editNotes.trim() || null,
    })
    setEditSaving(false)
    if (res.error) {
      setEditError(res.error.messageKo)
      return
    }
    cancelEdit()
    onRefresh()
  }

  return (
    <div className="case-detail-panel__docs" style={{ padding: 'var(--space-page-h, 24px)' }}>
      {/* Section header */}
      <div
        className="case-detail-panel__docs-title"
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}
      >
        <span>당사자 {parties.length}명</span>
        {!showAddForm && (
          <button
            type="button"
            className="btn btn--outline btn--sm"
            onClick={() => { setShowAddForm(true); setAddError(null) }}
            aria-label="당사자 추가"
          >
            당사자 추가
          </button>
        )}
      </div>

      {/* Add form — slide-in on button click */}
      {showAddForm && (
        <form
          onSubmit={handleAdd}
          aria-label="당사자 등록 폼"
          style={{
            border: '1px solid var(--color-border)',
            borderRadius: 6,
            padding: 12,
            marginBottom: 12,
            background: 'var(--color-surface-1)',
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
          }}
        >
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: '0 0 160px' }}>
              <span style={{ fontSize: 12, color: 'var(--color-text-2)' }}>역할 *</span>
              <select
                value={addRole}
                onChange={e => setAddRole(e.target.value as PartyRole)}
                className="form-control"
                required
              >
                {PARTY_ROLES.map(r => (
                  <option key={r} value={r}>{ROLE_LABEL_MAP[r]}</option>
                ))}
              </select>
            </label>
            <label style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: '1 1 200px' }}>
              <span style={{ fontSize: 12, color: 'var(--color-text-2)' }}>당사자명 * (최대 255자)</span>
              <input
                type="text"
                value={addName}
                onChange={e => setAddName(e.target.value)}
                className="form-control"
                maxLength={255}
                required
                placeholder="예) 주식회사 한빛테크"
              />
            </label>
          </div>
          <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <span style={{ fontSize: 12, color: 'var(--color-text-2)' }}>메모 (선택, 최대 255자)</span>
            <textarea
              value={addNotes}
              onChange={e => setAddNotes(e.target.value)}
              className="form-control"
              maxLength={255}
              rows={2}
              placeholder="예) 원고 법인. 소프트웨어 공급 계약 상대방."
            />
          </label>
          {addError && (
            <p style={{ color: 'var(--color-error, #e53e3e)', fontSize: 13, margin: 0 }} role="alert">
              {addError}
            </p>
          )}
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              type="submit"
              className="btn btn--primary btn--sm"
              disabled={addSaving}
              aria-busy={addSaving}
            >
              {addSaving ? '저장 중…' : '등록'}
            </button>
            <button
              type="button"
              className="btn btn--outline btn--sm"
              onClick={() => { setShowAddForm(false); setAddError(null) }}
            >
              취소
            </button>
          </div>
        </form>
      )}

      {/* Party list */}
      {parties.length === 0 && !showAddForm ? (
        <p style={{ color: 'var(--color-text-2)', fontSize: 14, margin: 0 }}>
          등록된 당사자가 없습니다.
        </p>
      ) : (
        <ul className="case-detail-panel__doc-list" aria-label="당사자 목록">
          {parties.map(p => (
            <li key={p.party_id} className="case-detail-panel__doc-item">
              {editingId === p.party_id ? (
                /* Inline edit form */
                <form
                  onSubmit={handleEdit}
                  aria-label="당사자 수정 폼"
                  style={{ display: 'flex', flexDirection: 'column', gap: 8, width: '100%' }}
                >
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    <label style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: '0 0 160px' }}>
                      <span style={{ fontSize: 12, color: 'var(--color-text-2)' }}>역할</span>
                      <select
                        value={editRole}
                        onChange={e => setEditRole(e.target.value as PartyRole)}
                        className="form-control"
                      >
                        {PARTY_ROLES.map(r => (
                          <option key={r} value={r}>{ROLE_LABEL_MAP[r]}</option>
                        ))}
                      </select>
                    </label>
                    <label style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: '1 1 200px' }}>
                      <span style={{ fontSize: 12, color: 'var(--color-text-2)' }}>당사자명 (최대 255자)</span>
                      <input
                        type="text"
                        value={editName}
                        onChange={e => setEditName(e.target.value)}
                        className="form-control"
                        maxLength={255}
                        required
                      />
                    </label>
                  </div>
                  <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <span style={{ fontSize: 12, color: 'var(--color-text-2)' }}>메모 (최대 255자)</span>
                    <textarea
                      value={editNotes}
                      onChange={e => setEditNotes(e.target.value)}
                      className="form-control"
                      maxLength={255}
                      rows={2}
                    />
                  </label>
                  {editError && (
                    <p style={{ color: 'var(--color-error, #e53e3e)', fontSize: 13, margin: 0 }} role="alert">
                      {editError}
                    </p>
                  )}
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button
                      type="submit"
                      className="btn btn--primary btn--sm"
                      disabled={editSaving}
                      aria-busy={editSaving}
                    >
                      {editSaving ? '저장 중…' : '저장'}
                    </button>
                    <button
                      type="button"
                      className="btn btn--outline btn--sm"
                      onClick={cancelEdit}
                    >
                      취소
                    </button>
                  </div>
                </form>
              ) : (
                /* Read row */
                <>
                  <span className="case-detail-panel__doc-type">
                    {ROLE_LABEL_MAP[p.role as PartyRole] ?? p.role}
                  </span>
                  <span className="case-detail-panel__doc-title">{p.name}</span>
                  {p.notes && (
                    <span style={{ fontSize: 12, color: 'var(--color-text-2)', flexShrink: 0 }}>
                      {p.notes}
                    </span>
                  )}
                  <button
                    type="button"
                    className="btn btn--outline btn--sm"
                    style={{ flexShrink: 0, marginLeft: 'auto' }}
                    onClick={() => openEdit(p)}
                    aria-label={`${p.name} 수정`}
                  >
                    수정
                  </button>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

// ── Main screen ────────────────────────────────────────────────────────────

export default function CaseDetailScreen() {
  const { id: caseId } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [detail, setDetail] = useState<CaseDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  // refreshKey: incrementing triggers re-fetch (used by PartyPanel.onRefresh)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    if (!caseId) {
      setNotFound(true)
      setLoading(false)
      return
    }

    let cancelled = false

    async function fetch() {
      setLoading(true)
      setNotFound(false)
      setErrorMsg(null)

      const res = await apiGetCase(caseId!)

      if (cancelled) return
      setLoading(false)

      if (res.error) {
        if (res.error.isAuth) {
          navigate('/login', { replace: true })
          return
        }
        // AC-06: 404(존재 은폐) + 기타 에러 모두 동일 메시지 패턴
        // 백엔드가 타 변호사 사건을 404로 은폐하므로, 404를 특별 분기하지 않아도 됨
        setNotFound(true)
        return
      }

      setDetail(res.data!)
    }

    fetch()
    return () => { cancelled = true }
  }, [caseId, navigate, refreshKey])

  function handleSearch() {
    navigate(`/search?case_id=${encodeURIComponent(caseId ?? '')}`)
  }

  function handleRefresh() {
    setRefreshKey(k => k + 1)
  }

  // ── Loading ──────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <main className="page-main">
        <p className="results-message" role="status" aria-live="polite">
          불러오는 중…
        </p>
      </main>
    )
  }

  // ── 404 / 에러 (AC-06) ───────────────────────────────────────────────────
  if (notFound || errorMsg || !detail) {
    return (
      <main className="page-main">
        <div style={{ marginBottom: 12 }}>
          <button
            type="button"
            className="btn btn--outline btn--sm"
            onClick={() => navigate('/cases')}
            aria-label="사건 목록으로 돌아가기"
          >
            ← 목록으로
          </button>
        </div>
        <p className="results-message" role="alert">
          사건을 찾을 수 없습니다.
        </p>
      </main>
    )
  }

  // ── 정상 렌더 ────────────────────────────────────────────────────────────
  return (
    <main className="page-main" style={{ padding: 0, flex: 1 }}>
      {/* 상단 타이틀 바 + 액션 */}
      <div
        className="page-title-bar"
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            type="button"
            className="btn btn--outline btn--sm"
            onClick={() => navigate('/cases')}
            aria-label="사건 목록으로 돌아가기"
          >
            ← 목록으로
          </button>
          <span>{detail.title}</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {/* G-2 C1 진입점: [사건 수정] -> /cases/:id/edit (기존 렌더 로직 불변) */}
          <button
            type="button"
            className="btn btn--outline btn--sm"
            onClick={() => navigate(`/cases/${caseId}/edit`)}
            aria-label="사건 수정"
          >
            사건 수정
          </button>
          <button
            type="button"
            className="btn btn--primary btn--sm"
            onClick={handleSearch}
            aria-label="이 사건으로 판례 검색"
          >
            검색
          </button>
        </div>
      </div>

      {/* 메타 행 (null 필드 생략) */}
      <div className="case-detail-panel__meta">
        <MetaRow label="사건번호" value={detail.case_number} />
        <MetaRow label="상태" value={statusLabel(detail.status)} />
        {detail.case_type && <MetaRow label="유형" value={detail.case_type} />}
        {detail.opened_at && <MetaRow label="접수일" value={detail.opened_at} />}
        {detail.closed_at && <MetaRow label="종결일" value={detail.closed_at} />}
      </div>

      {/* 사건 개요 */}
      {detail.description && (
        <div
          style={{
            padding: '12px var(--space-page-h, 24px)',
            fontSize: 'var(--text-body-size)',
            lineHeight: 'var(--text-body-lh)',
            color: 'var(--color-text-2)',
            borderBottom: '1px solid var(--color-border)',
            background: 'var(--color-surface-1)',
          }}
        >
          {detail.description}
        </div>
      )}

      {/* G-2 C2 당사자 패널 (인라인, 별도 라우트 없음 — §2.3) */}
      {caseId && (
        <PartyPanel
          caseId={caseId}
          parties={detail.parties ?? []}
          onRefresh={handleRefresh}
        />
      )}

      {/* 문서 목록 */}
      <div className="case-detail-panel__docs" style={{ padding: 'var(--space-page-h, 24px)' }}>
        <div className="case-detail-panel__docs-title">
          문서 {detail.documents.length}건
        </div>

        {detail.documents.length === 0 ? (
          <li className="case-detail-panel__doc-item case-detail-panel__doc-empty" style={{ listStyle: 'none' }}>
            등록된 문서가 없습니다.
          </li>
        ) : (
          <ul className="case-detail-panel__doc-list" aria-label="소속 문서 목록">
            {detail.documents.map(doc => (
              <DocItem key={doc.doc_id} doc={doc} />
            ))}
          </ul>
        )}
      </div>
    </main>
  )
}
