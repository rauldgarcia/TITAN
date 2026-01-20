/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        slate: {
          850: '#151e2e',
          950: '#020617',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
  safelist: [
    // Backgrounds Base
    'bg-red-500', 'bg-amber-500', 'bg-emerald-500',
    // Backgrounds with Opacity (Glass effect)
    'bg-red-500/10', 'bg-amber-500/10', 'bg-emerald-500/10',
    // Borders
    'border-red-500/20', 'border-amber-500/20', 'border-emerald-500/20',
    // Texts
    'text-red-400', 'text-amber-400', 'text-emerald-400',
    // Shadows (Glow effect)
    'shadow-[0_0_10px_rgba(244,63,94,0.1)]', 
    // Utilities
    'animate-pulse', 'w-full', 'py-1.5', 'rounded'
  ]
}