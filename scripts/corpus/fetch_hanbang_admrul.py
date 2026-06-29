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
SEARCH_KEYWORDS = ["첩약 급여", "한방 건강보험", "한의약", "약침"]


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
    행정규칙 항목: <admrul> 하위 한글 태그 (실제 응답 구조 기준)
      - 행정규칙명, 행정규칙ID, 소관부처명, 행정규칙종류, 발령일자
    반환: [{"name": ..., "id": ..., "ministry": ..., "kind": ..., "date": ...}, ...]
    """
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        print(f"  [WARN] XML parse error: {e}")
        return []

    results = []
    # 행정규칙 항목 태그 — 한글 자식 태그 우선 (실제 API 응답 구조)
    for item in root.iter():
        tag = item.tag.lower()
        if tag in ("admrul",):
            name_el = item.find("행정규칙명")
            id_el = item.find("행정규칙ID")
            seq_el = item.find("행정규칙일련번호")
            link_el = item.find("행정규칙상세링크")
            ministry_el = item.find("소관부처명")
            kind_el = item.find("행정규칙종류")
            date_el = item.find("발령일자")
            # 한글 태그가 없을 때만 영문 태그 fallback
            if name_el is None:
                name_el = item.find("admrulNm")
            if id_el is None:
                id_el = item.find("admrulSeq") or item.find("mst") or item.find("admrulId")
            if ministry_el is None:
                ministry_el = item.find("chrDeptNm") or item.find("ministryNm")
            results.append({
                "name": name_el.text.strip() if name_el is not None and name_el.text else "",
                "id": id_el.text.strip() if id_el is not None and id_el.text else "",
                # 본문조회 ID= 파라미터는 행정규칙ID 가 아니라 행정규칙일련번호 를 쓴다
                "seq": seq_el.text.strip() if seq_el is not None and seq_el.text else "",
                # 검색 응답이 제공하는 상세링크(OC·target·ID 임베드) — 본문조회에 직접 사용
                "detail_link": link_el.text.strip() if link_el is not None and link_el.text else "",
                "ministry": ministry_el.text.strip() if ministry_el is not None and ministry_el.text else "",
                "kind": kind_el.text.strip() if kind_el is not None and kind_el.text else "",
                "date": date_el.text.strip() if date_el is not None and date_el.text else "",
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
                    "kind": "",
                    "date": "",
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
            "search": "2",  # 2=본문검색 (1=법령명만) — 첩약/약침 등 제목 미포함 고시도 수집
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

    # 2. 본문 조회 — 관련 항목 우선 선택 (남북한방문 같은 오탐 제외)
    if not unique_hits:
        print("\n[결론] 중복 제거 후 유효 항목 없음")
        return

    _RELEVANT = ("한의", "한방", "첩약", "약침", "한의약")
    target_item = next(
        (h for h in unique_hits if any(k in h["name"] for k in _RELEVANT)),
        unique_hits[0],  # 관련 항목 없으면 첫 번째
    )
    print(f"\n[본문 조회] {target_item['name']} (id={target_item['id']}, seq={target_item.get('seq','')})")

    detail_raw: bytes | None = None
    saved_path: Path | None = None

    # 본문조회 URL 후보: ①검색이 준 상세링크(가장 견고, ID=행정규칙일련번호 임베드)
    #                    ②행정규칙일련번호를 ID= 로 직접 구성 (상세링크 부재 시)
    detail_urls: list[tuple[str, str]] = []
    link = target_item.get("detail_link", "")
    if link:
        full = "https://www.law.go.kr" + link
        if "type=" not in full:
            full += "&type=XML"
        detail_urls.append(("상세링크", full))
    if target_item.get("seq"):
        params = urllib.parse.urlencode({
            "OC": oc_key, "target": "admrul", "type": "XML", "ID": target_item["seq"],
        })
        detail_urls.append(("일련번호 ID", f"{BASE_DETAIL_URL}?{params}"))

    for label, url in detail_urls:
        print(f"  시도: {label}  URL={mask_oc(url)}")
        try:
            raw = http_get(url)
            ET.fromstring(raw)  # XML 파싱 최소 확인
            decoded = raw.decode("utf-8", errors="replace")
            # 빈 응답/오류 스텁 감지 (예: "일치하는 행정규칙이 없습니다.")
            if "일치하는" in decoded or "없습니다" in decoded or len(decoded) < 300:
                print(f"  [WARN] {label} 빈/오류 응답 ({len(raw)} bytes) — 다음 후보 시도")
                continue
            detail_raw = raw
            print(f"  [OK] 본문 XML 수신 ({len(detail_raw)} bytes)")
            break
        except Exception as e:
            print(f"  [WARN] {label} 실패: {e}")

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
