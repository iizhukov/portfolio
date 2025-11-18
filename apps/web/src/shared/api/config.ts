import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { env } from '@shared/config/env'
import { ApiErrorHandler } from './error-handler'

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${env.GATEWAY_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    return config
  },
  (error) => {
    if (import.meta.env.DEV) {
      console.error('[API Request Error]', error)
    }
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    ApiErrorHandler.handleError(error)
    return Promise.reject(error)
  }
)

export default apiClient

