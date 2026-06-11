"""
scripts/preflight.py — L4 live test pre-flight checker.

Verifies all prerequisites so Claude can run L4 without user intervention.
Run before any L4 live test or demo launch:

    python scripts/preflight.py
    python scripts/preflight.py --profile lawfirm-demo

Exit 0 = all checks pass. Exit 1 = one or more failed (details printed).
"""

from __future__ import annotations

import argparse
import importlib
import os
import pathlib
import socket
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PASS = "  [ok]"
_FAIL = "  [FAIL]"
_SKIP = "  [skip]"
_failures: list[str] = []


def ok(msg: str) -> None:
    print(f"{_PASS} {msg}")


def fail(msg: str) -> None:
    print(f"{_FAIL} {msg}")
    _failures.append(msg)


def skip(msg: str) -> None:
    print(f"{_SKIP} {msg}")


def _mask_password(url: str) -> str:
    """Replace password in DSN URL with ***."""
    import re
    return re.sub(r"(://[^:]+:)[^@]+(@)", r"\1***\2", url)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_packages() -> None:
    print("\n[1] Python packages")
    required = ["psycopg2", "fastapi", "uvicorn"]
    optional = ["dotenv"]  # python-dotenv

    for pkg in required:
        try:
            importlib.import_module(pkg)
            ok(pkg)
        except ImportError:
            fail(f"{pkg} missing — pip install {pkg.replace('psycopg2','psycopg2-binary')}")

    for pkg in optional:
        try:
            importlib.import_module(pkg)
            ok(f"python-dotenv ({pkg})")
        except ImportError:
            skip(f"python-dotenv not installed — DATABASE_URL must be set manually")


def check_env() -> str | None:
    """Load .env, check DATABASE_URL. Returns URL or None."""
    print("\n[2] Environment")

    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=env_path, override=False)
            ok(f".env loaded ({env_path})")
        except ImportError:
            skip(f".env found but python-dotenv not installed ({env_path})")
    else:
        skip(f".env not found — copy .env.example → .env and fill in values")

    url = os.environ.get("DATABASE_URL", "")
    if url:
        ok(f"DATABASE_URL = {_mask_password(url)}")
        return url
    else:
        fail("DATABASE_URL not set — add to .env or export before running")
        return None


def check_database(url: str) -> bool:
    """Test DB connectivity, table existence, and seed data."""
    print("\n[3] Database")
    try:
        import psycopg2
    except ImportError:
        fail("psycopg2 not available — skipping DB checks")
        return False

    try:
        conn = psycopg2.connect(url)
    except Exception as exc:
        fail(f"DB connection failed — {exc}")
        return False

    ok("PostgreSQL connection established")

    tables_to_check = [
        ("legal_precedent", 1),
        ("legal_case", 1),
        ("hr_employee", 1),
        ("hr_department", 1),
    ]

    all_ok = True
    try:
        cur = conn.cursor()
        for table, min_rows in tables_to_check:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                if count >= min_rows:
                    ok(f"table '{table}' — {count} rows")
                else:
                    fail(f"table '{table}' exists but has {count} rows (min {min_rows}) — run setup_lawfirm.py")
                    all_ok = False
            except Exception as exc:
                fail(f"table '{table}' error — {exc} (run setup_lawfirm.py)")
                all_ok = False

        # Check GIN index
        cur.execute(
            "SELECT 1 FROM pg_indexes WHERE tablename='legal_precedent' AND indexname='idx_precedent_fts'"
        )
        if cur.fetchone():
            ok("GIN index 'idx_precedent_fts' present")
        else:
            fail("GIN index missing on legal_precedent — run setup_lawfirm.py")
            all_ok = False
    finally:
        conn.close()

    return all_ok


def check_ports() -> None:
    print("\n[4] Ports")
    ports = {
        8000: "L4 test port",
        8081: "FastAPI default port",
        5432: "PostgreSQL",
    }
    for port, label in ports.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(("127.0.0.1", port))
        if port == 5432:
            if result == 0:
                ok(f":{port} ({label}) — listening")
            else:
                fail(f":{port} ({label}) — not reachable (PostgreSQL not running?)")
        else:
            if result != 0:
                ok(f":{port} ({label}) — free")
            else:
                skip(f":{port} ({label}) — already in use (FastAPI may already be running)")


def check_uvicorn() -> None:
    print("\n[5] FastAPI launcher")
    try:
        import uvicorn  # noqa: F401
        ok("uvicorn importable")
    except ImportError:
        fail("uvicorn not installed — pip install uvicorn[standard]")

    # Check main.py exists
    main_py = REPO_ROOT / "backend" / "adapters" / "fastapi" / "main.py"
    if main_py.exists():
        ok(f"main.py found ({main_py.relative_to(REPO_ROOT)})")
    else:
        fail(f"main.py not found at {main_py}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="L4 pre-flight checker")
    parser.add_argument("--profile", default=None, help="Customer profile slug (informational)")
    args = parser.parse_args()

    print("=" * 56)
    print(" compounding-stack-harness — L4 pre-flight check")
    if args.profile:
        print(f" profile: {args.profile}")
    print("=" * 56)

    check_packages()
    db_url = check_env()
    if db_url:
        check_database(db_url)
    else:
        skip("DB checks skipped (no DATABASE_URL)")
    check_ports()
    check_uvicorn()

    print("\n" + "=" * 56)
    if _failures:
        print(f" FAILED — {len(_failures)} issue(s):")
        for f in _failures:
            print(f"   ✗ {f}")
        print("\n Fix the above, then re-run: python scripts/preflight.py")
        return 1
    else:
        print(" ALL CHECKS PASSED — ready for L4 live test")
        print(" Launch:  uvicorn main:app --app-dir backend/adapters/fastapi --port 8000")
        print(" Seed:    python scripts/demo/setup_lawfirm.py")
        return 0


if __name__ == "__main__":
    sys.exit(main())
