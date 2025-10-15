const UIManager = {
    init() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');

        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
    },

    scrollToBottom() {
        this.chatMessages.scrollTo({
            top: this.chatMessages.scrollHeight
        });
    },

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = `${this.messageInput.scrollHeight}px`;
    }
};