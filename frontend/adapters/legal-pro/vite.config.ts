import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// legal-pro adapter — Vite config
// Proxies /auth, /search, /health to the legal-rag backend (not /api/* like generic adapter).
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@contract': resolve(__dirname, './src/contract/contract.gen.ts'),
      '@api': resolve(__dirname, './src/api'),
      '@screens': resolve(__dirname, './src/screens'),
      '@components': resolve(__dirname, './src/components'),
    },
  },
  server: {
    port: parseInt(process.env.FRONTEND_PORT ?? '5174'),
    proxy: {
      // legal-rag backend routes (no /api prefix — direct service paths)
      '/auth': {
        target: process.env.BACKEND_BASE_URL ?? 'http://localhost:8000',
        changeOrigin: true,
      },
      '/search': {
        target: process.env.BACKEND_BASE_URL ?? 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: process.env.BACKEND_BASE_URL ?? 'http://localhost:8000',
        changeOrigin: true,
      },
      '/documents': {
        target: process.env.BACKEND_BASE_URL ?? 'http://localhost:8000',
        changeOrigin: true,
      },
      '/cases': {
        target: process.env.BACKEND_BASE_URL ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: parseInt(process.env.FRONTEND_PORT ?? '5174'),
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // base=/pro/ ensures all asset hrefs are rooted at /pro/ when served
    // by FastAPI StaticFiles at /pro.  Must match BrowserRouter basename in main.tsx.
  },
  base: '/pro/',
  test: {
    environment: 'node',
    globals: true,
    include: ['src/**/*.test.ts'],
  },
})
