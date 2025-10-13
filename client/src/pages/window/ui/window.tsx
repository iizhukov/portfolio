import { clsx } from 'clsx'
import { useWindowSize } from '../hooks/use-window-size'

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
        'fixed bg-white dark:bg-gray-900 rounded-xl shadow-2xl flex flex-col overflow-hidden transition-all duration-500 ease-out',
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
        transition: 'all 0.5s ease-out',
      }}
    >
      {/* Window Header */}
      <div className="h-9 flex items-center px-2.5 gap-2 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        {/* Window Controls */}
        <div className="flex gap-2">
          <button
            onClick={onClose}
            className="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-all duration-200 cursor-pointer hover:scale-110"
            title="Close"
          />
          <button
            onClick={onMinimize}
            className="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-all duration-200 cursor-pointer hover:scale-110"
            title="Minimize"
          />
          <button
            onClick={onMaximize}
            className="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-all duration-200 cursor-pointer hover:scale-110"
            title="Maximize"
          />
        </div>

        {/* Window Title */}
        <span className="flex-1 text-center font-medium text-sm text-gray-700 dark:text-gray-300">
          {app.name}
        </span>
      </div>

      {/* Window Content */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex items-center justify-center">
          <div
            className={clsx('text-center transition-all duration-700 delay-200', {
              'opacity-100 translate-y-0': isActive,
              'opacity-0 translate-y-4': !isActive,
            })}
          >
            <h2 className="text-2xl font-bold mb-4">{app.name}</h2>
            <p className="text-gray-600 dark:text-gray-400">App content will be here</p>
          </div>
        </div>
      </div>
    </div>
  )
}
