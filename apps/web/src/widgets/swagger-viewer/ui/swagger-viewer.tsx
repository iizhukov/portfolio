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
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (url) {
      setSpecUrl(getFileUrl(url))
      setError(null)
    } else {
      setSpecUrl(null)
      setError('Swagger spec URL is missing')
    }
  }, [url])

  if (error || !specUrl) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-window-bg text-red-400">
        {error ?? 'Failed to load Swagger documentation'}
      </div>
    )
  }

  return (
    <div className="w-full h-full bg-window-bg flex flex-col">
      {title && (
        <div className="px-6 py-4 border-b border-window-header-border text-window-text text-xl font-semibold">
          {title}
        </div>
      )}
      <div className="flex-1 overflow-auto bg-white swagger-viewer">
        <SwaggerUI url={specUrl} docExpansion="none" deepLinking />
      </div>
    </div>
  )
}

