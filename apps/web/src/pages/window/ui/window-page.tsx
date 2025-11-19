import { Window } from './window'
import { useEffect, useState, useMemo, useRef } from 'react'
import { LOCATION_CHANGE_EVENT } from '@shared/utils/location'
import { navigateToWindow, replaceWindowRoute, navigateToLaunchpad } from '@shared/utils/navigation'
import { parseWindowQueryParams } from '@shared/utils/query-params'
import { useAppConfig } from '../hooks/use-app-config'
import { isBrowser } from '@shared/utils/browser'
import type { WindowQueryParams } from '../types'

const WINDOW_APPEAR_DELAY = 100
const WINDOW_CLOSE_DELAY = 350
const WINDOW_SWITCH_DELAY = 350

export const WindowPage = () => {
  const initialParams = parseWindowQueryParams()
  const [isActive, setIsActive] = useState(false)
  const [isMaximized, setIsMaximized] = useState(false)
  const [urlParams, setUrlParams] = useState<WindowQueryParams>(initialParams)
  const prevAppIdRef = useRef<string | undefined>(undefined)
  const prevParamsRef = useRef<string>(JSON.stringify(initialParams))
  const isInitialMountRef = useRef(true)

  useEffect(() => {
    if (!isBrowser) return

    let switchTimeoutId: ReturnType<typeof setTimeout> | undefined

    const handleLocationChange = () => {
      const newParams = parseWindowQueryParams()
      const paramsString = JSON.stringify(newParams)
      const prevApp = prevAppIdRef.current
      const newApp = newParams.app
      const isFirstOpen = isInitialMountRef.current && newApp !== undefined
      const appChanged = !isInitialMountRef.current && prevApp !== undefined && newApp !== undefined && prevApp !== newApp
      const paramsChanged = prevParamsRef.current !== paramsString
      
      if (isFirstOpen) {
        setUrlParams(newParams)
        prevAppIdRef.current = newApp
        prevParamsRef.current = paramsString
        isInitialMountRef.current = false
        setTimeout(() => {
          setIsActive(true)
        }, WINDOW_APPEAR_DELAY)
        return
      }
      
      if (paramsChanged) {
        if (switchTimeoutId) {
          clearTimeout(switchTimeoutId)
        }

        setUrlParams(newParams)
        prevAppIdRef.current = newApp
        prevParamsRef.current = paramsString
        
        if (appChanged) {
          setIsActive(false)
          setIsMaximized(false)
          switchTimeoutId = setTimeout(() => {
            setIsActive(true)
            switchTimeoutId = undefined
          }, WINDOW_SWITCH_DELAY)
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
      if (switchTimeoutId) {
        clearTimeout(switchTimeoutId)
      }
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
    // setIsActive(false)
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
