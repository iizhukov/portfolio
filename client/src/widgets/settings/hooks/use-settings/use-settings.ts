import { useState, useEffect } from 'react'

export interface Settings {
  // Appearance
  wallpaper: 'big-sur-default' | 'dark-gradient' | 'code-pattern'
  theme: 'light' | 'dark' | 'auto'
  animations: boolean
  language: 'ru' | 'en'

  // Display
  resolution: 'default' | 'scaled'
  nightShift: boolean
  trueTone: boolean

  // Sound
  outputDevice: 'internal-speakers' | 'external-speakers' | 'bluetooth'
  notificationVolume: number
  balance: 'left' | 'center' | 'right'

  // Security
  fileVault: boolean
  firewall: boolean
  locationServices: boolean
}

const defaultSettings: Settings = {
  // Appearance
  wallpaper: 'big-sur-default',
  theme: 'auto',
  animations: true,
  language: 'en',

  // Display
  resolution: 'default',
  nightShift: false,
  trueTone: false,

  // Sound
  outputDevice: 'internal-speakers',
  notificationVolume: 50,
  balance: 'center',

  // Security
  fileVault: false,
  firewall: false,
  locationServices: false,
}

export const useSettings = () => {
  const [settings, setSettings] = useState<Settings>(defaultSettings)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('macos-settings')
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings)
        setSettings({ ...defaultSettings, ...parsed })
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    } finally {
      setIsLoaded(true)
    }
  }, [])

  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    const newSettings = { ...settings, [key]: value }
    setSettings(newSettings)

    try {
      localStorage.setItem('macos-settings', JSON.stringify(newSettings))
    } catch (error) {
      console.error('Failed to save settings:', error)
    }
  }

  const resetSettings = () => {
    setSettings(defaultSettings)
    try {
      localStorage.setItem('macos-settings', JSON.stringify(defaultSettings))
    } catch (error) {
      console.error('Failed to reset settings:', error)
    }
  }

  return {
    settings,
    updateSetting,
    resetSettings,
    isLoaded,
  }
}
