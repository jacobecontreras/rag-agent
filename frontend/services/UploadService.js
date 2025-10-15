// Base URL for backend API
const API_BASE_URL = 'http://localhost:8000';

// Service for handling file uploads
const UploadService = {
    // Open directory picker via Electron API
    async selectDirectory() {
        return await window.electronAPI.selectDirectory();
    },

    // Send report directory path to backend
    async uploadReport(directoryPath) {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory_path: directoryPath })
        });

        return await response.json();
    }
};