import { Window } from './window'
import { MOCK_APPS } from '../model/window'
import { router } from '@shared/router'
import { useEffect, useState, useMemo } from 'react'

// Константы для анимаций
const WINDOW_APPEAR_DELAY = 50 // ms
const WINDOW_CLOSE_DELAY = 500 // ms

export const WindowPage = () => {
  const [isActive, setIsActive] = useState(false)
  const [isMaximized, setIsMaximized] = useState(false)
  const [currentAppIndex, _] = useState(0)

  const currentApp = MOCK_APPS[currentAppIndex]

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
      router.push({ path: '/', params: {}, query: {}, method: 'push' })
    }, WINDOW_CLOSE_DELAY) // +300ms для анимации виджета
  }

  const handleMinimize = () => {
    // TODO: Implement minimize functionality
  }

  const handleMaximize = () => {
    setIsMaximized(!isMaximized)
  }

  // const switchToApp = (appType: string) => {
  //   const appIndex = MOCK_APPS.findIndex(app => app.type === appType)
  //   if (appIndex !== -1) {
  //     setCurrentAppIndex(appIndex)
  //   }
  // }

  // Для демонстрации - переключаемся на finder через 3 секунды
  useEffect(() => {
    const timer = setTimeout(() => {
      // switchToApp('finder')
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

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
