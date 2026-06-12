"""
apps/intake/tests/test_intake.py — intake 앱 pytest 스모크 테스트

테스트 항목:
  1. GET / → 200 (폼 렌더링)
  2. questions.yaml 파싱 (스키마 버전, 질문 목록 존재)
  3. POST /submit → revision 파일 생성
  4. edit_token 라운드트립 (GET/POST /edit/{token})
  5. GET /admin 인증 없음 → 401, 인증 있음 → 200
  6. intake_to_profile 변환기 → 생성된 YAML 파싱 가능
  7. GET /health → 200
  8. [BLOCK-2] path traversal → 400/404
  9. [FIX-1] admin lockout — 10회 실패 후 429

실행:
  python -m pytest apps/intake -q
"""
from __future__ import annotations

import base64
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# sys.path 설정 (apps/intake 를 직접 import 하기 위해)
# ---------------------------------------------------------------------------

INTAKE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(INTAKE_DIR))

# ---------------------------------------------------------------------------
# FastAPI TestClient 준비
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def tmp_data_dir(tmp_path_factory):
    """테스트용 DATA_DIR (세션 단위)."""
    d = tmp_path_factory.mktemp("intake_data")
    return d


@pytest.fixture(scope="session")
def client(tmp_data_dir):
    """FastAPI TestClient with isolated DATA_DIR and admin password."""
    os.environ["DATA_DIR"] = str(tmp_data_dir)
    os.environ["INTAKE_ADMIN_PASSWORD"] = "test-admin-pw"

    # 환경변수 세팅 후 app 임포트 (캐시 초기화 포함)
    import importlib
    import app as intake_app
    # _QUESTIONS_CACHE 리셋 (이전 세션 잔재 방지)
    intake_app._QUESTIONS_CACHE = None

    from fastapi.testclient import TestClient
    return TestClient(intake_app.app, raise_server_exceptions=True)


# ---------------------------------------------------------------------------
# 테스트 1: GET / → 200
# ---------------------------------------------------------------------------

def test_form_200(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "상담 신청" in resp.text or "intake" in resp.text.lower()


# ---------------------------------------------------------------------------
# 테스트 2: questions.yaml 파싱
# ---------------------------------------------------------------------------

def test_questions_yaml_parse():
    questions_path = INTAKE_DIR / "questions.yaml"
    assert questions_path.exists(), "questions.yaml 없음"
    with open(questions_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data.get("schema_version") == 1
    questions = data.get("questions", [])
    assert len(questions) > 0, "질문 목록이 비어있음"
    # 필수 필드 확인
    for q in questions:
        assert "id" in q, f"id 없는 질문: {q}"
        assert "type" in q, f"type 없는 질문: {q}"
        assert "persona" in q, f"persona 없는 질문: {q}"


def test_all_option_values_are_str():
    """YAML 1.1 불리언 파싱 회귀 — 모든 option value 가 str 이어야 한다."""
    questions_path = INTAKE_DIR / "questions.yaml"
    with open(questions_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    non_str = []
    for q in data.get("questions", []):
        for opt in q.get("options", []):
            v = opt.get("value")
            if not isinstance(v, str):
                non_str.append(
                    f"q={q['id']} opt_value={v!r} (type={type(v).__name__})"
                )
    assert not non_str, (
        "bool/int option value 발견 — 따옴표 누락:\n" + "\n".join(non_str)
    )


# ---------------------------------------------------------------------------
# 테스트 3: POST /submit → revision 파일 생성
# ---------------------------------------------------------------------------

def test_submit_creates_revision(client, tmp_data_dir):
    form_data = {
        "contact_email": "test@example.com",
        "contact_phone": "010-1234-5678",
        "company_name": "테스트회사",
        "industry": "manufacturing",
        "data_domains": ["customer", "order"],
        "existing_system": "excel_manual",
        "persona_role": "ceo",
        "ceo_pain_bottleneck": "주문 관리가 너무 복잡함",
        "ceo_pain_frequency": "daily",
        "ceo_cost_of_pain": "매일 2시간 낭비",
        "ceo_success_criteria": "주문 입력 오류 0건",
        "ceo_user_count": "6-20",
        "ceo_data_security": "cloud_ok",
        "_hp": "",  # honeypot 비워둠
    }
    resp = client.post("/submit", data=form_data)
    assert resp.status_code == 200
    # confirm 페이지: /edit/ 링크 or confirm-card 클래스 존재
    assert "/edit/" in resp.text or "confirm-card" in resp.text

    # 파일 생성 확인
    clients_dir = tmp_data_dir / "clients"
    assert clients_dir.exists(), "clients 디렉터리 미생성"
    client_dirs = list(clients_dir.iterdir())
    assert len(client_dirs) > 0, "client 디렉터리 미생성"
    rev_dir = client_dirs[0] / "revisions"
    assert rev_dir.exists(), "revisions 디렉터리 미생성"
    rev_files = list(rev_dir.glob("*.json"))
    assert len(rev_files) > 0, "revision 파일 미생성"

    # 저장 내용 확인
    with open(rev_files[0], encoding="utf-8") as f:
        saved = json.load(f)
    assert saved.get("contact_email") == "test@example.com"
    assert "customer" in saved.get("data_domains", [])


# ---------------------------------------------------------------------------
# 테스트 4: edit_token 라운드트립
# ---------------------------------------------------------------------------

def test_edit_token_roundtrip(client, tmp_data_dir):
    # 먼저 submit으로 edit_token 획득
    form_data = {
        "contact_email": "edit_test@example.com",
        "industry": "logistics",
        "data_domains": ["inventory"],
        "existing_system": "legacy_system",
        "persona_role": "staff",
        "staff_daily_pain": "재고 확인이 느림",
        "staff_workaround_tool": "excel",
        "staff_approval_needed": "no",
        "_hp": "",
    }
    resp = client.post("/submit", data=form_data)
    assert resp.status_code == 200

    # edit_token 파싱 (응답 HTML에서 추출)
    import re
    token_match = re.search(r"/edit/([A-Za-z0-9_-]{20,})", resp.text)
    assert token_match, "edit_token이 확인 페이지에 없음"
    token = token_match.group(1)

    # GET /edit/{token} → 200, prefill 확인
    edit_resp = client.get(f"/edit/{token}")
    assert edit_resp.status_code == 200
    assert "edit_test@example.com" in edit_resp.text

    # POST /edit/{token} → 새 revision 추가
    form_data["staff_daily_pain"] = "재고 확인이 개선됨 (수정)"
    edit_post_resp = client.post(f"/edit/{token}", data=form_data)
    assert edit_post_resp.status_code == 200
    assert "/edit/" in edit_post_resp.text or "confirm-card" in edit_post_resp.text

    # revision이 2개여야 함
    # email→client_id 인덱스에서 찾기
    import app as intake_app
    index = intake_app._load_email_index()
    cid = index.get("edit_test@example.com")
    assert cid is not None, "email 인덱스에 없음"
    revisions = intake_app._list_revisions(cid)
    assert len(revisions) >= 2, f"revision 수 부족: {len(revisions)}"


# ---------------------------------------------------------------------------
# 테스트 5: /admin 인증 401/200
# ---------------------------------------------------------------------------

def test_admin_unauthorized(client):
    resp = client.get("/admin")
    assert resp.status_code == 401


def test_admin_authorized(client):
    credentials = base64.b64encode(b"admin:test-admin-pw").decode()
    resp = client.get("/admin", headers={"Authorization": f"Basic {credentials}"})
    assert resp.status_code == 200
    assert "의뢰인" in resp.text or "admin" in resp.text.lower()


# ---------------------------------------------------------------------------
# 테스트 6: intake_to_profile 변환기 → YAML 파싱 가능
# ---------------------------------------------------------------------------

def test_converter_produces_valid_yaml(tmp_path):
    from intake_to_profile import convert, _render_profile

    answers = {
        "contact_email": "conv@example.com",
        "company_name": "변환테스트",
        "industry": "finance",
        "data_domains": ["customer", "order"],
        "existing_system": "excel_manual",
        "persona_role": "it",
        "it_frontend_pref": "react",
        "it_backend_pref": "fastapi",
        "it_db_dialect": "postgres",
        "it_auth_method": "simple_session",
        "it_server_env": "onpremise_linux",
    }

    profile_data, extra_signals = convert(answers)
    assert profile_data["customer"]["slug"], "slug 없음"
    assert profile_data["stack"].get("frontend") == "react"
    assert profile_data["stack"].get("backend") == "fastapi"
    assert profile_data["ddl"].get("dialect") == "postgres"

    yaml_str = _render_profile(profile_data)
    # YAML 파싱 가능 확인
    parsed = yaml.safe_load(yaml_str)
    assert parsed.get("version") == 1
    assert parsed["customer"]["slug"] == profile_data["customer"]["slug"]

    # vanilla_htmx 보정 확인
    answers2 = {**answers, "it_frontend_pref": "vanilla_htmx", "it_backend_pref": "node_express"}
    profile2, _ = convert(answers2)
    assert profile2["stack"].get("frontend") == "vanilla-htmx"
    assert profile2["stack"].get("backend") == "node-express"

    # 비지원값 → 키 생략 + extra_signals 기재
    answers3 = {**answers, "it_db_dialect": "mssql"}
    profile3, signals3 = convert(answers3)
    assert "dialect" not in profile3.get("ddl", {}), "mssql은 profile에 넣지 말아야"
    assert any("mssql" in s for s in signals3), "mssql extra signal 누락"


# ---------------------------------------------------------------------------
# 테스트 7: GET /health → 200
# ---------------------------------------------------------------------------

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"


# ---------------------------------------------------------------------------
# 테스트 8: BLOCK-2 — path traversal 방어
# ---------------------------------------------------------------------------

def test_admin_path_traversal_rejected(client):
    """detail=../../../../etc 같은 path traversal 시도는 400으로 거부."""
    credentials = base64.b64encode(b"admin:test-admin-pw").decode()
    headers = {"Authorization": f"Basic {credentials}"}

    # 점-점 슬래시 traversal
    resp = client.get("/admin?detail=../../../../etc", headers=headers)
    assert resp.status_code == 400, f"path traversal이 거부되지 않음: {resp.status_code}"

    # null byte 삽입 시도 (URL 인코딩 포함)
    resp2 = client.get("/admin?detail=abc%00def", headers=headers)
    assert resp2.status_code in (400, 422), f"null byte가 거부되지 않음: {resp2.status_code}"

    # 너무 짧은 id (포맷 불일치)
    resp3 = client.get("/admin?detail=short", headers=headers)
    assert resp3.status_code == 400, f"짧은 id가 거부되지 않음: {resp3.status_code}"

    # 대문자/특수문자 포함 (hex 포맷 불일치)
    resp4 = client.get("/admin?detail=AABBCCDD11223344", headers=headers)
    assert resp4.status_code == 400, f"대문자 id가 거부되지 않음: {resp4.status_code}"


def test_edit_token_path_traversal_rejected(client):
    """edit_token 경로에 포맷 불일치 값은 404로 거부."""
    # 슬래시 포함 (FastAPI 라우터가 먼저 처리하지만 명시 확인)
    resp = client.get("/edit/../../etc/passwd")
    # FastAPI 라우터는 /edit/ 이하를 단일 토큰으로 처리하므로 404 or 422
    assert resp.status_code in (404, 422)

    # 포맷 불일치 (특수문자 포함)
    resp2 = client.get("/edit/<script>alert(1)</script>")
    assert resp2.status_code in (404, 422)


# ---------------------------------------------------------------------------
# 테스트 9: FIX-1 — admin brute-force lockout
# ---------------------------------------------------------------------------

def test_admin_lockout_after_10_failures(client):
    """잘못된 비밀번호로 10회 실패 후 429를 반환한다."""
    import app as intake_app

    # lockout 상태 초기화 (테스트 격리)
    lockout_ip = "10.0.0.99"
    intake_app._ADMIN_FAIL[lockout_ip] = []

    bad_creds = base64.b64encode(b"admin:wrong-password").decode()
    headers = {"Authorization": f"Basic {bad_creds}"}

    # X-Forwarded-For 헤더로 테스트 IP 지정
    xff_headers = {**headers, "X-Forwarded-For": lockout_ip}

    # 10회 실패
    for i in range(10):
        resp = client.get("/admin", headers=xff_headers)
        assert resp.status_code == 401, f"{i+1}번째 시도가 401이어야 함: {resp.status_code}"

    # 11번째 → 429 (lockout)
    resp = client.get("/admin", headers=xff_headers)
    assert resp.status_code == 429, f"10회 실패 후 lockout(429)이어야 함: {resp.status_code}"

    # 정리: lockout 상태 초기화 (다른 테스트 영향 방지)
    intake_app._ADMIN_FAIL[lockout_ip] = []
