const API_BASE_URL = 'http://localhost:8000';

const UploadService = {
    async selectDirectory() {
        return await window.electronAPI.selectDirectory();
    },

    async uploadReport(directoryPath) {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory_path: directoryPath })
        });

        return await response.json();
    }
};