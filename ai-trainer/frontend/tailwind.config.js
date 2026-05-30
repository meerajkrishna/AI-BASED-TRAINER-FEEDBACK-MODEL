/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#E63E29',
          dark: '#CD1701',
          light: '#FFE8E0',
        },
        gray: {
          50: '#F9F9F9',
          100: '#F5F5F5',
          200: '#E0E0E0',
          300: '#CCCCCC',
          400: '#999999',
          500: '#808080',
          600: '#666666',
          700: '#333333',
          800: '#1F1F1F',
          900: '#0A0A0A',
        },
        success: '#4CAF50',
        info: '#2196F3',
        warning: '#FF9800',
        error: '#FF5722',
      },
      fontFamily: {
        display: ['Space Grotesk', 'Poppins', 'Inter', 'sans-serif'],
        sans: ['Poppins', 'Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      fontSize: {
        'hero': ['56px', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'subtitle': ['28px', { lineHeight: '1.3', letterSpacing: '0.01em' }],
      },
      boxShadow: {
        'card': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'card-hover': '0 8px 24px rgba(0, 0, 0, 0.12)',
        'button': '0 4px 12px rgba(230, 62, 41, 0.3)',
      },
      borderRadius: {
        'xl': '12px',
      },
    },
  },
  plugins: [],
}
