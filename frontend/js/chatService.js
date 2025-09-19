const chatService = {
    init() {
        this.chatMessages = document.getElementById('chatMessages');
        this.sendButton = document.getElementById('sendButton');
        this.setupEventListeners();
    },

    // Set up keypress and click event listeners for enter key and sendButton clicks
    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.handleSendMessage());

        document.addEventListener('keypress', (e) => {
            // Check if enter key is down (and shift is not, so we allows 'Shift + Enter' linebreaks)
            if (e.key === 'Enter' && !e.shiftKey && e.target.id === 'messageInput') {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
    },

    // Sends prompt to AI through OpenRouter (called when you click sendButton or press enter)
    async handleSendMessage() {
        const message = uiHelpers.getInputValue();
        if (message) {
            this.addUserMessage(message);
            uiHelpers.clearInput();

            setTimeout(() => scrollManager.scrollToBottom(), 100);

            await this.getAIResponse(message);
        }
    },

    async getAIResponse(message) {
        const streamingMessage = this.createStreamingMessage();
        const messageContent = streamingMessage.querySelector('.message-content');
        let accumulatedText = '';

        try {
            // Send user prompt and get response
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const reader = response.body.getReader(); // Setup stream reader
            const decoder = new TextDecoder(); // Setup binary to text

            // Process each chunk of data as it arrives
            while (true) {
                const { done, value } = await reader.read();
                if (done) break; // Stream complete, break

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.token) {
                                accumulatedText += data.token;
                                messageContent.innerHTML = marked.parse(accumulatedText); // Render with markdown 

                                if (streamingMessage.classList.contains('streaming')) {
                                    streamingMessage.classList.remove('streaming');
                                }

                                if (scrollManager.shouldAutoScroll()) {
                                    scrollManager.scrollToBottom();
                                }
                            } else if (data.done) {
                                streamingMessage.classList.remove('streaming');
                            }
                        } catch (e) {
                            // Ignore parsing errors
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Error:', error);
            messageContent.textContent = 'Sorry, there was an error processing your request.';
            streamingMessage.classList.remove('streaming');
        }
    },

    addUserMessage(message) {
        this.chatMessages.innerHTML += `<div class="message user-message"><div class="message-content">${message}</div></div>`;
    },

    // Adds an empty AI bubble to the chat (to be populated with AI output)
    createStreamingMessage() {
        const streamingMessage = document.createElement('div');
        streamingMessage.className = 'message ai-message streaming';
        streamingMessage.innerHTML = '<div class="message-content"></div>';
        this.chatMessages.appendChild(streamingMessage);
        return streamingMessage;
    }
};