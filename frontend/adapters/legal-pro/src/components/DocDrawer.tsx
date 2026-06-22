/**
 * DocDrawer.tsx — 원문 슬라이드오버 드로어.
 *
 * Ports services/legal-rag/web/app.js openDocDrawer() to React.
 * Uses .doc-drawer / .doc-drawer-backdrop CSS already in tokens.gen.css.
 *
 * Props:
 *   sourceType — 'precedent' | 'case_document'
 *   sourceId   — UUID string
 *   onClose    — 드로어 닫기 콜백
 */

import { useEffect, useCallback } from 'react'
import { apiGetDocument, type DocumentReadOut, type WireError } from '../api/wire'
import { useState } from 'react'

interface Props {
  sourceType: string
  sourceId: string
  onClose: () => void
}

type DrawerState = 'loading' | 'success' | 'error'

export default function DocDrawer({ sourceType, sourceId, onClose }: Props) {
  const [state, setState] = useState<DrawerState>('loading')
  const [doc, setDoc] = useState<DocumentReadOut | null>(null)
  const [error, setError] = useState<WireError | null>(null)

  // 마운트 시 fetch
  useEffect(() => {
    setState('loading')
    setDoc(null)
    setError(null)

    apiGetDocument(sourceType, sourceId).then(result => {
      if (result.error) {
        setError(result.error)
        setState('error')
      } else {
        setDoc(result.data)
        setState('success')
      }
    })
  }, [sourceType, sourceId])

  // ESC 키 닫기
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    },
    [onClose],
  )

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  // is-open 클래스 — 1 tick 지연으로 CSS transition 트리거
  const [isOpen, setIsOpen] = useState(false)
  useEffect(() => {
    const id = requestAnimationFrame(() => setIsOpen(true))
    return () => cancelAnimationFrame(id)
  }, [])

  const isPrecedent = sourceType === 'precedent'

  // 헤더 타이틀 결정
  const drawerTitle = state === 'success' && doc
    ? (doc.title ?? (isPrecedent ? '판례 원문' : '사건문서 원문'))
    : '원문 보기'

  // 서브타이틀 (citation 또는 document_type)
  const drawerSubtitle = state === 'success' && doc
    ? (isPrecedent ? doc.citation : doc.document_type) ?? null
    : null

  return (
    <>
      {/* 백드롭 */}
      <div
        className={`doc-drawer-backdrop${isOpen ? ' is-open' : ''}`}
        aria-hidden="true"
        onClick={onClose}
      />

      {/* 드로어 패널 */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="doc-drawer-title"
        className={`doc-drawer${isOpen ? ' is-open' : ''}`}
      >
        {/* 헤더 */}
        <div className="doc-drawer__header">
          <div className="doc-drawer__title-block">
            <div className="doc-drawer__title" id="doc-drawer-title">
              {drawerTitle}
            </div>
            {drawerSubtitle && (
              <div className="doc-drawer__citation">{drawerSubtitle}</div>
            )}
          </div>
          <button
            type="button"
            className="doc-drawer__close"
            aria-label="원문 보기 닫기"
            onClick={onClose}
          >
            ✕
          </button>
        </div>

        {/* 메타 행 (판례 전용) */}
        {state === 'success' && doc && isPrecedent && (
          <div className="doc-drawer__meta">
            {doc.court && (
              <span className="doc-drawer__meta-item">
                <strong>법원</strong>{doc.court}
              </span>
            )}
            {doc.decided_date && (
              <span className="doc-drawer__meta-item">
                <strong>선고일</strong>{doc.decided_date}
              </span>
            )}
            {doc.case_type && (
              <span className="doc-drawer__meta-item">
                <strong>유형</strong>{doc.case_type}
              </span>
            )}
            {doc.keywords && (
              <span className="doc-drawer__meta-item">
                <strong>키워드</strong>{doc.keywords}
              </span>
            )}
          </div>
        )}

        {/* 본문 영역 */}
        <div className="doc-drawer__body">
          {state === 'loading' && (
            <div className="doc-drawer__status">불러오는 중...</div>
          )}

          {state === 'error' && (
            <div className="doc-drawer__status doc-drawer__status--error">
              {error?.code === 'NOT_FOUND'
                ? '원문을 찾을 수 없습니다.'
                : (error?.messageKo ?? '오류가 발생했습니다.')}
            </div>
          )}

          {state === 'success' && doc && (
            <>
              {doc.body_is_holding_fallback && (
                <div className="doc-drawer__fallback-badge">요지 표시 (전문 미충전)</div>
              )}
              {!isPrecedent && !doc.body && (
                <div className="doc-drawer__status">
                  원문이 아직 인덱싱되지 않았습니다.
                </div>
              )}
              {doc.body && (
                <pre className="doc-drawer__body-text">{doc.body}</pre>
              )}
            </>
          )}
        </div>
      </div>
    </>
  )
}
