import { createHistoryRouter, createRoute } from 'atomic-router'

export const routes = {
  launchpad: createRoute(),
  window: createRoute<{ app?: string; url?: string; title?: string; path?: string; returnPath?: string }>(),
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
