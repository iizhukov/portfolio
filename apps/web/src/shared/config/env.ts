interface EnvConfig {
  API_PROTOCOL: string
  API_IP: string
  GATEWAY_URL: string
}

const validateEnv = (): EnvConfig => {
  const protocol = import.meta.env.VITE_API_PROTOCOL
  const ip = import.meta.env.VITE_API_IP

  if (!protocol || !ip) {
    const missing = []
    if (!protocol) missing.push('VITE_API_PROTOCOL')
    if (!ip) missing.push('VITE_API_IP')
    
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}. ` +
      'Please check your .env file or build configuration.'
    )
  }

  if (protocol !== 'http' && protocol !== 'https') {
    throw new Error(
      `Invalid VITE_API_PROTOCOL: "${protocol}". Must be "http" or "https".`
    )
  }

  return {
    API_PROTOCOL: protocol,
    API_IP: ip,
    GATEWAY_URL: `${protocol}://${ip}`,
  }
}

export const env = validateEnv()

if (import.meta.env.DEV) {
  console.log('[Env] Configuration loaded:', {
    API_PROTOCOL: env.API_PROTOCOL,
    API_IP: env.API_IP,
    GATEWAY_URL: env.GATEWAY_URL,
  })
}

