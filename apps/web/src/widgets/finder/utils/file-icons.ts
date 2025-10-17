import { type FileType } from '../types/finder'

export const FILE_ICON_MAP: Record<FileType, string> = {
  // Folders
  folder: '/assets/icons/folder.ico',
  'folder-filled': '/assets/icons/wpaper_folder.ico',

  // GitHub and repositories
  github: '/assets/icons/github.ico',

  // Demos and live sites
  demo: '/assets/icons/demo.ico',

  // Diagrams and schemas
  diagram: '/assets/icons/diagram.ico',
  schema: '/assets/icons/schema.ico',

  // Documentation
  docs: '/assets/icons/docs.ico',

  // Deployment and infrastructure
  deployment: '/assets/icons/deployment.ico',

  // Configuration files
  config: '/assets/icons/config.ico',

  // Testing
  test: '/assets/icons/test.ico',

  // Package management
  package: '/assets/icons/package.ico',

  // Build tools
  build: '/assets/icons/build.ico',

  // Frontend components
  component: '/assets/icons/component.ico',

  // Pages
  page: '/assets/icons/page.ico',

  // Utilities
  util: '/assets/icons/util.ico',
}

export const getFileIcon = (fileType: FileType): string => {
  return FILE_ICON_MAP[fileType] || FILE_ICON_MAP.folder
}

export const getFolderIcon = (hasChildren: boolean): string => {
  return hasChildren ? FILE_ICON_MAP['folder-filled'] : FILE_ICON_MAP.folder
}

export const getFileTypeFromName = (name: string): FileType => {
  const lowerName = name.toLowerCase()

  // GitHub repositories
  if (lowerName.includes('github') || lowerName.includes('repository')) {
    return 'github'
  }

  // Demos and live sites
  if (lowerName.includes('demo') || lowerName.includes('live')) {
    return 'demo'
  }

  // Diagrams
  if (lowerName.includes('diagram') || lowerName.includes('architecture')) {
    return 'diagram'
  }

  // Schemas
  if (lowerName.includes('schema') || lowerName.includes('database')) {
    return 'schema'
  }

  // Documentation
  if (lowerName.includes('doc') || lowerName.includes('readme') || lowerName.includes('guide')) {
    return 'docs'
  }

  // Deployment
  if (lowerName.includes('deployment') || lowerName.includes('deploy')) {
    return 'deployment'
  }

  // Configuration
  if (
    lowerName.includes('config') ||
    lowerName.includes('package.json') ||
    lowerName.includes('settings')
  ) {
    return 'config'
  }

  // Tests
  if (lowerName.includes('test') || lowerName.includes('spec')) {
    return 'test'
  }

  // Package files
  if (
    lowerName.includes('package') ||
    lowerName.includes('yarn.lock') ||
    lowerName.includes('package-lock')
  ) {
    return 'package'
  }

  // Build files
  if (lowerName.includes('build') || lowerName.includes('webpack') || lowerName.includes('vite')) {
    return 'build'
  }

  // Components
  if (lowerName.includes('component') || lowerName.includes('ui')) {
    return 'component'
  }

  // Pages
  if (lowerName.includes('page') || lowerName.includes('route')) {
    return 'page'
  }

  // Utilities
  if (lowerName.includes('util') || lowerName.includes('helper') || lowerName.includes('lib')) {
    return 'util'
  }

  // Default to folder for unknown types
  return 'folder'
}
