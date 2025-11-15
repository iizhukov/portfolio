import apiClient from './config'
import type { ServiceInfo } from './types/modules'

export const modulesApi = {
  listServices: async (): Promise<ServiceInfo[]> => {
    const response = await apiClient.get<ServiceInfo[]>('/modules/services')
    return response.data
  },

  getServiceDetails: async (serviceName: string): Promise<ServiceInfo> => {
    const response = await apiClient.get<ServiceInfo>(`/modules/services/${serviceName}`)
    return response.data
  },
}

