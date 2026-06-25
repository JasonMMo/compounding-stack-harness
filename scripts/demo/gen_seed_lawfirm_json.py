"""
scripts/demo/gen_seed_lawfirm_json.py — Seed JSON generator for lawfirm-demo.

Assembles base (setup_lawfirm.py) + new (seed_lawfirm_full.py) records into
the InMemoryEntityStore-compatible format and writes seed-data/lawfirm-demo.json.

Entity keys match screen-manifest.json (hyphenated) and SEED_FILE spec.

Usage:
    python scripts/demo/gen_seed_lawfirm_json.py

Output:
    seed-data/lawfirm-demo.json  (overwritten, deterministic)
"""

from __future__ import annotations

import json
import pathlib
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_SCRIPTS_DEMO = _REPO_ROOT / "scripts" / "demo"
_OUT_PATH = _REPO_ROOT / "seed-data" / "lawfirm-demo.json"

# ---------------------------------------------------------------------------
# Import seed_lawfirm_full — real import (not py_compile) to catch NameErrors
# ---------------------------------------------------------------------------

def _import_seed_full():
    # Real import (not py_compile) so module-level NameErrors surface — same
    # pattern as dfd_verify.py. _E3-style defects must fail loudly here.
    sys.path.insert(0, str(_SCRIPTS_DEMO))
    import seed_lawfirm_full as mod

    return mod


# ---------------------------------------------------------------------------
# Base records (mirrors setup_lawfirm.py's DEPARTMENTS / EMPLOYEES /
# PRECEDENTS / CASES lists — same fixed UUIDs, same fields)
# ---------------------------------------------------------------------------

_NOW_BASE = "2024-01-01T09:00:00+00:00"  # stable ts for base records

_DEPT_ID  = "11111111-0000-0000-0000-000000000001"
_EMP_IDS  = [
    "22222222-0000-0000-0000-000000000001",
    "22222222-0000-0000-0000-000000000002",
    "22222222-0000-0000-0000-000000000003",
]
_PREC_IDS = [
    "33333333-0000-0000-0000-000000000001",
    "33333333-0000-0000-0000-000000000002",
    "33333333-0000-0000-0000-000000000003",
    "33333333-0000-0000-0000-000000000004",
    "33333333-0000-0000-0000-000000000005",
]
_CASE_IDS = [
    "44444444-0000-0000-0000-000000000001",
    "44444444-0000-0000-0000-000000000002",
    "44444444-0000-0000-0000-000000000003",
]

BASE_DEPARTMENTS = [
    {
        "id": _DEPT_ID,
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "code": "LAW001", "name": "소송부",
        "parent_id": None,
        "manager_id": _EMP_IDS[0],  # set after employees in setup_lawfirm
    },
]

BASE_EMPLOYEES = [
    {
        "id": _EMP_IDS[0],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "employee_number": "EMP001", "full_name": "김대호",
        "department_id": _DEPT_ID, "position_id": None,
        "hire_date": "2015-03-01", "status": "active",
    },
    {
        "id": _EMP_IDS[1],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "employee_number": "EMP002", "full_name": "이수진",
        "department_id": _DEPT_ID, "position_id": None,
        "hire_date": "2018-07-15", "status": "active",
    },
    {
        "id": _EMP_IDS[2],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "employee_number": "EMP003", "full_name": "박민우",
        "department_id": _DEPT_ID, "position_id": None,
        "hire_date": "2020-01-10", "status": "active",
    },
]

BASE_PRECEDENTS = [
    {
        "id": _PREC_IDS[0],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "citation": "대법원 2020다12345",
        "court": "대법원",
        "decided_date": "2020-05-21",
        "case_type": "civil",
        "holding": (
            "불법행위로 인한 손해배상 청구 사건에서 피고의 과실이 인정되고 "
            "원고의 손해와 인과관계가 있는 경우 피고는 손해배상 책임을 진다."
        ),
        "full_text": None,
        "keywords": "손해배상 불법행위 과실 인과관계",
    },
    {
        "id": _PREC_IDS[1],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "citation": "서울고등법원 2019나56789",
        "court": "서울고등법원",
        "decided_date": "2019-11-14",
        "case_type": "civil",
        "holding": (
            "계약 불이행으로 인한 손해배상에서 채무자의 귀책사유가 존재하면 "
            "채권자는 손해배상을 청구할 수 있다. 다만 채권자도 손해 경감 의무가 있다."
        ),
        "full_text": None,
        "keywords": "계약불이행 손해배상 귀책사유 채무불이행",
    },
    {
        "id": _PREC_IDS[2],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "citation": "대법원 2018다98765",
        "court": "대법원",
        "decided_date": "2018-09-07",
        "case_type": "commercial",
        "holding": (
            "상사 계약에서 위약금 조항은 손해배상액의 예정으로 유효하며, "
            "당사자 간 합의된 위약금은 원칙적으로 감액하지 않는다."
        ),
        "full_text": None,
        "keywords": "위약금 손해배상액예정 상사계약 감액",
    },
    {
        "id": _PREC_IDS[3],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "citation": "헌법재판소 2017헌바321",
        "court": "헌법재판소",
        "decided_date": "2017-06-29",
        "case_type": "administrative",
        "holding": (
            "행정처분에 대한 취소소송에서 처분 당시 법령을 기준으로 "
            "적법 여부를 판단하며, 재량권 일탈·남용 여부를 심사한다."
        ),
        "full_text": None,
        "keywords": "행정처분 취소소송 재량권 일탈남용",
    },
    {
        "id": _PREC_IDS[4],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "citation": "대법원 2021도11111",
        "court": "대법원",
        "decided_date": "2021-03-18",
        "case_type": "criminal",
        "holding": (
            "형사 사건에서 피고인의 자백은 유죄의 유일한 증거가 될 수 없으며, "
            "보강 증거가 있어야 유죄를 인정할 수 있다."
        ),
        "full_text": None,
        "keywords": "자백 보강증거 형사 유죄",
    },
]

BASE_CASES = [
    {
        "id": _CASE_IDS[0],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "case_number": "CASE-2024-001",
        "title": "ABC주식회사 손해배상 청구 사건",
        "case_type": "civil",
        "status": "active",
        "filed_date": "2024-01-15",
        "court": "서울중앙지방법원",
        "next_hearing_date": "2024-08-20",
        "assigned_attorney_id": _EMP_IDS[0],
        "client_contact_id": None,
        "summary": "공급 계약 불이행으로 인한 손해배상 청구. 계약금액 5억원 분쟁.",
    },
    {
        "id": _CASE_IDS[1],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "case_number": "CASE-2024-002",
        "title": "부동산 매매 계약 위반 사건",
        "case_type": "civil",
        "status": "intake",
        "filed_date": "2024-03-10",
        "court": "수원지방법원",
        "next_hearing_date": None,
        "assigned_attorney_id": _EMP_IDS[1],
        "client_contact_id": None,
        "summary": "부동산 매매 계약 해제 및 위약금 반환 청구 사건.",
    },
    {
        "id": _CASE_IDS[2],
        "created_at": _NOW_BASE, "updated_at": _NOW_BASE,
        "case_number": "CASE-2024-003",
        "title": "행정 제재처분 취소 청구",
        "case_type": "administrative",
        "status": "active",
        "filed_date": "2024-02-20",
        "court": "서울행정법원",
        "next_hearing_date": "2024-09-05",
        "assigned_attorney_id": _EMP_IDS[2],
        "client_contact_id": None,
        "summary": "영업정지 처분에 대한 취소소송. 재량권 남용 주장.",
    },
]


# ---------------------------------------------------------------------------
# Field projection — strip postgres-only fields (created_at/updated_at are
# fine; store ignores unknown fields gracefully). Apply manifest key mapping.
# ---------------------------------------------------------------------------

def _project_department(r: dict) -> dict:
    return {
        "id": r["id"],
        "code": r["code"],
        "name": r["name"],
        "parent_id": r.get("parent_id"),
        "manager_id": r.get("manager_id"),
    }


def _project_employee(r: dict) -> dict:
    return {
        "id": r["id"],
        "employee_number": r["employee_number"],
        "full_name": r["full_name"],
        "department_id": r.get("department_id"),
        "position_id": r.get("position_id"),
        "hire_date": r.get("hire_date"),
        "status": r.get("status"),
    }


def _project_precedent(r: dict) -> dict:
    return {
        "id": r["id"],
        "citation": r["citation"],
        "court": r["court"],
        "decided_date": r.get("decided_date"),
        "case_type": r.get("case_type"),
        "holding": r.get("holding"),
        "full_text": r.get("full_text"),
        "keywords": r.get("keywords"),
    }


def _project_legal_case(r: dict) -> dict:
    return {
        "id": r["id"],
        "case_number": r["case_number"],
        "title": r["title"],
        "case_type": r.get("case_type"),
        "status": r.get("status"),
        "filed_date": r.get("filed_date"),
        "court": r.get("court"),
        "next_hearing_date": r.get("next_hearing_date"),
        "assigned_attorney_id": r.get("assigned_attorney_id"),
        "client_contact_id": r.get("client_contact_id"),
        "summary": r.get("summary"),
    }


def _project_case_party(r: dict) -> dict:
    return {
        "id": r["id"],
        "case_id": r["case_id"],
        "role": r["role"],
        "name": r["name"],
        "contact_id": r.get("contact_id"),
        "notes": r.get("notes"),
    }


def _project_case_document(r: dict) -> dict:
    return {
        "id": r["id"],
        "case_id": r["case_id"],
        "document_type": r["document_type"],
        "title": r["title"],
        "filed_at": r.get("filed_at"),
        "storage_key": r.get("storage_key"),
        "notes": r.get("notes"),
        "content_text": r.get("content_text"),
        "ingest_status": r.get("ingest_status"),
        "ingested_at": r.get("ingested_at"),
    }


def _project_doc_category(r: dict) -> dict:
    return {
        "id": r["id"],
        "code": r["code"],
        "name": r["name"],
        "parent_id": r.get("parent_id"),
        "default_retention_days": r.get("default_retention_days"),
    }


def _project_document(r: dict) -> dict:
    return {
        "id": r["id"],
        "title": r["title"],
        "category_id": r.get("category_id"),
        "owner_id": r.get("owner_id"),
        "status": r.get("status"),
        "current_version_id": r.get("current_version_id"),
        "retention_date": r.get("retention_date"),
    }


def _project_doc_version(r: dict) -> dict:
    return {
        "id": r["id"],
        "document_id": r["document_id"],
        "version_number": r["version_number"],
        "uploaded_by": r.get("uploaded_by"),
        "file_name": r.get("file_name"),
        "file_size_bytes": r.get("file_size_bytes"),
        "mime_type": r.get("mime_type"),
        "storage_key": r.get("storage_key"),
        "checksum": r.get("checksum"),
        "is_published": r.get("is_published"),
    }


def _project_access_rule(r: dict) -> dict:
    return {
        "id": r["id"],
        "document_id": r["document_id"],
        "principal_type": r["principal_type"],
        "principal_id": r["principal_id"],
        "permission": r["permission"],
        "expires_at": r.get("expires_at"),
    }


def _project_approval_request(r: dict) -> dict:
    return {
        "id": r["id"],
        "subject_type": r["subject_type"],
        "subject_id": r["subject_id"],
        "requester_id": r["requester_id"],
        "status": r["status"],
        "title": r["title"],
        "expires_at": r.get("expires_at"),
    }


def _project_approval_step(r: dict) -> dict:
    return {
        "id": r["id"],
        "request_id": r["request_id"],
        "sequence": r["sequence"],
        "name": r["name"],
        "status": r["status"],
        "requires_all": r["requires_all"],
    }


def _project_approver(r: dict) -> dict:
    return {
        "id": r["id"],
        "step_id": r["step_id"],
        "employee_id": r["employee_id"],
        "notified_at": r.get("notified_at"),
        "responded_at": r.get("responded_at"),
    }


def _project_approval_decision(r: dict) -> dict:
    return {
        "id": r["id"],
        "step_id": r["step_id"],
        "approver_id": r["approver_id"],
        "decision": r["decision"],
        "comment": r.get("comment"),
        "decided_at": r.get("decided_at"),
    }


def _project_time_entry(r: dict) -> dict:
    return {
        "id": r["id"],
        "case_id": r["case_id"],
        "employee_id": r["employee_id"],
        "work_date": r["work_date"],
        "minutes": r["minutes"],
        "description": r["description"],
        "billable": r["billable"],
        "hourly_rate": r["hourly_rate"],
        "amount": r["amount"],
        "status": r["status"],
    }


def _project_invoice(r: dict) -> dict:
    return {
        "id": r["id"],
        "case_id": r["case_id"],
        "client_name": r["client_name"],
        "issue_date": r["issue_date"],
        "period_start": r.get("period_start"),
        "period_end": r.get("period_end"),
        "subtotal": r["subtotal"],
        "tax": r["tax"],
        "total": r["total"],
        "status": r["status"],
    }


# ---------------------------------------------------------------------------
# Backfill current_version_id into document records
# ---------------------------------------------------------------------------

def _backfill_current_version(documents: list, version_map: dict) -> list:
    """Return new list with current_version_id set per DOC_CURRENT_VERSION_MAP."""
    result = []
    for doc in documents:
        d = dict(doc)
        if d["id"] in version_map:
            d["current_version_id"] = version_map[d["id"]]
        result.append(d)
    return result


# ---------------------------------------------------------------------------
# Expected counts (CTO gate)
# ---------------------------------------------------------------------------

EXPECTED = {
    "department":        5,
    "employee":         14,
    "precedent":        12,
    "legal-case":       10,
    "case-party":       28,
    "case-document":    22,
    "document-category": 6,
    "document":         10,
    "document-version": 14,
    "access-rule":       8,
    "approval-request":  7,
    "approval-step":    13,
    "approver":         14,
    "approval-decision":10,
    "time-entry":       25,
    "case-invoice":      6,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Real import (catches NameError / import chain failures)
    S = _import_seed_full()

    # 2. Assemble departments (base 1 + new 4)
    #    Apply manager_id updates from DEPT_MANAGER_UPDATES to new depts
    new_dept_manager_map = {dept_id: emp_id for emp_id, dept_id in S.DEPT_MANAGER_UPDATES}
    new_departments = []
    for dept in S.NEW_DEPARTMENTS:
        d = dict(dept)
        if d["id"] in new_dept_manager_map:
            d["manager_id"] = new_dept_manager_map[d["id"]]
        new_departments.append(d)

    departments = [_project_department(r) for r in BASE_DEPARTMENTS + new_departments]

    # 3. Employees (base 3 + new 11)
    employees = [_project_employee(r) for r in BASE_EMPLOYEES + S.NEW_EMPLOYEES]

    # 4. Precedents (base 5 + new 7)
    precedents = [_project_precedent(r) for r in BASE_PRECEDENTS + S.NEW_PRECEDENTS]

    # 5. Legal cases (base 3 + new 7)
    legal_cases = [_project_legal_case(r) for r in BASE_CASES + S.NEW_CASES]

    # 6. Case parties (all from seed_full, covers all 10 cases)
    case_parties = [_project_case_party(r) for r in S.CASE_PARTIES]

    # 7. Case documents (all from seed_full)
    case_documents = [_project_case_document(r) for r in S.CASE_DOCUMENTS]

    # 8. Document categories
    doc_categories = [_project_doc_category(r) for r in S.DOC_CATEGORIES]

    # 9. Documents — backfill current_version_id
    documents_raw = _backfill_current_version(S.DOC_DOCUMENTS, S.DOC_CURRENT_VERSION_MAP)
    documents = [_project_document(r) for r in documents_raw]

    # 10. Document versions
    doc_versions = [_project_doc_version(r) for r in S.DOC_VERSIONS]

    # 11. Access rules
    access_rules = [_project_access_rule(r) for r in S.DOC_ACCESS_RULES]

    # 12. Approval requests
    approval_requests = [_project_approval_request(r) for r in S.APPROVAL_REQUESTS]

    # 13. Approval steps
    approval_steps = [_project_approval_step(r) for r in S.APPROVAL_STEPS]

    # 14. Approvers
    approvers = [_project_approver(r) for r in S.APPROVAL_APPROVERS]

    # 15. Approval decisions
    approval_decisions = [_project_approval_decision(r) for r in S.APPROVAL_DECISIONS]

    # 16. Time entries (K3)
    time_entries = [_project_time_entry(r) for r in S.TIME_ENTRIES]

    # 17. Invoices (K3)
    invoices = [_project_invoice(r) for r in S.INVOICES]

    # --- Assemble payload ---
    payload = {
        "department":         departments,
        "employee":           employees,
        "precedent":          precedents,
        "legal-case":         legal_cases,
        "case-party":         case_parties,
        "case-document":      case_documents,
        "document-category":  doc_categories,
        "document":           documents,
        "document-version":   doc_versions,
        "access-rule":        access_rules,
        "approval-request":   approval_requests,
        "approval-step":      approval_steps,
        "approver":           approvers,
        "approval-decision":  approval_decisions,
        "time-entry":         time_entries,
        "case-invoice":       invoices,
    }

    # --- Self-assert (CTO gate) ---
    errors = []
    actual_counts = {}
    for key, records in payload.items():
        actual = len(records)
        actual_counts[key] = actual
        expected = EXPECTED[key]
        if actual != expected:
            errors.append(f"  {key}: expected {expected}, got {actual}")

    if errors:
        print("ASSERT FAILED — count mismatch:", flush=True)
        for e in errors:
            print(e, flush=True)
        raise AssertionError("Seed count mismatch — see above")

    # --- Write ---
    _OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _OUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # --- Summary ---
    print(f"[gen_seed] Written: {_OUT_PATH}", flush=True)
    print("[gen_seed] Record counts (all match expected):", flush=True)
    for key, count in actual_counts.items():
        print(f"  {key:<22} : {count}", flush=True)


if __name__ == "__main__":
    main()
