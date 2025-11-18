import apiClient from './config'
import type { AxiosResponse, AxiosRequestConfig } from 'axios'
import type { Connection, Status, Working, Image, Health } from './types/connections'

export const connectionsApi = {
  getConnections: async (config?: AxiosRequestConfig): Promise<AxiosResponse<Connection[]>> => {
    return apiClient.get<Connection[]>('/connections/connections/', config)
  },

  getStatus: async (config?: AxiosRequestConfig): Promise<AxiosResponse<Status>> => {
    return apiClient.get<Status>('/connections/status/', config)
  },

  getWorking: async (config?: AxiosRequestConfig): Promise<AxiosResponse<Working>> => {
    return apiClient.get<Working>('/connections/working-on/', config)
  },

  getImage: async (config?: AxiosRequestConfig): Promise<AxiosResponse<Image>> => {
    return apiClient.get<Image>('/connections/image/', config)
  },

  getHealth: async (): Promise<Health> => {
    const response = await apiClient.get<Health>('/connections/health/')
    return response.data
  },
}

