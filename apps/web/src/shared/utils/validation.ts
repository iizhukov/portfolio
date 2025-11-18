export const validateUrlParam = (value: string | null, maxLength = 1000): string | undefined => {
  if (!value) return undefined
  
  if (value.length > maxLength) {
    if (import.meta.env.DEV) {
      console.warn('URL parameter exceeds maximum length')
    }
    return undefined
  }
  
  if (/<script|javascript:|onerror=|onload=/i.test(value)) {
    if (import.meta.env.DEV) {
      console.warn('Potentially dangerous URL parameter detected')
    }
    return undefined
  }
  
  return value
}

