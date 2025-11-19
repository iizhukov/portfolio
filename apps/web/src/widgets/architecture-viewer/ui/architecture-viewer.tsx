import { useEffect, useState, lazy, Suspense, useRef } from 'react'
import { getFileUrl } from '@shared/utils/url'
import { validateExcalidrawJson } from '@shared/utils/validators'

const Excalidraw = lazy(async () => {
  await import('@excalidraw/excalidraw/index.css')
  const module = await import('@excalidraw/excalidraw')
  return { default: module.Excalidraw }
})

interface ArchitectureViewerProps {
  url: string
  title?: string
}

type ExcalidrawInitialData = Record<string, unknown>

export const ArchitectureViewer = ({ url, title }: ArchitectureViewerProps) => {
  const [initialData, setInitialData] = useState<ExcalidrawInitialData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [containerKey, setContainerKey] = useState(0)

  useEffect(() => {
    let cancelled = false

    const loadScene = async () => {
      try {
        setLoading(true)
        setError(null)

        const fileUrl = getFileUrl(url)
        const response = await fetch(fileUrl)
        if (!response.ok) {
          throw new Error(`Failed to load scene: ${response.statusText}`)
        }

        const json = await response.json()
        if (!cancelled) {
          const validation = validateExcalidrawJson(json)
          if (!validation.valid) {
            throw new Error(validation.error || 'Invalid Excalidraw file format')
          }
          setInitialData(json)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load architecture')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    if (url) {
      loadScene()
    } else {
      setError('Architecture file URL is missing')
      setLoading(false)
    }

    return () => {
      cancelled = true
    }
  }, [url])

  useEffect(() => {
    if (!containerRef.current) return

    const resizeObserver = new ResizeObserver(() => {
      setContainerKey(prev => prev + 1)
    })

    resizeObserver.observe(containerRef.current)

    return () => {
      resizeObserver.disconnect()
    }
  }, [])

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-window-bg text-window-text-secondary">
        Loading architecture...
      </div>
    )
  }

  if (error || !initialData) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-window-bg text-red-400">
        {error ?? 'Failed to render architecture'}
      </div>
    )
  }

  return (
    <div className="w-full h-full bg-window-bg flex flex-col overflow-hidden">
      <div ref={containerRef} className="flex-1 w-full h-full relative">
        <Suspense fallback={
          <div className="w-full h-full flex items-center justify-center bg-window-bg text-window-text-secondary">
            Loading Excalidraw...
          </div>
        }>
          <div className="w-full h-full absolute inset-0" key={containerKey}>
            <Excalidraw
              initialData={initialData}
              viewModeEnabled
              zenModeEnabled
              UIOptions={{
                canvasActions: {
                  changeViewBackgroundColor: false,
                  clearCanvas: false,
                  export: false,
                  loadScene: false,
                  saveToActiveFile: false,
                  toggleTheme: false,
                },
              }}
              renderTopRightUI={() => null}
            />
          </div>
        </Suspense>
      </div>
    </div>
  )
}

