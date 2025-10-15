const Chat = {
    elements: {},

    init() {
        this.elements = {
            chatMessages: document.getElementById('chatMessages'),
            sendButton: document.getElementById('sendButton'),
            uploadButton: document.getElementById('uploadButton'),
            messageInput: document.getElementById('messageInput')
        };

        this.setupEventListeners();
    },

    setupEventListeners() {
        const { sendButton, uploadButton } = this.elements;

        sendButton.addEventListener('click', () => this.handleSendMessage());
        uploadButton.addEventListener('click', () => this.handleUploadReport());

        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && e.target.id === 'messageInput') {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
    },

    addMessage(messageCreator, text) {
        const message = messageCreator(text);
        this.elements.chatMessages.appendChild(message);
        UIManager.scrollToBottom();
    },

    async handleSendMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message) return;

        this.addMessage(Message.createUserMessage, message);
        this.clearInput();
        await this.getAIResponse(message);
    },

    async handleUploadReport() {
        try {
            const selectResult = await UploadService.selectDirectory();
            if (selectResult?.success) {
                await UploadService.uploadReport(selectResult.directory_path);
            }
        } catch (error) {
            console.error('Upload failed:', error);
        }
    },

    async getAIResponse(message) {
        try {
            const aiResponse = await AIService.sendMessage(message);
            this.addMessage(Message.createAIMessage, aiResponse);
        } catch (error) {
            console.error('Error in getAIResponse:', error);
            this.addMessage(Message.createErrorMessage, 'Sorry, there was an error processing your request.');
        }
    },

    clearInput() {
        this.elements.messageInput.value = '';
        UIManager.autoResizeTextarea();
    }
};