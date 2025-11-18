export const safeDecodeURIComponent = (str: string | undefined | null): string | undefined => {
  if (!str) return undefined
  try {
    return decodeURIComponent(str)
  } catch {
    return str
  }
}

