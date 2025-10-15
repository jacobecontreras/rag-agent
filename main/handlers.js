const { ipcMain, dialog } = require('electron');

function registerHandlers(mainWindow) {
  // Handle directory selection
  ipcMain.handle('select-directory', async () => {

    if (!mainWindow) {
      return { success: false, error: 'No main window available' };
    }

    try {
      const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        title: 'Select LEAPP Report Directory'
      });

      if (result.canceled) {
        return { success: false, error: 'User cancelled directory selection' };
      } else {
        return { success: true, directory_path: result.filePaths[0] };
      }
    } catch (error) {
      console.error('Directory selection error:', error);
      return { success: false, error: error.message };
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