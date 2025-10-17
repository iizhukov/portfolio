import type { ReactNode } from 'react'
import { Background } from './background'

interface LayoutProps {
  children: ReactNode
  wallpaper?: string
  blur?: boolean
}

export const Layout = ({ children, wallpaper, blur = true }: LayoutProps) => {
  return (
    <>
      <Background wallpaper={wallpaper} blur={blur} />
      {children}
    </>
  )
}
