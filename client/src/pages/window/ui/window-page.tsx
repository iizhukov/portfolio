import { Window } from './window'
import { MOCK_APPS } from '../model/window'
import { router } from '@shared/router'
import { useEffect, useState } from 'react'

export const WindowPage = () => {
  const [isActive, setIsActive] = useState(false)

  const currentApp = MOCK_APPS[0]

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsActive(true)
    }, 50)

    return () => clearTimeout(timer)
  }, [])

  const handleClose = () => {
    setIsActive(false)
    setTimeout(() => {
      router.push({ path: '/', params: {}, query: {}, method: 'push' })
    }, 500)
  }

  const handleMinimize = () => {
    console.log('Minimize window')
  }

  const handleMaximize = () => {
    console.log('Maximize window')
  }

  return (
    <Window
      app={currentApp}
      isActive={isActive}
      onClose={handleClose}
      onMinimize={handleMinimize}
      onMaximize={handleMaximize}
    />
  )
}
