// Entry point for the Electron main process
const { app, BrowserWindow } = require('electron');
const { startBackend, stopBackend } = require('./backend');
const { registerHandlers, unregisterHandlers } = require('./handlers');
const config = require('./config');
const path = require('path');

function createWindow() {
  const mainWindow = new BrowserWindow({
    ...config.window,
    icon: config.paths.icon
  });

  // Load the frontend
  mainWindow.loadFile(config.paths.frontend);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  return mainWindow;
}

function initializeApp() {
  // Handle app ready event
  app.whenReady().then(() => {
    const mainWindow = createWindow();
    startBackend();
    registerHandlers(mainWindow);

    // Handle app activation (macOS)
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  });

  // Handle window-all-closed event
  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });

  // Handle app quit event
  app.on('before-quit', () => {
    stopBackend();
    unregisterHandlers();
  });
}

// Initialize the application
initializeApp();