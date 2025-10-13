import { clsx } from 'clsx'
import { LAUNCHPAD_ICON_SIZE, LAUNCHPAD_GRID_COLS } from '../model/launchpad'
import { useLaunchpadLayout } from '../hooks/use-launchpad-layout'

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
          gridTemplateColumns: `repeat(${LAUNCHPAD_GRID_COLS}, 1fr)`,
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
                style={{ width: `${LAUNCHPAD_ICON_SIZE}px`, height: `${LAUNCHPAD_ICON_SIZE}px` }}
              />
            </div>
            <div className="mt-2 text-sm font-medium">{app.name}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
