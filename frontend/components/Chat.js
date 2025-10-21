const Chat = {
    init() {
        this.chatMessages = document.getElementById('chatMessages');
        this.sendButton = document.getElementById('sendButton');
        this.uploadButton = document.getElementById('uploadButton');
        this.messageInput = document.getElementById('messageInput');
        this.isStreaming = false;
        this.currentResponse = null;

        this.setupEventListeners();
    },

    setupEventListeners() {
        // Listeners for send/stop message button
        this.sendButton.addEventListener('click', () => {
            this.isStreaming ? this.handleStopGeneration() : this.handleSendMessage();
        });

        // Listeners for upload report button
        this.uploadButton.addEventListener('click', () => this.handleUploadReport());

        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && e.target.id === 'messageInput' && !this.isStreaming) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
    },

    getInputValue() {
        return this.messageInput.value;
    },

    clearInput() {
        this.messageInput.value = '';
        UIManager.autoResizeTextarea();
    },

    addUserMessage(text) {
        this.chatMessages.appendChild(Message.createUserMessage(text));
    },

    async handleSendMessage() {
        const message = this.getInputValue();
        if (!message) return;

        this.addUserMessage(message);
        this.clearInput();
        this.setStreamingState(true);
        await this.getAIResponse(message);
    },

    handleStopGeneration() {
        if (this.currentResponse?.abort) {
            this.currentResponse.abort();
        }
        this.clearStreamingState();
        this.setStreamingState(false);
    },

    setStreamingState(isStreaming) {
        this.isStreaming = isStreaming;
        this.sendButton.classList.toggle('stop-button', isStreaming);
    },

    clearStreamingState() {
        this.currentResponse = null;
        this.chatMessages.querySelectorAll('.ai-message.streaming')
            .forEach(msg => msg.classList.remove('streaming'));
    },

    async handleUploadReport() {
        try {
            const selectResult = await UploadService.selectDirectory();
            if (!selectResult.success) return;

            const uploadResult = await UploadService.uploadReport(selectResult.directory_path);
        } catch (error) {
            console.error('Upload failed:', error);
        }
    },

    async getAIResponse(message) {
        const streamingMessage = Message.createStreamingMessage();
        this.chatMessages.appendChild(streamingMessage);
        UIManager.scrollToBottom();

        let agentProcessText = '';
        let finalAnswerText = '';

        try {
            const response = AIService.sendMessage(
                message,
                (responseChunk) => {
                    if (responseChunk.type === 'agent_process') {
                        agentProcessText += responseChunk.content;
                        Message.updateStreamingMessageWithStructuredData(streamingMessage, agentProcessText, finalAnswerText);
                    } else if (responseChunk.type === 'final_answer_partial') {
                        finalAnswerText = responseChunk.content;
                        Message.updateStreamingMessageWithStructuredData(streamingMessage, agentProcessText, finalAnswerText);
                    } else if (responseChunk.type === 'final_answer') {
                        finalAnswerText = responseChunk.content;
                        Message.updateStreamingMessageWithStructuredData(streamingMessage, agentProcessText, finalAnswerText);
                    }

                    if (UIManager.shouldAutoScroll()) {
                        UIManager.scrollToBottom();
                    }
                },
                () => {
                    Message.updateStreamingMessageWithStructuredData(streamingMessage, agentProcessText, finalAnswerText);
                    this.clearStreamingState();
                    this.setStreamingState(false);
                },
                (error) => {
                    Message.setErrorMessage(streamingMessage, error);
                    this.clearStreamingState();
                    this.setStreamingState(false);
                }
            );

            this.currentResponse = response;
            await response.promise;
        } catch (error) {
            console.error('Error in getAIResponse:', error);
            Message.setErrorMessage(streamingMessage, 'Sorry, there was an error processing your request.');
            this.clearStreamingState();
            this.setStreamingState(false);
        }
    }
};