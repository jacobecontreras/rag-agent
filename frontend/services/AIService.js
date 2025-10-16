// AI service for handling backend chat API calls
const AIService = {
    // Sends a message to backend chat API and gets a response
    async sendMessage(message) {
        const response = await fetch(`http://localhost:8000/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Backend API error! status: ${response.status}, details: ${errorText}`);
        }

        const data = await response.json();
        return data.response;
    }
};