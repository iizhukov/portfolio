import apiClient from './config'
import type { AxiosResponse, AxiosRequestConfig } from 'axios'
import type { Project, ProjectHealth } from './types/projects'

export const projectsApi = {
  getProjects: async (parentId?: number, depth?: number, config?: AxiosRequestConfig): Promise<AxiosResponse<Project[]>> => {
    const params: Record<string, string | number> = {}
    if (parentId !== undefined) {
      params.parent_id = parentId
    }
    if (depth !== undefined) {
      params.depth = depth
    }
    return apiClient.get<Project[]>('/projects/', { ...config, params })
  },

  getProjectById: async (projectId: number, depth?: number, config?: AxiosRequestConfig): Promise<AxiosResponse<Project>> => {
    const params: Record<string, number> = {}
    if (depth !== undefined) {
      params.depth = depth
    }
    return apiClient.get<Project>(`/projects/${projectId}`, { ...config, params })
  },

  getProjectTree: async (rootId?: number, config?: AxiosRequestConfig): Promise<AxiosResponse<Project[]>> => {
    const params = rootId !== undefined ? { root_id: rootId } : {}
    return apiClient.get<Project[]>('/projects/tree', { ...config, params })
  },

  getHealth: async (): Promise<ProjectHealth> => {
    const response = await apiClient.get<ProjectHealth>('/projects/health/')
    return response.data
  },
}

