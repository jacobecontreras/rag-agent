const Chat = {
    init() {
        this.chatMessages = document.getElementById('chatMessages');
        this.sendButton = document.getElementById('sendButton');
        this.uploadButton = document.getElementById('uploadButton');
        this.apiKeyInput = document.getElementById('apiKeyInput');
        this.saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
        this.messageInput = document.getElementById('messageInput');
        this.isStreaming = false;
        this.currentResponse = null;

        this.loadApiKey();
        this.setupEventListeners();
    },

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => {
            this.isStreaming ? this.handleStopGeneration() : this.handleSendMessage();
        });

        this.uploadButton.addEventListener('click', () => this.handleUploadReport());
        this.saveApiKeyBtn.addEventListener('click', () => this.saveApiKey());

        this.apiKeyInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.saveApiKey();
        });

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
            if (uploadResult.success) {
                this.addUserMessage('Report uploaded successfully!');
            }
        } catch (error) {
            console.error('Upload failed:', error);
        }
    },

    async getAIResponse(message) {
        const streamingMessage = Message.createStreamingMessage();
        this.chatMessages.appendChild(streamingMessage);
        UIManager.scrollToBottom();

        try {
            const response = AIService.sendMessage(
                message,
                (token, accumulatedText) => {
                    Message.updateStreamingMessage(streamingMessage, accumulatedText);
                    if (UIManager.shouldAutoScroll()) {
                        UIManager.scrollToBottom();
                    }
                },
                (finalText) => {
                    Message.updateStreamingMessage(streamingMessage, finalText);
                    this.clearStreamingState();
                    this.setStreamingState(false);
                },
                () => {
                    Message.setErrorMessage(streamingMessage, 'Sorry, there was an error processing your request.');
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
    },

    loadApiKey() {
        const savedKey = localStorage.getItem('zai_api_key');
        if (savedKey) this.apiKeyInput.value = savedKey;
    },

    saveApiKey() {
        const apiKey = this.apiKeyInput.value.trim();
        if (apiKey) {
            localStorage.setItem('zai_api_key', apiKey);
        } else {
            localStorage.removeItem('zai_api_key');
        }
    }
};