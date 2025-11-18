import { useMemo } from 'react'
import { projectsApi } from '../projects'
import { useApiQuery } from './use-api-query'
import { CACHE_TTL } from '@shared/constants/cache'
import type { Project } from '../types/projects'

export const useProjects = (parentId?: number) => {
  const cacheKey = useMemo(() => `projects:${parentId ?? 'root'}`, [parentId])
  
  const { data, loading, error } = useApiQuery<Project[]>(
    cacheKey,
    (signal, config) => projectsApi.getProjects(parentId, { ...config, signal }),
    { ttl: CACHE_TTL.DEFAULT }
  )

  return { projects: data ?? [], loading, error }
}

export const useProjectTree = (rootId?: number) => {
  const cacheKey = useMemo(() => `project-tree:${rootId ?? 'root'}`, [rootId])
  
  const { data, loading, error } = useApiQuery<Project[]>(
    cacheKey,
    (signal, config) => projectsApi.getProjectTree(rootId, { ...config, signal }),
    { ttl: CACHE_TTL.DEFAULT }
  )

  return { projects: data ?? [], loading, error }
}

export const useProject = (projectId: number) => {
  const cacheKey = useMemo(() => `project:${projectId}`, [projectId])
  
  const { data, loading, error } = useApiQuery<Project>(
    cacheKey,
    (signal, config) => projectsApi.getProjectById(projectId, { ...config, signal }),
    { 
      ttl: CACHE_TTL.DEFAULT,
      enabled: !!projectId 
    }
  )

  return { project: data ?? null, loading, error }
}

