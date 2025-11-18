import type { WindowQueryParams } from '@pages/window/types'
import { isBrowser } from './browser'
import { notifyLocationChange } from './location'

const buildQueryString = (params: WindowQueryParams): string => {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      query.set(key, value)
    }
  })
  return query.toString()
}

export const navigateToWindow = (params: WindowQueryParams): void => {
  if (!isBrowser) {
    return
  }

  const fullPath = `/window?${buildQueryString(params)}`

  window.history.pushState(params, '', fullPath)
  notifyLocationChange()
  window.dispatchEvent(new PopStateEvent('popstate'))
}

export const navigateToLaunchpad = (): void => {
  if (!isBrowser) {
    return
  }

  window.history.pushState(null, '', '/')
  notifyLocationChange()
  window.dispatchEvent(new PopStateEvent('popstate'))
}

export const replaceWindowRoute = (params: WindowQueryParams): void => {
  if (!isBrowser) {
    return
  }

  const fullPath = `/window?${buildQueryString(params)}`

  window.history.replaceState(null, '', fullPath)
  notifyLocationChange()
  window.dispatchEvent(new PopStateEvent('popstate'))
}

