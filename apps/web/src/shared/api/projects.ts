import apiClient from './config'
import type { Project, ProjectHealth } from './types/projects'

export const projectsApi = {
  getProjects: async (parentId?: number): Promise<Project[]> => {
    const params = parentId !== undefined ? { parent_id: parentId } : {}
    const response = await apiClient.get<Project[]>('/projects/', { params })
    return response.data
  },

  getProjectById: async (projectId: number): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${projectId}`)
    return response.data
  },

  getProjectTree: async (rootId?: number): Promise<Project[]> => {
    const params = rootId !== undefined ? { root_id: rootId } : {}
    const response = await apiClient.get<Project[]>('/projects/tree', { params })
    return response.data
  },

  getHealth: async (): Promise<ProjectHealth> => {
    const response = await apiClient.get<ProjectHealth>('/projects/health/')
    return response.data
  },
}

