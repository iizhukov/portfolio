import { Window } from './window'
import { useEffect, useState, useMemo, useRef } from 'react'
import { LOCATION_CHANGE_EVENT } from '@shared/utils/location'
import { navigateToWindow, replaceWindowRoute, navigateToLaunchpad } from '@shared/utils/navigation'
import { parseWindowQueryParams } from '@shared/utils/query-params'
import { useAppConfig } from '../hooks/use-app-config'
import { isBrowser } from '@shared/utils/browser'
import type { WindowQueryParams } from '../types'

const WINDOW_APPEAR_DELAY = 50
const WINDOW_CLOSE_DELAY = 500

export const WindowPage = () => {
  const [isActive, setIsActive] = useState(false)
  const [isMaximized, setIsMaximized] = useState(false)
  const [urlParams, setUrlParams] = useState<WindowQueryParams>(parseWindowQueryParams)
  const prevAppIdRef = useRef<string | undefined>(urlParams.app)
  const prevParamsRef = useRef<string>(JSON.stringify(urlParams))

  useEffect(() => {
    if (!isBrowser) return

    const handleLocationChange = () => {
      const newParams = parseWindowQueryParams()
      const paramsString = JSON.stringify(newParams)
      const appChanged = prevAppIdRef.current !== newParams.app
      const paramsChanged = prevParamsRef.current !== paramsString
      
      if (paramsChanged) {
        setUrlParams(newParams)
        prevAppIdRef.current = newParams.app
        prevParamsRef.current = paramsString
        
        if (appChanged) {
          setIsActive(false)
          setIsMaximized(false)
          setTimeout(() => {
            setIsActive(true)
          }, WINDOW_APPEAR_DELAY)
        } else {
          setIsActive(true)
        }
      }
    }

    window.addEventListener('popstate', handleLocationChange)
    window.addEventListener(LOCATION_CHANGE_EVENT, handleLocationChange)

    const checkInterval = setInterval(() => {
      const currentParams = parseWindowQueryParams()
      const currentString = JSON.stringify(currentParams)
      if (currentString !== prevParamsRef.current) {
        handleLocationChange()
      }
    }, 100)

    handleLocationChange()

    return () => {
      window.removeEventListener('popstate', handleLocationChange)
      window.removeEventListener(LOCATION_CHANGE_EVENT, handleLocationChange)
      clearInterval(checkInterval)
    }
  }, [])

  const currentApp = useAppConfig(urlParams)

  useEffect(() => {
    if (currentApp.type === 'finder' && !urlParams.app) {
      const params: WindowQueryParams = { app: 'projects' }
      if (urlParams.path) {
        params.path = urlParams.path
      }
      replaceWindowRoute(params)
    }
  }, [currentApp.type, urlParams.app, urlParams.path])

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
        const params: WindowQueryParams = { app: 'projects', path: returnPath }
        navigateToWindow(params)
      } else {
        navigateToLaunchpad()
      }
    }, WINDOW_CLOSE_DELAY)
  }

  const handleMinimize = () => {
    setIsActive(false)
  }

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
