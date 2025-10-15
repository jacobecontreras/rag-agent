// Frontend window setup and management
const { BrowserWindow } = require('electron');
const config = require('./config');

let mainWindow = null;

function createWindow() {
  // Create window object
  mainWindow = new BrowserWindow({
    ...config.window, // Spreads or unpacks each property of config.window into new object
    icon: config.paths.icon
  });

  // Load the frontend into window object
  mainWindow.loadFile(config.paths.frontend);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  return mainWindow;
}

function getMainWindow() {
  return mainWindow;
}

module.exports = {
  createWindow,
  getMainWindow
};