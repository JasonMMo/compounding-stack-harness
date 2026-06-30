"""
ingest_hanbang_notices.py — D2 corpus loader for hanbang-rag.

Reads curated admrul XMLs (manifest.json), extracts notice metadata + body,
upserts hanbang_rag_notice rows, then chunks+embeds via the REAL ingest.py
pipeline (no re-implementation) into hanbang_rag_document_chunk.

Run inside a one-off container on the Coolify network (reaches db + embed):
  DSN=postgresql://app_service:***@db:5432/legaldb \
  EMBED=http://embed:8080 \
  python ingest_hanbang_notices.py

Env:
  DSN     psycopg DSN (app_service role — BYPASSRLS, required for chunk writes)
  EMBED   embedding sidecar base URL (multilingual-e5-base, 768-dim)
  CORPUS  corpus dir containing manifest.json + *.xml (default /corpus)
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import psycopg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ingest as ing  # the real chunking/embedding pipeline
from embed_client import EmbedClient

DSN = os.environ["DSN"]
EMBED = os.environ["EMBED"].rstrip("/")
CORPUS = Path(os.environ.get("CORPUS", "/corpus"))
MODEL = os.environ.get("MODEL", "multilingual-e5-base")

# admrul content-bearing tags (metadata excluded)
CONTENT_TAGS = {"조문내용", "별표", "부칙내용"}

# ── 별표/서식 표-괘선 정제 (CTO 검증 2026-06-30, 실 corpus 3건) ──────────────
# law.go.kr 별표는 박스드로잉 문자로 표를 그린다. 셀 텍스트는 보존하고 테두리만
# 제거 → 임베딩/FTS/발췌문 품질 향상. 검증: 박스문자 195K→0, 핵심토큰(청구처·
# 연번·추나·상대가치·약침·첩약·대분류) 출현수 raw==clean(전부 보존), corpus 14~22%로 축소.
_BOX_CHARS = "─━│┃┌┐└┘├┤┬┴┼╋┏┓┗┛┣┫┳┻═║╔╗╚╝╠╣╦╩╬"
_BOX_RE = re.compile("[" + re.escape(_BOX_CHARS) + "]")
_RULE_LINE_RE = re.compile(r"^[\s" + re.escape(_BOX_CHARS) + r"]+$")
_PAPERSIZE_RE = re.compile(r"\d+\s*㎜\s*[×xX*]\s*\d+\s*㎜(?:\[[^\]]*\])?")
_MULTISPACE_RE = re.compile(r"[ \t]{2,}")
_MULTINEWLINE_RE = re.compile(r"\n{3,}")


def clean_admrul_text(text: str) -> str:
    """별표/서식의 표-괘선·용지규격 보일러플레이트를 제거(셀 텍스트는 보존)."""
    out = []
    for line in text.split("\n"):
        if _RULE_LINE_RE.match(line):
            continue  # 순수 표-괘선 줄 → 제거
        line = _BOX_RE.sub(" ", line)       # 테두리 → 공백 (셀 텍스트 보존)
        line = _PAPERSIZE_RE.sub("", line)  # 용지규격(210㎜×297㎜ 등) 제거
        line = _MULTISPACE_RE.sub(" ", line).rstrip()
        if line.strip():
            out.append(line)
    cleaned = "\n".join(out)
    cleaned = _MULTINEWLINE_RE.sub("\n\n", cleaned)
    return cleaned.strip()


_UPSERT_NOTICE = """
INSERT INTO hanbang_rag_notice
  (notice_number, ministry, issued_date, notice_type, summary, full_text)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (notice_number) DO UPDATE SET
  ministry    = EXCLUDED.ministry,
  issued_date = EXCLUDED.issued_date,
  notice_type = EXCLUDED.notice_type,
  summary     = EXCLUDED.summary,
  full_text   = EXCLUDED.full_text,
  updated_at  = now()
RETURNING id
"""


def parse_xml(path: Path):
    root = ET.parse(path).getroot()
    bi = root.find(".//행정규칙기본정보")

    def g(tag: str) -> str:
        if bi is None:
            return ""
        el = bi.find(tag)
        return (el.text or "").strip() if el is not None and el.text else ""

    name = g("행정규칙명")
    ministry = g("소관부처명") or "보건복지부"
    issued = g("발령일자")          # YYYYMMDD
    decree = g("발령번호")          # e.g. 2025-85
    seq = g("행정규칙일련번호")
    notice_number = (
        f"{ministry}고시 제{decree}호" if decree
        else f"{ministry}고시 일련{seq}"
    )
    issued_date = (
        f"{issued[:4]}-{issued[4:6]}-{issued[6:8]}" if len(issued) == 8 else None
    )

    parts = []
    for el in root.iter():
        if el.tag in CONTENT_TAGS:
            t = "".join(el.itertext()).strip()
            if t:
                parts.append(t)
    body = clean_admrul_text("\n\n".join(parts))
    return name, ministry, issued_date, notice_number, body


async def main() -> None:
    embed = EmbedClient(EMBED, timeout=120.0)
    if not embed.health_check():
        print(f"FATAL: embed sidecar not healthy at {EMBED}", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    print(f"manifest: {len(manifest)} curated notices")

    total_chunks = 0
    async with await psycopg.AsyncConnection.connect(DSN, autocommit=False) as conn:
        for entry in manifest:
            xml_path = CORPUS / entry["xml_file"]
            if not xml_path.exists():
                print(f"SKIP missing: {xml_path.name}")
                continue
            name, ministry, issued_date, nn, body = parse_xml(xml_path)
            if not body.strip():
                print(f"SKIP no-body: {xml_path.name}")
                continue
            summary = body[:300]
            async with conn.cursor() as cur:
                await cur.execute(
                    _UPSERT_NOTICE,
                    (nn, ministry, issued_date, "고시", summary, body),
                )
                row = await cur.fetchone()
                nid = row[0]
            await conn.commit()

            txt = Path("/tmp") / f"{nid}.txt"
            txt.write_text(body, encoding="utf-8")

            n = await ing.ingest_file(
                conn=conn,
                embed_client=embed,
                model_version=MODEL,
                file_path=str(txt),
                source_type="notice",
                source_id=nid,
                chunk_token_target=500,
                chunk_overlap_tokens=50,
                batch_size=8,
            )
            await conn.commit()
            total_chunks += n
            print(
                f"OK  {name[:30]:<30} | {nn:<28} | {issued_date} "
                f"| body={len(body):>7} | chunks={n}"
            )

    print(f"DONE total_chunks={total_chunks}")


if __name__ == "__main__":
    asyncio.run(main())