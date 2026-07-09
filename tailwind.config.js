/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ok: '#22c55e',
        warn: '#eab308',
        no: '#ef4444',
        pet: {
          50: '#fff8f0',
          100: '#ffefdb',
          200: '#ffdcb0',
          300: '#ffc37d',
          400: '#ffa94d',
          500: '#ff8c1a',
        },
      },
      borderRadius: {
        xl2: '1.25rem',
      },
    },
  },
  plugins: [],
}
