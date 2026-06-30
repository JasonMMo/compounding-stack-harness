#!/usr/bin/env python3
# D3 라이브 검증: 로그인 + 5시나리오 하이브리드 검색 + 원문 드로어 1건
import json, urllib.request, urllib.error

BASE = "https://hanbang-rag.n9n.co.kr"

def post(path, body, token=None):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, json.loads(r.read().decode("utf-8"))

def get(path, token=None):
    req = urllib.request.Request(BASE + path, method="GET")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, json.loads(r.read().decode("utf-8"))

# 1) login
st, lr = post("/auth/login", {"email": "demo@hanbang-rag.local", "password": "hanbang2026"})
token = lr.get("token")
print(f"[LOGIN] HTTP {st} role={lr.get('role')} token={'OK' if token else 'MISSING'}")
assert token, "no token"

# 2) 5 search scenarios
QUERIES = [
    "추나요법 급여 기준",
    "비급여 진료비용 보고 대상",
    "의료급여 본인부담",
    "상대가치점수",
    "보건의료기술 분류체계",
]
first_source = None
for q in QUERIES:
    st, sr = post("/search", {"query": q, "top_k": 5, "match_mode": "or"}, token)
    results = sr.get("results", [])
    top = results[0] if results else None
    if top and not first_source:
        first_source = top.get("source_id")
    tn = top.get("notice_number") if top else "-"
    excerpt = (top.get("chunk_text_excerpt","")[:40].replace("\n"," ")) if top else ""
    print(f"[SEARCH] HTTP {st} q='{q}' -> {sr.get('total_results',0)}건 | top={tn} | {excerpt}")

# 3) 원문 드로어 (GET /documents/notice/{id})
if first_source:
    st, dr = get(f"/documents/notice/{first_source}", token)
    ft_len = len(dr.get("full_text") or "")
    print(f"[DOC] HTTP {st} notice={dr.get('notice_number')} ministry={dr.get('ministry')} full_text_len={ft_len}")
print("VERIFY_DONE")
