// tailwind.config.js — base config for landing-astro adapter.
// Theme tokens are injected by scripts/build-tokens.mjs at build time
// via src/styles/tokens.gen.css (CSS custom properties).
// Tailwind theme.extend values are written to src/styles/tailwind-theme.gen.js
// and imported here dynamically.
//
// Pattern: build-tokens.mjs writes CSS vars (:root) + tailwind-theme.gen.js.
// This config reads the generated JS to populate theme.extend.
// If tailwind-theme.gen.js does not exist yet (first run before build), uses empty extend.

import { createRequire } from 'module'
import { existsSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const generatedThemePath = resolve(__dirname, 'src', 'styles', 'tailwind-theme.gen.js')

let generatedTheme = {}
if (existsSync(generatedThemePath)) {
  // Dynamic import not available in CJS require context; use createRequire
  const req = createRequire(import.meta.url)
  try {
    generatedTheme = req(generatedThemePath).theme ?? {}
  } catch {
    // First build before codegen — safe to continue with empty theme
    generatedTheme = {}
  }
}

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/**/*.{astro,html,js,jsx,ts,tsx,vue,svelte}',
  ],
  theme: {
    extend: {
      ...generatedTheme,
    },
  },
  plugins: [],
}
