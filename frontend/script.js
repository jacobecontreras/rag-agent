const agentView = document.getElementById('agentView');
const settingsView = document.getElementById('settingsView');
const agentNav = document.querySelector('.agent-nav');
const settingsNav = document.querySelector('.settings-nav');

function showAgentView() {
    agentView.style.display = 'flex';
    settingsView.style.display = 'none';
    agentNav.classList.add('active');
    settingsNav.classList.remove('active');
}

function showSettingsView() {
    agentView.style.display = 'none';
    settingsView.style.display = 'block';
    agentNav.classList.remove('active');
    settingsNav.classList.add('active');
}

agentNav.addEventListener('click', showAgentView);
settingsNav.addEventListener('click', showSettingsView);

const messageInput = document.getElementById('messageInput');

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
}

messageInput.addEventListener('input', autoResizeTextarea);

document.getElementById('sendButton').addEventListener('click', () => {
    const message = messageInput.value;
    if (message) {
        document.getElementById('chatMessages').innerHTML += `<div class="message user-message"><div class="message-content">${message}</div></div>`;
        messageInput.value = '';
        autoResizeTextarea();
        document.getElementById('chatMessages').innerHTML += '<div class="message ai-message"><div class="message-content">Hello</div></div>';
    }
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('sendButton').click();
    }
});

showAgentView();