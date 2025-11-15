export interface Connection {
  id: number
  label: string
  type: 'social' | 'email'
  href: string
  value: string
}

export interface Status {
  id: number
  status: 'active' | 'inactive'
}

export interface Working {
  id: number
  working_on: string
  percentage: number
}

export interface Image {
  id: number
  filename: string
  content_type: string
  url: string
}

export interface Health {
  status: string
  timestamp: string
  database: boolean
  redpanda: boolean
  modules_service: boolean
}

