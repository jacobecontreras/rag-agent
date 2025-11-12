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

    // Used to update streaming messages with structured data (agent process + final answer)
    updateStreamingMessageWithStructuredData(messageElement, agentProcessText, finalAnswerText) {
        const messageContent = messageElement.querySelector('.message-content');

        // Check if agent process container already exists
        let processContainer = messageContent.querySelector('.agent-process-container');
        let answerContainer = messageContent.querySelector('.final-answer-content');

        // Create agent process container if it doesn't exist and there's agent process
        if (agentProcessText && !processContainer) {
            processContainer = document.createElement('div');
            processContainer.className = 'agent-process-container expanded';

            const toggleButton = document.createElement('button');
            toggleButton.className = 'agent-process-toggle';
            toggleButton.textContent = 'Agent Process';

            const processContent = document.createElement('div');
            processContent.className = 'agent-process-content';
            processContent.textContent = agentProcessText;

            toggleButton.onclick = () => {
                processContainer.classList.toggle('expanded');
            };

            processContainer.appendChild(toggleButton);
            processContainer.appendChild(processContent);

            // Insert agent process container before final answer container to maintain proper order
            if (answerContainer) {
                messageContent.insertBefore(processContainer, answerContainer);
            } else {
                messageContent.appendChild(processContainer);
            }
        } else if (agentProcessText && processContainer) {
            // Update existing agent process content
            const processContent = processContainer.querySelector('.agent-process-content');
            processContent.innerHTML = agentProcessText.replace(/^→ (.+)$/gm, '<span class="action-text">$1</span>');
        }

        // Create or update final answer container
        if (finalAnswerText) {
            if (!answerContainer) {
                answerContainer = document.createElement('div');
                answerContainer.className = 'final-answer-content';
                messageContent.appendChild(answerContainer);
            }
            // Convert literal \n to actual line breaks for proper markdown rendering
            const processedText = finalAnswerText.replace(/\\n/g, '\n');
            answerContainer.innerHTML = marked.parse(processedText);
        }

        // Remove streaming class when final answer is received
        if (finalAnswerText && messageElement.classList.contains('streaming')) {
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