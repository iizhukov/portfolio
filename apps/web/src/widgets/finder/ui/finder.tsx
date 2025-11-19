import { useFinder } from '../hooks/use-finder'
import { NavigationBar } from './navigation-bar'
import { Sidebar } from './sidebar'
import { FileGrid } from './file-grid'

export const Finder = () => {
  const {
    state,
    currentItems,
    allProjects,
    navigateToItem,
    navigateTo,
    goBack,
    goForward,
    goToRoot,
    toggleSelection,
    canGoBack,
    canGoForward,
    loading,
    error,
  } = useFinder()

  return (
    <div className="flex h-full bg-finder-bg">
      <div className="hidden md:block">
        <Sidebar
          currentPath={state.navigation.currentPath}
          onNavigateTo={path => {
            if (path.length === 0) {
              goToRoot()
            } else {
              navigateTo(path)
            }
          }}
        />
      </div>

      <div className="flex-1 flex flex-col">
        <NavigationBar
          canGoBack={canGoBack}
          canGoForward={canGoForward}
          currentPath={state.navigation.currentPath}
          projects={allProjects}
          onGoBack={goBack}
          onGoForward={goForward}
          onGoToRoot={goToRoot}
          onNavigateToPath={path => {
            if (path.length === 0) {
              goToRoot()
            } else {
              navigateTo(path)
            }
          }}
        />

        {loading ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-400">Loading projects...</p>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-red-400">Error loading projects: {error.message}</p>
          </div>
        ) : (
          <FileGrid
            items={currentItems}
            selectedItems={state.selectedItems}
            viewMode={state.viewMode}
            onItemClick={navigateToItem}
            onItemSelect={toggleSelection}
          />
        )}
      </div>
    </div>
  )
}
