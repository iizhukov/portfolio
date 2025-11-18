import { useState, useEffect } from 'react'
import { STORAGE_KEYS } from '@shared/constants/storage'
import { safeJsonParse } from '@shared/utils/safe-json'
import { isBrowser } from '@shared/utils/browser'

export interface Settings {
  wallpaper: 'big-sur-default' | 'dark-gradient' | 'code-pattern'
  theme: 'light' | 'dark' | 'auto'
  animations: boolean
  language: 'ru' | 'en'
  resolution: 'default' | 'scaled'
  nightShift: boolean
  trueTone: boolean
  outputDevice: 'internal-speakers' | 'external-speakers' | 'bluetooth'
  notificationVolume: number
  balance: 'left' | 'center' | 'right'
  fileVault: boolean
  firewall: boolean
  locationServices: boolean
}

const defaultSettings: Settings = {
  wallpaper: 'big-sur-default',
  theme: 'auto',
  animations: true,
  language: 'en',
  resolution: 'default',
  nightShift: false,
  trueTone: false,
  outputDevice: 'internal-speakers',
  notificationVolume: 50,
  balance: 'center',
  fileVault: false,
  firewall: false,
  locationServices: false,
}

export const useSettings = () => {
  const [settings, setSettings] = useState<Settings>(defaultSettings)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    if (!isBrowser) {
      setIsLoaded(true)
      return
    }

    try {
      const savedSettings = localStorage.getItem(STORAGE_KEYS.SETTINGS)
      if (savedSettings) {
        const parsed = safeJsonParse<Partial<Settings>>(savedSettings, {})
        setSettings({ ...defaultSettings, ...parsed })
      }
    } catch (error) {
      if (error instanceof DOMException) {
        if (error.name === 'QuotaExceededError') {
          console.error('LocalStorage quota exceeded. Clearing old data...')
        } else if (error.name === 'SecurityError') {
          console.error('LocalStorage access denied')
        }
      } else {
        console.error('Error loading settings:', error)
      }
    } finally {
      setIsLoaded(true)
    }
  }, [])

  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    if (!isBrowser) return

    const newSettings = { ...settings, [key]: value }
    setSettings(newSettings)

    try {
      localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(newSettings))
    } catch (error) {
      if (error instanceof DOMException) {
        if (error.name === 'QuotaExceededError') {
          console.error('LocalStorage quota exceeded. Cannot save settings.')
        } else if (error.name === 'SecurityError') {
          console.error('LocalStorage access denied')
        }
      } else {
        console.error('Error saving settings:', error)
      }
    }
  }

  const resetSettings = () => {
    if (!isBrowser) return

    setSettings(defaultSettings)
    try {
      localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(defaultSettings))
    } catch (error) {
      if (error instanceof DOMException) {
        if (error.name === 'QuotaExceededError') {
          console.error('LocalStorage quota exceeded. Cannot reset settings.')
        } else if (error.name === 'SecurityError') {
          console.error('LocalStorage access denied')
        }
      } else {
        console.error('Error resetting settings:', error)
      }
    }
  }

  return {
    settings,
    updateSetting,
    resetSettings,
    isLoaded,
  }
}
