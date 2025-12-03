import os
import json
import httpx
from typing import AsyncGenerator
from fastapi import HTTPException
from dotenv import load_dotenv
from services.settings_service import settings_service

load_dotenv()

class AIService:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self._settings_service = settings_service

        # Get API key from database only
        self.api_key = self._settings_service.get_api_key()

        # Get model from database only
        db_model = self._settings_service.get_model()
        self.model = f"z-ai/{db_model}" if not db_model.startswith("z-ai/") else db_model

        if not self.api_key:
            raise ValueError("AI service not configured: No API key found in database. Please configure your API key in the settings.")

    def refresh_settings(self):
        """Refresh API key and model from database"""
        self.api_key = self._settings_service.get_api_key()
        db_model = self._settings_service.get_model()
        self.model = f"z-ai/{db_model}" if not db_model.startswith("z-ai/") else db_model

        if not self.api_key:
            raise ValueError("AI service not configured: No API key found in database. Please configure your API key in the settings.")

    async def chat_stream_with_context(self, input_data) -> AsyncGenerator[str, None]:
        """Send messages to AI and stream response tokens in real-time

        Args:
            input_data: Either a single message string or list of message dictionaries with conversation context
        """
        # Handle both single message and message list with smart type detection
        if isinstance(input_data, list):
            messages = input_data
        elif isinstance(input_data, str):
            messages = [{"role": "user", "content": input_data}]
        else:
            raise ValueError("input_data must be either a string or list of message dictionaries")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream",
            "HTTP-Referer": "https://capstone.forensics",
            "X-Title": "CAPSTONE Forensics",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                async with client.stream(
                    "POST",
                    self.base_url,
                    headers=headers,
                    json=payload
                ) as response:

                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"AI service error: {error_text.decode()}"
                        )

                    buffer = ""
                    async for chunk in response.aiter_text():
                        buffer += chunk
                        lines = buffer.split('\n')
                        buffer = lines.pop() or ""

                        for line in lines:
                            if not line.startswith('data: '):
                                continue

                            data = line[6:].strip()
                            if data == '[DONE]':
                                return

                            try:
                                parsed = json.loads(data)
                                content = parsed['choices'][0].get('delta', {}).get('content') if parsed['choices'] else None
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue

            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to AI service: {str(e)}"
                )


# Global instance - lazy initialization
ai_service = None

def get_ai_service():
    """Get or create the AI service instance"""
    global ai_service
    if ai_service is None:
        ai_service = AIService()
    return ai_service