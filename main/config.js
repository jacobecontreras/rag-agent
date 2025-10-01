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
    icon: path.join(__dirname, '..', 'frontend', 'assets', 'logo.png'),
    backendScript: 'backend/main.py'
  },

  // Backend configuration
  backend: {
    pythonCommand: 'python3',
    args: ['-c', 'import sys; sys.path.insert(0, "backend"); import main; import uvicorn; uvicorn.run(main.app, host="0.0.0.0", port=8000)'],
    cwd: path.join(__dirname, '..'),
    stdio: 'pipe'
  },

  // Development settings
  dev: {
    openDevTools: true
  }
};