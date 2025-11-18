import { env } from '@shared/config/env'

export const getFileUrl = (url: string | undefined | null): string => {
  if (!url) {
    return ''
  }

  if (url.startsWith('/storage/')) {
    return `${env.GATEWAY_URL}${url}`
  }

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }

  return url
}

