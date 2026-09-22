/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mospi: {
          navy: '#0F172A',
          dark: '#1E293B',
          card: '#182234',
          border: '#334155',
          primary: '#4F46E5',
          accent: '#38BDF8',
          success: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444',
          gold: '#FBBF24',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
