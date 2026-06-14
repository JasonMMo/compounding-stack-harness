"""
apps/intake/app.py — intake 웹폼 FastAPI 앱

의뢰인(숨고/크몽 계약 전)이 needs를 입력하는 웹폼.
- GET  /           : questions.yaml 기반 폼 렌더링
- POST /submit     : 검증 → 저장 → 확인 페이지 + 수정 링크
- GET  /edit/{token}: 기존 답변 prefill → 수정 제출
- GET  /admin      : HTTP Basic auth 의뢰인 목록/상세
- GET  /health     : 200 JSON
- GET  /letter/{token}: 안내문 서빙 (PM 작성 HTML, base 템플릿 래핑)

저장: DATA_DIR/clients/<client_id>/meta.json + revisions/<ts>.json (append-only)
letter 저장: DATA_DIR/letters/<token>.html (신뢰된 내부 산출물)
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import secrets
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Sibling-module imports (VPS working dir = apps/intake/; bare import first)
# ---------------------------------------------------------------------------

try:
    from qualify import qualify as _qualify
    from intake_to_profile import convert_to_files as _convert_to_files
    import audit as _audit
except ImportError:
    from apps.intake.qualify import qualify as _qualify          # type: ignore
    from apps.intake.intake_to_profile import convert_to_files as _convert_to_files  # type: ignore
    import apps.intake.audit as _audit                           # type: ignore

import yaml
import jinja2
from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ---------------------------------------------------------------------------
# 경로 상수
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_YAML = BASE_DIR / "questions.yaml"


def _data_dir() -> Path:
    """DATA_DIR 런타임 평가 (테스트에서 환경변수 오버라이드 지원)."""
    return Path(os.environ.get("DATA_DIR", str(BASE_DIR / "data")))

# ---------------------------------------------------------------------------
# 앱 초기화
# ---------------------------------------------------------------------------

app = FastAPI(title="intake", docs_url=None, redoc_url=None)

# FIX-2: 64KB body limit — textarea 반복 제출 메모리 소모 방지
from starlette.middleware.base import BaseHTTPMiddleware

class _LimitBodyMiddleware(BaseHTTPMiddleware):
    MAX_BODY = 64 * 1024  # 64 KB

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_BODY:
            return Response(
                content="요청 크기가 너무 큽니다 (최대 64KB).",
                status_code=413,
            )
        return await call_next(request)

app.add_middleware(_LimitBodyMiddleware)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
# BLOCK-3: autoescape=True 명시 — FastAPI/Jinja2 버전 무관하게 XSS 방어 고정.
# jinja2.Environment 직접 구성으로 starlette "Extra environment options" 경고 회피.
_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=True,
)
templates = Jinja2Templates(env=_jinja_env)

# ---------------------------------------------------------------------------
# questions.yaml 로드 (startup 시 캐시, reload 없음)
# ---------------------------------------------------------------------------

def _normalize_option_value(v: object) -> str:
    """option value 를 str 로 강제 정규화.

    YAML 1.1 불리언 파싱 방어: yes/no/true/false 가 bool 로 들어올 경우
    "yes"/"no" 로 복원한다. 그 외 모든 값은 str() 변환.
    """
    if isinstance(v, bool):
        return "yes" if v else "no"
    return str(v)


def _load_questions() -> dict:
    with open(QUESTIONS_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # option value 전수 정규화 (bool 파싱 방어)
    for q in data.get("questions", []):
        for opt in q.get("options", []):
            opt["value"] = _normalize_option_value(opt["value"])
    return data

_QUESTIONS_CACHE: dict | None = None


def get_questions() -> dict:
    global _QUESTIONS_CACHE
    if _QUESTIONS_CACHE is None:
        _QUESTIONS_CACHE = _load_questions()
    return _QUESTIONS_CACHE

# ---------------------------------------------------------------------------
# 저장 헬퍼
# ---------------------------------------------------------------------------

def _email_index_path() -> Path:
    p = _data_dir() / "email_index.json"
    return p


def _load_email_index() -> dict[str, str]:
    """email → client_id 인덱스 로드."""
    p = _email_index_path()
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _save_email_index(index: dict[str, str]) -> None:
    _data_dir().mkdir(parents=True, exist_ok=True)
    with open(_email_index_path(), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def _client_dir(client_id: str) -> Path:
    return _data_dir() / "clients" / client_id


def _get_or_create_client(email: str) -> tuple[str, bool]:
    """email로 client_id를 반환. 없으면 생성. (client_id, is_new)"""
    index = _load_email_index()
    if email in index:
        return index[email], False
    client_id = hashlib.sha256(email.encode()).hexdigest()[:16]
    # 충돌 방지: 이미 다른 email이 같은 id를 쓰면 uuid fallback
    used_ids = set(index.values())
    if client_id in used_ids:
        client_id = secrets.token_hex(8)
    index[email] = client_id
    _save_email_index(index)
    return client_id, True


def _load_meta(client_id: str) -> dict | None:
    p = _client_dir(client_id) / "meta.json"
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _save_meta(client_id: str, meta: dict) -> None:
    d = _client_dir(client_id)
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def _save_revision(client_id: str, answers: dict) -> str:
    """answers를 revisions/<UTC_ts>.json 으로 저장. 타임스탬프 반환."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rev_dir = _client_dir(client_id) / "revisions"
    rev_dir.mkdir(parents=True, exist_ok=True)
    p = rev_dir / f"{ts}.json"
    # 같은 초 충돌 방지
    counter = 0
    while p.exists():
        counter += 1
        p = rev_dir / f"{ts}_{counter}.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=2)
    return ts


def _list_revisions(client_id: str) -> list[dict]:
    """revisions/ 디렉터리의 모든 revision을 시간순으로 반환."""
    rev_dir = _client_dir(client_id) / "revisions"
    if not rev_dir.exists():
        return []
    revisions = []
    for p in sorted(rev_dir.glob("*.json")):
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        revisions.append({"ts": p.stem, "answers": data})
    return revisions


def _submit(answers: dict) -> tuple[str, str, str]:
    """answers 저장 → (edit_token, client_id, ts)."""
    email = answers.get("contact_email", "").strip().lower()
    client_id, is_new = _get_or_create_client(email)
    ts = _save_revision(client_id, answers)

    meta = _load_meta(client_id)
    if meta is None:
        # 신규 의뢰인
        edit_token = secrets.token_urlsafe(32)
        meta = {
            "client_id": client_id,
            "email": email,
            "edit_token": edit_token,
            "created_at": ts,
            "updated_at": ts,
        }
    else:
        # 재문의: edit_token 유지, updated_at 갱신
        edit_token = meta["edit_token"]
        meta["updated_at"] = ts
    _save_meta(client_id, meta)
    return edit_token, client_id, ts


def _post_submit_conversion(client_id: str, answers: dict, ts: str) -> None:
    """Run qualify + convert + audit + inbox append after a successful submit.

    MUST NOT raise — any exception is logged and swallowed so the customer's
    confirm response is never broken by a conversion failure.
    """
    try:
        result = _qualify(answers)
        slug, profile_yaml, needs_note = _convert_to_files(answers)

        client_path = _client_dir(client_id)
        client_path.mkdir(parents=True, exist_ok=True)

        # triage.json — PII-free scoring artefact
        triage = {
            "ts": ts,
            "slug": slug,
            "score": result.score,
            "status": result.status,
            "gaps": [
                {
                    "gap_category": g.gap_category,
                    "todo_axis": g.todo_axis,
                    "trigger": g.trigger,
                    "expansion_note": g.expansion_note,
                }
                for g in result.gaps
            ],
            "reasons": result.reasons,
        }
        (client_path / "triage.json").write_text(
            json.dumps(triage, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # draft.yaml
        (client_path / "draft.yaml").write_text(profile_yaml, encoding="utf-8")

        # needs-note.md
        (client_path / "needs-note.md").write_text(needs_note, encoding="utf-8")

        # audit event (PII-free: slug/score/status/prefer_call only)
        _audit.append_event(
            client_id,
            "INTAKE_SUBMITTED",
            data={
                "slug": slug,
                "score": result.score,
                "status": result.status,
                "prefer_call": answers.get("prefer_call"),
            },
            data_dir=_data_dir(),
        )

        # inbox.jsonl — one line per submission, PII-free
        inbox_path = _data_dir() / "inbox.jsonl"
        inbox_record = json.dumps(
            {
                "ts": ts,
                "client_id": client_id,
                "slug": slug,
                "score": result.score,
                "status": result.status,
                "prefer_call": answers.get("prefer_call", ""),
                "qualifies": result.status == "qualify",
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        with open(inbox_path, "a", encoding="utf-8") as fh:
            fh.write(inbox_record + "\n")

    except Exception:
        logging.exception(
            "[_post_submit_conversion] conversion failed for client_id=%s ts=%s",
            client_id,
            ts,
        )

# ---------------------------------------------------------------------------
# 검증
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _show_if_met(q: dict, answers: dict) -> bool:
    """show_if 조건이 충족되면 True, 아니면 False.

    show_if 없으면 항상 True.
    trigger 값이 str → 완전 일치.
    trigger 값이 list → 포함 여부 (answers가 list이면 교집합 비어있지 않으면 True).
    """
    show_if = q.get("show_if")
    if not show_if:
        return True
    for trigger_qid, allowed in show_if.items():
        answer_val = answers.get(trigger_qid, "")
        if isinstance(allowed, list):
            if isinstance(answer_val, list):
                # multiselect: 교집합
                if not any(v in allowed for v in answer_val):
                    return False
            else:
                if answer_val not in allowed:
                    return False
        else:
            # str 단일값
            if isinstance(answer_val, list):
                if allowed not in answer_val:
                    return False
            else:
                if answer_val != allowed:
                    return False
    return True


def _validate(answers: dict, questions: list[dict]) -> list[str]:
    """required 필드 + email 형식 검증. 오류 메시지 리스트 반환.

    persona 분기: persona_role 값에 해당하는 섹션 질문만 required 검증.
    persona=all 질문은 항상 검증.
    show_if 조건 미충족 질문은 required 검증 스킵.
    """
    persona_role = answers.get("persona_role", "")
    errors = []
    for q in questions:
        qid = q["id"]
        required = q.get("required", False)
        persona = q.get("persona", "all")

        # persona 필터: all이 아니면 현재 role과 일치할 때만 required 검증
        if required and persona != "all" and persona != persona_role:
            continue

        # show_if 조건 미충족 시 스킵
        if not _show_if_met(q, answers):
            continue

        val = answers.get(qid, "")
        # multiselect는 리스트
        if isinstance(val, list):
            is_empty = len(val) == 0
        else:
            is_empty = not val

        if required and is_empty:
            errors.append(f"'{q['label']}' 항목은 필수입니다.")
        if qid == "contact_email" and val and not _EMAIL_RE.match(str(val)):
            errors.append("이메일 주소 형식이 올바르지 않습니다.")
    return errors

# ---------------------------------------------------------------------------
# BLOCK-1: 실제 클라이언트 IP 추출
# ---------------------------------------------------------------------------
# 컨테이너는 published port 없이 Coolify uuid 넷에서 Traefik만 접근 가능.
# 이 전제 하에 X-Forwarded-For 첫 번째 값을 신뢰한다.
# 외부에서 직접 접근 불가 구조이므로 forwarded-allow-ips="*" 허용 (BLOCK-1 해설).

def _client_ip(request: Request) -> str:
    """Traefik 역방향 프록시 뒤에서 실제 클라이언트 IP를 반환한다.

    uvicorn --proxy-headers --forwarded-allow-ips="*" 전제.
    X-Forwarded-For가 없으면 request.client.host fallback.
    """
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        # 첫 번째 IP가 실제 클라이언트 (Traefik이 append 방식으로 넣음)
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ---------------------------------------------------------------------------
# 안티스팸: honeypot + per-IP rate limit (인메모리, --workers 1 전제)
# ---------------------------------------------------------------------------

_RATE_LIMIT: dict[str, list[float]] = defaultdict(list)
_RATE_WINDOW = 60.0   # 초
_RATE_MAX = 5         # 분당 최대 제출 수


def _check_rate_limit(ip: str) -> bool:
    """True = 허용, False = 차단."""
    now = time.time()
    window = [t for t in _RATE_LIMIT[ip] if now - t < _RATE_WINDOW]
    _RATE_LIMIT[ip] = window
    if len(window) >= _RATE_MAX:
        return False
    _RATE_LIMIT[ip].append(now)
    return True


# ---------------------------------------------------------------------------
# FIX-1: Admin 인증 실패 per-IP lockout (인메모리)
# ---------------------------------------------------------------------------

_ADMIN_FAIL: dict[str, list[float]] = defaultdict(list)
_ADMIN_FAIL_MAX = 10          # 최대 실패 횟수
_ADMIN_FAIL_WINDOW = 60.0     # 실패 집계 윈도우 (초)
_ADMIN_LOCKOUT = 15 * 60.0    # lockout 지속 시간 (15분)


def _check_admin_lockout(ip: str) -> bool:
    """True = 접근 허용, False = lockout 중."""
    now = time.time()
    # lockout 윈도우 내 실패만 유지
    recent = [t for t in _ADMIN_FAIL[ip] if now - t < _ADMIN_LOCKOUT]
    _ADMIN_FAIL[ip] = recent
    return len(recent) < _ADMIN_FAIL_MAX


def _record_admin_fail(ip: str) -> None:
    """인증 실패 1회 기록."""
    _ADMIN_FAIL[ip].append(time.time())


# ---------------------------------------------------------------------------
# Admin 인증
# ---------------------------------------------------------------------------

def _admin_password() -> str | None:
    return os.environ.get("INTAKE_ADMIN_PASSWORD")


def _check_admin_auth(request: Request) -> bool:
    """HTTP Basic 인증 확인. 비밀번호 미설정 시 항상 False."""
    pw = _admin_password()
    if not pw:
        return False
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Basic "):
        return False
    import base64
    try:
        decoded = base64.b64decode(auth[6:]).decode("utf-8")
        _, given_pw = decoded.split(":", 1)
        # 상수시간 비교 (timing attack 방지)
        return secrets.compare_digest(given_pw, pw)
    except Exception:
        return False

# ---------------------------------------------------------------------------
# 라우트: GET /
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    q = get_questions()
    return templates.TemplateResponse(
        request,
        "form.html",
        {
            "questions": q["questions"],
            "form_title": q.get("form_title", "상담 신청"),
            "form_description": q.get("form_description", ""),
            "prefill": {},
            "errors": [],
            "edit_mode": False,
            "edit_token": None,
        },
    )

# ---------------------------------------------------------------------------
# 라우트: POST /submit
# ---------------------------------------------------------------------------

@app.post("/submit", response_class=HTMLResponse)
async def submit(request: Request):
    # BLOCK-1: 실제 클라이언트 IP (X-Forwarded-For 우선)
    ip = _client_ip(request)
    if not _check_rate_limit(ip):
        raise HTTPException(status_code=429, detail="너무 많은 요청입니다. 잠시 후 다시 시도해 주세요.")

    form = await request.form()
    # honeypot 검사: _hp 필드가 비어있어야 정상 사용자
    if form.get("_hp", ""):
        # 봇으로 판단 — 정상 응답처럼 보이지만 저장하지 않음
        return templates.TemplateResponse(
            request,
            "confirm.html",
            {"edit_token": "fake", "fake": True},
        )

    q = get_questions()
    questions = q["questions"]

    # answers 수집 (multiselect → 리스트)
    answers: dict[str, Any] = {}
    for question in questions:
        qid = question["id"]
        if question["type"] == "multiselect":
            vals = form.getlist(qid)
            answers[qid] = vals if vals else []
        else:
            answers[qid] = form.get(qid, "").strip()

    # 검증
    errors = _validate(answers, questions)
    if errors:
        return templates.TemplateResponse(
            request,
            "form.html",
            {
                "questions": questions,
                "form_title": q.get("form_title", "상담 신청"),
                "form_description": q.get("form_description", ""),
                "prefill": answers,
                "errors": errors,
                "edit_mode": False,
                "edit_token": None,
            },
        )

    edit_token, client_id, ts = _submit(answers)
    _post_submit_conversion(client_id, answers, ts)
    return templates.TemplateResponse(
        request,
        "confirm.html",
        {
            "edit_token": edit_token,
            "fake": False,
        },
    )

# ---------------------------------------------------------------------------
# 라우트: GET /edit/{edit_token}
# ---------------------------------------------------------------------------

@app.get("/edit/{edit_token}", response_class=HTMLResponse)
async def edit_form(request: Request, edit_token: str):
    # BLOCK-2: edit_token 포맷 검증 (path traversal 방어)
    if not _EDIT_TOKEN_RE.fullmatch(edit_token):
        raise HTTPException(status_code=404, detail="수정 링크가 유효하지 않습니다.")
    # edit_token으로 client 찾기
    client_id = _find_client_by_token(edit_token)
    if not client_id:
        raise HTTPException(status_code=404, detail="수정 링크가 유효하지 않습니다.")

    revisions = _list_revisions(client_id)
    latest_answers = revisions[-1]["answers"] if revisions else {}

    q = get_questions()
    return templates.TemplateResponse(
        request,
        "form.html",
        {
            "questions": q["questions"],
            "form_title": q.get("form_title", "상담 신청"),
            "form_description": q.get("form_description", ""),
            "prefill": latest_answers,
            "errors": [],
            "edit_mode": True,
            "edit_token": edit_token,
        },
    )


@app.post("/edit/{edit_token}", response_class=HTMLResponse)
async def edit_submit(request: Request, edit_token: str):
    # BLOCK-2: edit_token 포맷 검증 (path traversal 방어)
    if not _EDIT_TOKEN_RE.fullmatch(edit_token):
        raise HTTPException(status_code=404, detail="수정 링크가 유효하지 않습니다.")

    # BLOCK-1: 실제 클라이언트 IP (X-Forwarded-For 우선)
    ip = _client_ip(request)
    if not _check_rate_limit(ip):
        raise HTTPException(status_code=429, detail="너무 많은 요청입니다. 잠시 후 다시 시도해 주세요.")

    client_id = _find_client_by_token(edit_token)
    if not client_id:
        raise HTTPException(status_code=404, detail="수정 링크가 유효하지 않습니다.")

    form = await request.form()
    if form.get("_hp", ""):
        return templates.TemplateResponse(
            request,
            "confirm.html",
            {"edit_token": edit_token, "fake": True},
        )

    q = get_questions()
    questions = q["questions"]

    answers: dict[str, Any] = {}
    for question in questions:
        qid = question["id"]
        if question["type"] == "multiselect":
            vals = form.getlist(qid)
            answers[qid] = vals if vals else []
        else:
            answers[qid] = form.get(qid, "").strip()

    errors = _validate(answers, questions)
    if errors:
        return templates.TemplateResponse(
            request,
            "form.html",
            {
                "questions": questions,
                "form_title": q.get("form_title", "상담 신청"),
                "form_description": q.get("form_description", ""),
                "prefill": answers,
                "errors": errors,
                "edit_mode": True,
                "edit_token": edit_token,
            },
        )

    # append-only: 새 revision 추가 (기존 meta의 edit_token 유지)
    meta = _load_meta(client_id)
    ts = _save_revision(client_id, answers)
    if meta:
        meta["updated_at"] = ts
        _save_meta(client_id, meta)

    _post_submit_conversion(client_id, answers, ts)
    return templates.TemplateResponse(
        request,
        "confirm.html",
        {
            "edit_token": edit_token,
            "fake": False,
        },
    )

# ---------------------------------------------------------------------------
# 라우트: GET /admin
# ---------------------------------------------------------------------------

# BLOCK-2: 입력값 포맷 검증 정규식
_CLIENT_ID_RE = re.compile(r"^[0-9a-f]{16,32}$")
# edit_token: secrets.token_urlsafe(32) → URL-safe base64 43자 (A-Za-z0-9_-)
_EDIT_TOKEN_RE = re.compile(r"^[A-Za-z0-9_\-]{20,60}$")
# letter_token: secrets.token_urlsafe(16) → URL-safe base64 22자 (A-Za-z0-9_-)
_LETTER_TOKEN_RE = re.compile(r"^[A-Za-z0-9_\-]{10,40}$")


@app.get("/admin", response_class=HTMLResponse)
async def admin_list(request: Request, detail: str | None = None):
    # 미설정 시 404
    if not _admin_password():
        raise HTTPException(status_code=404)

    # FIX-1: lockout 먼저 확인 (인증 시도 전)
    ip = _client_ip(request)
    if not _check_admin_lockout(ip):
        return Response(
            content="너무 많은 인증 실패. 15분 후 다시 시도하세요.",
            status_code=429,
        )

    if not _check_admin_auth(request):
        _record_admin_fail(ip)
        return Response(
            content="인증이 필요합니다.",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="intake-admin"'},
        )

    # BLOCK-2: detail 파라미터 path traversal 방어 — 포맷 검증 + resolve 이중 방어
    clients_dir = _data_dir() / "clients"
    if detail is not None:
        if not _CLIENT_ID_RE.fullmatch(detail):
            raise HTTPException(status_code=400, detail="잘못된 client_id 형식입니다.")
        # resolve().is_relative_to() 이중 방어
        candidate = (_client_dir(detail)).resolve()
        if not str(candidate).startswith(str(clients_dir.resolve())):
            raise HTTPException(status_code=400, detail="잘못된 경로입니다.")

    client_list = []
    if clients_dir.exists():
        for meta_path in sorted(clients_dir.glob("*/meta.json")):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
            client_id = meta["client_id"]
            revs = _list_revisions(client_id)
            rev_count = len(revs)
            latest_rev = revs[-1]["answers"] if revs else {}
            client_list.append({
                "client_id": client_id,
                "email": meta.get("email", ""),
                "company": latest_rev.get("company_name", ""),
                "industry": latest_rev.get("industry", ""),
                "updated_at": meta.get("updated_at", ""),
                "rev_count": rev_count,
            })

    # 상세 보기
    detail_data = None
    if detail:
        meta = _load_meta(detail)
        if meta:
            revs = _list_revisions(detail)
            detail_data = {"meta": meta, "revisions": revs}

    return templates.TemplateResponse(
        request,
        "admin.html",
        {
            "clients": client_list,
            "detail": detail_data,
            "detail_id": detail,
        },
    )

# ---------------------------------------------------------------------------
# 라우트: GET /letter/{token}
# ---------------------------------------------------------------------------

@app.get("/letter/{token}", response_class=HTMLResponse)
async def letter(request: Request, token: str):
    """신뢰된 내부 안내문(PM 작성)을 base 템플릿에 래핑해 서빙한다.

    letter HTML 파일은 PM 이 작성한 신뢰된 내부 산출물이다.
    외부 사용자 입력이 아니므로 본문 markup 을 safe 처리한다.
    단, base 템플릿 변수 주입부(title 등)는 autoescape 를 유지한다.

    token 규약: secrets.token_urlsafe(16) 산출물 (URL-safe, 경로 traversal 차단).
    파일 위치: DATA_DIR/letters/<token>.html
    """
    # BLOCK-2 계승: token 포맷 검증 (path traversal 방어)
    if not _LETTER_TOKEN_RE.fullmatch(token):
        raise HTTPException(status_code=404, detail="안내문을 찾을 수 없습니다.")

    letters_dir = _data_dir() / "letters"
    candidate = (letters_dir / f"{token}.html").resolve()
    # resolve 이중 방어: 정규화된 경로가 letters_dir 하위여야 한다
    if not str(candidate).startswith(str(letters_dir.resolve())):
        raise HTTPException(status_code=404, detail="안내문을 찾을 수 없습니다.")

    if not candidate.exists():
        raise HTTPException(status_code=404, detail="안내문을 찾을 수 없습니다.")

    body = candidate.read_text(encoding="utf-8")

    # <title> 태그가 있으면 추출해 템플릿 title 변수로 노출, 없으면 기본값
    import html as _html_mod
    _title_match = re.search(r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
    page_title = _html_mod.unescape(_title_match.group(1).strip()) if _title_match else "안내문"

    return templates.TemplateResponse(
        request,
        "letter.html",
        {
            "title": page_title,
            "body": body,
        },
    )


# ---------------------------------------------------------------------------
# 라우트: GET /health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

# ---------------------------------------------------------------------------
# 내부 헬퍼: edit_token → client_id
# ---------------------------------------------------------------------------

def _find_client_by_token(edit_token: str) -> str | None:
    """edit_token으로 client_id를 찾는다. 없으면 None."""
    clients_dir = _data_dir() / "clients"
    if not clients_dir.exists():
        return None
    for meta_path in clients_dir.glob("*/meta.json"):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        # 상수시간 비교 (timing attack 방지)
        stored_token = meta.get("edit_token", "")
        if stored_token and secrets.compare_digest(stored_token, edit_token):
            return meta["client_id"]
    return None
