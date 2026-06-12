"""
seed_demo_data.py — deterministic demo seed generator.

Reads out/<slug>/screen-manifest.json, generates 8~15 plausible Korean
fictional records per entity, writes out/<slug>/seed-data.json.

Usage:
    python scripts/workflow/seed_demo_data.py --profile edu-program
    python scripts/workflow/seed_demo_data.py --profile edu-program --out out/

Rules:
  - PYTHONIOENCODING=utf-8
  - random.seed fixed per (slug + entity_type) for deterministic output
  - No real persons, institutions, or PII — purely fictional values
  - Field-type dispatch: string/name/email/phone/date/timestamp/decimal/
    integer/boolean/enum/uuid/text/code
  - Domain hints: crm→student names/depts, finance→budget items,
    asset→equipment names, document→official doc titles,
    lead→application/review status distribution

Exit codes: 0 success, 1 error.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Korean fictional name pool (purely fictional — not real persons)
# ---------------------------------------------------------------------------
_FAMILY_NAMES = [
    "김", "이", "박", "최", "정", "한", "조", "윤", "장", "임",
    "오", "신", "강", "권", "황", "안", "송", "홍", "류", "전",
]
_GIVEN_NAMES = [
    "민준", "서연", "지호", "예린", "하준", "수아", "도윤", "지아",
    "시우", "채원", "준서", "소율", "주원", "유진", "태양", "나연",
    "지훈", "서현", "민재", "예은", "현우", "지수", "성민", "하은",
    "동현", "은지", "재원", "수빈", "경민", "아린",
]

def _korean_name(rng: random.Random) -> str:
    return rng.choice(_FAMILY_NAMES) + rng.choice(_GIVEN_NAMES)

# ---------------------------------------------------------------------------
# Domain-specific pools
# ---------------------------------------------------------------------------
_EDU_DEPTS = [
    "컴퓨터공학과", "경영학과", "영어영문학과", "전자공학과",
    "사회복지학과", "수학과", "행정학과", "기계공학과",
    "심리학과", "교육학과",
]
_EDU_PROGRAMS = [
    "지역혁신사업단", "글로벌창업교육센터", "산학협력단", "취업지원팀",
    "교수학습개발원", "국제교류원",
]
_ASSET_NAMES = [
    "노트북 (Dell Latitude)", "프로젝터 (Epson EB-X51)", "책상 (6인용)",
    "서버랙 (42U)", "공기청정기 (LG 퓨리케어)", "모니터 (27인치 LG)",
    "프린터 (HP LaserJet Pro)", "냉장고 (소형 사무용)", "화이트보드 (이동식)",
    "카메라 (소니 ZV-E10)", "UPS 전원장치", "전자칠판 (75인치)",
    "복합기 (캐논 imageRUNNER)", "에어컨 (시스템)", "빔프로젝터 스크린",
]
_DOC_TITLES = [
    "2026년도 사업계획서", "협약 체결 결과 보고", "예산 집행 내역서",
    "성과지표 모니터링 보고", "참여 학생 선발 결과", "외부 전문가 자문 회의록",
    "현장실습 운영 지침", "연구윤리 서약서", "연간 교육 성과 보고서",
    "산학협력 협약서 (갱신)", "정산 보고서 (상반기)", "출장 복명서",
    "워크숍 결과 보고서", "설문 분석 결과서",
]
_FINANCE_DESCRIPTIONS = [
    "강사 인건비 지급", "교육 자료 구매", "학생 장학금 집행",
    "운영비 정산 (4월분)", "용역비 지급 (교육콘텐츠 개발)",
    "해외 파견 출장비", "장비 수리비 지급", "인쇄·제본비",
    "임차료 (실습실)", "외부 위탁 교육비",
]
_VENDOR_NAMES = [
    "(주)에듀테크솔루션", "한국교육기자재(주)", "글로벌이러닝(주)",
    "(주)스마트러닝", "교육콘텐츠개발원", "(주)미래인재개발",
    "에이치알디(주)", "테크브리지교육(주)",
]
_REPORT_NAMES = [
    "월별 참여 학생 현황", "지역 취업률 현황 (분기)",
    "사업비 집행 요약", "성과지표 달성률 보고",
    "외부 평가 대비 현황", "참여 기업 만족도 분석",
    "교육 이수 현황 (학과별)", "사업단 인력 현황",
]
_LOCATIONS = [
    "본관 3층 302호", "제2공학관 511호", "학생회관 B동",
    "IT센터 서버실", "행정동 1층 창고", "도서관 지하 1층",
    "실습동 401호", "경력개발센터 2층",
]

# ---------------------------------------------------------------------------
# Generic value generators by type / field-name heuristic
# ---------------------------------------------------------------------------

def _gen_uuid(rng: random.Random) -> str:
    # Use rng bytes for deterministic uuid
    return str(uuid.UUID(bytes=bytes(rng.getrandbits(8) for _ in range(16))))


def _gen_date(rng: random.Random, future: bool = False) -> str:
    year = 2025 if not future else 2026
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def _gen_timestamp(rng: random.Random) -> str:
    date = _gen_date(rng)
    hour = rng.randint(8, 18)
    minute = rng.choice([0, 15, 30, 45])
    return f"{date}T{hour:02d}:{minute:02d}:00"


def _gen_amount(rng: random.Random, scale: str = "medium") -> float:
    """Generate plausible KRW amounts."""
    if scale == "large":
        base = rng.choice([500, 1000, 2000, 3000, 5000]) * 10000
    elif scale == "small":
        base = rng.choice([5, 10, 15, 20, 30, 50]) * 10000
    else:
        base = rng.choice([50, 100, 150, 200, 300, 500]) * 10000
    return float(base)


def _gen_hours(rng: random.Random) -> float:
    return float(rng.choice([20, 40, 80, 120, 160, 200]))


def _gen_code(rng: random.Random, prefix: str, idx: int) -> str:
    return f"{prefix}-{idx:04d}"


def _gen_email(rng: random.Random, name: str) -> str:
    domains = ["edu.kr", "univ.ac.kr", "college.ac.kr", "campus.kr"]
    slug = "".join(
        c for c in name.lower().replace(" ", "")
        if c.isascii() and c.isalnum()
    ) or f"user{rng.randint(100,999)}"
    if not slug:
        slug = f"user{rng.randint(100,999)}"
    return f"{slug}{rng.randint(10,99)}@{rng.choice(domains)}"


def _gen_phone(rng: random.Random) -> str:
    middle = rng.randint(1000, 9999)
    last = rng.randint(1000, 9999)
    return f"010-{middle}-{last}"


def _gen_version(rng: random.Random, idx: int) -> str:
    return f"v{rng.randint(1, 3)}.{rng.randint(0, 5)}"


def _gen_mime(rng: random.Random) -> str:
    return rng.choice([
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "image/png",
    ])


def _gen_checksum(rng: random.Random) -> str:
    return "".join(rng.choice("0123456789abcdef") for _ in range(40))


def _gen_storage_key(rng: random.Random, idx: int) -> str:
    return f"docs/{rng.randint(2024, 2026)}/{rng.randint(10000,99999)}/v{idx}.bin"


# ---------------------------------------------------------------------------
# Per-entity record generator
# ---------------------------------------------------------------------------

def _field_value(
    field: dict,
    entity_type: str,
    domain: str,
    idx: int,
    rng: random.Random,
    id_pools: dict[str, list[str]],
) -> object:
    name = field["name"]
    ftype = field["type"]

    # UUID foreign-key fields — pick from id_pool or generate stable placeholder
    if ftype == "uuid":
        if name.endswith("_id") or name == "owner_id" or name == "assigned_to":
            fk_entity = field.get("fk_entity")
            if fk_entity and fk_entity in id_pools and id_pools[fk_entity]:
                return rng.choice(id_pools[fk_entity])
        return _gen_uuid(rng)

    # Enum fields
    if ftype == "enum":
        options = field.get("options", [])
        if not options:
            return None
        # Apply distribution hints for lead.status
        if entity_type == "lead" and name == "status":
            # distribution: new(4) contacted(3) qualified(2) converted(2) disqualified(1)
            weighted = (
                ["new"] * 4 + ["contacted"] * 3 +
                ["qualified"] * 2 + ["converted"] * 2 + ["disqualified"] * 1
            )
            return rng.choice([o for o in weighted if o in options] or options)
        if entity_type == "lead" and name == "source":
            weighted = ["web"] * 4 + ["referral"] * 3 + ["event"] * 2 + ["cold-call"] * 1 + ["other"] * 1
            return rng.choice([o for o in weighted if o in options] or options)
        if entity_type == "invoice" and name == "status":
            weighted = ["issued"] * 4 + ["paid"] * 3 + ["draft"] * 2 + ["overdue"] * 1
            return rng.choice([o for o in weighted if o in options] or options)
        if entity_type == "asset" and name == "status":
            weighted = ["active"] * 7 + ["under-maintenance"] * 2 + ["disposed"] * 1
            return rng.choice([o for o in weighted if o in options] or options)
        return rng.choice(options)

    # Boolean
    if ftype == "boolean":
        if name == "is_active" or name == "is_approved" or name == "is_published":
            return rng.random() < 0.85
        return rng.random() < 0.5

    # Date / timestamp
    if ftype == "date":
        if "end" in name or "due" in name or "retention" in name:
            return _gen_date(rng, future=True)
        return _gen_date(rng)
    if ftype == "timestamp":
        return _gen_timestamp(rng)

    # Numeric
    if ftype == "decimal":
        if "amount" in name or "cost" in name or "value" in name or "budget" in name:
            return _gen_amount(rng)
        if "hours" in name:
            return _gen_hours(rng)
        return round(rng.uniform(10.0, 9999.0), 2)
    if ftype == "integer":
        if "life" in name or "years" in name:
            return rng.choice([3, 5, 7, 10, 15])
        if "size" in name or "bytes" in name:
            return rng.choice([102400, 512000, 1048576, 2097152, 4194304])
        if "retention" in name:
            return rng.choice([365, 730, 1825, 3650])
        if "row_count" in name:
            return rng.randint(10, 500)
        return rng.randint(1, 100)

    # Text / textarea
    if ftype in ("text",):
        if entity_type == "maintenance-record" and name == "description":
            return rng.choice([
                "정기 점검 완료. 이상 없음.",
                "부품 교체 (배터리 팩 교체)",
                "소프트웨어 업데이트 및 최적화",
                "화면 불량 수리 완료",
                "하드디스크 교체 완료",
                "펌웨어 업그레이드 적용",
            ])
        if entity_type == "report-definition" and name == "description":
            return rng.choice([
                "학과별 월별 참여 현황을 집계한 보고서",
                "사업비 집행률을 분기별로 요약",
                "성과지표 달성 현황 자동 집계",
                "참여 기업 및 학생 만족도 분석",
                "취업률 추이를 연도별로 비교",
            ])
        if entity_type == "report-output" and name == "error_message":
            return None  # most outputs don't have errors
        return f"내용 {idx}"

    # String — heuristic dispatch on field name
    if ftype == "string":
        max_len = field.get("max_length", 255)

        if name == "full_name":
            return _korean_name(rng)

        if name == "email" or name == "contact_email":
            n = _korean_name(rng)
            return _gen_email(rng, n)[:max_len]

        if name == "phone":
            return _gen_phone(rng)[:max_len]

        if name in ("company_name",):
            if domain == "crm":
                return rng.choice(_EDU_DEPTS)[:max_len]
            return rng.choice(_VENDOR_NAMES)[:max_len]

        if name == "code":
            prefix_map = {
                "account": "AC", "project": "PRJ", "vendor": "VND",
                "asset-category": "CAT", "document-category": "DCAT",
                "report-definition": "RPT",
            }
            prefix = prefix_map.get(entity_type, entity_type[:3].upper())
            return _gen_code(rng, prefix, idx)[:max_len]

        if name == "name":
            if domain == "finance":
                return rng.choice(_FINANCE_DESCRIPTIONS)[:max_len]
            if domain == "asset":
                return rng.choice(_ASSET_NAMES)[:max_len]
            if domain == "procurement":
                return rng.choice(_VENDOR_NAMES)[:max_len]
            if domain == "reporting":
                return rng.choice(_REPORT_NAMES)[:max_len]
            if domain == "document":
                return rng.choice(_DOC_TITLES)[:max_len]
            return f"{entity_type}-{idx:03d}"

        if name == "title":
            return rng.choice(_DOC_TITLES)[:max_len]

        if name == "currency":
            return "KRW"

        if name == "payment_terms":
            return rng.choice(["30일", "60일", "즉시", "선금 50%"])[:max_len]

        if name == "summary":
            return rng.choice([
                "초기 상담 진행", "학과 안내 제공", "이메일 발송 완료",
                "입학처 연계", "산학 면담 실시", "프로그램 소개",
                "서류 접수 안내", "1차 심사 결과 전달",
            ])[:max_len]

        if name == "outcome":
            return rng.choice([
                "후속 면담 예정", "지원 의향 확인", "미응답",
                "합격 통보", "추가 서류 요청", "보류",
            ])[:max_len]

        if name == "role":
            return rng.choice([
                "PM", "교육 담당", "행정 지원", "멘토",
                "현장 지도교수", "외부 전문가",
            ])[:max_len]

        if name == "reference":
            return f"REF-{rng.randint(10000, 99999)}"[:max_len]

        if name == "asset_number":
            return _gen_code(rng, "AST", idx)

        if name == "serial_number":
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            return "".join(rng.choice(chars) for _ in range(10))[:max_len]

        if name == "location":
            return rng.choice(_LOCATIONS)[:max_len]

        if name == "invoice_number":
            return f"INV-{rng.randint(1000, 9999)}"[:max_len]

        if name == "performed_by":
            return _korean_name(rng)[:max_len]

        if name == "version_number":
            return _gen_version(rng, idx)[:max_len]

        if name == "file_name":
            return rng.choice([
                "사업계획서.pdf", "결과보고서.docx", "예산집행내역.xlsx",
                "협약서.pdf", "성과지표.xlsx", "출장보고서.docx",
            ])[:max_len]

        if name == "mime_type":
            return _gen_mime(rng)[:max_len]

        if name == "storage_key":
            return _gen_storage_key(rng, idx)[:max_len]

        if name == "checksum":
            return _gen_checksum(rng)[:max_len]

        if name == "domain":
            return rng.choice(["crm", "finance", "project", "asset", "document"])[:max_len]

        if name == "storage_key":
            return f"reports/{rng.randint(10000,99999)}.csv"[:max_len]

        if name == "error_message":
            return None

        # fallback
        return f"{entity_type}-{name}-{idx:03d}"[:max_len]

    return None


def generate_entity_records(
    entity_type: str,
    entity_def: dict,
    domain: str,
    count: int,
    rng: random.Random,
    id_pools: dict[str, list[str]],
) -> list[dict]:
    records = []
    generated_ids = []

    for idx in range(1, count + 1):
        rec_id = _gen_uuid(rng)
        generated_ids.append(rec_id)

        record: dict = {"id": rec_id}
        now_ms = 1748000000000 + idx * 86400000  # stable epoch ms

        for field in entity_def.get("fields", []):
            val = _field_value(field, entity_type, domain, idx, rng, id_pools)
            record[field["name"]] = val

        record["created_at"] = now_ms
        record["updated_at"] = now_ms

        records.append(record)

    # Expose generated ids for FK consumers (populated after generation)
    id_pools[entity_type] = generated_ids
    return records


def generate_seed(slug: str, out_root: Path) -> dict[str, list[dict]]:
    manifest_path = out_root / slug / "screen-manifest.json"
    if not manifest_path.exists():
        print(
            f"[seed_demo_data] ERROR: manifest not found at {manifest_path}\n"
            f"  Run: python scripts/workflow/scaffold.py --profile {slug}",
            file=sys.stderr,
        )
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entities: dict = manifest.get("entities", {})

    # Determine entity order: generate leaf entities first so FK pools are populated
    # Heuristic: entities with no FK fields first, then FK-dependent ones
    def _fk_count(ed: dict) -> int:
        return sum(1 for f in ed.get("fields", []) if f.get("fk_entity"))

    entity_order = sorted(entities.keys(), key=lambda k: _fk_count(entities[k]))

    id_pools: dict[str, list[str]] = {}
    seed_data: dict[str, list[dict]] = {}
    counts: dict[str, int] = {}

    for entity_type in entity_order:
        entity_def = entities[entity_type]
        domain = entity_def.get("domain", "generic")

        # Deterministic RNG per (slug, entity_type)
        rng = random.Random(f"{slug}::{entity_type}")
        count = rng.randint(8, 15)

        records = generate_entity_records(
            entity_type, entity_def, domain, count, rng, id_pools
        )
        seed_data[entity_type] = records
        counts[entity_type] = len(records)

    return seed_data, counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate deterministic demo seed data from screen-manifest.json."
    )
    parser.add_argument("--profile", required=True, help="Profile slug (e.g. edu-program)")
    parser.add_argument(
        "--out", default=str(REPO_ROOT / "out"),
        help="Output root directory (default: out/)",
    )
    args = parser.parse_args()

    slug = args.profile
    out_root = Path(args.out).resolve()

    print(f"[seed_demo_data] generating seed for profile={slug} ...")
    seed_data, counts = generate_seed(slug, out_root)

    out_dir = out_root / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    seed_path = out_dir / "seed-data.json"
    seed_path.write_text(
        json.dumps(seed_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    total = sum(counts.values())
    print(f"[seed_demo_data] written → {seed_path}")
    print(f"[seed_demo_data] entity counts (total={total}):")
    for et, n in counts.items():
        print(f"  {et}: {n} records")

    return 0


if __name__ == "__main__":
    sys.exit(main())
