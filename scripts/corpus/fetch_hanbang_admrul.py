"""
fetch_hanbang_admrul.py
-----------------------
한방 급여 관련 보건복지부 고시(행정규칙)를 law.go.kr Open API로 수집하는 PoC.

사용:
    python scripts/corpus/fetch_hanbang_admrul.py

보안 원칙:
- OC 키는 stdout/로그/반환에 절대 출력 안 함.
- URL 출력 시 OC 파라미터는 OC=*** 마스킹.
"""

import sys
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
SECRETS_FILE = Path(__file__).parent.parent.parent / "infra" / "secrets" / "open.law.go.kr.env"
OUT_DIR = Path(__file__).parent.parent.parent / "out" / "corpus" / "hanbang"
BASE_SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
BASE_DETAIL_URL = "https://www.law.go.kr/DRF/lawService.do"
TIMEOUT = 15
SEARCH_KEYWORDS = ["첩약", "한방", "한의", "약침"]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def load_oc_key() -> str:
    """infra/secrets/open.law.go.kr.env 에서 LAW_GO_KR_OC 값을 읽는다."""
    if not SECRETS_FILE.exists():
        sys.exit(f"[ERROR] secrets file not found: {SECRETS_FILE}")

    with SECRETS_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("LAW_GO_KR_OC="):
                val = line.split("=", 1)[1].strip()
                if val:
                    return val
    sys.exit("[ERROR] LAW_GO_KR_OC not found in secrets file")


def mask_oc(url: str) -> str:
    """URL의 OC 파라미터 값을 마스킹한다."""
    return re.sub(r"(OC=)[^&]+", r"\1***", url)


def http_get(url: str) -> bytes:
    """URL GET 요청. 타임아웃 15s. 실패 시 예외."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (PoC/1.0)"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def check_auth_error(xml_bytes: bytes) -> str | None:
    """인증/IP 오류 응답이면 에러 메시지를 반환, 아니면 None."""
    try:
        root = ET.fromstring(xml_bytes)
        result_el = root.find(".//result")
        if result_el is not None and result_el.text:
            text = result_el.text.strip()
            if "검증" in text or "실패" in text or "오류" in text:
                msg_el = root.find(".//msg")
                msg = msg_el.text.strip() if msg_el is not None and msg_el.text else ""
                return f"{text} | {msg}"
    except Exception:
        pass
    return None


def parse_search_xml(xml_bytes: bytes) -> list[dict]:
    """
    lawSearch.do 응답 XML 파싱.
    행정규칙 항목: <admrul> 하위 <admrulNm>, <admrulSeq> (또는 <mst>)
    반환: [{"name": ..., "id": ..., "ministry": ...}, ...]
    """
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        print(f"  [WARN] XML parse error: {e}")
        return []

    results = []
    # 행정규칙 항목 태그 후보
    for item in root.iter():
        tag = item.tag.lower()
        if tag in ("admrul",):
            name_el = item.find("admrulNm")
            seq_el = item.find("admrulSeq") or item.find("mst") or item.find("admrulId")
            ministry_el = item.find("chrDeptNm") or item.find("ministryNm")
            results.append({
                "name": name_el.text.strip() if name_el is not None and name_el.text else "",
                "id": seq_el.text.strip() if seq_el is not None and seq_el.text else "",
                "ministry": ministry_el.text.strip() if ministry_el is not None and ministry_el.text else "",
            })

    # fallback: 응답이 다른 구조일 수 있음 (law 항목으로 섞여서 올 때)
    if not results:
        for item in root.iter():
            tag = item.tag.lower()
            if tag in ("law", "prec", "ordin"):
                name_el = (item.find("lawNm") or item.find("precNm") or
                           item.find("ordinNm") or item.find("name"))
                seq_el = (item.find("lawSeq") or item.find("mst") or item.find("lawId"))
                ministry_el = item.find("chrDeptNm") or item.find("ministryNm")
                results.append({
                    "name": name_el.text.strip() if name_el is not None and name_el.text else "",
                    "id": seq_el.text.strip() if seq_el is not None and seq_el.text else "",
                    "ministry": ministry_el.text.strip() if ministry_el is not None and ministry_el.text else "",
                    "tag": tag,
                })

    return results


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    oc_key = load_oc_key()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== law.go.kr 행정규칙 한방 급여 PoC ===\n")

    all_hits: list[dict] = []

    # 1. 목록 조회 — 검색어별 순회
    for keyword in SEARCH_KEYWORDS:
        params = urllib.parse.urlencode({
            "OC": oc_key,
            "target": "admrul",
            "type": "XML",
            "query": keyword,
            "display": "20",
        })
        url = f"{BASE_SEARCH_URL}?{params}"
        print(f"[검색] keyword={keyword!r}  URL={mask_oc(url)}")

        try:
            raw = http_get(url)
        except Exception as e:
            print(f"  [ERROR] HTTP 실패: {e}")
            continue

        # 인증/IP 오류 조기 감지
        auth_err = check_auth_error(raw)
        if auth_err:
            print(f"  [AUTH ERROR] {auth_err}")
            print("  [HINT] 이 OC 키는 특정 서버 IP에만 허용됩니다. VPS(187.77.140.157)에서 실행하세요.")
            # 첫 키워드에서만 출력, 나머지는 스킵
            break

        items = parse_search_xml(raw)
        print(f"  결과: {len(items)}건")
        for i in items[:3]:
            print(f"    - {i['name']}  (id={i['id']}, 부처={i['ministry']})")

        for item in items:
            item["keyword"] = keyword
        all_hits.extend(items)

    if not all_hits:
        print("\n[결론] 행정규칙 목록 없음 -- IP 화이트리스트 제한 또는 admrul target 파라미터 문제 가능성")
        print("[ACTION] VPS(187.77.140.157)에서 재실행하면 IP 제한 해소 가능")
        return

    # 중복 제거 (id 기준)
    seen: set[str] = set()
    unique_hits = []
    for h in all_hits:
        if h["id"] and h["id"] not in seen:
            seen.add(h["id"])
            unique_hits.append(h)

    print(f"\n[합계] 고유 행정규칙 {len(unique_hits)}건 (중복 제거 후)")

    # 2. 본문 조회 — 첫 번째 유효 항목
    target_item = unique_hits[0]
    print(f"\n[본문 조회] {target_item['name']} (id={target_item['id']})")

    detail_raw: bytes | None = None
    saved_path: Path | None = None

    for id_param in ("ID", "MST"):
        if not target_item["id"]:
            break
        params = urllib.parse.urlencode({
            "OC": oc_key,
            "target": "admrul",
            "type": "XML",
            **{id_param: target_item["id"]},
        })
        url = f"{BASE_DETAIL_URL}?{params}"
        print(f"  시도: {id_param} 파라미터  URL={mask_oc(url)}")
        try:
            detail_raw = http_get(url)
            # XML 파싱 최소 확인
            ET.fromstring(detail_raw)
            print(f"  [OK] 본문 XML 수신 ({len(detail_raw)} bytes)")
            break
        except Exception as e:
            print(f"  [WARN] {id_param} 실패: {e}")
            detail_raw = None

    if detail_raw:
        slug = re.sub(r"[^\w가-힣-]", "_", target_item["name"])[:60]
        saved_path = OUT_DIR / f"{slug}.xml"
        saved_path.write_bytes(detail_raw)
        char_count = len(detail_raw.decode("utf-8", errors="replace"))
        print(f"\n[저장] {saved_path}")
        print(f"  본문 글자수(UTF-8 근사): {char_count:,}")
    else:
        print("\n[본문] 저장 실패 — ID 파라미터 방식 둘 다 실패")

    # 3. 판정
    print("\n=== 판정 ===")
    hit_count = len(unique_hits)
    if detail_raw and saved_path:
        print(f"게이트② corpus 수집경로: 확증  (검색 {hit_count}건, 본문 1건 저장 완료)")
    elif hit_count > 0:
        print(f"게이트② corpus 수집경로: 부분확증  (검색 {hit_count}건 찾음, 본문 저장 실패)")
    else:
        print("게이트② corpus 수집경로: 실패  (검색 결과 없음)")


if __name__ == "__main__":
    main()
