import { useState, useEffect } from 'react'
import { WINDOW_SIZES } from '../model/window'
import type { WindowSize } from '../ui/window'
import { SCREEN_DIMENSIONS } from '../constants/screen'
import { isBrowser } from '@shared/utils/browser'

const BASE_SCREEN = {
  width: SCREEN_DIMENSIONS.BASE_WIDTH,
  height: SCREEN_DIMENSIONS.BASE_HEIGHT,
}

const SCREEN_BREAKPOINT = SCREEN_DIMENSIONS.BREAKPOINT

type WindowDimensions = {
  width: string
  height: string
  maxWidth: string
  maxHeight: string
  top?: string
  left?: string
}

const computeDimensions = (size: WindowSize): WindowDimensions => {
  const baseSize = WINDOW_SIZES[size]

  if (size === 'fullscreen' || !isBrowser) {
    return {
      width: baseSize.width,
      height: baseSize.height,
      maxWidth: baseSize.width,
      maxHeight: baseSize.height,
      top: size === 'fullscreen' ? '50%' : undefined,
      left: size === 'fullscreen' ? '50%' : undefined,
    }
  }

  const screenWidth = window.innerWidth
  const screenHeight = window.innerHeight

  if (screenWidth < SCREEN_BREAKPOINT || screenHeight < BASE_SCREEN.height) {
    const scaleX = screenWidth / BASE_SCREEN.width
    const scaleY = screenHeight / BASE_SCREEN.height
    const scale = Math.min(scaleX, scaleY, 1)

    const scaledWidth = Math.round(parseInt(baseSize.width) * scale)
    const scaledHeight = Math.round(parseInt(baseSize.height) * scale)

    return {
      width: `${scaledWidth}px`,
      height: `${scaledHeight}px`,
      maxWidth: `${scaledWidth}px`,
      maxHeight: `${scaledHeight}px`,
      top: undefined,
      left: undefined,
    }
  }

  return {
    width: baseSize.width,
    height: baseSize.height,
    maxWidth: baseSize.width,
    maxHeight: baseSize.height,
    top: undefined,
    left: undefined,
  }
}

const RESIZE_DEBOUNCE_DELAY = 150

export const useWindowSize = (size: WindowSize) => {
  const [dimensions, setDimensions] = useState<WindowDimensions>(() => computeDimensions(size))

  useEffect(() => {
    if (!isBrowser) return

    let timeoutId: ReturnType<typeof setTimeout> | undefined

    const updateDimensions = () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
      timeoutId = setTimeout(() => {
        setDimensions(computeDimensions(size))
      }, RESIZE_DEBOUNCE_DELAY)
    }

    setDimensions(computeDimensions(size))
    
    window.addEventListener('resize', updateDimensions)

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
      window.removeEventListener('resize', updateDimensions)
    }
  }, [size])

  return dimensions
}
