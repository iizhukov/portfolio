import { type FileType } from '../types/finder'

export const FILE_ICON_MAP: Record<FileType, string> = {
  folder: '/assets/icons/folder.ico',
  'folder-filled': '/assets/icons/wpaper_folder.ico',
  readme: '/assets/icons/docs.ico',
  architecture: '/assets/icons/diagram.ico',
  database: '/assets/icons/schema.ico',
  demo: '/assets/icons/demo.ico',
  github: '/assets/icons/github.ico',
  swagger: '/assets/icons/swagger.ico',
}

export const getFileIcon = (
  type: 'folder' | 'file',
  fileType?: string | null
): string => {
  if (type === 'folder') {
    return FILE_ICON_MAP.folder
  }

  if (fileType && fileType in FILE_ICON_MAP) {
    return FILE_ICON_MAP[fileType as FileType]
  }

  if (fileType) {
    const fileTypeLower = fileType.toLowerCase()
    if (fileTypeLower.includes('readme')) return FILE_ICON_MAP.readme
    if (fileTypeLower.includes('arch') || fileTypeLower.includes('excalidraw'))
      return FILE_ICON_MAP.architecture
    if (fileTypeLower.includes('db') || fileTypeLower.includes('schema'))
      return FILE_ICON_MAP.database
    if (fileTypeLower.includes('github')) return FILE_ICON_MAP.github
    if (fileTypeLower.includes('demo')) return FILE_ICON_MAP.demo
    if (fileTypeLower.includes('swagger') || fileTypeLower.includes('openapi'))
      return FILE_ICON_MAP.swagger
  }

  return FILE_ICON_MAP.folder
}

export const getFolderIcon = (hasChildren: boolean): string => {
  return hasChildren ? FILE_ICON_MAP['folder-filled'] : FILE_ICON_MAP.folder
}

export const getFileTypeFromName = (name: string): FileType => {
  const lowerName = name.toLowerCase()

  if (lowerName.includes('readme') || lowerName === 'readme.md') {
    return 'readme'
  }

  if (
    lowerName.includes('architecture') ||
    lowerName.includes('arch') ||
    lowerName.includes('excalidraw')
  ) {
    return 'architecture'
  }

  if (
    lowerName.includes('database') ||
    lowerName.includes('db') ||
    lowerName.includes('dbdiagram') ||
    lowerName.includes('schema')
  ) {
    return 'database'
  }

  if (lowerName.includes('github') || lowerName.includes('repository') || lowerName.includes('repo')) {
    return 'github'
  }

  if (lowerName.includes('demo') || lowerName.includes('live') || lowerName.includes('preview')) {
    return 'demo'
  }

  if (
    lowerName.includes('swagger') ||
    lowerName.includes('api-docs') ||
    lowerName.includes('openapi')
  ) {
    return 'swagger'
  }

  return 'folder'
}
