import { useState, useEffect } from 'react'
import { connectionsApi } from '../connections'
import type { Connection, Status, Working, Image } from '../types/connections'

export const useConnections = () => {
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchConnections = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await connectionsApi.getConnections()
        setConnections(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch connections'))
      } finally {
        setLoading(false)
      }
    }

    fetchConnections()
  }, [])

  return { connections, loading, error }
}

export const useStatus = () => {
  const [status, setStatus] = useState<Status | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await connectionsApi.getStatus()
        setStatus(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch status'))
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
  }, [])

  return { status, loading, error }
}

export const useWorking = () => {
  const [working, setWorking] = useState<Working | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchWorking = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await connectionsApi.getWorking()
        setWorking(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch working status'))
      } finally {
        setLoading(false)
      }
    }

    fetchWorking()
  }, [])

  return { working, loading, error }
}

export const useImage = () => {
  const [image, setImage] = useState<Image | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchImage = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await connectionsApi.getImage()
        setImage(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch image'))
      } finally {
        setLoading(false)
      }
    }

    fetchImage()
  }, [])

  return { image, loading, error }
}

