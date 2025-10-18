import { clsx } from 'clsx'
import { useState } from 'react'

export interface SelectOption {
  value: string
  label: string
}

interface SelectProps {
  options: SelectOption[]
  value: string
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export const Select = ({
  options,
  value,
  onChange,
  placeholder = 'Select...',
  disabled = false,
  className,
}: SelectProps) => {
  const [isOpen, setIsOpen] = useState(false)

  const selectedOption = options.find(option => option.value === value)

  return (
    <div className={clsx('relative', className)}>
      <button
        type="button"
        className={clsx(
          'w-full px-3 py-2 text-left bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
      >
        <span className="block truncate">
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <svg
            className={clsx(
              'w-5 h-5 text-gray-400 transition-transform duration-200',
              isOpen && 'rotate-180'
            )}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
          <ul className="py-1 max-h-60 overflow-auto">
            {options.map(option => (
              <li key={option.value}>
                <button
                  type="button"
                  className={clsx(
                    'w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-700',
                    value === option.value &&
                      'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                  )}
                  onClick={() => {
                    onChange(option.value)
                    setIsOpen(false)
                  }}
                >
                  {option.label}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
