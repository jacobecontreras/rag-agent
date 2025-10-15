// UI manager for handling interface interactions
const UIManager = {
    // Initialize UI elements and set up event listeners
    init() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');

        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
    },

    // Scroll chat messages to bottom
    scrollToBottom() {
        this.chatMessages.scrollTo({
            top: this.chatMessages.scrollHeight
        });
    },

    // Auto-resize textarea based on content
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = `${this.messageInput.scrollHeight}px`;
    }
};