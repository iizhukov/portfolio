import { type Project } from '../types/finder'
import { getFileIcon, getFolderIcon } from '../utils/file-icons'

interface FileGridProps {
  items: Project[]
  selectedItems: string[]
  viewMode: 'grid' | 'list'
  onItemClick: (item: Project) => void
  onItemSelect: (itemId: string) => void
}

export const FileGrid = ({
  items,
  selectedItems,
  viewMode,
  onItemClick,
  onItemSelect,
}: FileGridProps) => {
  const handleItemClick = (item: Project, event: React.MouseEvent) => {
    if (event.ctrlKey || event.metaKey) {
      onItemSelect(item.id)
    } else {
      onItemClick(item)
    }
  }

  const handleItemDoubleClick = (item: Project) => {
    onItemClick(item)
  }

  if (viewMode === 'list') {
    return (
      <div className="flex-1 p-4">
        <div className="space-y-1">
          {items.map(item => (
            <div
              key={item.id}
              onClick={e => handleItemClick(item, e)}
              onDoubleClick={() => handleItemDoubleClick(item)}
              className={`flex items-center p-2 rounded-lg cursor-pointer transition-colors duration-200 ${
                selectedItems.includes(item.id)
                  ? 'bg-finder-active text-white'
                  : 'hover:bg-finder-hover'
              }`}
            >
              <img
                src={
                  item.type === 'folder'
                    ? getFolderIcon(!!item.children && item.children.length > 0)
                    : getFileIcon(item.type, item.fileType)
                }
                alt={item.name}
                className="w-6 h-6 mr-3"
                onError={e => {
                  const target = e.target as HTMLImageElement
                  target.style.display = 'none'
                  const parent = target.parentElement
                  if (parent) {
                    const emoji = document.createElement('span')
                    emoji.className = 'text-2xl mr-3'
                    emoji.textContent = item.icon
                    parent.insertBefore(emoji, target)
                  }
                }}
              />
              <div className="flex-1">
                <div className="font-medium">{item.name}</div>
                <div className="text-sm text-finder-text-secondary">
                  {item.type === 'folder' ? 'Folder' : 'File'}
                </div>
              </div>
              {item.type === 'folder' && (
                <svg
                  className="w-4 h-4 text-finder-text-secondary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 p-4">
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {items.map(item => (
          <div
            key={item.id}
            onClick={e => handleItemClick(item, e)}
            onDoubleClick={() => handleItemDoubleClick(item)}
            className={`flex flex-col items-center p-3 rounded-lg cursor-pointer transition-all duration-200 hover:scale-105 ${
              selectedItems.includes(item.id)
                ? 'bg-finder-active text-white'
                : 'hover:bg-finder-hover'
            }`}
          >
            <img
              src={
                item.type === 'folder'
                  ? getFolderIcon(!!item.children && item.children.length > 0)
                  : getFileIcon(item.type, item.fileType)
              }
              alt={item.name}
              className="w-12 h-12 mb-2"
              onError={e => {
                const target = e.target as HTMLImageElement
                target.style.display = 'none'
                const parent = target.parentElement
                if (parent) {
                  const emoji = document.createElement('div')
                  emoji.className = 'text-4xl mb-2'
                  emoji.textContent = item.icon
                  parent.insertBefore(emoji, target)
                }
              }}
            />
            <div className="text-center">
              <div className="text-sm font-medium truncate w-full">{item.name}</div>
              <div className="text-xs text-finder-text-secondary mt-1">
                {item.type === 'folder' ? 'Folder' : 'File'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
