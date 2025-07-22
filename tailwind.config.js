/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',           // Django template chính
    './**/templates/**/*.html',        // Template trong app Django con
    './static/**/*.js',                // Nếu có file JS
  ],
  theme: {
    extend: {
      fontFamily: {
      inter: ['Inter', 'sans-serif']
    }
    },
  },
  plugins: [],
}
