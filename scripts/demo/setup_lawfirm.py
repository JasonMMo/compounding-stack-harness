"""
scripts/demo/setup_lawfirm.py — DB initializer for lawfirm-demo A안.

Actions (idempotent — safe to re-run):
  1. Creates all tables from out/lawfirm-demo/ddl/postgres.sql
  2. Adds tsvector GIN index on legal_precedent for Korean full-text search
  3. Inserts seed data: 1 department, 3 employees, 5 precedents, 3 legal cases

Usage:
    python scripts/demo/setup_lawfirm.py

Environment:
    DATABASE_URL — psycopg2 DSN (default: postgresql://localhost/lawfirm_demo)
"""

from __future__ import annotations

import os
import pathlib
import sys
import uuid
from datetime import date, datetime, timezone

# Windows consoles default to a legacy codepage (e.g. cp949) that cannot
# encode the em-dash/Korean glyphs this script prints — force UTF-8.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=pathlib.Path(__file__).resolve().parents[2] / ".env", override=False)
except ImportError:
    pass  # python-dotenv optional; set DATABASE_URL manually if absent

try:
    import psycopg2
    from psycopg2 import sql as pgsql
except ImportError:
    sys.exit(
        "psycopg2 not found. Install with: pip install psycopg2-binary"
    )

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://localhost/lawfirm_demo"
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_DDL_PATH = _REPO_ROOT / "out" / "lawfirm-demo" / "ddl" / "postgres.sql"

_GIN_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_precedent_fts ON legal_precedent
  USING GIN (to_tsvector('simple', holding || ' ' || COALESCE(keywords, '')));
"""


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

def _uid() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# Fixed UUIDs so re-runs are idempotent (upsert by id)
_DEPT_ID = "11111111-0000-0000-0000-000000000001"
_EMP_IDS = [
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

DEPARTMENTS = [
    {
        "id": _DEPT_ID,
        "created_at": _now(),
        "updated_at": _now(),
        "code": "LAW001",
        "name": "소송부",
        "parent_id": None,
        "manager_id": None,  # set after employees inserted
    }
]

EMPLOYEES = [
    {
        "id": _EMP_IDS[0],
        "created_at": _now(),
        "updated_at": _now(),
        "employee_number": "EMP001",
        "full_name": "김대호",
        "department_id": _DEPT_ID,
        "position_id": None,
        "hire_date": "2015-03-01",
        "status": "active",
    },
    {
        "id": _EMP_IDS[1],
        "created_at": _now(),
        "updated_at": _now(),
        "employee_number": "EMP002",
        "full_name": "이수진",
        "department_id": _DEPT_ID,
        "position_id": None,
        "hire_date": "2018-07-15",
        "status": "active",
    },
    {
        "id": _EMP_IDS[2],
        "created_at": _now(),
        "updated_at": _now(),
        "employee_number": "EMP003",
        "full_name": "박민우",
        "department_id": _DEPT_ID,
        "position_id": None,
        "hire_date": "2020-01-10",
        "status": "active",
    },
]

PRECEDENTS = [
    {
        "id": _PREC_IDS[0],
        "created_at": _now(),
        "updated_at": _now(),
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
        "created_at": _now(),
        "updated_at": _now(),
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
        "created_at": _now(),
        "updated_at": _now(),
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
        "created_at": _now(),
        "updated_at": _now(),
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
        "created_at": _now(),
        "updated_at": _now(),
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

CASES = [
    {
        "id": _CASE_IDS[0],
        "created_at": _now(),
        "updated_at": _now(),
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
        "created_at": _now(),
        "updated_at": _now(),
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
        "created_at": _now(),
        "updated_at": _now(),
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
# DB helpers
# ---------------------------------------------------------------------------

def _connect() -> "psycopg2.connection":
    print(f"Connecting to: {DATABASE_URL}")
    return psycopg2.connect(DATABASE_URL)


def _exec_ddl(cur, ddl_text: str) -> None:
    """Execute DDL statements one-by-one, skipping ALTER TABLE add FK (uses deferred refs)."""
    statements = [s.strip() for s in ddl_text.split(";") if s.strip()]
    for stmt in statements:
        # Skip comments-only fragments
        lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
        clean = "\n".join(lines).strip()
        if not clean:
            continue
        try:
            cur.execute(clean)
        except Exception as exc:
            # On re-run, "already exists" errors are acceptable for CREATE TABLE/INDEX
            if "already exists" in str(exc).lower():
                print(f"  [skip] already exists: {clean[:60].replace(chr(10),' ')}...")
                cur.connection.rollback()
            else:
                raise


def _upsert_department(cur, dept: dict) -> None:
    cur.execute(
        """
        INSERT INTO hr_department (id, created_at, updated_at, code, name, parent_id, manager_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (
            dept["id"], dept["created_at"], dept["updated_at"],
            dept["code"], dept["name"], dept["parent_id"], dept["manager_id"],
        ),
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
        (
            emp["id"], emp["created_at"], emp["updated_at"],
            emp["employee_number"], emp["full_name"],
            emp["department_id"], emp["position_id"],
            emp["hire_date"], emp["status"],
        ),
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
        (
            prec["id"], prec["created_at"], prec["updated_at"],
            prec["citation"], prec["court"], prec["decided_date"],
            prec["case_type"], prec["holding"], prec["full_text"], prec["keywords"],
        ),
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
        (
            c["id"], c["created_at"], c["updated_at"],
            c["case_number"], c["title"],
            c["case_type"], c["status"], c["filed_date"], c["court"],
            c["next_hearing_date"], c["assigned_attorney_id"],
            c["client_contact_id"], c["summary"],
        ),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ddl_text = _DDL_PATH.read_text(encoding="utf-8")

    conn = _connect()
    try:
        with conn:
            cur = conn.cursor()

            print("Step 1: executing DDL from postgres.sql ...")
            # Split DDL into individual transactions to handle "already exists"
            statements = [s.strip() for s in ddl_text.split(";") if s.strip()]
            for stmt in statements:
                lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
                clean = "\n".join(lines).strip()
                if not clean:
                    continue
                try:
                    cur.execute(clean)
                    conn.commit()
                except Exception as exc:
                    conn.rollback()
                    if "already exists" in str(exc).lower():
                        print(f"  [skip] already exists — {clean[:70].replace(chr(10),' ')}...")
                    else:
                        print(f"  [warn] DDL error (continuing): {exc}")

            print("Step 2: adding tsvector GIN index ...")
            try:
                cur.execute(_GIN_INDEX_SQL)
                conn.commit()
                print("  [ok] GIN index created.")
            except Exception as exc:
                conn.rollback()
                if "already exists" in str(exc).lower():
                    print("  [skip] GIN index already exists.")
                else:
                    print(f"  [warn] GIN index error: {exc}")

            print("Step 3: inserting seed data ...")

            print("  departments ...")
            for dept in DEPARTMENTS:
                _upsert_department(cur, dept)
            conn.commit()

            print("  employees ...")
            for emp in EMPLOYEES:
                _upsert_employee(cur, emp)
            conn.commit()

            # Update department manager_id to first employee after employees exist
            cur.execute(
                "UPDATE hr_department SET manager_id = %s WHERE id = %s AND manager_id IS NULL",
                (_EMP_IDS[0], _DEPT_ID),
            )
            conn.commit()

            print("  precedents ...")
            for prec in PRECEDENTS:
                _upsert_precedent(cur, prec)
            conn.commit()

            print("  legal cases ...")
            for c in CASES:
                _upsert_case(cur, c)
            conn.commit()

            print("\nSetup complete.")
            print(f"  Departments : {len(DEPARTMENTS)}")
            print(f"  Employees   : {len(EMPLOYEES)}")
            print(f"  Precedents  : {len(PRECEDENTS)}")
            print(f"  Legal cases : {len(CASES)}")
            print("\nVerify with:")
            print("  SELECT citation, case_type FROM legal_precedent;")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
