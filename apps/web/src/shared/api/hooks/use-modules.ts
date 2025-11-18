import { useMemo } from 'react'
import { modulesApi } from '../modules'
import { useApiQuery } from './use-api-query'
import { CACHE_TTL } from '@shared/constants/cache'
import type { ServiceInfo } from '../types/modules'

const CACHE_KEY_SERVICES = 'modules:services'

export const useModules = () => {
  const { data, loading, error } = useApiQuery<ServiceInfo[]>(
    CACHE_KEY_SERVICES,
    (signal, config) => modulesApi.listServices({ ...config, signal }),
    { ttl: CACHE_TTL.DEFAULT }
  )

  return { services: data ?? [], loading, error }
}

