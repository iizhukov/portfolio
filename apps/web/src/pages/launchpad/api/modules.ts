import axios from 'axios'
import type { AxiosInstance } from 'axios'

const API_PROTOCOL = import.meta.env.VITE_API_PROTOCOL || 'http'
const API_IP = import.meta.env.VITE_API_IP || 'localhost'
const GATEWAY_URL = `${API_PROTOCOL}://${API_IP}`

const apiClient: AxiosInstance = axios.create({
  baseURL: `${GATEWAY_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

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
}

export const SERVICE_APP_MAPPING: Record<string, { icon: string; type: string; name: string }> = {
  projects: {
    icon: '/assets/icons/wpaper_folder.ico',
    type: 'finder',
    name: 'Projects',
  },
  connections: {
    icon: '/assets/icons/discord.ico',
    type: 'connections',
    name: 'Connections',
  },
  swagger: {
    icon: '/assets/icons/swagger.ico',
    type: 'swagger',
    name: 'Swagger',
  },
}

