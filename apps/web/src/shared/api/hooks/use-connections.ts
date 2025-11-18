import { connectionsApi } from '../connections'
import { useApiQuery } from './use-api-query'
import { CACHE_TTL } from '@shared/constants/cache'
import type { Connection, Status, Working, Image } from '../types/connections'

const CACHE_KEY_CONNECTIONS = 'connections:list'
const CACHE_KEY_STATUS = 'connections:status'
const CACHE_KEY_WORKING = 'connections:working'
const CACHE_KEY_IMAGE = 'connections:image'

export const useConnections = () => {
  const { data, loading, error } = useApiQuery<Connection[]>(
    CACHE_KEY_CONNECTIONS,
    (signal, config) => connectionsApi.getConnections({ ...config, signal }),
    { ttl: CACHE_TTL.DEFAULT }
  )

  return { connections: data ?? [], loading, error }
}

export const useStatus = () => {
  const { data, loading, error } = useApiQuery<Status>(
    CACHE_KEY_STATUS,
    (signal, config) => connectionsApi.getStatus({ ...config, signal }),
    { ttl: CACHE_TTL.DEFAULT }
  )

  return { status: data ?? null, loading, error }
}

export const useWorking = () => {
  const { data, loading, error } = useApiQuery<Working>(
    CACHE_KEY_WORKING,
    (signal, config) => connectionsApi.getWorking({ ...config, signal }),
    { ttl: CACHE_TTL.DEFAULT }
  )

  return { working: data ?? null, loading, error }
}

export const useImage = () => {
  const { data, loading, error } = useApiQuery<Image>(
    CACHE_KEY_IMAGE,
    (signal, config) => connectionsApi.getImage({ ...config, signal }),
    { ttl: CACHE_TTL.DEFAULT }
  )

  return { image: data ?? null, loading, error }
}

