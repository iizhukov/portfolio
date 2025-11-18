import { CACHE_TTL, MAX_CACHE_SIZE } from '@shared/constants/cache'

interface CacheEntry<T> {
  data: T
  timestamp: number
  etag?: string
}

interface CacheOptions {
  ttl?: number
  key?: string
}

class ApiCache {
  private cache = new Map<string, CacheEntry<unknown>>()
  private readonly defaultTTL = CACHE_TTL.DEFAULT

  private generateKey(url: string, params?: Record<string, unknown>): string {
    if (!params || Object.keys(params).length === 0) {
      return url
    }
    const sortedParams = Object.keys(params)
      .sort()
      .map(key => `${key}=${JSON.stringify(params[key])}`)
      .join('&')
    return `${url}?${sortedParams}`
  }

  private isExpired(entry: CacheEntry<unknown>, ttl: number): boolean {
    return Date.now() - entry.timestamp > ttl
  }

  private hasDataChanged(newEtag: string | undefined, cachedEtag: string | undefined): boolean {
    if (!newEtag || !cachedEtag) return true
    return newEtag !== cachedEtag
  }

  get<T>(url: string, params?: Record<string, unknown>, options?: CacheOptions): T | null {
    const key = options?.key || this.generateKey(url, params)
    const entry = this.cache.get(key) as CacheEntry<T> | undefined

    if (!entry) {
      return null
    }

    const ttl = options?.ttl ?? this.defaultTTL
    if (this.isExpired(entry, ttl)) {
      this.cache.delete(key)
      return null
    }

    return entry.data
  }

  getEtag(url: string, params?: Record<string, unknown>, options?: CacheOptions): string | undefined {
    const key = options?.key || this.generateKey(url, params)
    const entry = this.cache.get(key) as CacheEntry<unknown> | undefined

    if (!entry) {
      return undefined
    }

    const ttl = options?.ttl ?? this.defaultTTL
    if (this.isExpired(entry, ttl)) {
      return undefined
    }

    return entry.etag
  }

  set<T>(
    url: string,
    data: T,
    params?: Record<string, unknown>,
    options?: CacheOptions,
    etag?: string
  ): void {
    const key = options?.key || this.generateKey(url, params)
    const cachedEntry = this.cache.get(key) as CacheEntry<T> | undefined

    if (cachedEntry) {
      if (etag && cachedEntry.etag && !this.hasDataChanged(etag, cachedEntry.etag)) {
        cachedEntry.timestamp = Date.now()
        return
      }

      const dataString = JSON.stringify(data)
      const cachedDataString = JSON.stringify(cachedEntry.data)

      if (dataString === cachedDataString) {
        cachedEntry.timestamp = Date.now()
        if (etag) {
          cachedEntry.etag = etag
        }
        return
      }
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      etag,
    })

    if (this.cache.size > MAX_CACHE_SIZE) {
      const entries = Array.from(this.cache.entries())
        .sort((a, b) => a[1].timestamp - b[1].timestamp)
      const toDelete = entries.slice(0, entries.length - MAX_CACHE_SIZE)
      toDelete.forEach(([keyToDelete]) => this.cache.delete(keyToDelete))
    }
  }

  invalidate(pattern?: string | RegExp): void {
    if (!pattern) {
      this.cache.clear()
      return
    }

    const regex = typeof pattern === 'string' 
      ? new RegExp(pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
      : pattern

    const keysToDelete: string[] = []
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        keysToDelete.push(key)
      }
    }
    keysToDelete.forEach(key => this.cache.delete(key))
  }

  clear(): void {
    this.cache.clear()
  }
}

export const apiCache = new ApiCache()

