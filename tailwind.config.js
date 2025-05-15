module.exports = {
  content: ['./templates/**/*.html', './src/**/*.{js,css}', '**/*.py'],
  theme: {
    extend: {},
  },
  safelist: ['alert-success', 'alert-error', 'alert-info', 'alert-warning'],
  plugins: [require('daisyui')],
};
