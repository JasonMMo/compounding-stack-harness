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
 10. GET /letter/{token} 정상 서빙 / 404 / traversal 차단

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
        "deliverable_kind": "business-system",
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
        "deliverable_kind": "business-system",
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


# ---------------------------------------------------------------------------
# 테스트 10: GET /letter/{token} — 정상 서빙 / 404 / traversal 차단
# ---------------------------------------------------------------------------

def test_letter_serve_ok(client, tmp_data_dir):
    """letters/ 에 파일을 직접 넣고 /letter/{token} 이 200 + 본문을 반환한다."""
    letters_dir = tmp_data_dir / "letters"
    letters_dir.mkdir(parents=True, exist_ok=True)

    token = "testTokenABC1234xyz"  # _LETTER_TOKEN_RE 에 맞는 토큰
    content = "<p>안내문 본문입니다.</p>"
    (letters_dir / f"{token}.html").write_text(content, encoding="utf-8")

    resp = client.get(f"/letter/{token}")
    assert resp.status_code == 200, f"예상 200, 실제 {resp.status_code}"
    # 본문 HTML 이 포함돼야 한다
    assert "안내문 본문입니다" in resp.text
    # base 템플릿 요소 확인
    assert "Pretendard" in resp.text or "pico" in resp.text.lower()


def test_letter_not_found(client):
    """존재하지 않는 토큰은 404 를 반환한다."""
    resp = client.get("/letter/nonExistentToken99X")
    assert resp.status_code == 404, f"예상 404, 실제 {resp.status_code}"


def test_letter_token_traversal_rejected(client):
    """경로 traversal 시도 토큰은 404 로 차단된다."""
    # 점-점 슬래시: FastAPI 라우터가 먼저 분해하지만 포맷 검증에서도 차단
    resp = client.get("/letter/../../etc/passwd")
    assert resp.status_code in (404, 422), f"traversal이 허용됨: {resp.status_code}"

    # _LETTER_TOKEN_RE 불일치 — 특수문자 포함
    resp2 = client.get("/letter/<bad>token!")
    assert resp2.status_code in (404, 422), f"특수문자 토큰이 허용됨: {resp2.status_code}"

    # 너무 짧은 토큰 (9자 미만)
    resp3 = client.get("/letter/abc")
    assert resp3.status_code in (404, 422), f"짧은 토큰이 허용됨: {resp3.status_code}"


# ---------------------------------------------------------------------------
# 테스트 11: _show_if_met — 조건 충족/미충족/multiselect 교집합
# ---------------------------------------------------------------------------

def test_show_if_met_no_condition():
    """show_if 없는 질문은 항상 True."""
    from app import _show_if_met
    q = {"id": "foo", "type": "text"}
    assert _show_if_met(q, {}) is True
    assert _show_if_met(q, {"foo": "bar"}) is True


def test_show_if_met_str_trigger_met():
    """단일 str trigger — 값 일치 시 True."""
    from app import _show_if_met
    q = {"id": "x", "type": "textarea", "show_if": {"it_has_external_integration": "yes"}}
    assert _show_if_met(q, {"it_has_external_integration": "yes"}) is True


def test_show_if_met_str_trigger_not_met():
    """단일 str trigger — 값 불일치 시 False."""
    from app import _show_if_met
    q = {"id": "x", "type": "textarea", "show_if": {"it_has_external_integration": "yes"}}
    assert _show_if_met(q, {"it_has_external_integration": "no"}) is False
    assert _show_if_met(q, {}) is False


def test_show_if_met_list_trigger_met():
    """list trigger — 값이 목록에 포함되면 True."""
    from app import _show_if_met
    q = {"id": "x", "type": "textarea",
         "show_if": {"staff_approval_needed": ["yes_frequent", "yes_occasional"]}}
    assert _show_if_met(q, {"staff_approval_needed": "yes_frequent"}) is True
    assert _show_if_met(q, {"staff_approval_needed": "yes_occasional"}) is True


def test_show_if_met_list_trigger_not_met():
    """list trigger — 값이 목록에 없으면 False."""
    from app import _show_if_met
    q = {"id": "x", "type": "textarea",
         "show_if": {"staff_approval_needed": ["yes_frequent", "yes_occasional"]}}
    assert _show_if_met(q, {"staff_approval_needed": "no"}) is False


def test_show_if_met_multiselect_overlap():
    """multiselect trigger — 교집합 있으면 True, 없으면 False."""
    from app import _show_if_met
    q = {"id": "x", "type": "textarea",
         "show_if": {"industry": ["logistics", "manufacturing"]}}
    # answer가 list인 경우 (multiselect)
    assert _show_if_met(q, {"industry": ["logistics", "retail"]}) is True
    assert _show_if_met(q, {"industry": ["retail", "finance"]}) is False
    # answer가 str인 경우 (select/radio)
    assert _show_if_met(q, {"industry": "logistics"}) is True
    assert _show_if_met(q, {"industry": "retail"}) is False


# ---------------------------------------------------------------------------
# 테스트 12: _validate — show_if 미충족 시 required 질문 스킵
# ---------------------------------------------------------------------------

def test_validate_skips_required_when_show_if_unmet():
    """show_if 조건 미충족인 required 질문은 _validate 에서 스킵된다."""
    from app import _validate

    fake_questions = [
        {
            "id": "trigger_q",
            "type": "radio",
            "persona": "all",
            "required": True,
            "label": "트리거 질문",
            "options": [{"value": "yes", "label": "예"}, {"value": "no", "label": "아니요"}],
        },
        {
            "id": "conditional_q",
            "type": "textarea",
            "persona": "all",
            "required": True,  # required=True 지만 show_if 조건 미충족 시 스킵
            "label": "조건부 질문",
            "show_if": {"trigger_q": "yes"},
        },
    ]

    # trigger_q=no → conditional_q 의 show_if 미충족 → 오류 없어야 함
    errors = _validate({"trigger_q": "no"}, fake_questions)
    assert not any("조건부 질문" in e for e in errors), (
        "show_if 미충족인 required 질문이 검증됨: " + str(errors)
    )

    # trigger_q=yes → conditional_q 표시되어야 함 → 빈 값이면 오류 발생
    errors2 = _validate({"trigger_q": "yes"}, fake_questions)
    assert any("조건부 질문" in e for e in errors2), (
        "show_if 충족된 required 질문이 검증 안 됨: " + str(errors2)
    )


# ---------------------------------------------------------------------------
# 테스트 13: convert() — industry-default fallback
# ---------------------------------------------------------------------------

def test_convert_applies_industry_default_frontend():
    """it_frontend_pref=unknown 일 때 industry-default frontend 가 주입된다."""
    from intake_to_profile import convert, _INDUSTRY_DEFAULTS_CACHE
    import intake_to_profile as itp

    # 캐시 초기화 (테스트 격리)
    itp._INDUSTRY_DEFAULTS_CACHE = None

    answers = {
        "contact_email": "default_test@example.com",
        "industry": "manufacturing",
        "data_domains": [],           # 도메인도 비어있음
        "it_frontend_pref": "unknown",
        "it_backend_pref": "unknown",
        "it_db_dialect": "unknown",
    }

    profile_data, extra_signals = convert(answers)

    # manufacturing default = vanilla-htmx/fastapi/postgres
    assert profile_data["stack"].get("frontend") == "vanilla-htmx", (
        f"expected vanilla-htmx, got {profile_data['stack'].get('frontend')}"
    )
    assert profile_data["stack"].get("backend") == "fastapi", (
        f"expected fastapi, got {profile_data['stack'].get('backend')}"
    )

    # extra_signals 에 "industry-default 적용" 기록 확인
    default_signals = [s for s in extra_signals if "industry-default 적용" in s]
    assert default_signals, f"industry-default 신호 없음. signals={extra_signals}"
    assert any("frontend=vanilla-htmx" in s for s in default_signals)


def test_convert_applies_industry_default_domains_when_zero():
    """data_domains 선택 없을 때 industry-default domains 가 주입된다."""
    from intake_to_profile import convert
    import intake_to_profile as itp

    itp._INDUSTRY_DEFAULTS_CACHE = None

    answers = {
        "contact_email": "domain_test@example.com",
        "industry": "logistics",
        "data_domains": [],           # 빈 선택 → 0개 매핑 → default 주입
        "it_frontend_pref": "react",  # 명시적 선택 → default 덮어쓰지 않아야
        "it_backend_pref": "fastapi",
        "it_db_dialect": "postgres",
    }

    profile_data, extra_signals = convert(answers)

    # domains 가 비어있지 않아야 함 (logistics default 주입)
    assert len(profile_data["domains"]) > 0, "industry-default domains 미주입"

    # extra_signals 에 domains default 기록 확인
    domain_signals = [s for s in extra_signals if "industry-default 적용" in s and "domains" in s]
    assert domain_signals, f"domains default 신호 없음. signals={extra_signals}"

    # 명시적 frontend 는 override 되지 않아야
    assert profile_data["stack"].get("frontend") == "react", (
        "명시적 frontend 가 default 로 덮어씌워짐"
    )


# ---------------------------------------------------------------------------
# 테스트 14: Phase 3 — _post_submit_conversion 아티팩트 생성
# ---------------------------------------------------------------------------

_CEO_FORM = {
    "contact_email": "phase3test@example.com",
    "contact_phone": "010-9999-0001",
    "company_name": "Phase3Corp",
    "industry": "manufacturing",
    "deliverable_kind": "business-system",
    "data_domains": ["customer", "order"],
    "existing_system": "excel_manual",
    "persona_role": "ceo",
    "ceo_pain_bottleneck": "재고 오류가 잦음",
    "ceo_pain_frequency": "daily",
    "ceo_cost_of_pain": "일 3시간 낭비",
    "ceo_success_criteria": "오류 0건",
    "ceo_user_count": "6-20",
    "ceo_data_security": "cloud_ok",
    "ceo_budget_setup": "500_1000",
    "_hp": "",
}


def test_post_submit_conversion_creates_artifacts(client, tmp_data_dir):
    """POST /submit 이후 draft.yaml, triage.json, needs-note.md, inbox.jsonl 이 생성된다."""
    import app as intake_app

    resp = client.post("/submit", data=_CEO_FORM)
    assert resp.status_code == 200

    # client_id 조회
    index = intake_app._load_email_index()
    client_id = index.get("phase3test@example.com")
    assert client_id is not None, "email 인덱스에 없음"

    client_path = intake_app._client_dir(client_id)

    # 아티팩트 존재 확인
    assert (client_path / "draft.yaml").exists(), "draft.yaml 미생성"
    assert (client_path / "triage.json").exists(), "triage.json 미생성"
    assert (client_path / "needs-note.md").exists(), "needs-note.md 미생성"

    # triage.json 내용 확인
    with open(client_path / "triage.json", encoding="utf-8") as f:
        triage = json.load(f)
    assert "score" in triage, "triage.json에 score 없음"
    assert "status" in triage, "triage.json에 status 없음"
    assert "slug" in triage, "triage.json에 slug 없음"

    # inbox.jsonl 존재 + 해당 client 레코드 확인
    inbox_path = tmp_data_dir / "inbox.jsonl"
    assert inbox_path.exists(), "inbox.jsonl 미생성"

    found = None
    with open(inbox_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("client_id") == client_id:
                found = record
                break

    assert found is not None, "inbox.jsonl에 해당 client_id 레코드 없음"
    assert "score" in found, "inbox 레코드에 score 없음"
    assert "status" in found, "inbox 레코드에 status 없음"
    assert "qualifies" in found, "inbox 레코드에 qualifies 없음"
    # PII 금지: email/contact_email 키가 없어야 함
    assert "email" not in found, "inbox 레코드에 PII(email) 포함됨"
    assert "contact_email" not in found, "inbox 레코드에 PII(contact_email) 포함됨"


def test_post_submit_conversion_never_raises(tmp_data_dir):
    """convert_to_files 또는 qualify 가 예외를 던져도 _post_submit_conversion 은 None 을 반환한다."""
    import app as intake_app
    import intake_to_profile

    original = intake_to_profile.convert_to_files

    def _boom(answers, slug=None):
        raise RuntimeError("테스트용 강제 예외")

    intake_to_profile.convert_to_files = _boom
    # _convert_to_files 도 교체 (app 모듈이 import 시 바인딩함)
    original_app = intake_app._convert_to_files
    intake_app._convert_to_files = _boom

    try:
        result = intake_app._post_submit_conversion(
            "deadbeef00000001",
            {"contact_email": "x@example.com", "industry": "manufacturing"},
            "20260614T000000Z",
        )
        assert result is None, "_post_submit_conversion 이 None 이 아닌 값을 반환함"
    finally:
        intake_to_profile.convert_to_files = original
        intake_app._convert_to_files = original_app


def test_submit_returns_three_tuple():
    """_submit 이 (edit_token, client_id, ts) 3-튜플을 반환한다."""
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["DATA_DIR"] = tmp
        import app as intake_app
        answers = {
            "contact_email": "tuple_test@example.com",
            "company_name": "TupleTest",
            "industry": "generic",
            "data_domains": [],
            "existing_system": "excel_manual",
            "persona_role": "ceo",
        }
        result = intake_app._submit(answers)
        assert len(result) == 3, f"_submit 이 3-튜플을 반환하지 않음: {result!r}"
        edit_token, client_id, ts = result
        assert isinstance(edit_token, str) and len(edit_token) > 10
        assert isinstance(client_id, str) and len(client_id) > 0
        assert isinstance(ts, str) and "T" in ts


# ---------------------------------------------------------------------------
# 테스트 15: _load_industry_defaults — candidate path fallback
# ---------------------------------------------------------------------------

def test_industry_defaults_loads_from_candidate_path(tmp_path, monkeypatch):
    """REPO_ROOT candidate が 존재하지 않아도 __file__-relative candidate 에서 로드된다.

    두 가지 서브케이스:
      (a) env override INTAKE_INDUSTRY_DEFAULTS → 비어있지 않은 dict 반환
      (b) 모든 candidate 없음 → {} 반환 (graceful degradation)
    """
    import intake_to_profile as itp

    # --- (a) env override candidate ---
    # presets 파일의 실제 내용으로 임시 파일 생성
    presets_src = INTAKE_DIR.parents[1] / "presets" / "industry-defaults.yaml"
    import yaml as _yaml
    if presets_src.exists():
        with open(presets_src, encoding="utf-8") as _f:
            _content = _f.read()
    else:
        # 파일이 없는 CI 환경을 대비한 최소 fixture
        _content = "manufacturing:\n  frontend: vanilla-htmx\n  backend: fastapi\n  dialect: postgres\n  domains: []\n"

    fake_presets = tmp_path / "fake-industry-defaults.yaml"
    fake_presets.write_text(_content, encoding="utf-8")

    # 캐시 초기화
    itp._INDUSTRY_DEFAULTS_CACHE = None

    # INTAKE_INDUSTRY_DEFAULTS env override → repo_root candidate 보다 먼저 히트
    monkeypatch.setenv("INTAKE_INDUSTRY_DEFAULTS", str(fake_presets))
    # REPO_ROOT candidate 를 존재하지 않는 경로로 교체 (env override 우선순위 검증)
    monkeypatch.setattr(itp, "_INDUSTRY_DEFAULTS_PATH", tmp_path / "nonexistent.yaml")

    result = itp._load_industry_defaults()
    assert isinstance(result, dict) and len(result) > 0, (
        f"env override candidate 에서 로드 실패: {result!r}"
    )
    assert "manufacturing" in result, f"manufacturing 키 없음: {list(result.keys())}"

    # --- (b) 모든 candidate 없음 → {} ---
    itp._INDUSTRY_DEFAULTS_CACHE = None
    monkeypatch.setenv("INTAKE_INDUSTRY_DEFAULTS", str(tmp_path / "also_missing.yaml"))
    monkeypatch.setattr(itp, "_INDUSTRY_DEFAULTS_PATH", tmp_path / "nonexistent.yaml")
    # __file__-relative candidate (/app/presets/...) 도 존재하지 않으므로
    # 세 후보 모두 미존재 → {} 반환
    # (테스트 환경에서 __file__ = apps/intake/intake_to_profile.py,
    #  apps/intake/presets/industry-defaults.yaml 은 실제로 없음)
    import os as _os
    _sibling = itp._industry_defaults_candidates()[-1]  # __file__-relative candidate
    if _sibling.exists():
        # 만약 실제로 존재하는 환경이라면 monkeypatch 로 우회 불가 — 스킵
        pytest.skip("__file__-relative candidate 가 실제로 존재하여 '모두 없음' 케이스 스킵")

    result_empty = itp._load_industry_defaults()
    assert result_empty == {}, f"모든 candidate 없을 때 {{}} 이어야 함: {result_empty!r}"

    # 캐시 정리 (다른 테스트 영향 방지)
    itp._INDUSTRY_DEFAULTS_CACHE = None
    monkeypatch.delenv("INTAKE_INDUSTRY_DEFAULTS", raising=False)


# ---------------------------------------------------------------------------
# 테스트 16: marketing-site — convert() site 블록 생성
# ---------------------------------------------------------------------------

_MS_ANSWERS_FULL = {
    "contact_email": "ms-test@example.com",
    "company_name": "테스트에이전시",
    "industry": "service",
    "persona_role": "ceo",
    "deliverable_kind": "marketing-site",
    "ms_brand_name": "TestAgency",
    "ms_tagline": "더 빠른 런칭, 더 나은 전환",
    "ms_target_audience": "중소기업 대표, 마케터",
    "ms_pages": ["about", "contact", "pricing"],
    "ms_tone": "bold-energetic",
    "ms_primary_cta": "무료 상담 신청",
    "ms_reference_sites": "https://example.com",
    "ceo_budget_setup": "500_1000",
}


def test_convert_marketing_site_returns_site_block():
    """deliverable_kind=marketing-site → profile 에 site: 블록, domains/ddl 없음."""
    from intake_to_profile import convert

    profile, extra_signals = convert(_MS_ANSWERS_FULL)

    # deliverable_kind 분기 확인
    assert profile["stack"]["deliverable_kind"] == "marketing-site"
    assert profile["stack"]["frontend"] == "landing-astro"
    assert profile["stack"]["backend"] == "none"

    # site 블록 존재
    assert "site" in profile, "site 블록 없음"
    site = profile["site"]
    assert "theme" in site
    assert "pages" in site

    # domains / ddl 없음 (marketing-site 는 entity 없음)
    assert "domains" not in profile or profile.get("domains") is None
    assert "ddl" not in profile or profile.get("ddl") is None


def test_convert_ms_tone_maps_to_theme():
    """ms_tone bold-energetic → aurora, minimal-editorial → studio."""
    from intake_to_profile import convert

    answers_aurora = {**_MS_ANSWERS_FULL, "ms_tone": "bold-energetic"}
    profile_aurora, _ = convert(answers_aurora)
    assert profile_aurora["site"]["theme"] == "aurora"

    answers_studio = {**_MS_ANSWERS_FULL, "ms_tone": "minimal-editorial"}
    profile_studio, _ = convert(answers_studio)
    assert profile_studio["site"]["theme"] == "studio"

    answers_no_tone = {**_MS_ANSWERS_FULL, "ms_tone": ""}
    profile_default, signals = convert(answers_no_tone)
    assert profile_default["site"]["theme"] == "aurora", "미선택 시 aurora 기본값"
    assert any("aurora" in s for s in signals), "미선택 시 extra_signal 기록 없음"


def test_convert_ms_pages_include_home_always():
    """home 은 ms_pages 선택과 무관하게 항상 포함."""
    from intake_to_profile import convert

    answers = {**_MS_ANSWERS_FULL, "ms_pages": ["about", "faq"]}
    profile, _ = convert(answers)
    page_slugs = [p["slug"] for p in profile["site"]["pages"]]
    assert "home" in page_slugs, "home 페이지 누락"
    assert "about" in page_slugs
    assert "faq" in page_slugs


def test_convert_ms_pages_sections_have_required_copy():
    """각 페이지 섹션의 catalog required copy_slots 이 모두 채워져 있어야 한다."""
    from intake_to_profile import convert

    answers = {**_MS_ANSWERS_FULL, "ms_pages": ["about", "services_features", "pricing", "testimonials", "faq", "contact"]}
    profile, _ = convert(answers)

    # Required copy slot 검사 (catalog 기준)
    required_by_type = {
        "hero": ["headline", "subhead"],
        "features": ["headline"],
        "pricing": ["headline"],
        "testimonial": ["quote", "author_name"],
        "faq": ["headline"],
        "cta": ["headline"],
        "footer": ["brand_name"],
        "logos": ["eyebrow"],
    }

    for page in profile["site"]["pages"]:
        for section in page.get("sections", []):
            sec_type = section["type"]
            required = required_by_type.get(sec_type, [])
            copy = section.get("copy", {})
            for slot in required:
                assert slot in copy, (
                    f"page={page['slug']} section={sec_type}: "
                    f"required copy slot '{slot}' 누락"
                )


def test_convert_ms_contact_page_enables_contact_block():
    """ms_pages 에 contact 포함 시 site.contact.enabled=True."""
    from intake_to_profile import convert

    answers_with_contact = {**_MS_ANSWERS_FULL, "ms_pages": ["contact"]}
    profile, _ = convert(answers_with_contact)
    assert profile["site"].get("contact", {}).get("enabled") is True

    answers_no_contact = {**_MS_ANSWERS_FULL, "ms_pages": ["about"]}
    profile2, _ = convert(answers_no_contact)
    assert not profile2["site"].get("contact", {}).get("enabled", False)


def test_convert_ms_site_block_passes_validate_site():
    """convert() 로 생성된 site: 블록이 site_manifest.validate_site 위반 0."""
    import sys
    import os
    sys.path.insert(0, str(INTAKE_DIR.parents[1] / "scripts" / "workflow"))
    from site_manifest import load_section_catalog, validate_site

    from intake_to_profile import convert

    answers = {
        **_MS_ANSWERS_FULL,
        "ms_pages": ["about", "services_features", "pricing", "testimonials", "faq", "contact"],
    }
    profile, _ = convert(answers)
    site = profile["site"]

    catalog = load_section_catalog()
    violations = validate_site(site, catalog)
    assert violations == [], (
        "convert() 생성 site 블록 validate_site 위반:\n" + "\n".join(violations)
    )


def test_render_profile_marketing_site_produces_valid_yaml():
    """_render_profile() 로 직렬화된 marketing-site profile 이 YAML 파싱 가능."""
    from intake_to_profile import convert, _render_profile

    profile, _ = convert(_MS_ANSWERS_FULL)
    yaml_str = _render_profile(profile)

    parsed = yaml.safe_load(yaml_str)
    assert parsed.get("version") == 1
    assert parsed["stack"]["deliverable_kind"] == "marketing-site"
    assert "site" in parsed
    assert "domains" not in parsed
    assert "ddl" not in parsed


def test_business_system_path_unchanged_by_ms_changes():
    """marketing-site 분기 추가 후 business-system convert() 경로 회귀 0."""
    from intake_to_profile import convert, _render_profile

    answers = {
        "contact_email": "bs@example.com",
        "company_name": "BizCorp",
        "industry": "manufacturing",
        "deliverable_kind": "business-system",
        "data_domains": ["customer", "order"],
        "it_frontend_pref": "react",
        "it_backend_pref": "fastapi",
        "it_db_dialect": "postgres",
        "it_auth_method": "simple_session",
        "it_server_env": "onpremise_linux",
    }
    profile, signals = convert(answers)
    assert profile["stack"].get("frontend") == "react"
    assert profile["stack"].get("backend") == "fastapi"
    assert profile["ddl"].get("dialect") == "postgres"
    assert len(profile["domains"]) > 0

    yaml_str = _render_profile(profile)
    parsed = yaml.safe_load(yaml_str)
    assert "ddl" in parsed
    assert "domains" in parsed
    assert "site" not in parsed


# ---------------------------------------------------------------------------
# 테스트 17: marketing-site qualify 채점
# ---------------------------------------------------------------------------

def test_qualify_marketing_site_uses_ms_scoring():
    """deliverable_kind=marketing-site 는 marketing_site_scoring 을 사용한다."""
    from qualify import qualify

    result = qualify(_MS_ANSWERS_FULL)
    # base 50 + company(5) + target(10) + pages 3*(min(3,4)=3)(9) + cta(5) + tone(5) + budget_over500(10) + ref(3) = 50+5+10+9+5+5+10+3 = 97
    assert result.score > 50, f"marketing-site score 너무 낮음: {result.score}"
    assert result.status in ("qualify", "defer"), f"예상 외 status: {result.status}"
    assert not result.disqualified


def test_qualify_marketing_site_no_business_system_gaps():
    """marketing-site 채점 결과에 dialect/auth/stack 갭이 없어야 한다."""
    from qualify import qualify

    result = qualify(_MS_ANSWERS_FULL)
    gap_axes = [g.todo_axis for g in result.gaps]
    assert "ddl" not in gap_axes, "marketing-site 에서 ddl 갭 감지됨"
    assert "auth-sso-keycloak" not in [g.gap_category for g in result.gaps]


def test_qualify_marketing_site_scope_ecommerce_signal():
    """ms_reference_sites 에 이커머스 키워드 있으면 scope 갭 감지."""
    from qualify import qualify

    answers = {**_MS_ANSWERS_FULL, "ms_reference_sites": "https://shopify.com (쇼핑몰 참고)"}
    result = qualify(answers)
    gap_cats = [g.gap_category for g in result.gaps]
    assert "marketing-site-scope-ecommerce" in gap_cats, (
        f"이커머스 scope 신호 미감지. gaps={gap_cats}"
    )
    assert not result.disqualified, "scope 신호는 disqualify 하면 안 됨"


# ---------------------------------------------------------------------------
# 테스트 18: show_if 게이팅 — marketing-site 사용자에게 DDL 질문 required 아님
# ---------------------------------------------------------------------------

def test_validate_marketing_site_no_it_questions_required():
    """deliverable_kind=marketing-site 제출 시 DDL/IT 질문 required 검증 안 됨."""
    from app import _validate
    import yaml as _yaml

    questions_path = INTAKE_DIR / "questions.yaml"
    with open(questions_path, encoding="utf-8") as f:
        data = _yaml.safe_load(f)
    questions = data["questions"]

    # marketing-site 사용자 최소 answers (IT 질문 전혀 없음)
    answers = {
        "contact_email": "ms-val@example.com",
        "industry": "service",
        "persona_role": "ceo",
        "deliverable_kind": "marketing-site",
        "ms_brand_name": "MyBrand",
        "ms_target_audience": "중소기업 대표",
        "ms_pages": ["about"],
        "ms_tone": "bold-energetic",
        "ceo_pain_bottleneck": "홈페이지가 없어서 신뢰가 낮음",
        "ceo_pain_frequency": "daily",
        "ceo_success_criteria": "홈페이지 론칭 후 문의 월 10건",
        "ceo_user_count": "1-5",
    }

    errors = _validate(answers, questions)

    # DDL/dialect/stack 관련 오류 없어야 함
    ddl_related = [e for e in errors if any(kw in e for kw in
                   ["데이터베이스", "DB", "dialect", "서버 환경", "Docker", "프론트엔드", "백엔드"])]
    assert not ddl_related, (
        f"marketing-site 사용자에게 DDL/IT 질문 required 오류 발생:\n" + "\n".join(ddl_related)
    )


def test_validate_deliverable_kind_required():
    """deliverable_kind 미입력 시 필수 오류 발생."""
    from app import _validate
    import yaml as _yaml

    questions_path = INTAKE_DIR / "questions.yaml"
    with open(questions_path, encoding="utf-8") as f:
        data = _yaml.safe_load(f)
    questions = data["questions"]

    answers = {
        "contact_email": "nodk@example.com",
        "industry": "service",
        "persona_role": "ceo",
        # deliverable_kind 누락
    }
    errors = _validate(answers, questions)
    assert any("deliverable_kind" in e or "원하시는 것" in e for e in errors), (
        f"deliverable_kind 누락 오류 없음. errors={errors}"
    )
