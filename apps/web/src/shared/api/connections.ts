import apiClient from './config'
import type { Connection, Status, Working, Image, Health } from './types/connections'

export const connectionsApi = {
  getConnections: async (): Promise<Connection[]> => {
    const response = await apiClient.get<Connection[]>('/connections/connections/')
    return response.data
  },

  getStatus: async (): Promise<Status> => {
    const response = await apiClient.get<Status>('/connections/status/')
    return response.data
  },

  getWorking: async (): Promise<Working> => {
    const response = await apiClient.get<Working>('/connections/working-on/')
    return response.data
  },

  getImage: async (): Promise<Image> => {
    const response = await apiClient.get<Image>('/connections/image/')
    return response.data
  },

  getHealth: async (): Promise<Health> => {
    const response = await apiClient.get<Health>('/connections/health/')
    return response.data
  },
}

