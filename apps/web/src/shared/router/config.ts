import { createHistoryRouter, createRoute } from 'atomic-router'

export interface WindowRouteParams {
  app?: string
  url?: string
  title?: string
  path?: string
  returnPath?: string
  dbml?: string
  excalidraw?: string
  swagger?: string
}

export const routes = {
  launchpad: createRoute(),
  window: createRoute<WindowRouteParams>(),
}

export const mappedRoutes = [
  {
    route: routes.launchpad,
    path: '/',
  },
  {
    route: routes.window,
    path: '/window',
  },
]

export const router = createHistoryRouter({
  routes: mappedRoutes,
})
