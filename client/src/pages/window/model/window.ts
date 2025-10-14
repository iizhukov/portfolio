export const MOCK_APPS = [
  {
    id: 'finder',
    name: 'Finder',
    icon: '/assets/icons/folder.ico',
    type: 'finder',
  },
  {
    id: 'notes',
    name: 'Notes',
    icon: '/assets/icons/notes.ico',
    type: 'notes',
  },
  {
    id: 'theme',
    name: 'Theme',
    icon: '/assets/icons/color_meter.ico',
    type: 'theme',
  },
]

export const WINDOW_SIZES = {
  standard: { width: '800px', height: '600px' },
  large: { width: '1200px', height: '800px' },
  vertical: { width: '500px', height: '800px' },
  fullscreen: { width: '95vw', height: '95vh' },
} as const
