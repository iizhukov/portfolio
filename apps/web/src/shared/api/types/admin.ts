export interface AdminFile {
  name: string
  extension: string
  path?: string
  content?: string | null
  filename?: string | null
  content_type?: string | null
  url?: string | null
  bucket?: string | null
  size?: number | null
}

export interface AdminCommandRequest {
  service: string
  payload: Record<string, unknown>
  file?: AdminFile | null
}

export interface AdminCommandResponse {
  request_id: string
  status: string
  service: string
  payload: Record<string, unknown>
  file?: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface AdminMessageStatus {
  request_id: string
  status: string
  service: string
  payload: Record<string, unknown>
  response?: Record<string, unknown> | null
  file?: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

