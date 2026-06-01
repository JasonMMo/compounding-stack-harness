/**
 * paging.ts — pure paging-state predicates (F-2).
 *
 * Extracted from ListScreen so both the screen and unit tests share one
 * source of truth.  No imports from React or wire — intentionally
 * dependency-free for easy testing.
 */

export interface PagingState {
  mode: 'offset' | 'cursor'
  /** offset mode: current 1-based page number */
  page?: number
  /** offset mode: page size */
  size?: number
  /** offset mode: total item count from server */
  total?: number
  /** cursor mode: next_cursor value from server response (empty string or undefined = no more) */
  nextCursor?: string | null
}

/**
 * Returns true when there are more pages / items to load.
 *
 * offset: more pages exist when page < totalPages (ceil(total/size)).
 * cursor: more pages exist when next_cursor is a non-empty string.
 */
export function hasMorePages(state: PagingState): boolean {
  if (state.mode === 'cursor') {
    return typeof state.nextCursor === 'string' && state.nextCursor.length > 0
  }
  // offset
  const total = state.total ?? 0
  const size = state.size ?? 1
  const page = state.page ?? 1
  const totalPages = Math.max(1, Math.ceil(total / size))
  return page < totalPages
}

/**
 * Convenience: total page count for offset mode.
 * Returns 1 as the minimum (even for 0-item results).
 */
export function totalPageCount(total: number, size: number): number {
  return Math.max(1, Math.ceil(total / size))
}
