import apiClient from './config'
import type { AxiosResponse, AxiosRequestConfig } from 'axios'
import type { Project, ProjectHealth } from './types/projects'

export const projectsApi = {
  getProjects: async (parentId?: number, config?: AxiosRequestConfig): Promise<AxiosResponse<Project[]>> => {
    const params = parentId !== undefined ? { parent_id: parentId } : {}
    return apiClient.get<Project[]>('/projects/', { ...config, params })
  },

  getProjectById: async (projectId: number, config?: AxiosRequestConfig): Promise<AxiosResponse<Project>> => {
    return apiClient.get<Project>(`/projects/${projectId}`, config)
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

