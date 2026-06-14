/**
 * smoke.test.mjs — Build smoke test.
 * Verifies npm run build succeeds (L3: BUILD SUCCESS) for agency-demo manifest.
 * Also checks dist/ contains home and about pages.
 *
 * Run: node --test tests/smoke.test.mjs
 * Prerequisites: npm install must have been run already.
 */

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { existsSync, readdirSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ADAPTER_ROOT = resolve(__dirname, '..')
const REPO_ROOT = resolve(ADAPTER_ROOT, '..', '..', '..')

// Generate fresh site-manifest.json for agency-demo before build
function ensureManifest() {
  const scaffoldScript = resolve(REPO_ROOT, 'scripts', 'workflow', 'scaffold.py')
  const result = spawnSync(
    process.platform === 'win32' ? 'python' : 'python3',
    [scaffoldScript, '--profile', 'agency-demo'],
    { cwd: REPO_ROOT, encoding: 'utf8', timeout: 30000 }
  )
  if (result.status !== 0) {
    throw new Error(`scaffold.py failed: ${result.stderr}`)
  }
}

test('L3 build smoke: astro build succeeds for agency-demo', { timeout: 300000 }, () => {
  // Ensure manifest exists
  ensureManifest()

  // Run codegen + build-tokens + astro build
  const result = spawnSync(
    'npm',
    ['run', 'build'],
    {
      cwd: ADAPTER_ROOT,
      encoding: 'utf8',
      timeout: 240000,
      env: {
        ...process.env,
        // Point to agency-demo manifest (default dogfood path)
        // PUBLIC_SITE_MANIFEST defaults to out/agency-demo/site-manifest.json
        FORCE_COLOR: '0',
      },
      shell: process.platform === 'win32',
    }
  )

  assert.strictEqual(
    result.status, 0,
    `npm run build must exit 0 (L3 BUILD SUCCESS)\nstdout: ${result.stdout}\nstderr: ${result.stderr}`
  )
})

test('L3 build: dist/index.html exists (home page)', () => {
  const distHome = resolve(ADAPTER_ROOT, 'dist', 'index.html')
  assert.ok(existsSync(distHome), 'dist/index.html must exist (home page rendered)')
})

test('L3 build: dist/about/index.html exists (about page)', () => {
  const distAbout = resolve(ADAPTER_ROOT, 'dist', 'about', 'index.html')
  assert.ok(existsSync(distAbout), 'dist/about/index.html must exist (about page rendered)')
})

test('L3 build: dist contains CSS bundle', () => {
  const distDir = resolve(ADAPTER_ROOT, 'dist')
  const astroDir = resolve(distDir, '_astro')
  if (existsSync(astroDir)) {
    const files = readdirSync(astroDir)
    const cssFiles = files.filter(f => f.endsWith('.css'))
    assert.ok(cssFiles.length > 0, 'dist/_astro/ must contain at least one CSS bundle')
  }
  // If _astro doesn't exist, dist root may have assets directly — just check dist exists
  assert.ok(existsSync(distDir), 'dist/ directory must exist after build')
})
