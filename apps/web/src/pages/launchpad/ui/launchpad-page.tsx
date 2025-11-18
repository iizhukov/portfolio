import { Launchpad } from './launchpad'
import { useMemo } from 'react'
import { SERVICE_APP_MAPPING } from '../api/modules'
import { useModules } from '@shared/api/hooks/use-modules'
import { navigateToWindow } from '@shared/utils/navigation'
import type { WindowQueryParams } from '@pages/window/types'

interface AppIcon {
  id: string
  name: string
  icon: string
  type: string
}

export const LaunchpadPage = () => {
  const { services, loading, error } = useModules()

  const apps = useMemo(() => {
    const appsFromServices: AppIcon[] = services
      .filter(service => SERVICE_APP_MAPPING[service.service_name])
      .map(service => {
        const mapping = SERVICE_APP_MAPPING[service.service_name]
        return {
          id: service.service_name,
          name: mapping.name,
          icon: mapping.icon,
          type: mapping.type,
        }
      })

    const allApps: AppIcon[] = [
      ...appsFromServices,
      {
        id: 'settings',
        name: 'Settings',
        icon: '/assets/icons/settings.ico',
        type: 'settings',
      },
    ]

    return allApps.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))
  }, [services])

  const handleAppClick = (appId: string) => {
    const params: WindowQueryParams = { app: appId }
    navigateToWindow(params)
  }

  if (loading && apps.length === 0) {
    return <div className="fixed inset-0 flex items-center justify-center text-white">Loading...</div>
  }

  if (error && apps.length === 0) {
    return (
      <div className="fixed inset-0 flex items-center justify-center text-white">
        <div className="text-center">
          <p className="text-red-400 mb-2">Failed to load apps</p>
          <p className="text-sm text-gray-400">{error.message}</p>
        </div>
      </div>
    )
  }

  return <Launchpad apps={apps} onAppClick={handleAppClick} />
}
