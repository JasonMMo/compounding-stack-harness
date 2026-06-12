"""
apps/intake/make_letter.py — 로컬 letter 생성 헬퍼

사용법:
  python make_letter.py <plain.txt> [--title "제목"] [--out-dir out/letters]

동작:
  1. plain.txt 를 읽어 문단 구조를 보존해 HTML 로 변환한다.
     - 빈 줄 구분 문단 → <p> 태그
     - 줄 끝 \\n 보존 → <br> 처리 (문단 내 줄바꿈)
  2. secrets.token_urlsafe(16) 으로 랜덤 토큰을 생성한다.
  3. <out-dir>/<token>.html 로 저장한다.
  4. stdout 에 토큰과 예상 URL 을 출력한다.

업로드는 CTO 가 scp 로 DATA_DIR/letters/ 에 배포한다.

PYTHONIOENCODING=utf-8 환경을 권장한다.
"""
from __future__ import annotations

import argparse
import html
import secrets
import sys
from pathlib import Path


def _txt_to_html(text: str, title: str) -> str:
    """평문 텍스트를 문단 구조 보존 HTML 로 변환한다.

    규칙:
    - 빈 줄(1개 이상)로 구분된 블록을 <p> 로 감싼다.
    - 블록 내 줄바꿈은 <br> 로 처리한다.
    - 모든 텍스트는 html.escape 로 이스케이프한다.
    - <title> 태그에 제목을 넣어 letter 라우트가 추출할 수 있게 한다.
    """
    # 줄 끝 공백 제거
    lines = [ln.rstrip() for ln in text.splitlines()]

    # 빈 줄 기준으로 문단 분리
    paragraphs: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line == "":
            if current:
                paragraphs.append(current)
                current = []
        else:
            current.append(line)
    if current:
        paragraphs.append(current)

    # 각 문단을 <p> 로 감싸기
    p_tags: list[str] = []
    for para in paragraphs:
        escaped_lines = [html.escape(ln) for ln in para]
        p_tags.append("<p>" + "<br>\n".join(escaped_lines) + "</p>")

    body_html = "\n".join(p_tags)
    escaped_title = html.escape(title)

    return f"<title>{escaped_title}</title>\n{body_html}\n"


def generate_letter(
    source_txt: Path,
    title: str,
    out_dir: Path,
) -> tuple[str, Path]:
    """letter HTML 파일을 생성하고 (token, path) 를 반환한다."""
    text = source_txt.read_text(encoding="utf-8")
    html_content = _txt_to_html(text, title)

    token = secrets.token_urlsafe(16)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{token}.html"
    out_path.write_text(html_content, encoding="utf-8")
    return token, out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="평문 txt 를 letter HTML 로 변환하고 랜덤 토큰 파일명으로 저장한다."
    )
    parser.add_argument("source", help="변환할 평문 txt 파일 경로")
    parser.add_argument("--title", default="안내문", help="letter 제목 (기본값: 안내문)")
    parser.add_argument(
        "--out-dir",
        default="out/letters",
        help="출력 디렉터리 (기본값: out/letters)",
    )
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"오류: 파일을 찾을 수 없습니다 — {source_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out_dir)
    token, out_path = generate_letter(source_path, args.title, out_dir)

    print(f"token : {token}")
    print(f"path  : {out_path.resolve()}")
    print(f"url   : <BASE_URL>/letter/{token}")
    print()
    print("업로드: scp {path} <server>:<DATA_DIR>/letters/{token}.html".format(
        path=out_path.resolve(), token=token
    ))


if __name__ == "__main__":
    main()
