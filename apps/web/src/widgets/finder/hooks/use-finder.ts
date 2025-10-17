import { useState, useCallback } from 'react'
import { type Project, type FinderState } from '../types/finder'
import { PROJECTS_DATA } from '../models/projects'

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

  const getCurrentItems = useCallback((): Project[] => {
    let current = PROJECTS_DATA

    for (const pathId of state.navigation.currentPath) {
      const found = current.find(item => item.id === pathId)
      if (found && found.children) {
        current = found.children
      } else {
        return []
      }
    }

    return current
  }, [state.navigation.currentPath])

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
      if (item.type === 'folder' && item.children) {
        const newPath = [...state.navigation.currentPath, item.id]
        navigateTo(newPath)
      } else if (item.action) {
        item.action()
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
  }, [state.navigation.historyIndex, state.navigation.history])

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
  }, [state.navigation.historyIndex, state.navigation.history])

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
  }
}
