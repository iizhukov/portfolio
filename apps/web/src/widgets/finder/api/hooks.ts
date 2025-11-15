import { useState, useEffect } from 'react'
import { projectsApi } from './projects'
import type { Project } from './types'

export const useProjects = (parentId?: number) => {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await projectsApi.getProjects(parentId)
        setProjects(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch projects'))
      } finally {
        setLoading(false)
      }
    }

    fetchProjects()
  }, [parentId])

  return { projects, loading, error }
}

export const useProjectTree = (rootId?: number) => {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchTree = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await projectsApi.getProjectTree(rootId)
        setProjects(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch project tree'))
      } finally {
        setLoading(false)
      }
    }

    fetchTree()
  }, [rootId])

  return { projects, loading, error }
}

export const useProject = (projectId: number) => {
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchProject = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await projectsApi.getProjectById(projectId)
        setProject(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch project'))
      } finally {
        setLoading(false)
      }
    }

    if (projectId) {
      fetchProject()
    }
  }, [projectId])

  return { project, loading, error }
}

