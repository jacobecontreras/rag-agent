// Entry point for the Electron main process
const path = require('path');
const { app, BrowserWindow } = require('electron');
const { startBackend, stopBackend } = require('./backend');
const { registerHandlers, unregisterHandlers } = require('./handlers');
const { createWindow } = require('./frontend');

// Hot reload functionality in development
if (process.env.NODE_ENV === 'development') {
  console.log('Setting up hot reload...');

  try {
    // Electron-reload setup
    require('electron-reload')([
      __dirname,  // Watch main process files
      path.join(__dirname, '..', 'frontend')  // Watch frontend files
    ], {
      hardResetMethod: 'exit'
    });
    console.log('Hot reload enabled for main process and frontend');
  } catch (err) {
    console.log('electron-reload setup failed:', err.message);
    console.log('Backend hot reload still works automatically');
  }
}

function initializeApp() {
  // Handle app ready event
  app.whenReady().then(() => {
    const mainWindow = createWindow(); // Start frontend
    startBackend(); // Start backend
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