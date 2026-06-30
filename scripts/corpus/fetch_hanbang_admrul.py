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
import json
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
# 본문 조회 최대 건수 (law.go.kr 호출 폭주 방지)
MAX_FULLTEXT = 12
# 데모 corpus: 검증된 한방 급여 관련 "전문(rich)" 고시 일련번호 (CTO 큐레이션 2026-06-30)
#   개정문(thin, 별표 미포함)만 반환하는 건강보험 세부사항/상대가치점수는 제외.
TARGET_SEQS = [
    "2100000270620",  # 의료급여수가의 기준 및 일반기준 (720K, 추나/한의/한방 급여 수가·기준)
    "2100000274952",  # 비급여 진료비용 등의 보고 및 공개에 관한 기준 (544K, 약침/첩약/추나 비급여)
    "2100000259168",  # 보건의료기술 분류체계에 관한 고시 (183K, 한의 의료기술 분류)
]


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
def parse_detail_meta(xml_bytes: bytes) -> dict:
    """행정규칙 본문 XML의 행정규칙기본정보에서 메타 추출."""
    meta = {"name": "", "seq": "", "ministry": "", "kind": "", "date": ""}
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return meta
    base = root.find(".//행정규칙기본정보")
    if base is None:
        return meta
    def _t(tag: str) -> str:
        el = base.find(tag)
        return el.text.strip() if el is not None and el.text else ""
    meta["name"] = _t("행정규칙명")
    meta["seq"] = _t("행정규칙일련번호")
    meta["ministry"] = _t("소관부처명")
    meta["kind"] = _t("행정규칙종류")
    meta["date"] = _t("발령일자")
    return meta


def fetch_fulltext(item: dict, oc_key: str) -> "bytes | None":
    """단일 행정규칙 항목의 본문 XML을 조회한다.

    ① 검색이 준 상세링크(OC·ID 임베드) → ② 일련번호 ID 직접구성 폴백.
    빈/오류 응답은 None. SECURITY: oc_key 는 URL 에만, 로그/반환에 노출 금지.
    """
    detail_urls: list[tuple[str, str]] = []
    link = item.get("detail_link", "")
    if link:
        full = "https://www.law.go.kr" + link
        if "type=" not in full:
            full += "&type=XML"
        detail_urls.append(("상세링크", full))
    if item.get("seq"):
        params = urllib.parse.urlencode({
            "OC": oc_key, "target": "admrul", "type": "XML", "ID": item["seq"],
        })
        detail_urls.append(("일련번호 ID", f"{BASE_DETAIL_URL}?{params}"))

    for label, url in detail_urls:
        print(f"    시도: {label}  URL={mask_oc(url)}")
        try:
            raw = http_get(url)
            ET.fromstring(raw)
            decoded = raw.decode("utf-8", errors="replace")
            if len(decoded) < 300 or (len(decoded) < 2000 and ("일치하는" in decoded or "없습니다" in decoded)):
                print(f"    [WARN] {label} 빈/오류 응답 ({len(raw)} bytes) — 다음 후보")
                continue
            print(f"    [OK] 본문 XML 수신 ({len(raw)} bytes)")
            return raw
        except Exception as e:
            print(f"    [WARN] {label} 실패: {e}")
    return None


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

    # 2. 본문 조회 — 큐레이션된 한방 급여 전문 고시(TARGET_SEQS) 수집
    #    키워드 검색(위)은 발견/로깅용. 실제 corpus 는 검증된 전문 고시로 큐레이션.
    print(f"\n[큐레이션 수집] TARGET_SEQS {len(TARGET_SEQS)}건 (검증된 전문 고시), 검색발견 {len(unique_hits)}건")
    manifest: list[dict] = []
    name_counter: dict[str, int] = {}

    for seq in TARGET_SEQS:
        body = fetch_fulltext({"seq": seq, "detail_link": ""}, oc_key)
        if body is None:
            print(f"  [SKIP] seq={seq} 본문 없음")
            continue
        meta = parse_detail_meta(body)
        name = meta["name"] or f"admrul_{seq}"
        print(f"  - {name[:50]} (seq={seq})")
        slug = re.sub(r"[^\w가-힣-]", "_", name)[:60] or "notice"
        n = name_counter.get(slug, 0)
        name_counter[slug] = n + 1
        fname = f"{slug}.xml" if n == 0 else f"{slug}_{n + 1}.xml"
        (OUT_DIR / fname).write_bytes(body)
        char_count = len(body.decode("utf-8", errors="replace"))
        manifest.append({
            "name": name,
            "id": "",
            "seq": seq,
            "ministry": meta["ministry"],
            "kind": meta["kind"],
            "date": meta["date"],
            "keyword": "curated",
            "char_count": char_count,
            "xml_file": fname,
        })

    manifest_path = OUT_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 3. 요약 + 판정
    print(f"\n=== 수집 요약 ({len(manifest)}건, manifest → {manifest_path.name}) ===")
    for m in manifest:
        print(f"  - {m['name'][:46]}  [{m['ministry']}/{m['date']}]  {m['char_count']:,}자  → {m['xml_file']}")
    print("\n=== 판정 ===")
    if manifest:
        print(f"corpus 수집: 확증  (큐레이션 {len(manifest)}건 저장)")
    else:
        print("corpus 수집: 실패  (TARGET_SEQS 본문조회 전부 실패)")


if __name__ == "__main__":
    main()
