import { modulesApi } from '@shared/api/modules'
import { apiCache } from '@shared/api/cache'
import { ApiErrorHandler } from '@shared/api/error-handler'
import type { ServiceInfo } from '@shared/api/types/modules'

const CACHE_TTL = 5 * 60 * 1000

export const SERVICE_APP_MAPPING: Record<string, { icon: string; type: string; name: string }> = {
  projects: {
    icon: '/assets/icons/wpaper_folder.ico',
    type: 'finder',
    name: 'Projects',
  },
  connections: {
    icon: '/assets/icons/discord.ico',
    type: 'connections',
    name: 'Connections',
  },
  swagger: {
    icon: '/assets/icons/swagger.ico',
    type: 'swagger',
    name: 'Swagger',
  },
}

export const fetchServices = async (): Promise<ServiceInfo[]> => {
  const cacheKey = 'modules:services'
  const cached = apiCache.get<ServiceInfo[]>(cacheKey)
  if (cached) {
    return cached
  }

  try {
    const response = await modulesApi.listServices()
    const etag = response.headers?.['etag'] as string | undefined
    apiCache.set(cacheKey, response.data, undefined, { ttl: CACHE_TTL }, etag)
    return response.data
  } catch (err) {
    ApiErrorHandler.handleError(err)
    throw err
  }
}

