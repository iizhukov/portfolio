import { useFinder } from '../hooks/use-finder'
import { NavigationBar } from './navigation-bar'
import { Sidebar } from './sidebar'
import { FileGrid } from './file-grid'
import { PROJECTS_DATA } from '../models/projects'

export const Finder = () => {
  const {
    state,
    currentItems,
    navigateToItem,
    navigateTo,
    goBack,
    goForward,
    goToRoot,
    toggleSelection,
    // getPathString,
    canGoBack,
    canGoForward,
  } = useFinder()

  return (
    <div className="flex h-full bg-finder-bg">
      {/* Sidebar */}
      <Sidebar
        currentPath={state.navigation.currentPath}
        onNavigateTo={path => {
          if (path.length === 0) {
            goToRoot()
          }
        }}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Navigation Bar */}
        <NavigationBar
          canGoBack={canGoBack}
          canGoForward={canGoForward}
          currentPath={state.navigation.currentPath}
          projects={PROJECTS_DATA}
          onGoBack={goBack}
          onGoForward={goForward}
          onGoToRoot={goToRoot}
          onNavigateToPath={path => {
            // Reset to root when clicking root
            if (path.length === 0) {
              goToRoot()
            } else {
              // Navigate to specific path
              navigateTo(path)
            }
          }}
        />

        {/* File Grid */}
        <FileGrid
          items={currentItems}
          selectedItems={state.selectedItems}
          viewMode={state.viewMode}
          onItemClick={navigateToItem}
          onItemSelect={toggleSelection}
        />
      </div>
    </div>
  )
}
