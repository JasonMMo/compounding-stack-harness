// astro.config.mjs — Astro configuration for landing-astro adapter.
// Output: static (SSG). Adapter reads site-manifest.json at build time.
// Integrations: @astrojs/tailwind (reads tailwind.config.js).
// Self-host fonts via @fontsource packages (DEC-2: no external CDN).

import { defineConfig } from 'astro/config'
import tailwind from '@astrojs/tailwind'

export default defineConfig({
  output: 'static',
  integrations: [
    tailwind({
      // tailwind.config.js lives at adapter root — Astro resolves relative to project root
      configFile: './tailwind.config.js',
    }),
  ],
  // PUBLIC_SITE_MANIFEST and PUBLIC_API_BASE are passed as env vars at build time.
  // astro.env is not used — env vars are read by src/lib/manifest.ts at build time.
  build: {
    // Ensure trailing slashes match page slugs
    format: 'directory',
  },
  vite: {
    // Allow Vite to resolve @fontsource packages from node_modules
    optimizeDeps: {
      include: [],
    },
  },
})
