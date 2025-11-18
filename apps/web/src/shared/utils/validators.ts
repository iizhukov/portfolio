export const validateDbml = (dbml: string): { valid: boolean; error?: string } => {
  if (!dbml || typeof dbml !== 'string') {
    return { valid: false, error: 'DBML must be a non-empty string' }
  }

  if (dbml.trim().length === 0) {
    return { valid: false, error: 'DBML cannot be empty' }
  }

  const hasTable = /Table\s+["\w\s]+\s*\{/i.test(dbml)
  if (!hasTable) {
    return { valid: false, error: 'DBML must contain at least one Table definition' }
  }

  const openBraces = (dbml.match(/\{/g) || []).length
  const closeBraces = (dbml.match(/\}/g) || []).length
  if (openBraces !== closeBraces) {
    return { valid: false, error: 'DBML has unbalanced braces' }
  }

  return { valid: true }
}

export const validateExcalidrawJson = (data: unknown): { valid: boolean; error?: string } => {
  if (!data || typeof data !== 'object') {
    return { valid: false, error: 'Excalidraw data must be an object' }
  }

  const obj = data as Record<string, unknown>

  if (!('type' in obj) && !('elements' in obj) && !('appState' in obj)) {
    if (Object.keys(obj).length === 0) {
      return { valid: false, error: 'Excalidraw data cannot be empty' }
    }
  }

  return { valid: true }
}

