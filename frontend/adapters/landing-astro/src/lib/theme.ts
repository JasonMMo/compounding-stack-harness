/**
 * theme.ts — Theme loader and style hint resolver.
 * Used by [...page].astro at SSG build time.
 * DEC-1: unknown/absent/default theme slug -> aurora.
 */

import { readFileSync, existsSync } from 'fs'
import { resolve } from 'path'
import yaml from 'js-yaml'

export const FLAGSHIP_THEME = 'aurora'

// Resolve REPO_ROOT relative to adapter root (frontend/adapters/landing-astro)
// process.cwd() is the adapter root during `astro build` (npm run build from adapter dir)
function getRepoRoot(): string {
  const cwd = process.cwd()
  // candidate: cwd is adapter root -> 3 levels up = repo root
  const candidate = resolve(cwd, '..', '..', '..')
  return candidate
}

export function getThemesDir(): string {
  return resolve(getRepoRoot(), 'presets', 'themes')
}

export function resolveThemeSlug(slug: string | undefined): string {
  if (!slug || slug === 'default') {
    if (slug === 'default') {
      process.stderr.write(`[theme] "default" -> flagship "${FLAGSHIP_THEME}"\n`)
    }
    return FLAGSHIP_THEME
  }
  const themePath = resolve(getThemesDir(), slug, 'theme.yaml')
  if (!existsSync(themePath)) {
    process.stderr.write(`[theme] unknown theme "${slug}" — falling back to "${FLAGSHIP_THEME}"\n`)
    return FLAGSHIP_THEME
  }
  return slug
}

export function loadTheme(slug: string): Record<string, unknown> {
  const p = resolve(getThemesDir(), slug, 'theme.yaml')
  try {
    return yaml.load(readFileSync(p, 'utf-8')) as Record<string, unknown>
  } catch {
    return {}
  }
}

export function getStyleHints(
  theme: Record<string, unknown>,
  sectionType: string,
  variant?: string
): Record<string, unknown> {
  if (!variant) return {}
  const sections = (theme.sections ?? {}) as Record<string, unknown>
  const sectionEntry = (sections[sectionType] ?? {}) as Record<string, unknown>
  return (sectionEntry[variant] ?? {}) as Record<string, unknown>
}

export function getMotionPreset(
  theme: Record<string, unknown>,
  sectionType: string
): string {
  const motion = (theme.motion ?? {}) as Record<string, unknown>
  const presets = (motion.section_presets ?? {}) as Record<string, string>
  return presets[sectionType] ?? (motion.default_preset as string) ?? 'fade-up'
}
