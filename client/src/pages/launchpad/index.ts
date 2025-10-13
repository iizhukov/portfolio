import { routes } from '@shared/router/config'
import { LaunchpadPage } from './ui/launchpad-page'

export { LaunchpadPage } from './ui/launchpad-page'
export { Launchpad } from './ui/launchpad'
export {
  MOCK_APPS,
  LAUNCHPAD_GRID_COLS,
  LAUNCHPAD_ICON_SIZE,
  LAUNCHPAD_ICON_GAP,
} from './model/launchpad'

export const LaunchpadRoute = {
  view: LaunchpadPage,
  route: routes.launchpad,
}
