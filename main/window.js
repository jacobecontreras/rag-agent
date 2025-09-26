const { BrowserWindow } = require('electron');
const path = require('path');
const config = require('./config');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    ...config.window,
    icon: config.paths.icon
  });

  // Load the frontend
  mainWindow.loadFile(config.paths.frontend);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
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