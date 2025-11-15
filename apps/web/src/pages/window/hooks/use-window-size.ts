import { useState, useEffect } from 'react'
import { WINDOW_SIZES } from '../model/window'
import type { WindowSize } from '../ui/window'

const BASE_SCREEN = {
  width: 1440,
  height: 900,
}

const SCREEN_BREAKPOINT = 1440

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

  if (size === 'fullscreen' || typeof window === 'undefined') {
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

export const useWindowSize = (size: WindowSize) => {
  const [dimensions, setDimensions] = useState<WindowDimensions>(() => computeDimensions(size))

  useEffect(() => {
    const updateDimensions = () => {
      setDimensions(computeDimensions(size))
    }

    updateDimensions()
    window.addEventListener('resize', updateDimensions)

    return () => window.removeEventListener('resize', updateDimensions)
  }, [size])

  return dimensions
}
