const Message = {
    createMessage(text, className, processor = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        const content = processor ? processor(text) : text;
        messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
        return messageDiv;
    },

    createUserMessage(text) {
        return Message.createMessage(text, 'user-message');
    },

    createAIMessage(text) {
        return Message.createMessage(text, 'ai-message', (content) => marked.parse(content));
    },

    createErrorMessage(errorText) {
        return Message.createMessage(errorText, 'ai-message error');
    }
};