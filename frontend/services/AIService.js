const AIService = {
    // Send message to AI and handle streaming response
    sendMessage(message, onToken, onComplete, onError) {
        return new Promise((resolve, reject) => {
            try {
                // Create EventSource for real time streaming connection to backend
                const eventSource = new EventSource(`http://localhost:8000/chat?message=${encodeURIComponent(message)}`);

                let accumulatedText = '';

                // Handle incoming streaming messages from server
                eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);

                        // Process individual AI response tokens
                        if (data.token) {
                            accumulatedText += data.token;
                            if (onToken) {
                                onToken(data.token, accumulatedText);
                            }
                        }
                        // Handle streaming completion
                        else if (data.done) {
                            if (onComplete) {
                                onComplete(accumulatedText);
                            }
                            // Close connection and resolve Promise with final text
                            eventSource.close();
                            resolve(accumulatedText);
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                };

                // Handle connection errors
                eventSource.onerror = (error) => {
                    console.error('EventSource error:', error);
                    eventSource.close();
                    if (onError) {
                        onError('Connection error');
                    }
                    reject(new Error('Streaming connection failed'));
                };

                // Handle successful connection establishment
                eventSource.onopen = () => {
                    console.log('Streaming connection established');
                };

            } catch (error) {
                console.error('AI Service Error:', error);
                if (onError) {
                    onError(error.message);
                }
                reject(error);
            }
        });
    }
};