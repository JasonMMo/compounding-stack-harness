/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_MANIFEST_URL?: string
  readonly FRONTEND_PORT?: string
  readonly BACKEND_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
