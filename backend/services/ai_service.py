import logging
import requests
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configuration for Ollama API
OLLAMA_CONFIG = {
    "url": os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat"),
    "model": os.getenv("OLLAMA_MODEL", "gpt-oss:20b"),
    "system_prompt": "You are a LEAPP forensic analysis assistant. You specialize in analyzing aLEAPP and iLEAPP reports. Help users analyze forensic data and answer questions about your LEAPP reports."
}


class AIService:
    """Service for handling Ollama API calls"""

    def __init__(self):
        self.config = OLLAMA_CONFIG

    async def send_message(self, message: str) -> str:
        """Send a message to Ollama API and get a response"""
        try:
            logger.info(f"Sending message to Ollama: {message[:100]}...")

            payload = {
                "model": self.config["model"],
                "messages": [
                    {"role": "system", "content": self.config["system_prompt"]},
                    {"role": "user", "content": message}
                ],
                "stream": False
            }

            response = requests.post(
                self.config["url"],
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30  # 30 second timeout
            )

            if not response.ok:
                error_msg = f"Ollama API error! status: {response.status_code}, response: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

            data = response.json()
            ai_response = data.get("message", {}).get("content", "")

            logger.info(f"Received AI response: {ai_response[:100]}...")
            return ai_response

        except requests.exceptions.Timeout:
            error_msg = "Ollama API request timed out after 30 seconds"
            logger.error(error_msg)
            raise Exception(error_msg)

        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to Ollama API. Is Ollama running?"
            logger.error(error_msg)
            raise Exception(error_msg)

        except Exception as e:
            error_msg = f"Error in AI service: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)


# Global instance
ai_service = AIService()