import { clsx } from 'clsx'
import { LAUNCHPAD_ICON_SIZE, LAUNCHPAD_ICON_SIZE_MOBILE, LAUNCHPAD_GRID_COLS, LAUNCHPAD_GRID_COLS_MOBILE } from '../model/launchpad'
import { useLaunchpadLayout } from '../hooks/use-launchpad-layout'
import { useState, useEffect } from 'react'

interface AppIcon {
  id: string
  name: string
  icon: string
  type: string
}

interface LaunchpadProps {
  apps: AppIcon[]
  onAppClick: (appId: string) => void
  className?: string
}

export const Launchpad = ({ apps = [], onAppClick = () => {}, className }: LaunchpadProps) => {
  const layout = useLaunchpadLayout()
  const [isMobile, setIsMobile] = useState(() => window.innerWidth < 768)

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const gridCols = isMobile ? LAUNCHPAD_GRID_COLS_MOBILE : LAUNCHPAD_GRID_COLS
  const iconSize = isMobile ? LAUNCHPAD_ICON_SIZE_MOBILE : LAUNCHPAD_ICON_SIZE

  return (
    <div
      className={clsx('fixed inset-0 flex justify-center items-start z-10', className)}
      style={{
        padding: layout.padding,
      }}
    >
      <div
        className={`grid w-full text-white`}
        style={{
          gridTemplateColumns: `repeat(${gridCols}, 1fr)`,
          gap: `${layout.gap}px`,
          maxWidth: layout.maxWidth,
        }}
      >
        {apps.map(app => (
          <div
            key={app.id}
            className="text-center cursor-pointer animate-fade-in"
            onClick={() => onAppClick(app.id)}
          >
            <div className="icon-img">
              <img
                src={app.icon}
                alt={app.name}
                className="rounded-[20px] transition-transform duration-250 hover:scale-110 mx-auto"
                style={{ width: `${iconSize}px`, height: `${iconSize}px` }}
              />
            </div>
            <div className="mt-2 text-sm font-medium">{app.name}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
