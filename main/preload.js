const { ipcRenderer } = require('electron');

window.electronAPI = {
    selectDirectory: () => ipcRenderer.invoke('select-directory')
};