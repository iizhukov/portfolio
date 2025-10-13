/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', 'index.html'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border-light))',

        background: 'hsl(var(--bg-primary))',
        foreground: 'hsl(var(--text-primary))',
        accent: {
          DEFAULT: 'hsl(var(--accent-blue))',
          foreground: 'hsl(var(--text-white))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--bg-secondary))',
          foreground: 'hsl(var(--text-secondary))',
        },
        sidebar: {
          DEFAULT: 'hsl(var(--bg-sidebar))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--accent-red))',
          foreground: 'hsl(var(--text-white))',
        },
        muted: {
          DEFAULT: 'hsl(var(--bg-secondary))',
          foreground: 'hsl(var(--text-secondary))',
        },
        popover: {
          DEFAULT: 'hsl(var(--bg-primary))',
          foreground: 'hsl(var(--text-primary))',
        },
        card: {
          DEFAULT: 'hsl(var(--bg-primary))',
          foreground: 'hsl(var(--text-primary))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      transitionDuration: {
        DEFAULT: 'var(--transition)',
      },
    },
  },
  plugins: [],
}
