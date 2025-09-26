const UIManager = {
    init() {
        // View Management
        this.agentView = document.getElementById('agentView');
        this.settingsView = document.getElementById('settingsView');
        this.agentNav = document.querySelector('.agent-nav');
        this.settingsNav = document.querySelector('.settings-nav');

        // Scroll Management
        this.userScrolledUp = false;
        this.lastScrollTop = 0;
        this.chatMessages = document.getElementById('chatMessages');

        // Input Management
        this.messageInput = document.getElementById('messageInput');

        this.setupEventListeners();
        this.showAgentView(); // Show agent view by default
    },

    setupEventListeners() {
        // View event listeners
        if (this.agentNav) {
            this.agentNav.addEventListener('click', () => this.showAgentView());
        }
        if (this.settingsNav) {
            this.settingsNav.addEventListener('click', () => this.showSettingsView());
        }

        // Scroll event listeners
        if (this.chatMessages) {
            this.chatMessages.addEventListener('scroll', () => {
                const currentScrollTop = this.chatMessages.scrollTop;

                if (currentScrollTop < this.lastScrollTop) {
                    this.userScrolledUp = true; // If user scrolled up
                } else if (this.isNearBottom()) {
                    this.userScrolledUp = false; // If user is scrolling down and is near bottom
                }

                this.lastScrollTop = currentScrollTop;
            });
        }

        // Input
        if (this.messageInput) {
            this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
        }
    },

    // View Management Methods
    showAgentView() {
        if (this.agentView) this.agentView.style.display = 'flex';
        if (this.settingsView) this.settingsView.style.display = 'none';
        if (this.agentNav) this.agentNav.classList.add('active');
        if (this.settingsNav) this.settingsNav.classList.remove('active');
    },

    showSettingsView() {
        if (this.agentView) this.agentView.style.display = 'none';
        if (this.settingsView) this.settingsView.style.display = 'block';
        if (this.agentNav) this.agentNav.classList.remove('active');
        if (this.settingsNav) this.settingsNav.classList.add('active');
    },

    // Scroll Management Methods
    scrollToBottom() {
        if (this.chatMessages) {
            this.chatMessages.scrollTo({
                top: this.chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }
    },

    // Check if user is within 100 pixels of the bottom of the chat container
    isNearBottom() {
        if (!this.chatMessages) return false;
        const threshold = 100;
        return this.chatMessages.scrollHeight - this.chatMessages.scrollTop - this.chatMessages.clientHeight <= threshold;
    },

    shouldAutoScroll() {
        return !this.userScrolledUp;
    }
};