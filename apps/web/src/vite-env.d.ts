export interface ImportMetaEnv {
  readonly VITE_API_PROTOCOL?: string
  readonly VITE_API_IP?: string
}

export interface ImportMeta {
  readonly env: ImportMetaEnv
}

export {}