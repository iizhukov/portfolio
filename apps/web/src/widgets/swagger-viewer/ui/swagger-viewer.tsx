import { useEffect, useState } from 'react'
import SwaggerUI from 'swagger-ui-react'
import { getFileUrl } from '@shared/utils/url'
import 'swagger-ui-react/swagger-ui.css'
import '../styles/swagger-viewer.css'

interface SwaggerViewerProps {
  url: string
  title?: string
}

export const SwaggerViewer = ({ url, title }: SwaggerViewerProps) => {
  const [specUrl, setSpecUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const loadSwaggerSpec = async () => {
      if (!url) {
        if (!cancelled) {
          setSpecUrl(null)
          setError('Swagger spec URL is missing')
          setLoading(false)
        }
        return
      }

      try {
        setLoading(true)
        setError(null)
        const fileUrl = getFileUrl(url)
        
        const response = await fetch(fileUrl, { method: 'HEAD' })
        if (!response.ok) {
          throw new Error(`Failed to load Swagger spec: ${response.statusText}`)
        }

        if (!cancelled) {
          setSpecUrl(fileUrl)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load Swagger documentation')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadSwaggerSpec()

    return () => {
      cancelled = true
    }
  }, [url])

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-window-bg text-window-text-secondary">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-window-text mx-auto mb-4"></div>
          <p>Loading Swagger documentation...</p>
        </div>
      </div>
    )
  }

  if (error || !specUrl) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-window-bg text-red-400">
        <div className="text-center">
          <p className="mb-2">Error loading Swagger documentation</p>
          <p className="text-sm text-window-text-secondary">{error ?? 'Failed to load Swagger documentation'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-full bg-window-bg flex flex-col">
      <div className="flex-1 overflow-auto bg-white swagger-viewer">
        <SwaggerUI url={specUrl} docExpansion="none" deepLinking />
      </div>
    </div>
  )
}

