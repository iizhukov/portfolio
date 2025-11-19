export const LAUNCHPAD_GRID_COLS = 7
export const LAUNCHPAD_GRID_COLS_MOBILE = 3
export const LAUNCHPAD_ICON_SIZE = 100
export const LAUNCHPAD_ICON_SIZE_MOBILE = 80
export const LAUNCHPAD_ICON_GAP = 80

export const LAUNCHPAD_CONTAINER = {
  maxWidth: '1200px',
  padding: '80px',
  gap: '80px',
} as const

export const LAUNCHPAD_RESPONSIVE = {
  small: {
    padding: '40px',
    maxWidth: '100%',
  },

  large: {
    padding: '80px',
    maxWidth: '1200px',
  },
} as const
