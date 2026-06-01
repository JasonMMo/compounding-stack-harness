import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@contract': resolve(__dirname, './src/contract/contract.gen.ts'),
      '@api': resolve(__dirname, './src/api'),
      '@hooks': resolve(__dirname, './src/hooks'),
      '@screens': resolve(__dirname, './src/screens'),
      '@components': resolve(__dirname, './src/components'),
    },
  },
  server: {
    port: parseInt(process.env.FRONTEND_PORT ?? '5173'),
    proxy: {
      '/api': {
        target: process.env.BACKEND_BASE_URL ?? 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: parseInt(process.env.FRONTEND_PORT ?? '5173'),
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  test: {
    environment: 'node',
    globals: true,
    include: [
      // Compliance suite in tests/adapters/react/ (relative to repo root)
      '../../../tests/adapters/react/**/*.test.ts',
      // Any local tests
      'src/**/*.test.ts',
    ],
  },
})
