import { createHistoryRouter, createRoute } from 'atomic-router'

export const routes = {
  launchpad: createRoute(),
  window: createRoute(),
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
