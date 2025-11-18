import type { AxiosResponseHeaders } from 'axios'

export interface ApiResponseHeaders {
  etag?: string
  'content-type'?: string
  'content-length'?: string
  'last-modified'?: string
}

export const getEtagFromHeaders = (
  headers: AxiosResponseHeaders | Record<string, unknown>
): string | undefined => {
  if (!headers || typeof headers !== 'object') {
    return undefined
  }

  const headersObj = headers as Record<string, unknown>
  
  const etag = 
    headersObj.etag ||
    headersObj.Etag ||
    headersObj.ETag ||
    headersObj['etag']
  
  return typeof etag === 'string' ? etag : undefined
}

