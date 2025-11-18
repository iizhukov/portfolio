import type { AxiosError } from 'axios'

export interface ApiError {
  message: string
  status?: number
  code?: string
}

export class ApiErrorHandler {
  private static errorCallbacks: Array<(error: ApiError) => void> = []

  static onError(callback: (error: ApiError) => void): () => void {
    this.errorCallbacks.push(callback)
    return () => {
      this.errorCallbacks = this.errorCallbacks.filter(cb => cb !== callback)
    }
  }

  static handleError(error: unknown): ApiError {
    let apiError: ApiError

    if (this.isAxiosError(error)) {
      if (error.code === 'ERR_CANCELED' || error.message === 'canceled') {
        return {
          message: 'Request canceled',
          code: 'CANCELED',
        }
      }

      if (error.response) {
        apiError = {
          message: this.extractMessage(error.response.data) || `Server error: ${error.response.status}`,
          status: error.response.status,
          code: error.code,
        }
      } else if (error.request) {
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          apiError = {
            message: 'Request timeout: Server did not respond in time',
            code: 'TIMEOUT',
          }
        } else if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
          apiError = {
            message: 'Network error: Unable to reach server',
            code: 'NETWORK_ERROR',
          }
        } else {
          apiError = {
            message: 'Network error: Unable to reach server',
            code: error.code || 'NETWORK_ERROR',
          }
        }
      } else {
        apiError = {
          message: error.message || 'An unexpected error occurred',
          code: error.code,
        }
      }
    } else if (error instanceof Error) {
      apiError = {
        message: error.message,
      }
    } else {
      apiError = {
        message: 'An unknown error occurred',
      }
    }

    this.notifyError(apiError)
    return apiError
  }

  private static isAxiosError(error: unknown): error is AxiosError {
    return (
      typeof error === 'object' &&
      error !== null &&
      'isAxiosError' in error &&
      (error as AxiosError).isAxiosError === true
    )
  }

  private static extractMessage(data: unknown): string | null {
    if (typeof data === 'string') return data
    if (typeof data === 'object' && data !== null) {
      if ('message' in data && typeof data.message === 'string') {
        return data.message
      }
      if ('detail' in data && typeof data.detail === 'string') {
        return data.detail
      }
      if ('error' in data && typeof data.error === 'string') {
        return data.error
      }
    }
    return null
  }

  private static notifyError(error: ApiError): void {
    if (error.code === 'CANCELED') {
      return
    }

    if (import.meta.env.DEV) {
      console.error('[API Error]', error)
    }
    this.errorCallbacks.forEach(callback => callback(error))
  }
}

