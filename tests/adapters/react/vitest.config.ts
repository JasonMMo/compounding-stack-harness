import { defineConfig } from 'vitest/config'
import { resolve } from 'path'

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
  },
  resolve: {
    alias: {
      // Allows the test to import contract.gen.ts and wire.ts from the adapter src
      '@contract': resolve(__dirname, '../../../frontend/adapters/react/src/contract/contract.gen.ts'),
    },
  },
})
