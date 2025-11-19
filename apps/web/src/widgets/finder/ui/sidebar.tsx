import { getFileIcon } from '../utils/file-icons'

interface SidebarProps {
  currentPath: string[]
  onNavigateTo: (path: string[]) => void
}

const FAVORITES = [
  { id: 'projects', name: 'Projects', path: [] },
]

export const Sidebar = ({ currentPath, onNavigateTo }: SidebarProps) => {
  return (
    <div className="w-56 h-full bg-finder-sidebar border-r border-finder-border flex flex-col">
      <div className="p-4 flex-1">
        <h3 className="text-sm font-semibold text-finder-text-secondary mb-4">Favorites</h3>
        <nav className="space-y-1">
          {FAVORITES.map(favorite => (
            <button
              key={favorite.id}
              onClick={() => onNavigateTo(favorite.path)}
              className={`w-full flex items-center px-3 py-2 text-left rounded-lg transition-colors duration-200 ${
                JSON.stringify(currentPath) === JSON.stringify(favorite.path)
                  ? 'bg-finder-active text-white'
                  : 'text-finder-text hover:bg-finder-hover'
              }`}
            >
              <img
                src={getFileIcon('folder')}
                alt={favorite.name}
                className="w-5 h-5 mr-3"
                onError={e => {
                  const target = e.target as HTMLImageElement
                  target.style.display = 'none'
                }}
              />
              <span className="font-medium">{favorite.name}</span>
            </button>
          ))}
        </nav>

        <div className="mt-8">
          <h3 className="text-sm font-semibold text-finder-text-secondary mb-4">Recent</h3>
          <div className="space-y-1">
            <div className="px-3 py-2 text-finder-text-secondary text-sm">No recent items</div>
          </div>
        </div>
      </div>
    </div>
  )
}
