// Main Chat component, handles chat interface functionality
const Chat = {
    // For storing DOM element references
    elements: {},

    // Initialize chat component and cache DOM elements
    init() {
        this.elements = {
            chatMessages: document.getElementById('chatMessages'),
            sendButton: document.getElementById('sendButton'),
            uploadButton: document.getElementById('uploadButton'),
            messageInput: document.getElementById('messageInput')
        };

        this.setupEventListeners();
    },

    // Set up event listeners for chat interactions
    setupEventListeners() {
        const { sendButton, uploadButton } = this.elements;

        // Handles click events on send message and upload report buttons
        sendButton.addEventListener('click', () => this.handleSendMessage());
        uploadButton.addEventListener('click', () => this.handleUploadReport());

        // Handles Enter key for sending messages
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && e.target.id === 'messageInput') {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
    },

    // Add a message to the chat display
    addMessage(messageCreator, text) {
        const message = messageCreator(text);
        this.elements.chatMessages.appendChild(message);
        UIManager.scrollToBottom();
    },

    // Handle sending a user's message
    async handleSendMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message) return;

        this.addMessage(Message.createUserMessage, message);
        this.clearInput();
        await this.getAIResponse(message);
    },

    // Handle report upload functionality
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

    // Get AI response to user message
    async getAIResponse(message) {
        try {
            const aiResponse = await AIService.sendMessage(message);
            this.addMessage(Message.createAIMessage, aiResponse);
        } catch (error) {
            console.error('Error in getAIResponse:', error);
            this.addMessage(Message.createErrorMessage, 'Sorry, there was an error processing your request.');
        }
    },

    // Clear message input and resize textarea
    clearInput() {
        this.elements.messageInput.value = '';
        UIManager.autoResizeTextarea();
    }
};