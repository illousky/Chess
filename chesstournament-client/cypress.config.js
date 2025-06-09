const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    specPattern: 'cypress/e2e/**/*.{cy,spec}.{js,jsx,ts,tsx}',
    baseUrl: 'http://localhost:5173'
  },
  component: {
    specPattern: 'src/**/__tests__/*.{cy,spec}.{js,ts,jsx,tsx}',
    devServer: {
      framework: 'vue',
      bundler: 'vite'
    }
  },
  env: {
    username: "alumnodb",
    password: "alumnodb",
    python: "/home/ignaciioglezz/Escritorio/UNIVERSIDAD/5o_ano/PSI/psi-lab4/p4_env/bin/python",
    // python: "/home/nacho/Documentos/psi-lab4/chesstournament/p4_env/bin/python",
//    manage: "/home/roberto/Docencia/psi/2024-25/chesstournament/chesstournament_server/manage.py",
    manage: "/home/ignaciioglezz/Escritorio/UNIVERSIDAD/5o_ano/PSI/psi-lab4/chesstournament/manage.py",
    // manage: "/home/nacho/Documentos/psi-lab4/chesstournament/manage.py",
  },
})
