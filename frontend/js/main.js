// Initialize all modules when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    viewManager.init();
    uiHelpers.init();
    scrollManager.init();
    chatService.init();
});