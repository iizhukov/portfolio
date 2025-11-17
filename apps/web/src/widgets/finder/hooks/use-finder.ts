import { useState, useCallback, useEffect } from 'react'
import { type Project, type FinderState } from '../types/finder'
import { useProjectTree } from '../api/hooks'
import { adaptApiProjectToFinder } from '../utils/project-adapter'
import { handleFileOpen, setCurrentFinderPath } from '../utils/file-handlers'
import { notifyLocationChange } from '@shared/utils/location'

const initialState: FinderState = {
  navigation: {
    currentPath: [],
    history: [[]],
    historyIndex: 0,
  },
  selectedItems: [],
  viewMode: 'grid',
  sortBy: 'name',
  sortOrder: 'asc',
}

export const useFinder = () => {
  const [state, setState] = useState<FinderState>(initialState)
  const { projects: apiProjects, loading, error } = useProjectTree()
  const finderProjects = apiProjects.map(adaptApiProjectToFinder)

  const restorePathFromUrl = useCallback(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('app') !== 'finder') {
      return
    }
    const pathParam = params.get('path')
    if (pathParam) {
      const path = pathParam.split(',').filter(Boolean)
      if (path.length > 0) {
        setState(prev => ({
          ...prev,
          navigation: {
            currentPath: path,
            history: [path],
            historyIndex: 0,
          },
          selectedItems: [],
        }))
        setCurrentFinderPath(path)
      }
    }
  }, [setState])

  useEffect(() => {
    restorePathFromUrl()
  }, [restorePathFromUrl])

  useEffect(() => {
    setCurrentFinderPath(state.navigation.currentPath)
    const params = new URLSearchParams(window.location.search)
    if (params.get('app') !== 'finder') {
      return
    }
    params.set('app', 'finder')
    if (state.navigation.currentPath.length > 0) {
      params.set('path', state.navigation.currentPath.join(','))
    } else {
      params.delete('path')
    }
    const queryString = params.toString()
    const newUrl = queryString ? `/window?${queryString}` : '/window'
    window.history.replaceState(null, '', newUrl)
    notifyLocationChange()
  }, [state.navigation.currentPath])

  const getCurrentItems = useCallback((): Project[] => {
    if (loading || error || finderProjects.length === 0) {
      return []
    }

    let current = finderProjects

    for (const pathId of state.navigation.currentPath) {
      const found = current.find(item => item.id === pathId)
      if (found && found.children) {
        current = found.children
      } else {
        return []
      }
    }

    const sorted = [...current].sort((a, b) => {
      if (a.type === 'folder' && b.type !== 'folder') {
        return -1
      }
      if (a.type !== 'folder' && b.type === 'folder') {
        return 1
      }
      return a.name.localeCompare(b.name, undefined, { sensitivity: 'base' })
    })

    return sorted
  }, [state.navigation.currentPath, finderProjects, loading, error])

  const navigateTo = useCallback((path: string[]) => {
    setState(prev => {
      const newHistory = [
        ...prev.navigation.history.slice(0, prev.navigation.historyIndex + 1),
        path,
      ]
      return {
        ...prev,
        navigation: {
          currentPath: path,
          history: newHistory,
          historyIndex: newHistory.length - 1,
        },
        selectedItems: [],
      }
    })
  }, [])

  const navigateToItem = useCallback(
    (item: Project) => {
      if (item.type === 'folder') {
        if (item.children && item.children.length > 0) {
          const newPath = [...state.navigation.currentPath, item.id]
          navigateTo(newPath)
        }
      } else {
        handleFileOpen(item)
      }
    },
    [state.navigation.currentPath, navigateTo]
  )

  const goBack = useCallback(() => {
    if (state.navigation.historyIndex > 0) {
      setState(prev => ({
        ...prev,
        navigation: {
          ...prev.navigation,
          historyIndex: prev.navigation.historyIndex - 1,
          currentPath: prev.navigation.history[prev.navigation.historyIndex - 1],
        },
        selectedItems: [],
      }))
    }
  }, [state.navigation.historyIndex])

  const goForward = useCallback(() => {
    if (state.navigation.historyIndex < state.navigation.history.length - 1) {
      setState(prev => ({
        ...prev,
        navigation: {
          ...prev.navigation,
          historyIndex: prev.navigation.historyIndex + 1,
          currentPath: prev.navigation.history[prev.navigation.historyIndex + 1],
        },
        selectedItems: [],
      }))
    }
  }, [state.navigation.historyIndex, state.navigation.history.length])

  const goToRoot = useCallback(() => {
    navigateTo([])
  }, [navigateTo])

  const toggleSelection = useCallback((itemId: string) => {
    setState(prev => ({
      ...prev,
      selectedItems: prev.selectedItems.includes(itemId)
        ? prev.selectedItems.filter(id => id !== itemId)
        : [...prev.selectedItems, itemId],
    }))
  }, [])

  const clearSelection = useCallback(() => {
    setState(prev => ({
      ...prev,
      selectedItems: [],
    }))
  }, [])

  const setViewMode = useCallback((mode: 'grid' | 'list') => {
    setState(prev => ({
      ...prev,
      viewMode: mode,
    }))
  }, [])

  const setSortBy = useCallback((sortBy: 'name' | 'type' | 'date') => {
    setState(prev => ({
      ...prev,
      sortBy,
    }))
  }, [])

  const setSortOrder = useCallback((sortOrder: 'asc' | 'desc') => {
    setState(prev => ({
      ...prev,
      sortOrder,
    }))
  }, [])

  const getPathString = useCallback(() => {
    if (state.navigation.currentPath.length === 0) {
      return 'Projects'
    }
    return state.navigation.currentPath.join(' > ')
  }, [state.navigation.currentPath])

  const canGoBack = state.navigation.historyIndex > 0
  const canGoForward = state.navigation.historyIndex < state.navigation.history.length - 1

  return {
    state,
    currentItems: getCurrentItems(),
    allProjects: finderProjects,
    navigateToItem,
    navigateTo,
    goBack,
    goForward,
    goToRoot,
    toggleSelection,
    clearSelection,
    setViewMode,
    setSortBy,
    setSortOrder,
    getPathString,
    canGoBack,
    canGoForward,
    loading,
    error,
  }
}
