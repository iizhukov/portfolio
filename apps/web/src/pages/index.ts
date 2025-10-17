import { createRoutesView } from 'atomic-router-react'

import { LaunchpadRoute } from './launchpad'
import { WindowRoute } from './window'

export const Pages = createRoutesView({
  routes: [LaunchpadRoute, WindowRoute],
})
