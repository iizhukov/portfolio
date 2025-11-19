import { clsx } from 'clsx'
import { useWindowSize } from '../hooks/use-window-size'
import { Connections } from '@widgets/connections'
import { Settings } from '@widgets/settings'
import { Finder } from '@widgets/finder'
import { MarkdownViewer } from '@widgets/markdown-viewer'
import { DatabaseViewer } from '@widgets/database-viewer'
import { ArchitectureViewer } from '@widgets/architecture-viewer'
import { SwaggerViewer } from '@widgets/swagger-viewer'
import type { AppConfig } from '../types'

export type WindowSize =
  | 'standard' // (800x600px)
  | 'large' // (1200x800px)
  | 'vertical' // (600x800px)
  | 'fullscreen' // (95% x 95%)

interface WindowProps {
  app: AppConfig
  isActive: boolean
  onClose: () => void
  onMinimize: () => void
  onMaximize: () => void
  size: WindowSize
  className?: string
}

const CLOSING_SIZE = { width: '200px', height: '150px' }

const APPS_WITHOUT_MAXIMIZE: AppConfig['type'][] = ['connections']

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
  const canMaximize = !APPS_WITHOUT_MAXIMIZE.includes(app.type)

  return (
    <div
      className={clsx(
        'fixed bg-window-bg rounded-xl shadow-2xl flex flex-col overflow-hidden',
        {
          'opacity-100 pointer-events-auto': isActive,
          'opacity-0 pointer-events-none': !isActive,
        },
        className
      )}
      style={{
        visibility: isActive ? 'visible' : 'hidden',
        width: isActive ? dimensions.width : CLOSING_SIZE.width,
        height: isActive ? dimensions.height : CLOSING_SIZE.height,
        maxWidth: isActive ? dimensions.maxWidth : CLOSING_SIZE.width,
        maxHeight: isActive ? dimensions.maxHeight : CLOSING_SIZE.height,
        top: isActive ? (dimensions.top || '50%') : '50%',
        left: isActive ? (dimensions.left || '50%') : '50%',
        transform: dimensions.isMobile 
          ? (isActive ? 'none' : 'scale(0.9)') 
          : (isActive ? 'translate(-50%, -50%) scale(1)' : 'translate(-50%, -50%) scale(0.9)'),
        transition: isActive
          ? 'width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), height 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), max-width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), max-height 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.4s ease-out, transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)'
          : 'width 0.3s ease-in, height 0.3s ease-in, max-width 0.3s ease-in, max-height 0.3s ease-in, opacity 0.3s ease-in, transform 0.3s ease-in',
        willChange: 'width, height, max-width, max-height, transform, opacity',
      }}
    >
      {/* Window Header */}
      <div className="h-9 flex items-center px-2.5 gap-2 bg-window-header-bg border-b border-window-header-border relative">
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
            onClick={canMaximize ? onMaximize : undefined}
            className={clsx(
              'w-3 h-3 rounded-full bg-control-maximize transition-colors duration-200',
              {
                'hover:bg-control-maximize-hover cursor-pointer': canMaximize,
                'opacity-50 cursor-not-allowed': !canMaximize,
              }
            )}
            title="Maximize"
            disabled={!canMaximize}
          />
        </div>

        {/* Window Title - centered relative to entire window */}
        <span className="absolute left-1/2 transform -translate-x-1/2 font-medium text-sm text-window-text pointer-events-none">
          {app.name}
        </span>
      </div>

      {/* Window Content */}
      <div className="flex-1 flex overflow-hidden">
        <div
          className="w-full h-full"
          style={{
            opacity: isActive ? 1 : 0,
            transition: isActive 
              ? 'opacity 0.4s ease-out 0.1s' 
              : 'opacity 0.2s ease-in',
          }}
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
            <SwaggerViewer url={app.swagger || app.url || ''} title={app.name} />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-window-bg text-window-text">
              <p>Application type &quot;{app.type}&quot; is not supported</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
