import { Window } from './window'
import { MOCK_APPS } from '../model/window'
import { router } from '@shared/router'
import { useEffect, useState, useMemo } from 'react'
import { LOCATION_CHANGE_EVENT, notifyLocationChange } from '@shared/utils/location'

const WINDOW_APPEAR_DELAY = 50
const WINDOW_CLOSE_DELAY = 500

const parseQueryParams = () => {
  const params = new URLSearchParams(window.location.search)
  return {
    url: params.get('url'),
    title: params.get('title'),
    app: params.get('app'),
    path: params.get('path'),
    returnPath: params.get('returnPath'),
    dbml: params.get('dbml'),
    excalidraw: params.get('excalidraw'),
    swagger: params.get('swagger'),
  }
}

export const WindowPage = () => {
  const [isActive, setIsActive] = useState(false)
  const [isMaximized, setIsMaximized] = useState(false)
  const [urlParams, setUrlParams] = useState(parseQueryParams)

  useEffect(() => {
    const handleChange = () => {
      setUrlParams(parseQueryParams())
    }

    window.addEventListener('popstate', handleChange)
    window.addEventListener(LOCATION_CHANGE_EVENT, handleChange)
    handleChange()

    return () => {
      window.removeEventListener('popstate', handleChange)
      window.removeEventListener(LOCATION_CHANGE_EVENT, handleChange)
    }
  }, [])

  const currentApp = useMemo(() => {
    const dbml = urlParams.dbml
    const excalidraw = urlParams.excalidraw
    const swagger = urlParams.swagger
    const url = urlParams.url
    const title = urlParams.title ? decodeURIComponent(urlParams.title) : undefined

    if (excalidraw) {
      return {
        id: 'architecture',
        name: title ?? '',
        icon: '/assets/icons/architecture.ico',
        type: 'architecture',
        excalidraw: decodeURIComponent(excalidraw),
      }
    }

    if (dbml) {
      return {
        id: 'database-viewer',
        name: title ?? '',
        icon: '/assets/icons/database.ico',
        type: 'database',
        dbml: decodeURIComponent(dbml),
      }
    }
    
    if (swagger) {
      return {
        id: 'swagger-viewer',
        name: title ?? '',
        icon: '/assets/icons/swagger.ico',
        type: 'swagger',
        swagger: decodeURIComponent(swagger),
      }
    }

    if (url && title) {
      return {
        id: 'markdown-viewer',
        name: decodeURIComponent(title),
        icon: '/assets/icons/docs.ico',
        type: 'markdown-viewer',
        url: decodeURIComponent(url),
      }
    }

    const appId = urlParams.app || 'finder'
    const foundApp = MOCK_APPS.find(app => app.id === appId)
    
    if (foundApp) {
      return foundApp
    }
    
    if (appId === 'projects' || appId === 'finder') {
      return {
        id: 'finder',
        name: 'Projects',
        icon: '/assets/icons/wpaper_folder.ico',
        type: 'finder',
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
    
    return MOCK_APPS[0]
  }, [urlParams])

  const windowSize = useMemo(() => {
    if (isMaximized) return 'fullscreen'

    switch (currentApp.type) {
      case 'finder':
        return 'large'
      case 'notes':
        return 'vertical'
      case 'settings':
        return 'large'
      case 'theme':
        return 'standard'
      case 'markdown-viewer':
        return 'large'
      case 'connections':
        return 'vertical'
      case 'database':
        return 'fullscreen'
      case 'architecture':
        return 'fullscreen'
      case 'swagger':
        return 'large'
      default:
        return 'standard'
    }
  }, [isMaximized, currentApp.type])

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsActive(true)
    }, WINDOW_APPEAR_DELAY)

    return () => clearTimeout(timer)
  }, [])

  const handleClose = () => {
    setIsActive(false)
    setTimeout(() => {
      const returnPath = urlParams.returnPath
      if (returnPath) {
        const params = new URLSearchParams({ app: 'finder', path: returnPath })
        const fullPath = `/window?${params.toString()}`
        router
          .push({ path: fullPath, params: {}, query: {}, method: 'push' })
          .then(() => {
            setUrlParams({
              url: null,
              title: null,
              app: 'finder',
              path: returnPath,
              returnPath: null,
              dbml: null,
              excalidraw: null,
              swagger: null,
            })
            setIsActive(true)
            notifyLocationChange()
            const cleanParams = new URLSearchParams({ app: 'finder', path: returnPath })
            window.history.replaceState(null, '', `/window?${cleanParams.toString()}`)
          })
          .catch(() => {
            window.location.href = fullPath
          })
      } else {
        router
          .push({ path: '/', params: {}, query: {}, method: 'push' })
          .then(() => {
            setIsActive(true)
            notifyLocationChange()
          })
          .catch(() => {
            window.location.href = '/'
          })
      }
    }, WINDOW_CLOSE_DELAY)
  }

  const handleMinimize = () => {}

  const handleMaximize = () => {
    setIsMaximized(!isMaximized)
  }

  return (
    <Window
      app={currentApp}
      isActive={isActive}
      onClose={handleClose}
      onMinimize={handleMinimize}
      onMaximize={handleMaximize}
      size={windowSize}
    />
  )
}
