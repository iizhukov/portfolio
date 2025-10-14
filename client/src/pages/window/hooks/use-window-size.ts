import { useState, useEffect } from 'react'
import { WINDOW_SIZES } from '../model/window'
import type { WindowSize } from '../ui/window'

// Базовые размеры экрана MacBook Air M1 13"
const BASE_SCREEN = {
  width: 1440,
  height: 900,
}

const SCREEN_BREAKPOINT = 1440 // px

type WindowDimensions = {
  width: string
  height: string
  maxWidth: string
  maxHeight: string
  top?: string
  left?: string
}

export const useWindowSize = (size: WindowSize) => {
  const [dimensions, setDimensions] = useState<WindowDimensions>(() => {
    const baseSize = WINDOW_SIZES[size]

    if (size === 'fullscreen') {
      return {
        width: baseSize.width,
        height: baseSize.height,
        maxWidth: baseSize.width,
        maxHeight: baseSize.height,
        top: '50%',
        left: '50%',
      }
    }

    return {
      width: baseSize.width,
      height: baseSize.height,
      maxWidth: size === 'vertical' ? '70vw' : '95vw',
      maxHeight: '90vh',
      top: undefined,
      left: undefined,
    }
  })

  useEffect(() => {
    const updateDimensions = () => {
      const baseSize = WINDOW_SIZES[size]

      if (size === 'fullscreen') {
        setDimensions({
          width: baseSize.width,
          height: baseSize.height,
          maxWidth: baseSize.width,
          maxHeight: baseSize.height,
          top: '50%',
          left: '50%',
        })
        return
      }

      const screenWidth = window.innerWidth
      const screenHeight = window.innerHeight

      if (screenWidth < SCREEN_BREAKPOINT || screenHeight < BASE_SCREEN.height) {
        const scaleX = screenWidth / BASE_SCREEN.width
        const scaleY = screenHeight / BASE_SCREEN.height
        const scale = Math.min(scaleX, scaleY, 1)

        const scaledWidth = Math.round(parseInt(baseSize.width) * scale)
        const scaledHeight = Math.round(parseInt(baseSize.height) * scale)

        setDimensions({
          width: `${scaledWidth}px`,
          height: `${scaledHeight}px`,
          maxWidth: '95vw',
          maxHeight: '90vh',
          top: undefined,
          left: undefined,
        })
      } else {
        // Для больших экранов используем базовые размеры
        setDimensions({
          width: baseSize.width,
          height: baseSize.height,
          maxWidth: size === 'vertical' ? '70vw' : '95vw',
          maxHeight: '90vh',
          top: undefined,
          left: undefined,
        })
      }
    }

    updateDimensions()
    window.addEventListener('resize', updateDimensions)

    return () => window.removeEventListener('resize', updateDimensions)
  }, [size])

  return dimensions
}
