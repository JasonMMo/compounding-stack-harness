---
name: htmx-demo-verify
description: Verify a CSS/layout fix on a LIVE-deployed vanilla-htmx demo with headless Chrome BEFORE spending a redeploy cycle. Measures real DOM geometry (getBoundingClientRect/getComputedStyle) and injects a candidate CSS rule to prove it moves the layout. Use when a founder reports "design fix not reflected", header/footer whitespace, button-height mismatch, or any visual regression on *.n9n.co.kr demos. No API, no Chromium download.
---

# htmx-demo-verify — prove a CSS fix on the live demo before redeploy

A CSS change on these demos can look "not reflected" for **two unrelated reasons**.
Measure first; never guess. (Fixed-px padding can't cause viewport-proportional
whitespace — if the gap *scales with window width*, it's a container `max-width`.)

| symptom | likely cause | check |
|---|---|---|
| HTML change shows, **CSS change doesn't** | PWA service worker stale cache `[[pwa-sw-stale-cache]]` | direct-fetch `/static/css/app.css` = new, but render = old → SW stale. Fix is network-first + `CACHE` bump; user does F12 → Application → Service Workers → Unregister → reload |
| header/footer has **left/right whitespace that scales with window width** | Pico classless reading-container `max-width` on body-direct `<header>`/`<footer>` `[[pico-container-maxwidth-shell]]` | measure: trapped element shows `x>0, w==1450/1200`; full-bleed shows `x≈0, w≈viewport` |
| nothing in browser updates at all | push missing `[[push-before-deploy]]` | `git log origin/master` has the commit? |

## Workflow

1. **Measure the live page as-deployed** — confirm the defect is real and quantify it.
2. **Inject the candidate CSS** (`--css` / `--css-file`) — the script reprints geometry AFTER injection, in the same run, with no deploy. If geometry moves to the target (`x→0, w→viewport` for full-bleed), the rule is proven.
3. **Only then** edit `frontend/adapters/vanilla-htmx/static/css/app.css` and commit. The fix is common-adapter → propagates to all ~10 live demos.
4. Tell the founder to redeploy + (if SW was stale) unregister-and-reload once.

## Run it (black box — do not read the script source unless customizing)

```bash
# one-time setup if puppeteer-core is missing
cd "$TEMP" && npm i puppeteer-core@23

# measure only (login demo/demo, default selectors .app-header,.app-footer,.app-logo @ vw=1822)
node .claude/skills/htmx-demo-verify/scripts/verify_live_css.mjs \
  --url https://lawfirm-demo.n9n.co.kr/board/case-deadline --login demo:demo

# prove a candidate fix without deploying
node .claude/skills/htmx-demo-verify/scripts/verify_live_css.mjs \
  --url https://lawfirm-demo.n9n.co.kr/board/case-deadline --login demo:demo \
  --css ".app-header,.app-footer{max-width:none;width:100%;margin-inline:0}"
```

`--help` semantics are in the script header. Key flags: `--url` (req), `--login user:pass`,
`--sel "a,b"`, `--css` / `--css-file`, `--vw/--vh`, `--shot PATH`, `--chrome`, `--node-path`.

## Specificity note

A **class** selector `.app-header` (0,1,0) beats Pico's `:where(body>header)` (0,0,0),
so the override wins **without `!important`**. A rule that only sets `padding` won't fix a
`max-width` problem — it must *declare the conflicting property* (`max-width:none`).

## Env (Windows, this machine)

- Chrome: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- puppeteer-core@23 under `$TEMP/node_modules` (no Chromium download)
- demo creds: `demo` / `demo` (fastapi `_DEMO_USERS`, `user_id=user-demo`)
- screenshots > 100KB: downscale via PIL (`C:\Python314`) into `out/` (gitignored) before Read — Read guards block large images.

Related: `webapp-testing` skill is for **local** Playwright dev servers; this skill is for
**already-deployed live** demos + pre-deploy CSS injection proof.
