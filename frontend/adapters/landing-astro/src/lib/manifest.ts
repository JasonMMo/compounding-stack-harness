/**
 * manifest.ts — Site manifest loader for landing-astro adapter.
 *
 * Reads out/<slug>/site-manifest.json at build time.
 * Path resolved from env PUBLIC_SITE_MANIFEST (absolute path) or falls back
 * to repo-root out/agency-demo/site-manifest.json for dogfood builds.
 *
 * G-1: this module reads the manifest; it does not reimplement section logic.
 * DEC-1: theme "default" or absent -> "aurora" (resolved in build-tokens, not here).
 */

import { readFileSync, existsSync } from 'fs'
import { resolve } from 'path'

// ── Types ──────────────────────────────────────────────────────────────────

export interface SectionCta {
  label: string
  href: string
}

export interface StatItem {
  label: string
  value: string
}

export interface Section {
  type: string
  variant?: string
  copy?: Record<string, string>
  assets?: string[]
  cta?: SectionCta
  items?: Array<Record<string, unknown>>
  /** Optional highlight pills (used by glowy-waves hero variant). */
  pills?: string[]
  /** Optional stat tiles (used by glowy-waves hero variant). */
  stats?: StatItem[]
  /** Optional image paths (used by logos/marquee-3d variant — proof wall). */
  images?: string[]
  /** Optional company name strings for asset-free text wordmark rendering (logos/horizontal-scroll). */
  companies?: string[]
}

export interface PageSeo {
  title?: string
  description?: string
  og_image?: string
}

export interface Page {
  slug: string
  title: string
  seo?: PageSeo
  sections: Section[]
}

export interface ContactBlock {
  enabled: boolean
  fields: string[]
  wire_key: string      // "entity.create" (DEC-5)
  entity_type: string   // "lead" (DEC-5)
}

export interface SiteManifest {
  slug: string
  deliverable_kind: string
  theme: string
  pages: Page[]
  contact?: ContactBlock
}

// ── Loader ─────────────────────────────────────────────────────────────────

/**
 * Load site-manifest.json from the path given by PUBLIC_SITE_MANIFEST env var,
 * or from the default dogfood path (repo-root/out/agency-demo/site-manifest.json).
 *
 * Called at build time (Astro SSG). Not available at runtime in browser.
 */
export function loadManifest(): SiteManifest {
  const envPath = process.env['PUBLIC_SITE_MANIFEST']

  let manifestPath: string

  if (envPath) {
    manifestPath = resolve(envPath)
  } else {
    // Default dogfood: resolve from process.cwd() (repo root when running from repo root,
    // or from adapter root — try both).
    // process.cwd() is stable at SSG build time even after bundling.
    const cwd = process.cwd()
    // If cwd is the adapter root (frontend/adapters/landing-astro), go up 3 levels
    const candidate1 = resolve(cwd, 'out', 'agency-demo', 'site-manifest.json')
    const candidate2 = resolve(cwd, '..', '..', '..', 'out', 'agency-demo', 'site-manifest.json')
    if (existsSync(candidate1)) {
      manifestPath = candidate1
    } else {
      manifestPath = candidate2
    }
  }

  if (!existsSync(manifestPath)) {
    throw new Error(
      `[manifest] site-manifest.json not found at: ${manifestPath}\n` +
      `  Run: python scripts/workflow/scaffold.py --profile <slug>\n` +
      `  Or set PUBLIC_SITE_MANIFEST=<absolute-path> env var.`
    )
  }

  const raw = readFileSync(manifestPath, 'utf-8')
  const manifest: SiteManifest = JSON.parse(raw)

  if (manifest.deliverable_kind !== 'marketing-site') {
    throw new Error(
      `[manifest] expected deliverable_kind=marketing-site, got: ${manifest.deliverable_kind}`
    )
  }

  return manifest
}
