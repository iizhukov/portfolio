export const MOCK_APPS = [
  {
    id: 'finder',
    name: 'Projects',
    icon: '/assets/icons/wpaper_folder.ico',
    type: 'finder',
  },
  {
    id: 'discord',
    name: 'Connections',
    icon: '/assets/icons/discord.ico',
    type: 'discord',
  },
  {
    id: 'settings',
    name: 'Settings',
    icon: '/assets/icons/settings.ico',
    type: 'settings',
  },
]

export const LAUNCHPAD_GRID_COLS = 7
export const LAUNCHPAD_ICON_SIZE = 100
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
