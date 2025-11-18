import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'atomic-router-react'
import { router } from '@shared/router'
import { Pages } from '@pages/index'
import { Layout } from './layout'
import { ErrorBoundary } from '@shared/ui/error-boundary'
import { appStarted } from '@shared/config/init'
import '@shared/styles/global.css'

appStarted()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <Layout wallpaper="/assets/wallpapers/wallpaper.jpg" blur={true}>
        <RouterProvider router={router}>
          <ErrorBoundary>
            <Pages />
          </ErrorBoundary>
        </RouterProvider>
      </Layout>
    </ErrorBoundary>
  </StrictMode>
)
