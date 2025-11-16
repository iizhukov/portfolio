import { Launchpad } from './launchpad'
import { router } from '@shared/router'
import { useEffect, useState } from 'react'
import { modulesApi, SERVICE_APP_MAPPING } from '../api/modules'
import { notifyLocationChange } from '@shared/utils/location'

interface AppIcon {
  id: string
  name: string
  icon: string
  type: string
}

export const LaunchpadPage = () => {
  const [apps, setApps] = useState<AppIcon[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchApps = async () => {
      try {
        setLoading(true)
        const services = await modulesApi.listServices()
        
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

        const sortedApps = allApps.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))

        setApps(sortedApps)
      } catch (error) {
        console.error('Failed to fetch apps:', error)
        setApps([
          {
            id: 'settings',
            name: 'Settings',
            icon: '/assets/icons/settings.ico',
            type: 'settings',
          },
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchApps()
  }, [])

  const handleAppClick = (appId: string) => {
    const params = new URLSearchParams({ app: appId })
    const fullPath = `/window?${params.toString()}`
    router
      .push({ path: fullPath, params: {}, query: {}, method: 'push' })
      .then(() => notifyLocationChange())
      .catch(() => {
        window.location.href = fullPath
      })
  }

  if (loading) {
    return <div className="fixed inset-0 flex items-center justify-center text-white">Loading...</div>
  }

  return <Launchpad apps={apps} onAppClick={handleAppClick} />
}
