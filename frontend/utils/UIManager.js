const UIManager = {
    init() {
        // Scroll Management
        this.userScrolledUp = false;
        this.lastScrollTop = 0;
        this.chatMessages = document.getElementById('chatMessages');

        // Input Management
        this.messageInput = document.getElementById('messageInput');

        this.setupEventListeners();
    },

    setupEventListeners() {
        // Scroll event listeners
        this.chatMessages.addEventListener('scroll', () => {
            const currentScrollTop = this.chatMessages.scrollTop;

            if (currentScrollTop < this.lastScrollTop) {
                this.userScrolledUp = true; // If user scrolled up
            } else if (this.isNearBottom()) {
                this.userScrolledUp = false; // If user is scrolling down and is near bottom
            }

            this.lastScrollTop = currentScrollTop;
        });

        // Input
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
    },

    // Scroll Management Methods
    scrollToBottom() {
        this.chatMessages.scrollTo({
            top: this.chatMessages.scrollHeight
        });
    },

    // Check if user is within 100 pixels of the bottom of the chat container
    isNearBottom() {
        const threshold = 100;
        return this.chatMessages.scrollHeight - this.chatMessages.scrollTop - this.chatMessages.clientHeight <= threshold;
    },

    shouldAutoScroll() {
        return !this.userScrolledUp;
    },

    // Auto-resize textarea based on content
    autoResizeTextarea() {
        if (this.messageInput) {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        }
    }
};