/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        charney: {
          red: '#FF5959',
          black: '#000000',
          cream: '#F6F1EB',
          white: '#FFFFFF',
          gray: '#666666',
          'light-gray': '#E5E5E5',
        },
        primary: {
          DEFAULT: '#FF5959',
          50: '#fff1f1',
          100: '#ffe1e1',
          200: '#ffc7c7',
          300: '#ffa0a0',
          400: '#ff6969',
          500: '#FF5959',
          600: '#ed2626',
          700: '#c81d1d',
          800: '#a51d1d',
          900: '#881f1f',
        },
      },
      fontFamily: {
        sans: ['Franklin Gothic', 'Arial Narrow', 'Arial', 'sans-serif'],
        franklin: ['Franklin Gothic', 'Arial Narrow', 'Arial', 'sans-serif'],
      },
      spacing: {
        'xs': '8px',
        'sm': '16px',
        'md': '24px',
        'lg': '40px',
        'xl': '60px',
        '2xl': '80px',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
      },
      boxShadow: {
        'sm': '0 1px 3px rgba(0,0,0,0.08)',
        'md': '0 4px 12px rgba(0,0,0,0.1)',
        'lg': '0 8px 24px rgba(0,0,0,0.12)',
      },
    },
  },
  plugins: [],
}
