const AIService = {
    sendMessage(message, onToken, onComplete, onError) {
        let aborted = false;
        const controller = new AbortController();

        const promise = (async () => {
            try {
                const apiKey = localStorage.getItem('zai_api_key');
                if (!apiKey) {
                    throw new Error('No API key found');
                }

                const response = await fetch('https://api.z.ai/api/paas/v4/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${apiKey}`,
                        'Accept': 'text/event-stream',
                    },
                    signal: controller.signal,
                    body: JSON.stringify({
                        model: 'glm-4.5',
                        messages: [
                            { role: "system", content: "You are a LEAPP forensic analysis assistant. You specialize in analyzing aLEAPP and iLEAPP reports. Help users analyze forensic data and answer questions about their LEAPP reports." },
                            { role: "user", content: message }
                        ],
                        stream: true
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let accumulatedText = '';
                let buffer = '';

                try {
                    while (!aborted) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\n');
                        buffer = lines.pop() || '';

                        for (const line of lines) {
                            if (!line.startsWith('data: ')) continue;

                            const data = line.slice(6).trim();
                            if (data === '[DONE]') {
                                return accumulatedText;
                            }

                            try {
                                const parsed = JSON.parse(data);
                                const content = parsed.choices?.[0]?.delta?.content;
                                if (content) {
                                    accumulatedText += content;
                                    if (onToken) onToken(content, accumulatedText);
                                }
                            } catch (e) {
                                // Skip invalid JSON silently
                            }
                        }
                    }
                } finally {
                    reader.releaseLock();
                }
                return accumulatedText;
            } catch (error) {
                if (error.name === 'AbortError' || aborted) {
                    return accumulatedText || '';
                }
                throw error;
            }
        })();

        return {
            promise: promise
                .then(text => {
                    if (!aborted && onComplete) onComplete(text);
                    return text;
                })
                .catch(error => {
                    if (!aborted && onError) onError(error.message);
                    throw error;
                }),
            abort: () => {
                aborted = true;
                controller.abort();
            }
        };
    }
};