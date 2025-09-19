const uiHelpers = {
    init() {
        this.messageInput = document.getElementById('messageInput');
        this.setupEventListeners();
    },

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 150) + 'px'; // Limit height to 150px
    },

    setupEventListeners() {
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
    },

    clearInput() {
        this.messageInput.value = '';
        this.autoResizeTextarea();
    },

    getInputValue() {
        return this.messageInput.value;
    }
};