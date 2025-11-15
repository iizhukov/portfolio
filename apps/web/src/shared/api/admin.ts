import apiClient from './config'
import type {
  AdminCommandRequest,
  AdminCommandResponse,
  AdminMessageStatus,
} from './types/admin'

export const adminApi = {
  submitCommand: async (command: AdminCommandRequest): Promise<AdminCommandResponse> => {
    const response = await apiClient.post<AdminCommandResponse>('/admin/commands', command)
    return response.data
  },

  getMessageStatus: async (requestId: string): Promise<AdminMessageStatus> => {
    const response = await apiClient.get<AdminMessageStatus>(`/admin/messages/${requestId}`)
    return response.data
  },
}

