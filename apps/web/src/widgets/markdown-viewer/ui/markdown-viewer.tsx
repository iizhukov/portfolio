import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeRaw from 'rehype-raw'
import '../styles/github-dark.css'
import './markdown-viewer.css'

interface MarkdownViewerProps {
  url: string
  title?: string
}

export const MarkdownViewer = ({ url, title }: MarkdownViewerProps) => {
  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMarkdown = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await fetch(url)
        
        if (!response.ok) {
          throw new Error(`Failed to fetch markdown: ${response.statusText}`)
        }
        
        const text = await response.text()
        setContent(text)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load markdown')
      } finally {
        setLoading(false)
      }
    }

    if (url) {
      fetchMarkdown()
    }
  }, [url])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-window-bg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-window-text mx-auto mb-4"></div>
          <p className="text-window-text-secondary">Loading markdown...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-window-bg">
        <div className="text-center">
          <p className="text-red-500 mb-2">Error loading markdown</p>
          <p className="text-window-text-secondary text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full w-full overflow-auto bg-window-bg">
      <div className="max-w-4xl mx-auto p-8">
        {title && (
          <h1 className="text-3xl font-bold mb-6 text-window-text">{title}</h1>
        )}
        <div className="markdown-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw, rehypeHighlight]}
          >
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  )
}

