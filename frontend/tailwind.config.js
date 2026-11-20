/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: { navy: { 950: '#0b1424', 900: '#101a2d', 800: '#16233b', 700: '#1f2f4d' }, ivory: '#f4f1ea', lime: '#c8fc57', gold: '#e5b87d' },
      fontFamily: { sans: ['"DM Sans"', 'system-ui', 'sans-serif'], serif: ['"Playfair Display"', 'Georgia', 'serif'], mono: ['"DM Mono"', 'ui-monospace', 'monospace'] },
    },
  },
  plugins: [],
};
