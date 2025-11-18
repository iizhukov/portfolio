import apiClient from './config'
import type { AxiosResponse, AxiosRequestConfig } from 'axios'
import type { ServiceInfo } from './types/modules'

export const modulesApi = {
  listServices: async (config?: AxiosRequestConfig): Promise<AxiosResponse<ServiceInfo[]>> => {
    return apiClient.get<ServiceInfo[]>('/modules/services', config)
  },

  getServiceDetails: async (serviceName: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ServiceInfo>> => {
    return apiClient.get<ServiceInfo>(`/modules/services/${serviceName}`, config)
  },
}

