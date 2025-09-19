const viewManager = {
    init() {
        this.agentView = document.getElementById('agentView');
        this.settingsView = document.getElementById('settingsView');
        this.agentNav = document.querySelector('.agent-nav');
        this.settingsNav = document.querySelector('.settings-nav');

        this.setupEventListeners();
        this.showAgentView();
    },

    showAgentView() {
        this.agentView.style.display = 'flex';
        this.settingsView.style.display = 'none';
        this.agentNav.classList.add('active');
        this.settingsNav.classList.remove('active');
    },

    showSettingsView() {
        this.agentView.style.display = 'none';
        this.settingsView.style.display = 'block';
        this.agentNav.classList.remove('active');
        this.settingsNav.classList.add('active');
    },

    setupEventListeners() {
        this.agentNav.addEventListener('click', () => this.showAgentView());
        this.settingsNav.addEventListener('click', () => this.showSettingsView());
    }
};