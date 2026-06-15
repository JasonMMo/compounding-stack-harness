/**
 * build-tokens-auto.mjs — Theme-aware wrapper for build-tokens.mjs.
 *
 * Reads the site-manifest pointed to by PUBLIC_SITE_MANIFEST, extracts the
 * theme slug, then delegates to build-tokens.mjs <slug>.
 *
 * Fallback: if env is absent or manifest is unreadable, falls back to "aurora"
 * so gtm-landing (and any build without PUBLIC_SITE_MANIFEST) keeps working.
 *
 * Usage (from package.json "build" script):
 *   node scripts/build-tokens-auto.mjs
 *
 * Docker: PUBLIC_SITE_MANIFEST is set by the Dockerfile ENV instruction before
 * npm run build executes — no Dockerfile change needed.
 *
 * Local dev: set PUBLIC_SITE_MANIFEST env before npm run build, e.g.:
 *   PUBLIC_SITE_MANIFEST=out/hopwell/site-manifest.json npm run build
 */

import { readFileSync, existsSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import { spawnSync } from 'child_process'

const __dirname = dirname(fileURLToPath(import.meta.url))
const BUILD_TOKENS_SCRIPT = resolve(__dirname, 'build-tokens.mjs')

const FALLBACK = 'aurora'

function resolveThemeFromManifest() {
  const manifestEnv = process.env.PUBLIC_SITE_MANIFEST
  if (!manifestEnv) {
    process.stderr.write(
      `[build-tokens-auto] PUBLIC_SITE_MANIFEST not set — falling back to "${FALLBACK}"\n`
    )
    return FALLBACK
  }

  // Manifest path may be absolute or relative to cwd (adapter root).
  const manifestPath = resolve(process.cwd(), manifestEnv)
  if (!existsSync(manifestPath)) {
    process.stderr.write(
      `[build-tokens-auto] manifest not found at "${manifestPath}" — falling back to "${FALLBACK}"\n`
    )
    return FALLBACK
  }

  let manifest
  try {
    manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
  } catch (e) {
    process.stderr.write(
      `[build-tokens-auto] failed to parse manifest: ${e.message} — falling back to "${FALLBACK}"\n`
    )
    return FALLBACK
  }

  const theme = manifest.theme
  if (!theme || typeof theme !== 'string') {
    process.stderr.write(
      `[build-tokens-auto] manifest has no theme field — falling back to "${FALLBACK}"\n`
    )
    return FALLBACK
  }

  process.stdout.write(`[build-tokens-auto] resolved theme "${theme}" from manifest\n`)
  return theme
}

const themeSlug = resolveThemeFromManifest()

// Delegate to build-tokens.mjs <themeSlug> using the same node binary.
const result = spawnSync(process.execPath, [BUILD_TOKENS_SCRIPT, themeSlug], {
  stdio: 'inherit',
  env: process.env,
})

if (result.error) {
  process.stderr.write(`[build-tokens-auto] spawn error: ${result.error.message}\n`)
  process.exit(1)
}

if (result.status !== 0) {
  process.exit(result.status ?? 1)
}
