import { useState, useEffect } from 'react'
import { LAUNCHPAD_CONTAINER, LAUNCHPAD_RESPONSIVE } from '../model/launchpad'

const BREAKPOINTS = {
  small: 1440,
  large: 1600,
} as const

export const useLaunchpadLayout = () => {
  const [layout, setLayout] = useState(() => {
    const screenWidth = window.innerWidth

    const isLargeScreen = screenWidth > BREAKPOINTS.small

    return {
      maxWidth: isLargeScreen
        ? LAUNCHPAD_RESPONSIVE.large.maxWidth
        : LAUNCHPAD_RESPONSIVE.small.maxWidth,
      padding: isLargeScreen
        ? LAUNCHPAD_RESPONSIVE.large.padding
        : LAUNCHPAD_RESPONSIVE.small.padding,
      gap: LAUNCHPAD_CONTAINER.gap,
      isLargeScreen,
    }
  })

  useEffect(() => {
    const updateLayout = () => {
      const screenWidth = window.innerWidth
      const isLargeScreen = screenWidth > BREAKPOINTS.small

      setLayout({
        maxWidth: isLargeScreen
          ? LAUNCHPAD_RESPONSIVE.large.maxWidth
          : LAUNCHPAD_RESPONSIVE.small.maxWidth,
        padding: isLargeScreen
          ? LAUNCHPAD_RESPONSIVE.large.padding
          : LAUNCHPAD_RESPONSIVE.small.padding,
        gap: LAUNCHPAD_CONTAINER.gap,
        isLargeScreen,
      })
    }

    updateLayout()
    window.addEventListener('resize', updateLayout)

    return () => window.removeEventListener('resize', updateLayout)
  }, [])

  return layout
}
