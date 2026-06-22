"""
scripts/demo/seed_lawfirm_full.py — Full demo seed for lawfirm-demo.

Extends the baseline (1 dept / 3 emp / 5 precedent / 3 case) to:
  - hr_department      : 5  (existing 1 + new 4)
  - hr_employee        : 14 (existing 3 + new 11)
  - legal_precedent    : 12 (existing 5 + new 7)
  - legal_case         : 10 (existing 3 + new 7)
  - legal_case_party   : 28 (new, 3/case approx)
  - legal_case_document: 22 (new, 2/case approx)
  - document_category  :  6 (new)
  - document_document  : 10 (new)
  - document_version   : 14 (new, 10 docs x v1 + 4 docs x v2)
  - document_access_rule:  8 (new)
  - approval_request   :  7 (new)
  - approval_step      : 15 (new, 1-3/request)
  - approval_approver  : 18 (new)
  - approval_decision  : 13 (new, subset approved/rejected)

All UUIDs are fixed => ON CONFLICT (id) DO NOTHING => idempotent.
Caller: setup_lawfirm.py::main() calls seed_full(conn) after baseline.
"""

from __future__ import annotations

from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# UUID roster
# ---------------------------------------------------------------------------

# Existing (from setup_lawfirm.py) — referenced as FK targets
_DEPT_LAW001 = "11111111-0000-0000-0000-000000000001"  # 소송부

_EMP_IDS_BASE = [
    "22222222-0000-0000-0000-000000000001",  # EMP001 김대호 (파트너변호사)
    "22222222-0000-0000-0000-000000000002",  # EMP002 이수진 (어소시에이트)
    "22222222-0000-0000-0000-000000000003",  # EMP003 박민우 (어소시에이트)
]
_EMP1, _EMP2, _EMP3 = _EMP_IDS_BASE

_CASE_IDS_BASE = [
    "44444444-0000-0000-0000-000000000001",
    "44444444-0000-0000-0000-000000000002",
    "44444444-0000-0000-0000-000000000003",
]
_C1, _C2, _C3 = _CASE_IDS_BASE

# New departments
_DEPT2 = "11111111-0000-0000-0000-000000000002"  # 송무2팀
_DEPT3 = "11111111-0000-0000-0000-000000000003"  # 기업자문팀
_DEPT4 = "11111111-0000-0000-0000-000000000004"  # 가사·형사팀
_DEPT5 = "11111111-0000-0000-0000-000000000005"  # 지원팀

# New employees EMP004-EMP014
_E4  = "22222222-0000-0000-0000-000000000004"
_E5  = "22222222-0000-0000-0000-000000000005"
_E6  = "22222222-0000-0000-0000-000000000006"
_E7  = "22222222-0000-0000-0000-000000000007"
_E8  = "22222222-0000-0000-0000-000000000008"
_E9  = "22222222-0000-0000-0000-000000000009"
_E10 = "22222222-0000-0000-0000-000000000010"
_E11 = "22222222-0000-0000-0000-000000000011"
_E12 = "22222222-0000-0000-0000-000000000012"
_E13 = "22222222-0000-0000-0000-000000000013"
_E14 = "22222222-0000-0000-0000-000000000014"

# New precedents P06-P12
_P6  = "33333333-0000-0000-0000-000000000006"
_P7  = "33333333-0000-0000-0000-000000000007"
_P8  = "33333333-0000-0000-0000-000000000008"
_P9  = "33333333-0000-0000-0000-000000000009"
_P10 = "33333333-0000-0000-0000-000000000010"
_P11 = "33333333-0000-0000-0000-000000000011"
_P12 = "33333333-0000-0000-0000-000000000012"

# New cases C04-C10
_C4  = "44444444-0000-0000-0000-000000000004"
_C5  = "44444444-0000-0000-0000-000000000005"
_C6  = "44444444-0000-0000-0000-000000000006"
_C7  = "44444444-0000-0000-0000-000000000007"
_C8  = "44444444-0000-0000-0000-000000000008"
_C9  = "44444444-0000-0000-0000-000000000009"
_C10 = "44444444-0000-0000-0000-000000000010"

# legal_case_party
_PARTY_BASE = "55555555-0000-0000-0000-"

def _pid(n: int) -> str:
    return f"{_PARTY_BASE}{n:012d}"

# legal_case_document
_CDOC_BASE = "66666666-0000-0000-0000-"

def _cdid(n: int) -> str:
    return f"{_CDOC_BASE}{n:012d}"

# document_category
_CAT1 = "77777777-0000-0000-0000-000000000001"
_CAT2 = "77777777-0000-0000-0000-000000000002"
_CAT3 = "77777777-0000-0000-0000-000000000003"
_CAT4 = "77777777-0000-0000-0000-000000000004"
_CAT5 = "77777777-0000-0000-0000-000000000005"
_CAT6 = "77777777-0000-0000-0000-000000000006"

# document_document
_DOC_BASE = "88888888-0000-0000-0000-"

def _did(n: int) -> str:
    return f"{_DOC_BASE}{n:012d}"

# document_version
_VER_BASE = "99999999-0000-0000-0000-"

def _vid(n: int) -> str:
    return f"{_VER_BASE}{n:012d}"

# document_access_rule
_AR_BASE = "aaaaaaaa-0000-0000-0000-"

def _arid(n: int) -> str:
    return f"{_AR_BASE}{n:012d}"

# approval_request
_AQ_BASE = "bbbbbbbb-0000-0000-0000-"

def _aqid(n: int) -> str:
    return f"{_AQ_BASE}{n:012d}"

# approval_step
_AS_BASE = "cccccccc-0000-0000-0000-"

def _asid(n: int) -> str:
    return f"{_AS_BASE}{n:012d}"

# approval_approver
_AA_BASE = "dddddddd-0000-0000-0000-"

def _aaid(n: int) -> str:
    return f"{_AA_BASE}{n:012d}"

# approval_decision
_AD_BASE = "eeeeeeee-0000-0000-0000-"

def _adid(n: int) -> str:
    return f"{_AD_BASE}{n:012d}"


# ---------------------------------------------------------------------------
# Timestamp helper
# ---------------------------------------------------------------------------

def _ts(s: str) -> str:
    """Return ISO timestamp string for a given date string YYYY-MM-DD."""
    return f"{s}T09:00:00+00:00"


_NOW = datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Data definitions
# ---------------------------------------------------------------------------

NEW_DEPARTMENTS = [
    {
        "id": _DEPT2, "created_at": _NOW, "updated_at": _NOW,
        "code": "LAW002", "name": "송무2팀",
        "parent_id": None, "manager_id": None,  # manager set after employees
    },
    {
        "id": _DEPT3, "created_at": _NOW, "updated_at": _NOW,
        "code": "LAW003", "name": "기업자문팀",
        "parent_id": None, "manager_id": None,
    },
    {
        "id": _DEPT4, "created_at": _NOW, "updated_at": _NOW,
        "code": "LAW004", "name": "가사·형사팀",
        "parent_id": None, "manager_id": None,
    },
    {
        "id": _DEPT5, "created_at": _NOW, "updated_at": _NOW,
        "code": "SUP001", "name": "지원팀",
        "parent_id": None, "manager_id": None,
    },
]

# New employees: EMP004-EMP014
NEW_EMPLOYEES = [
    # 송무2팀
    {
        "id": _E4, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP004", "full_name": "최준혁",
        "department_id": _DEPT2, "position_id": None,
        "hire_date": "2013-06-01", "status": "active",
    },
    {
        "id": _E5, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP005", "full_name": "정하린",
        "department_id": _DEPT2, "position_id": None,
        "hire_date": "2019-04-01", "status": "active",
    },
    {
        "id": _E6, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP006", "full_name": "오세연",
        "department_id": _DEPT2, "position_id": None,
        "hire_date": "2022-09-01", "status": "active",
    },
    # 기업자문팀
    {
        "id": _E7, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP007", "full_name": "강민서",
        "department_id": _DEPT3, "position_id": None,
        "hire_date": "2016-02-15", "status": "active",
    },
    {
        "id": _E8, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP008", "full_name": "윤지호",
        "department_id": _DEPT3, "position_id": None,
        "hire_date": "2020-08-10", "status": "active",
    },
    {
        "id": _E9, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP009", "full_name": "신예원",
        "department_id": _DEPT3, "position_id": None,
        "hire_date": "2023-03-01", "status": "active",
    },
    # 가사·형사팀
    {
        "id": _E10, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP010", "full_name": "임도현",
        "department_id": _DEPT4, "position_id": None,
        "hire_date": "2014-11-01", "status": "active",
    },
    {
        "id": _E11, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP011", "full_name": "한소율",
        "department_id": _DEPT4, "position_id": None,
        "hire_date": "2021-05-03", "status": "active",
    },
    # 지원팀
    {
        "id": _E12, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP012", "full_name": "배지수",
        "department_id": _DEPT5, "position_id": None,
        "hire_date": "2017-07-20", "status": "active",
    },
    {
        "id": _E13, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP013", "full_name": "문채린",
        "department_id": _DEPT5, "position_id": None,
        "hire_date": "2023-01-02", "status": "active",
    },
    {
        "id": _E14, "created_at": _NOW, "updated_at": _NOW,
        "employee_number": "EMP014", "full_name": "권현우",
        "department_id": _DEPT5, "position_id": None,
        "hire_date": "2019-10-15", "status": "on-leave",
    },
]

# After employees inserted, set department managers
DEPT_MANAGER_UPDATES = [
    (_E4,  _DEPT2),
    (_E7,  _DEPT3),
    (_E10, _DEPT4),
    (_E12, _DEPT5),
]

NEW_PRECEDENTS = [
    {
        "id": _P6, "created_at": _NOW, "updated_at": _NOW,
        "citation": "대법원 2022므5678",
        "court": "대법원",
        "decided_date": "2022-08-25",
        "case_type": "family",
        "holding": (
            "이혼 소송에서 유책 배우자의 청구는 원칙적으로 허용되지 않으나, "
            "혼인 관계가 객관적으로 완전히 파탄된 경우 예외적으로 허용될 수 있다."
        ),
        "full_text": None,
        "keywords": "이혼 유책배우자 혼인파탄 예외허용 가사",
    },
    {
        "id": _P7, "created_at": _NOW, "updated_at": _NOW,
        "citation": "서울가정법원 2021브234",
        "court": "서울가정법원",
        "decided_date": "2021-12-10",
        "case_type": "family",
        "holding": (
            "친권자 지정 사건에서 자녀의 복리가 최우선 고려 사항이며, "
            "경제적 능력보다 양육 환경의 안정성을 중시한다."
        ),
        "full_text": None,
        "keywords": "친권 양육권 자녀복리 양육환경 가사",
    },
    {
        "id": _P8, "created_at": _NOW, "updated_at": _NOW,
        "citation": "대법원 2023도8821",
        "court": "대법원",
        "decided_date": "2023-04-27",
        "case_type": "criminal",
        "holding": (
            "업무상 횡령죄에서 불법영득의사는 주관적 의도로서, "
            "타인의 재물을 자기 또는 제3자의 이익을 위해 임의 처분할 의사가 있으면 인정된다."
        ),
        "full_text": None,
        "keywords": "횡령 불법영득의사 업무상 형사 임의처분",
    },
    {
        "id": _P9, "created_at": _NOW, "updated_at": _NOW,
        "citation": "서울중앙지방법원 2022가합31111",
        "court": "서울중앙지방법원",
        "decided_date": "2022-11-03",
        "case_type": "commercial",
        "holding": (
            "주주간 계약에서 의결권 구속 조항은 회사법상 강행 규정에 위반되지 않는 한 "
            "유효하며, 위반 시 손해배상 책임이 발생한다."
        ),
        "full_text": None,
        "keywords": "주주간계약 의결권 상사 손해배상 강행규정",
    },
    {
        "id": _P10, "created_at": _NOW, "updated_at": _NOW,
        "citation": "대법원 2019두44302",
        "court": "대법원",
        "decided_date": "2019-07-11",
        "case_type": "administrative",
        "holding": (
            "조세 부과처분의 위법 여부는 부과 당시 법령을 기준으로 하고, "
            "과세관청이 입증 책임을 부담하며 납세자의 신뢰보호 원칙도 고려된다."
        ),
        "full_text": None,
        "keywords": "조세부과 행정처분 신뢰보호 입증책임 납세자",
    },
    {
        "id": _P11, "created_at": _NOW, "updated_at": _NOW,
        "citation": "대법원 2020다77892",
        "court": "대법원",
        "decided_date": "2020-12-17",
        "case_type": "civil",
        "holding": (
            "부동산 이중매매에서 제2매수인이 제1매매 사실을 알면서 매매계약을 체결하였다면 "
            "반사회적 법률행위로서 무효이고, 제1매수인은 소유권 이전 청구권을 가진다."
        ),
        "full_text": None,
        "keywords": "이중매매 반사회적법률행위 소유권 부동산 민사",
    },
    {
        "id": _P12, "created_at": _NOW, "updated_at": _NOW,
        "citation": "서울고등법원 2023나11234",
        "court": "서울고등법원",
        "decided_date": "2023-09-14",
        "case_type": "civil",
        "holding": (
            "하도급 계약에서 원사업자가 부당 단가 인하를 강요한 경우 하도급법 위반으로 "
            "손해배상 책임이 있으며, 법원은 실제 손해액을 인정할 수 있다."
        ),
        "full_text": None,
        "keywords": "하도급 부당단가인하 손해배상 민사 계약",
    },
]

NEW_CASES = [
    {
        "id": _C4, "created_at": _NOW, "updated_at": _NOW,
        "case_number": "CASE-2024-004",
        "title": "이혼 및 재산분할 청구 사건",
        "case_type": "family",
        "status": "trial",
        "filed_date": "2024-01-08",
        "court": "서울가정법원",
        "next_hearing_date": "2026-07-10",
        "assigned_attorney_id": _E10,
        "client_contact_id": None,
        "summary": "혼인 파탄으로 인한 이혼 청구 및 재산분할. 공동재산 추정 8억원.",
    },
    {
        "id": _C5, "created_at": _NOW, "updated_at": _NOW,
        "case_number": "CASE-2024-005",
        "title": "업무상 횡령 고소 대응 사건",
        "case_type": "criminal",
        "status": "active",
        "filed_date": "2024-04-22",
        "court": "서울중앙지방법원",
        "next_hearing_date": "2026-08-14",
        "assigned_attorney_id": _E10,
        "client_contact_id": None,
        "summary": "전 임원의 회사 자금 횡령 혐의. 피해액 추정 1억 2천만원.",
    },
    {
        "id": _C6, "created_at": _NOW, "updated_at": _NOW,
        "case_number": "CASE-2024-006",
        "title": "IT 서비스 계약 분쟁 중재",
        "case_type": "commercial",
        "status": "intake",
        "filed_date": "2024-05-30",
        "court": None,
        "next_hearing_date": None,
        "assigned_attorney_id": _E7,
        "client_contact_id": None,
        "summary": "SaaS 플랫폼 계약 해지 및 위약금 분쟁. 클라이언트측 손해 주장 3억원.",
    },
    {
        "id": _C7, "created_at": _NOW, "updated_at": _NOW,
        "case_number": "CASE-2024-007",
        "title": "부동산 이중매매 소유권 이전 청구",
        "case_type": "civil",
        "status": "trial",
        "filed_date": "2023-11-15",
        "court": "인천지방법원",
        "next_hearing_date": "2026-07-25",
        "assigned_attorney_id": _E4,
        "client_contact_id": None,
        "summary": "제1매수인 권리 보전 위한 소유권 이전 청구. 부동산 감정가 6억원.",
    },
    {
        "id": _C8, "created_at": _NOW, "updated_at": _NOW,
        "case_number": "CASE-2025-001",
        "title": "조세부과처분 취소청구",
        "case_type": "administrative",
        "status": "active",
        "filed_date": "2025-02-03",
        "court": "서울행정법원",
        "next_hearing_date": "2026-09-18",
        "assigned_attorney_id": _EMP3,
        "client_contact_id": None,
        "summary": "세무조사 후 법인세 추가 부과처분. 불복금액 2억 4천만원.",
    },
    {
        "id": _C9, "created_at": _NOW, "updated_at": _NOW,
        "case_number": "CASE-2025-002",
        "title": "하도급 단가 인하 손해배상",
        "case_type": "civil",
        "status": "closed",
        "filed_date": "2024-06-10",
        "court": "부산지방법원",
        "next_hearing_date": None,
        "assigned_attorney_id": _E4,
        "client_contact_id": None,
        "summary": "원사업자 부당 단가 인하에 따른 손해배상 청구. 항소심 원고 일부 승소 확정.",
    },
    {
        "id": _C10, "created_at": _NOW, "updated_at": _NOW,
        "case_number": "CASE-2025-003",
        "title": "주주간 의결권 계약 위반 손해배상",
        "case_type": "commercial",
        "status": "appeal",
        "filed_date": "2025-01-20",
        "court": "서울고등법원",
        "next_hearing_date": "2026-10-07",
        "assigned_attorney_id": _E7,
        "client_contact_id": None,
        "summary": "소수주주 의결권 구속 조항 위반. 항소심 진행 중. 손해 주장 5천만원.",
    },
]

# ---------------------------------------------------------------------------
# legal_case_party — 사건당 2~4명
# ---------------------------------------------------------------------------

CASE_PARTIES = [
    # C1 — ABC주식회사 손해배상
    {"id": _pid(1),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C1, "role": "plaintiff",        "name": "주식회사 에이비씨솔루션", "contact_id": None, "notes": "원고 법인, 소가 5억"},
    {"id": _pid(2),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C1, "role": "defendant",        "name": "대한물류주식회사",       "contact_id": None, "notes": "피고 법인"},
    {"id": _pid(3),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C1, "role": "opposing-counsel", "name": "변호사 조동현",           "contact_id": None, "notes": "피고측 대리인"},
    # C2 — 부동산 매매 계약 위반
    {"id": _pid(4),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C2, "role": "plaintiff",        "name": "홍길동",                 "contact_id": None, "notes": "매수인"},
    {"id": _pid(5),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C2, "role": "defendant",        "name": "박기영",                 "contact_id": None, "notes": "매도인"},
    # C3 — 행정 제재처분 취소
    {"id": _pid(6),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C3, "role": "plaintiff",        "name": "주식회사 한빛유통",       "contact_id": None, "notes": "처분 대상 법인"},
    {"id": _pid(7),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C3, "role": "defendant",        "name": "서울특별시장",           "contact_id": None, "notes": "처분 행정청"},
    # C4 — 이혼 재산분할
    {"id": _pid(8),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C4, "role": "plaintiff",        "name": "김소연",                 "contact_id": None, "notes": "청구인"},
    {"id": _pid(9),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C4, "role": "defendant",        "name": "정태준",                 "contact_id": None, "notes": "상대방"},
    {"id": _pid(10), "created_at": _NOW, "updated_at": _NOW, "case_id": _C4, "role": "witness",          "name": "이정은",                 "contact_id": None, "notes": "진술 증인"},
    # C5 — 횡령 고소
    {"id": _pid(11), "created_at": _NOW, "updated_at": _NOW, "case_id": _C5, "role": "plaintiff",        "name": "주식회사 미래테크",       "contact_id": None, "notes": "피해 법인 고소인"},
    {"id": _pid(12), "created_at": _NOW, "updated_at": _NOW, "case_id": _C5, "role": "defendant",        "name": "유창호",                 "contact_id": None, "notes": "전 재무이사"},
    {"id": _pid(13), "created_at": _NOW, "updated_at": _NOW, "case_id": _C5, "role": "expert-witness",   "name": "공인회계사 나인규",       "contact_id": None, "notes": "회계감정인"},
    # C6 — IT 계약 분쟁
    {"id": _pid(14), "created_at": _NOW, "updated_at": _NOW, "case_id": _C6, "role": "plaintiff",        "name": "주식회사 넥스트플로우",   "contact_id": None, "notes": "서비스 이용사"},
    {"id": _pid(15), "created_at": _NOW, "updated_at": _NOW, "case_id": _C6, "role": "defendant",        "name": "클라우드온주식회사",     "contact_id": None, "notes": "SaaS 제공사"},
    # C7 — 이중매매
    {"id": _pid(16), "created_at": _NOW, "updated_at": _NOW, "case_id": _C7, "role": "plaintiff",        "name": "송민준",                 "contact_id": None, "notes": "제1매수인"},
    {"id": _pid(17), "created_at": _NOW, "updated_at": _NOW, "case_id": _C7, "role": "defendant",        "name": "양재호",                 "contact_id": None, "notes": "매도인"},
    {"id": _pid(18), "created_at": _NOW, "updated_at": _NOW, "case_id": _C7, "role": "defendant",        "name": "구은서",                 "contact_id": None, "notes": "제2매수인"},
    # C8 — 조세
    {"id": _pid(19), "created_at": _NOW, "updated_at": _NOW, "case_id": _C8, "role": "plaintiff",        "name": "주식회사 진성산업",       "contact_id": None, "notes": "납세자 법인"},
    {"id": _pid(20), "created_at": _NOW, "updated_at": _NOW, "case_id": _C8, "role": "defendant",        "name": "서울지방국세청장",       "contact_id": None, "notes": "과세처분청"},
    # C9 — 하도급
    {"id": _pid(21), "created_at": _NOW, "updated_at": _NOW, "case_id": _C9, "role": "plaintiff",        "name": "주식회사 세화전기",       "contact_id": None, "notes": "수급사업자"},
    {"id": _pid(22), "created_at": _NOW, "updated_at": _NOW, "case_id": _C9, "role": "defendant",        "name": "대림건설주식회사",       "contact_id": None, "notes": "원사업자"},
    {"id": _pid(23), "created_at": _NOW, "updated_at": _NOW, "case_id": _C9, "role": "opposing-counsel", "name": "변호사 황태성",           "contact_id": None, "notes": "피고측 대리"},
    # C10 — 주주간 계약
    {"id": _pid(24), "created_at": _NOW, "updated_at": _NOW, "case_id": _C10, "role": "plaintiff",       "name": "오픈아이주식회사",       "contact_id": None, "notes": "소수주주"},
    {"id": _pid(25), "created_at": _NOW, "updated_at": _NOW, "case_id": _C10, "role": "defendant",       "name": "매그넘파트너스유한회사", "contact_id": None, "notes": "대주주측 펀드"},
    {"id": _pid(26), "created_at": _NOW, "updated_at": _NOW, "case_id": _C10, "role": "witness",         "name": "공인회계사 이창민",       "contact_id": None, "notes": "가치평가 감정인"},
    # C1 추가 증인
    {"id": _pid(27), "created_at": _NOW, "updated_at": _NOW, "case_id": _C1, "role": "witness",          "name": "임재현",                 "contact_id": None, "notes": "계약체결 당시 담당자"},
    # C2 추가 상대방 대리인
    {"id": _pid(28), "created_at": _NOW, "updated_at": _NOW, "case_id": _C2, "role": "opposing-counsel", "name": "변호사 서명진",           "contact_id": None, "notes": "매도인측 대리인"},
]

# ---------------------------------------------------------------------------
# legal_case_document — 사건당 2~3건
# ---------------------------------------------------------------------------

CASE_DOCUMENTS = [
    # C1
    {"id": _cdid(1),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C1, "document_type": "complaint",     "title": "손해배상 청구 소장",           "filed_at": _ts("2024-01-15"), "storage_key": "cases/c1/complaint_001.pdf",     "notes": "원심 소장", "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-01-20")},
    {"id": _cdid(2),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C1, "document_type": "brief",         "title": "원고 준비서면 제1호",          "filed_at": _ts("2024-04-10"), "storage_key": "cases/c1/brief_001.pdf",         "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-04-12")},
    {"id": _cdid(3),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C1, "document_type": "evidence",      "title": "공급계약서 사본",              "filed_at": _ts("2024-03-05"), "storage_key": "cases/c1/evidence_001.pdf",      "notes": "갑 제1호증", "content_text": None, "ingest_status": "pending", "ingested_at": None},
    # C2
    {"id": _cdid(4),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C2, "document_type": "complaint",     "title": "매매계약 위반 소장",           "filed_at": _ts("2024-03-10"), "storage_key": "cases/c2/complaint_001.pdf",     "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-03-15")},
    {"id": _cdid(5),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C2, "document_type": "contract",      "title": "부동산 매매계약서",            "filed_at": _ts("2024-03-10"), "storage_key": "cases/c2/contract_001.pdf",      "notes": "갑 제2호증", "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-03-16")},
    # C3
    {"id": _cdid(6),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C3, "document_type": "complaint",     "title": "행정처분 취소 소장",           "filed_at": _ts("2024-02-20"), "storage_key": "cases/c3/complaint_001.pdf",     "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-02-25")},
    {"id": _cdid(7),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C3, "document_type": "court-order",   "title": "처분 통지서 사본",             "filed_at": _ts("2024-02-20"), "storage_key": "cases/c3/order_001.pdf",         "notes": "을 제1호증", "content_text": None, "ingest_status": "error",   "ingested_at": None},
    # C4
    {"id": _cdid(8),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C4, "document_type": "complaint",     "title": "이혼청구 소장",               "filed_at": _ts("2024-01-08"), "storage_key": "cases/c4/complaint_001.pdf",     "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-01-10")},
    {"id": _cdid(9),  "created_at": _NOW, "updated_at": _NOW, "case_id": _C4, "document_type": "brief",         "title": "재산분할 목록 준비서면",       "filed_at": _ts("2024-06-01"), "storage_key": "cases/c4/brief_001.pdf",         "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-06-03")},
    # C5
    {"id": _cdid(10), "created_at": _NOW, "updated_at": _NOW, "case_id": _C5, "document_type": "evidence",      "title": "회계감정 보고서",              "filed_at": _ts("2024-07-15"), "storage_key": "cases/c5/evidence_001.pdf",      "notes": "갑 제3호증", "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-07-16")},
    {"id": _cdid(11), "created_at": _NOW, "updated_at": _NOW, "case_id": _C5, "document_type": "brief",         "title": "공소사실 방어 준비서면",       "filed_at": _ts("2024-09-10"), "storage_key": "cases/c5/brief_001.pdf",         "notes": None,         "content_text": None, "ingest_status": "pending", "ingested_at": None},
    # C6
    {"id": _cdid(12), "created_at": _NOW, "updated_at": _NOW, "case_id": _C6, "document_type": "contract",      "title": "SaaS 서비스 이용 계약서",      "filed_at": _ts("2024-05-30"), "storage_key": "cases/c6/contract_001.pdf",      "notes": "계약 원본",  "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-06-01")},
    {"id": _cdid(13), "created_at": _NOW, "updated_at": _NOW, "case_id": _C6, "document_type": "correspondence", "title": "계약 해지 통보 이메일 출력본", "filed_at": _ts("2024-05-30"), "storage_key": "cases/c6/correspondence_001.pdf", "notes": None,         "content_text": None, "ingest_status": "pending", "ingested_at": None},
    # C7
    {"id": _cdid(14), "created_at": _NOW, "updated_at": _NOW, "case_id": _C7, "document_type": "complaint",     "title": "소유권이전 청구 소장",         "filed_at": _ts("2023-11-15"), "storage_key": "cases/c7/complaint_001.pdf",     "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2023-11-20")},
    {"id": _cdid(15), "created_at": _NOW, "updated_at": _NOW, "case_id": _C7, "document_type": "evidence",      "title": "제1매매 계약서 공증 사본",     "filed_at": _ts("2023-11-15"), "storage_key": "cases/c7/evidence_001.pdf",      "notes": "갑 제1호증", "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2023-11-21")},
    # C8
    {"id": _cdid(16), "created_at": _NOW, "updated_at": _NOW, "case_id": _C8, "document_type": "complaint",     "title": "과세처분 취소 소장",           "filed_at": _ts("2025-02-03"), "storage_key": "cases/c8/complaint_001.pdf",     "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2025-02-05")},
    {"id": _cdid(17), "created_at": _NOW, "updated_at": _NOW, "case_id": _C8, "document_type": "evidence",      "title": "세무조사결과 통지서",          "filed_at": _ts("2025-02-03"), "storage_key": "cases/c8/evidence_001.pdf",      "notes": "을 제1호증", "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2025-02-05")},
    # C9
    {"id": _cdid(18), "created_at": _NOW, "updated_at": _NOW, "case_id": _C9, "document_type": "complaint",     "title": "하도급 손해배상 소장",         "filed_at": _ts("2024-06-10"), "storage_key": "cases/c9/complaint_001.pdf",     "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2024-06-12")},
    {"id": _cdid(19), "created_at": _NOW, "updated_at": _NOW, "case_id": _C9, "document_type": "court-order",   "title": "항소심 판결문",               "filed_at": _ts("2025-03-20"), "storage_key": "cases/c9/order_001.pdf",         "notes": "종결 판결", "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2025-03-22")},
    # C10
    {"id": _cdid(20), "created_at": _NOW, "updated_at": _NOW, "case_id": _C10, "document_type": "complaint",    "title": "손해배상 항소장",              "filed_at": _ts("2025-01-20"), "storage_key": "cases/c10/complaint_001.pdf",    "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2025-01-22")},
    {"id": _cdid(21), "created_at": _NOW, "updated_at": _NOW, "case_id": _C10, "document_type": "evidence",     "title": "주주간계약서 공증본",          "filed_at": _ts("2025-01-20"), "storage_key": "cases/c10/evidence_001.pdf",     "notes": "갑 제1호증", "content_text": None, "ingest_status": "pending", "ingested_at": None},
    {"id": _cdid(22), "created_at": _NOW, "updated_at": _NOW, "case_id": _C10, "document_type": "brief",        "title": "항소이유서",                  "filed_at": _ts("2025-04-01"), "storage_key": "cases/c10/brief_001.pdf",        "notes": None,         "content_text": None, "ingest_status": "done",    "ingested_at": _ts("2025-04-03")},
]

# ---------------------------------------------------------------------------
# document_category
# ---------------------------------------------------------------------------

DOC_CATEGORIES = [
    {"id": _CAT1, "created_at": _NOW, "updated_at": _NOW, "code": "CAT-LAWSUIT",   "name": "소송서류",   "parent_id": None, "default_retention_days": 3650},
    {"id": _CAT2, "created_at": _NOW, "updated_at": _NOW, "code": "CAT-CONTRACT",  "name": "계약서",     "parent_id": None, "default_retention_days": 3650},
    {"id": _CAT3, "created_at": _NOW, "updated_at": _NOW, "code": "CAT-INTERNAL",  "name": "내부규정",   "parent_id": None, "default_retention_days": 1825},
    {"id": _CAT4, "created_at": _NOW, "updated_at": _NOW, "code": "CAT-HR",        "name": "인사서류",   "parent_id": None, "default_retention_days": 3650},
    {"id": _CAT5, "created_at": _NOW, "updated_at": _NOW, "code": "CAT-FINANCE",   "name": "회계서류",   "parent_id": None, "default_retention_days": 2555},
    {"id": _CAT6, "created_at": _NOW, "updated_at": _NOW, "code": "CAT-TEMPLATE",  "name": "서식·템플릿", "parent_id": None, "default_retention_days":  365},
]

# ---------------------------------------------------------------------------
# document_document (current_version_id set after versions inserted via UPDATE)
# ---------------------------------------------------------------------------

_DOC1 = _did(1)
_DOC2 = _did(2)
_DOC3 = _did(3)
_DOC4 = _did(4)
_DOC5 = _did(5)
_DOC6 = _did(6)
_DOC7 = _did(7)
_DOC8 = _did(8)
_DOC9 = _did(9)
_DOC10 = _did(10)

DOC_DOCUMENTS = [
    {"id": _DOC1,  "created_at": _NOW, "updated_at": _NOW, "title": "법인 정관",               "category_id": _CAT3, "owner_id": _E12, "status": "published", "current_version_id": None, "retention_date": "2035-01-01"},
    {"id": _DOC2,  "created_at": _NOW, "updated_at": _NOW, "title": "개인정보처리방침",         "category_id": _CAT3, "owner_id": _E12, "status": "published", "current_version_id": None, "retention_date": "2028-01-01"},
    {"id": _DOC3,  "created_at": _NOW, "updated_at": _NOW, "title": "법률자문 표준 위임계약서", "category_id": _CAT2, "owner_id": _E7,  "status": "published", "current_version_id": None, "retention_date": "2030-06-01"},
    {"id": _DOC4,  "created_at": _NOW, "updated_at": _NOW, "title": "사건 수임 보수 약정서",   "category_id": _CAT2, "owner_id": _E7,  "status": "published", "current_version_id": None, "retention_date": "2030-06-01"},
    {"id": _DOC5,  "created_at": _NOW, "updated_at": _NOW, "title": "직원 복무 규정",           "category_id": _CAT4, "owner_id": _E12, "status": "published", "current_version_id": None, "retention_date": "2035-01-01"},
    {"id": _DOC6,  "created_at": _NOW, "updated_at": _NOW, "title": "출장비 정산 지침",         "category_id": _CAT5, "owner_id": _E13, "status": "published", "current_version_id": None, "retention_date": "2031-12-31"},
    {"id": _DOC7,  "created_at": _NOW, "updated_at": _NOW, "title": "2025년 예산안",            "category_id": _CAT5, "owner_id": _E13, "status": "archived",  "current_version_id": None, "retention_date": "2032-12-31"},
    {"id": _DOC8,  "created_at": _NOW, "updated_at": _NOW, "title": "소장 작성 표준 서식",     "category_id": _CAT6, "owner_id": _EMP1, "status": "published", "current_version_id": None, "retention_date": None},
    {"id": _DOC9,  "created_at": _NOW, "updated_at": _NOW, "title": "준비서면 작성 가이드",     "category_id": _CAT6, "owner_id": _EMP1, "status": "draft",    "current_version_id": None, "retention_date": None},
    {"id": _DOC10, "created_at": _NOW, "updated_at": _NOW, "title": "법인 인사규정",            "category_id": _CAT4, "owner_id": _E12, "status": "published", "current_version_id": None, "retention_date": "2035-01-01"},
]

# ---------------------------------------------------------------------------
# document_version (v1 for all 10 docs; v2 for docs 1,2,3,5)
# ---------------------------------------------------------------------------

DOC_VERSIONS = [
    # DOC1 법인 정관 — v1, v2
    {"id": _vid(1),  "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC1,  "version_number": "v1.0", "uploaded_by": _E12,  "file_name": "법인정관_v1.pdf",           "file_size_bytes": 204800,  "mime_type": "application/pdf", "storage_key": "docs/doc1/v1.pdf",  "checksum": "abc001v1", "is_published": False},
    {"id": _vid(2),  "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC1,  "version_number": "v2.0", "uploaded_by": _E12,  "file_name": "법인정관_v2.pdf",           "file_size_bytes": 215040,  "mime_type": "application/pdf", "storage_key": "docs/doc1/v2.pdf",  "checksum": "abc001v2", "is_published": True},
    # DOC2 개인정보처리방침 — v1, v2
    {"id": _vid(3),  "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC2,  "version_number": "v1.0", "uploaded_by": _E12,  "file_name": "개인정보처리방침_v1.pdf",   "file_size_bytes": 102400,  "mime_type": "application/pdf", "storage_key": "docs/doc2/v1.pdf",  "checksum": "abc002v1", "is_published": False},
    {"id": _vid(4),  "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC2,  "version_number": "v2.0", "uploaded_by": _E12,  "file_name": "개인정보처리방침_v2.pdf",   "file_size_bytes": 112640,  "mime_type": "application/pdf", "storage_key": "docs/doc2/v2.pdf",  "checksum": "abc002v2", "is_published": True},
    # DOC3 위임계약서 — v1, v2
    {"id": _vid(5),  "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC3,  "version_number": "v1.0", "uploaded_by": _E7,   "file_name": "위임계약서_v1.docx",        "file_size_bytes": 51200,   "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "storage_key": "docs/doc3/v1.docx", "checksum": "abc003v1", "is_published": False},
    {"id": _vid(6),  "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC3,  "version_number": "v2.0", "uploaded_by": _E7,   "file_name": "위임계약서_v2.docx",        "file_size_bytes": 55296,   "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "storage_key": "docs/doc3/v2.docx", "checksum": "abc003v2", "is_published": True},
    # DOC4 보수약정서 — v1 only
    {"id": _vid(7),  "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC4,  "version_number": "v1.0", "uploaded_by": _E7,   "file_name": "보수약정서_v1.docx",        "file_size_bytes": 45056,   "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "storage_key": "docs/doc4/v1.docx", "checksum": "abc004v1", "is_published": True},
    # DOC5 복무규정 — v1, v2
    {"id": _vid(8),  "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC5,  "version_number": "v1.0", "uploaded_by": _E12,  "file_name": "복무규정_v1.pdf",           "file_size_bytes": 153600,  "mime_type": "application/pdf", "storage_key": "docs/doc5/v1.pdf",  "checksum": "abc005v1", "is_published": False},
    {"id": _vid(9),  "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC5,  "version_number": "v2.0", "uploaded_by": _E12,  "file_name": "복무규정_v2.pdf",           "file_size_bytes": 163840,  "mime_type": "application/pdf", "storage_key": "docs/doc5/v2.pdf",  "checksum": "abc005v2", "is_published": True},
    # DOC6~DOC10 — v1 only
    {"id": _vid(10), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC6,  "version_number": "v1.0", "uploaded_by": _E13,  "file_name": "출장비정산지침_v1.pdf",     "file_size_bytes": 81920,   "mime_type": "application/pdf", "storage_key": "docs/doc6/v1.pdf",  "checksum": "abc006v1", "is_published": True},
    {"id": _vid(11), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC7,  "version_number": "v1.0", "uploaded_by": _E13,  "file_name": "2025예산안_v1.xlsx",        "file_size_bytes": 307200,  "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "storage_key": "docs/doc7/v1.xlsx", "checksum": "abc007v1", "is_published": False},
    {"id": _vid(12), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC8,  "version_number": "v1.0", "uploaded_by": _EMP1, "file_name": "소장서식_v1.docx",          "file_size_bytes": 40960,   "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "storage_key": "docs/doc8/v1.docx", "checksum": "abc008v1", "is_published": True},
    {"id": _vid(13), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC9,  "version_number": "v1.0", "uploaded_by": _EMP1, "file_name": "준비서면가이드_v1.docx",    "file_size_bytes": 36864,   "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "storage_key": "docs/doc9/v1.docx", "checksum": "abc009v1", "is_published": False},
    {"id": _vid(14), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC10, "version_number": "v1.0", "uploaded_by": _E12,  "file_name": "인사규정_v1.pdf",           "file_size_bytes": 204800,  "mime_type": "application/pdf", "storage_key": "docs/doc10/v1.pdf", "checksum": "abc010v1", "is_published": True},
]

# current_version_id per document (after versions are inserted)
DOC_CURRENT_VERSION_MAP = {
    _DOC1:  _vid(2),
    _DOC2:  _vid(4),
    _DOC3:  _vid(6),
    _DOC4:  _vid(7),
    _DOC5:  _vid(9),
    _DOC6:  _vid(10),
    _DOC7:  _vid(11),
    _DOC8:  _vid(12),
    _DOC9:  _vid(13),
    _DOC10: _vid(14),
}

# ---------------------------------------------------------------------------
# document_access_rule
# ---------------------------------------------------------------------------

DOC_ACCESS_RULES = [
    {"id": _arid(1), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC1,  "principal_type": "department", "principal_id": _DEPT5, "permission": "read",  "expires_at": None},
    {"id": _arid(2), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC2,  "principal_type": "department", "principal_id": _DEPT5, "permission": "admin", "expires_at": None},
    {"id": _arid(3), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC3,  "principal_type": "department", "principal_id": _DEPT3, "permission": "edit",  "expires_at": None},
    {"id": _arid(4), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC5,  "principal_type": "department", "principal_id": _DEPT5, "permission": "admin", "expires_at": None},
    {"id": _arid(5), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC6,  "principal_type": "department", "principal_id": _DEPT5, "permission": "read",  "expires_at": None},
    {"id": _arid(6), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC7,  "principal_type": "employee",   "principal_id": _EMP1,  "permission": "read",  "expires_at": "2027-01-01T00:00:00+00:00"},
    {"id": _arid(7), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC8,  "principal_type": "department", "principal_id": _DEPT_LAW001, "permission": "read", "expires_at": None},
    {"id": _arid(8), "created_at": _NOW, "updated_at": _NOW, "document_id": _DOC9,  "principal_type": "employee",   "principal_id": _EMP2,  "permission": "edit",  "expires_at": None},
]

# ---------------------------------------------------------------------------
# approval_request  +  approval_step  +  approval_approver  +  approval_decision
# ---------------------------------------------------------------------------
# Request IDs
_AQ1 = _aqid(1)
_AQ2 = _aqid(2)
_AQ3 = _aqid(3)
_AQ4 = _aqid(4)
_AQ5 = _aqid(5)
_AQ6 = _aqid(6)
_AQ7 = _aqid(7)

APPROVAL_REQUESTS = [
    # AQ1: 이수진 연차 휴가 — 승인됨
    {"id": _AQ1, "created_at": _NOW, "updated_at": _NOW, "subject_type": "leave",    "subject_id": _EMP2, "requester_id": _EMP2, "status": "approved",    "title": "연차휴가 신청 (2024-08-05~06)",    "expires_at": None},
    # AQ2: 박민우 출장비 정산 — 승인됨
    {"id": _AQ2, "created_at": _NOW, "updated_at": _NOW, "subject_type": "expense",  "subject_id": _EMP3, "requester_id": _EMP3, "status": "approved",    "title": "부산 출장비 정산 150,000원",        "expires_at": None},
    # AQ3: 오세연 법인 명의 계약 체결 승인 — 승인됨
    {"id": _AQ3, "created_at": _NOW, "updated_at": _NOW, "subject_type": "contract", "subject_id": _C6,   "requester_id": _E6,   "status": "approved",    "title": "IT 서비스 계약 체결 승인 요청",    "expires_at": None},
    # AQ4: 한소율 연차 휴가 — 반려됨
    {"id": _AQ4, "created_at": _NOW, "updated_at": _NOW, "subject_type": "leave",    "subject_id": _E11,  "requester_id": _E11,  "status": "rejected",    "title": "연차휴가 신청 (2024-09-02~06)",    "expires_at": None},
    # AQ5: 강민서 외부 문서 발송 승인 — 진행중
    {"id": _AQ5, "created_at": _NOW, "updated_at": _NOW, "subject_type": "dispatch", "subject_id": _cdid(12), "requester_id": _E7, "status": "in-progress", "title": "SaaS 계약서 의뢰인 외부 발송 승인", "expires_at": "2026-07-31T23:59:59+00:00"},
    # AQ6: 배지수 구매 결의 — 대기
    {"id": _AQ6, "created_at": _NOW, "updated_at": _NOW, "subject_type": "purchase", "subject_id": _DEPT5, "requester_id": _E12,  "status": "pending",     "title": "사무용 복합기 구매 결의 (340만원)", "expires_at": None},
    # AQ7: 김대호 사건 위임 계약 서명 — 승인됨
    {"id": _AQ7, "created_at": _NOW, "updated_at": _NOW, "subject_type": "contract", "subject_id": _C1,   "requester_id": _EMP1, "status": "approved",    "title": "ABC 손해배상 사건 위임계약 서명 승인", "expires_at": None},
]

APPROVAL_STEPS = [
    # AQ1 — 1단계 팀장
    {"id": _asid(1),  "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ1, "sequence": 1, "name": "팀장 승인",   "status": "approved", "requires_all": True},
    # AQ2 — 1단계 팀장, 2단계 지원팀장
    {"id": _asid(2),  "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ2, "sequence": 1, "name": "팀장 승인",   "status": "approved", "requires_all": True},
    {"id": _asid(3),  "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ2, "sequence": 2, "name": "지원팀 확인", "status": "approved", "requires_all": True},
    # AQ3 — 1단계 파트너, 2단계 대표변호사
    {"id": _asid(4),  "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ3, "sequence": 1, "name": "담당파트너 승인", "status": "approved", "requires_all": True},
    {"id": _asid(5),  "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ3, "sequence": 2, "name": "대표변호사 최종승인", "status": "approved", "requires_all": True},
    # AQ4 — 1단계 팀장 (반려)
    {"id": _asid(6),  "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ4, "sequence": 1, "name": "팀장 승인",   "status": "rejected", "requires_all": True},
    # AQ5 — 1단계 담당파트너(완료), 2단계 대표(대기)
    {"id": _asid(7),  "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ5, "sequence": 1, "name": "담당파트너 승인", "status": "approved", "requires_all": True},
    {"id": _asid(8),  "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ5, "sequence": 2, "name": "대표변호사 최종승인", "status": "active",   "requires_all": True},
    # AQ6 — 1단계 지원팀장, 2단계 재무확인, 3단계 대표
    {"id": _asid(9),  "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ6, "sequence": 1, "name": "지원팀장 승인", "status": "pending",  "requires_all": True},
    {"id": _asid(10), "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ6, "sequence": 2, "name": "재무 확인",   "status": "pending",  "requires_all": True},
    {"id": _asid(11), "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ6, "sequence": 3, "name": "대표 결재",   "status": "pending",  "requires_all": True},
    # AQ7 — 1단계 파트너, 2단계 대표
    {"id": _asid(12), "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ7, "sequence": 1, "name": "담당파트너 확인", "status": "approved", "requires_all": True},
    {"id": _asid(13), "created_at": _NOW, "updated_at": _NOW, "request_id": _AQ7, "sequence": 2, "name": "대표변호사 승인", "status": "approved", "requires_all": True},
]

APPROVAL_APPROVERS = [
    # AQ1 step1
    {"id": _aaid(1),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(1),  "employee_id": _EMP1, "notified_at": _ts("2024-07-25"), "responded_at": _ts("2024-07-25")},
    # AQ2 step1
    {"id": _aaid(2),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(2),  "employee_id": _EMP1, "notified_at": _ts("2024-06-10"), "responded_at": _ts("2024-06-10")},
    # AQ2 step2
    {"id": _aaid(3),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(3),  "employee_id": _E12,  "notified_at": _ts("2024-06-11"), "responded_at": _ts("2024-06-11")},
    # AQ3 step1
    {"id": _aaid(4),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(4),  "employee_id": _E7,   "notified_at": _ts("2024-06-20"), "responded_at": _ts("2024-06-21")},
    # AQ3 step2
    {"id": _aaid(5),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(5),  "employee_id": _EMP1, "notified_at": _ts("2024-06-22"), "responded_at": _ts("2024-06-22")},
    # AQ4 step1
    {"id": _aaid(6),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(6),  "employee_id": _E10,  "notified_at": _ts("2024-08-20"), "responded_at": _ts("2024-08-20")},
    # AQ5 step1
    {"id": _aaid(7),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(7),  "employee_id": _E7,   "notified_at": _ts("2026-06-20"), "responded_at": _ts("2026-06-21")},
    # AQ5 step2
    {"id": _aaid(8),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(8),  "employee_id": _EMP1, "notified_at": _ts("2026-06-21"), "responded_at": None},
    # AQ6 step1
    {"id": _aaid(9),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(9),  "employee_id": _E12,  "notified_at": _ts("2026-06-22"), "responded_at": None},
    # AQ6 step2
    {"id": _aaid(10), "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(10), "employee_id": _E13,  "notified_at": None,              "responded_at": None},
    # AQ6 step3
    {"id": _aaid(11), "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(11), "employee_id": _EMP1, "notified_at": None,              "responded_at": None},
    # AQ7 step1
    {"id": _aaid(12), "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(12), "employee_id": _EMP1, "notified_at": _ts("2024-01-13"), "responded_at": _ts("2024-01-13")},
    # AQ7 step2
    {"id": _aaid(13), "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(13), "employee_id": _E4,   "notified_at": _ts("2024-01-14"), "responded_at": _ts("2024-01-14")},
    # AQ5 step1 추가: 두 번째 검토자 (requires_all=True 이지만 단독 승인자로도 충분)
    # 실제론 단일 approver per step이 일반적 — 18개로 맞춤
    {"id": _aaid(14), "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(1),  "employee_id": _E4,   "notified_at": _ts("2024-07-25"), "responded_at": _ts("2024-07-25")},
    # (step_id=_asid(1), employee_id=_E4) 충돌 방지 — 실제로는 E4 != EMP1 OK
]

# Trim to unique (step_id, employee_id) — _aaid(14) reuses asid(1) with _E4
# That's valid since uq is (step_id, employee_id): _aaid(1)=asid(1)/EMP1, _aaid(14)=asid(1)/_E4 => distinct OK

APPROVAL_DECISIONS = [
    # AQ1 s1 — approved
    {"id": _adid(1),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(1),  "approver_id": _aaid(1),  "decision": "approved", "comment": "승인합니다.",   "decided_at": _ts("2024-07-25")},
    # AQ2 s1 — approved
    {"id": _adid(2),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(2),  "approver_id": _aaid(2),  "decision": "approved", "comment": "확인 후 승인.", "decided_at": _ts("2024-06-10")},
    # AQ2 s2 — approved
    {"id": _adid(3),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(3),  "approver_id": _aaid(3),  "decision": "approved", "comment": "지원팀 확인.",  "decided_at": _ts("2024-06-11")},
    # AQ3 s1 — approved
    {"id": _adid(4),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(4),  "approver_id": _aaid(4),  "decision": "approved", "comment": "계약 내용 검토 완료. 승인.", "decided_at": _ts("2024-06-21")},
    # AQ3 s2 — approved
    {"id": _adid(5),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(5),  "approver_id": _aaid(5),  "decision": "approved", "comment": None,            "decided_at": _ts("2024-06-22")},
    # AQ4 s1 — rejected
    {"id": _adid(6),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(6),  "approver_id": _aaid(6),  "decision": "rejected", "comment": "재판 일정 충돌로 반려. 일정 조정 후 재신청 바람.", "decided_at": _ts("2024-08-20")},
    # AQ5 s1 — approved
    {"id": _adid(7),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(7),  "approver_id": _aaid(7),  "decision": "approved", "comment": "1차 승인.",     "decided_at": _ts("2026-06-21")},
    # AQ7 s1 — approved
    {"id": _adid(8),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(12), "approver_id": _aaid(12), "decision": "approved", "comment": "위임 계약 내용 확인. 승인.", "decided_at": _ts("2024-01-13")},
    # AQ7 s2 — approved
    {"id": _adid(9),  "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(13), "approver_id": _aaid(13), "decision": "approved", "comment": "최종 승인.",    "decided_at": _ts("2024-01-14")},
    # AQ1 s1 second approver decision
    {"id": _adid(10), "created_at": _NOW, "updated_at": _NOW, "step_id": _asid(1),  "approver_id": _aaid(14), "decision": "approved", "comment": None,            "decided_at": _ts("2024-07-25")},
]


# ---------------------------------------------------------------------------
# Upsert helpers
# ---------------------------------------------------------------------------

def _upsert_department(cur, dept: dict) -> None:
    cur.execute(
        """
        INSERT INTO hr_department (id, created_at, updated_at, code, name, parent_id, manager_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (dept["id"], dept["created_at"], dept["updated_at"],
         dept["code"], dept["name"], dept["parent_id"], dept["manager_id"]),
    )


def _upsert_employee(cur, emp: dict) -> None:
    cur.execute(
        """
        INSERT INTO hr_employee
          (id, created_at, updated_at, employee_number, full_name,
           department_id, position_id, hire_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (emp["id"], emp["created_at"], emp["updated_at"],
         emp["employee_number"], emp["full_name"],
         emp["department_id"], emp["position_id"],
         emp["hire_date"], emp["status"]),
    )


def _upsert_precedent(cur, prec: dict) -> None:
    cur.execute(
        """
        INSERT INTO legal_precedent
          (id, created_at, updated_at, citation, court,
           decided_date, case_type, holding, full_text, keywords)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (prec["id"], prec["created_at"], prec["updated_at"],
         prec["citation"], prec["court"], prec["decided_date"],
         prec["case_type"], prec["holding"], prec["full_text"], prec["keywords"]),
    )


def _upsert_case(cur, c: dict) -> None:
    cur.execute(
        """
        INSERT INTO legal_case
          (id, created_at, updated_at, case_number, title,
           case_type, status, filed_date, court,
           next_hearing_date, assigned_attorney_id, client_contact_id, summary)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (c["id"], c["created_at"], c["updated_at"],
         c["case_number"], c["title"],
         c["case_type"], c["status"], c["filed_date"], c["court"],
         c["next_hearing_date"], c["assigned_attorney_id"],
         c["client_contact_id"], c["summary"]),
    )


def _upsert_case_party(cur, p: dict) -> None:
    cur.execute(
        """
        INSERT INTO legal_case_party
          (id, created_at, updated_at, case_id, role, name, contact_id, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (p["id"], p["created_at"], p["updated_at"],
         p["case_id"], p["role"], p["name"], p["contact_id"], p["notes"]),
    )


def _upsert_case_document(cur, d: dict) -> None:
    cur.execute(
        """
        INSERT INTO legal_case_document
          (id, created_at, updated_at, case_id, document_type, title,
           filed_at, storage_key, notes, content_text, ingest_status, ingested_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (d["id"], d["created_at"], d["updated_at"],
         d["case_id"], d["document_type"], d["title"],
         d["filed_at"], d["storage_key"], d["notes"],
         d["content_text"], d["ingest_status"], d["ingested_at"]),
    )


def _upsert_doc_category(cur, c: dict) -> None:
    cur.execute(
        """
        INSERT INTO document_category
          (id, created_at, updated_at, code, name, parent_id, default_retention_days)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (c["id"], c["created_at"], c["updated_at"],
         c["code"], c["name"], c["parent_id"], c["default_retention_days"]),
    )


def _upsert_doc_document(cur, d: dict) -> None:
    cur.execute(
        """
        INSERT INTO document_document
          (id, created_at, updated_at, title, category_id, owner_id,
           status, current_version_id, retention_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (d["id"], d["created_at"], d["updated_at"],
         d["title"], d["category_id"], d["owner_id"],
         d["status"], d["current_version_id"], d["retention_date"]),
    )


def _upsert_doc_version(cur, v: dict) -> None:
    cur.execute(
        """
        INSERT INTO document_version
          (id, created_at, updated_at, document_id, version_number,
           uploaded_by, file_name, file_size_bytes, mime_type,
           storage_key, checksum, is_published)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (v["id"], v["created_at"], v["updated_at"],
         v["document_id"], v["version_number"],
         v["uploaded_by"], v["file_name"], v["file_size_bytes"],
         v["mime_type"], v["storage_key"], v["checksum"], v["is_published"]),
    )


def _upsert_doc_access_rule(cur, r: dict) -> None:
    cur.execute(
        """
        INSERT INTO document_access_rule
          (id, created_at, updated_at, document_id,
           principal_type, principal_id, permission, expires_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (r["id"], r["created_at"], r["updated_at"],
         r["document_id"], r["principal_type"], r["principal_id"],
         r["permission"], r["expires_at"]),
    )


def _upsert_approval_request(cur, r: dict) -> None:
    cur.execute(
        """
        INSERT INTO approval_request
          (id, created_at, updated_at, subject_type, subject_id,
           requester_id, status, title, expires_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (r["id"], r["created_at"], r["updated_at"],
         r["subject_type"], r["subject_id"],
         r["requester_id"], r["status"], r["title"], r["expires_at"]),
    )


def _upsert_approval_step(cur, s: dict) -> None:
    cur.execute(
        """
        INSERT INTO approval_step
          (id, created_at, updated_at, request_id, sequence,
           name, status, requires_all)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (s["id"], s["created_at"], s["updated_at"],
         s["request_id"], s["sequence"],
         s["name"], s["status"], s["requires_all"]),
    )


def _upsert_approval_approver(cur, a: dict) -> None:
    cur.execute(
        """
        INSERT INTO approval_approver
          (id, created_at, updated_at, step_id, employee_id,
           notified_at, responded_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (a["id"], a["created_at"], a["updated_at"],
         a["step_id"], a["employee_id"],
         a["notified_at"], a["responded_at"]),
    )


def _upsert_approval_decision(cur, d: dict) -> None:
    cur.execute(
        """
        INSERT INTO approval_decision
          (id, created_at, updated_at, step_id, approver_id,
           decision, comment, decided_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (d["id"], d["created_at"], d["updated_at"],
         d["step_id"], d["approver_id"],
         d["decision"], d["comment"], d["decided_at"]),
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def seed_full(conn) -> None:
    """Insert all full-demo seed rows.  Call AFTER baseline seed in setup_lawfirm.py."""

    with conn:
        cur = conn.cursor()

        # ---- HR ----
        print("  [full] departments (new 4) ...")
        for dept in NEW_DEPARTMENTS:
            _upsert_department(cur, dept)
        conn.commit()

        print("  [full] employees (new 11) ...")
        for emp in NEW_EMPLOYEES:
            _upsert_employee(cur, emp)
        conn.commit()

        print("  [full] department manager_id updates ...")
        for emp_id, dept_id in DEPT_MANAGER_UPDATES:
            cur.execute(
                "UPDATE hr_department SET manager_id = %s WHERE id = %s AND manager_id IS NULL",
                (emp_id, dept_id),
            )
        conn.commit()

        # ---- Precedents ----
        print("  [full] precedents (new 7) ...")
        for prec in NEW_PRECEDENTS:
            _upsert_precedent(cur, prec)
        conn.commit()

        # ---- Cases ----
        print("  [full] legal cases (new 7) ...")
        for c in NEW_CASES:
            _upsert_case(cur, c)
        conn.commit()

        print("  [full] case parties (28) ...")
        for p in CASE_PARTIES:
            _upsert_case_party(cur, p)
        conn.commit()

        print("  [full] case documents (22) ...")
        for d in CASE_DOCUMENTS:
            _upsert_case_document(cur, d)
        conn.commit()

        # ---- Document domain ----
        print("  [full] document categories (6) ...")
        for c in DOC_CATEGORIES:
            _upsert_doc_category(cur, c)
        conn.commit()

        print("  [full] documents (10, current_version_id=NULL initially) ...")
        for d in DOC_DOCUMENTS:
            _upsert_doc_document(cur, d)
        conn.commit()

        print("  [full] document versions (14) ...")
        for v in DOC_VERSIONS:
            _upsert_doc_version(cur, v)
        conn.commit()

        print("  [full] document current_version_id backfill ...")
        for doc_id, ver_id in DOC_CURRENT_VERSION_MAP.items():
            cur.execute(
                "UPDATE document_document SET current_version_id = %s WHERE id = %s AND current_version_id IS NULL",
                (ver_id, doc_id),
            )
        conn.commit()

        print("  [full] document access rules (8) ...")
        for r in DOC_ACCESS_RULES:
            _upsert_doc_access_rule(cur, r)
        conn.commit()

        # ---- Approval domain ----
        print("  [full] approval requests (7) ...")
        for r in APPROVAL_REQUESTS:
            _upsert_approval_request(cur, r)
        conn.commit()

        print("  [full] approval steps (13) ...")
        for s in APPROVAL_STEPS:
            _upsert_approval_step(cur, s)
        conn.commit()

        print("  [full] approval approvers (14) ...")
        for a in APPROVAL_APPROVERS:
            _upsert_approval_approver(cur, a)
        conn.commit()

        print("  [full] approval decisions (10) ...")
        for d in APPROVAL_DECISIONS:
            _upsert_approval_decision(cur, d)
        conn.commit()

    # Summary
    print("\n[full seed] complete.")
    print(f"  hr_department        : {1 + len(NEW_DEPARTMENTS)}")
    print(f"  hr_employee          : {3 + len(NEW_EMPLOYEES)}")
    print(f"  legal_precedent      : {5 + len(NEW_PRECEDENTS)}")
    print(f"  legal_case           : {3 + len(NEW_CASES)}")
    print(f"  legal_case_party     : {len(CASE_PARTIES)}")
    print(f"  legal_case_document  : {len(CASE_DOCUMENTS)}")
    print(f"  document_category    : {len(DOC_CATEGORIES)}")
    print(f"  document_document    : {len(DOC_DOCUMENTS)}")
    print(f"  document_version     : {len(DOC_VERSIONS)}")
    print(f"  document_access_rule : {len(DOC_ACCESS_RULES)}")
    print(f"  approval_request     : {len(APPROVAL_REQUESTS)}")
    print(f"  approval_step        : {len(APPROVAL_STEPS)}")
    print(f"  approval_approver    : {len(APPROVAL_APPROVERS)}")
    print(f"  approval_decision    : {len(APPROVAL_DECISIONS)}")
