import { type Project } from '../types/finder'
import { notifyLocationChange } from '@shared/utils/location'

let currentFinderPath: string[] = []

export const setCurrentFinderPath = (path: string[]): void => {
  currentFinderPath = path
}

export const getCurrentFinderPath = (): string[] => {
  return currentFinderPath
}

export const handleFileOpen = (project: Project): void => {
  if (project.type === 'folder') {
    return
  }

  if (!project.url) {
    console.warn(`No URL for file: ${project.name}`)
    alert(`[Заглушка] Файл ${project.name} не имеет URL`)
    return
  }

  let fileType = project.fileType
  if (!fileType && project.name) {
    const nameLower = project.name.toLowerCase()
    if (nameLower.includes('readme') || nameLower.endsWith('.md')) {
      fileType = 'readme'
    }
  }
  
  const finalFileType = fileType || 'folder'

  switch (finalFileType) {
    case 'readme':
      handleReadme(project)
      break
    case 'architecture':
      handleArchitecture(project)
      break
    case 'demo':
      handleDemo(project)
      break
    case 'github':
      handleGithub(project)
      break
    case 'database':
      handleDatabase(project)
      break
    case 'swagger':
      handleSwagger(project)
      break
    default:
      window.open(project.url, '_blank')
  }
}

const handleReadme = (project: Project): void => {
  if (project.url) {
    console.log('Opening README:', project.name, project.url)
    const finderPath = getCurrentFinderPath()
    const pathParam = finderPath.join(',')

    const query: Record<string, string> = {
    url: project.url,
    title: project.name,
    }
    if (pathParam) {
      query.returnPath = pathParam
    }

    const params = new URLSearchParams(query)
    const fullPath = `/window?${params.toString()}`
    window.history.pushState(null, '', fullPath)
    notifyLocationChange()
  } else {
    console.warn('No URL for README file:', project.name)
  }
}

const handleArchitecture = (project: Project): void => {
  if (!project.url) {
    console.warn('No Excalidraw URL for architecture file')
    return
  }

  const finderPath = getCurrentFinderPath()
  const pathParam = finderPath.join(',')

  const params = new URLSearchParams({
    app: 'architecture',
    excalidraw: project.url,
  })
  if (pathParam) {
    params.set('returnPath', pathParam)
  }

  const fullPath = `/window?${params.toString()}`
  window.history.pushState(null, '', fullPath)
  notifyLocationChange()
}

const handleDemo = (project: Project): void => {
  if (project.url) {
    window.open(project.url, '_blank')
  }
}

const handleGithub = (project: Project): void => {
  if (project.url) {
    window.open(project.url, '_blank')
  }
}

const handleDatabase = (project: Project): void => {
  if (!project.url) {
    console.warn('No DBML url for database file')
    return
  }

  const finderPath = getCurrentFinderPath()
  const pathParam = finderPath.join(',')

  const params = new URLSearchParams({
    dbml: project.url,
    app: 'database',
  })
  if (pathParam) {
    params.set('returnPath', pathParam)
  }

  const fullPath = `/window?${params.toString()}`
  window.history.pushState(null, '', fullPath)
  notifyLocationChange()
}

const handleSwagger = (project: Project): void => {
  if (!project.url) {
    console.warn('No Swagger URL for documentation file')
    return
  }

  const finderPath = getCurrentFinderPath()
  const pathParam = finderPath.join(',')

  const params = new URLSearchParams({
    app: 'swagger',
    swagger: project.url,
  })
  if (pathParam) {
    params.set('returnPath', pathParam)
  }

  const fullPath = `/window?${params.toString()}`
  window.history.pushState(null, '', fullPath)
  notifyLocationChange()
}

