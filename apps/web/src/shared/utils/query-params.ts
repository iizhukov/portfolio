import type { WindowQueryParams } from '@pages/window/types'
import { validateUrlParam } from './validation'
import { isBrowser } from './browser'

export const parseWindowQueryParams = (): WindowQueryParams => {
  if (!isBrowser) {
    return {}
  }
  const params = new URLSearchParams(window.location.search)
  return {
    url: validateUrlParam(params.get('url')),
    title: validateUrlParam(params.get('title')),
    app: validateUrlParam(params.get('app')),
    path: validateUrlParam(params.get('path')),
    returnPath: validateUrlParam(params.get('returnPath')),
    dbml: validateUrlParam(params.get('dbml')),
    excalidraw: validateUrlParam(params.get('excalidraw')),
    swagger: validateUrlParam(params.get('swagger')),
  }
}

