/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',           // Template chính
    './**/templates/**/*.html',        // Template trong app con
    './static/**/*.js',                // Nếu có JS dùng class Tailwind
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}