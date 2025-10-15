const OLLAMA_CONFIG = {
    url: 'http://localhost:11434/api/chat',
    model: 'gpt-oss:20b',
    systemPrompt: "You are a LEAPP forensic analysis assistant. You specialize in analyzing aLEAPP and iLEAPP reports. Help users analyze forensic data and answer questions about your LEAPP reports."
};

const AIService = {
    async sendMessage(message) {
        const response = await fetch(OLLAMA_CONFIG.url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: OLLAMA_CONFIG.model,
                messages: [
                    { role: "system", content: OLLAMA_CONFIG.systemPrompt },
                    { role: "user", content: message }
                ],
                stream: false
            })
        });

        if (!response.ok) {
            throw new Error(`Ollama API error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.message.content;
    }
};