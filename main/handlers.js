const { ipcMain, dialog } = require('electron');
const { getMainWindow } = require('./window');

function registerHandlers() {
  // Handle directory selection
  ipcMain.handle('select-directory', async () => {
    const mainWindow = getMainWindow();

    if (!mainWindow) {
      return JSON.stringify({ success: false, error: 'No main window available' });
    }

    try {
      const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        title: 'Select LEAPP Report Directory'
      });

      if (result.canceled) {
        return JSON.stringify({ success: false, error: 'User cancelled directory selection' });
      } else {
        return JSON.stringify({ success: true, directory_path: result.filePaths[0] });
      }
    } catch (error) {
      console.error('Directory selection error:', error);
      return JSON.stringify({ success: false, error: error.message });
    }
  });
}

function unregisterHandlers() {
  // Remove all handlers when app is closing
  ipcMain.removeHandler('select-directory');
}

module.exports = {
  registerHandlers,
  unregisterHandlers
};