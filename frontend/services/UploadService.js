const UploadService = {
    // Allow user directory selection using electron's API
    async selectDirectory() {
        try {
            const result = await window.electronAPI.selectDirectory();
            return JSON.parse(result);
        } catch (error) {
            console.error('Directory selection failed:', error);
            throw error;
        }
    },

    // Send the directory path for processing
    async uploadReport(directoryPath) {
        try {
            const response = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ directory_path: directoryPath })
            });

            return await response.json();
        } catch (error) {
            console.error('Upload failed:', error);
            throw error;
        }
    }
};