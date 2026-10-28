"""
record_noshow_demo.py — 노쇼가드 30초 시연 영상 자동 녹화 (크몽/숨고 포트폴리오용).

Playwright 가 데모의 3단계 시나리오(docs/business/noshow-demo-spec.md §2)를
실제로 조작하며 녹화하고, 자막·가짜 커서·인트로/아웃트로를 페이지 안에서
렌더링한다. 나레이션 원고(narration.md)·TTS 입력(narration.txt)·자막(.srt)은
SCENES 단일 소스에서 실측 장면 시각으로 생성된다.

전제: 데모 서버가 **방금 기동된 상태**(시드 직후)여야 한다 — 빨리감기·취소가
DB 를 바꾸므로 재녹화 시 서버를 재시작한다.

    python scripts/video/record_noshow_demo.py --base-url http://localhost:18765
    # 산출: out/noshow-video/{noshow-demo.mp4, noshow-demo.srt, narration.md, narration.txt, timeline.json}

비용: LLM/API 호출 0. Playwright + ffmpeg 로컬만 사용.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

# 가로: 앱은 1280 CSS폭 레이아웃 그대로, body zoom 으로 1080p 선명 렌더링.
# 세로(9:16, 숨고·모바일 피드): 432 CSS폭 = 앱의 모바일 레이아웃.
# (device_scale_factor 는 Playwright 녹화 프레임에 반영되지 않아 화면 1/4만 찍힘)
LAYOUTS = {"landscape": (1920, 1080, 1.5), "vertical": (1080, 1920, 2.5)}
VIEW_W, VIEW_H, ZOOM = LAYOUTS["landscape"]

# 단일 소스: (key, 목표 길이 s, 자막, 나레이션)
SCENES = [
    ("intro", 3.0, None,
     "미용실 노쇼, 이제 자동으로 막으세요."),
    ("booking", 9.0, "손님은 시술·날짜·시간만 고르면 예약 끝",
     "손님은 휴대폰으로 시술과 날짜, 시간만 고르면 예약이 끝납니다."),
    ("confirm", 4.5, "예약 즉시, 확인 카톡 자동 발송",
     "예약하는 순간, 확인 카톡이 자동으로 나갑니다."),
    ("reminder", 6.5, "전날·당일 리마인더 자동 발송",
     "전날과 당일엔 리마인더가 자동으로 나가고, 노쇼 위험 손님은 따로 표시됩니다."),
    ("cancel", 7.5, "취소가 나면 대기 손님으로 빈자리 자동 채움",
     "갑자기 취소가 나도, 대기 손님에게 바로 제안이 가서 빈자리가 채워집니다."),
    ("outro", 4.5, None,
     "예약·노쇼 자동화, 노쇼가드. 라이브 데모로 먼저 체험해 보세요."),
]

OVERLAY_JS = r"""
(() => {
  // zoom 은 미디어쿼리 판정 폭을 안 바꾼다 — 실효 CSS폭(innerWidth/zoom)보다 큰
  // min-width 규칙을 지워 세로판에서 앱의 모바일 레이아웃이 걸리게 한다.
  const fitMedia = () => {
    if (document.body.hasAttribute('data-vid-nozoom')) return;
    const w = innerWidth / __ZOOM__;
    for (const sheet of document.styleSheets) {
      let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
      for (let i = rules.length - 1; i >= 0; i--) {
        const m = rules[i] instanceof CSSMediaRule && rules[i].conditionText.match(/min-width:\s*(\d+)px/);
        if (m && +m[1] > w) sheet.deleteRule(i);
      }
    }
  };
  addEventListener('load', fitMedia);
  const install = () => {
    if (document.getElementById('__vid_style')) return;
    fitMedia();
    if (!document.body.hasAttribute('data-vid-nozoom')) document.body.style.zoom = '__ZOOM__';
    const st = document.createElement('style');
    st.id = '__vid_style';
    st.textContent = `
      #__vid_cap{position:fixed;left:50%;bottom:54px;transform:translate(-50%,18px);opacity:0;
        transition:opacity .35s ease,transform .35s ease;z-index:2147483646;pointer-events:none;
        background:rgba(28,28,40,.9);color:#fff;font:700 45px/1.3 "Malgun Gothic",sans-serif;
        padding:21px 45px;border-radius:999px;white-space:nowrap;box-shadow:0 12px 42px rgba(0,0,0,.25)}
      #__vid_cap.on{opacity:1;transform:translate(-50%,0)}
      #__vid_cap b{display:inline-block;background:#5b4bff;border-radius:999px;font-size:30px;
        padding:4px 18px;margin-right:21px;vertical-align:6px}
      @media (max-aspect-ratio:1/1){#__vid_cap{bottom:120px;width:max-content;max-width:900px;
        white-space:normal;text-align:center;border-radius:36px;word-break:keep-all}}
      #__vid_cur{position:fixed;left:960px;top:600px;width:42px;height:42px;z-index:2147483647;
        pointer-events:none;transition:left .55s cubic-bezier(.3,.7,.2,1),top .55s cubic-bezier(.3,.7,.2,1)}
      .__vid_ripple{position:fixed;width:24px;height:24px;margin:-12px 0 0 -12px;border-radius:50%;
        background:rgba(91,75,255,.45);z-index:2147483645;pointer-events:none;animation:__vr .55s ease-out forwards}
      @keyframes __vr{to{transform:scale(4.5);opacity:0}}
      .__vid_hl{outline:3px solid #5b4bff !important;outline-offset:3px;border-radius:10px;
        animation:__vh 1.2s ease-out 2}
      @keyframes __vh{0%{box-shadow:0 0 0 0 rgba(91,75,255,.55)}100%{box-shadow:0 0 0 16px rgba(91,75,255,0)}}
    `;
    document.head.appendChild(st);
    const cap = document.createElement('div'); cap.id = '__vid_cap';
    const cur = document.createElement('div'); cur.id = '__vid_cur';
    cur.innerHTML = '<svg viewBox="0 0 24 24" width="42" height="42"><path d="M4 2l15 10-7 1.5 4 7.5-3 1.5-4-7.5L4 20z" fill="#1c1c28" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    // body 밖(html 직속)에 둬야 zoom 영향 없이 Playwright 뷰포트 좌표와 일치
    document.documentElement.append(cap, cur);
  };
  window.__vid = {
    caption(text, step) {
      install();
      const cap = document.getElementById('__vid_cap');
      if (!text) { cap.classList.remove('on'); return; }
      cap.innerHTML = '';
      if (step) { const b = document.createElement('b'); b.textContent = step; cap.appendChild(b); }
      cap.appendChild(document.createTextNode(text));
      requestAnimationFrame(() => cap.classList.add('on'));
    },
    move(x, y) { install(); const c = document.getElementById('__vid_cur'); c.style.left = (x - 6) + 'px'; c.style.top = (y - 3) + 'px'; },
    ripple(x, y) { const r = document.createElement('div'); r.className = '__vid_ripple';
      r.style.left = x + 'px'; r.style.top = y + 'px'; document.documentElement.appendChild(r); setTimeout(() => r.remove(), 700); },
    hl(el) { el.classList.remove('__vid_hl'); void el.offsetWidth; el.classList.add('__vid_hl'); },
  };
  if (document.readyState !== 'loading') install(); else document.addEventListener('DOMContentLoaded', install);
})();
"""

CARD_HTML = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;font-family:"Malgun Gothic",sans-serif}
body{display:flex;flex-direction:column;justify-content:center;align-items:center;gap:33px;
  background:radial-gradient(120% 120% at 20% 10%,#7a6dff 0%,#5b4bff 45%,#2e2391 100%);color:#fff;text-align:center}
.brand{font-weight:800;font-size:45px;letter-spacing:.02em;background:#fee500;color:#3c1e1e;
  padding:12px 33px;border-radius:999px}
h1{margin:0;font-size:87px;line-height:1.25;font-weight:800;letter-spacing:-.02em}
p{margin:0;font-size:39px;opacity:.9}
.url{margin-top:9px;font-size:45px;font-weight:700;background:rgba(255,255,255,.14);
  padding:18px 45px;border-radius:21px}
.fade{animation:f .7s ease-out both}.d1{animation-delay:.2s}.d2{animation-delay:.45s}
@keyframes f{from{opacity:0;transform:translateY(14px)}}
@media (max-aspect-ratio:1/1){h1{font-size:96px;padding:0 60px;word-break:keep-all}
  p{font-size:42px;padding:0 60px;word-break:keep-all}}
</style></head><body data-vid-nozoom>__BODY__</body></html>"""

INTRO_BODY = """<div class="brand fade">노쇼가드</div>
<h1 class="fade d1">미용실 노쇼,<br>이제 자동으로 막으세요</h1>
<p class="fade d2">예약 확인 · 리마인더 · 대기자 자동 채움</p>"""

OUTRO_BODY = """<div class="brand fade">노쇼가드</div>
<h1 class="fade d1">라이브 데모로 먼저 체험하세요</h1>
<div class="url fade d2">noshow.n9n.co.kr</div>
<p class="fade d2">셋업부터 운영까지 대행 · 크몽 / 숨고 문의</p>"""


class Director:
    def __init__(self, page: Page):
        self.page = page
        self.t0 = time.monotonic()
        self.marks: list[dict] = []
        self.deadline = 0.0

    def now(self) -> float:
        return time.monotonic() - self.t0

    def scene(self, key: str) -> None:
        self.hold_until(self.deadline)
        spec = next(s for s in SCENES if s[0] == key)
        start = self.now()
        self.marks.append({"key": key, "start": round(start, 2)})
        self.deadline = start + spec[1]
        idx = [s[0] for s in SCENES if s[2]].index(key) + 1 if spec[2] else 0
        self.page.evaluate("([t,s]) => window.__vid.caption(t, s)",
                           [spec[2], f"{idx}" if idx else None])

    def finish(self) -> None:
        self.hold_until(self.deadline)
        self.marks.append({"key": "end", "start": round(self.now(), 2)})

    def hold_until(self, t: float) -> None:
        remaining = t - self.now()
        if remaining > 0:
            self.page.wait_for_timeout(remaining * 1000)

    def wait(self, ms: int) -> None:
        self.page.wait_for_timeout(ms)

    def scroll_to(self, y: int, ms: int = 650) -> None:
        self.page.evaluate("y => window.scrollTo({top: y, behavior: 'smooth'})", y)
        self.wait(ms)

    def scroll_to_el(self, selector: str, ms: int = 900) -> None:
        box = self.page.locator(selector).first.bounding_box()
        assert box is not None
        self.scroll_to(int(box["y"] + self.page.evaluate("window.scrollY")) - 30, ms)

    def reveal(self, selector: str, margin: int = 210) -> None:
        """요소가 화면 하단 자막 영역에 가리지 않도록 스크롤."""
        box = self.page.locator(selector).first.bounding_box()
        if box and (box["y"] < 90 or box["y"] + box["height"] > VIEW_H - margin):
            y = self.page.evaluate("window.scrollY") + box["y"] - 180
            self.scroll_to(max(0, int(y)))

    def click(self, locator, pause: int = 350) -> None:
        locator.scroll_into_view_if_needed()
        box = locator.bounding_box()
        assert box is not None
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        self.page.evaluate("([x,y]) => window.__vid.move(x, y)", [x, y])
        self.wait(600)
        self.page.evaluate("([x,y]) => window.__vid.ripple(x, y)", [x, y])
        locator.click()
        self.wait(pause)

    def type(self, locator, text: str) -> None:
        self.click(locator, pause=100)
        locator.press_sequentially(text, delay=45)

    def highlight(self, selector: str) -> None:
        self.page.locator(selector).first.evaluate("el => window.__vid.hl(el)")

    def highlight_all(self, selector: str, text: str) -> None:
        self.page.locator(selector, has_text=text).evaluate_all("els => els.forEach(window.__vid.hl)")


def card(page: Page, body: str) -> None:
    page.set_content(CARD_HTML.replace("__BODY__", body))
    page.evaluate("() => window.__vid && window.__vid.move(-200, -200)")


def run(base: str, out_dir: Path, suffix: str = "") -> tuple[Path, list[dict]]:
    raw_dir = out_dir / f"raw{suffix}"
    shutil.rmtree(raw_dir, ignore_errors=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": VIEW_W, "height": VIEW_H},
            record_video_dir=str(raw_dir),
            record_video_size={"width": VIEW_W, "height": VIEW_H},
            locale="ko-KR",
        )
        ctx.add_init_script(OVERLAY_JS.replace("__ZOOM__", str(ZOOM)))
        page = ctx.new_page()
        # 시드 예약의 리마인더는 관리자 첫 조회 때 지연 발송된다 — 미리 소진시켜
        # 녹화 중 확인 카톡이 메시지 로그 맨 위에 오도록 한다.
        page.request.get(f"{base}/api/admin/messages")
        d = Director(page)

        # ── 0. 인트로 ─────────────────────────────────────────────────────
        card(page, INTRO_BODY)
        d.scene("intro")
        d.hold_until(d.deadline)

        # ── 1. 손님 예약 (/demo) ─────────────────────────────────────────
        page.goto(f"{base}/demo")
        page.locator(".service-card").first.wait_for()
        d.scene("booking")
        d.click(page.locator(".service-card", has_text="커트"))
        # 모레 날짜로 예약 → 빨리감기 시 '전일 리마인더'가 내 예약에 발송된다
        d.click(page.locator(".date-chip").nth(2))
        page.locator(".slot-btn:not([disabled])").first.wait_for()
        d.reveal("#slot-grid")
        d.click(page.locator(".slot-btn:not([disabled])").first)
        d.reveal("#contact-step", margin=60)
        d.type(page.locator("#booking-name"), "한지수")
        d.type(page.locator("#booking-phone"), "010-2468-1357")
        d.click(page.locator("#btn-submit-reservation"), pause=200)
        page.locator("#screen-complete").wait_for()
        d.scroll_to(0, 300)

        # ── 2. 확인 카톡 (/admin 메시지 로그) ────────────────────────────
        d.hold_until(d.deadline - 0.2)
        page.goto(f"{base}/admin")
        page.locator(".chat-bubble").first.wait_for()
        d.scene("confirm")
        d.wait(500)
        d.scroll_to_el(".admin-panel--messages")
        d.highlight_all(".chat-bubble", "한지수")

        # ── 3. 하루 빨리감기 → 리마인더 ─────────────────────────────────
        d.scene("reminder")
        d.scroll_to(0, 700)
        d.click(page.locator("#btn-fast-forward"), pause=200)
        page.locator("#fast-forward-result").wait_for()
        d.highlight("#fast-forward-result")
        d.wait(1300)
        d.scroll_to_el(".admin-panel--messages")
        d.highlight(".chat-bubble")

        # ── 4. 취소 → 대기자 자동 채움 ───────────────────────────────────
        d.scene("cancel")
        row = page.locator("#reservations-tbody tr", has_text="최유진")
        if VIEW_W > VIEW_H:
            d.scroll_to(195, 700)
        else:
            d.scroll_to_el("#reservations-tbody tr:has-text('최유진')", 700)
        d.click(row.locator(".btn--cancel-row"), pause=600)
        page.locator("#reservations-tbody tr", has_text="이대기").wait_for()
        d.highlight(".waitlist-item--fulfilled")
        page.locator("#reservations-tbody tr", has_text="이대기").evaluate("el => window.__vid.hl(el)")
        d.wait(1700)
        d.scroll_to_el(".admin-panel--messages")
        d.highlight_all(".chat-bubble", "이대기")

        # ── 5. 아웃트로 ──────────────────────────────────────────────────
        d.hold_until(d.deadline)
        card(page, OUTRO_BODY)
        d.scene("outro")
        d.finish()

        assert page.video is not None
        video = Path(page.video.path())
        ctx.close()
        browser.close()

    (out_dir / f"timeline{suffix}.json").write_text(json.dumps(d.marks, ensure_ascii=False, indent=2), encoding="utf-8")
    return video, d.marks


def fmt_srt(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_texts(out_dir: Path, marks: list[dict], suffix: str = "") -> None:
    starts = {m["key"]: m["start"] for m in marks}
    keys = [m["key"] for m in marks]
    srt, md, txt = [], [], []
    md.append("# 노쇼가드 시연 영상 — 나레이션 원고\n")
    md.append("> 자동 생성 (scripts/video/record_noshow_demo.py). 각 줄은 표시된 구간 안에 끝나야 한다.")
    md.append("> 권장: 차분한 30대 여성/남성 톤, 0.95~1.0배속. 장면 시작 후 0.3초 뒤 발화.\n")
    md.append("| # | 구간 (s) | 길이 | 화면 | 나레이션 |")
    md.append("|---|---|---|---|---|")
    for i, (key, _, caption, narration) in enumerate(SCENES, 1):
        start = starts[key]
        end = starts[keys[keys.index(key) + 1]]
        srt += [str(i), f"{fmt_srt(start + 0.3)} --> {fmt_srt(end - 0.2)}", narration, ""]
        md.append(f"| {i} | {start:.1f} – {end:.1f} | {end - start:.1f}s | {caption or key} | {narration} |")
        txt.append(f"[{start:.2f}-{end:.2f}] {narration}")
    (out_dir / f"noshow-demo{suffix}.srt").write_text("\n".join(srt), encoding="utf-8")
    (out_dir / f"narration{suffix}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out_dir / f"narration{suffix}.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")


def encode(webm: Path, mp4: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(webm),
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", "30", "-movflags", "+faststart", str(mp4)],
        check=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="노쇼가드 시연 영상 자동 녹화")
    ap.add_argument("--base-url", default="http://localhost:18765")
    ap.add_argument("--out-dir", default="out/noshow-video")
    ap.add_argument("--vertical", action="store_true", help="9:16 세로판 (산출물 이름에 -vertical)")
    args = ap.parse_args()
    global VIEW_W, VIEW_H, ZOOM
    VIEW_W, VIEW_H, ZOOM = LAYOUTS["vertical" if args.vertical else "landscape"]
    suffix = "-vertical" if args.vertical else ""
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    webm, marks = run(args.base_url.rstrip("/"), out_dir, suffix)
    mp4 = out_dir / f"noshow-demo{suffix}.mp4"
    encode(webm, mp4)
    write_texts(out_dir, marks, suffix)
    print(json.dumps({"mp4": str(mp4), "timeline": marks}, ensure_ascii=False))


if __name__ == "__main__":
    main()
