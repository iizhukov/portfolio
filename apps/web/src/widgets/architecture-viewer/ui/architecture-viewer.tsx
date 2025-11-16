import { useEffect, useState, lazy, Suspense } from 'react'

const Excalidraw = lazy(async () => {
  await import('@excalidraw/excalidraw/index.css')
  const module = await import('@excalidraw/excalidraw')
  return { default: module.Excalidraw }
})

interface ArchitectureViewerProps {
  url: string
  title?: string
}

type ExcalidrawInitialData = any

export const ArchitectureViewer = ({ url, title }: ArchitectureViewerProps) => {
  const [initialData, setInitialData] = useState<ExcalidrawInitialData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const loadScene = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(url)
        if (!response.ok) {
          throw new Error(`Failed to load scene: ${response.statusText}`)
        }

        const json = await response.json()
        if (!cancelled) {
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
    <div className="w-full h-full bg-window-bg flex flex-col">
      {title && (
        <div className="px-6 py-4 border-b border-window-header-border text-window-text text-xl font-semibold">
          {title}
        </div>
      )}
      <div className="flex-1">
        <Suspense fallback={
          <div className="w-full h-full flex items-center justify-center bg-window-bg text-window-text-secondary">
            Loading Excalidraw...
          </div>
        }>
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
        </Suspense>
      </div>
    </div>
  )
}

