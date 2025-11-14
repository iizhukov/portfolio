import { type FileType } from '../types/finder'

export const FILE_ICON_MAP: Record<FileType, string> = {
  // Folders
  folder: '/assets/icons/folder.ico',
  'folder-filled': '/assets/icons/wpaper_folder.ico',

  // Documentation
  readme: '/assets/icons/docs.ico',

  // Diagrams and architecture
  architecture: '/assets/icons/diagram.ico',
  database: '/assets/icons/schema.ico',

  // Links
  demo: '/assets/icons/demo.ico',
  github: '/assets/icons/github.ico',

  // API Documentation
  swagger: '/assets/icons/postman.ico',
}

export const getFileIcon = (fileType: FileType): string => {
  return FILE_ICON_MAP[fileType] || FILE_ICON_MAP.folder
}

export const getFolderIcon = (hasChildren: boolean): string => {
  return hasChildren ? FILE_ICON_MAP['folder-filled'] : FILE_ICON_MAP.folder
}

export const getFileTypeFromName = (name: string): FileType => {
  const lowerName = name.toLowerCase()

  // README files
  if (lowerName.includes('readme') || lowerName === 'readme.md') {
    return 'readme'
  }

  // Architecture diagrams (excalidraw)
  if (
    lowerName.includes('architecture') ||
    lowerName.includes('arch') ||
    lowerName.includes('excalidraw')
  ) {
    return 'architecture'
  }

  // Database diagrams (dbdiagram)
  if (
    lowerName.includes('database') ||
    lowerName.includes('db') ||
    lowerName.includes('dbdiagram') ||
    lowerName.includes('schema')
  ) {
    return 'database'
  }

  // GitHub repositories
  if (lowerName.includes('github') || lowerName.includes('repository') || lowerName.includes('repo')) {
    return 'github'
  }

  // Demo links
  if (lowerName.includes('demo') || lowerName.includes('live') || lowerName.includes('preview')) {
    return 'demo'
  }

  // Swagger documentation
  if (
    lowerName.includes('swagger') ||
    lowerName.includes('api-docs') ||
    lowerName.includes('openapi')
  ) {
    return 'swagger'
  }

  // Default to folder for unknown types
  return 'folder'
}
