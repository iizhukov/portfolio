import { Launchpad } from './launchpad'
import { MOCK_APPS } from '../model/launchpad'
import { router } from '@shared/router'

export const LaunchpadPage = () => {
  const handleAppClick = (appId: string) => {
    router.push({ path: '/window', params: {}, query: { app: appId }, method: 'push' })
  }

  return <Launchpad apps={MOCK_APPS} onAppClick={handleAppClick} />
}
