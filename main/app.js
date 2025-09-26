const { app, BrowserWindow } = require('electron');
const { createWindow } = require('./window');
const { startBackend, stopBackend } = require('./backend');
const { registerHandlers, unregisterHandlers } = require('./handlers');

function initializeApp() {
  // Handle app ready event
  app.whenReady().then(() => {
    createWindow();
    startBackend();
    registerHandlers();

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

module.exports = {
  initializeApp
};