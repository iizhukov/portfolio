import { type Project } from '../types/finder'
import { getFileUrl } from '@shared/utils/url'
import { ApiErrorHandler } from '@shared/api/error-handler'
import { SERVICE_APP_MAPPING } from '@pages/launchpad/api/modules'
import { navigateToWindow } from '@shared/utils/navigation'
import type { WindowQueryParams } from '@pages/window/types'

export const handleFileOpen = (project: Project, currentPath: string[] = []): void => {
  if (project.type === 'folder') {
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
      if (!project.url) {
        ApiErrorHandler.handleError(new Error(`File ${project.name} does not have a URL`))
        return
      }
      handleReadme(project, currentPath)
      break
    case 'architecture':
      if (!project.url) {
        ApiErrorHandler.handleError(new Error(`File ${project.name} does not have a URL`))
        return
      }
      handleArchitecture(project, currentPath)
      break
    case 'demo':
      if (!project.url) {
        ApiErrorHandler.handleError(new Error(`File ${project.name} does not have a URL`))
        return
      }
      handleDemo(project)
      break
    case 'github':
      if (!project.url) {
        ApiErrorHandler.handleError(new Error(`File ${project.name} does not have a URL`))
        return
      }
      handleGithub(project)
      break
    case 'database':
      if (!project.url) {
        ApiErrorHandler.handleError(new Error(`File ${project.name} does not have a URL`))
        return
      }
      handleDatabase(project, currentPath)
      break
    case 'swagger':
      if (!project.url) {
        ApiErrorHandler.handleError(new Error(`File ${project.name} does not have a URL`))
        return
      }
      handleSwagger(project, currentPath)
      break
    default:
      if (project.url) {
        window.open(getFileUrl(project.url), '_blank')
      } else {
        const appName = project.name.toLowerCase()
        const appMapping = Object.entries(SERVICE_APP_MAPPING).find(
          ([, mapping]) => mapping.name.toLowerCase() === appName
        )
        if (appMapping) {
          handleAppOpen(appMapping[0], currentPath)
        } else {
          ApiErrorHandler.handleError(new Error(`Cannot open ${project.name}: no URL or app mapping found`))
        }
      }
  }
}

const handleAppOpen = (appId: string, currentPath: string[]): void => {
  const pathParam = currentPath.join(',')
  const params: WindowQueryParams = {
    app: appId,
  }
  if (pathParam) {
    params.returnPath = pathParam
  }
  navigateToWindow(params)
}

const handleReadme = (project: Project, currentPath: string[]): void => {
  if (!project.url) {
    ApiErrorHandler.handleError(new Error(`No URL for README file: ${project.name}`))
    return
  }

  const pathParam = currentPath.join(',')
  const params: WindowQueryParams = {
    url: project.url,
    title: project.name,
  }
  if (pathParam) {
    params.returnPath = pathParam
  }
  navigateToWindow(params)
}

const handleArchitecture = (project: Project, currentPath: string[]): void => {
  if (!project.url) {
    ApiErrorHandler.handleError(new Error('No Excalidraw URL for architecture file'))
    return
  }

  const pathParam = currentPath.join(',')
  const params: WindowQueryParams = {
    app: 'architecture',
    excalidraw: project.url,
  }
  if (pathParam) {
    params.returnPath = pathParam
  }
  navigateToWindow(params)
}

const handleDemo = (project: Project): void => {
  if (project.url) {
    window.open(getFileUrl(project.url), '_blank')
  }
}

const handleGithub = (project: Project): void => {
  if (project.url) {
    window.open(getFileUrl(project.url), '_blank')
  }
}

const handleDatabase = (project: Project, currentPath: string[]): void => {
  if (!project.url) {
    ApiErrorHandler.handleError(new Error('No DBML URL for database file'))
    return
  }

  const pathParam = currentPath.join(',')
  const params: WindowQueryParams = {
    dbml: project.url,
    app: 'database',
  }
  if (pathParam) {
    params.returnPath = pathParam
  }
  navigateToWindow(params)
}

const handleSwagger = (project: Project, currentPath: string[]): void => {
  if (!project.url) {
    ApiErrorHandler.handleError(new Error('No Swagger URL for documentation file'))
    return
  }

  const pathParam = currentPath.join(',')
  const params: WindowQueryParams = {
    app: 'swagger',
    swagger: project.url,
  }
  if (pathParam) {
    params.returnPath = pathParam
  }
  navigateToWindow(params)
}

