export interface Project {
  id: number
  name: string
  type: 'folder' | 'file'
  file_type?: string | null
  parent_id?: number | null
  url?: string | null
  children?: Project[]
  created_at?: string | null
  updated_at?: string | null
}

export interface ProjectHealth {
  status: string
  timestamp: string
  database: boolean
  redpanda: boolean
  modules_service: boolean
}

