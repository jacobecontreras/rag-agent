const scrollManager = {
    init() {
        this.userScrolledUp = false;
        this.lastScrollTop = 0; // Stores previous scroll position
        this.chatMessages = document.getElementById('chatMessages');
        this.setupEventListeners();
    },

    scrollToBottom() {
        this.chatMessages.scrollTo({
            top: this.chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    },

    isNearBottom() {
        const threshold = 100;
        return this.chatMessages.scrollHeight - this.chatMessages.scrollTop - this.chatMessages.clientHeight <= threshold;
    },

    setupEventListeners() {
        this.chatMessages.addEventListener('scroll', () => {
            const currentScrollTop = this.chatMessages.scrollTop;

            if (currentScrollTop < this.lastScrollTop) {
                this.userScrolledUp = true; // If user scrolled up 
            } else if (this.isNearBottom()) {
                this.userScrolledUp = false; // If user is scrolling down and is near bottom 
            }

            this.lastScrollTop = currentScrollTop;
        });
    },

    shouldAutoScroll() {
        return !this.userScrolledUp;
    }
};