/**
 * build-tokens.mjs — Design token + theme override → CSS custom properties
 *                     + tailwind-theme.gen.js (Tailwind theme.extend object).
 *
 * Usage:
 *   node scripts/build-tokens.mjs <theme-slug>
 *   node scripts/build-tokens.mjs aurora      # default if no arg
 *   node scripts/build-tokens.mjs studio
 *
 * Reads:
 *   design/tokens/semantic.json          (repo root — base token values, ref syntax)
 *   design/tokens/raw.json               (repo root — resolver for {dot.path} refs)
 *   presets/themes/<slug>/theme.yaml     (repo root — landing-only overrides, real hex values)
 *
 * Emits:
 *   src/styles/tokens.gen.css            (CSS custom properties :root block)
 *   src/styles/tailwind-theme.gen.js     (Tailwind theme.extend CJS module)
 *
 * DEC-1: unknown/absent theme slug -> falls back to "aurora" (flagship).
 * DEC-2: self-hosted fonts only (no CDN URLs emitted here).
 * Theme format: presets/themes/_theme-format.md
 * Theme has REAL hex/CSS values (no {ref} syntax) per format doc §1 invariant.
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import yaml from 'js-yaml'

const __dirname = dirname(fileURLToPath(import.meta.url))
// Adapter root: landing-astro/
const ADAPTER_ROOT = resolve(__dirname, '..')
// Repo root: 4 levels up from scripts/
const REPO_ROOT = resolve(__dirname, '..', '..', '..', '..')
const TOKENS_DIR = resolve(REPO_ROOT, 'design', 'tokens')
const THEMES_DIR = resolve(REPO_ROOT, 'presets', 'themes')
const OUT_DIR = resolve(ADAPTER_ROOT, 'src', 'styles')

// ── CLI arg ──────────────────────────────────────────────────────────────────

const FLAGSHIP = 'aurora'
const rawArg = process.argv[2]?.trim() ?? ''

function resolveThemeSlug(slug) {
  if (!slug || slug === 'default') {
    // DEC-1: "default" or absent -> aurora
    if (slug === 'default') {
      process.stderr.write(`[build-tokens] WARN: theme "default" resolved to flagship "${FLAGSHIP}"\n`)
    }
    return FLAGSHIP
  }
  const themePath = resolve(THEMES_DIR, slug, 'theme.yaml')
  if (!existsSync(themePath)) {
    process.stderr.write(`[build-tokens] WARN: unknown theme slug "${slug}" — falling back to "${FLAGSHIP}"\n`)
    return FLAGSHIP
  }
  return slug
}

const themeSlug = resolveThemeSlug(rawArg)
const themeYamlPath = resolve(THEMES_DIR, themeSlug, 'theme.yaml')

// ── Load sources ─────────────────────────────────────────────────────────────

function loadJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function loadYaml(path) {
  return yaml.load(readFileSync(path, 'utf8'))
}

const raw = loadJson(resolve(TOKENS_DIR, 'raw.json'))
const semantic = loadJson(resolve(TOKENS_DIR, 'semantic.json'))
const theme = loadYaml(themeYamlPath)

// ── Reference resolver (for semantic.json {dot.path} syntax) ─────────────────
// Theme values are real hex/CSS — no resolver needed for theme.yaml.

const REF_RE = /^\{([^}]+)\}$/
const REF_GLOBAL_RE = /\{([^}]+)\}/g

function getNested(obj, dottedPath) {
  return dottedPath.split('.').reduce((cur, part) => {
    if (cur == null || typeof cur !== 'object') return undefined
    return cur[part]
  }, obj)
}

function resolveRef(value, rawDoc) {
  const m = REF_RE.exec(value)
  if (m) {
    const resolved = getNested(rawDoc, m[1])
    if (resolved == null) throw new Error(`Unresolvable token reference: {${m[1]}}`)
    return String(resolved)
  }
  if (!value.includes('{')) return value
  return value.replace(REF_GLOBAL_RE, (_, path) => {
    const resolved = getNested(rawDoc, path)
    if (resolved == null) {
      process.stderr.write(`[build-tokens] WARN: unresolvable compound ref {${path}} — kept as-is\n`)
      return `{${path}}`
    }
    return String(resolved)
  })
}

// ── Strip keys ────────────────────────────────────────────────────────────────

const STRIP_KEYS = new Set(['_meta', '_density', 'note'])
const FONT_SHORTHAND_KEYS = new Set([
  'body', 'label', 'caption', 'heading-1', 'heading-2', 'heading-3', 'code',
])

// ── Flatten semantic.json → CSS pairs ─────────────────────────────────────────

function cssVarName(parts) {
  return '--' + parts.map(p => p.replace(/_/g, '-')).join('-')
}

function flattenSemantic(obj, path, rawDoc, output, inFont = false) {
  if (obj !== null && typeof obj === 'object' && !Array.isArray(obj)) {
    for (const [key, val] of Object.entries(obj)) {
      if (STRIP_KEYS.has(key) || key.startsWith('_')) continue
      const nextInFont = inFont || (path.length === 0 && key === 'font') ||
                         (path.length === 1 && path[0] === 'font')
      if (nextInFont && FONT_SHORTHAND_KEYS.has(key)) continue
      flattenSemantic(val, [...path, key], rawDoc, output, nextInFont)
    }
  } else if (typeof obj === 'string' || typeof obj === 'number') {
    let resolved = String(obj)
    try { resolved = resolveRef(resolved, rawDoc) } catch (e) {
      process.stderr.write(`[build-tokens] ${e.message} — emitting raw\n`)
    }
    output.push([cssVarName(path), resolved])
  }
}

// ── Apply theme overrides ─────────────────────────────────────────────────────
// Theme values are real hex/CSS values (format doc §1 — no resolver).

function flattenThemeSection(sectionObj, prefix, output) {
  for (const [key, val] of Object.entries(sectionObj)) {
    if (val == null || typeof val === 'object') continue
    const varName = `--${prefix}-${key}`
    output.push([varName, String(val)])
  }
}

// ── Tailwind theme.extend builder ─────────────────────────────────────────────
// Sections: color.* -> colors, font.family-* -> fontFamily, font.size-* -> fontSize,
//           space.section-y etc -> spacing, radius.* -> borderRadius, shadow.* -> boxShadow

function buildTailwindExtend(themeYaml) {
  const tw = {
    colors: {},
    fontFamily: {},
    fontSize: {},
    lineHeight: {},
    fontWeight: {},
    letterSpacing: {},
    spacing: {},
    borderRadius: {},
    boxShadow: {},
  }

  const color = themeYaml.color ?? {}
  for (const [k, v] of Object.entries(color)) {
    if (typeof v !== 'string') continue
    // Tailwind key: use CSS var reference so runtime picks up :root override
    tw.colors[k] = `var(--color-${k})`
  }

  const font = themeYaml.font ?? {}
  for (const [k, v] of Object.entries(font)) {
    if (typeof v !== 'string') continue
    if (k.startsWith('family-')) {
      const tailwindKey = k.replace('family-', '')
      tw.fontFamily[tailwindKey] = v.split(',').map(s => s.trim())
    } else if (k.startsWith('size-')) {
      const scale = k.replace('size-', '') // e.g. "5xl"
      tw.fontSize[scale] = v
    } else if (k.startsWith('line-')) {
      const scale = k.replace('line-', '')
      tw.lineHeight[scale] = v
    } else if (k === 'weight-display') {
      tw.fontWeight['display'] = v
    } else if (k === 'letter-spacing-display') {
      tw.letterSpacing['display'] = v
    } else if (k === 'letter-spacing-body') {
      tw.letterSpacing['body'] = v
    }
  }

  const space = themeYaml.space ?? {}
  for (const [k, v] of Object.entries(space)) {
    if (typeof v !== 'string') continue
    tw.spacing[k] = v
  }

  const radius = themeYaml.radius ?? {}
  for (const [k, v] of Object.entries(radius)) {
    if (typeof v !== 'string') continue
    tw.borderRadius[k] = v
  }

  const shadow = themeYaml.shadow ?? {}
  for (const [k, v] of Object.entries(shadow)) {
    if (typeof v !== 'string') continue
    tw.boxShadow[k] = v
  }

  // Prune empty sections
  for (const key of Object.keys(tw)) {
    if (Object.keys(tw[key]).length === 0) delete tw[key]
  }

  return tw
}

// ── Generate CSS ──────────────────────────────────────────────────────────────

const cssLines = [
  `/* Auto-generated by scripts/build-tokens.mjs — DO NOT EDIT */`,
  `/* Theme: ${themeSlug} | Source: design/tokens/semantic.json + presets/themes/${themeSlug}/theme.yaml */`,
  '',
]

// 1. Semantic base layer (resolved)
const semPairs = []
flattenSemantic(semantic, [], raw, semPairs)
cssLines.push('/* ── Semantic base layer ── */')
cssLines.push(':root {')
for (const [name, value] of semPairs) {
  cssLines.push(`  ${name}: ${value};`)
}
cssLines.push('}', '')

// 2. Theme color overrides -> CSS vars
const colorOverrides = []
for (const [k, v] of Object.entries(theme.color ?? {})) {
  if (typeof v === 'string') colorOverrides.push([`--color-${k}`, v])
}
// Theme font overrides
const fontOverrides = []
const font = theme.font ?? {}
for (const [k, v] of Object.entries(font)) {
  if (typeof v !== 'string') continue
  if (k.startsWith('family-')) fontOverrides.push([`--font-${k}`, v])
  else if (k.startsWith('size-')) fontOverrides.push([`--font-${k}`, v])
  else if (k.startsWith('line-')) fontOverrides.push([`--font-${k}`, v])
  else if (k === 'weight-display') fontOverrides.push([`--font-weight-display`, v])
  else if (k === 'letter-spacing-display') fontOverrides.push([`--font-letter-spacing-display`, v])
  else if (k === 'letter-spacing-body') fontOverrides.push([`--font-letter-spacing-body`, v])
}
// Theme spacing overrides
const spaceOverrides = []
for (const [k, v] of Object.entries(theme.space ?? {})) {
  if (typeof v === 'string') spaceOverrides.push([`--space-${k}`, v])
}
// Theme radius overrides
const radiusOverrides = []
for (const [k, v] of Object.entries(theme.radius ?? {})) {
  if (typeof v === 'string') radiusOverrides.push([`--radius-${k}`, v])
}
// Theme shadow overrides
const shadowOverrides = []
for (const [k, v] of Object.entries(theme.shadow ?? {})) {
  if (typeof v === 'string') shadowOverrides.push([`--shadow-${k}`, v])
}

const allThemeOverrides = [
  ...colorOverrides, ...fontOverrides, ...spaceOverrides,
  ...radiusOverrides, ...shadowOverrides,
]

if (allThemeOverrides.length > 0) {
  cssLines.push(`/* ── Theme override: ${themeSlug} ── */`)
  cssLines.push(':root {')
  for (const [name, value] of allThemeOverrides) {
    cssLines.push(`  ${name}: ${value};`)
  }
  cssLines.push('}', '')
}

// 3. @keyframes (motion presets — defined once globally)
cssLines.push('/* ── Motion @keyframes ── */')
cssLines.push(`@keyframes fade-simple {
  from { opacity: 0; }
  to   { opacity: 1; }
}`)
cssLines.push(`@keyframes fade-up {
  from { opacity: 0; transform: translateY(var(--translate-y-from, 24px)); }
  to   { opacity: 1; transform: translateY(0); }
}`)
cssLines.push(`@keyframes slide-in-left {
  from { opacity: 0; transform: translateX(var(--translate-x-from, -40px)); }
  to   { opacity: 1; transform: translateX(0); }
}`)
cssLines.push(`@keyframes scale-in {
  from { opacity: 0; transform: scale(var(--scale-from, 0.96)); }
  to   { opacity: 1; transform: scale(1); }
}`)

const css = cssLines.join('\n') + '\n'

// ── Generate Tailwind extend JS ───────────────────────────────────────────────

const twExtend = buildTailwindExtend(theme)
const twJs = [
  `// Auto-generated by scripts/build-tokens.mjs — DO NOT EDIT`,
  `// Theme: ${themeSlug}`,
  `// Imported by tailwind.config.js`,
  `'use strict'`,
  `module.exports = { theme: ${JSON.stringify(twExtend, null, 2)} }`,
  '',
].join('\n')

// ── Write outputs ─────────────────────────────────────────────────────────────

mkdirSync(OUT_DIR, { recursive: true })

const cssOut = resolve(OUT_DIR, 'tokens.gen.css')
const twOut = resolve(OUT_DIR, 'tailwind-theme.gen.js')

writeFileSync(cssOut, css, 'utf8')
writeFileSync(twOut, twJs, 'utf8')

console.log(`[build-tokens] theme: ${themeSlug}`)
console.log(`[build-tokens] CSS  → ${cssOut}`)
console.log(`[build-tokens] TW   → ${twOut}`)
console.log(`[build-tokens] semantic pairs: ${semPairs.length}, theme overrides: ${allThemeOverrides.length}`)
