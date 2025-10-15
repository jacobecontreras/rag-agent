// Message component for creating chat messages
const Message = {
    // Create a generic message with optional content processing
    createMessage(text, className, processor = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        const content = processor ? processor(text) : text;
        messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
        return messageDiv;
    },

    // Create user message
    createUserMessage(text) {
        return Message.createMessage(text, 'user-message');
    },

    // Create AI message with markdown parsing
    createAIMessage(text) {
        return Message.createMessage(text, 'ai-message', (content) => marked.parse(content));
    },

    // Create error message
    createErrorMessage(errorText) {
        return Message.createMessage(errorText, 'ai-message error');
    }
};