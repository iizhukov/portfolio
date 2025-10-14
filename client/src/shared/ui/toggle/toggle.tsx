import { clsx } from 'clsx'

interface ToggleProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export const Toggle = ({
  checked,
  onChange,
  disabled = false,
  className,
  size = 'md',
}: ToggleProps) => {
  const sizeClasses = {
    sm: 'w-8 h-4',
    md: 'w-11 h-6',
    lg: 'w-14 h-7',
  }

  const thumbSizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }

  const translateClasses = {
    sm: checked ? 'translate-x-4' : 'translate-x-0.5',
    md: checked ? 'translate-x-5' : 'translate-x-0.5',
    lg: checked ? 'translate-x-7' : 'translate-x-0.5',
  }

  return (
    <button
      type="button"
      className={clsx(
        'relative inline-flex items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
        checked ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600',
        disabled && 'opacity-50 cursor-not-allowed',
        sizeClasses[size],
        className
      )}
      onClick={() => !disabled && onChange(!checked)}
      disabled={disabled}
    >
      <span
        className={clsx(
          'inline-block rounded-full bg-white shadow transform transition-transform duration-200',
          thumbSizeClasses[size],
          translateClasses[size]
        )}
      />
    </button>
  )
}
