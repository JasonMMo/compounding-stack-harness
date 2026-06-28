/**
 * build-tokens.mjs — Design token JSON → CSS custom properties (L3 build step).
 *
 * Reads:  design/tokens/raw.json
 *         design/tokens/semantic.json
 *         design/tokens/persona/*.json
 *
 * Emits:  src/tokens/tokens.gen.css
 *
 * Implements the same generation rules as vanilla-htmx/token_css_generator.py
 * (the reference generator), adapted to Node.js. The output CSS is imported
 * by src/main.tsx so it is bundled into the SPA.
 *
 * Rules (per design/tokens/README.md):
 *   1. raw.json       → :root { --raw-<path>: value }
 *   2. semantic.json  → :root { --<path>: resolved-value } (resolves {dot.path} refs)
 *   3. persona/*.json → [data-persona="<name>"] { ... } (override keys only)
 *   4. Strip: _meta, _density, note keys (and any key starting with _)
 *   5. Font shorthand keys (body, label, caption, heading-*, code) skipped
 *   6. Compound values: emitted as-is, no extra quoting
 */

import { readFileSync, writeFileSync, readdirSync, mkdirSync } from 'fs'
import { resolve, dirname, basename } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = resolve(__dirname, '..', '..', '..', '..')
const TOKENS_DIR = resolve(REPO_ROOT, 'design', 'tokens')
const OUT_FILE = resolve(__dirname, '..', 'src', 'tokens', 'tokens.gen.css')

// ── Constants ──────────────────────────────────────────────────────────────
const STRIP_KEYS = new Set(['_meta', '_density', 'note'])
const FONT_SHORTHAND_KEYS = new Set([
  'body', 'label', 'caption', 'heading-1', 'heading-2', 'heading-3', 'code',
])
const REF_RE = /^\{([^}]+)\}$/

// ── Helpers ────────────────────────────────────────────────────────────────

function loadJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function getNested(obj, dottedPath) {
  return dottedPath.split('.').reduce((cur, part) => {
    if (cur == null || typeof cur !== 'object') return undefined
    return cur[part]
  }, obj)
}

// Matches any {dotted.path} segment — used for compound values like "{a} {b}"
const REF_GLOBAL_RE = /\{([^}]+)\}/g

function resolveRef(value, raw) {
  // Fast path: single ref with no other content
  const m = REF_RE.exec(value)
  if (m) {
    const resolved = getNested(raw, m[1])
    if (resolved == null) throw new Error(`Unresolvable token reference: {${m[1]}}`)
    return String(resolved)
  }
  // Compound value: replace each {ref} inline (e.g. "{a} {b}" → "200ms ease-in-out")
  if (!value.includes('{')) return value
  return value.replace(REF_GLOBAL_RE, (_, path) => {
    const resolved = getNested(raw, path)
    if (resolved == null) {
      console.warn(`[build-tokens] Unresolvable compound ref: {${path}} — keeping as-is`)
      return `{${path}}`
    }
    return String(resolved)
  })
}

function rawCssName(parts) {
  return '--raw-' + parts.map(p => p.replace(/_/g, '-')).join('-')
}

function semanticCssName(parts) {
  return '--' + parts.map(p => p.replace(/_/g, '-')).join('-')
}

// ── Flattenners ───────────────────────────────────────────────────────────

function flattenRaw(obj, path, output) {
  if (obj !== null && typeof obj === 'object' && !Array.isArray(obj)) {
    for (const [key, val] of Object.entries(obj)) {
      if (STRIP_KEYS.has(key) || key.startsWith('_')) continue
      flattenRaw(val, [...path, key], output)
    }
  } else if (typeof obj === 'string' || typeof obj === 'number') {
    output.push([rawCssName(path), String(obj)])
  }
  // arrays skipped
}

function flattenSemantic(obj, path, raw, output, inFont = false) {
  if (obj !== null && typeof obj === 'object' && !Array.isArray(obj)) {
    for (const [key, val] of Object.entries(obj)) {
      if (STRIP_KEYS.has(key) || key.startsWith('_')) continue
      const nextInFont = inFont || (path.length === 0 && key === 'font') || (path.length === 1 && path[0] === 'font')
      if (nextInFont && FONT_SHORTHAND_KEYS.has(key)) continue
      flattenSemantic(val, [...path, key], raw, output, nextInFont)
    }
  } else if (typeof obj === 'string' || typeof obj === 'number') {
    let resolved = String(obj)
    try {
      resolved = resolveRef(resolved, raw)
    } catch (e) {
      console.warn(`[build-tokens] ${e.message} — emitting raw value`)
    }
    output.push([semanticCssName(path), resolved])
  }
}

function flattenPersona(obj, path, raw, output, inFont = false) {
  if (obj !== null && typeof obj === 'object' && !Array.isArray(obj)) {
    for (const [key, val] of Object.entries(obj)) {
      if (STRIP_KEYS.has(key) || key.startsWith('_')) continue
      const nextInFont = inFont || (path.length === 0 && key === 'font') || (path.length === 1 && path[0] === 'font')
      if (nextInFont && FONT_SHORTHAND_KEYS.has(key)) continue
      flattenPersona(val, [...path, key], raw, output, nextInFont)
    }
  } else if (typeof obj === 'string' || typeof obj === 'number') {
    let resolved = String(obj)
    try {
      resolved = resolveRef(resolved, raw)
    } catch (e) {
      console.warn(`[build-tokens] persona ref: ${e.message} — emitting raw value`)
    }
    output.push([semanticCssName(path), resolved])
  }
}

function varsBlock(pairs, indent = '  ') {
  return pairs.map(([name, value]) => `${indent}${name}: ${value};`).join('\n')
}

// ── Generate ──────────────────────────────────────────────────────────────

const raw = loadJson(resolve(TOKENS_DIR, 'raw.json'))
const semantic = loadJson(resolve(TOKENS_DIR, 'semantic.json'))

const sections = [
  '/* Auto-generated by scripts/build-tokens.mjs — DO NOT EDIT MANUALLY */',
  '/* Source: design/tokens/raw.json + semantic.json + persona/*.json */',
  '',
]

// 1. Raw layer
const rawPairs = []
flattenRaw(raw, [], rawPairs)
sections.push('/* ── Raw token layer ── */')
sections.push(':root {')
sections.push(varsBlock(rawPairs))
sections.push('}', '')

// 2. Semantic layer
const semPairs = []
flattenSemantic(semantic, [], raw, semPairs)
sections.push('/* ── Semantic token layer ── */')
sections.push(':root {')
sections.push(varsBlock(semPairs))
sections.push('}', '')

// 3. Persona overrides
const personaDir = resolve(TOKENS_DIR, 'persona')
let personaFiles
try {
  personaFiles = readdirSync(personaDir).filter(f => f.endsWith('.json')).sort()
} catch {
  personaFiles = []
}

for (const file of personaFiles) {
  const personaName = basename(file, '.json')
  const personaData = loadJson(resolve(personaDir, file))
  const personaPairs = []
  flattenPersona(personaData, [], raw, personaPairs)
  if (personaPairs.length === 0) continue
  sections.push(`/* ── Persona: ${personaName} ── */`)
  sections.push(`[data-persona="${personaName}"] {`)
  sections.push(varsBlock(personaPairs))
  sections.push('}', '')
}

// 4. prefers-reduced-motion: override all --motion-duration-* to near-zero
// Derived from semPairs so new tokens are covered automatically (no hardcoding).
const durationNames = semPairs
  .map(([name]) => name)
  .filter(name => name.startsWith('--motion-duration-'))
  .sort()
sections.push('/* ── a11y: prefers-reduced-motion override (WCAG 2.3.3 / KWCAG) ── */')
sections.push('@media (prefers-reduced-motion: reduce) {')
sections.push('  :root {')
for (const name of durationNames) {
  sections.push(`    ${name}: 0.01ms;`)
}
sections.push('  }')
sections.push('}', '')

const css = sections.join('\n') + '\n'
mkdirSync(dirname(OUT_FILE), { recursive: true })
writeFileSync(OUT_FILE, css, 'utf8')

console.log(`[build-tokens] Wrote ${OUT_FILE} (${css.length} bytes, ${css.split('\n').length} lines)`)
