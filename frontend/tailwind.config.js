/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    // A deliberately small, editorial radius scale — no oversized pills.
    borderRadius: {
      none: '0',
      sm: '2px',
      DEFAULT: '4px',
      md: '6px',
      lg: '8px',
      full: '9999px',
    },
    extend: {
      colors: {
        // Warm "paper" canvas + surfaces.
        paper: {
          DEFAULT: '#F3F0E8', // app canvas
          card: '#FCFBF7', // raised surfaces
          sunk: '#ECE7DB', // wells / hovers
        },
        // Near-black ink, with softer tiers for secondary/tertiary text.
        ink: {
          DEFAULT: '#21201B',
          soft: '#56524A',
          faint: '#8B8579',
        },
        // Hairline rules.
        line: {
          DEFAULT: '#E0DBCE',
          strong: '#CBC4B2',
        },
        // Single chromatic accent: clay / terracotta.
        accent: {
          DEFAULT: '#B0532B',
          hover: '#984524',
          soft: '#F1E4DA',
          line: '#E2C9B8',
        },
        // Functional status colors (earthy, not neon).
        ok: { DEFAULT: '#3C7A4E', soft: '#E6EEE5', line: '#CADBC6' },
        wait: { DEFAULT: '#9A781F', soft: '#F1E9D2', line: '#E0D2A8' },
        err: { DEFAULT: '#A23A2A', soft: '#F2E0DB', line: '#E5C5BC' },
      },
      fontFamily: {
        // Editorial serif for the wordmark + titles.
        display: ['Fraunces', 'Georgia', 'ui-serif', 'serif'],
        // Humanist grotesk for UI/body (intentionally not Inter).
        sans: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        // Mono for data, IDs and timestamps.
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        // Used sparingly — a single soft lift, never a glow.
        lift: '0 1px 0 0 #E0DBCE, 0 8px 24px -16px rgba(33,32,27,0.35)',
      },
      letterSpacing: {
        eyebrow: '0.12em',
      },
    },
  },
  plugins: [],
}
