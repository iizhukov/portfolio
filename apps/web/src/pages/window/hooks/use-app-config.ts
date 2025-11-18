import { useMemo } from 'react'
import { SERVICE_APP_MAPPING } from '@pages/launchpad/api/modules'
import { safeDecodeURIComponent } from '@shared/utils/safe-decode'
import type { WindowQueryParams, AppConfig, AppType } from '../types'

export const useAppConfig = (urlParams: WindowQueryParams): AppConfig => {
  return useMemo((): AppConfig => {
    const appId = urlParams.app
    const dbml = urlParams.dbml
    const excalidraw = urlParams.excalidraw
    const swagger = urlParams.swagger
    const url = urlParams.url
    const title = urlParams.title ? safeDecodeURIComponent(urlParams.title) : undefined

    if (excalidraw) {
      return {
        id: 'architecture',
        name: title || 'Architecture',
        icon: '/assets/icons/architecture.ico',
        type: 'architecture',
        excalidraw: safeDecodeURIComponent(excalidraw),
      }
    }

    if (dbml) {
      return {
        id: 'database-viewer',
        name: title || 'Database',
        icon: '/assets/icons/database.ico',
        type: 'database',
        dbml: safeDecodeURIComponent(dbml),
      }
    }
    
    if (swagger) {
      return {
        id: 'swagger-viewer',
        name: title || 'Swagger',
        icon: '/assets/icons/swagger.ico',
        type: 'swagger',
        swagger: safeDecodeURIComponent(swagger),
      }
    }

    if (url && title) {
      return {
        id: 'markdown-viewer',
        name: safeDecodeURIComponent(title) || 'Document',
        icon: '/assets/icons/docs.ico',
        type: 'markdown-viewer',
        url: safeDecodeURIComponent(url),
      }
    }

    if (!appId) {
      return {
        id: 'finder',
        name: 'Projects',
        icon: '/assets/icons/wpaper_folder.ico',
        type: 'finder',
      }
    }
    
    if (appId === 'settings') {
      return {
        id: 'settings',
        name: 'Settings',
        icon: '/assets/icons/settings.ico',
        type: 'settings',
      }
    }
    
    if (appId === 'connections') {
      return {
        id: 'connections',
        name: 'Connections',
        icon: '/assets/icons/discord.ico',
        type: 'connections',
      }
    }

    if (appId === 'projects' || appId === 'finder') {
      return {
        id: 'finder',
        name: 'Projects',
        icon: '/assets/icons/wpaper_folder.ico',
        type: 'finder',
      }
    }

    const serviceMapping = SERVICE_APP_MAPPING[appId]
    if (serviceMapping) {
      const appType = serviceMapping.type as AppType
      return {
        id: appId,
        name: serviceMapping.name,
        icon: serviceMapping.icon,
        type: appType,
      }
    }
    
    return {
      id: 'finder',
      name: 'Projects',
      icon: '/assets/icons/wpaper_folder.ico',
      type: 'finder',
    }
  }, [
    urlParams.app,
    urlParams.dbml,
    urlParams.excalidraw,
    urlParams.swagger,
    urlParams.url,
    urlParams.title,
  ])
}

