/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', 'index.html'],
  theme: {
    extend: {
      colors: {
        connections: {
          DEFAULT: 'hsl(var(--bg-connections))',
        },
        settings: {
          bg: 'hsl(var(--settings-bg))',
          'sidebar-bg': 'hsl(var(--settings-sidebar-bg))',
          border: 'hsl(var(--settings-border))',
          text: 'hsl(var(--settings-text))',
          'text-secondary': 'hsl(var(--settings-text-secondary))',
          hover: 'hsl(var(--settings-hover))',
          active: 'hsl(var(--settings-active))',
        },
        window: {
          bg: 'hsl(var(--window-bg))',
          header: {
            bg: 'hsl(var(--window-header-bg))',
            border: 'hsl(var(--window-header-border))',
          },
          text: 'hsl(var(--window-text))',
          'text-secondary': 'hsl(var(--window-text-secondary))',
        },
        control: {
          close: 'hsl(var(--control-close))',
          'close-hover': 'hsl(var(--control-close-hover))',
          minimize: 'hsl(var(--control-minimize))',
          'minimize-hover': 'hsl(var(--control-minimize-hover))',
          maximize: 'hsl(var(--control-maximize))',
          'maximize-hover': 'hsl(var(--control-maximize-hover))',
        },
        status: {
          green: 'hsl(var(--status-green))',
          red: 'hsl(var(--status-red))',
        },
      },
      borderRadius: {
        lg: '12px',
        md: '10px',
        sm: '8px',
      },
      borderColor: {
        connections: 'hsl(var(--bg-connections))',
      },

      transitionDuration: {
        DEFAULT: '0.25s',
      },
      spacing: {
        '25': '100px',
      },
    },
  },
  plugins: [],
}
