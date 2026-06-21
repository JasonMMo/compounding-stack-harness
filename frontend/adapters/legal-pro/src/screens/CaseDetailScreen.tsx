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
  type CaseDetailResponse,
  type CaseDocumentItem,
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

// ── Main screen ────────────────────────────────────────────────────────────

export default function CaseDetailScreen() {
  const { id: caseId } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [detail, setDetail] = useState<CaseDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

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
  }, [caseId, navigate])

  function handleSearch() {
    navigate(`/search?case_id=${encodeURIComponent(caseId ?? '')}`)
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
