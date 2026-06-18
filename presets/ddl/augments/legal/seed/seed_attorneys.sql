-- =============================================================================
-- seed_attorneys.sql — 법무법인 한강 RAG MVP 변호사 계정 시드 데이터
-- 변호사 3명: 파트너 김정훈 + 어소시에이트 이준호·박서연
-- UUID 고정: seed_cases.sql 의 assigned_attorney_id / partner_id 와 1:1 일치
-- 초기 데모 자격증명은 self-host 런북(#8) 문서 참조
-- 로드 순서: 반드시 seed_cases.sql 보다 먼저 실행 (FK 의존성)
-- =============================================================================

-- UUID 매핑 (불변 — seed_cases.sql 과 동일)
-- a1000000-0000-0000-0000-000000000001 → 이준호 (어소시에이트)
-- a1000000-0000-0000-0000-000000000002 → 박서연 (어소시에이트)
-- a1000000-0000-0000-0000-000000000003 → 김정훈 (파트너 — 이준호·박서연 감독)

-- ─────────────────────────────────────────────
-- 파트너 김정훈 먼저 삽입 (이준호·박서연의 partner_id 가 이 UUID 를 참조)
-- ─────────────────────────────────────────────
INSERT INTO legal_attorney (id, email, password_hash, display_name, partner_id, role, is_active, created_at, updated_at)
VALUES (
  'a1000000-0000-0000-0000-000000000003'::uuid,
  'jh.kim@example-lawfirm.kr',
  '$2b$12$tNyhYcMFyBTa5Ly1mPjzT.h8bjIb5ku08j/nMqN2MLAib6sRpb/8a',
  '김정훈',
  NULL,                                                                -- 파트너는 감독자 없음
  'partner',
  true,
  NOW(), NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ─────────────────────────────────────────────
-- 어소시에이트 이준호
-- seed_cases.sql 에서 c001~c006 assigned_attorney_id 참조
-- partner_id (seed_cases의 RLS 파트너 열) 도 이 UUID 사용 — 단, legal_attorney.partner_id ≠ legal_case.partner_id
-- legal_attorney.partner_id = 감독 파트너 (김정훈)
-- ─────────────────────────────────────────────
INSERT INTO legal_attorney (id, email, password_hash, display_name, partner_id, role, is_active, created_at, updated_at)
VALUES (
  'a1000000-0000-0000-0000-000000000001'::uuid,
  'lee.junho@example-lawfirm.kr',
  '$2b$12$D7T7IzhOHbw/rjUrtHjX4Omr5X/C0GrwfOkf6XsfvrfTToeBz6mkW',
  '이준호',
  'a1000000-0000-0000-0000-000000000003'::uuid,                       -- 감독 파트너: 김정훈
  'attorney',
  true,
  NOW(), NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ─────────────────────────────────────────────
-- 어소시에이트 박서연
-- seed_cases.sql 에서 c007~c012 assigned_attorney_id 참조
-- ─────────────────────────────────────────────
INSERT INTO legal_attorney (id, email, password_hash, display_name, partner_id, role, is_active, created_at, updated_at)
VALUES (
  'a1000000-0000-0000-0000-000000000002'::uuid,
  'park.seoyeon@example-lawfirm.kr',
  '$2b$12$fH0rM.qenelFB0zvYwnrzeJjHTwcKmeJuP25FCIIEy8NbCddUhSyO',
  '박서연',
  'a1000000-0000-0000-0000-000000000003'::uuid,                       -- 감독 파트너: 김정훈
  'attorney',
  true,
  NOW(), NOW()
)
ON CONFLICT (id) DO NOTHING;
