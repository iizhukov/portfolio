import { routes } from '@shared/router/config'
import { WindowPage } from './ui/window-page'

export { WindowPage } from './ui/window-page'
export { Window } from './ui/window'
export { MOCK_APPS } from './model/window'

export const WindowRoute = {
  view: WindowPage,
  route: routes.window,
}
