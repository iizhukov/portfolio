import apiClient from './config'

export interface ServiceInfo {
  id: number
  service_name: string
  version: string
  admin_topic: string
  ttl_seconds: number
  status: string
  created_at: string
  updated_at: string
}

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

