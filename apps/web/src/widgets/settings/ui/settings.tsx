import { useState } from 'react'
import {
  useSettings,
  type Settings as SettingsType,
} from '@widgets/settings/hooks/use-settings/use-settings'
import { Toggle } from '@shared/ui/toggle'
import { Select, type SelectOption } from '@shared/ui/select'
import { Slider } from '@shared/ui/slider'

type SettingsSection = 'appearance' | 'display' | 'sound' | 'security'

const SECTIONS = [
  { id: 'appearance', label: 'Appearance', icon: '🎨' },
  { id: 'display', label: 'Display', icon: '🖥️' },
  { id: 'sound', label: 'Sound', icon: '🔊' },
  { id: 'security', label: 'Security', icon: '🔒' },
] as const

const WALLPAPER_OPTIONS: SelectOption[] = [
  { value: 'big-sur-default', label: 'Big Sur Default' },
  { value: 'dark-gradient', label: 'Dark Gradient' },
  { value: 'code-pattern', label: 'Code Pattern' },
]

const THEME_OPTIONS: SelectOption[] = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'auto', label: 'Auto' },
]

const LANGUAGE_OPTIONS: SelectOption[] = [
  { value: 'en', label: 'English' },
  { value: 'ru', label: 'Русский' },
]

const RESOLUTION_OPTIONS: SelectOption[] = [
  { value: 'default', label: 'Default' },
  { value: 'scaled', label: 'Scaled' },
]

const OUTPUT_DEVICE_OPTIONS: SelectOption[] = [
  { value: 'internal-speakers', label: 'Internal Speakers' },
  { value: 'external-speakers', label: 'External Speakers' },
  { value: 'bluetooth', label: 'Bluetooth' },
]

const BALANCE_OPTIONS: SelectOption[] = [
  { value: 'left', label: 'Left' },
  { value: 'center', label: 'Center' },
  { value: 'right', label: 'Right' },
]

export const Settings = () => {
  const { settings, updateSetting } = useSettings()
  const [activeSection, setActiveSection] = useState<SettingsSection>('appearance')

  const renderAppearance = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-settings-text mb-4">Wallpaper</h3>
        <Select
          options={WALLPAPER_OPTIONS}
          value={settings.wallpaper}
          onChange={value => updateSetting('wallpaper', value as SettingsType['wallpaper'])}
        />
      </div>

      <div>
        <h3 className="text-lg font-semibold text-settings-text mb-4">Theme</h3>
        <Select
          options={THEME_OPTIONS}
          value={settings.theme}
          onChange={value => updateSetting('theme', value as SettingsType['theme'])}
        />
      </div>

      <div>
        <h3 className="text-lg font-semibold text-settings-text mb-4">Language</h3>
        <Select
          options={LANGUAGE_OPTIONS}
          value={settings.language}
          onChange={value => updateSetting('language', value as SettingsType['language'])}
        />
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-settings-text">Animations</h3>
          <p className="text-sm text-settings-text-secondary">Enable smooth transitions</p>
        </div>
        <Toggle
          checked={settings.animations}
          onChange={checked => updateSetting('animations', checked)}
        />
      </div>
    </div>
  )

  const renderDisplay = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-settings-text mb-4">Resolution</h3>
        <Select
          options={RESOLUTION_OPTIONS}
          value={settings.resolution}
          onChange={value => updateSetting('resolution', value as SettingsType['resolution'])}
        />
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-settings-text">Night Shift</h3>
          <p className="text-sm text-settings-text-secondary">
            Automatically shift colors at night
          </p>
        </div>
        <Toggle
          checked={settings.nightShift}
          onChange={checked => updateSetting('nightShift', checked)}
        />
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-settings-text">True Tone</h3>
          <p className="text-sm text-settings-text-secondary">
            Adjust display based on ambient light
          </p>
        </div>
        <Toggle
          checked={settings.trueTone}
          onChange={checked => updateSetting('trueTone', checked)}
        />
      </div>
    </div>
  )

  const renderSound = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-settings-text mb-4">Output Device</h3>
        <Select
          options={OUTPUT_DEVICE_OPTIONS}
          value={settings.outputDevice}
          onChange={value => updateSetting('outputDevice', value as SettingsType['outputDevice'])}
        />
      </div>

      <div>
        <h3 className="text-lg font-semibold text-settings-text mb-4">Notification Volume</h3>
        <div className="space-y-2">
          <Slider
            value={settings.notificationVolume}
            onChange={value => updateSetting('notificationVolume', value)}
            min={0}
            max={100}
          />
          <p className="text-sm text-settings-text-secondary">{settings.notificationVolume}%</p>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-settings-text mb-4">Balance</h3>
        <Select
          options={BALANCE_OPTIONS}
          value={settings.balance}
          onChange={value => updateSetting('balance', value as SettingsType['balance'])}
        />
      </div>
    </div>
  )

  const renderSecurity = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-settings-text">FileVault</h3>
          <p className="text-sm text-settings-text-secondary">Encrypt your disk</p>
        </div>
        <Toggle
          checked={settings.fileVault}
          onChange={checked => updateSetting('fileVault', checked)}
        />
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-settings-text">Firewall</h3>
          <p className="text-sm text-settings-text-secondary">Block incoming connections</p>
        </div>
        <Toggle
          checked={settings.firewall}
          onChange={checked => updateSetting('firewall', checked)}
        />
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-settings-text">Location Services</h3>
          <p className="text-sm text-settings-text-secondary">Allow apps to access your location</p>
        </div>
        <Toggle
          checked={settings.locationServices}
          onChange={checked => updateSetting('locationServices', checked)}
        />
      </div>
    </div>
  )

  const renderContent = () => {
    switch (activeSection) {
      case 'appearance':
        return renderAppearance()
      case 'display':
        return renderDisplay()
      case 'sound':
        return renderSound()
      case 'security':
        return renderSecurity()
      default:
        return renderAppearance()
    }
  }

  return (
    <div className="flex h-full bg-settings-bg">
      <div className="w-64 bg-settings-sidebar-bg border-r border-settings-border">
        <div className="p-4">
          <h2 className="text-xl font-bold text-settings-text mb-6">Settings</h2>
          <nav className="space-y-1">
            {SECTIONS.map(section => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id as SettingsSection)}
                className={`w-full flex items-center px-3 py-2 text-left rounded-lg transition-colors duration-200 ${
                  activeSection === section.id
                    ? 'bg-settings-active text-white'
                    : 'text-settings-text hover:bg-settings-hover'
                }`}
              >
                <span className="text-lg mr-3">{section.icon}</span>
                <span className="font-medium">{section.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-2xl">
          <h1 className="text-2xl font-bold text-settings-text mb-2">
            {SECTIONS.find(s => s.id === activeSection)?.label}
          </h1>
          <p className="text-settings-text-secondary mb-8">
            Customize your {SECTIONS.find(s => s.id === activeSection)?.label.toLowerCase()}{' '}
            preferences
          </p>

          {renderContent()}
        </div>
      </div>
    </div>
  )
}
