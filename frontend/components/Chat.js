const Chat = {
    // Get DOM element references and setup event listeners
    init() {
        this.chatMessages = document.getElementById('chatMessages');
        this.sendButton = document.getElementById('sendButton');
        this.uploadButton = document.getElementById('uploadButton');
        this.setupEventListeners();
    },

    // Setup event listeners for sending messages (clicking sendButton or pressing Enter)
    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.handleSendMessage());
        if (this.uploadButton) {
            this.uploadButton.addEventListener('click', () => this.handleUploadReport());
        }

        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && e.target.id === 'messageInput') {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
    },

    // Render a user's message
    addUserMessage(text) {
        const messageElement = Message.createUserMessage(text);
        this.chatMessages.appendChild(messageElement);
    },

    // Called when a user pressed send button
    async handleSendMessage() {
        const message = DOMUtils.getInputValue();
        if (message) {
            this.addUserMessage(message); // Render user message in chat
            DOMUtils.clearInput(); // Clear input
            UIManager.scrollToBottom(); // Scoll to bottom of chat container
            await this.getAIResponse(message); // Send user message and wait for response
        }
    },

    // Called when user pressess upload button
    async handleUploadReport() {
        try {
            // Open directory selector and wait for result
            const selectResult = await UploadService.selectDirectory();

            // If no result, return
            if (!selectResult.success) {
                return;
            }

            // Send chosen directory path to the backend and wait for reponse
            const uploadResult = await UploadService.uploadReport(selectResult.directory_path);

            if (uploadResult.success) {
                // Upload successful
                console.log('Report upload started successfully');
            }
        } catch (error) {
            console.error('Upload failed:', error);
        }
    },

    // Sends user prompt and recieves AI response
    async getAIResponse(message) {
        // Create the container for the AI streaming message
        const streamingMessage = Message.createStreamingMessage(); 
        this.chatMessages.appendChild(streamingMessage);

        try {
            await AIService.sendMessage(
                message,
                (accumulatedText) => { // Receive accumulated text as tokens stream in
                    Message.updateStreamingMessage(streamingMessage, accumulatedText); // Update streaming message in real time

                    // Handle auto-scroll
                    if (UIManager.shouldAutoScroll()) {
                        UIManager.scrollToBottom();
                    }
                },
                (finalText) => {
                    // Completion callback
                    Message.updateStreamingMessage(streamingMessage, finalText);
                },
                () => {
                    // Error callback
                    Message.setErrorMessage(streamingMessage, 'Sorry, there was an error processing your request.');
                }
            );
        } catch (error) {
            console.error('Error in getAIResponse:', error);
            Message.setErrorMessage(streamingMessage, 'Sorry, there was an error processing your request.');
        }
    }
};