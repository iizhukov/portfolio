import { useState, useEffect, useRef } from 'react'
import type { AxiosResponse, AxiosRequestConfig } from 'axios'
import { apiCache } from '../cache'
import { ApiErrorHandler } from '../error-handler'
import { getEtagFromHeaders } from '../types/headers'
import { CACHE_TTL } from '@shared/constants/cache'

interface UseApiQueryOptions {
  enabled?: boolean
  ttl?: number
  staleTime?: number
}

export function useApiQuery<T>(
  queryKey: string,
  queryFn: (signal: AbortSignal, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>,
  options?: UseApiQueryOptions
) {
  const [data, setData] = useState<T | null>(() => {
    if (options?.enabled !== false) {
      const cached = apiCache.get<T>(queryKey, undefined, { key: queryKey })
      if (cached) {
        return cached
      }
    }
    return null
  })
  const [loading, setLoading] = useState(() => {
    if (options?.enabled === false) {
      return false
    }
    const cached = apiCache.get<T>(queryKey, undefined, { key: queryKey })
    return !cached
  })
  const [error, setError] = useState<Error | null>(null)
  
  const queryFnRef = useRef(queryFn)
  queryFnRef.current = queryFn

  useEffect(() => {
    if (options?.enabled === false) {
      setLoading(false)
      return
    }

    const abortController = new AbortController()
    let isMounted = true

    const fetchData = async () => {
      const cached = apiCache.get<T>(queryKey, undefined, { key: queryKey })
      const cachedEtag = apiCache.getEtag(queryKey, undefined, { key: queryKey })
      
      if (cached && isMounted) {
        setData(cached)
        setLoading(false)
      }

      const requestConfig: AxiosRequestConfig = {
        signal: abortController.signal,
      }
      
      if (cachedEtag) {
        requestConfig.headers = {
          'If-None-Match': cachedEtag,
        }
      }

      try {
        if (!cached && isMounted) {
          setLoading(true)
          setError(null)
        }
        
        const response = await queryFnRef.current(abortController.signal, requestConfig)
        
        if (abortController.signal.aborted || !isMounted) {
          return
        }

        if (response.status === 304) {
          return
        }

        const etag = getEtagFromHeaders(response.headers)
        const newData = response.data
        
        const dataChanged = !cached || JSON.stringify(cached) !== JSON.stringify(newData)
        
        apiCache.set(
          queryKey,
          newData,
          undefined,
          { key: queryKey, ttl: options?.ttl ?? CACHE_TTL.DEFAULT },
          etag
        )
        
        if (isMounted && (dataChanged || !cached)) {
          setData(newData)
        }
      } catch (err) {
        if (abortController.signal.aborted || !isMounted) {
          return
        }

        if (err && typeof err === 'object') {
          const axiosError = err as { code?: string; message?: string; name?: string; response?: { status?: number } }
          
          if (axiosError.response?.status === 304) {
            return
          }
          
          if (
            axiosError.code === 'ERR_CANCELED' ||
            axiosError.message === 'canceled' ||
            axiosError.name === 'AbortError' ||
            axiosError.name === 'CanceledError'
          ) {
            return
          }
        }
        
        const apiError = ApiErrorHandler.handleError(err)
        if (apiError.code !== 'CANCELED' && isMounted) {
          setError(new Error(apiError.message))
          if (cached) {
            setLoading(false)
          }
        }
      } finally {
        if (!abortController.signal.aborted && isMounted) {
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      isMounted = false
      abortController.abort()
    }
  }, [queryKey, options?.enabled, options?.ttl])

  return { data, loading, error }
}

