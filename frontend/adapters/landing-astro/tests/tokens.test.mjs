/**
 * tokens.test.mjs — Build-token smoke tests.
 * Verifies build-tokens.mjs runs without errors for aurora and studio.
 * L3-adjacent: validates the token build step that precedes astro build.
 *
 * Run: node --test tests/tokens.test.mjs
 * (from landing-astro/ with node_modules present)
 */

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ADAPTER_ROOT = resolve(__dirname, '..')
const SCRIPT = resolve(ADAPTER_ROOT, 'scripts', 'build-tokens.mjs')
const CSS_OUT = resolve(ADAPTER_ROOT, 'src', 'styles', 'tokens.gen.css')
const TW_OUT = resolve(ADAPTER_ROOT, 'src', 'styles', 'tailwind-theme.gen.js')

function runBuildTokens(themeArg) {
  return execFileSync(process.execPath, [SCRIPT, themeArg], {
    cwd: ADAPTER_ROOT,
    encoding: 'utf8',
    env: { ...process.env },
  })
}

test('build-tokens aurora: exits 0 and emits CSS', () => {
  const out = runBuildTokens('aurora')
  assert.ok(out.includes('[build-tokens] theme: aurora'), 'stdout must mention aurora')
  assert.ok(existsSync(CSS_OUT), 'tokens.gen.css must exist after aurora build')
  const css = readFileSync(CSS_OUT, 'utf8')
  assert.ok(css.includes(':root {'), 'CSS must contain :root block')
  assert.ok(css.includes('--color-'), 'CSS must contain color custom properties')
  assert.ok(css.includes('@keyframes fade-simple'), 'CSS must contain fade-simple keyframe')
  assert.ok(css.includes('@keyframes fade-up'), 'CSS must contain fade-up keyframe')
})

test('build-tokens aurora: emits tailwind-theme.gen.js', () => {
  runBuildTokens('aurora')
  assert.ok(existsSync(TW_OUT), 'tailwind-theme.gen.js must exist after aurora build')
  const tw = readFileSync(TW_OUT, 'utf8')
  assert.ok(tw.includes('module.exports'), 'must be CJS module')
  assert.ok(tw.includes('"colors"') || tw.includes('"fontFamily"'), 'must contain Tailwind extend keys')
})

test('build-tokens studio: exits 0 and emits CSS', () => {
  const out = runBuildTokens('studio')
  assert.ok(out.includes('[build-tokens] theme: studio'), 'stdout must mention studio')
  assert.ok(existsSync(CSS_OUT), 'tokens.gen.css must exist after studio build')
  const css = readFileSync(CSS_OUT, 'utf8')
  // Studio uses DM Serif Display — verify font family override present
  assert.ok(css.includes('DM Serif Display') || css.includes('--font-family-display'), 'studio font override must be present')
})

test('build-tokens unknown slug: falls back to aurora (DEC-1)', () => {
  runBuildTokens('__nonexistent_theme__')
  // Script should warn to stderr and fall back
  assert.ok(existsSync(CSS_OUT), 'tokens.gen.css must exist even with unknown theme (fallback)')
  // The CSS output should be aurora content (not empty)
  const css = readFileSync(CSS_OUT, 'utf8')
  assert.ok(css.length > 200, 'CSS output must have real content after fallback')
})

test('build-tokens "default" slug: falls back to aurora (DEC-1)', () => {
  runBuildTokens('default')
  assert.ok(existsSync(CSS_OUT), 'tokens.gen.css must exist after "default" -> aurora fallback')
  const css = readFileSync(CSS_OUT, 'utf8')
  assert.ok(css.includes(':root {'), 'CSS must be valid after default fallback')
})

test('build-tokens CSS: contains motion keyframes', () => {
  runBuildTokens('aurora')
  const css = readFileSync(CSS_OUT, 'utf8')
  assert.ok(css.includes('@keyframes scale-in'), 'scale-in keyframe required')
  assert.ok(css.includes('@keyframes slide-in-left'), 'slide-in-left keyframe required')
})

test('build-tokens CSS: motion palette primitives present (brick-2 guard)', () => {
  // Growth-87 brick-2: design motion palette must be emitted so IO-reveal var()
  // references in global.css resolve. Assert all 3 series exist.
  runBuildTokens('aurora')
  const css = readFileSync(CSS_OUT, 'utf8')
  // duration series
  assert.ok(css.includes('--motion-duration-fast'), 'motion-duration-fast must be emitted')
  assert.ok(css.includes('--motion-duration-base'), 'motion-duration-base must be emitted')
  assert.ok(css.includes('--motion-duration-slow'), 'motion-duration-slow must be emitted')
  assert.ok(css.includes('--motion-duration-intro'), 'motion-duration-intro must be emitted')
  // ease series
  assert.ok(css.includes('--motion-ease-standard'), 'motion-ease-standard must be emitted')
  assert.ok(css.includes('--motion-ease-emphasized'), 'motion-ease-emphasized must be emitted')
  assert.ok(css.includes('--motion-ease-exit'), 'motion-ease-exit must be emitted')
  assert.ok(css.includes('--motion-ease-spring'), 'motion-ease-spring must be emitted')
  // stagger series
  assert.ok(css.includes('--motion-stagger-tight'), 'motion-stagger-tight must be emitted')
  assert.ok(css.includes('--motion-stagger-base'), 'motion-stagger-base must be emitted')
  assert.ok(css.includes('--motion-stagger-loose'), 'motion-stagger-loose must be emitted')
})

test('build-tokens CSS: no legacy motion-transition-* tokens (palette supersedes)', () => {
  // Growth-87 brick-2: old --motion-transition-* slots removed from semantic.json.
  // Verify they are no longer emitted (consumers in src/ were 0 — already validated).
  runBuildTokens('aurora')
  const css = readFileSync(CSS_OUT, 'utf8')
  assert.ok(!css.includes('--motion-transition-control'), '--motion-transition-control must not be emitted')
  assert.ok(!css.includes('--motion-transition-enter'),  '--motion-transition-enter must not be emitted')
  assert.ok(!css.includes('--motion-transition-exit'),   '--motion-transition-exit must not be emitted')
  assert.ok(!css.includes('--motion-transition-fast'),   '--motion-transition-fast must not be emitted')
})
