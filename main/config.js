const path = require('path');

module.exports = {
  // Window configuration
  window: {
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    show: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false,
      preload: path.join(__dirname, 'preload.js')
    }
  },

  // File paths
  paths: {
    frontend: path.join(__dirname, '..', 'frontend', 'index.html'),
    icon: path.join(__dirname, '..', 'frontend', 'assets', 'text.png'),
    backendScript: 'backend/main.py'
  },

  // Backend configuration
  backend: {
    pythonCommand: 'python3',
    args: ['backend/main.py'],
    stdio: 'pipe'
  },

  // Development settings
  dev: {
    openDevTools: true
  }
};