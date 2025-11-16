const API_PROTOCOL = import.meta.env.VITE_API_PROTOCOL || 'http'
const API_IP = import.meta.env.VITE_API_IP || 'localhost'
const GATEWAY_URL = `${API_PROTOCOL}://${API_IP}`

export const getFileUrl = (url: string | undefined | null): string => {
  if (!url) {
    return ''
  }

  if (url.startsWith('/storage/')) {
    return `${GATEWAY_URL}${url}`
  }

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }

  return url
}

