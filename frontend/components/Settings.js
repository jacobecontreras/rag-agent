class Settings {
    constructor() {
        this.apiKeyInput = document.getElementById('apiKeyInput');
        this.modelSelect = document.getElementById('modelSelect');
        this.newRuleInput = document.getElementById('newRuleInput');
        this.addRuleBtn = document.getElementById('addRuleBtn');
        this.rulesList = document.getElementById('rulesList');
        this.rules = [];
        this.apiBase = 'http://localhost:8000';

        this.init();
    }

    init() {
        this.loadSettings();
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                this.switchTab(e.target.dataset.tab);
            }
        });

        // Save API key when changed
        this.apiKeyInput?.addEventListener('input', () => {
            this.saveApiKey();
        });

        // Save model when changed
        this.modelSelect?.addEventListener('change', () => {
            this.saveModel();
        });

        // Add rule button
        this.addRuleBtn?.addEventListener('click', () => {
            this.addRule();
        });

        // Enter key to add rule
        this.newRuleInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.addRule();
            }
        });

        // Rules list event delegation
        this.rulesList?.addEventListener('click', (e) => {
            const ruleItem = e.target.closest('.rule-item');
            if (!ruleItem) return;

            const ruleId = ruleItem.dataset.ruleId;

            if (e.target.closest('.edit-btn')) {
                this.editRule(ruleId);
            } else if (e.target.closest('.delete-btn')) {
                this.deleteRule(ruleId);
            }
        });
    }

    switchTab(tabName) {
        // Remove active class from all tabs and panes
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });

        // Add active class to selected tab and pane
        document.querySelector(`.tab-btn[data-tab="${tabName}"]`)?.classList.add('active');
        document.querySelector(`.tab-pane[data-tab="${tabName}"]`)?.classList.add('active');
    }

    async saveApiKey() {
        const apiKey = this.apiKeyInput.value.trim();

        const response = await fetch(`${this.apiBase}/settings`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ api_key: apiKey })
        });

        if (!response.ok) {
            throw new Error('Failed to save API key to database');
        }
    }

    async saveModel() {
        const model = this.modelSelect.value;

        const response = await fetch(`${this.apiBase}/settings`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ model: model })
        });

        if (!response.ok) {
            throw new Error('Failed to save model to database');
        }
    }

    // Rule Management Methods
    addRule() {
        const ruleText = this.newRuleInput.value.trim();
        if (!ruleText) return;

        const rule = {
            id: Date.now().toString(),
            text: ruleText,
            createdAt: new Date().toISOString()
        };

        this.rules.push(rule);
        this.saveRules();
        this.renderRules();

        this.newRuleInput.value = '';
        this.newRuleInput.focus();
    }

    editRule(ruleId) {
        const ruleItem = document.querySelector(`[data-rule-id="${ruleId}"]`);
        const ruleTextElement = ruleItem.querySelector('.rule-text');
        const editBtn = ruleItem.querySelector('.edit-btn');

        if (ruleTextElement.contentEditable === 'true') {
            // Save the edit
            const newText = ruleTextElement.textContent.trim();
            const ruleIndex = this.rules.findIndex(r => r.id === ruleId);

            if (ruleIndex !== -1 && newText) {
                this.rules[ruleIndex].text = newText;
                this.saveRules();
            }

            ruleTextElement.contentEditable = 'false';
            editBtn.innerHTML = '<img src="assets/edit-icon.svg" alt="Edit" class="rule-icon">';
        } else {
            // Start editing
            ruleTextElement.contentEditable = 'true';
            ruleTextElement.focus();

            // Select all text
            const range = document.createRange();
            range.selectNodeContents(ruleTextElement);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);

            editBtn.innerHTML = '<img src="assets/save-icon.svg" alt="Save" class="rule-icon">';
        }
    }

    deleteRule(ruleId) {
        this.rules = this.rules.filter(rule => rule.id !== ruleId);
        this.saveRules();
        this.renderRules();
    }

    async saveRules() {
        const response = await fetch(`${this.apiBase}/settings`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rules: this.rules })
        });

        if (!response.ok) {
            throw new Error('Failed to save rules to database');
        }
    }

    async loadRules() {
        const response = await fetch(`${this.apiBase}/settings`);
        if (!response.ok) {
            throw new Error('Failed to load rules from database');
        }

        const data = await response.json();
        this.rules = data.settings.rules || [];
        this.renderRules();
    }

    renderRules() {
        if (!this.rulesList) return;

        if (this.rules.length === 0) {
            this.rulesList.innerHTML = '<div class="empty-rules">No rules defined yet. Add your first rule above.</div>';
            return;
        }

        this.rulesList.innerHTML = this.rules.map(rule => `
            <div class="rule-item" data-rule-id="${rule.id}">
                <div class="rule-content">
                    <p class="rule-text">${this.escapeHtml(rule.text)}</p>
                </div>
                <div class="rule-actions">
                    <button class="rule-btn edit-btn" title="Edit rule">
                        <img src="assets/edit-icon.svg" alt="Edit" class="rule-icon">
                    </button>
                    <button class="rule-btn delete-btn" title="Delete rule">
                        <img src="assets/delete-icon.svg" alt="Delete" class="rule-icon">
                    </button>
                </div>
            </div>
        `).join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async loadSettings() {
        const response = await fetch(`${this.apiBase}/settings`);
        if (!response.ok) {
            throw new Error('Failed to load settings from database');
        }

        const data = await response.json();
        const settings = data.settings;

        // Load API key
        if (settings.api_key && this.apiKeyInput) {
            this.apiKeyInput.value = settings.api_key;
        }

        // Load selected model
        if (settings.model && this.modelSelect) {
            this.modelSelect.value = settings.model;
        }

        // Load rules
        this.rules = settings.rules || [];
        this.renderRules();
    }

    async getApiKey() {
        const response = await fetch(`${this.apiBase}/settings`);
        if (!response.ok) {
            throw new Error('Failed to get API key from database');
        }

        const data = await response.json();
        return data.settings.api_key || '';
    }

    async getSelectedModel() {
        const response = await fetch(`${this.apiBase}/settings`);
        if (!response.ok) {
            throw new Error('Failed to get model from database');
        }

        const data = await response.json();
        return data.settings.model || 'glm-4.6';
    }
}