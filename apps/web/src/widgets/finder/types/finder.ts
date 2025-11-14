export interface Project {
  id: string
  name: string
  type: 'folder' | 'file'
  icon: string
  fileType?: FileType
  children?: Project[]
  url?: string
}

export interface NavigationState {
  currentPath: string[]
  history: string[][]
  historyIndex: number
}

export interface FinderState {
  navigation: NavigationState
  selectedItems: string[]
  viewMode: 'grid' | 'list'
  sortBy: 'name' | 'type' | 'date'
  sortOrder: 'asc' | 'desc'
}

export type FileType =
  | 'folder'
  | 'folder-filled'
  | 'readme'
  | 'architecture'
  | 'demo'
  | 'github'
  | 'database'
  | 'swagger'
