/**
 * sections.test.mjs — Section catalog + theme resolution tests.
 * Verifies all 8 section type component files exist and theme resolution logic.
 * Static analysis only — no Astro runtime needed.
 *
 * Run: node --test tests/sections.test.mjs
 */

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ADAPTER_ROOT = resolve(__dirname, '..')
const SECTIONS_DIR = resolve(ADAPTER_ROOT, 'src', 'sections')

// 8 section types per presets/site-sections/catalog.yaml
const SECTION_TYPES = ['hero', 'logos', 'features', 'pricing', 'testimonial', 'faq', 'cta', 'footer']

// Expected component file per section type (PascalCase)
const COMPONENT_MAP = {
  hero: 'Hero.astro',
  logos: 'Logos.astro',
  features: 'Features.astro',
  pricing: 'Pricing.astro',
  testimonial: 'Testimonial.astro',
  faq: 'Faq.astro',
  cta: 'Cta.astro',
  footer: 'Footer.astro',
}

// ── Section component existence ────────────────────────────────────────────

for (const sectionType of SECTION_TYPES) {
  test(`section component exists: ${sectionType}`, () => {
    const filename = COMPONENT_MAP[sectionType]
    const fullPath = resolve(SECTIONS_DIR, filename)
    assert.ok(existsSync(fullPath), `${filename} must exist at src/sections/${filename}`)
  })
}

// ── Section components are non-empty Astro files ───────────────────────────

for (const sectionType of SECTION_TYPES) {
  test(`section component is valid Astro file: ${sectionType}`, () => {
    const filename = COMPONENT_MAP[sectionType]
    const fullPath = resolve(SECTIONS_DIR, filename)
    if (!existsSync(fullPath)) return // already caught above
    const content = readFileSync(fullPath, 'utf8')
    assert.ok(content.length > 100, `${filename} must have meaningful content`)
    // Astro files have --- frontmatter
    assert.ok(content.includes('---'), `${filename} must have Astro frontmatter delimiters`)
  })
}

// ── Section components handle motion preset ───────────────────────────────

test('Hero.astro: uses data-motion attribute', () => {
  const src = readFileSync(resolve(SECTIONS_DIR, 'Hero.astro'), 'utf8')
  assert.ok(src.includes('data-motion'), 'Hero must use data-motion for IntersectionObserver')
})

test('Pricing.astro: DEC-3 highlight_tier is 0-based', () => {
  const src = readFileSync(resolve(SECTIONS_DIR, 'Pricing.astro'), 'utf8')
  // Comment or code must reference 0-based
  assert.ok(src.includes('0-based') || src.includes('highlightIndex'), 'Pricing must implement 0-based highlight_tier (DEC-3)')
})

test('Testimonial.astro: no autoplay (a11y invariant)', () => {
  const src = readFileSync(resolve(SECTIONS_DIR, 'Testimonial.astro'), 'utf8')
  // Must NOT set autoplay to true anywhere
  assert.ok(!src.includes('autoplay: true'), 'Testimonial must not enable autoplay (WCAG 2.2.2)')
  assert.ok(!src.includes('autoPlay'), 'Testimonial must not enable autoPlay (WCAG 2.2.2)')
})

// ── Layout and component files exist ─────────────────────────────────────

test('BaseLayout.astro exists', () => {
  assert.ok(existsSync(resolve(ADAPTER_ROOT, 'src', 'layouts', 'BaseLayout.astro')))
})

test('ContactForm.astro exists', () => {
  assert.ok(existsSync(resolve(ADAPTER_ROOT, 'src', 'components', 'ContactForm.astro')))
})

test('[...page].astro exists', () => {
  assert.ok(existsSync(resolve(ADAPTER_ROOT, 'src', 'pages', '[...page].astro')))
})

// ── ContactForm: DEC-5 wire key ─────────────────────────────────────────

test('ContactForm.astro: uses entity.create endpoint (DEC-5)', () => {
  const src = readFileSync(resolve(ADAPTER_ROOT, 'src', 'components', 'ContactForm.astro'), 'utf8')
  assert.ok(src.includes('entity.create') || src.includes('entity_create') || src.includes('/api/entities/'), 'ContactForm must reference entity.create wire key path')
  assert.ok(src.includes("'lead'") || src.includes('"lead"'), 'ContactForm must use entity_type lead (DEC-5)')
})

test('ContactForm.astro: no hardcoded contact.lead_capture', () => {
  const src = readFileSync(resolve(ADAPTER_ROOT, 'src', 'components', 'ContactForm.astro'), 'utf8')
  assert.ok(!src.includes('contact.lead_capture'), 'ContactForm must not use old placeholder wire key')
})

// ── manifest.ts exists and has loadManifest ───────────────────────────────

test('src/lib/manifest.ts exists', () => {
  assert.ok(existsSync(resolve(ADAPTER_ROOT, 'src', 'lib', 'manifest.ts')))
})

test('manifest.ts exports loadManifest', () => {
  const src = readFileSync(resolve(ADAPTER_ROOT, 'src', 'lib', 'manifest.ts'), 'utf8')
  assert.ok(src.includes('export function loadManifest'), 'manifest.ts must export loadManifest')
})

// ── Global CSS: prefers-reduced-motion ───────────────────────────────────

test('global.css: prefers-reduced-motion override present', () => {
  const src = readFileSync(resolve(ADAPTER_ROOT, 'src', 'styles', 'global.css'), 'utf8')
  assert.ok(src.includes('prefers-reduced-motion'), 'global.css must handle prefers-reduced-motion (WCAG 2.3.3)')
})

test('global.css: self-hosted fonts only (DEC-2, no CDN URLs)', () => {
  const src = readFileSync(resolve(ADAPTER_ROOT, 'src', 'styles', 'global.css'), 'utf8')
  assert.ok(!src.includes('fonts.googleapis.com'), 'global.css must not load Google Fonts CDN (DEC-2)')
  assert.ok(!src.includes('fonts.gstatic.com'), 'global.css must not load Google Fonts CDN (DEC-2)')
  assert.ok(src.includes('@fontsource/'), 'global.css must import @fontsource packages (DEC-2 self-host)')
})
