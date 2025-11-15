import { clsx } from 'clsx'
import { useWindowSize } from '../hooks/use-window-size'
import { Connections } from '@widgets/connections'
import { Settings } from '@widgets/settings'
import { Finder } from '@widgets/finder'
import { MarkdownViewer } from '@widgets/markdown-viewer'
import { DatabaseViewer } from '@widgets/database-viewer'
import { ArchitectureViewer } from '@widgets/architecture-viewer'
import { SwaggerViewer } from '@widgets/swagger-viewer'

export type WindowSize =
  | 'standard' // (800x600px)
  | 'large' // (1200x800px)
  | 'vertical' // (600x800px)
  | 'fullscreen' // (95% x 95%)

interface App {
  id: string
  name: string
  icon: string
  type: string
  url?: string
  dbml?: string
  excalidraw?: string
  swagger?: string
}

interface WindowProps {
  app: App
  isActive: boolean
  onClose: () => void
  onMinimize: () => void
  onMaximize: () => void
  size: WindowSize
  className?: string
}

export const Window = ({
  app,
  isActive,
  onClose,
  onMinimize,
  onMaximize,
  size,
  className,
}: WindowProps) => {
  const dimensions = useWindowSize(size)

  return (
    <div
      className={clsx(
        'fixed bg-window-bg rounded-xl shadow-2xl flex flex-col overflow-hidden transition-all duration-500 ease-out',
        {
          'opacity-100 scale-100': isActive,
          'opacity-0 scale-95 pointer-events-none': !isActive,
        },
        className
      )}
      style={{
        visibility: isActive ? 'visible' : 'hidden',
        width: dimensions.width,
        height: dimensions.height,
        maxWidth: dimensions.maxWidth,
        maxHeight: dimensions.maxHeight,
        top: dimensions.top || '50%',
        left: dimensions.left || '50%',
        transform: 'translate(-50%, -50%)',
        transition: 'width 0.4s ease-out, height 0.4s ease-out, opacity 0.3s ease-out, transform 0.3s ease-out',
        willChange: 'width, height, transform',
      }}
    >
      {/* Window Header */}
      <div className="h-9 flex items-center px-2.5 gap-2 bg-window-header-bg border-b border-window-header-border">
        {/* Window Controls */}
        <div className="flex gap-2">
          <button
            onClick={onClose}
            className="w-3 h-3 rounded-full bg-control-close hover:bg-control-close-hover transition-colors duration-200 cursor-pointer"
            title="Close"
          />
          <button
            onClick={onMinimize}
            className="w-3 h-3 rounded-full bg-control-minimize hover:bg-control-minimize-hover transition-colors duration-200 cursor-pointer"
            title="Minimize"
          />
          <button
            onClick={onMaximize}
            className="w-3 h-3 rounded-full bg-control-maximize hover:bg-control-maximize-hover transition-colors duration-200 cursor-pointer"
            title="Maximize"
          />
        </div>

        {/* Window Title */}
        <span className="flex-1 text-center font-medium text-sm text-window-text">{app.name}</span>
      </div>

      {/* Window Content */}
      <div className="flex-1 flex overflow-hidden">
        <div
          className={clsx('w-full h-full transition-opacity', {
            'duration-300 opacity-100': isActive,
            'duration-100 opacity-0': !isActive,
          })}
        >
          {app.type === 'settings' ? (
            <Settings />
          ) : app.type === 'finder' ? (
            <Finder />
          ) : app.type === 'connections' ? (
            <Connections />
          ) : app.type === 'markdown-viewer' ? (
            <MarkdownViewer url={app.url || ''} title={app.name} />
          ) : app.type === 'database' ? (
            <DatabaseViewer url={app.dbml || ''} title={app.name} />
          ) : app.type === 'architecture' ? (
            <ArchitectureViewer url={app.excalidraw || ''} title={app.name} />
          ) : app.type === 'swagger' ? (
            <SwaggerViewer url={app.swagger || ''} title={app.name} />
          ) : (
            <Connections />
          )}
        </div>
      </div>
    </div>
  )
}
