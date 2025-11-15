import { Button } from '@shared/ui/button'
import { type Project } from '../types/finder'
import { getFileIcon, getFolderIcon } from '../utils/file-icons'

interface NavigationBarProps {
  canGoBack: boolean
  canGoForward: boolean
  currentPath: string[]
  projects: Project[]
  onGoBack: () => void
  onGoForward: () => void
  onGoToRoot: () => void
  onNavigateToPath: (path: string[]) => void
}

export const NavigationBar = ({
  canGoBack,
  canGoForward,
  currentPath,
  projects,
  onGoBack,
  onGoForward,
  onNavigateToPath,
}: NavigationBarProps) => {
  const findProjectInTree = (projects: Project[], targetId: string): Project | null => {
    for (const project of projects) {
      if (project.id === targetId) {
        return project
      }
      if (project.children) {
        const found = findProjectInTree(project.children, targetId)
        if (found) {
          return found
        }
      }
    }
    return null
  }

  const getBreadcrumbItems = () => {
    const items = []

    items.push({
      id: 'root',
      name: 'Projects',
      path: [],
      icon: getFileIcon('folder'),
    })

    let currentLevel = projects
    for (let i = 0; i < currentPath.length; i++) {
      const pathId = currentPath[i]
      const item = findProjectInTree(currentLevel, pathId)

      if (item) {
        items.push({
          id: item.id,
          name: item.name,
          path: currentPath.slice(0, i + 1),
          icon:
            item.type === 'folder'
              ? getFolderIcon(!!item.children && item.children.length > 0)
              : getFileIcon(item.type, item.fileType),
        })

        if (item.children && item.children.length > 0) {
          currentLevel = item.children
        } else {
          break
        }
      } else {
        break
      }
    }

    return items
  }

  const breadcrumbItems = getBreadcrumbItems()
  return (
    <div className="flex items-center gap-2 p-3 bg-finder-toolbar border-b border-finder-border">
      <div className="flex gap-1">
        <Button
          variant="ghost"
          size="sm"
          onClick={onGoBack}
          disabled={!canGoBack}
          className="w-8 h-8 p-0"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onGoForward}
          disabled={!canGoForward}
          className="w-8 h-8 p-0"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Button>
      </div>

      <div className="flex-1 flex items-center">
        {breadcrumbItems.map((item, index) => (
          <div key={item.id} className="flex items-center">
            {index > 0 && <span className="mx-2 text-finder-text-secondary">/</span>}
            <button
              onClick={() => onNavigateToPath(item.path)}
              className="flex items-center gap-1 text-finder-text hover:text-finder-text-hover transition-colors duration-200"
            >
              {item.id === 'root' && (
                <img
                  src={item.icon}
                  alt={item.name}
                  className="w-4 h-4"
                  onError={e => {
                    const target = e.target as HTMLImageElement
                    target.src = getFileIcon('folder')
                  }}
                />
              )}
              <span className="font-medium">{item.name}</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
