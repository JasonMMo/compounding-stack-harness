#!/usr/bin/env node
/* verify_live_css.mjs — headless Chrome verification of a LIVE-deployed
 * vanilla-htmx demo. Measures real layout geometry and (optionally) proves a
 * candidate CSS fix by injecting it BEFORE the founder spends a redeploy cycle.
 *
 * WHY this exists (Growth-129): a CSS deploy on these demos has TWO ways to look
 * "not reflected" — (1) the PWA service worker serving stale CSS [pwa-sw-stale-cache],
 * (2) the CSS itself rendering wrong. Guessing wastes redeploy cycles. This harness
 * measures the live DOM and lets you inject a candidate rule to PROVE the fix moves
 * the geometry, with zero deploy. Pico container max-width on body-direct <header>/
 * <footer> was the real header-whitespace cause [pico-container-maxwidth-shell].
 *
 * Uses puppeteer-core driving the locally-installed Chrome (no Chromium download,
 * no API cost — honors CLAUDE.md "api를 사용하지 않는다").
 *
 * USAGE:
 *   node verify_live_css.mjs --url <URL> [opts]
 *
 * OPTIONS:
 *   --url URL            page to measure (required), e.g. https://lawfirm-demo.n9n.co.kr/board/case-deadline
 *   --login user:pass    submit the /login form first (sets session cookie; demo demos use demo:demo)
 *   --sel "a,b,c"        comma CSS selectors to measure (default ".app-header,.app-footer,.app-logo")
 *   --css "<rules>"      candidate CSS to inject; prints BEFORE then AFTER geometry
 *   --css-file PATH      read candidate CSS from a file instead of --css
 *   --vw N --vh N        viewport (default 1822x980 — matches founder's report width)
 *   --shot PATH          save a screenshot (downscale large PNGs to out/ if you must Read them)
 *   --chrome PATH        Chrome binary (default: C:\Program Files\Google\Chrome\Application\chrome.exe)
 *   --node-path DIR      node_modules dir holding puppeteer-core (default: $TEMP/node_modules)
 *
 * SETUP (one-time, if puppeteer-core missing):
 *   cd "$TEMP" && npm i puppeteer-core@23
 *
 * Geometry printed per selector: {x, y, w, h, maxWidth, marginLeft}. A full-bleed
 * shell element should have x≈0 and w≈viewport width; a Pico-trapped one shows
 * x>0 and w==1450/1200 (centered reading container).
 */
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';

function arg(name, def) {
  const i = process.argv.indexOf('--' + name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : def;
}
const URL_ = arg('url');
if (!URL_) { console.error('ERROR: --url required'); process.exit(2); }
const LOGIN = arg('login');
const SEL = arg('sel', '.app-header,.app-footer,.app-logo').split(',').map(s => s.trim()).filter(Boolean);
let CSS = arg('css');
const CSS_FILE = arg('css-file');
if (CSS_FILE) CSS = readFileSync(CSS_FILE, 'utf8');
const VW = parseInt(arg('vw', '1822'), 10);
const VH = parseInt(arg('vh', '980'), 10);
const SHOT = arg('shot');
const CHROME = arg('chrome', 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe');
const NODE_PATH = arg('node-path', (process.env.TEMP || process.env.TMP || '/tmp') + '/node_modules');

const require = createRequire(NODE_PATH + '/');
let puppeteer;
try { puppeteer = require('puppeteer-core'); }
catch { console.error(`ERROR: puppeteer-core not found under ${NODE_PATH}.\n  Run: cd "$TEMP" && npm i puppeteer-core@23`); process.exit(3); }

const measure = (sels) => {
  const out = {};
  for (const s of sels) {
    const el = document.querySelector(s);
    if (!el) { out[s] = null; continue; }
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    out[s] = { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height),
               maxWidth: cs.maxWidth, marginLeft: cs.marginLeft };
  }
  return out;
};

const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: VW, height: VH });

  if (LOGIN) {
    const [u, p] = LOGIN.split(':');
    const origin = new global.URL(URL_).origin;
    // Log in via the Flask /login FORM — this sets the session cookie that gates
    // page navigation. Do NOT POST /api/auth/login: that is the backend JSON
    // endpoint, returns a bearer token, and sets NO frontend session cookie, so
    // every subsequent goto silently redirects to /login (you'd measure the login
    // page, not the target). Verified live on lawfirm-demo 2026-06-28.
    await page.goto(origin + '/login', { waitUntil: 'networkidle2' });
    await page.type('input[name="username"]', u);
    await page.type('input[name="password"]', p);
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle2' }),
      page.click('button[type="submit"]'),
    ]);
    const landed = page.url();
    console.log(`login → ${landed}${landed.endsWith('/login') ? '  ⚠️ STILL ON /login (auth failed)' : '  ✅'}`);
  }

  await page.goto(URL_, { waitUntil: 'networkidle2' });
  await page.evaluate(() => new Promise(r => setTimeout(r, 400)));

  const before = await page.evaluate(measure, SEL);
  console.log('=== BEFORE (live as-deployed) ===\n' + JSON.stringify(before, null, 2));

  if (CSS) {
    await page.addStyleTag({ content: CSS });
    await page.evaluate(() => new Promise(r => setTimeout(r, 200)));
    const after = await page.evaluate(measure, SEL);
    console.log('\n=== AFTER (candidate CSS injected, NOT deployed) ===\n' + JSON.stringify(after, null, 2));
    // quick verdict for the common full-bleed-shell check
    for (const s of SEL) {
      const b = before[s], a = after[s];
      if (b && a) console.log(`  ${s}: x ${b.x}->${a.x}  w ${b.w}->${a.w}  ${a.x === 0 && a.w >= VW - 4 ? 'FULL-WIDTH ✅' : ''}`);
    }
  }

  if (SHOT) { await page.screenshot({ path: SHOT, fullPage: false }); console.log(`\nscreenshot: ${SHOT}`); }
} finally { await browser.close(); }
