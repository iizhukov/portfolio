import { useState, useCallback, useEffect, useMemo } from 'react'
import { type Project, type FinderState } from '../types/finder'
import { useProjects } from '@shared/api/hooks/use-projects'
import { useProject } from '@shared/api/hooks/use-projects'
import { projectsStore } from '../models/projects-store'
import { handleFileOpen } from '../utils/file-handlers'
import { STORAGE_KEYS } from '@shared/constants/storage'
import { safeJsonParse } from '@shared/utils/safe-json'
import { isBrowser } from '@shared/utils/browser'

const getInitialState = (): FinderState => {
  if (!isBrowser) {
    return {
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
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEYS.FINDER_STATE)
    if (stored) {
      const parsed = safeJsonParse<FinderState>(stored, {
        navigation: {
          currentPath: [],
          history: [[]],
          historyIndex: 0,
        },
        selectedItems: [],
        viewMode: 'grid',
        sortBy: 'name',
        sortOrder: 'asc',
      })
      return parsed
    }
  } catch (error) {
    console.error('Failed to load finder state from storage:', error)
  }

  return {
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
}

export const useFinder = () => {
  const [state, setState] = useState<FinderState>(getInitialState)
  const [isInitialLoad, setIsInitialLoad] = useState(true)
  const [storeUpdateCounter, setStoreUpdateCounter] = useState(0)

  projectsStore.initialize()

  useEffect(() => {
    const unsubscribe = projectsStore.subscribe(() => {
      setStoreUpdateCounter(projectsStore.getUpdateCounter())
    })
    return unsubscribe
  }, [])

  const shouldLoadRoots = state.navigation.currentPath.length === 0
  const rootProjectsFromStore = projectsStore.getRootProjects()
  const needsRootLoad = shouldLoadRoots && (isInitialLoad || rootProjectsFromStore.length === 0)
  
  const { projects: rootProjects, loading: rootLoading, error: rootError } = useProjects(
    undefined,
    1,
    needsRootLoad
  )

  const currentFolderId = state.navigation.currentPath.length > 0 
    ? state.navigation.currentPath[state.navigation.currentPath.length - 1]
    : null

  const { project: currentFolder, loading: folderLoading, error: folderError } = useProject(
    currentFolderId ? Number(currentFolderId) : 0,
    2,
    currentFolderId !== null
  )

  const hasRootData = rootProjectsFromStore.length > 0
  const hasFolderData = currentFolderId ? projectsStore.getProject(currentFolderId) !== undefined : true
  
  const loading = (shouldLoadRoots && !hasRootData && rootLoading) || (currentFolderId && !hasFolderData && folderLoading)
  const error = rootError || folderError

  useEffect(() => {
    if (rootProjects.length > 0) {
      projectsStore.addProjects(rootProjects)
    }
    if (isInitialLoad && (rootProjects.length > 0 || rootProjectsFromStore.length > 0)) {
      setIsInitialLoad(false)
    }
  }, [rootProjects, isInitialLoad, rootProjectsFromStore.length])

  useEffect(() => {
    if (currentFolder && currentFolderId) {
      projectsStore.addProject(currentFolder)
    }
  }, [currentFolder, currentFolderId])

  useEffect(() => {
    if (!isBrowser) return

    try {
      localStorage.setItem(STORAGE_KEYS.FINDER_STATE, JSON.stringify(state))
    } catch (error) {
      console.error('Failed to save finder state to storage:', error)
    }
  }, [state])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const app = params.get('app')
    if (app !== 'finder' && app !== 'projects') {
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
        setIsInitialLoad(false)
      }
    }
  }, [])

  useEffect(() => {
    const currentParams = new URLSearchParams(window.location.search)
    const currentApp = currentParams.get('app')
    
    if (currentApp && currentApp !== 'finder' && currentApp !== 'projects') {
      return
    }
    
    if (state.navigation.currentPath.length === 0) {
      return
    }
    
    const query: Record<string, string> = {}
    const existingApp = currentParams.get('app')
    if (existingApp) {
      query.app = existingApp
    }
    query.path = state.navigation.currentPath.join(',')
    
    const params = new URLSearchParams(query)
    const fullPath = `/window?${params.toString()}`
    
    if (window.location.pathname === '/window') {
      const currentSearch = window.location.search
      const newSearch = `?${params.toString()}`
      if (currentSearch !== newSearch) {
        window.history.replaceState(null, '', fullPath)
        window.dispatchEvent(new PopStateEvent('popstate'))
      }
    }
  }, [state.navigation.currentPath])

  const getCurrentItems = useMemo((): Project[] => {
    if (state.navigation.currentPath.length === 0) {
      const roots = projectsStore.getRootProjects()
      return roots
    }

    const parentId = state.navigation.currentPath[state.navigation.currentPath.length - 1]
    return projectsStore.getChildren(parentId)
  }, [state.navigation.currentPath, storeUpdateCounter])

  const allProjects = useMemo(() => {
    return projectsStore.getRootProjects()
  }, [rootProjects, currentFolder, storeUpdateCounter])

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
        const newPath = [...state.navigation.currentPath, item.id]
        navigateTo(newPath)
      } else {
        handleFileOpen(item, state.navigation.currentPath)
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
    currentItems: getCurrentItems,
    allProjects,
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
