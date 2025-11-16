import { clsx } from 'clsx'

interface BackgroundProps {
  wallpaper?: string
  blur?: boolean
  className?: string
}

export const Background = ({
  wallpaper = '/assets/wallpapers/wallpaper.jpg',
  blur = true,
  className,
}: BackgroundProps) => {
  return (
    <div
      className={clsx('fixed inset-0 w-full h-full', 'bg-cover bg-center bg-no-repeat', className)}
      style={{
        backgroundImage: `url(${wallpaper})`,
      }}
    >
      {blur && <div className="absolute inset-0 backdrop-blur-lg bg-black/10" />}
    </div>
  )
}
