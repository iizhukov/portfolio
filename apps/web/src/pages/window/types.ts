export interface WindowQueryParams {
  url?: string
  title?: string
  app?: string
  path?: string
  returnPath?: string
  dbml?: string
  excalidraw?: string
  swagger?: string
}

export type AppType = 
  | 'finder'
  | 'settings'
  | 'connections'
  | 'markdown-viewer'
  | 'database'
  | 'architecture'
  | 'swagger'
  | 'notes'
  | 'theme'

export interface AppConfig {
  id: string
  name: string
  icon: string
  type: AppType
  url?: string
  dbml?: string
  excalidraw?: string
  swagger?: string
}

