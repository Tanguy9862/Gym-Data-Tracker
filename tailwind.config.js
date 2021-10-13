const plugin = require("tailwindcss/plugin")

module.exports = {
  purge: {
    enabled: false,
    content: []
  },
  darkMode: false, // or 'media' or 'class'
  theme: {    
    fontFamily:{
      body: ['Poppins']
    },
    fontSize:{
      'xxxs': '0.5rem',
      'xxs':'0.625rem',
      'xs': '.75rem',
      'sm': '.875rem',
      'tiny': '.875rem',
      'base': '1rem',
      'lg': '1.125rem',
      'xl': '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
      '5xl': '3rem',
      '6xl': '4rem',
      '7xl': '5rem',
    },
    colors: {
      white: "#FFF",
      blue: {
        700: "#182952"
      },
      purple: {
        400: "#6E44AD"
      },
      red: {
        300: "#E26890"
      },
      green: {
        400: "#1DAC90"
      }
    },
    extend: {},
  },
  variants: {},
  corePlugins: {
    wordBreak: false
  },
  plugins: [
    plugin(function ({ addUtilities }) {
      addUtilities({
        '.break-words': {
          'overflow-wrap': 'break-word',
          'word-break': 'break-word'
        }
      }, ['responsive'])
    })
  ]
}