import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        brand: {
          900: 'var(--plp-color-brand-900)',
          800: 'var(--plp-color-brand-800)',
          700: 'var(--plp-color-brand-700)',
          600: 'var(--plp-color-brand-600)',
          400: 'var(--plp-color-brand-400)',
          300: 'var(--plp-color-brand-300)',
          200: 'var(--plp-color-brand-200)',
          100: 'var(--plp-color-brand-100)',
        },
        accent: 'var(--plp-color-accent-500)',
        app: 'var(--plp-color-bg)',
        surface: 'var(--plp-color-surface)',
        line: 'var(--plp-color-border)',
        'line-soft': 'var(--plp-color-border-soft)',
        ink: 'var(--plp-color-text)',
        muted: 'var(--plp-color-text-muted)',
        secondary: 'var(--plp-color-text-secondary)',
        success: {
          bg: 'var(--plp-color-success-bg)',
          border: 'var(--plp-color-success-border)',
          text: 'var(--plp-color-success-text)',
        },
        warning: {
          bg: 'var(--plp-color-warning-bg)',
          text: 'var(--plp-color-warning-text)',
        },
        info: {
          bg: 'var(--plp-color-info-bg)',
          text: 'var(--plp-color-info-text)',
        },
        danger: {
          DEFAULT: 'var(--plp-color-danger)',
          bg: 'var(--plp-color-danger-bg)',
          soft: 'var(--plp-color-danger-soft)',
          border: 'var(--plp-color-danger-border)',
          strong: 'var(--plp-color-danger-strong)',
        },
        neutral: {
          bg: 'var(--plp-color-neutral-bg)',
          text: 'var(--plp-color-neutral-text)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        sm: 'var(--plp-radius-sm)',
        md: 'var(--plp-radius-md)',
        lg: 'var(--plp-radius-lg)',
        xl: 'var(--plp-radius-xl)',
        pill: 'var(--plp-radius-pill)',
      },
      boxShadow: {
        none: 'none',
      },
      screens: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px',
      },
      transitionDuration: {
        DEFAULT: '150ms',
      },
    },
  },
  plugins: [],
} satisfies Config
