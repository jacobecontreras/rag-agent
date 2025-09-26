const DOMUtils = {
    autoResizeTextarea() {
        if (UIManager.messageInput) {
            UIManager.messageInput.style.height = 'auto';
            UIManager.messageInput.style.height = Math.min(UIManager.messageInput.scrollHeight, 150) + 'px';
        }
    },

    clearInput() {
        if (UIManager.messageInput) {
            UIManager.messageInput.value = '';
            this.autoResizeTextarea();
        }
    },

    getInputValue() {
        return UIManager.messageInput ? UIManager.messageInput.value : '';
    }
};