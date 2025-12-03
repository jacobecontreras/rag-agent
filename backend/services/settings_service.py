import json
import logging
from typing import Dict, Any, Optional
from database.database import get_ai_setting, set_ai_setting, get_all_ai_settings

logger = logging.getLogger(__name__)

class SettingsService:
    """Service for managing AI settings stored in database"""

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all AI settings as a dictionary"""
        settings = get_all_ai_settings()

        # Parse JSON fields
        result = {
            'api_key': settings.get('api_key', ''),
            'model': settings.get('model', ''),
            'disable_embedding': settings.get('disable_embedding', 'false').lower() == 'true'
        }

        # Parse rules as JSON
        rules_json = settings.get('rules', '[]')
        try:
            result['rules'] = json.loads(rules_json)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON for rules in database: {rules_json}")
            result['rules'] = []

        return result

    def get_api_key(self) -> str:
        """Get the stored API key"""
        return get_ai_setting('api_key') or ''

    def get_model(self) -> str:
        """Get the stored model"""
        return get_ai_setting('model') or ''

    def get_rules(self) -> list:
        """Get the stored AI rules as a list"""
        rules_json = get_ai_setting('rules') or '[]'
        try:
            return json.loads(rules_json)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON for rules in database: {rules_json}")
            return []

    def get_disable_embedding(self) -> bool:
        """Get the disable_embedding setting"""
        return get_ai_setting('disable_embedding') == 'true'

    def set_api_key(self, api_key: str):
        """Set the API key"""
        set_ai_setting('api_key', api_key)
        logger.info("API key updated")

    def set_model(self, model: str):
        """Set the AI model"""
        set_ai_setting('model', model)
        logger.info(f"Model updated to: {model}")

    def set_rules(self, rules: list):
        """Set the AI rules (stored as JSON)"""
        rules_json = json.dumps(rules)
        set_ai_setting('rules', rules_json)
        logger.info(f"Rules updated: {len(rules)} rules stored")

    def set_disable_embedding(self, disable: bool):
        """Set the disable_embedding setting"""
        set_ai_setting('disable_embedding', str(disable).lower())
        logger.info(f"Disable embedding updated to: {disable}")

    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update multiple settings at once"""
        try:
            if 'api_key' in settings:
                self.set_api_key(settings['api_key'])

            if 'model' in settings:
                self.set_model(settings['model'])

            if 'disable_embedding' in settings:
                self.set_disable_embedding(settings['disable_embedding'])

            if 'rules' in settings:
                if isinstance(settings['rules'], list):
                    self.set_rules(settings['rules'])
                else:
                    logger.error("Rules must be a list")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return False

# Global instance
settings_service = SettingsService()