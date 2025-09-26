const Message = {
    // Used to render user messages in chat
    createUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `<div class="message-content">${text}</div>`;
        return messageDiv;
    },

    // Used to render streaming messages in chat
    createStreamingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message streaming';
        messageDiv.innerHTML = '<div class="message-content"></div>';
        return messageDiv;
    },

    // Used to update streaming messages in real time in chat
    updateStreamingMessage(messageElement, content) {
        const messageContent = messageElement.querySelector('.message-content');
        messageContent.innerHTML = marked.parse(content);

        // Remove streaming class immediately when content is received
        if (messageElement.classList.contains('streaming')) {
            messageElement.classList.remove('streaming');
        }
    },

    // Users to render error messages in chat
    setErrorMessage(messageElement, errorText) {
        const messageContent = messageElement.querySelector('.message-content');
        messageContent.textContent = errorText;
        messageElement.classList.remove('streaming');
    }
};